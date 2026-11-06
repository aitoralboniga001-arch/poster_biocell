// Interleaved A/B on one stretch of the show, in ONE page session (so first-use costs don't land on either side):
//   node ab.mjs <url> <sid> <t> <secs> <rounds> "<variant ON js>" "<variant OFF js>"
// Plays the stretch once to warm it, then alternates base / variant <rounds> times, printing per run the frame count and
// the frames over 25 / 45 / 100 ms, and at the end the medians per side.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const OUT = fileURLToPath(new URL('./out', import.meta.url)).split(String.fromCharCode(92)).join('/');
const [URL0, SID, T0, SECS, ROUNDS, ON, OFF] = [process.argv[2], process.argv[3], +process.argv[4], +process.argv[5], +process.argv[6] || 4, process.argv[7] || '', process.argv[8] || ''];
const LEAD = +(process.env.LEAD || 1.5);
const PORT = 9400 + Math.floor(Math.random() * 200), W = 1600, H = 900;
fs.mkdirSync(OUT, { recursive: true });
const ch = spawn(CHROME, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${OUT}/chprof_ab`, `--window-size=${W},${H + 80}`, '--window-position=-2600,40',
  '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding', '--disable-background-timer-throttling',
  '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
// never hang silently: a stalled Chrome (profile lock, lost socket) ends the run with a clear message
setTimeout(() => { console.log('TIMEOUT: run stalled'); try { ch.kill(); } catch {} process.exit(2); }, +(process.env.LIMIT || 600) * 1000).unref();
let ws, id = 0; const pending = new Map();
for (let i = 0; i < 80 && !ws; i++) {
  try { const l = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); const p = l.find(t => t.type === 'page'); if (p) { const w = new WebSocket(p.webSocketDebuggerUrl); await new Promise(r => w.onopen = r); ws = w; } } catch {}
  if (!ws) await sleep(200);
}
ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } };
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
const run = async () => {
  await ev(`__seek('${SID}', ${Math.max(0, T0 - LEAD)}); App.mode = 'film';`);
  await sleep(LEAD * 1000 / 1.2);
  return ev(`new Promise(res => { const a = []; const t0 = performance.now();
    (function f(t) { a.push(t); if (t - t0 < ${SECS * 1000}) requestAnimationFrame(f); else {
      const d = []; for (let i = 1; i < a.length; i++) d.push(a[i] - a[i - 1]);
      res({ n: a.length, g25: d.filter(x => x > 25).length, g45: d.filter(x => x > 45).length, g100: d.filter(x => x > 100).length, max: Math.round(Math.max(...d)), sum: Math.round(d.filter(x => x > 25).reduce((s, x) => s + x - 16.7, 0)) }); } })(t0); })`);
};
await run();                                         // warm-up: first decodes, uploads and shader compiles
const R = { base: [], var: [] };
for (let i = 0; i < ROUNDS; i++) {
  for (const side of (i % 2 ? ['var', 'base'] : ['base', 'var'])) {
    await ev(side === 'var' ? (ON || '0') : (OFF || '0'));
    const r = await run(); R[side].push(r);
    console.log(`${side.padEnd(4)} frames=${r.n} >25=${r.g25} >45=${r.g45} >100=${r.g100} max=${r.max} lost=${r.sum}ms`);
  }
}
await ev(OFF || '0');
const med = (a, k) => { const v = a.map(x => x[k]).sort((x, y) => x - y); return v[Math.floor(v.length / 2)]; };
for (const side of ['base', 'var']) console.log(`MEDIAN ${side.padEnd(4)} frames=${med(R[side], 'n')} >25=${med(R[side], 'g25')} >45=${med(R[side], 'g45')} lost=${med(R[side], 'sum')}ms max=${med(R[side], 'max')}`);
await send('Browser.close').catch(() => {}); await sleep(800);
try { ch.kill(); } catch {}
process.exit(0);
