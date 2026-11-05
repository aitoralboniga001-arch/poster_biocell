"""Section 2 Recognition (V2, zone A): drawn directly at the cell's leading edge, no window.

A Gram-negative rod (geom.BACT) hangs in the air between the two pseudopod arms.  Its envelope is drawn at molecular
scale on the side that faces the cell (inner membrane, periplasm with thin peptidoglycan, outer membrane with LPS,
mannose-rich glycans, opsonins IgG / iC3b) and tapers smoothly to a simple outline round the far side.
The macrophage plasma membrane along geom.LEAD_MEM is over-drawn as a molecular bilayer whose thickness tapers into
the skeleton's thinner membrane at both ends.  Receptors bridge the gap:
  CD14 + TLR4-MD-2 (single-pass, LPS)  ->  TIR -> MyD88 -> (dotted) NF-kB -> inflammation
  MR (CD206) on glycans;  CR3 (CD11b/CD18) on iC3b;  FcgR on the IgG Fc, with its ITAM
Cytosol (to the right):  Src -> ITAM-P -> Syk -> PI3K (PIP3) -> Cdc42-GTP -> WASP  and  Rac-GTP -> WAVE  -> Arp2/3
-> 70-degree branched F-actin, barbed ends at the membrane, pushing into both pseudopod arms (filaments taper in scale
from molecular at the leading edge to organelle scale inside the arms).
Scale: bilayer ~4.6 mm = 5 nm (0.92 mm per nm) at the contact; molecular detail enlarged versus the organelles."""
import math, random
from lib import *
import geom as G
import marks
from style import shade, shade_rot, sheen, spec, tone, lighten, darken, mix, contact_shadow, inside

# ------------------------------------------------------------------ identity colours
NAVY_ = G.MOL['IgG']            # IgG / FcgR
TEAL_ = G.MOL['CR3']            # iC3b / CR3
BROWN_ = G.MOL['MR']            # mannose receptor
PLUM = G.MOL['TLR4']            # TLR4 / MD-2 / CD14 / LPS
ACT = G.MOL['actin']            # F-actin / Arp2/3
OLIVE = BACT
PHOS = M6P                      # phosphate (gold)
MANN = '#3E9B57'                # mannose (SNFG green circle)
KIN = '#6F7A8A'                 # signalling intermediates: neutral slate
MEM = '#C07A66'                 # skeleton plasma-membrane colour (cellmod.MEM)
MEM_CORE = '#FDF0E8'
SK_HEAD = '#A45E4D'             # skeleton head-group beading
LBL = '#3B4350'
DPHAG = '#B8321C'
AIRH = '#F3F1E8'                # label halo on the air
CYH = '#FCEFE7'                 # label halo on the cytoplasm
BACH = '#EEF0D6'                # label halo on the bacterium

# ------------------------------------------------------------------ geometry
BX, BY, BR, BH = G.BACT         # rod centre, radius, half-length (vertical)
R_OM = BR - 1.0                 # outer-membrane centreline radius
CAP1 = (BX, BY - (BH - BR))     # centre of the upper cap
CAP2 = (BX, BY + (BH - BR))     # centre of the lower cap

LEAD = list(G.LEAD_MEM_DENSE)   # bottom -> top, cytosol on the right
LEAD_TOP, LEAD_BOT = min(p[1] for p in LEAD), max(p[1] for p in LEAD)
_LS = sorted(LEAD, key=lambda p: p[1])


def mem_x(y):
    """x of the plasma-membrane centreline at height y (along LEAD_MEM)."""
    for (x0, y0), (x1, y1) in zip(_LS, _LS[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * ((y - y0) / ((y1 - y0) or 1e-9))
    return _LS[0][0] if y < _LS[0][1] else _LS[-1][0]


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def mem_e(y):
    """0 at both ends of LEAD_MEM (skeleton thickness) -> 1 over the contact (molecular thickness)."""
    return _ease(min(y - LEAD_TOP, LEAD_BOT - y) / 38.0)


W_SK, W_MOL = 2.9, 4.6


def mem_w(y):
    return W_SK + (W_MOL - W_SK) * mem_e(y)


# ---- bacterium envelope frame
def env_s(x):
    """Molecular scale of the envelope: 1 on the face toward the cell, ~0.3 on the far side."""
    return 0.24 + 0.76 * _ease((x - 58.0) / 34.0)


def env_frame(y, side=1):
    """(point on the OM centreline, outward unit normal) on the right (side=1) face of the rod at height y."""
    if CAP1[1] <= y <= CAP2[1]:
        return (BX + side * R_OM, y), (side, 0.0)
    c = CAP1 if y < CAP1[1] else CAP2
    dy = max(-R_OM + 0.01, min(R_OM - 0.01, y - c[1]))
    dx = side * math.sqrt(R_OM * R_OM - dy * dy)
    return (c[0] + dx, c[1] + dy), (dx / R_OM, dy / R_OM)


def env_pt(y, off):
    (px, py), (nx, ny) = env_frame(y)
    s = env_s(px)
    return px + nx * off * s, py + ny * off * s


def om_n(y):
    return env_frame(y)[1]


def capsule(step=0.5):
    """OM centreline of the rod, clockwise on screen from the left of the upper cap, with outward normals."""
    pts = []
    n_arc = int(math.pi * R_OM / step)
    for i in range(n_arc):
        a = math.pi + math.pi * i / n_arc            # left -> top -> right (upper cap)
        pts.append((CAP1[0] + R_OM * math.cos(a), CAP1[1] + R_OM * math.sin(a)))
    n_st = int((CAP2[1] - CAP1[1]) / step)
    for i in range(n_st):
        pts.append((BX + R_OM, CAP1[1] + (CAP2[1] - CAP1[1]) * i / n_st))
    for i in range(n_arc):
        a = math.pi * i / n_arc                      # right -> bottom -> left (lower cap)
        pts.append((CAP2[0] + R_OM * math.cos(a), CAP2[1] + R_OM * math.sin(a)))
    for i in range(n_st):
        pts.append((BX - R_OM, CAP2[1] - (CAP2[1] - CAP1[1]) * i / n_st))
    nrm = []
    for (x, y) in pts:
        c = CAP1 if y < CAP1[1] else (CAP2 if y > CAP2[1] else (BX, y))
        dx, dy = x - c[0], y - c[1]
        L = math.hypot(dx, dy) or 1
        nrm.append((dx / L, dy / L))
    return pts, nrm


# ------------------------------------------------------------------ small drawing helpers
def _ug(doc, kind, stops, **a):
    gid = doc.uid('rg_')
    st = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (fmt(o), c, fmt(op)) for o, c, op in stops)
    at = ' '.join('%s="%s"' % (k, fmt(v)) for k, v in a.items())
    doc.defs.append('<%sGradient id="%s" gradientUnits="userSpaceOnUse" %s>%s</%sGradient>' % (kind, gid, at, st, kind))
    return 'url(#%s)' % gid


def dom(doc, cx, cy, rx, ry, rot, color, light=0.45, dark=0.2, sw=0.28, glint=False):
    """One protein domain: lit ellipse, toned outline."""
    ell(doc, cx, cy, rx, ry, fill=shade_rot(doc, color, rot, light=light, dark=dark), stroke=tone(color, 0.45), w=sw, rot=rot)
    if glint and min(rx, ry) >= 1.6:
        spec(doc, cx, cy, min(rx, ry), a0=205, a1=245, op=0.55, inset=0.6, w=0.3)


def ball(doc, cx, cy, r, color, light=0.45, dark=0.2, sw=0.28, glint=True):
    circ(doc, cx, cy, r, fill=shade(doc, color, light=light, dark=dark), stroke=tone(color, 0.45), w=sw)
    if glint and r >= 1.7:
        spec(doc, cx, cy, r, a0=205, a1=245, op=0.6, inset=0.62, w=max(0.28, r * 0.1))


def tm_helix(doc, x0, x1, y, color, w=2.0):
    """Transmembrane helix crossing the (near-vertical) bilayer from x0 to x1."""
    path(doc, 'M%s,%s L%s,%s' % (fmt(x0), fmt(y), fmt(x1), fmt(y)), stroke=tone(color, 0.45), w=w + 0.5)
    path(doc, 'M%s,%s L%s,%s' % (fmt(x0), fmt(y), fmt(x1), fmt(y)), stroke=sheen(doc, color, 0.4, 0.15, angle=90), w=w)
    path(doc, 'M%s,%s L%s,%s' % (fmt(x0 + 0.3), fmt(y - w * 0.22), fmt(x1 - 0.3), fmt(y - w * 0.22)), stroke='#FFFFFF', w=0.3, op=0.45)


def chain(doc, pts, r, color, sw=0.22, light=0.42):
    """Bead chain (glycan / O-antigen)."""
    path(doc, poly_d(pts), stroke=tone(color, 0.35), w=r * 0.55)
    for (x, y) in pts:
        circ(doc, x, y, r, fill=shade(doc, color, light=light, dark=0.15), stroke=tone(color, 0.45), w=sw)


def lbl(doc, x, y, s, color=LBL, size=4.6, weight=600, anchor='start', halo=None, italic=False):
    T(doc, x, y, s, size=size, weight=weight, fill=color, anchor=anchor, halo=halo, italic=italic)


def hair(doc, pts, color, w=0.25):
    leader(doc, pts, color=color, w=w, dot=False, bow=0.0)


def band(pts, nrm, h_in, h_out):
    """Closed polygon between offsets +h_out (along nrm) and -h_in, per point (lists or scalars)."""
    n = len(pts)
    hi = h_in if isinstance(h_in, list) else [h_in] * n
    ho = h_out if isinstance(h_out, list) else [h_out] * n
    a = [(p[0] + q[0] * o, p[1] + q[1] * o) for p, q, o in zip(pts, nrm, ho)]
    b = [(p[0] - q[0] * i, p[1] - q[1] * i) for p, q, i in zip(pts, nrm, hi)]
    return a + b[::-1]


def ring(pts, nrm, off):
    """Closed offset curve (per-point offsets) of a closed polyline."""
    return [(p[0] + q[0] * o, p[1] + q[1] * o) for p, q, o in zip(pts, nrm, off)]


def ring_d(pts, nrm, o_out, o_in):
    """Even-odd annulus between two closed offset curves."""
    return poly_d(ring(pts, nrm, o_out), True) + poly_d(ring(pts, nrm, o_in)[::-1], True)


def beads_along(pts, nrm, off_f, step_f, r_f):
    """Head-group beads at a variable offset / spacing / radius (functions of the point index)."""
    out = []
    acc, nxt = 0.0, 0.0
    for i in range(len(pts)):
        if i:
            acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        if acc >= nxt:
            o = off_f(i)
            out.append((pts[i][0] + nrm[i][0] * o, pts[i][1] + nrm[i][1] * o, r_f(i), i))
            nxt = acc + step_f(i)
    return out


# ------------------------------------------------------------------ the bacterium
def bacterium(doc):
    pts, nrm = capsule()
    S = [env_s(p[0]) for p in pts]
    N = len(pts)
    # soft cast shadow on the air (light from the top left)
    for (dx, dy, w, op) in ((3.4, 5.0, 14, 0.03), (2.4, 3.6, 8, 0.04), (1.5, 2.3, 3.5, 0.05)):
        sh = poly_d([(x + dx, y + dy) for x, y in ring(pts, nrm, [2.0 * s for s in S])], True)
        path(doc, sh, fill='#5B4A26', op=op)
        path(doc, sh, stroke='#5B4A26', w=w, op=op * 0.7)
    # envelope body (periplasm) out to the outer leaflet
    path(doc, poly_d(ring(pts, nrm, [2.2 * s for s in S]), True),
         fill=_ug(doc, 'linear', [(0, '#E6EAC6', 1), (1, '#D8DFA8', 1)], x1=BX - BR, y1=BY - BH, x2=BX + BR, y2=BY + BH))
    # cytoplasm (inside the inner membrane)
    im_off = [-15.5 * s for s in S]
    cyto = ring(pts, nrm, [o - 1.9 * s for o, s in zip(im_off, S)])
    path(doc, poly_d(cyto, True), fill=_ug(doc, 'radial', [(0, '#F6F7E4', 1), (0.55, '#E9EDC8', 1), (1, '#D5DC9F', 1)],
                                           cx=BX - 8, cy=BY - 40, r=BH * 1.2))
    _bact_interior(doc, cyto)
    # inner membrane
    im = ring(pts, nrm, im_off)
    _bilayer_var(doc, im, nrm, [3.4 * s for s in S], tone(OLIVE, -0.1), '#F7F8E8', tone(OLIVE, 0.5))
    # thin peptidoglycan: two glycan strands + peptide cross-links
    pgc = tone(OLIVE, 0.38)
    for off in (-9.4, -6.6):
        q = ring(pts, nrm, [off * s for s in S])
        for j in range(0, N, 12):
            f = _ease((S[j] - 0.38) / 0.3)
            if f > 0.02:
                path(doc, poly_d(q[j:j + 13]), stroke=pgc, w=0.55, dash='1.5 0.45', cap='butt', op=0.75 * f)
    xl = []
    for i in range(0, N, 3):
        if S[i] > 0.5 and (i // 3) % 2:
            p, n, s = pts[i], nrm[i], S[i]
            xl.append('M%s,%sL%s,%s' % (fmt(p[0] - n[0] * 9.4 * s), fmt(p[1] - n[1] * 9.4 * s), fmt(p[0] - n[0] * 6.6 * s), fmt(p[1] - n[1] * 6.6 * s)))
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="0.34" opacity="0.75"/>' % (''.join(xl), pgc))
    # outer membrane
    _bilayer_var(doc, pts, nrm, [4.0 * s for s in S], OLIVE, '#F5F7E2', tone(OLIVE, 0.5))
    # top-left rim light
    lit = _ug(doc, 'linear', [(0, '#FFFFFF', 0.85), (0.5, '#FFFFFF', 0.2), (1, '#FFFFFF', 0)], x1=BX - BR, y1=BY - BH,
              x2=BX + BR * 0.6, y2=BY)
    path(doc, poly_d(ring(pts, nrm, [2.3 * s + 0.2 for s in S]), True), stroke=lit, w=0.45)
    _lps(doc, pts, nrm, S)
    return pts, nrm, S


def _bilayer_var(doc, pts, nrm, W, color, core, heads):
    """Closed bilayer of variable thickness W (per point): rim, leaflets, pale core, head-group beads."""
    path(doc, ring_d(pts, nrm, [w / 2 + 0.3 for w in W], [-w / 2 - 0.3 for w in W]), fill=tone(color, 0.22), extra='fill-rule="evenodd"')
    path(doc, ring_d(pts, nrm, [w / 2 for w in W], [-w / 2 for w in W]), fill=color, extra='fill-rule="evenodd"')
    path(doc, ring_d(pts, nrm, [w * 0.19 for w in W], [-w * 0.19 for w in W]), fill=core, extra='fill-rule="evenodd"')
    for sgn in (-1, 1):
        bs = beads_along(pts, nrm, lambda i: sgn * W[i] * 0.36, lambda i: max(0.75, W[i] * 0.46), lambda i: W[i] * 0.13)
        for r_band in ((0.0, 0.2), (0.2, 0.35), (0.35, 9)):
            sel = [b for b in bs if r_band[0] <= b[2] < r_band[1]]
            if not sel:
                continue
            rr = sum(b[2] for b in sel) / len(sel)
            doc.add('<path d="%s" fill="none" stroke="%s" stroke-linecap="round" stroke-width="%s"/>' % (
                ''.join('M%s,%sh0.001' % (fmt(x), fmt(y)) for x, y, r, i in sel), heads, fmt(2 * rr)))


def _bact_interior(doc, cyto):
    """Goodsell-style hints: a pale nucleoid tangle and ribosomes, kept sparse."""
    rnd = random.Random(44)
    for k in range(6):
        cx, cy = BX - 8 + rnd.uniform(-4, 4), BY + rnd.uniform(-38, 38)
        loop = [(cx + rnd.uniform(-11, 11), cy + rnd.uniform(-20, 20)) for _ in range(7)]
        path(doc, cr_path(loop, True), stroke='#8E9452', w=0.4, op=0.22)
    dots = []
    tries = 0
    while len(dots) < 140 and tries < 20000:
        tries += 1
        x, y = rnd.uniform(BX - BR, BX + BR), rnd.uniform(BY - BH, BY + BH)
        if inside(cyto, x, y) and all((x - a) ** 2 + (y - b) ** 2 > 10 for a, b, _ in dots):
            if all(inside(cyto, x + math.cos(t) * 3.0, y + math.sin(t) * 3.0) for t in (0, 1.57, 3.14, 4.71)):
                dots.append((x, y, rnd.choice((0, 0, 1))))
    for kind, col, w in ((0, '#ABA96A', 1.9), (1, '#C9B47E', 1.35)):
        pts = [(x, y) for x, y, k in dots if k == kind]
        doc.add('<path d="%s" fill="none" stroke="%s" stroke-linecap="round" stroke-width="%s" opacity="0.6"/>' % (
            ''.join('M%s,%sh0.001' % (fmt(x), fmt(y)) for x, y in pts), col, fmt(w)))
        doc.add('<path d="%s" fill="none" stroke="#FFFFFF" stroke-linecap="round" stroke-width="%s" opacity="0.45"/>' % (
            ''.join('M%s,%sh0.001' % (fmt(x - w * 0.16), fmt(y - w * 0.16)) for x, y in pts), fmt(w * 0.3)))


def _lps(doc, pts, nrm, S):
    """Lipid A in the outer leaflet (plum) and LPS chains (core + O-antigen) into the air, scaled with the envelope."""
    rnd = random.Random(21)
    lps_light = mix(PLUM, '#FFFFFF', 0.5)
    n = len(pts)
    i = 0
    segs, beads_o, beads_c, heads = [], [], [], []
    while i < n - 1:
        p, q, s = pts[i], nrm[i], S[i]
        base = (p[0] + q[0] * 1.5 * s, p[1] + q[1] * 1.5 * s)
        heads.append((base, 0.6 * s))
        L = rnd.uniform(7.0, 11.0) * s
        step = 1.45 * s
        steps = max(2, int(L / step))
        ph = rnd.uniform(0, 6.28)
        ch = []
        for k in range(1, steps + 1):
            t = k * step
            wob = 0.55 * s * math.sin(ph + k * 1.25)
            ch.append((base[0] + q[0] * t - q[1] * wob, base[1] + q[1] * t + q[0] * wob))
        segs.append(([base] + ch, s))
        beads_c += [(c, 0.55 * s) for c in ch[:2]]
        beads_o += [(c, 0.5 * s) for c in ch[2:]]
        gap = rnd.uniform(2.3, 3.1) * max(s, 0.5)
        acc = 0.0
        while i < n - 1 and acc < gap:
            acc += math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            i += 1
    for ch, s in segs:
        path(doc, poly_d(ch), stroke=mix(PLUM, '#FFFFFF', 0.25), w=0.38 * s)
    for (c, r) in beads_o:
        circ(doc, c[0], c[1], r, fill=lps_light, stroke=mix(PLUM, '#FFFFFF', 0.15), w=0.14 * r / 0.5)
    for (c, r) in beads_c:
        circ(doc, c[0], c[1], r, fill=mix(PLUM, '#FFFFFF', 0.2))
    for (c, r) in heads:
        circ(doc, c[0], c[1], r, fill=PLUM)


# ------------------------------------------------------------------ macrophage membrane (tapered bilayer)
def lead_frame(ext=14):
    """LEAD_MEM run of the outline, extended by `ext` samples (~0.7 mm each) at both ends so the over-drawn bilayer
    starts and ends on top of the identical skeleton membrane (no seam)."""
    import cellmod as cm
    i0, i1 = cm._nearest(cm.OUT, LEAD[0]), cm._nearest(cm.OUT, LEAD[-1])
    n = len(cm.OUT)
    pts = [cm.OUT[(i0 - ext + k) % n] for k in range((i1 - i0) % n + 2 * ext + 1)]
    nin = []
    for i in range(len(pts)):
        a, b = pts[max(0, i - 2)], pts[min(len(pts) - 1, i + 2)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nin.append((-ty / L, tx / L))           # traversal upward: (-ty, tx) points into the cytosol (+x)
    return pts, nin


def macrophage_membrane(doc, pip3=(430, 478)):
    pts, nin = lead_frame()
    E = [mem_e(p[1]) for p in pts]
    W = [W_SK + (W_MOL - W_SK) * e for e in E]
    rim = [w / 2 + 0.4 * e for w, e in zip(W, E)]
    j = [k for k, e in enumerate(E) if e > 0.01]
    a, b = j[0], j[-1] + 1
    # faint shadow cast on the cytosol at molecular scale
    sh = [(p[0] + 0.7 * e, p[1] + 1.0 * e) for p, e in zip(pts, E)]
    path(doc, poly_d(band(sh[a:b], nin[a:b], [W[k] / 2 + 0.6 * E[k] for k in range(a, b)], [W[k] / 2 for k in range(a, b)]), True),
         fill='#5B3426', op=0.07)
    path(doc, poly_d(band(pts[a:b], nin[a:b], rim[a:b], rim[a:b]), True), fill=tone(MEM, 0.2))
    path(doc, poly_d(band(pts, nin, [w / 2 for w in W], [w / 2 for w in W]), True), fill=MEM)
    core = [w * (0.207 * (1 - e) + 0.19 * e) for w, e in zip(W, E)]
    path(doc, poly_d(band(pts, nin, core, core), True), fill=MEM_CORE)
    for sgn in (-1, 1):
        bs = beads_along(pts, nin, lambda i: sgn * W[i] * (0.345 + 0.025 * E[i]), lambda i: 1.5 + 0.6 * E[i],
                         lambda i: 0.35 + 0.27 * E[i])
        for x, y, r, i in bs:
            circ(doc, x, y, r, fill=mix(SK_HEAD, '#A9604F', E[i]), op=0.65 + 0.3 * E[i])
    # top-left light on the air side (continues the skeleton's lit line)
    lit = _ug(doc, 'linear', [(0, '#FFFFFF', 0.85), (0.5, '#FFFFFF', 0.25), (1, '#FFFFFF', 0.0)], x1=150, y1=110, x2=700, y2=600)
    path(doc, poly_d([(p[0] - q[0] * (w / 2 + 0.65 + 0.35 * e), p[1] - q[1] * (w / 2 + 0.65 + 0.35 * e))
                      for p, q, w, e in zip(pts, nin, W, E)]), stroke=lit, w=0.6)
    # PIP3 (3-phosphoinositide) head groups in the inner leaflet where PI3K acts
    ins = [(p[0] + q[0] * 1.75, p[1] + q[1] * 1.75) for p, q in zip(pts, nin)]
    k = 0
    for p in resample(ins, 2.05, closed=False):
        if pip3[0] <= p[1] <= pip3[1]:
            k += 1
            if k % 2 == 0:
                circ(doc, p[0], p[1], 0.72, fill=PHOS, stroke='#8A6A12', w=0.14)


# ------------------------------------------------------------------ ligands + receptors
def igg(doc, hx, hy, ang=0.0, spread=50, k=1.15):
    """IgG: hinge at (hx, hy); Fc points along ang (deg, 0 = +x = toward the macrophage), Fabs splay back."""
    hc = NAVY_
    lc = mix(NAVY_, '#FFFFFF', 0.5)

    def U(a):
        return math.cos(math.radians(a)), math.sin(math.radians(a))

    ux, uy = U(ang)
    px, py = -uy, ux
    path(doc, 'M%s,%s L%s,%s' % (fmt(hx), fmt(hy), fmt(hx + ux * 2.0 * k), fmt(hy + uy * 2.0 * k)), stroke=tone(hc, 0.4), w=0.6)
    tips = []
    for sgn in (-1, 1):
        a = ang + 180 + sgn * spread
        vx, vy = U(a)
        qx, qy = -vy, vx
        path(doc, 'M%s,%s L%s,%s' % (fmt(hx), fmt(hy), fmt(hx + vx * 1.8 * k), fmt(hy + vy * 1.8 * k)), stroke=tone(hc, 0.4), w=0.6)
        for dpos in (3.2, 7.2):
            for side, c in ((1, hc), (-1, lc)):
                s_ = side * sgn
                cx, cy = hx + (vx * dpos + qx * s_ * 1.12) * k, hy + (vy * dpos + qy * s_ * 1.12) * k
                dom(doc, cx, cy, 1.95 * k, 1.1 * k, a, c, light=0.42, dark=0.18, sw=0.25)
        tips.append((hx + vx * 9.4 * k, hy + vy * 9.4 * k))
    for dpos in (3.6, 7.5):
        for side in (-1, 1):
            cx, cy = hx + (ux * dpos + px * side * 1.12) * k, hy + (uy * dpos + py * side * 1.12) * k
            dom(doc, cx, cy, 1.95 * k, 1.1 * k, ang, hc, light=0.42, dark=0.18, sw=0.25)
    return tips, (hx + ux * 9.6 * k, hy + uy * 9.6 * k)


def fcgr(doc, y, fc_end):
    """FcgR (2 Ig-like domains, single TM, ITAM-bearing tail) binding the IgG Fc."""
    xo = mem_x(y)
    tm_helix(doc, xo - 3.0, xo + 3.0, y, NAVY_, w=1.7)
    d2 = (xo - 6.6, y + 1.2)
    d1 = (fc_end[0] + 2.3, fc_end[1] + 1.6)
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(xo - 3.0), fmt(y), fmt(xo - 4.4), fmt(y + 1.2), fmt(d2[0] + 2.4), fmt(d2[1])), stroke=tone(NAVY_, 0.3), w=0.9)
    dom(doc, d2[0], d2[1], 2.9, 2.1, -15, NAVY_, glint=True)
    dom(doc, d1[0], d1[1], 2.8, 2.05, -40, NAVY_, glint=True)
    return xo


def itam_tail(doc, y, xo):
    """Cytoplasmic tail with the ITAM; two phospho-tyrosines."""
    pts = [(xo + 2.8, y), (xo + 7, y + 0.6), (xo + 11, y + 0.2), (xo + 15.5, y + 1.0), (xo + 19, y + 0.6)]
    path(doc, cr_path(pts, False), stroke=tone(NAVY_, 0.35), w=1.25)
    path(doc, cr_path(pts, False), stroke=NAVY_, w=0.85)
    return [(xo + 9.8, y + 0.3), (xo + 15.2, y + 0.95)]


def pdot(doc, x, y, r=1.15):
    circ(doc, x, y, r, fill=shade(doc, PHOS, light=0.45, dark=0.12), stroke='#7A5A08', w=0.2)
    T(doc, x, y + r * 0.62, 'P', size=r * 1.55, weight=700, fill='#4A3500', anchor='middle')


def cr3(doc, y):
    """CR3 = CD11b (alpha_M, with the I domain) + CD18 (beta2), extended-open, binding iC3b."""
    xo = mem_x(y)
    ca, cb = mix(TEAL_, '#FFFFFF', 0.18), tone(TEAL_, 0.12)
    ya, yb = y - 2.3, y + 2.3
    tm_helix(doc, xo - 3.0, xo + 3.0, ya, ca, w=1.5)
    tm_helix(doc, xo - 3.0, xo + 3.0, yb, cb, w=1.5)
    for (x_, r_) in ((xo - 4.6, 1.15), (xo - 7.0, 1.15), (xo - 9.4, 1.15), (xo - 11.8, 1.15)):
        ball(doc, x_, yb + 0.3, r_, cb, glint=False, sw=0.22)
    dom(doc, xo - 15.0, yb + 0.6, 2.0, 1.45, 8, cb)
    dom(doc, xo - 19.0, yb - 0.2, 2.2, 1.7, -10, cb, glint=True)
    for (x_, rx_, rot_) in ((xo - 5.4, 2.3, -4), (xo - 10.0, 2.3, -6), (xo - 14.6, 2.3, -10)):
        dom(doc, x_, ya - 0.3, rx_, 1.45, rot_, ca, glint=False)
    px, py = xo - 21.0, ya - 2.4
    ball(doc, px, py, 3.0, ca)
    for k in range(7):
        a = math.radians(k * 360 / 7 + 10)
        path(doc, 'M%s,%s L%s,%s' % (fmt(px + math.cos(a) * 1.0), fmt(py + math.sin(a) * 1.0), fmt(px + math.cos(a) * 2.7),
                                     fmt(py + math.sin(a) * 2.7)), stroke=tone(ca, 0.35), w=0.22, op=0.8)
    ai = (px - 4.2, py - 1.0)
    ball(doc, ai[0], ai[1], 1.9, tone(TEAL_, 0.05))
    return xo, ai, (px, py)


def ic3b(doc, ai):
    """iC3b: TED (C3d) domain covalently bound to a surface sugar, contacted by the alpha-I domain; MG-ring core on
    the opened CUB linker."""
    col = mix(TEAL_, '#FFFFFF', 0.45)
    ted = (ai[0] - 3.6, ai[1] + 2.4)
    anchor = env_pt(ted[1] + 2.0, 9.0)
    path(doc, 'M%s,%s L%s,%s' % (fmt(anchor[0]), fmt(anchor[1]), fmt(ted[0] - 1.8), fmt(ted[1] + 0.8)), stroke=tone(TEAL_, 0.35), w=0.55)
    circ(doc, anchor[0], anchor[1], 0.65, fill=tone(TEAL_, 0.35))
    mg = (ted[0] - 1.0, ted[1] - 7.6)
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(ted[0]), fmt(ted[1] - 1.5), fmt(ted[0] + 2.6), fmt(ted[1] - 4.5), fmt(mg[0] + 1.5), fmt(mg[1] + 2.2)),
         stroke=tone(col, 0.35), w=0.55)
    for k in range(6):
        a = math.radians(k * 60 + 15)
        ball(doc, mg[0] + math.cos(a) * 2.35, mg[1] + math.sin(a) * 2.2, 1.25, col, glint=False, sw=0.22)
    ball(doc, mg[0], mg[1], 1.05, tone(col, 0.1), glint=False, sw=0.2)
    dom(doc, ted[0], ted[1], 2.5, 2.1, -20, col, glint=True)
    return ted, mg


def mannose_receptor(doc, y):
    """CD206: TM + 8 CTLDs + FN-II + Cys-rich N-terminal domain."""
    xo = mem_x(y)
    tm_helix(doc, xo - 3.0, xo + 3.0, y, BROWN_, w=1.6)
    path(doc, 'M%s,%s L%s,%s' % (fmt(xo + 2.8), fmt(y), fmt(xo + 6.0), fmt(y + 0.8)), stroke=BROWN_, w=0.8)
    ctrl = [(xo - 3.0, y), (xo - 8, y - 0.5), (xo - 14, y - 0.9), (xo - 20, y - 0.5), (xo - 26, y + 0.4), (xo - 31.5, y + 0.8)]
    sp = cr_sample(ctrl, closed=False, per=10)
    beads = resample(sp, 2.85, closed=False)[1:11]
    path(doc, poly_d(sp), stroke=tone(BROWN_, 0.3), w=0.6)
    out = []
    for i, (bx, by) in enumerate(beads):
        if i < 8:
            dom(doc, bx, by, 1.55, 1.3, 0, BROWN_, light=0.42, dark=0.2, sw=0.22)
        elif i == 8:
            dom(doc, bx, by, 1.2, 1.0, 0, tone(BROWN_, -0.15), sw=0.22)
        else:
            dom(doc, bx, by, 1.35, 1.2, 0, tone(BROWN_, 0.1), sw=0.22)
        out.append((bx, by))
    return xo, out


def glycan(doc, root, tip_dir, n=4, seed=1, reach=1, k=1.0):
    """Mannose-rich glycan: short stem from the surface with a branched head of mannoses (SNFG green circles)."""
    ux, uy = tip_dir
    stem = [(root[0] + ux * s * k, root[1] + uy * s * k) for s in [0] + [1.6 + i * 1.75 for i in range(int(reach))]]
    path(doc, poly_d(stem), stroke=tone(MANN, 0.35), w=0.4 * k)
    circ(doc, stem[1][0], stem[1][1], 0.62 * k, fill='#2A62C0', stroke='#173B7A', w=0.14)
    head = stem[-1]
    pts = []
    for (a, L) in ((-38, 1.7), (36, 1.7), (-70, 3.1), (4, 3.2), (68, 3.0), (-18, 4.6), (30, 4.6))[:n + 2]:
        aa = math.atan2(uy, ux) + math.radians(a)
        pts.append((head[0] + math.cos(aa) * L * k, head[1] + math.sin(aa) * L * k))
    for p in pts:
        path(doc, poly_d([head, p]), stroke=tone(MANN, 0.35), w=0.32 * k)
    for p in [head] + pts:
        circ(doc, p[0], p[1], 0.72 * k, fill=shade(doc, MANN, light=0.4, dark=0.15), stroke=tone(MANN, 0.45), w=0.16)
    return pts


def _horseshoe(doc, cx, cy, r, a0, a1, color, hw=1.35):
    """LRR solenoid: a thick lit crescent along a circular arc, with LRR striations."""
    n = 28
    sp = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
          for i in range(n + 1)]
    nm = normals(sp, closed=False)
    hs = [hw * (0.8 + 0.35 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    left = [(p[0] + q[0] * h, p[1] + q[1] * h) for p, q, h in zip(sp, nm, hs)]
    right = [(p[0] - q[0] * h, p[1] - q[1] * h) for p, q, h in zip(sp, nm, hs)]
    path(doc, poly_d(left + right[::-1], True), fill=shade(doc, color, light=0.42, dark=0.2), stroke=tone(color, 0.45), w=0.28)
    for i in range(2, n - 1, 3):
        p, q, h = sp[i], nm[i], hs[i]
        path(doc, 'M%s,%s L%s,%s' % (fmt(p[0] + q[0] * h * 0.7), fmt(p[1] + q[1] * h * 0.7), fmt(p[0] - q[0] * h * 0.7),
                                     fmt(p[1] - q[1] * h * 0.7)), stroke=lighten(color, 0.55), w=0.2, op=0.75)
    return sp


def tlr4_complex(doc, y1, y2):
    """Activated (TLR4-MD-2-LPS)2 'm'-shaped dimer.  Each TLR4 is single-pass: ONE TM helix, one LRR horseshoe, its own
    MD-2 in the opening; lipid A in each MD-2 bridges to the partner TLR4.  Two TIR domains inside."""
    xo = mem_x((y1 + y2) / 2)
    yc = (y1 + y2) / 2
    r = 4.4
    md = mix(PLUM, '#FFFFFF', 0.42)
    cols = (PLUM, tone(PLUM, 0.14))
    for k, (ytm, sgn) in enumerate(((y1, -1), (y2, 1))):
        col = cols[k]
        ccx, ccy = xo - 10.4, ytm + sgn * 0.6
        if sgn < 0:
            sp = _horseshoe(doc, ccx, ccy, r, 28, -208, col)
        else:
            sp = _horseshoe(doc, ccx, ccy, r, -28, 208, col)
        path(doc, poly_d([sp[0], (xo - 3.0, ytm)]), stroke=tone(col, 0.3), w=0.85)
        tm_helix(doc, xo - 3.0, xo + 3.0, ytm, col, w=1.6)
        ball(doc, xo + 5.3, ytm, 1.8, col, glint=False)           # TIR domain
        dom(doc, ccx - 0.4, ccy - sgn * 2.6, 2.0, 1.45, 0, md, glint=True)
    for sgn in (-1, 1):
        lx, ly = xo - 12.6, yc + sgn * 2.4
        for j in range(3):
            yy = ly - sgn * (0.4 + j * 0.75)
            path(doc, 'M%s,%s l1.8,0 l0.9,%s l0.9,%s l0.9,%s' % (fmt(lx + 0.6), fmt(yy), fmt(-sgn * 0.5), fmt(sgn * 0.5), fmt(-sgn * 0.5)),
                 stroke=tone(PLUM, 0.5), w=0.28)
        circ(doc, lx, ly, 0.85, fill=tone(PLUM, 0.2))
        chain(doc, [(lx - 1.8, ly + sgn * 0.4), (lx - 3.6, ly + sgn * 0.9), (lx - 5.4, ly + sgn * 0.6), (lx - 7.2, ly + sgn * 1.1)],
              0.55, mix(PLUM, '#FFFFFF', 0.3), sw=0.14)
    return xo, (xo + 5.3, y1), (xo + 5.3, y2)


def cd14(doc, y):
    """CD14: GPI-anchored horseshoe that hands an LPS monomer to MD-2."""
    xo = mem_x(y)
    col = mix(PLUM, '#FFFFFF', 0.18)
    path(doc, 'M%s,%s L%s,%s' % (fmt(xo - 1.0), fmt(y), fmt(xo - 5.0), fmt(y)), stroke=tone(col, 0.35), w=0.5)
    circ(doc, xo - 1.2, y, 0.7, fill=tone(col, 0.35))
    c = [(xo - 5.0, y + 3.0), (xo - 8.6, y + 3.4), (xo - 11.2, y + 1.0), (xo - 10.8, y - 2.4), (xo - 7.6, y - 3.6)]
    sp = cr_sample(c, closed=False, per=10)
    nm = normals(sp, closed=False)
    h = 1.5
    left = [(p[0] + n[0] * h, p[1] + n[1] * h) for p, n in zip(sp, nm)]
    right = [(p[0] - n[0] * h, p[1] - n[1] * h) for p, n in zip(sp, nm)]
    path(doc, poly_d([(xo - 5.0, y)] + [sp[0]]), stroke=tone(col, 0.3), w=0.6)
    path(doc, poly_d(left + right[::-1], True), fill=shade(doc, col, light=0.42, dark=0.2), stroke=tone(col, 0.45), w=0.26)
    lx, ly = xo - 8.4, y
    for k in range(3):
        path(doc, 'M%s,%s l1.6,0.25 l0.7,-0.4' % (fmt(lx), fmt(ly - 0.8 + k * 0.8)), stroke=tone(PLUM, 0.5), w=0.26)
    chain(doc, [(lx - 1.2, ly), (lx - 3.0, ly - 0.5), (lx - 4.8, ly + 0.2), (lx - 6.6, ly - 0.4)], 0.55, mix(PLUM, '#FFFFFF', 0.3), sw=0.14)
    return xo


# ------------------------------------------------------------------ cytosolic machinery
def kinase(doc, x, y, r, color, rot=0):
    """Bilobed kinase: smaller N-lobe on top-left of a larger C-lobe."""
    dom(doc, x + r * 0.25, y + r * 0.25, r, r * 0.86, rot, color, glint=False)
    dom(doc, x - r * 0.5, y - r * 0.45, r * 0.68, r * 0.6, rot, mix(color, '#FFFFFF', 0.15), glint=True)


def gtpase(doc, x, y, r, anchor):
    """Small GTPase (Rac / Cdc42) prenyl-anchored in the inner leaflet, with bound GTP."""
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(anchor[0]), fmt(anchor[1]), fmt((anchor[0] + x) / 2), fmt(y + 1.5), fmt(x - r * 0.8), fmt(y + r * 0.3)),
         stroke=tone(KIN, 0.3), w=0.5)
    ball(doc, x, y, r, mix(KIN, '#7FA6A0', 0.35))
    circ(doc, x + r * 0.62, y - r * 0.55, r * 0.42, fill=shade(doc, '#F2C14E', light=0.4, dark=0.1), stroke='#8A6A12', w=0.16)


def filament(doc, a, b, w=1.35, op=1.0):
    """F-actin: toned rod with subunit beading; barbed end at b."""
    d = poly_d([a, b])
    path(doc, d, stroke=tone(ACT, 0.42), w=w + 0.45 * min(1, w), cap='round', op=op)
    path(doc, d, stroke=ACT, w=w, cap='round', op=op)
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    if w >= 0.6:
        path(doc, poly_d([(a[0] - uy * w * 0.18, a[1] + ux * w * 0.18), (b[0] - uy * w * 0.18, b[1] + ux * w * 0.18)]),
             stroke=lighten(ACT, 0.55), w=w * 0.3, dash='%s %s' % (fmt(w * 0.45), fmt(w * 0.4)), cap='butt', op=0.9 * op)


def _crosses(p, q, a, b):
    d1 = (q[0] - p[0], q[1] - p[1]); d2 = (b[0] - a[0], b[1] - a[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return False
    t = ((a[0] - p[0]) * d2[1] - (a[1] - p[1]) * d2[0]) / den
    u = ((a[0] - p[0]) * d1[1] - (a[1] - p[1]) * d1[0]) / den
    return 0.02 < t < 0.98 and 0.02 < u < 0.98


def actin_front(run, scale, seed, spacing=2.9, keep=None, depth=(10, 20), max_cross=1):
    """Dendritic F-actin under a stretch of membrane `run` (dense outline points, any direction).  At each front point
    (spacing shrinks with the local scale) one mother filament runs 35 deg off the local membrane normal with its
    barbed end at the inner leaflet; Arp2/3 on it nucleates daughters at 70 deg, which run 35 deg the other way with
    their barbed ends again at the membrane.  scale(i) (0.2-1) shrinks width, length and gap, so the network tapers
    from molecular scale at the leading edge into the thin pseudopod arms.  keep(x, y) masks areas."""
    import cellmod as cm
    rnd = random.Random(seed)
    OUTL = [p for p in cm.OUT if -10 < p[0] < 300 and 200 < p[1] < 620]
    nin = []
    for i in range(len(run)):
        a, b = run[max(0, i - 3)], run[min(len(run) - 1, i + 3)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        n = (-ty / L, tx / L)
        if not G.inside_cell(run[i][0] + n[0] * 2.5, run[i][1] + n[1] * 2.5):
            n = (-n[0], -n[1])
        nin.append(n)

    def dist_mem(x, y):
        return min((x - p[0]) ** 2 + (y - p[1]) ** 2 for p in OUTL) ** 0.5

    fil, nodes = [], []

    def ok_pt(x, y, gap):
        return G.inside_cell(x, y) and dist_mem(x, y) >= gap and (keep is None or keep(x, y))

    def grow(p, ang, maxL, gap, st=0.4):
        ux, uy = math.cos(ang), math.sin(ang)
        L, x, y = 0.0, p[0], p[1]
        while L < maxL and ok_pt(x + ux * st, y + uy * st, gap):
            x, y, L = x + ux * st, y + uy * st, L + st
        return (x, y), L

    def ok(p, q, skip=()):
        n = 0
        for i, (a, b, _) in enumerate(fil):
            if i not in skip and _crosses(p, q, a, b):
                n += 1
                if n > max_cross:
                    return False
        return True

    acc, nxt = 0.0, 0.0
    for i in range(len(run)):
        if i:
            acc += math.hypot(run[i][0] - run[i - 1][0], run[i][1] - run[i - 1][1])
        if acc < nxt:
            continue
        k = scale(i)
        nxt = acc + spacing * (0.7 + 0.3 * k) * rnd.uniform(0.8, 1.2)
        s = rnd.choice((-1, 1))
        gap = 2.9 * k + 0.9
        on = math.atan2(-nin[i][1], -nin[i][0])          # outward normal
        d = on + s * math.radians(35 + rnd.uniform(-5, 5))
        Lm = rnd.uniform(*depth) * (0.3 + 0.7 * k)
        F = (run[i][0] + nin[i][0] * (gap + 0.2), run[i][1] + nin[i][1] * (gap + 0.2))
        P = (F[0] - math.cos(d) * Lm, F[1] - math.sin(d) * Lm)
        if not ok_pt(P[0], P[1], gap):
            continue
        end, L = grow(P, d, Lm + 3, gap)
        if L < 1.5 or not ok(P, end):
            continue
        fil.append((P, end, k)); mi = len(fil) - 1
        if rnd.random() < 0.8:
            fr = (rnd.uniform(0.2, 0.45),) if rnd.random() < 0.5 else (rnd.uniform(0.15, 0.35), rnd.uniform(0.55, 0.75))
            for frac in fr:
                q = (P[0] + math.cos(d) * L * frac, P[1] + math.sin(d) * L * frac)
                a2 = d - s * math.radians(70 + rnd.uniform(-3, 3))
                e2, L2 = grow(q, a2, 24 * (0.3 + 0.7 * k), gap)
                if L2 < 2.0 * k + 0.8 or not ok(q, e2, skip=(mi,)):
                    continue
                fil.append((q, e2, k)); di = len(fil) - 1; nodes.append((q, d, a2, k))
                if L2 > 8 * k and rnd.random() < 0.6:
                    q3 = (q[0] + math.cos(a2) * L2 * 0.45, q[1] + math.sin(a2) * L2 * 0.45)
                    a3 = a2 + s * math.radians(70 + rnd.uniform(-3, 3))
                    e3, L3 = grow(q3, a3, 24 * (0.3 + 0.7 * k), gap)
                    if L3 >= 2.0 * k + 0.8 and ok(q3, e3, skip=(di,)):
                        fil.append((q3, e3, k)); nodes.append((q3, a2, a3, k))
    return fil, nodes


def _veiled(p):
    """Inside the signalling column (Src ... WAVE), where the network is drawn faint, behind the cascade."""
    return p[0] < 176 and 398 < p[1] < 466


def draw_actin(doc, fil, nodes):
    for a, b, k in fil:
        v = _veiled(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
        filament(doc, a, b, w=0.38 + 0.62 * k, op=(0.75 + 0.25 * k) * (0.32 if v else 1.0))
    for (q, a1, a2, k) in nodes:
        x, y = q
        if _veiled(q):
            continue
        if k < 0.45:
            circ(doc, x, y, 0.32 + 0.5 * k, fill=tone(ACT, 0.45))
            continue
        dx, dy = math.cos(a2), math.sin(a2)
        r = 0.95 * (0.45 + 0.55 * k)
        ball(doc, x + dx * 0.5 * r, y + dy * 0.5 * r, r, tone(ACT, 0.38), glint=False, sw=0.18)
        ball(doc, x + dx * 0.5 * r + math.cos(a1) * 1.15 * r, y + dy * 0.5 * r + math.sin(a1) * 1.15 * r, r * 0.78,
             tone(ACT, 0.58), glint=False, sw=0.18)


# ------------------------------------------------------------------ layout (poster mm)
Y_TLR = (318.0, 331.0)
Y_CD14 = 349.0
Y_MR, Y_CR3, Y_FC, Y_CR3B = 369.0, 393.0, 418.0, 441.0
LIG_X = 77.0                     # right edge of the ligand-label column on the bacterium
COL_X = 176.0                    # left edge of the cytosolic label column


def molecules(doc):
    import cellmod as cm
    g = {}
    # ---- actin: one dendritic front along the whole cup (lower arm -> leading edge -> upper arm), tapering in scale
    run = cm.run_between((176, 553), (172, 249))

    def kscale(i):
        x, y = run[i]
        mol = [p for p in LEAD[::4] if 336 <= p[1] <= 484]
        d = min(math.hypot(x - p[0], y - p[1]) for p in mol)
        return 0.2 + 0.8 * _ease(1 - d / 42.0)

    def keep(x, y):
        if x < 170 and 310 < y < 337:            # TIR / MyD88
            return False
        for yr in (Y_CD14, Y_MR, Y_CR3 - 2.3, Y_CR3 + 2.3, Y_CR3B - 2.3, Y_CR3B + 2.3):
            if abs(y - yr) < 2.4 and x < mem_x(yr) + 9:
                return False
        return True

    fil, nodes = actin_front(run, kscale, seed=120, keep=keep)
    doc._actin_data = (fil, nodes)
    with actor(doc, 'recog.actin', pivot=(148, 398), bbox=(95, 225, 105, 345), zone='zone_a'):
        doc.add('<g clip-path="url(#%s)">' % cm.cell_clip(doc))
        wash = cr_sample([(150, 548), (128, 518), (146, 470), (150, 392), (147, 312), (132, 268), (160, 244)], closed=False, per=10)
        path(doc, poly_d(wash), stroke=ACT, w=26, op=0.05)
        path(doc, poly_d(wash), stroke=ACT, w=12, op=0.05)
        draw_actin(doc, fil, nodes)
        doc.add('</g>')
    nl = [nd for nd in nodes if nd[3] > 0.6 and nd[0][1] > 462]
    with actor(doc, 'recog.receptors', pivot=(128, 385), bbox=(80, 230, 145, 340), zone='zone_a'):
        macrophage_membrane(doc)

        # ---- TLR4 / CD14
        xt, tir1, tir2 = tlr4_complex(doc, *Y_TLR)
        cd14(doc, Y_CD14)
    with actor(doc, 'recog.signalling', pivot=(160, 415), bbox=(115, 275, 165, 235), zone='zone_a'):
        my = (xt + 12.5, (Y_TLR[0] + Y_TLR[1]) / 2)
        mc = mix(PLUM, '#6A6A8A', 0.45)
        path(doc, poly_d([(tir1[0] + 1.2, tir1[1] + 1.0), (my[0] - 1.5, my[1] - 0.8)]), stroke=tone(mc, 0.3), w=0.5)
        path(doc, poly_d([(tir2[0] + 1.2, tir2[1] - 1.0), (my[0] - 1.5, my[1] + 0.8)]), stroke=tone(mc, 0.3), w=0.5)
        ball(doc, my[0], my[1], 2.1, mc)
        ball(doc, my[0] + 3.9, my[1] - 0.4, 1.9, tone(mc, 0.12))
        sig = [(my[0] + 7.0, my[1] - 0.8), (my[0] + 24, my[1] - 6.0), (my[0] + 44, my[1] - 16.0), (my[0] + 60, my[1] - 27.0)]
        arrow(doc, sig, INFL, 'signal', w=1.1, head=4.2)
    g.update(xt=xt, my=my, sig=sig)

    # ---- mannose receptor + glycans
    with actor(doc, 'recog.receptors'):
        xm, beads = mannose_receptor(doc, Y_MR)
        gy = beads[4][1] + 0.5
        glycan(doc, env_pt(gy + 1.0, 2.6), om_n(gy), n=5, seed=3, reach=7)
    with actor(doc, 'recog.bacterium'):
        for yy, rch in ((341.0, 3), (Y_CR3 + 11.0, 4), (Y_FC + 12.0, 3), (455.0, 4), (306.0, 3), (468.0, 3)):
            glycan(doc, env_pt(yy, 2.6), om_n(yy), n=3, seed=int(yy), reach=rch, k=env_s(env_frame(yy)[0][0]))
    g.update(xm=xm, beads=beads)

    # ---- CR3 + iC3b
    with actor(doc, 'recog.receptors'):
        xc, ai, prop = cr3(doc, Y_CR3)
        ted, mg = ic3b(doc, ai)
        g.update(xc=xc, ai=ai, mg=mg, ted=ted)
        _, ai2, _ = cr3(doc, Y_CR3B)
        ic3b(doc, ai2)

        # ---- IgG + FcgR
        xf0 = mem_x(Y_FC)
        tips, fc_end = igg(doc, xf0 - 25.6, Y_FC - 1.6, ang=0, spread=54)
        xf = fcgr(doc, Y_FC, fc_end)
        ps = itam_tail(doc, Y_FC, xf)
        g.update(tips=tips, fc_end=fc_end, xf=xf, ps=ps)

    # ---- cytosolic cascade: Src -> ITAM-P -> Syk -> PI3K -> Cdc42/WASP + Rac/WAVE -> Arp2/3
    with actor(doc, 'recog.signalling'):
        srcc = mix(KIN, '#8C7CA8', 0.3)
        src = (xf + 12.0, Y_FC - 7.0)
        path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(xf + 2.6), fmt(Y_FC - 7.6), fmt(xf + 6.0), fmt(Y_FC - 8.8), fmt(src[0] - 2.4), fmt(src[1] - 0.6)),
             stroke=tone(srcc, 0.3), w=0.5)
        kinase(doc, src[0], src[1], 2.3, srcc)
        for (px, py) in ps:
            pdot(doc, px, py + 0.1)
        arrow(doc, [(src[0] - 1.6, src[1] + 2.4), (ps[0][0] + 0.2, ps[0][1] - 1.5)], tone(srcc, 0.2), 'transport', w=0.45, head=1.7, bow=0.0)
        sykc = mix(KIN, '#4E7FA8', 0.35)
        sh = [(ps[0][0] + 0.2, ps[0][1] + 2.8), (ps[1][0] + 0.1, ps[1][1] + 2.8)]
        syk = (ps[1][0] + 7.6, Y_FC + 8.2)
        path(doc, poly_d([sh[0], sh[1], (syk[0] - 1.6, syk[1] - 0.6)]), stroke=tone(sykc, 0.3), w=0.55)
        for p in sh:
            ball(doc, p[0], p[1], 1.25, sykc, glint=False, sw=0.22)
        kinase(doc, syk[0], syk[1], 2.5, sykc)
        pi3k = (mem_x(436) + 14.0, 436.0)
        pc = mix(KIN, '#A08C6E', 0.4)
        ball(doc, pi3k[0] - 4.4, pi3k[1] - 0.2, 1.7, tone(pc, 0.08), glint=False)
        ball(doc, pi3k[0], pi3k[1], 2.9, pc)
        cdc = (mem_x(449) + 8.5, 449.0)
        wasp = (cdc[0] + 10.0, 449.4)
        rac = (mem_x(460) + 8.5, 460.0)
        wave = (rac[0] + 10.0, 460.4)
        gtpase(doc, cdc[0], cdc[1], 2.1, (mem_x(cdc[1]) + 2.3, cdc[1] - 0.6))
        gtpase(doc, rac[0], rac[1], 2.0, (mem_x(rac[1]) + 2.3, rac[1] - 0.6))
        wc = mix(KIN, '#A86E8C', 0.3)
        vc = mix(KIN, '#8E7AA8', 0.25)
        tgt = (wave[0] - 1.0, wave[1] + 10.0)
        arp = min(nl, key=lambda nd: math.hypot(nd[0][0] - tgt[0], nd[0][1] - tgt[1]))[0] if nl else tgt
        dom(doc, wasp[0], wasp[1], 2.8, 1.7, 0, wc, glint=True)
        dom(doc, wave[0], wave[1], 2.8, 1.7, 0, vc, glint=True)
        ink = '#5E6672'
        arrow(doc, [(syk[0] - 1.6, syk[1] + 2.6), (pi3k[0] + 2.0, pi3k[1] - 3.0)], ink, 'transport', w=0.55, head=2.2, bow=0.0)
        arrow(doc, [(cdc[0] + 2.4, cdc[1]), (wasp[0] - 3.0, wasp[1])], ink, 'transport', w=0.5, head=1.9, bow=0.0)
        arrow(doc, [(rac[0] + 2.4, rac[1]), (wave[0] - 3.0, wave[1])], ink, 'transport', w=0.5, head=1.9, bow=0.0)
        arrow(doc, [(wasp[0] + 2.6, wasp[1] + 1.2), (wasp[0] + 6.0, wasp[1] + 8.0), (arp[0] + 2.2, arp[1] - 1.4)], ink, 'transport', w=0.5, head=1.9)
        arrow(doc, [(wave[0] - 0.4, wave[1] + 1.9), (arp[0] + 0.6, arp[1] - 1.9)], ink, 'transport', w=0.5, head=1.9, bow=0.0)
        g.update(src=src, syk=syk, pi3k=pi3k, cdc=cdc, wasp=wasp, rac=rac, wave=wave, arp=arp)
    return g


def labels(doc, g):
    sz, s2 = 4.6, 4.4
    # receptors: TLR4-MD-2 in the air above, the others on the cytosolic side of their own TM helix
    with actor(doc, 'recog.receptors'):
        lbl(doc, 128.0, 306.5, 'TLR4–MD-2', tone(PLUM, 0.25), sz, anchor='middle', halo=AIRH)
        for yy, txt, col in ((Y_CD14, 'CD14', PLUM), (Y_MR, 'MR', BROWN_), (Y_CR3, 'CR3 → RhoA', TEAL_)):
            lbl(doc, COL_X, yy + 1.6, txt, tone(col, 0.2), sz, halo=CYH)
            hair(doc, [(mem_x(yy) + (6.8 if txt == 'MR' else 4.0), yy), (COL_X - 1.2, yy)], mix(col, '#9AA0A8', 0.6))
    with actor(doc, 'recog.signalling'):
        lbl(doc, g['my'][0] - 3.0, g['my'][1] + 8.0, 'MyD88', tone(PLUM, 0.35), s2, halo=CYH)
        e = g['sig'][-1]
        lbl(doc, e[0] + 3.0, e[1] - 2.5, 'NF-κB → inflammation', tone(INFL, 0.15), sz, halo=CYH)
    # ligands: a column on the bacterium, facing their receptors across the gap
    with actor(doc, 'recog.bacterium'):
        lbl(doc, LIG_X - 2.0, (Y_TLR[0] + Y_TLR[1]) / 2 + 1.6, 'LPS', tone(PLUM, 0.25), sz, anchor='end', halo=BACH)
        lbl(doc, LIG_X, Y_MR + 1.6, 'glycans', tone(MANN, 0.35), sz, anchor='end', halo=BACH)
        lbl(doc, LIG_X, Y_CR3 - 3.0, 'iC3b', tone(TEAL_, 0.25), sz, anchor='end', halo=BACH)
        lbl(doc, LIG_X, Y_FC + 1.6, 'IgG', tone(NAVY_, 0.15), sz, anchor='end', halo=BACH)
    with actor(doc, 'recog.receptors'):
        lbl(doc, g['xf'] - 3.0, Y_FC + 12.5, 'FcγR', tone(NAVY_, 0.15), sz, anchor='end', halo=AIRH)
    # cascade column, in signalling order
    with actor(doc, 'recog.signalling'):
        lbl(doc, COL_X, g['src'][1] + 1.6, 'Src', LBL, sz, halo=CYH)
        lbl(doc, g['ps'][1][0] + 6.0, Y_FC + 2.0, 'ITAM', tone(NAVY_, 0.15), s2, halo=CYH)
        lbl(doc, COL_X, g['syk'][1] + 1.6, 'Syk', LBL, sz, halo=CYH)
        lbl(doc, COL_X, g['pi3k'][1] + 1.6, 'PI3K', LBL, sz, halo=CYH)
        lbl(doc, COL_X, g['wasp'][1] + 1.6, 'Cdc42 → WASP', LBL, sz, halo=CYH)
        lbl(doc, COL_X, g['wave'][1] + 1.6, 'Rac → WAVE', LBL, sz, halo=CYH)
        ya = g['wave'][1] + 11.0
        lbl(doc, COL_X, ya + 1.6, 'Arp2/3', tone(ACT, 0.3), sz, halo=CYH)
        hair(doc, [(g['arp'][0] + 1.6, g['arp'][1]), (COL_X - 1.2, ya)], tone(ACT, 0.1))
        lbl(doc, COL_X, ya + 11.0, 'F-actin', tone(ACT, 0.3), sz, halo=CYH)
        for key, dx in (('src', 3.0), ('syk', 3.4), ('pi3k', 3.6), ('wasp', 3.2), ('wave', 3.2)):
            x, y = g[key]
            if COL_X - (x + dx) > 3:
                hair(doc, [(x + dx, y), (COL_X - 1.2, y)], '#9AA0A8')
    # bacterium
    with actor(doc, 'recog.bacterium'):
        pg = env_pt(440.0, -8.0)
        lbl(doc, LIG_X, 441.6, 'peptidoglycan', tone(OLIVE, 0.45), s2, anchor='end', halo=BACH)
        hair(doc, [(LIG_X + 1.0, 440.0), (pg[0] - 0.6, pg[1])], tone(OLIVE, 0.35))
        marks.hand(doc, 49.0, 352.0, 'Bacterium', size=12.5, fill=tone(OLIVE, 0.45), anchor='middle', halo=BACH)
    # scale bar: 10 nm (bilayer 4.6 mm = 5 nm)
    sb, sx, sy = 9.2, COL_X, ya + 21.0
    path(doc, 'M%s,%s h%s' % (fmt(sx), fmt(sy), fmt(sb)), stroke='#6B6455', w=0.4, cap='butt')
    for xx in (sx, sx + sb):
        path(doc, 'M%s,%s v-1.4' % (fmt(xx), fmt(sy + 0.7)), stroke='#6B6455', w=0.3, cap='butt')
    lbl(doc, sx + sb + 2.0, sy + 1.4, '10 nm', '#6B6455', s2, weight=400, halo=CYH)
    # 2.1 contact tag
    import annot2
    annot2.tag(doc, 123.5, 383.0, '2.1', DPHAG)
    marks.section(doc, 30.0, 248.0, 2, 'Recognition', marks.color_of(2))


def draw(doc):
    with actor(doc, 'recog.bacterium', pivot=(BX, BY), bbox=(10, 255, 115, 270), zone='zone_a'):
        bacterium(doc)
    g = molecules(doc)
    labels(doc, g)
