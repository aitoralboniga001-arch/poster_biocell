"""V2 skeleton: the macrophage interior at organelle scale (poster mm).

Owned here: nucleus, rough ER leaving the nuclear envelope toward the enzyme staircase (zone D), the phagosome chain
NASCENT -> EARLY -> LATE (zone B), mitochondria, centrosome + microtubules, the two painted route ribbons.
NOT drawn here (zone owners): ER/Golgi/TGN/LE/lysosome sacs (zone D), docking lysosomes + phagolysosome (zone E),
silica / NLRP3 (zone F), asbestos (zone G), recognition at the leading edge (zone A).
"""
import math, random
from lib import *
from bio import *
from cellmod import *
import geom_v2 as V
from style import shade, sheen, contact_shadow, spec, tone, lighten, darken, mix, shade_rot, sheen_rot, lit_side

TEAL = '#13848C'
EE_STROKE, EE_FILL = '#E8892D', '#FFE9CF'
LE_STROKE, LE_FILL = '#C23B2A', '#F9D5CA'
LY_STROKE, LY_FILL = '#6F36A8', '#E4D3F3'
NP_STROKE, NP_FILL = '#D9472F', '#FFE3D9'
ACTIN, ARP = '#E07B39', '#B4561C'      # F-actin / Arp2/3 identity (orange)
RAB5, RAB7 = '#E3A21A', '#C0392B'      # Rab identities

# ------------------------------------------------------------------ key positions (V2 contract; V1 names kept)
NP = V.NASCENT
EP = V.EARLY
LP = V.LATE
PL = V.PHAGOLYSOSOME
SPL = V.SILICA_PL
NUC_C = V.NUCLEUS[:2]
CENTRO = (588, 316)
LATE_DOCK_ARC = (-100, 15)            # upper-right arc of LATE kept free for the fusion owner (degrees, y down)
L1 = (on_circle(LP[0], LP[1], LP[2] + 16, -45)) + (13,)        # where a docking lysosome would sit (zone E draws it)
L2 = (PL[0] + 40, PL[1] - 74, 13)
FUSION_4 = (on_circle(LP[0], LP[1], LP[2], -45)) + (15,)
CONTACT = (V.LEAD_MEM[2][0], V.LEAD_MEM[2][1])
NLRP = (800, 520)
GOLGI_C = ((V.BANDS['3.2 cis-Golgi'][0] + V.BANDS['3.2 cis-Golgi'][2]) / 2, (V.BANDS['3.2 cis-Golgi'][1] + V.BANDS['3.2 cis-Golgi'][3]) / 2)
TGN_Y = (V.BANDS['3.3 TGN'][1] + V.BANDS['3.3 TGN'][3]) / 2
LE = ((V.BANDS['3.5 LE'][0] + V.BANDS['3.5 LE'][2]) / 2, (V.BANDS['3.5 LE'][1] + V.BANDS['3.5 LE'][3]) / 2, 21)
EE1 = (362, 522, 9)
EE2 = (408, 590, 8)
COPII_V = [(745, 200), (700, 262)]
CCV = [(720, 345), (790, 345)]

# ------------------------------------------------------------------ nucleus: a bean (indented toward the centrosome)
def _nucleus_pts():
    cx, cy, rx, ry = V.NUCLEUS
    rnd = random.Random(5)
    pts = []
    N = 22
    for i in range(N):
        a = 2 * math.pi * i / N
        deg = math.degrees(a)
        dd = min(abs(deg - 52), 360 - abs(deg - 52))
        k = 1 - 0.16 * math.exp(-(dd / 26) ** 2) + rnd.uniform(-0.018, 0.018)
        k += 0.03 * math.cos(3 * a + 0.6)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


NUC = _nucleus_pts()
NUC_DENSE = cr_sample(NUC, True, 12)


def nucleus(doc):
    from style import soft_shadow_path, signed_area, inside, dots_path
    cx, cy, rx, ry = V.NUCLEUS
    d = cr_path(NUC, True)
    dense = NUC_DENSE
    out_sgn = 1 if signed_area(dense) > 0 else -1
    soft_shadow_path(doc, d, dx=2.4, dy=4.0, strength=0.07, blur=9, steps=5)
    g = doc.radgrad([(0, '#F9F7FE'), (0.45, '#E9E3F7'), (0.82, '#D7CEEF'), (1, '#C6BBE5')], cx=.4, cy=.36, r=.72, fx=.33, fy=.27)
    path(doc, d, fill=g)
    cid = doc.uid('nucclip')
    doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
    doc.add('<g clip-path="url(#%s)">' % cid)
    for k in range(7):
        path(doc, d, fill='none', stroke='#B4A7DB', w=28 - k * 3.6, op=0.05)
    rnd = random.Random(8)
    n = len(dense)
    base = offset_poly(dense, -out_sgn * 2.6, closed=True)
    # heterochromatin hugging the lamina
    for st_f in (0.02, 0.12, 0.23, 0.35, 0.47, 0.58, 0.69, 0.8, 0.9):
        st = int(n * st_f)
        ln = rnd.randint(int(n * 0.05), int(n * 0.09))
        amp = rnd.uniform(7.0, 11.0)
        k1, ph = rnd.uniform(2.5, 4.5), rnd.uniform(0, 6.28)
        idx = [(st + i) % n for i in range(ln)]
        outer = [base[i] for i in idx]
        inn = []
        for j, i in enumerate(idx):
            t = j / (ln - 1)
            th = amp * math.sin(math.pi * t) ** 0.6 * (0.72 + 0.32 * math.sin(t * k1 * 6.28 + ph))
            p, q = dense[i], base[i]
            vx, vy = q[0] - p[0], q[1] - p[1]
            L = math.hypot(vx, vy) or 1
            inn.append((q[0] + vx / L * th, q[1] + vy / L * th))
        poly = outer + inn[::-1]
        path(doc, cr_path(poly[::3] if len(poly) > 24 else poly, True), fill='#8073BE', stroke='#5F539D', w=0.45, op=0.6)
    # free heterochromatin foci + a few chromatin threads
    for (fx, fy, frx, fry, sd) in [(-52, -30, 8, 5, 1), (40, -42, 6.5, 4.2, 2), (52, 22, 7, 4.6, 3), (-58, 30, 6, 4, 4),
                                   (-10, 46, 5.5, 3.6, 6), (12, -8, 4.6, 3.2, 7)]:
        path(doc, blob(cx + fx, cy + fy, frx, fry, n=8, j=0.22, seed=sd, rot=rnd.uniform(0, 180)), fill='#8073BE', stroke='#5F539D', w=0.35, op=0.45)
    for _ in range(6):
        x0, y0 = cx + rnd.uniform(-rx * 0.7, rx * 0.7), cy + rnd.uniform(-ry * 0.6, ry * 0.6)
        pts = [(x0, y0)]
        for _ in range(4):
            pts.append((pts[-1][0] + rnd.uniform(-9, 9), pts[-1][1] + rnd.uniform(-7, 7)))
        path(doc, cr_path(pts, False), stroke='#6D61AE', w=0.45, op=0.3)
    xs = [p[0] for p in NUC]; ys = [p[1] for p in NUC]
    pts = []
    while len(pts) < 900:
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys))
        if inside(dense, x, y):
            pts.append((x, y))
    doc.add('<path d="%s" fill="none" stroke="#6D61AE" stroke-width="0.6" stroke-linecap="round" opacity="0.3"/>' % dots_path(pts))
    doc.add('</g>')
    # double envelope (outer + inner membrane, pale perinuclear space)
    path(doc, d, fill='none', stroke='#5B5096', w=4.6)
    path(doc, d, fill='none', stroke='#F2EEFB', w=2.7)
    path(doc, poly_d(offset_poly(dense, out_sgn * 1.8, True), True), stroke='#FFFFFF', w=0.35, op=0.35)
    # ribosomes on the outer nuclear membrane (it is continuous with the rough ER)
    ribosomes_along(doc, offset_poly(dense, out_sgn * 3.2, True), spacing=4.2, off=0.0, r=0.62, seed=4, skip=0.45)
    # nuclear pores
    res = resample(dense, poly_len(dense, True) / 30, closed=True)
    nm = normals(res, closed=True)
    for p, nn in zip(res, nm):
        ang = math.degrees(math.atan2(nn[1], nn[0]))
        doc.add('<g transform="translate(%s %s) rotate(%s)"><rect x="-3.0" y="-1.3" width="6.0" height="2.6" rx="1.0" fill="#4B428C"/>'
                '<path d="M-2.5,0 L2.5,0" stroke="#E8E3F7" stroke-width="0.6" stroke-linecap="round"/></g>' % (fmt(p[0]), fmt(p[1]), fmt(ang)))
    # nucleolus
    nx, ny, nr = cx - 14, cy - 12, 15
    contact_shadow(doc, nx, ny, nr, strength=0.14)
    path(doc, blob(nx, ny, nr, nr * 0.88, n=9, j=0.06, seed=3), fill=shade(doc, '#8B80C6', light=0.42, dark=0.22), stroke='#594E95', w=0.6)
    for (fx, fy, fr) in [(-3, 3, 3.0), (5, -4, 2.2), (6, 5, 1.8), (-6, -5, 1.7), (1, -1, 1.2)]:
        circ(doc, nx + fx, ny + fy, fr, fill='#5D529C', op=0.7)
    spec(doc, nx, ny, nr, a0=200, a1=250, op=0.75, inset=0.74, w=1.3)


def envelope_point(target):
    """Point on the nuclear envelope nearest to target, and its outward normal."""
    from style import signed_area
    i = min(range(len(NUC_DENSE)), key=lambda k: (NUC_DENSE[k][0] - target[0]) ** 2 + (NUC_DENSE[k][1] - target[1]) ** 2)
    nm = normals(NUC_DENSE, True)
    sg = 1 if signed_area(NUC_DENSE) > 0 else -1
    return NUC_DENSE[i], (nm[i][0] * sg, nm[i][1] * sg)


# ------------------------------------------------------------------ rough ER: sheets leave the envelope toward 3.1
ER_LEFT = (V.BANDS['3.1 ER'][0], (V.BANDS['3.1 ER'][1] + V.BANDS['3.1 ER'][3]) / 2)   # left end of the ER band


def _er_sheet_pts(start_t, mids, end):
    (ex, ey), (nx, ny) = envelope_point(start_t)
    return [(ex - nx * 3.5, ey - ny * 3.5), (ex + nx * 10, ey + ny * 10)] + mids + [end]


ER_SHEETS = [
    _er_sheet_pts((515, 180), [(552, 178), (586, 186), (620, 190), (654, 186), (690, 181), (720, 171)], (745, 163)),
    _er_sheet_pts((543, 212), [(580, 214), (612, 208), (646, 210), (682, 202), (716, 189)], (747, 177)),
    _er_sheet_pts((553, 244), [(588, 242), (620, 233), (652, 232), (684, 220), (713, 204)], (746, 190)),
]
ER_PERI = [(372, 190), (384, 168), (408, 152), (440, 146), (472, 148)]      # perinuclear sheet over the nucleus


def cisterna(doc, pts, w=7.0, seed=1, fill='#D3E3F8', line_c='#2D5FA8', ribo=True, start_open=False):
    """A flattened rough-ER cisterna: a lumen of gently varying width (dilated rims, pinched waists), lit from the
    top left, studded with ribosomes on its cytosolic faces."""
    rnd = random.Random(seed)
    dense = resample(cr_sample(pts, closed=False, per=12), 0.8, closed=False)
    n = len(dense)
    nm = normals(dense, closed=False)
    k1, k2, ph = rnd.uniform(5, 8), rnd.uniform(11, 16), rnd.uniform(0, 6.3)
    half = []
    for i in range(n):
        t = i / (n - 1)
        h = w / 2 * (0.82 + 0.16 * math.sin(t * k1 + ph) + 0.08 * math.sin(t * k2 + 2 * ph))
        end = min(1.0, (n - i) / 5.0, 1.0 if start_open else (i + 1) / 5.0) ** 0.5     # rounded ends
        half.append(max(0.9, h * end))
    left = [(p[0] + q[0] * h, p[1] + q[1] * h) for p, q, h in zip(dense, nm, half)]
    right = [(p[0] - q[0] * h, p[1] - q[1] * h) for p, q, h in zip(dense, nm, half)]
    outline = poly_d(left + right[::-1], True)
    path(doc, outline, fill='none', stroke='#8E6F66', w=1.6, op=0.08, extra='transform="translate(0.7 1.3)"')
    path(doc, outline, fill=sheen(doc, fill, light=0.5, dark=0.14), stroke=tone(line_c, 0.18), w=0.75)
    lit = left if sum(p[1] for p in left) < sum(p[1] for p in right) else right
    path(doc, poly_d([(x, y) for (x, y), (px, py) in zip(lit[3:-3], dense[3:-3])]), stroke='#FFFFFF', w=0.55, op=0.55)
    if ribo:
        for side, sd in ((1, 0), (-1, 7)):
            edge = [(p[0] + q[0] * (h + 1.25) * side, p[1] + q[1] * (h + 1.25) * side) for p, q, h in zip(dense, nm, half)]
            ribosomes_along(doc, edge[2:-2], spacing=3.3, off=0.0, r=0.82, seed=seed + sd, skip=0.15)


def rough_er(doc):
    for i, s in enumerate(ER_SHEETS):
        cisterna(doc, s, w=7.6, seed=10 + i, start_open=True)
    cisterna(doc, ER_PERI, w=6.2, seed=31)


# ------------------------------------------------------------------ cytoskeleton + other organelles
MITOS = [(452, 500, 30, 13, -24, 1), (398, 398, 34, 14, 18, 2), (505, 430, 32, 14, -12, 3), (520, 520, 28, 13, 36, 4),
         (733, 520, 30, 13, 78, 5), (268, 718, 30, 13, -8, 6), (880, 470, 26, 12, -6, 7), (560, 372, 22, 11, -30, 8),
         (712, 724, 26, 12, 8, 9)]


def misc_organelles(doc):
    for (x, y, L, Wd, rot, sd) in MITOS:
        mito(doc, x, y, L, Wd, rot=rot, seed=sd)
    rnd = random.Random(21)
    from style import inside
    for _ in range(160):                          # free polysomes / glycogen speckle
        x, y = rnd.uniform(160, 1000), rnd.uniform(120, 750)
        if inside(OUT, x, y):
            circ(doc, x, y, 0.55, fill='#7C8DB5', op=0.35)


def microtubules(doc):
    cx, cy = CENTRO
    rnd = random.Random(4)
    targets = [(330, 420), (300, 520), (380, 560), (470, 610), (560, 600), (700, 520), (860, 300), (900, 420),
               (760, 160), (640, 470), (230, 600), (420, 700)]
    for (tx, ty) in targets:
        mx, my = (cx + tx) / 2 + rnd.uniform(-18, 18), (cy + ty) / 2 + rnd.uniform(-18, 18)
        tx, ty = cx + (tx - cx) * 0.62, cy + (ty - cy) * 0.62
        mx, my = (cx + tx) / 2 + rnd.uniform(-10, 10), (cy + ty) / 2 + rnd.uniform(-10, 10)
        path(doc, cr_path([(cx, cy), (mx, my), (tx, ty)], False), stroke='#9AA2B4', w=0.45, op=0.22)
    # centrosome: pair of centrioles in a pericentriolar cloud
    circ(doc, cx, cy, 9, fill='#C9CCE0', op=0.25)
    circ(doc, cx, cy, 5.5, fill='#B9BDD6', op=0.3)
    centrosome(doc, cx, cy)


# ------------------------------------------------------------------ phagosome chain (zone B)
def rab_dots(doc, x, y, r, angles, color, rr=1.25):
    """Rab GTPases on the cytosolic face of a membrane: a small lit sphere on a short prenyl tether."""
    body = shade(doc, color, light=0.5, dark=0.16)
    dk = tone(color, 0.4)
    for a in angles:
        px, py = on_circle(x, y, r + 0.4, a)
        qx, qy = on_circle(x, y, r + 1.4 + rr, a)
        line(doc, px, py, qx, qy, dk, 0.35)
        circ(doc, qx, qy, rr, fill=body, stroke=dk, w=0.25)


def nox2(doc, x, y, cyt_deg, s=1.0):
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(cyt_deg + 90), fmt(s))]
    rt = cyt_deg + 90
    g.append('<rect x="-4.2" y="-1.9" width="8.4" height="3.8" rx="1.3" fill="%s" stroke="#7a0c37" stroke-width="0.42"/>' % shade_rot(doc, '#EBA3BE', rt, light=0.5, dark=0.12))
    hd = shade_rot(doc, INFL, rt, light=0.45, dark=0.2)
    for dx in (-3.6, 0, 3.6):
        g.append('<circle cx="%s" cy="-5.2" r="1.9" fill="%s" stroke="#7a0c37" stroke-width="0.33"/>' % (dx, hd))
    g.append('<path d="M0,-2 L0,3.8" stroke="#7a0c37" stroke-width="0.5" stroke-dasharray="0.6 0.7"/>')
    g.append('</g>')
    doc.add(''.join(g))


def _phago(doc, c, fill, stroke, w, lumen_glow):
    x, y, r = c
    vesicle(doc, x, y, r, fill=fill, stroke=stroke, w=w)
    g = doc.radgrad([(0, lumen_glow, 0.0), (0.7, lumen_glow, 0.0), (1, lumen_glow, 0.35)])
    circ(doc, x, y, r - 1.6, fill=g)


def _degraded(doc, x, y, L, Wd, rot, seed, frac):
    """A bacterium being digested: shrunken, paler, envelope breaking up into fragments (frac 0 = intact .. 1)."""
    rnd = random.Random(seed)
    group(doc, opacity=fmt(1 - 0.35 * frac))
    bacterium(doc, x, y, L=L, W=Wd, rot=rot, lps=frac < 0.3, flagella=False, seed=seed)
    endgroup(doc)
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    # pale digested patches on the envelope
    for _ in range(int(2 + 5 * frac)):
        u, v = rnd.uniform(-L * 0.38, L * 0.38), rnd.choice((-1, 1)) * Wd * rnd.uniform(0.32, 0.5)
        ell(doc, x + u * ca - v * sa, y + u * sa + v * ca, rnd.uniform(1.6, 2.8), rnd.uniform(1.0, 1.6), fill='#F6E9E2',
            rot=rot, op=0.85)
    # envelope fragments + debris drifting in the lumen
    for _ in range(int(3 + 10 * frac)):
        u, v = rnd.uniform(-L * 0.75, L * 0.75), rnd.uniform(-Wd * 1.3, Wd * 1.3)
        if abs(u) < L * 0.45 and abs(v) < Wd * 0.55:
            continue
        px, py = x + u * ca - v * sa, y + u * sa + v * ca
        r0 = rnd.uniform(1.2, 2.6)
        a0 = rnd.uniform(0, 360)
        p1 = on_circle(px, py, r0, a0)
        p2 = on_circle(px, py, r0, a0 + 110)
        path(doc, 'M%s,%s A%s,%s 0 0 1 %s,%s' % (fmt(p1[0]), fmt(p1[1]), fmt(r0), fmt(r0), fmt(p2[0]), fmt(p2[1])),
             stroke='#6A781E', w=0.7, op=0.75)
    for _ in range(int(4 + 10 * frac)):
        u, v = rnd.uniform(-L * 0.7, L * 0.7), rnd.uniform(-Wd * 1.2, Wd * 1.2)
        circ(doc, x + u * ca - v * sa, y + u * sa + v * ca, rnd.uniform(0.4, 0.9), fill='#8C9A3A', op=0.75)


def _free_arc(a):
    """True if angle a (deg) lies outside LATE's reserved docking arc."""
    a = (a + 360) % 360
    lo, hi = (LATE_DOCK_ARC[0] + 360) % 360, LATE_DOCK_ARC[1]
    return not (a >= lo or a <= hi)


def phagosomes(doc):
    # 2.3 nascent phagosome: just sealed, plasma-membrane receptors still on it, NOX2 -> ROS, first Rab5
    x, y, r = NP
    _phago(doc, NP, NP_FILL, NP_STROKE, 0.95, '#E8A08C')
    bacterium(doc, x, y, L=50, W=21, rot=62, lps=True, flagella=False, seed=9)
    for a in (205, 290, 110, 20):
        px, py = on_circle(x, y, r, a)
        receptor(doc, px, py, h=5.0, rot=a + 90, color='#3E5C86', kind='fc', tail=False)
    for a in (330, 160):
        px, py = on_circle(x, y, r, a)
        nox2(doc, px, py, a, s=1.0)
        for (k, rr) in ((-14, 9), (10, 12), (0, 17)):
            qx, qy = on_circle(x, y, r - rr, a + k)
            ros(doc, qx, qy, s=0.9)
    rab_dots(doc, x, y, r, (240, 60), RAB5, rr=1.3)
    # 2.4 early phagosome: Rab5 coat, first V-ATPases (pH ~6.5)
    x, y, r = EP
    _phago(doc, EP, EE_FILL, EE_STROKE, 1.0, '#F2B978')
    _degraded(doc, x, y, 44, 18, 18, 10, 0.25)
    px, py = on_circle(x, y, r, 300)
    nox2(doc, px, py, 300, s=1.0)
    ros(doc, *on_circle(x, y, r - 10, 296), s=0.9)
    for a in (180, 65):
        vatpase(doc, *on_circle(x, y, r, a), a, s=0.78)
    for (dx, dy) in ((-22, 12), (20, -16)):
        hplus(doc, x + dx, y + dy, 0.95)
    rab_dots(doc, x, y, r, (95, 125, 150, 205, 228, 250, 318, 345, 15, 40), RAB5, rr=1.4)
    # 2.5 late phagosome: Rab7 has replaced Rab5, more V-ATPase (pH ~5.5), cargo partly digested.
    # The upper-right arc is left free for the docking lysosomes (zone E).
    x, y, r = LP
    _phago(doc, LP, LE_FILL, LE_STROKE, 1.05, '#E58E7C')
    circ(doc, x, y, r - 2.8, fill='none', stroke='#8A5A4A', w=0.7, dash='0.2 1.1', op=0.7)
    _degraded(doc, x, y, 34, 14.5, -12, 11, 0.75)
    for a in (35, 80, 125, 165, 215):
        vatpase(doc, *on_circle(x, y, r, a), a, s=0.78)
    rnd = random.Random(5)
    for _ in range(9):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(14, r - 7)
        hplus(doc, x + rr * math.cos(a), y + rr * math.sin(a), 0.95)
    rab_dots(doc, x, y, r, [a for a in (55, 100, 145, 190, 235, 250) if _free_arc(a)], RAB7, rr=1.4)
    rab_dots(doc, x, y, r, (172,), RAB5, rr=1.1)        # the last Rab5 being exchanged


def early_endosomes(doc):
    """Two small Rab5 early endosomes that exchange content with the early phagosome (kiss-and-run)."""
    for (ex, ey, er_) in (EE1, EE2):
        vesicle(doc, ex, ey, er_, fill=EE_FILL, stroke=EE_STROKE, w=0.8)
        rab_dots(doc, ex, ey, er_, (30, 150, 260), RAB5, rr=1.0)


# ------------------------------------------------------------------ actin (helpers shared with zone owners)
def _cell_clip(doc):
    return cell_clip(doc)


def actin_network(doc, seg, depth=13.0, step=2.2, seed=7, w=0.42, op=0.92, arp=True, wash=0.09, gens=3):
    """Dendritic (Arp2/3-branched, 70 deg) F-actin under a stretch of plasma membrane, clipped to the cell."""
    from style import inside, dots_path
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

    for i in range(len(res)):
        if rnd.random() < 0.35:
            continue
        p = res[i]
        o = (-sg * nm[i][0], -sg * nm[i][1])
        s0 = depth * rnd.uniform(0.45, 1.0)
        side = rnd.choice((-1, 1))
        d = rot(o, side * (35 + rnd.uniform(-7, 7)))
        grow((p[0] - o[0] * s0, p[1] - o[1] * s0), o, s0, d, side, 1)
    doc.add('<g clip-path="url(#%s)">' % cell_clip(doc))
    if wash:
        path(doc, poly_d(res), stroke=ACTIN, w=depth * 1.7, op=wash)
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/>' % (
        ''.join(fil), ACTIN, fmt(w), op))
    if arp and nodes:
        doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/>' % (
            dots_path(nodes), ARP, fmt(w * 2.5), op))
    doc.add('</g>')


def cortex_mesh(doc, seg, depth=5.5, step=1.15, seed=17, w=0.32, op=0.6):
    """Resting cortex: a thin cross-linked F-actin meshwork running roughly parallel to the membrane."""
    from style import inside
    rnd = random.Random(seed)
    res = resample(seg, step, closed=False)
    nm = normals(res, closed=False)
    mid = len(res) // 2
    sg = 1 if inside(OUT, res[mid][0] + nm[mid][0] * 4, res[mid][1] + nm[mid][1] * 4) else -1
    n = len(res)
    out = []
    for i, (p, q) in enumerate(zip(res, nm)):
        fade = min(1.0, (n - 1 - i) / (n * 0.15), i / (n * 0.15))
        if rnd.random() > 0.35 + 0.65 * fade:
            continue
        s = rnd.uniform(1.8, depth) * (0.6 + 0.4 * fade)
        cx, cy = p[0] + sg * q[0] * s, p[1] + sg * q[1] * s
        tx, ty = -q[1], q[0]
        a = math.radians(rnd.uniform(-32, 32))
        dx, dy = tx * math.cos(a) + sg * q[0] * math.sin(a), ty * math.cos(a) + sg * q[1] * math.sin(a)
        L = rnd.uniform(2.2, 4.6)
        out.append('M%s,%sL%s,%s' % (fmt(cx - dx * L / 2), fmt(cy - dy * L / 2), fmt(cx + dx * L / 2), fmt(cy + dy * L / 2)))
    doc.add('<g clip-path="url(#%s)"><path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/></g>' % (
        cell_clip(doc), ''.join(out), ACTIN, fmt(w), op))


# ------------------------------------------------------------------ route ribbons (painted, under the content)
def _jitter(pts, amp, seed):
    rnd = random.Random(seed)
    return [pts[0]] + [(x + rnd.uniform(-amp, amp), y + rnd.uniform(-amp, amp)) for x, y in pts[1:-1]] + [pts[-1]]


def _wash(doc, pts, stops, w, seed, passes=3, x1=None, y1=None, x2=None, y2=None):
    """Watercolour-like ribbon: several jittered passes of stacked, widening translucent strokes (feathered edge),
    coloured by a gradient along the route, plus a slightly darker 'pigment edge' on one pass."""
    (sx, sy), (ex, ey) = pts[0], pts[-1]
    grad = ug(doc, 'linear', stops, x1=sx if x1 is None else x1, y1=sy if y1 is None else y1,
              x2=ex if x2 is None else x2, y2=ey if y2 is None else y2)
    for p in range(passes):
        q = _jitter(pts, 7, seed + p)
        dense = cr_sample(q, closed=False, per=16)
        d = poly_d(dense)
        for k, f in enumerate((1.55, 1.3, 1.1, 0.92, 0.75, 0.55)):
            path(doc, d, stroke=grad, w=w * f * (1 + 0.06 * p), op=0.16 + 0.03 * k, cap='round')
        if p == 1:
            for side in (1, -1):
                path(doc, poly_d(offset_poly(dense, side * w * 0.52, closed=False)), stroke=grad, w=1.6, op=0.18)


def _flow_marks(doc, pts, color, every=46, start=40, size=3.2, op=0.55):
    """Small soft chevrons along the route (flow direction), not arrows."""
    dense = cr_sample(pts, closed=False, per=16)
    L = poly_len(dense)
    s = start
    while s < L - 30:
        x, y, ang = pt_on(dense, s / L)
        a = math.radians(ang)
        ca, sa = math.cos(a), math.sin(a)
        p1 = (x - ca * size + sa * size * 0.9, y - sa * size - ca * size * 0.9)
        p2 = (x + ca * size * 0.4, y + sa * size * 0.4)
        p3 = (x - ca * size - sa * size * 0.9, y - sa * size + ca * size * 0.9)
        path(doc, 'M%s,%s L%s,%s L%s,%s' % (fmt(p1[0]), fmt(p1[1]), fmt(p2[0]), fmt(p2[1]), fmt(p3[0]), fmt(p3[1])),
             stroke=color, w=1.1, op=op)
        s += every


RED_STOPS = [(0, '#F2B27A', 0.0), (0.16, '#F09A62', 0.3), (0.45, '#E86A50', 0.34), (0.8, '#D9485A', 0.34), (1, '#B8457E', 0.26)]
BLUE_STOPS = [(0, '#8DB4F0', 0.0), (0.2, '#7EA6EE', 0.22), (0.6, '#5E86E2', 0.22), (0.9, '#6E68D2', 0.22), (1, '#8456C4', 0.2)]


def ribbons(doc):
    """The two routes as wide painted bands under the content, converging at the phagolysosome (the V)."""
    doc.add('<g clip-path="url(#%s)">' % cell_clip(doc))
    _wash(doc, V.RED_ROUTE, RED_STOPS, 40, seed=3)
    _wash(doc, V.BLUE_ROUTE, BLUE_STOPS, 36, seed=11)
    # convergence pool at the phagolysosome
    px, py, pr = PL
    pool = doc.radgrad([(0, '#A060C8', 0.22), (0.6, '#A060C8', 0.12), (1, '#A060C8', 0.0)])
    circ(doc, px, py, pr * 1.6, fill=pool)
    ribbon_marks(doc)
    doc.add('</g>')


def ribbon_marks(doc):
    _flow_marks(doc, V.RED_ROUTE[1:], '#D9563E', every=44, start=30)
    _flow_marks(doc, V.BLUE_ROUTE, '#4C78D8', every=58, start=36)


# ------------------------------------------------------------------ draw
def draw_cell(doc):
    plasma_membrane(doc)
    ribbons(doc)
    microtubules(doc)
    misc_organelles(doc)
    rough_er(doc)
    nucleus(doc)
    early_endosomes(doc)
    phagosomes(doc)
