"""Section 3: hydrolase-journey strip (right column, top) -- the molecular biography of ONE lysosomal hydrolase.

Read top -> bottom, like the cell (ER at the top, lysosome below).  Every compartment is a short magnified fragment:
a band of lumen between two toned bilayers that dissolves into the paper at both ends (no boxes).  The same cobalt
hydrolase, with its N-glycan tree, appears once per compartment along a gentle S-path:

    3.1 rough ER  ->  COPII  ->  3.2 cis-Golgi  ->  3.3 TGN / 3.4 clathrin bud  ->  3.5 endosome  ->  3.6 lysosome

Drawn in poster mm (not inside the cell transform)."""
import math, random
from lib import *
from bio import vatpase, hplus, m6pr, copii
from style import shade, spec, tone, lighten, mix, contact_shadow
import geom as G
from layout2 import heading
from stage import caption
from lenses import _ugrad, _hair, LINK
from annot2 import tag, DBIO, DGOL, DLE, DLY

HYD = BIO                     # hydrolase identity (cobalt)
GOLD = '#E2B33C'              # M6P phosphate identity
M6PR_C = '#1E8A5A'            # M6P receptor identity
CLATH = '#6B7C93'             # clathrin identity (grey-blue)
ENZ = '#9A8F80'               # processing enzymes / chaperone: warm neutral (not poster identities)
LAMP_C = '#8E7BB0'
GLCNAC = '#22407E'            # SNFG-style glycan symbols, tuned to the cobalt family
MAN = '#9DC0F2'
GLC = '#F4F1EA'
SMALL = '#5A6573'             # in-figure annotation colour
NAME_S, NOTE_S, MINI_S = 5.6, 4.6, 4.3

# compartment palette (lumen tint, membrane tone) -- the same hues as the organelles in the cell
ER_C = ('#D3E3F8', '#3D6AAE')
CIS_C = ('#D4ECF6', '#2F7FA8')
TGN_C = ('#B9DCEE', '#1F5A7E')
END_C = ('#F8D9CF', '#C23B2A')
LYS_C = ('#E6D7F4', '#6F36A8')


# ============================================================================== primitives
def _uv(x0, y0, ang, k):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return lambda u, v: (x0 + k * (u * c - v * s), y0 + k * (u * s + v * c))


# N-glycan (local units, u along the tree, v across it).  Man9GlcNAc2 core + Glc3 on the A arm.
_GN = {'N1': (1.0, 0), 'N2': (2.0, 0), 'M0': (3.0, 0),
       'A1': (3.85, -0.85), 'A2': (4.75, -1.3), 'A3': (5.7, -1.5),
       'B1': (3.85, 0.85), 'B2a': (4.75, 0.45), 'B3a': (5.7, 0.35), 'B2b': (4.75, 1.45), 'B3b': (5.7, 1.85),
       'G1': (6.65, -1.6), 'G2': (7.6, -1.65), 'G3': (8.55, -1.7),
       'P': (6.75, -1.6), 'PN': (7.85, -1.65)}
_GE = [('S', 'N1'), ('N1', 'N2'), ('N2', 'M0'), ('M0', 'A1'), ('A1', 'A2'), ('A2', 'A3'), ('M0', 'B1'), ('B1', 'B2a'),
       ('B2a', 'B3a'), ('B1', 'B2b'), ('B2b', 'B3b')]


def _square(doc, x, y, h, k):
    rect(doc, x - h, y - h, 2 * h, 2 * h, fill=GLCNAC, stroke='#0F2350', sw=0.12 * k, r=0.15)


def glycan(doc, x0, y0, ang, mode='trim', k=2.1, glc_fade=False):
    """N-glycan rooted at the Asn (x0, y0), growing toward `ang` (deg).
    mode: 'full' (Glc3Man9GlcNAc2), 'trim' (Man9GlcNAc2), 'gnp' (+ GlcNAc-1-P on the A-arm mannose),
          'm6p' (+ exposed phosphate).  Returns the global positions of the nodes."""
    f = _uv(x0, y0, ang, k)
    P = {n: f(*uv) for n, uv in _GN.items()}
    P['S'] = (x0, y0)
    edges = list(_GE)
    if mode == 'full':
        edges += [('A3', 'G1'), ('G1', 'G2'), ('G2', 'G3')]
    if mode in ('gnp', 'm6p'):
        edges += [('A3', 'P')]
    if mode == 'gnp':
        edges += [('P', 'PN')]
    path(doc, ''.join('M%s,%sL%s,%s' % (fmt(P[a][0]), fmt(P[a][1]), fmt(P[b][0]), fmt(P[b][1])) for a, b in edges),
         stroke='#1E3B6E', w=0.15 * k)
    rs = 0.40 * k
    for n in ('N1', 'N2'):
        _square(doc, P[n][0], P[n][1], rs * 0.92, k)
    mf = shade(doc, MAN, light=0.5, dark=0.12)
    for n in ('M0', 'A1', 'A2', 'A3', 'B1', 'B2a', 'B3a', 'B2b', 'B3b'):
        circ(doc, P[n][0], P[n][1], rs, fill=mf, stroke='#1E3B6E', w=0.11 * k)
    if mode == 'full':
        for i, n in enumerate(('G1', 'G2', 'G3')):
            circ(doc, P[n][0], P[n][1], rs, fill=GLC, stroke='#6E6A60', w=0.11 * k, op=(0.85 - 0.2 * i) if glc_fade else None)
    if mode in ('gnp', 'm6p'):
        phosphate(doc, P['P'][0], P['P'][1], rs * 1.3)
    if mode == 'gnp':
        _square(doc, P['PN'][0], P['PN'][1], rs * 0.92, k)
    return P


def phosphate(doc, x, y, r):
    circ(doc, x, y, r, fill=shade(doc, GOLD, light=0.45, dark=0.14), stroke='#7A5A00', w=0.28)
    T(doc, x, y + r * 0.5, 'P', size=r * 1.45, weight=700, fill='#3B2D00', anchor='middle')


def hydrolase(doc, cx, cy, r, gang, mode='trim', k=2.1, patch=False, seed=3, glc_fade=False):
    """The one hydrolase: shaded cobalt globule, active-site cleft, lysine signal patch, N-glycan on an Asn."""
    ax, ay = cx + r * 0.92 * math.cos(math.radians(gang)), cy + r * 0.92 * math.sin(math.radians(gang))
    nodes = glycan(doc, ax, ay, gang, mode, k, glc_fade)
    contact_shadow(doc, cx, cy, r, strength=0.12)
    path(doc, blob(cx, cy, r, r * 0.9, n=9, j=0.06, seed=seed, rot=gang), fill=shade(doc, HYD, light=0.45, dark=0.2),
         stroke=tone(HYD, 0.45), w=0.4)
    ca = math.radians(gang + 180)                       # active-site cleft, opposite the glycan
    nx, ny = math.cos(ca), math.sin(ca)
    tx, ty = -ny, nx
    e = (cx + nx * r * 1.0, cy + ny * r * 1.0)
    i = (cx + nx * r * 0.25, cy + ny * r * 0.25)
    path(doc, 'M%s,%sL%s,%sL%s,%sZ' % (fmt(e[0] + tx * r * 0.36), fmt(e[1] + ty * r * 0.36), fmt(i[0]), fmt(i[1]),
                                       fmt(e[0] - tx * r * 0.36), fmt(e[1] - ty * r * 0.36)), fill='#F3F6FF')
    spec(doc, cx, cy, r, a0=200, a1=250, op=0.55, inset=0.74, w=max(0.4, r * 0.1))
    pts = []
    if patch:                                           # lysine-based signal patch (three Lys, '+')
        pa = math.radians(gang - 92)
        for d in (-30, 0, 30):
            a = pa + math.radians(d)
            px, py = cx + r * 0.74 * math.cos(a), cy + r * 0.74 * math.sin(a)
            pts.append((px, py))
            circ(doc, px, py, 1.0, fill='#E8EEFF', stroke='#0F2E78', w=0.22)
            doc.add('<path d="M%s,%sh1.2M%s,%sv1.2" stroke="#0F2E78" stroke-width="0.34" stroke-linecap="round"/>' % (
                fmt(px - 0.6), fmt(py), fmt(px), fmt(py - 0.6)))
    nodes['patch'] = pts
    return nodes


def _mask_x(doc, x0, x1, y0, y1, fade=16):
    """Horizontal feather: the fragment dissolves into the paper at both ends."""
    gid = doc.uid('mxg')
    a, b = fade / (x1 - x0), 1 - fade / (x1 - x0)
    doc.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="0" x2="%s" y2="0">'
                    '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="%s" stop-color="#fff"/>'
                    '<stop offset="%s" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                    % (gid, fmt(x0), fmt(x1), fmt(a), fmt(b)))
    mid = doc.uid('mx')
    doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
                    '<rect x="%s" y="%s" width="%s" height="%s" fill="url(#%s)"/></mask>'
                    % (mid, fmt(x0), fmt(y0), fmt(x1 - x0), fmt(y1 - y0), fmt(x0), fmt(y0), fmt(x1 - x0), fmt(y1 - y0), gid))
    return mid


def bilayer(doc, pts, col):
    """Toned bilayer (two leaflets with head-group beading, pale hydrophobic core), like the v6 plasma membrane."""
    d = poly_d(pts)
    path(doc, d, stroke=mix(col, '#FFFFFF', 0.25), w=2.5)
    path(doc, d, stroke=mix(col, '#FFFFFF', 0.86), w=1.05)
    for off in (0.92, -0.92):
        path(doc, poly_d(offset_poly(pts, off, closed=False)), stroke=tone(col, 0.2), w=0.62, dash='0.01 1.25', op=0.75)


def _wave(x0, x1, y, amp=0.7, ph=0.0, n=7):
    pts = [(x0 + (x1 - x0) * i / (n - 1), y + amp * math.sin(i * 1.7 + ph)) for i in range(n)]
    return cr_sample(pts, closed=False, per=10)


def yat(poly, x):
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1e-9)
    return poly[0][1] if x < poly[0][0] else poly[-1][1]


def compartment(doc, x0, x1, ytop, ybot, colors, ph=0.0, extra=None, gap=None, pad=(9, 9)):
    """Magnified fragment: lumen band between two bilayers, feathered at both ends.  Returns (top, bottom) polylines.
    gap = (xa, xb): opening in the bottom membrane (bud neck).  extra(doc, lum, mem) draws inside the feather."""
    lum, mem = colors
    tp = _wave(x0, x1, ytop, 0.8, ph)
    bt = _wave(x0, x1, ybot, 0.8, ph + 2.1)
    mid = _mask_x(doc, x0, x1, ytop - pad[0], ybot + pad[1])
    doc.add('<g mask="url(#%s)">' % mid)
    path(doc, poly_d(tp + bt[::-1], True), fill='none', stroke=lum, w=7, op=0.35)      # whisper of tint around it
    g = _ugrad(doc, 'linear', [(0, lighten(lum, 0.45), 1), (0.6, lum, 1), (1, mix(lum, mem, 0.12), 1)],
               x1=x0, y1=ytop, x2=x0 + 8, y2=ybot)
    path(doc, poly_d(tp + bt[::-1], True), fill=g)
    if extra:
        extra(doc, lum, mem)
    bilayer(doc, tp, mem)
    if gap:
        bilayer(doc, [p for p in bt if p[0] <= gap[0]], mem)
        bilayer(doc, [p for p in bt if p[0] >= gap[1]], mem)
    else:
        bilayer(doc, bt, mem)
    doc.add('</g>')
    return tp, bt


def tm_stub(doc, x, y, col, h=4.2, w=1.6):
    """Transmembrane segment crossing a horizontal bilayer at (x, y)."""
    rect(doc, x - w / 2, y - h / 2, w, h, fill=shade(doc, col, light=0.45, dark=0.15), stroke=tone(col, 0.4), sw=0.25, r=0.6)


def rect_rot(doc, x, y, w, h, ang, col):
    doc.add('<rect x="%s" y="%s" width="%s" height="%s" rx="0.6" fill="%s" stroke="%s" stroke-width="0.25" '
            'transform="rotate(%s %s %s)"/>' % (fmt(x - h / 2), fmt(y - w / 2), fmt(h), fmt(w), shade(doc, col, light=0.45, dark=0.15),
                                                tone(col, 0.4), fmt(ang), fmt(x), fmt(y)))


def receptor_tm(doc, x, y, toward, s=1.0):
    """M6PR crossing a membrane at (x, y): short cytosolic tail, TM segment, Y-shaped luminal domain pointing `toward`."""
    a = math.radians(toward)
    line(doc, x, y, x - math.cos(a) * 3.4, y - math.sin(a) * 3.4, tone(M6PR_C, 0.2), 0.8)
    rect_rot(doc, x, y, 1.5, 3.8, toward, M6PR_C)
    m6pr(doc, x + math.cos(a) * 1.4, y + math.sin(a) * 1.4, s=s, rot=toward + 90)
    return x + math.cos(a) * (1.4 + 7.2 * s), y + math.sin(a) * (1.4 + 7.2 * s)


def enzyme(doc, x, y, rx, ry, rot=0, seed=1, col=ENZ):
    path(doc, blob(x, y, rx, ry, n=8, j=0.1, seed=seed, rot=rot), fill=shade(doc, col, light=0.5, dark=0.16),
         stroke=tone(col, 0.4), w=0.35)


def mini(doc, x, y, s, anchor='start', fill=SMALL, italic=True, size=MINI_S):
    T(doc, x, y, s, size=size, fill=fill, anchor=anchor, italic=italic)


def step_label(doc, x, y, step, title, note, color, width, nfill=None, size=NAME_S):
    """Step tag + bold title + short note.  Returns the y of the last baseline."""
    w = (tag(doc, x, y - size * 0.14, step, color) + 2.0) if step else 0
    T(doc, x + w, y, title, size=size, weight=700, fill=color)
    if note:
        h = P(doc, x, y + NOTE_S * 1.3, note, width, size=NOTE_S, fill=nfill or color, lh=1.17)
        return y + NOTE_S * 1.3 + h - NOTE_S * 1.17
    return y


def journey(doc, pts, w=1.0, head=3.9, op=0.85):
    arrow(doc, pts, HYD, 'transport', w=w, head=head, opacity=op)


def lamp(doc, x, y, seed=1):
    """LAMP-1/2: TM stalk + two luminal domains densely coated with glycans (the lysosomal glycocalyx)."""
    rnd = random.Random(seed)
    tm_stub(doc, x, y, LAMP_C, h=3.8, w=1.3)
    line(doc, x, y + 1.6, x, y + 9.2, tone(LAMP_C, 0.25), 0.6)
    for (dy, rr) in ((4.2, 1.7), (8.0, 1.5)):
        circ(doc, x, y + dy, rr, fill=shade(doc, LAMP_C, light=0.45, dark=0.15), stroke=tone(LAMP_C, 0.4), w=0.25)
    for dy in (3.0, 4.4, 5.8, 7.0, 8.4, 9.6):
        for sgn in (-1, 1):
            px, py = x + sgn * (2.3 + rnd.uniform(0, 0.6)), y + dy + rnd.uniform(-0.4, 0.4)
            line(doc, x + (px - x) * 0.55, py, px, py, '#1E3B6E', 0.18, op=0.6)
            circ(doc, px, py, 0.55, fill=MAN, stroke='#1E3B6E', w=0.14)


def focus_link(doc, c, r, targets):
    """Hairline source ring at the exact in-cell site + two fine tangent hairlines that fade toward the strip."""
    col = mix(BIO, LINK, 0.55)
    circ(doc, c[0], c[1], r, fill='none', stroke=col, w=0.3, op=0.8)
    for q, sgn in zip(targets, (-1, 1)):
        d = math.hypot(q[0] - c[0], q[1] - c[1])
        a = math.atan2(q[1] - c[1], q[0] - c[0]) + sgn * math.acos(r / d)
        p = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
        _hair(doc, p, q, col, op0=0.7, op1=0.1, w=0.25)


def _arc(cx, cy, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


# ============================================================================== the strip
# V1.2b text diet: no caption, no notes.  Each compartment = step tag + NAME; molecules carry 1-word names.
# Every scene is drawn in its own (historical) local coordinates and placed with a uniform scale-up, so the strip
# grows into the space the caption used to take.
SC = 1.08
SCENES = {                      # scene: (old-coordinate origin, new poster position of that origin)
    'er': ((866, 143), (870, 119)),
    'copii': ((999, 196), (1041, 171)),
    'cis': ((866, 205), (870, 184)),
    'tgn': ((972, 236), (955, 222)),
    'end': ((866, 280), (870, 278)),
    'lys': ((952, 314), (933, 310)),
}
STEP_S = 6.2


def M(scene, x, y):
    (ox, oy), (ax, ay) = SCENES[scene]
    return ax + SC * (x - ox), ay + SC * (y - oy)


def _open(doc, scene):
    (ox, oy), (ax, ay) = SCENES[scene]
    doc.add('<g transform="translate(%s %s) scale(%s) translate(%s %s)">' % (fmt(ax), fmt(ay), SC, fmt(-ox), fmt(-oy)))


def _close(doc):
    doc.add('</g>')


def name_label(doc, x, y, step, title, color):
    step_label(doc, x, y, step, title, None, color, 100, size=STEP_S)


def draw(doc):
    x0, y0, x1, y1 = G.M6P
    heading(doc, x0, G.M6P_HEAD_Y, 3, 'Lysosome biogenesis')

    # ------------------------------------------------------------------ single quiet focus link: in-cell rough ER -> 3.1
    focus_link(doc, G.to_poster(791, 213), 6.5, [M('er', 870, 158.5), M('er', 870, 180.5)])

    # ------------------------------------------------------------------ 3.1 rough ER (scene left, label right)
    _open(doc, 'er')
    tp, bt = compartment(doc, 866, 988, 157, 181, ER_C, ph=0.3)
    sx = 891
    my = yat(tp, sx)
    for dx in (-2.3, 2.3):                              # Sec61 translocon
        rect(doc, sx + dx - 1.25, my - 2.9, 2.5, 5.8, fill=shade(doc, '#7D88A6', light=0.45, dark=0.15), stroke='#46506B', sw=0.25, r=0.9)
    ell(doc, sx + 1.5, my - 7.0, 7.4, 4.1, fill=shade(doc, '#5C6E9F', light=0.42, dark=0.18), stroke='#2E3B66', w=0.35)   # 60S
    ell(doc, sx + 0.5, my - 12.2, 5.6, 2.7, fill=shade(doc, '#8494C2', light=0.45, dark=0.15), stroke='#2E3B66', w=0.35)  # 40S
    path(doc, cr_path([(sx - 13, my - 12.6), (sx - 6, my - 11.6), (sx + 1, my - 12.9), (sx + 8, my - 11.8), (sx + 15, my - 12.8)], False),
         stroke='#7A4C8A', w=0.5)
    hx, hy, hr = 917, 170.5, 5.6
    path(doc, cr_path([(sx, my - 4.5), (sx, my + 2.5), (sx + 1.2, my + 7.0), (sx + 5, my + 10.5), (sx + 10, my + 13.2),
                       (hx - hr + 0.6, hy + 1.2)], False), stroke=HYD, w=0.7)       # nascent chain = the same molecule
    enzyme(doc, hx - 1.0, hy + hr + 2.1, 5.0, 2.3, rot=-6, seed=5)                  # BiP
    nd = hydrolase(doc, hx, hy, hr, -10, mode='full', k=2.3, seed=3, glc_fade=True)
    gx, gy = nd['G3']
    for (dx, dy, op) in ((4.0, -3.0, 0.8), (6.6, -0.6, 0.65), (8.8, -3.8, 0.5)):    # glucoses trimmed off
        circ(doc, gx + dx, gy + dy, 0.92, fill=GLC, stroke='#6E6A60', w=0.22, op=op)
    mini(doc, sx + 16.5, my - 11.2, 'mRNA')
    mini(doc, sx - 9.0, my - 2.6, 'Sec61', anchor='end')
    mini(doc, hx - 7.0, hy + hr + 10.8, 'BiP')
    mini(doc, gx + 12.0, gy - 1.0, 'Glc')
    _close(doc)
    name_label(doc, 1007, 146, '3.1', 'Rough ER', DBIO)

    # ------------------------------------------------------------------ COPII vesicle
    _open(doc, 'copii')
    vx, vy, vr = 999, 196, 7.4
    circ(doc, vx, vy, vr + 3.4, fill=ER_C[0], op=0.4)
    circ(doc, vx, vy, vr, fill=ER_C[0])
    bilayer(doc, _arc(vx, vy, vr, 0, 360, 40), ER_C[1])
    copii(doc, vx, vy, vr + 2.4, w=1.15)
    hydrolase(doc, vx - 2.6, vy + 0.4, 2.6, -15, mode='trim', k=0.9, seed=4)
    _close(doc)
    T(doc, 1056, 173.2, 'COPII', size=STEP_S, weight=700, fill=DBIO)
    journey(doc, [(997, 162.5), (1010, 167.5), (1026, 169.0)])
    journey(doc, [(1034, 184.5), (1018, 191.5), (1003, 193.5)])

    # glycan key (glyphs + one word each)
    ky, kx = 178.5, 875
    _square(doc, kx, ky - 1.5, 0.85, 2)
    mini(doc, kx + 2.4, ky, 'GlcNAc', italic=False)
    circ(doc, kx + 19.6, ky - 1.5, 0.9, fill=MAN, stroke='#1E3B6E', w=0.22)
    mini(doc, kx + 22.0, ky, 'mannose', italic=False)
    circ(doc, kx + 42.2, ky - 1.5, 0.9, fill=GLC, stroke='#6E6A60', w=0.22)
    mini(doc, kx + 44.6, ky, 'glucose', italic=False)
    phosphate(doc, kx + 63.8, ky - 1.5, 1.2)
    mini(doc, kx + 66.4, ky, 'phosphate', italic=False)

    # ------------------------------------------------------------------ 3.2 cis-Golgi (scene left, label right)
    _open(doc, 'cis')
    tp, bt = compartment(doc, 866, 990, 214, 236.5, CIS_C, ph=1.2)
    hx, hy, hr = 903, 228.0, 5.4
    nd = hydrolase(doc, hx, hy, hr, 4, mode='gnp', k=2.25, patch=True, seed=6)
    ex = 914
    ey = yat(tp, ex)
    tm_stub(doc, ex, ey, ENZ)                           # GlcNAc-1-phosphotransferase: Lys-patch lobe + catalytic lobe
    pt = nd['patch'][1]
    enzyme(doc, pt[0] + 0.6, pt[1] - 3.3, 4.6, 2.2, rot=-4, seed=8)
    enzyme(doc, nd['PN'][0] - 1.6, nd['PN'][1] - 4.2, 5.0, 2.3, rot=8, seed=9)
    path(doc, cr_path([(pt[0] + 4.6, pt[1] - 4.2), (ex, ey + 2.6), (nd['PN'][0] - 5.5, nd['PN'][1] - 5.2)], False), stroke=tone(ENZ, 0.3), w=0.9)
    mini(doc, pt[0] - 9.0, pt[1] - 0.6, 'Lys', anchor='end')
    mini(doc, pt[0] - 9.0, pt[1] + 4.2, 'patch', anchor='end')
    mini(doc, 950, 220.0, 'phosphotransferase')
    _close(doc)
    name_label(doc, 1009, 210, '3.2', 'cis-Golgi', DGOL)

    # ------------------------------------------------------------------ 3.3 TGN + 3.4 clathrin bud (scene right, label left)
    bty = 254.0
    bx, br, nh = 1015.0, 12.6, 6.4
    by = bty + math.sqrt(br * br - nh * nh)

    def _bud(doc_, lum, mem):
        circ(doc_, bx, by, br, fill=lum)
        a0 = math.degrees(math.atan2(bty - by, nh))
        bilayer(doc_, _arc(bx, by, br, a0, 180 - a0), mem)

    _open(doc, 'tgn')
    tp, bt = compartment(doc, 972, 1086, 241, bty, TGN_C, ph=2.4, extra=_bud, gap=(bx - nh, bx + nh), pad=(9, 34))
    ca0, ca1 = -12, 192                                # clathrin cage (outer) + AP-1 / GGA adaptors (inner), cytosolic face
    coat = _arc(bx, by, br + 4.2, ca0, ca1, 60)
    path(doc, poly_d(coat), stroke=CLATH, w=1.5, dash='2.2 1.0')
    path(doc, poly_d(coat), stroke=lighten(CLATH, 0.6), w=0.4, dash='2.2 1.0')
    for a in range(ca0 + 4, ca1, 13):
        p_, q_ = _arc(bx, by, br + 1.5, a, a, 1)[0], _arc(bx, by, br + 4.2, a, a, 1)[0]
        line(doc, p_[0], p_[1], q_[0], q_[1], CLATH, 0.45, op=0.8)
    for a in range(ca0 + 10, ca1 - 2, 13):
        p_ = _arc(bx, by, br + 2.5, a, a, 1)[0]
        circ(doc, p_[0], p_[1], 0.95, fill=shade(doc, '#A9B4C4', light=0.5, dark=0.15), stroke='#5E6B80', w=0.22)
    ra = 38                                            # the hydrolase's M6P held by an M6P receptor in the bud membrane
    rx_, ry_ = bx + br * math.cos(math.radians(ra)), by + br * math.sin(math.radians(ra))
    head = receptor_tm(doc, rx_, ry_, ra + 180, s=0.82)
    gang, k, hr = 40, 1.3, 3.4
    f = _uv(0, 0, gang, k)
    pu = f(*_GN['P'])
    ax, ay = head[0] - pu[0], head[1] - pu[1] - 1.2
    hx, hy = ax - hr * 0.92 * math.cos(math.radians(gang)), ay - hr * 0.92 * math.sin(math.radians(gang))
    hydrolase(doc, hx, hy, hr, gang, mode='m6p', k=k, seed=7)
    receptor_tm(doc, bx + br * math.cos(math.radians(140)), by + br * math.sin(math.radians(140)), 320, s=0.82)
    ux = 1060                                          # uncovering enzyme; the GlcNAc it removed drifts away
    uy = yat(tp, ux)
    tm_stub(doc, ux, uy, ENZ)
    enzyme(doc, ux - 1.0, uy + 4.4, 4.4, 2.2, rot=6, seed=11)
    _square(doc, ux - 9.0, uy + 7.6, 0.85, 2)
    path(doc, 'M%s,%s q-1.6,0.6 -3.0,2.0' % (fmt(ux - 4.6), fmt(uy + 5.6)), stroke='#8A8478', w=0.3, dash='0.6 0.7')
    mini(doc, 1048, 263.5, 'uncovering')
    mini(doc, 1048, 268.5, 'enzyme')
    leader(doc, [(1060.5, 259.4), (ux - 0.6, uy + 6.9)], color=SMALL, w=0.25, dot=False)
    mini(doc, 1035, 274.0, 'M6P', italic=False, fill='#8A6A10')
    mini(doc, 1035, 281.0, 'clathrin', fill=tone(CLATH, 0.3))
    mini(doc, 1035, 286.0, 'AP-1 · GGA', fill=tone(CLATH, 0.3))
    _close(doc)
    journey(doc, [(990, 218.5), (995, 223.5), (1000, 227.0)])
    name_label(doc, 874, 241, '3.3', 'TGN', DGOL)
    name_label(doc, 874, 252.5, '3.4', 'Clathrin bud', DGOL)

    # ------------------------------------------------------------------ 3.5 late endosome (scene left, label right)
    _open(doc, 'end')
    tp, bt = compartment(doc, 866, 982, 291.5, 310, END_C, ph=0.8)
    vxx = 886
    vatpase(doc, vxx, yat(tp, vxx), 270, s=1.1)
    for (px, py) in [(878, 298.5), (885, 305), (895, 299), (902, 306.5), (934, 306.5), (946, 298)]:
        hplus(doc, px, py, 0.95)
    rxx = 953                                          # emptied receptor: it goes back to the TGN
    rmy = yat(tp, rxx)
    receptor_tm(doc, rxx, rmy, 90, s=0.9)
    hx, hy, hr = 918, 301.0, 4.6
    nd = hydrolase(doc, hx, hy, hr, -6, mode='trim', k=1.9, seed=12)
    pa = nd['A3']
    phosphate(doc, pa[0] + 5.6, pa[1] - 2.2, 1.15)                                   # phosphate removed
    path(doc, 'M%s,%s l2.8,-1.0' % (fmt(pa[0] + 1.2), fmt(pa[1] - 0.5)), stroke='#8A8478', w=0.3, dash='0.6 0.7')
    mini(doc, pa[0] + 7.9, pa[1] - 0.9, 'P', italic=False)
    mini(doc, pa[0] + 10.7, pa[1] + 0.3, 'i', italic=False, size=3.4)
    mini(doc, vxx + 5.5, yat(tp, vxx) - 7.0, 'V-ATPase', fill=tone('#E75A8B', 0.35))
    mini(doc, rxx + 3.0, rmy + 12.6, 'M6PR', fill=tone(M6PR_C, 0.2), italic=False)
    _close(doc)
    r0 = M('end', rxx + 1.5, rmy - 4.5)
    arrow(doc, [r0, (r0[0] + 2.5, 266.0), (979.0, 245.5)], RECY, 'recycle', w=1.0, head=3.9)   # M6PR back to the TGN
    journey(doc, [M('tgn', bx - 9.0, by + br + 4.8), (982, 282.5), (974, 288.5)])
    name_label(doc, 1002, 301, '3.5', 'Late endosome', DLE)

    # ------------------------------------------------------------------ 3.6 lysosome (scene right, label left)
    LY = 6.0
    _open(doc, 'lys')
    tp, bt = compartment(doc, 952, 1086, 318 + LY, 336.5 + LY, LYS_C, ph=1.9)
    vatpase(doc, 1041, yat(tp, 1041), 270, s=0.9)
    for lx in (982, 1053, 1065, 1077):
        lamp(doc, lx, yat(tp, lx), seed=int(lx))
    for (px, py) in [(976, 331 + LY), (996, 333 + LY), (1040, 332.5 + LY), (1068, 334.0 + LY), (1006, 322.5 + LY)]:
        hplus(doc, px, py, 0.9)
    hx, hy, hr = 1024, 327.5 + LY, 4.4
    hydrolase(doc, hx, hy, hr, 0, mode='trim', k=1.75, seed=14)
    for (sx_, sy_) in [(hx - hr - 1.0, hy + 0.2), (hx - hr - 3.3, hy - 1.2), (hx - hr - 9.6, hy + 1.0), (hx - hr - 12.0, hy - 0.2)]:
        circ(doc, sx_, sy_, 0.95, fill='#C9CF8A', stroke='#6A741E', w=0.22)       # substrate being cleaved
    mini(doc, 1082, 320.0, 'LAMP', anchor='end', fill=tone(LAMP_C, 0.3), italic=False)
    _close(doc)
    journey(doc, [(984, 309.5), (990, 314.5), (994, 318.5)])
    name_label(doc, 874, 330, '3.6', 'Lysosome', DLY)
