// Frozen screenshots for before/after look checks: node shots.mjs <url> <label> "<sid>:<t>,<sid>:<t>,..."
// Each shot seeks to the scene time, freezes both clocks (App.paused, fixed ambient time) and waits for every image to
// settle, so two builds can be compared pixel for pixel.  Also prints the frame rate of a 2 s free run per shot.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const OUT = fileURLToPath(new URL('./out', import.meta.url)).split(String.fromCharCode(92)).join('/');
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [URL0, LABEL, LIST] = [process.argv[2], process.argv[3], process.argv[4]];
const PORT = 9800 + Math.floor(Math.random() * 150), W = 1600, H = 900;
const dir = `${OUT}/shots_${LABEL}`; fs.mkdirSync(dir, { recursive: true });
const ch = spawn(CHROME, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${OUT}/chprof_shots`, `--window-size=${W},${H + 80}`, '--window-position=-2600,40',
  '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding', '--disable-background-timer-throttling',
  '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws, id = 0; const pending = new Map(), errs = [];
for (let i = 0; i < 80 && !ws; i++) {
  try { const l = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); const p = l.find(t => t.type === 'page'); if (p) { const w = new WebSocket(p.webSocketDebuggerUrl); await new Promise(r => w.onopen = r); ws = w; } } catch {}
  if (!ws) await sleep(200);
}
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } else if (d.method === 'Runtime.exceptionThrown' || (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error')) errs.push(JSON.stringify(d.params).slice(0, 300)); };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result?.result?.value; };
await send('Page.enable'); await send('Runtime.enable');
// start from an empty HTTP cache: the pages-like server lets files live 10 min, and a profile reused within that
// window would otherwise run the previous build's scripts
await send('Network.enable'); await send('Network.clearBrowserCache'); await send('Network.disable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: URL0 + (URL0.includes('?') ? '&' : '?') + 'noattract' });
await ev(`new Promise(r => { const c = () => (typeof App !== 'undefined' && App.last && !App.hold) ? r(1) : setTimeout(c, 100); c(); })`);
await sleep(1500);
for (const item of LIST.split(',')) {
  const [sid, t] = item.split(':');
  // free run for 2 s from just before the shot (fps), then freeze at exactly the shot time
  const fps = await ev(`(async () => { App.paused = false; __seek('${sid}', Math.max(0, ${t} - 2.4)); App.mode = 'film';
    let n = 0; const t0 = performance.now(); await new Promise(r => { (function f() { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else r(); })(); });
    return Math.round(n * 1000 / (performance.now() - t0)); })()`);
  await ev(`__seek('${sid}', ${t}); App.mode = 'talk'; App.A = 100; App.paused = true; App.camSnap = true;`);
  await sleep(1800);
  const r = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${dir}/${sid}_${t}.png`, Buffer.from(r.result.data, 'base64'));
  console.log(`${sid}@${t}: ${fps} fps before the shot`);
}
if (errs.length) console.log('errors:', errs.slice(0, 5));
await send('Browser.close').catch(() => {}); await sleep(600);
try { ch.kill(); } catch {}
process.exit(0);
