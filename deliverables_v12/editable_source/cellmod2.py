"""The macrophage interior: organelles, carriers and both pathways (positions in poster mm)."""
import math, random
from lib import *
from bio import *
from cellmod import *
from style import shade, sheen, contact_shadow, spec, tone, lighten, darken, mix, shade_rot, sheen_rot, lit_side

TEAL = '#13848C'
EE_STROKE, EE_FILL = '#E8892D', '#FFE9CF'
LE_STROKE, LE_FILL = '#C23B2A', '#F9D5CA'
LY_STROKE, LY_FILL = '#6F36A8', '#E4D3F3'

# ------------------------------------------------------------------ key positions (shared with annotation code)
NUC_C = (510, 254)
NUC_SC = 1.12
GOLGI_C = (606, 392)
TGN_Y = 440
CENTRO = (566, 334)
NP = (352, 486, 27)      # nascent phagosome
EP = (400, 560, 31)      # early phagosome
LP = (480, 612, 33)      # late phagosome
PL = (600, 638, 52)      # phagolysosome
LE = (546, 524, 22)      # late endosome
L1 = (526, 590, 14)      # lysosome docking with late phagosome
L2 = (692, 586, 14)      # lysosome delivering to phagolysosome
EE1 = (456, 522, 12)
EE2 = (372, 600, 10)
SPL = (774, 470, 28)     # silica-loaded (damaged) phagolysosome
FIBRE = tuple(to_cell(*p) for p in ASB_FIBRE_POSTER)   # cell coords of the fibre (it lies outside the cell)
CONTACT = (304, 303)     # 2.1: opsonised bacterium A meets the receptors on the plasma membrane
CONTACT_RECEPTORS = [(284, 'tlr', '#8E3B8F'), (297, 'lectin', '#8F5A2A'), (310, 'cr', '#1F8F8A'), (322, 'fc', '#3E5C86')]
ACTIN, ARP = '#E07B39', '#B4561C'      # F-actin / Arp2/3 identity (orange); Arp2/3 nodes a shade deeper
RAB5, RAB7 = '#E3A21A', '#C0392B'      # Rab identities
FUSION_4 = (503, 598, 15)   # 4: lysosome L1 docking on the late phagosome (site magnified in the fusion strip)
ER_SHEETS = [
    [(618, 208), (655, 198), (700, 210), (745, 199), (786, 210), (808, 224)],
    [(622, 248), (660, 242), (704, 254), (752, 244), (795, 258), (818, 272)],
    [(612, 290), (654, 292), (700, 304), (750, 298), (792, 312), (822, 326)],
]
MIIC = (392, 646, 10)
NLRP = (744, 526)

NUC_BASE = [(428, 252), (436, 218), (466, 198), (512, 190), (560, 194), (598, 210), (610, 238), (602, 266), (584, 284),
            (562, 274), (542, 276), (526, 296), (490, 306), (452, 296), (432, 276)]
NUC = [(NUC_C[0] + (x - 519) * NUC_SC, NUC_C[1] + (y - 248) * NUC_SC) for x, y in NUC_BASE]


def nucleus(doc):
    from style import soft_shadow_path, signed_area, inside, dots_path, shade, spec, contact_shadow
    d = cr_path(NUC, True)
    dense = cr_sample(NUC, True, 10)
    out_sgn = 1 if signed_area(dense) > 0 else -1          # offset sign that points outward
    soft_shadow_path(doc, d, dx=2.0, dy=3.4, strength=0.07, blur=7, steps=4)
    g = doc.radgrad([(0, '#F7F5FD'), (0.5, '#E6E0F5'), (0.85, '#D6CEEE'), (1, '#C9BFE6')], cx=.42, cy=.38, r=.72, fx=.36, fy=.3)
    path(doc, d, fill=g)
    # inner shading toward the lower-right rim (volume) - clipped to the nucleus
    cid = doc.uid('nucclip')
    doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
    doc.add('<g clip-path="url(#%s)">' % cid)
    for k in range(6):
        path(doc, d, fill='none', stroke='#B7ABDD', w=22 - k * 3.4, op=0.05)
    # heterochromatin: soft organic blobs hugging the inner envelope (lamina-associated)
    rnd = random.Random(8)
    n = len(dense)
    inner = lambda dd: offset_poly(dense, -out_sgn * dd, closed=True)
    base = inner(2.4)
    starts = [int(n * f) for f in (0.02, 0.13, 0.25, 0.38, 0.5, 0.6, 0.71, 0.82, 0.91)]
    for si, st in enumerate(starts):
        ln = rnd.randint(int(n * 0.06), int(n * 0.1))
        amp = rnd.uniform(6.0, 9.5)
        k1, ph = rnd.uniform(2.5, 4.5), rnd.uniform(0, 6.28)
        idx = [(st + i) % n for i in range(ln)]
        outer = [base[i] for i in idx]
        inn = []
        for j, i in enumerate(idx):
            t = j / (ln - 1)
            th = amp * math.sin(math.pi * t) ** 0.6 * (0.72 + 0.32 * math.sin(t * k1 * 6.28 + ph))
            p = dense[i]
            q = base[i]
            vx, vy = q[0] - p[0], q[1] - p[1]
            L = math.hypot(vx, vy) or 1
            inn.append((q[0] + vx / L * th, q[1] + vy / L * th))
        poly = outer + inn[::-1]
        path(doc, cr_path(poly[::2] if len(poly) > 16 else poly, True), fill='#8175BF', stroke='#62569F', w=0.45, op=0.62)
    # a few free heterochromatin foci
    for (fx, fy, rx, ry, sd) in [(470, 232, 6, 4, 1), (548, 228, 5, 3.4, 2), (540, 270, 5.5, 3.6, 3), (452, 262, 4.6, 3.2, 4)]:
        path(doc, blob(fx, fy, rx, ry, n=8, j=0.22, seed=sd, rot=rnd.uniform(0, 180)), fill='#8175BF', stroke='#62569F', w=0.35, op=0.45)
    # euchromatin: fine stipple
    xs = [p[0] for p in NUC]; ys = [p[1] for p in NUC]
    pts = []
    while len(pts) < 520:
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys))
        if inside(dense, x, y):
            pts.append((x, y))
    doc.add('<path d="%s" fill="none" stroke="#6D61AE" stroke-width="0.55" stroke-linecap="round" opacity="0.32"/>' % dots_path(pts))
    doc.add('</g>')
    # double envelope: outer + inner membranes with a visible (pale) perinuclear space
    path(doc, d, fill='none', stroke='#5E5399', w=4.4)
    path(doc, d, fill='none', stroke='#F2EEFB', w=2.6)
    path(doc, poly_d(offset_poly(dense, out_sgn * 1.75, True), True), stroke='#FFFFFF', w=0.35, op=0.35)
    # nuclear pores: a dark plug spanning both membranes with a light central channel
    res = resample(dense, poly_len(dense, True) / 20, closed=True)
    nm = normals(res, closed=True)
    for p, nn in zip(res, nm):
        ang = math.degrees(math.atan2(nn[1], nn[0]))
        doc.add('<g transform="translate(%s %s) rotate(%s)"><rect x="-2.9" y="-1.25" width="5.8" height="2.5" rx="1.0" fill="#4E4590"/>'
                '<path d="M-2.4,0 L2.4,0" stroke="#E8E3F7" stroke-width="0.55" stroke-linecap="round"/></g>' % (fmt(p[0]), fmt(p[1]), fmt(ang)))
    # nucleolus: shaded sphere with fibrillar centres and a highlight
    contact_shadow(doc, 500, 246, 10, strength=0.14)
    circ(doc, 500, 246, 10, fill=shade(doc, '#8E84C8', light=0.42, dark=0.22), stroke='#5B5096', w=0.55)
    for (fx, fy, fr) in [(497, 249, 2.2), (503.5, 243.5, 1.6), (504, 250.5, 1.3), (495, 243, 1.2)]:
        circ(doc, fx, fy, fr, fill='#5F549E', op=0.7)
    spec(doc, 500, 246, 10, a0=200, a1=250, op=0.75, inset=0.72, w=1.0)


def rough_er(doc):
    for i, s in enumerate(ER_SHEETS):
        er_sheet(doc, s, w=8.4, ribo=True, seed=10 + i, ribo_r=1.0)
    er_sheet(doc, [(436, 232), (404, 214), (366, 224), (340, 254), (332, 292)], w=7.0, seed=31, ribo_r=0.95)
    er_sheet(doc, [(448, 306), (420, 326), (396, 352)], w=7.0, seed=32, ribo_r=0.95)


TGN_PTS = [(GOLGI_C[0] - 66, TGN_Y + 2), (GOLGI_C[0] - 36, TGN_Y - 7), (GOLGI_C[0], TGN_Y + 3), (GOLGI_C[0] + 36, TGN_Y - 6),
           (GOLGI_C[0] + 70, TGN_Y + 4)]
TGN_HALF = 5.2            # half-width of the TGN lumen (membrane band from 5.2 to 6.3)
_TGN_DENSE = cr_sample(TGN_PTS, closed=False, per=16)


def tgn_y(x):
    for (x0, y0), (x1, y1) in zip(_TGN_DENSE, _TGN_DENSE[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1e-9)
    return _TGN_DENSE[0][1] if x < _TGN_DENSE[0][0] else _TGN_DENSE[-1][1]


def golgi_and_tgn(doc):
    cx, cy = GOLGI_C
    cis = golgi(doc, cx, cy, w=150, n=5, gap=10.2, thick=6.0)
    ty = TGN_Y
    tg = cr_path(TGN_PTS, False)
    from style import contact_shadow as _cs
    w_in = 2 * TGN_HALF
    path(doc, tg, stroke='#9B7D6E', w=w_in + 2.6, op=0.12, extra='transform="translate(0.8 1.6)"')
    path(doc, tg, stroke='#1F5A7E', w=w_in + 2.2)
    path(doc, tg, stroke='#A9D3EA', w=w_in)
    dn = _TGN_DENSE[2:-2]
    path(doc, poly_d([(x, y + 2.6) for x, y in dn]), stroke='#8DC1DE', w=4.2, op=0.7)
    path(doc, poly_d([(x, y - 3.9) for x, y in dn]), stroke='#DDEFF8', w=1.3, op=0.9)
    for dx, dy in [(-58, 15), (-20, 16), (22, 16), (58, 17)]:
        _cs(doc, cx + dx, ty + dy, 3.6, strength=0.12)
        vesicle(doc, cx + dx, ty + dy, 3.6, fill='#4A95BD', stroke='#1F5A7E', w=0.4)
    return cis


def misc_organelles(doc):
    mito(doc, 396, 262, 36, 15, rot=-20, seed=1)
    mito(doc, 372, 424, 34, 15, rot=30, seed=2)
    mito(doc, 800, 652, 32, 14, rot=-25, seed=3)
    rnd = random.Random(21)
    for _ in range(90):
        x, y = rnd.uniform(330, 810), rnd.uniform(160, 690)
        circ(doc, x, y, 0.6, fill='#7C8DB5', op=0.45)


def microtubules(doc):
    cx, cy = CENTRO
    centrosome(doc, cx, cy)
    microtubule(doc, [(cx - 4, cy + 4), (528, 410), (486, 486), (440, 535), (420, 548)], color='#A5ABB8')
    microtubule(doc, [(cx - 2, cy + 6), (548, 440), (520, 520), (500, 580), (488, 596)], color='#A5ABB8')
    microtubule(doc, [(cx - 6, cy - 2), (520, 342), (452, 360), (392, 380)], color='#A5ABB8')


COPII_V = [(614, 336), (656, 348)]
CCV = [(566, 480), (630, 480)]


def er_exit_and_golgi_cargo(doc, cis):
    for (x, y, r) in [(660, 290, 8), (706, 301, 4), (752, 298, -6), (786, 309, 10), (650, 246, 4), (704, 252, 0), (762, 246, -4),
                      (675, 202, 0), (730, 203, 0), (775, 208, 8), (790, 256, 8)]:
        hydrolase(doc, x, y, s=0.78, rot=r)
    for k, (vx, vy) in enumerate(COPII_V):
        contact_shadow(doc, vx, vy, 10.2, strength=0.12)
        vesicle(doc, vx, vy, 8.4, fill='#E9F1FF', stroke='#2A5AA0', w=0.6)
        copii(doc, vx, vy, 10.0)
        hydrolase(doc, vx - 1, vy, s=0.7, rot=-20 + 40 * k)
    cx = GOLGI_C[0]
    ys = [y for y, _, _ in cis]
    hydrolase(doc, cx - 40, ys[0] + 2.4, s=0.68, rot=0)
    hydrolase(doc, cx + 38, ys[0] + 2.4, s=0.68, rot=170)
    hydrolase(doc, cx - 2, ys[1] + 2.4, s=0.68, rot=0, p=True)
    hydrolase(doc, cx + 40, ys[2] + 2.4, s=0.68, rot=180, p=True)
    hydrolase(doc, cx - 40, ys[3] + 2.4, s=0.68, rot=0, p=True)
    hydrolase(doc, cx + 12, ys[4] + 2.4, s=0.68, rot=0, p=True)
    for dx in (-50, -26, 4, 30, 56):
        x = cx + dx
        yb = tgn_y(x) + TGN_HALF + 0.5                 # in the lower (cytosol-facing) membrane
        line(doc, x, yb, x, yb + 2.4, tone('#1E8A5A', 0.25), 0.55)      # short cytosolic tail
        m6pr(doc, x, yb, s=0.55, rot=0)                                  # binding arms in the lumen
        if dx in (-50, 4, 56):                                           # hydrolase whose M6P sits in the receptor's fork
            hydrolase(doc, x - 0.98, yb - 3.6 - 4.35, s=0.5, rot=90, p=True)


def sorting_and_endosomes(doc):
    cx = GOLGI_C[0]
    for (x, y) in CCV:
        contact_shadow(doc, x, y, 10.4, strength=0.12)
        vesicle(doc, x, y, 8.0, fill='#EAF4FA', stroke='#1D5F86', w=0.58)
        clathrin(doc, x, y, 9.8)
        line(doc, x, y + 8.0, x, y + 10.4, tone('#1E8A5A', 0.25), 0.55)
        m6pr(doc, x, y + 8.0, s=0.7, rot=0)
        hydrolase(doc, x - 1.21, y + 8.0 - 4.62 - 5.39, s=0.62, rot=90, p=True)
    x, y, r = LE
    vesicle(doc, x, y, r, fill=LE_FILL, stroke=LE_STROKE, w=0.9)
    for (ix, iy, ir) in ((x - 6, y - 2, 6), (x + 7, y + 7, 4.5)):
        circ(doc, ix + 0.4, iy + 0.7, ir, fill=tone(LE_STROKE, 0.1), op=0.12)
        circ(doc, ix, iy, ir, fill=shade(doc, '#FCEBE5', light=0.6, dark=0.06), stroke=tone(LE_STROKE, 0.12), w=0.6)
        spec(doc, ix, iy, ir, a0=200, a1=245, op=0.8, inset=0.72, w=0.5)
    for (dx, dy) in [(-8, -8), (4, -9), (3, 2), (-9, 6), (12, -2), (-1, 12)]:
        hydrolase(doc, x + dx, y + dy, s=0.5, rot=random.Random(int(dx * 7 + dy)).uniform(-40, 40), glycan=False)
    for a in (190, 262, 20):
        px, py = on_circle(x, y, r + 0.6, a)
        qx, qy = on_circle(x, y, r + 2.8, a)
        line(doc, px, py, qx, qy, tone('#1E8A5A', 0.25), 0.55)
        m6pr(doc, px, py, s=0.62, rot=a - 90)
    for a in (130, 310):
        px, py = on_circle(x, y, r, a)
        vatpase(doc, px, py, a, s=0.7)
    rab_dots(doc, x, y, r, (58, 168, 238, 352), RAB7, rr=1.15)
    ex, ey, er_ = EE1
    vesicle(doc, ex, ey, er_, fill=EE_FILL, stroke=EE_STROKE, w=0.8)
    hydrolase(doc, ex, ey, s=0.4, glycan=False)
    rab_dots(doc, ex, ey, er_, (20, 75, 190, 320), RAB5, rr=1.05)
    ex, ey, er_ = EE2
    vesicle(doc, ex, ey, er_, fill=EE_FILL, stroke=EE_STROKE, w=0.75)
    rab_dots(doc, ex, ey, er_, (110, 170, 230), RAB5, rr=1.0)
    for (x, y, r) in [L1, L2]:
        vesicle(doc, x, y, r, fill='#DCC6F0', stroke=LY_STROKE, w=0.9)
        circ(doc, x, y, r - 2.5, fill='none', stroke='#6A4C8A', w=0.6, dash='0.2 1.0', op=0.8)
        rnd = random.Random(int(x))
        for _ in range(7):
            a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r - 5)
            enzyme_dot(doc, x + rr * math.cos(a), y + rr * math.sin(a), 1.7)
        for a in (-70, 150):
            px, py = on_circle(x, y, r, a)
            vatpase(doc, px, py, a, s=0.62)


def nox2(doc, x, y, cyt_deg, s=1.0):
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(cyt_deg + 90), fmt(s))]
    rt = cyt_deg + 90
    # NOX2 identity = crimson (INFL): gp91phox/p22phox in the membrane, cytosolic p47/p67/p40phox + Rac heads
    g.append('<rect x="-4.2" y="-1.9" width="8.4" height="3.8" rx="1.3" fill="%s" stroke="#7a0c37" stroke-width="0.42"/>' % shade_rot(doc, '#EBA3BE', rt, light=0.5, dark=0.12))
    hd = shade_rot(doc, INFL, rt, light=0.45, dark=0.2)
    for dx in (-3.6, 0, 3.6):
        g.append('<circle cx="%s" cy="-5.2" r="1.9" fill="%s" stroke="#7a0c37" stroke-width="0.33"/>' % (dx, hd))
    g.append('<path d="M0,-2 L0,3.8" stroke="#7a0c37" stroke-width="0.5" stroke-dasharray="0.6 0.7"/>')
    g.append('</g>')
    doc.add(''.join(g))


def _cell_clip(doc):
    c = doc.__dict__.setdefault('_style_cache', {})
    if 'cellclip2' not in c:
        cid = doc.uid('cellclip2')
        doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, poly_d(OUT, True)))
        c['cellclip2'] = cid
    return c['cellclip2']


def actin_network(doc, seg, depth=13.0, step=2.2, seed=7, w=0.42, op=0.92, arp=True, wash=0.09, gens=3):
    """Dendritic (Arp2/3-branched) F-actin under a stretch of plasma membrane.
    Mother filaments run at ~35 deg to the membrane normal with their barbed ends at the inner leaflet; Arp2/3 nucleates
    daughters at ~70 deg on the side of the mother, so the array becomes a criss-cross lattice that pushes the membrane
    outward.  Clipped to the cell outline (nothing leaks into the extracellular cup)."""
    from style import inside
    rnd = random.Random(seed)
    res = resample(seg, step, closed=False)
    nm = normals(res, closed=False)
    mid = len(res) // 2
    sg = 1 if inside(OUT, res[mid][0] + nm[mid][0] * 4, res[mid][1] + nm[mid][1] * 4) else -1
    fil, nodes = [], []
    c35, stop = math.cos(math.radians(35)), 1.7

    def rot(v, deg):
        a = math.radians(deg)
        return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))

    def grow(p0, o, s0, d, side, gen):
        """p0 start, o outward normal, s0 depth of the start, d direction, side = +-1 (which way it leans)."""
        L = max(0.0, (s0 - stop) / c35) * rnd.uniform(0.9, 1.05)
        if L < 1.6:
            return
        e = (p0[0] + d[0] * L, p0[1] + d[1] * L)
        fil.append('M%s,%sL%s,%s' % (fmt(p0[0]), fmt(p0[1]), fmt(e[0]), fmt(e[1])))
        if gen >= gens:
            return
        for t in ((rnd.uniform(0.25, 0.5),) if gen > 1 else (rnd.uniform(0.2, 0.4), rnd.uniform(0.55, 0.75))):
            if rnd.random() < (0.85 if gen == 1 else 0.6):
                b = (p0[0] + d[0] * L * t, p0[1] + d[1] * L * t)
                nodes.append(b)
                grow(b, o, s0 - L * t * c35, rot(d, -side * 70), -side, gen + 1)

    for i in range(0, len(res)):
        if rnd.random() < 0.35:
            continue
        p = res[i]
        o = (-sg * nm[i][0], -sg * nm[i][1])               # outward normal
        s0 = depth * rnd.uniform(0.45, 1.0)
        side = rnd.choice((-1, 1))
        d = rot(o, side * (35 + rnd.uniform(-7, 7)))
        grow((p[0] - o[0] * s0, p[1] - o[1] * s0), o, s0, d, side, 1)
    cid = _cell_clip(doc)
    doc.add('<g clip-path="url(#%s)">' % cid)
    if wash:
        path(doc, poly_d(res), stroke=ACTIN, w=depth * 1.7, op=wash)
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/>' % (
        ''.join(fil), ACTIN, fmt(w), op))
    if arp and nodes:
        from style import dots_path
        doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/>' % (
            dots_path(nodes), ARP, fmt(w * 2.5), op))
    doc.add('</g>')


def pseudopod_actin(doc):
    """2.2: branched cortical F-actin filling both pseudopods around the bacterium (cup surface + outer flanks),
    plus a thin, quiet cortex continuing down the lower-left flank (the cortex is everywhere; it is densest where the
    membrane is being pushed)."""
    def idx(p):            # robust to edits of the outline in cellmod.py: locate the stretch by its anchor points
        return min(range(len(OUT)), key=lambda i: (OUT[i][0] - p[0]) ** 2 + (OUT[i][1] - p[1]) ** 2)
    a, b = sorted((idx((294, 486)), idx((300, 338))))
    actin_network(doc, OUT[a:b + 1], depth=13.5, step=2.1, seed=7, w=0.4, op=0.9, wash=0.07)
    c, d = sorted((idx((399, 709)), idx((292, 490))))
    cortex_mesh(doc, OUT[c:d + 8], depth=5.5, seed=17)


def cortex_mesh(doc, seg, depth=5.5, step=1.15, seed=17, w=0.32, op=0.6):
    """Resting cortex: a thin, cross-linked F-actin meshwork running roughly parallel to the membrane, fading in from
    the pseudopod and out toward the base (reads as a quiet band, not as bristles)."""
    from style import inside
    rnd = random.Random(seed)
    res = resample(seg, step, closed=False)
    nm = normals(res, closed=False)
    mid = len(res) // 2
    sg = 1 if inside(OUT, res[mid][0] + nm[mid][0] * 4, res[mid][1] + nm[mid][1] * 4) else -1
    n = len(res)
    out = []
    for i, (p, q) in enumerate(zip(res, nm)):
        fade = min(1.0, (n - 1 - i) / (n * 0.15), i / (n * 0.35))       # strong next to the pseudopod, fades to the base
        if rnd.random() > 0.35 + 0.65 * fade:
            continue
        s = rnd.uniform(1.8, depth) * (0.6 + 0.4 * fade)
        cx, cy = p[0] + sg * q[0] * s, p[1] + sg * q[1] * s
        tx, ty = -q[1], q[0]
        a = math.radians(rnd.uniform(-32, 32))
        dx, dy = tx * math.cos(a) + sg * q[0] * math.sin(a), ty * math.cos(a) + sg * q[1] * math.sin(a)
        L = rnd.uniform(2.2, 4.6)
        out.append('M%s,%sL%s,%s' % (fmt(cx - dx * L / 2), fmt(cy - dy * L / 2), fmt(cx + dx * L / 2), fmt(cy + dy * L / 2)))
    cid = _cell_clip(doc)
    doc.add('<g clip-path="url(#%s)"><path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/></g>' % (
        cid, ''.join(out), ACTIN, fmt(w), op))


def rab_dots(doc, x, y, r, angles, color, rr=1.25):
    """Rab GTPases on the cytosolic face of a membrane: a small lit sphere on a short prenyl tether."""
    body = shade(doc, color, light=0.5, dark=0.16)
    dk = tone(color, 0.4)
    for a in angles:
        px, py = on_circle(x, y, r + 0.4, a)
        qx, qy = on_circle(x, y, r + 1.4 + rr, a)
        line(doc, px, py, qx, qy, dk, 0.35)
        circ(doc, qx, qy, rr, fill=body, stroke=dk, w=0.25)


def phagosomes(doc):
    # cup + bacteria -------------------------------------------------------------
    bacterium(doc, 266, 308, L=56, W=23, rot=-12, seed=4)
    bacterium(doc, 285, 407, L=54, W=23, rot=84, seed=6)
    pseudopod_actin(doc)
    # nascent phagosome ----------------------------------------------------------
    x, y, r = NP
    vesicle(doc, x, y, r, fill='#FFE1D8', stroke=PHAG, w=0.9)
    bacterium(doc, x, y, L=36, W=15, rot=70, lps=True, flagella=False, seed=9, scale=1.0)
    for a in (200, 280, 80):
        px, py = on_circle(x, y, r, a)
        receptor(doc, px, py, h=4.5, rot=a + 90, color='#3E5C86', kind='fc', tail=False)
    for a in (335, 140):
        px, py = on_circle(x, y, r, a)
        nox2(doc, px, py, a, s=1.0)
        for (k, rr) in ((-14, 8), (10, 11), (0, 15)):
            qx, qy = on_circle(x, y, r - rr, a + k)
            ros(doc, qx, qy, s=0.85)
    rab_dots(doc, x, y, r, (240, 20), RAB5)             # Rab5 starts arriving right after closure
    # early phagosome: Rab5 coat, first V-ATPases ---------------------------------
    x, y, r = EP
    vesicle(doc, x, y, r, fill=EE_FILL, stroke=EE_STROKE, w=0.95)
    bacterium(doc, x, y, L=38, W=16, rot=20, lps=False, flagella=False, seed=10)
    px, py = on_circle(x, y, r, 300)
    nox2(doc, px, py, 300, s=1.0)
    ros(doc, *on_circle(x, y, r - 9, 296), s=0.85)
    for a in (180, 65):
        vatpase(doc, *on_circle(x, y, r, a), a, s=0.72)
    rab_dots(doc, x, y, r, (95, 140, 160, 200, 218, 248, 318, 345, 8, 45), RAB5, rr=1.35)
    # late phagosome: Rab7 has replaced Rab5 (Mon1-Ccz1), more V-ATPase -----------
    x, y, r = LP
    vesicle(doc, x, y, r, fill=LE_FILL, stroke=LE_STROKE, w=1.0)
    circ(doc, x, y, r - 2.6, fill='none', stroke='#8A5A4A', w=0.7, dash='0.2 1.1', op=0.8)
    bacterium(doc, x, y, L=38, W=16, rot=-14, lps=False, flagella=False, seed=11)
    rab_dots(doc, x, y, r, (78, 122, 167, 208, 242, 290, 318, 345), RAB7, rr=1.35)
    rab_dots(doc, x, y, r, (186,), RAB5, rr=1.15)        # last Rab5 being exchanged
    # phagolysosome --------------------------------------------------------------
    x, y, r = PL
    g = doc.radgrad([(0, '#FFFFFF'), (0.35, '#F3EAFB'), (0.75, '#E3D2F3'), (1, '#CDB4E8')], cx=.42, cy=.38, r=.66, fx=.34, fy=.28)
    contact_shadow(doc, x, y, r, strength=0.12)
    vesicle(doc, x, y, r, fill=g, stroke=CONV, w=1.1, lit=False)
    rim_shade(doc, x, y, r - 1.4, tone(CONV, 0.2), op=0.2, w=6)
    spec(doc, x, y, r, a0=198, a1=244, op=0.7, inset=0.86, w=2.2)
    circ(doc, x, y, r - 2.8, fill='none', stroke='#6A4C8A', w=0.7, dash='0.2 1.1', op=0.8)


def phago_details(doc):
    lx, ly, lr = LP
    px_, py_, pr = PL
    for a in (100, 145, 225, 265, 305, 40):              # V-ATPase density rises: early 2 -> late 6 -> phagolysosome 11
        x, y = on_circle(lx, ly, lr, a)
        vatpase(doc, x, y, a, s=0.75)
    for (x, y) in [(lx - 18, ly + 8), (lx - 10, ly + 19), (lx + 8, ly + 21), (lx + 20, ly - 8), (lx - 20, ly - 9), (lx + 14, ly + 8)]:
        hplus(doc, x, y, 1.0)
    for a in (80, 102, 124, 146, 198, 220, 276, 298, 318, 350, 162):
        x, y = on_circle(px_, py_, pr, a)
        vatpase(doc, x, y, a, s=0.82)
    rnd = random.Random(14)
    for _ in range(18):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(8, pr - 9)
        hplus(doc, px_ + rr * math.cos(a), py_ + rr * math.sin(a), 0.95)
    for _ in range(20):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(6, pr - 9)
        enzyme_dot(doc, px_ + rr * math.cos(a), py_ + rr * math.sin(a), 2.3)
    for (dx, dy, L, W, rot) in [(-12, -4, 26, 10, 25), (9, 8, 18, 8, -35), (-6, 17, 14, 7, 70), (14, -12, 11, 6, 10)]:
        ls = lit_side(rot)
        g = ['<g transform="translate(%s %s) rotate(%s)" opacity="0.94">' % (fmt(px_ + dx), fmt(py_ + dy), rot),
             '<path d="M%s,%s L%s,%s L%s,%s L%s,%s L%s,%s Z" fill="%s" stroke="#5B6719" stroke-width="0.6" stroke-linejoin="round"/>' % (
                 fmt(-L / 2), fmt(-W / 2), fmt(L / 2 - 2), fmt(-W / 2 + 1.4), fmt(L / 2), fmt(0), fmt(L / 2 - 3), fmt(W / 2), fmt(-L / 2 + 1), fmt(W / 2 - 1),
                 sheen_rot(doc, '#C6CE72', rot, light=0.45, dark=0.16)),
             '<path d="M%s,%s L%s,%s" stroke="#fff" stroke-width="0.6" stroke-linecap="round" opacity="0.6"/>' % (
                 fmt(-L / 2 + 2), fmt(ls * (W / 2 - 1.5)), fmt(L / 2 - 4), fmt(ls * (W / 2 - 1.6))),
             '</g>']
        doc.add(''.join(g))
    rnd = random.Random(3)
    for _ in range(22):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(4, pr - 11)
        circ(doc, px_ + rr * math.cos(a), py_ + rr * math.sin(a) + 5, rnd.uniform(0.5, 1.1), fill='#8C9A3A', op=0.85)
    nx, ny = on_circle(px_, py_, pr, 250)
    nox2(doc, nx, ny, 250, s=1.15)
    for (dx, dy) in [(-3, 16), (7, 24), (-12, 26), (12, 14)]:
        ros(doc, nx + dx, ny + dy, s=1.15)


def ribbons(doc):
    """Soft pathway ribbons under the organelles: the two pathways read from a distance and blend where they converge."""
    ph = cr_path([(296, 400), (330, 452), (352, 486), (400, 560), (480, 612), (560, 640), (604, 640)], False)
    # subtle pH tint along the maturation path: near-neutral amber (nascent/early, pH ~6.5) -> vermilion (late, ~5.5)
    # -> acid magenta-violet (phagolysosome, ~4.5-5)
    gid = doc.uid('phg')
    doc.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="330" y1="452" x2="604" y2="640">'
                    '<stop offset="0" stop-color="#E9A23B" stop-opacity="0.13"/><stop offset="0.5" stop-color="%s" stop-opacity="0.12"/>'
                    '<stop offset="1" stop-color="#A8327E" stop-opacity="0.12"/></linearGradient>' % (gid, PHAG))
    path(doc, ph, stroke='url(#%s)' % gid, w=50, cap='round')
    bio = cr_path([(690, 262), (640, 300), (614, 340), (606, 392), (606, 440), (568, 482), (546, 524), (530, 580), (560, 622), (604, 640)], False)
    path(doc, bio, stroke='#3A7BE6', w=44, op=0.065, cap='round')


def draw_cell(doc):
    plasma_membrane(doc)
    ribbons(doc)
    misc_organelles(doc)
    rough_er(doc)
    nucleus(doc)
    cis = golgi_and_tgn(doc)
    er_exit_and_golgi_cargo(doc, cis)
    phagosomes(doc)
    sorting_and_endosomes(doc)
    phago_details(doc)
