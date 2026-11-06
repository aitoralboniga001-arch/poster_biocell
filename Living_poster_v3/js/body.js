/* The Living Poster v3: the opening world ("Powers of Ten").
   A pen-and-watercolour person breathes in; the camera dives down a procedurally grown bronchial tree, generation
   after generation (each branch ~0.8x its parent), into an alveolar sac.  One alveolus holds the poster itself:
   its wall dissolves and the camera lands on the poster.  World units are arbitrary (the person is ~1000 tall);
   at the bottom of the dive the view is ~2 units wide, so everything is vector and stays crisp. */
'use strict';
const Body = {
  built: false, g: null, chain: [], nodes: [],
  build(root) {
    if (this.built) return;
    this.built = true;
    this.g = root;
    const rnd = (() => { let s = 1234567; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
    this.rnd = rnd;
    const g = el('g', {}, root);
    const INKB = '#2B2730';

    /* ---------- watercolour lungs (layered translucent washes with a darker drying edge) */
    const L = [[705, 415], [662, 430], [620, 478], [592, 556], [576, 655], [572, 755], [588, 826], [640, 846], [700, 834], [744, 802], [768, 742], [776, 642], [771, 540], [757, 472], [736, 428]];
    const Rr = L.map(([x, y]) => [1600 - x, y]);
    Rr.forEach(p => { if (p[1] > 610 && p[1] < 800) p[0] += 26 * Math.sin(Math.PI * (p[1] - 610) / 190); });   // cardiac notch
    this.lungs = [L, Rr];
    const wob = (pts, amp, seed) => pts.map(([x, y], i) => [x + amp * noise(seed + i * 1.7), y + amp * noise(seed + 40 + i * 1.3)]);
    const dC = pts => { const P = Path.catmull(pts, true, 10); return 'M' + P.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join('L') + 'Z'; };
    this.lungG = el('g', {}, g);
    [L, Rr].forEach((poly, li) => {
      const lg = el('g', {}, this.lungG);
      el('path', { d: dC(wob(poly, 9, li * 10 + 1)), fill: '#F2C4B8', opacity: 0.55 }, lg);
      el('path', { d: dC(wob(poly, 7, li * 10 + 2)), fill: '#E8A399', opacity: 0.32 }, lg);
      el('path', { d: dC(wob(poly, 5, li * 10 + 3).map(([x, y]) => [x + (x < 800 ? 6 : -6), y + 8])), fill: '#D9817C', opacity: 0.18 }, lg);
      el('path', { d: dC(wob(poly, 6, li * 10 + 4)), fill: 'none', stroke: '#C8655F', 'stroke-width': 7, opacity: 0.16 }, lg);
      el('path', { d: dC(wob(poly, 2.2, li * 10 + 5)), fill: 'none', stroke: '#7E3B3A', 'stroke-width': 1.3, opacity: 0.55, 'stroke-dasharray': '30 4 60 3' }, lg);
    });

    /* ---------- the person: a pen sketch (head, neck, shoulders), drawn with a slightly trembling line */
    const inkLine = (pts, w, op = 1, seed = 1, per = 8) => {
      const P = Path.catmull(pts, false, per).map(([x, y], i) => [x + 0.8 * noise(seed + i * 0.31), y + 0.8 * noise(seed + 9 + i * 0.29)]);
      return el('path', { d: 'M' + P.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join('L'), fill: 'none', stroke: INKB, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: op, pathLength: 1000 }, this.personG);
    };
    this.personG = el('g', {}, g);
    const head = []; for (let i = 0; i <= 40; i++) { const a = -Math.PI / 2 + i / 40 * TAU * 1.04; head.push([800 + 86 * Math.cos(a) * (1 - 0.06 * Math.sin(a)), 176 + 112 * Math.sin(a)]); }
    this.strokes = [
      inkLine(head, 2.6, 1, 3, 4),
      inkLine([[752, 268], [748, 300], [742, 346]], 2.4, 1, 5), inkLine([[848, 268], [852, 300], [858, 346]], 2.4, 1, 6),
      inkLine([[742, 346], [690, 364], [600, 380], [520, 404], [470, 440], [452, 520], [446, 640], [442, 820], [440, 1020]], 2.8, 1, 7),
      inkLine([[858, 346], [910, 364], [1000, 380], [1080, 404], [1130, 440], [1148, 520], [1154, 640], [1158, 820], [1160, 1020]], 2.8, 1, 8),
      inkLine([[772, 380], [720, 384], [660, 392], [612, 398]], 1.6, 0.8, 9), inkLine([[828, 380], [880, 384], [940, 392], [988, 398]], 1.6, 0.8, 10),
      inkLine([[766, 182], [776, 186], [786, 182]], 1.6, 0.9, 11), inkLine([[814, 182], [824, 186], [834, 182]], 1.6, 0.9, 12),
      inkLine([[800, 190], [796, 214], [804, 220]], 1.4, 0.8, 13),
      inkLine([[790, 244], [800, 238], [810, 244], [800, 252], [790, 244]], 1.6, 0.9, 14),
      inkLine([[720, 120], [760, 78], [820, 70], [870, 96], [884, 140]], 1.2, 0.5, 15),
      inkLine([[505, 560], [560, 600]], 1.0, 0.35, 16), inkLine([[1095, 560], [1040, 600]], 1.0, 0.35, 17),
    ];
    this.mouth = [800, 246];

    /* ---------- bronchial tree */
    const inside = (x, y, poly) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const [xi, yi] = poly[i], [xj, yj] = poly[j]; if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) c = !c; } return c; };
    const segs = [];   // [x0,y0,x1,y1,w,depth]
    const leaves = [];
    const chainIdx = [];
    const BASE_DEPTH = 9, DEEP = 17;
    const grow = (x, y, ang, len, w, d, maxD, poly, onChain) => {
      const x1 = x + Math.cos(ang) * len, y1 = y + Math.sin(ang) * len;
      if (!onChain && d > 1 && d <= BASE_DEPTH + 1 && !inside(x1, y1, poly)) return false;
      segs.push([x, y, x1, y1, w, d]);
      const node = { x: x1, y: y1, len, w, d };
      if (onChain) this.chain.push(node);
      if (d >= maxD) { leaves.push({ x: x1, y: y1, len, ang, onChain, d }); return true; }
      const sp = 0.38 + rnd() * 0.24, asym = (rnd() - 0.5) * 0.18;
      const kids = [[ang - sp + asym, 0.78 + rnd() * 0.06], [ang + sp + asym, 0.76 + rnd() * 0.06]];
      // the dive follows the child heading down-and-out (towards the lung base) on top-level, then alternates
      const pick = onChain ? (d < 6 ? (Math.abs(Math.sin(kids[0][0])) > Math.abs(Math.sin(kids[1][0])) ? 0 : 1) : (d % 2)) : -1;
      let ok = false;
      kids.forEach(([a, f], i) => {
        const ch = onChain && i === pick;
        const md = ch ? DEEP : onChain ? (d >= 6 ? Math.min(DEEP, d + 3) : BASE_DEPTH) : maxD;
        if (grow(x1, y1, a, len * f, w * 0.79, d + 1, md, poly, ch)) ok = true;
      });
      if (!ok && len < 16) leaves.push({ x: x1, y: y1, len, ang, onChain: false, d });
      return true;
    };
    this.chain.push({ x: 800, y: 300, len: 180, w: 26, d: -1 });
    this.chain.push({ x: 800, y: 478, len: 180, w: 26, d: 0 });
    segs.push([800, 290, 800, 478, 26, 0]);
    grow(800, 478, Math.PI * 0.64, 84, 20, 1, BASE_DEPTH, L, true);           // person's right bronchus: steeper, wider
    grow(800, 478, Math.PI * 0.29, 92, 17, 1, BASE_DEPTH, Rr, false);
    this.treeOuter = el('g', { stroke: '#6E4A4C', 'stroke-linecap': 'round', fill: 'none' }, g);
    this.treeInner = el('g', { stroke: '#F7DCD2', 'stroke-linecap': 'round', fill: 'none' }, g);
    this.treeLight = el('g', { stroke: '#FFF4EE', 'stroke-linecap': 'round', fill: 'none', opacity: 0.6 }, g);
    // one path per stroke width instead of one <line> per segment (~1400 elements -> ~110): every line of a group has
    // the same colour and no opacity of its own, so the picture is identical, but painting the body (redone on every
    // frame of the dive, as the camera moves) records ~13x fewer items
    const byW = (host, key, w, d) => { const m = host._byW || (host._byW = new Map()); m.set(key, (m.get(key) || '') + d); };
    const seg = (x0, y0, x1, y1) => `M${+x0.toFixed(3)},${+y0.toFixed(3)}L${+x1.toFixed(3)},${+y1.toFixed(3)}`;
    for (const [x0, y0, x1, y1, w] of segs) {
      byW(this.treeOuter, (w + Math.max(0.25, w * 0.16)).toFixed(3), 0, seg(x0, y0, x1, y1));
      byW(this.treeInner, w.toFixed(3), 0, seg(x0, y0, x1, y1));
      if (w > 0.6) byW(this.treeLight, (w * 0.18).toFixed(3), 0, seg(x0 - w * 0.18, y0 - w * 0.1, x1 - w * 0.18, y1 - w * 0.1));
    }
    for (const host of [this.treeOuter, this.treeInner, this.treeLight]) {
      for (const [sw, d] of host._byW) el('path', { d, 'stroke-width': sw }, host);
      host._byW = null;
    }
    // cartilage rings on the trachea
    for (let y = 300; y < 470; y += 11) el('path', { d: `M787,${y} Q800,${y + 4} 813,${y}`, stroke: '#6E4A4C', 'stroke-width': 1.3, fill: 'none', opacity: 0.6 }, g);

    /* ---------- alveolar sacs at the twigs: grape clusters */
    this.sacG = el('g', {}, g);
    const sacs = [];         // every alveolus of every grape cluster, in drawing order: [cx, cy, r]
    const sac = (x, y, ang, r, n, seed) => {
      const out = [];
      for (let i = 0; i < n; i++) {
        const a = ang + (i - (n - 1) / 2) * 0.62 + 0.25 * noise(seed + i), dd = r * (1.25 + 0.55 * ((i * 7 + seed) % 3) / 2);
        out.push([x + Math.cos(a) * dd, y + Math.sin(a) * dd, r * (0.82 + 0.3 * hash(seed + i))]);
      }
      out.push([x + Math.cos(ang) * r * 2.6, y + Math.sin(ang) * r * 2.6, r * 1.05]);
      sacs.push(...out);
      return out;
    };
    leaves.forEach((lf, i) => { if (!lf.onChain) sac(lf.x, lf.y, lf.ang, Math.min(lf.len * 0.36, 4.2), 4, i * 3 + 1); });

    /* ---------- the end of the dive: one alveolus, holding the poster */
    const end = this.chain[this.chain.length - 1];
    const lastLeaf = leaves.find(l => l.onChain) || { x: end.x, y: end.y, ang: 0, len: end.len };
    const r0 = lastLeaf.len * 0.5;
    const cl = sac(lastLeaf.x, lastLeaf.y, lastLeaf.ang, r0, 5, 99);
    const tgt = cl[cl.length - 1];
    this.target = { x: tgt[0], y: tgt[1], r: tgt[2] };
    // ~2000 alveoli: on the GPU light layer when it is up (instanced discs, rings and highlights in the same order, so
    // overlaps look the same), as SVG circles otherwise. Those round the target alveolus stay in SVG whatever happens,
    // because its dark lumen and the poster inside it are drawn over them as the wall dissolves.
    this.sacFar = el('g', {}, this.sacG); this.sacNear = el('g', {}, this.sacG);
    this.sacList = [];
    const nearR = 7.4 * this.target.r;
    for (const [cx, cy, rr] of sacs) {
      const near = Math.hypot(cx - this.target.x, cy - this.target.y) - rr < nearR, host = near ? this.sacNear : this.sacFar;
      el('circle', { cx: cx.toFixed(3), cy: cy.toFixed(3), r: rr.toFixed(3), fill: '#F4D3C8', stroke: '#8E5B5B', 'stroke-width': (rr * 0.09).toFixed(3), opacity: 0.95 }, host);
      el('circle', { cx: (cx - rr * 0.25).toFixed(3), cy: (cy - rr * 0.3).toFixed(3), r: (rr * 0.35).toFixed(3), fill: '#FFF6F1', opacity: 0.5 }, host);
      if (!near) this.sacList.push(cx, cy, rr);
    }
    this.chain.push({ x: tgt[0], y: tgt[1], len: r0 * 2, w: r0, d: 99 });
    const T = this.target;
    this.s = T.r * 0.985 / Math.hypot(550, 450);       // poster scale inside the alveolus
    const tg = el('g', {}, g);
    const cp = el('clipPath', { id: 'alvClip' }, document.getElementById('defs'));
    this.alvClipC = el('circle', { cx: T.x, cy: T.y, r: T.r }, cp);
    this.alvLumen = el('circle', { cx: T.x, cy: T.y, r: T.r, fill: '#1B1612' }, tg);
    const pg = el('g', { 'clip-path': 'url(#alvClip)' }, tg);
    this.posterImg = el('image', { href: 'assets/poster.jpg', x: T.x - 550 * this.s, y: T.y - 450 * this.s, width: 1100 * this.s, height: 900 * this.s, preserveAspectRatio: 'none' }, pg);
    this.alvWall = el('circle', { cx: T.x, cy: T.y, r: T.r, fill: 'none', stroke: '#8E5B5B', 'stroke-width': T.r * 0.09 }, tg);
    this.alvGlow = el('circle', { cx: T.x, cy: T.y, r: T.r * 1.25, fill: G.glowFill('#FFE9C9'), opacity: 0 }, tg);

    /* ---------- dynamic layer: dust, air */
    this.dyn = el('g', {}, g);
    this.chainPath = new Path(this.chain.map(n => [n.x, n.y]), { smooth: true, per: 10 });
    this.poolDots = [];
  },

  /** camera for the dive at generation-parameter f (0 = carina ... n = target alveolus) */
  diveCam(f) {
    const C = this.chain, n = C.length - 1;
    f = clamp(f, 0, n);
    const i = Math.min(n - 1, Math.floor(f)), t = f - i;
    const a = C[i], b = C[i + 1];
    const la = Math.log(Math.max(a.len * 4.2, 0.0001)), lb = Math.log(Math.max(b.len * 4.2, 0.0001));
    const w = Math.exp(lerp(la, lb, t));
    // look slightly ahead along the airway
    const ahead = this._chainPt(f + 0.55);
    return [ahead[0], ahead[1], w];
  },
  _chainPt(f) {
    const C = this.chain, n = C.length - 1; f = clamp(f, 0, n);
    const i = Math.min(n - 1, Math.floor(f)), t = ease.sine(f - i);
    return [lerp(C[i].x, C[i + 1].x, t), lerp(C[i].y, C[i + 1].y, t)];
  },
  /** the poster's full view, expressed in body-world units */
  posterCam(aspect) {
    const T = this.target, wfit = Math.max(1100, 900 * aspect) * 1.06;
    return [T.x, T.y, wfit * this.s];
  },

  /** set an attribute only when it changes: the body is thousands of vector strokes on one layer, and any change to
   *  it re-rasterises all of them (~110 ms a frame), so a frame where nothing moves must touch nothing */
  _set(e, k, v) { const c = e._c || (e._c = {}); if (c[k] !== v) { e.setAttribute(k, v); c[k] = v; } },
  /** a mote of dust or air: on the GPU light layer when it is up (moving it never re-rasterises the vector body),
   *  otherwise a pooled SVG circle */
  dot(x, y, r, fill, op) {
    if (GLFX.ok) { GLFX.disc(x, y, r, fill, op); return; }
    let e = this.poolDots[this._di];
    if (!e) { e = el('circle', {}, this.dyn); this.poolDots.push(e); }
    e.style.display = '';
    setA(e, { cx: x.toFixed(4), cy: y.toFixed(4), r: r.toFixed(4), fill, opacity: op.toFixed(3) });
    this._di++;
  },

  /** draw the opening at story time T; returns the camera [cx, cy, w] in body units */
  draw(T, A, aspect) {
    this._di = 0;
    const S = (e, k, v) => this._set(e, k, v);
    // person draws itself, lungs bloom, the chest rises with the in-breath. (A slow idle breathing on top of it, a
    // 0.4 % scale wobble, used to change the lungs every frame and re-rasterise the whole body while the finale held
    // still: about 110 ms a frame. The in-breath itself plays while the camera is moving anyway.)
    this.strokes.forEach((s, i) => S(s, 'stroke-dasharray', `${(1000 * R(T, 6.6 + i * 0.12, 8.6 + i * 0.12, ease.cubic)).toFixed(0)} 1000`));
    const bloom = R(T, 8.0, 10.5, ease.out);
    const breath = R(T, 9.4, 12.2, ease.sine) * 0.035;
    S(this.lungG, 'opacity', bloom.toFixed(3));
    S(this.lungG, 'transform', `translate(800,600) scale(${(0.96 + 0.04 * bloom + breath).toFixed(4)}) translate(-800,-600)`);
    const tree = R(T, 9.0, 12.0);
    S(this.treeLight, 'opacity', (0.6 * tree).toFixed(3));
    const n = this.chain.length - 1, fCam = this.diveF(T), iris = R(T, 27.0, 29.6, ease.cubic);
    const cam = this._cam(T, aspect, fCam, n);

    // the alveoli (grape clusters at every twig): on the GPU layer, only those in or near the view
    const sacOp = R(T, 10.0, 12.5) * (1 - 0.85 * iris);
    show(this.sacFar, !GLFX.ok);
    if (GLFX.ok && sacOp > 0.003) {
      const L = this.sacList, hw = cam[2] * 0.8, hh = cam[2] / aspect * 0.8, x0 = cam[0] - hw, x1 = cam[0] + hw, y0 = cam[1] - hh, y1 = cam[1] + hh;
      const fill = GLFX.col('#F4D3C8'), edge = GLFX.col('#8E5B5B'), hi = GLFX.col('#FFF6F1');
      for (let i = 0; i < L.length; i += 3) {
        const cx = L[i], cy = L[i + 1], rr = L[i + 2];
        if (cx + rr < x0 || cx - rr > x1 || cy + rr < y0 || cy - rr > y1) continue;
        GLFX.disc(cx, cy, rr, fill, 0.95 * sacOp);
        GLFX.ring(cx, cy, rr, rr * 0.09, edge, 0.95 * sacOp);
        GLFX.disc(cx - rr * 0.25, cy - rr * 0.3, rr * 0.35, hi, 0.5 * sacOp);
      }
    }

    // dust in the air, drawn into the mouth by the in-breath, then down the airway
    const inhale = R(T, 9.2, 12.4, ease.sine);
    for (let i = 0; i < 70; i++) {
      const hx = 330 + hash(i) * 940, hy = 40 + hash(i + 50) * 360;
      const bx = hx + 18 * Math.sin(A * 0.25 + i), by = hy + 10 * Math.cos(A * 0.21 + i * 1.3);
      const pull = clamp(inhale * 1.6 - hash(i + 9) * 0.6);
      const [mx, my] = this.mouth;
      let x = lerp(bx, mx, ease.in(pull)), y = lerp(by, my, ease.in(pull));
      const op = (i % 7 === 0 ? 0.75 : 0.42) * R(T, 6.0, 8.0) * (1 - R(pull, 0.92, 1));
      const sil = i % 7 === 0;
      this.dot(x, y, sil ? 2.0 : 1.3, sil ? '#B8A07A' : '#8C8478', op);
    }
    // air streaming down the dive path (spaced evenly in generations, so there is always some near the camera)
    for (let i = 0; i < 46; i++) {
      const f = frac(i / 46 + A * 0.045) * n;
      if (Math.abs(f - fCam) > 3.2) continue;
      const p = this._chainPt(f), node = this.chain[Math.min(n, Math.round(f))];
      const off = (hash(i + 3) - 0.5) * node.w * 0.5;
      this.dot(p[0] + off, p[1] + off * 0.6, Math.max(node.w * 0.06, 0.004), '#FFFFFF', 0.85 * R(T, 12.5, 14) * (1 - R(T, 27, 28)));
    }
    for (let j = this._di; j < this.poolDots.length; j++) if (this.poolDots[j].style.display !== 'none') this.poolDots[j].style.display = 'none';

    // the alveolus holding the poster: glows as we approach, then its wall dissolves (iris)
    const T0 = this.target;
    S(this.alvClipC, 'r', (T0.r * (1 + 6 * iris)).toFixed(4));
    S(this.alvLumen, 'r', (T0.r * (1 + 6 * iris)).toFixed(4));
    S(this.alvWall, 'opacity', (1 - iris).toFixed(3));
    S(this.alvWall, 'r', (T0.r * (1 + 0.5 * iris)).toFixed(4));
    S(this.alvGlow, 'opacity', (bump(T, 23, 26, 27.5, 29) * 0.8).toFixed(3));
    S(this.sacG, 'opacity', sacOp.toFixed(3));
    S(this.treeOuter, 'opacity', (tree * (1 - iris)).toFixed(3));
    S(this.treeInner, 'opacity', (tree * (1 - iris)).toFixed(3));
    return cam;
  },
  /** camera: body -> chest -> dive -> the alveolus -> the poster's own framing */
  _cam(T, aspect, fCam, n) {
    const full = [800, 520, Math.max(1700, 1050 * aspect)];
    const chest = [800, 590, Math.max(760, 520 * aspect)];
    let cam = full;
    if (T > 11.5) cam = Cam.zoomPath(full, chest, 1.0)(R(T, 11.5, 13.5, ease.cubic));
    if (T > 13.5) {
      const d0 = this.diveCam(0);
      cam = T < 15 ? Cam.zoomPath(chest, d0, 1.0)(R(T, 13.5, 15, ease.sine)) : this.diveCam(fCam);
    }
    if (T > 26.2) cam = Cam.zoomPath(this.diveCam(n), this.posterCam(aspect), 0.9)(R(T, 26.2, 29.8, ease.cubic));
    return cam;
  },
  diveF(T) {
    const n = this.chain.length - 1;
    const u = clamp((T - 15) / 11.2);
    return n * (0.5 * ease.sine(u) + 0.5 * u);          // constant speed in log-zoom, softened at both ends
  },
};
