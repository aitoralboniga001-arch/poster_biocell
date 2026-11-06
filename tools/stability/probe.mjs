// Load the poster and evaluate expressions in it: node probe.mjs <url> "<js expr>" ["<js expr after waitSecs>" waitSecs]
// Prints each result as JSON, plus any page errors. For quick checks of state the soak does not log.
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const OUT = fileURLToPath(new URL('./out', import.meta.url)).split(String.fromCharCode(92)).join('/');
const [URL0, E1, E2, WAIT] = [process.argv[2], process.argv[3], process.argv[4], +(process.argv[5] || 3)];
const PORT = 9200 + Math.floor(Math.random() * 200), W = 1600, H = 900;
const ch = spawn(CHROME, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${OUT}/chprof_probe`, `--window-size=${W},${H + 80}`, '--window-position=-2600,40',
  '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding', '--disable-background-timer-throttling',
  '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
setTimeout(() => { console.log('TIMEOUT: run stalled'); try { ch.kill(); } catch {} process.exit(2); }, +(process.env.LIMIT || 180) * 1000).unref();
let ws, id = 0; const pending = new Map(), errs = [];
for (let i = 0; i < 80 && !ws; i++) {
  try { const l = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); const p = l.find(t => t.type === 'page'); if (p) { const w = new WebSocket(p.webSocketDebuggerUrl); await new Promise(r => w.onopen = r); ws = w; } } catch {}
  if (!ws) await sleep(200);
}
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } else if (d.method === 'Runtime.exceptionThrown' || (d.method === 'Runtime.consoleAPICalled' && ['error', 'warning', 'info'].includes(d.params.type))) errs.push(JSON.stringify(d.params.args ? d.params.args.map(a => a.value ?? a.description) : d.params.exceptionDetails).slice(0, 300)); };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); return r.result?.exceptionDetails ? 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300) : r.result?.result?.value; };
await send('Page.enable'); await send('Runtime.enable');
// start from an empty HTTP cache: the pages-like server lets files live 10 min, and a profile reused within that
// window would otherwise run the previous build's scripts
await send('Network.enable'); await send('Network.clearBrowserCache'); await send('Network.disable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: URL0 });
await ev(`new Promise(r => { const c = () => (typeof App !== 'undefined' && App.last && !App.hold) ? r(1) : setTimeout(c, 100); c(); })`);
await sleep(800);
console.log(JSON.stringify(await ev(E1)));
if (E2) { await sleep(WAIT * 1000); console.log(JSON.stringify(await ev(E2))); }
if (errs.length) console.log('console:', errs.slice(0, 8));
await send('Browser.close').catch(() => {}); await sleep(600);
try { ch.kill(); } catch {}
process.exit(0);
