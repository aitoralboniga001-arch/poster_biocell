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
FIBRE = ((753, 366), (952, 351))
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
    sheets = [
        [(618, 208), (655, 198), (700, 210), (745, 199), (786, 210), (808, 224)],
        [(622, 248), (660, 242), (704, 254), (752, 244), (795, 258), (818, 272)],
        [(612, 290), (654, 292), (700, 304), (750, 298), (792, 312), (822, 326)],
    ]
    for i, s in enumerate(sheets):
        er_sheet(doc, s, w=8.4, ribo=True, seed=10 + i, ribo_r=1.0)
    er_sheet(doc, [(436, 232), (404, 214), (366, 224), (340, 254), (332, 292)], w=7.0, seed=31, ribo_r=0.95)
    er_sheet(doc, [(448, 306), (420, 326), (396, 352)], w=7.0, seed=32, ribo_r=0.95)


def golgi_and_tgn(doc):
    cx, cy = GOLGI_C
    cis = golgi(doc, cx, cy, w=150, n=5, gap=10.2, thick=6.0)
    ty = TGN_Y
    tg = cr_path([(cx - 66, ty + 2), (cx - 36, ty - 7), (cx, ty + 3), (cx + 36, ty - 6), (cx + 70, ty + 4)], False)
    from style import contact_shadow as _cs
    tgp = [(cx - 66, ty + 2), (cx - 36, ty - 7), (cx, ty + 3), (cx + 36, ty - 6), (cx + 70, ty + 4)]
    path(doc, tg, stroke='#9B7D6E', w=7.4, op=0.12, extra='transform="translate(0.8 1.6)"')
    path(doc, tg, stroke='#1F5A7E', w=7.0)
    path(doc, tg, stroke='#4A95BD', w=5.2)
    dn = cr_sample(tgp, closed=False, per=10)[1:-1]
    path(doc, poly_d([(x, y + 1.0) for x, y in dn]), stroke='#3A7FA8', w=1.6, op=0.8)
    path(doc, poly_d([(x, y - 1.25) for x, y in dn]), stroke='#A9D3EA', w=1.0, op=0.9)
    for dx, dy in [(-58, 11), (-20, 12), (22, 12), (58, 13)]:
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
    for dx in (-52, -26, 4, 30, 56):
        m6pr(doc, cx + dx, TGN_Y - 5, s=0.9, rot=180)
    for dx in (-52, 4, 56):
        hydrolase(doc, cx + dx, TGN_Y - 17, s=0.7, rot=0, p=True)


def sorting_and_endosomes(doc):
    cx = GOLGI_C[0]
    for (x, y) in CCV:
        contact_shadow(doc, x, y, 10.4, strength=0.12)
        vesicle(doc, x, y, 8.0, fill='#EAF4FA', stroke='#1D5F86', w=0.58)
        clathrin(doc, x, y, 9.8)
        hydrolase(doc, x, y - 0.6, s=0.62, rot=0, p=True)
        m6pr(doc, x, y + 8.0, s=0.7, rot=0)
    x, y, r = LE
    vesicle(doc, x, y, r, fill=LE_FILL, stroke=LE_STROKE, w=0.9)
    for (ix, iy, ir) in ((x - 6, y - 2, 6), (x + 7, y + 7, 4.5)):
        circ(doc, ix + 0.4, iy + 0.7, ir, fill=tone(LE_STROKE, 0.1), op=0.12)
        circ(doc, ix, iy, ir, fill=shade(doc, '#FCEBE5', light=0.6, dark=0.06), stroke=tone(LE_STROKE, 0.12), w=0.6)
        spec(doc, ix, iy, ir, a0=200, a1=245, op=0.8, inset=0.72, w=0.5)
    for (dx, dy) in [(-8, -8), (4, -9), (3, 2), (-9, 6), (12, -2), (-1, 12)]:
        hydrolase(doc, x + dx, y + dy, s=0.5, rot=random.Random(int(dx * 7 + dy)).uniform(-40, 40), glycan=False)
    for a in (190, 262, 20):
        px, py = on_circle(x, y, r, a)
        m6pr(doc, px, py, s=0.75, rot=a + 90)
    for a in (130, 310):
        px, py = on_circle(x, y, r, a)
        vatpase(doc, px, py, a, s=0.7)
    ex, ey, er_ = EE1
    vesicle(doc, ex, ey, er_, fill=EE_FILL, stroke=EE_STROKE, w=0.8)
    hydrolase(doc, ex, ey, s=0.4, glycan=False)
    ex, ey, er_ = EE2
    vesicle(doc, ex, ey, er_, fill=EE_FILL, stroke=EE_STROKE, w=0.75)
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
    g.append('<rect x="-4.2" y="-1.9" width="8.4" height="3.8" rx="1.3" fill="%s" stroke="#8c1040" stroke-width="0.42"/>' % shade_rot(doc, '#F8C8DA', rt, light=0.5, dark=0.12))
    hd = shade_rot(doc, '#E75A8B', rt, light=0.45, dark=0.2)
    for dx in (-3.6, 0, 3.6):
        g.append('<circle cx="%s" cy="-5.2" r="1.9" fill="%s" stroke="#8c1040" stroke-width="0.33"/>' % (dx, hd))
    g.append('<path d="M0,-2 L0,3.8" stroke="#8c1040" stroke-width="0.5" stroke-dasharray="0.6 0.7"/>')
    g.append('</g>')
    doc.add(''.join(g))


def phagosomes(doc):
    # cup + bacteria -------------------------------------------------------------
    bacterium(doc, 266, 308, L=56, W=23, rot=-12, seed=4)
    bacterium(doc, 285, 407, L=54, W=23, rot=84, seed=6)
    cup_line = cr_sample([(272, 455), (300, 440), (313, 407), (299, 376), (270, 366)], closed=False, per=10)
    actin_cortex(doc, cup_line, seed=7, spacing=1.6, inward=-1, lens=(6, 15), w=0.65, spread=40)
    # nascent phagosome ----------------------------------------------------------
    x, y, r = NP
    vesicle(doc, x, y, r, fill='#FFE1D8', stroke=PHAG, w=0.9)
    bacterium(doc, x, y, L=36, W=15, rot=70, lps=True, flagella=False, seed=9, scale=1.0)
    for a in (200, 280, 80):
        px, py = on_circle(x, y, r, a)
        receptor(doc, px, py, h=4.5, rot=a + 90, color='#5A6B85', kind='fc', tail=False)
    for a in (335, 140):
        px, py = on_circle(x, y, r, a)
        nox2(doc, px, py, a, s=1.0)
        for (k, rr) in ((-14, 8), (10, 11), (0, 15)):
            qx, qy = on_circle(x, y, r - rr, a + k)
            ros(doc, qx, qy, s=0.85)
    # early phagosome ------------------------------------------------------------
    x, y, r = EP
    vesicle(doc, x, y, r, fill=EE_FILL, stroke=EE_STROKE, w=0.95)
    bacterium(doc, x, y, L=38, W=16, rot=20, lps=False, flagella=False, seed=10)
    px, py = on_circle(x, y, r, 300)
    nox2(doc, px, py, 300, s=1.0)
    ros(doc, *on_circle(x, y, r - 9, 296), s=0.85)
    # late phagosome -------------------------------------------------------------
    x, y, r = LP
    vesicle(doc, x, y, r, fill=LE_FILL, stroke=LE_STROKE, w=1.0)
    circ(doc, x, y, r - 2.6, fill='none', stroke='#8A5A4A', w=0.7, dash='0.2 1.1', op=0.8)
    bacterium(doc, x, y, L=38, W=16, rot=-14, lps=False, flagella=False, seed=11)
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
    for a in (200, 255, 320, 30, 110):
        x, y = on_circle(lx, ly, lr, a)
        vatpase(doc, x, y, a, s=0.75)
    for (x, y) in [(lx - 18, ly + 8), (lx - 10, ly + 19), (lx + 8, ly + 21), (lx + 20, ly - 8), (lx - 20, ly - 9), (lx + 14, ly + 8)]:
        hplus(doc, x, y, 1.0)
    for a in (190, 225, 285, 325, 15, 55, 95, 140):
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
    path(doc, ph, stroke=PHAG, w=50, op=0.11, cap='round')
    bio = cr_path([(690, 262), (640, 300), (614, 340), (606, 392), (606, 440), (568, 482), (546, 524), (530, 580), (560, 622), (604, 640)], False)
    path(doc, bio, stroke=BIO, w=44, op=0.10, cap='round')


def draw_cell(doc):
    plasma_membrane(doc)
    ribbons(doc)
    misc_organelles(doc)
    nucleus(doc)
    rough_er(doc)
    cis = golgi_and_tgn(doc)
    er_exit_and_golgi_cargo(doc, cis)
    phagosomes(doc)
    sorting_and_endosomes(doc)
    phago_details(doc)
