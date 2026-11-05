"""Section 3 (V2): Lysosome biogenesis -- a descending staircase of ENLARGED organelle sacs inside the cell.

One lysosomal hydrolase is followed down a meandering river of closed, rounded sacs (geom_v2.BANDS, top right ->
down left), each drawn at molecular scale with its lumen open to view:

    3.1 rough ER -> COPII -> 3.2 cis-Golgi -> 3.3 TGN / 3.4 clathrin bud -> 3.5 late endosome -> 3.6 lysosome
    -> lysosomes travel down the BLUE_ROUTE toward the phagolysosome (stop near (640, 560); zone E docks them).

The molecular scenes are drawn in their historical local units inside a per-sac frame (translate + uniform scale K);
labels are set in poster mm outside the frames, so they keep their true size.  The rough-ER sac opens on its left
into the three organelle-scale ER sheets of the skeleton (cellmod2.ER_SHEETS): its fingers follow the sheets' own
edges and its membrane thins to the sheets' line weight there."""
import math, random
from lib import *
from bio import vatpase, hplus, m6pr, copii
from style import shade, spec, tone, lighten, darken, mix, contact_shadow, soft_shadow_path
from lenses import _ugrad
from annot2 import tag, organelle, hand_width, DBIO, DGOL, DLY
import marks
import geom_v2 as V

HYD = BIO                     # hydrolase identity (cobalt)
GOLD = '#E2B33C'              # M6P phosphate identity
M6PR_C = '#1E8A5A'            # M6P receptor identity
CLATH = '#6B7C93'             # clathrin identity (grey-blue)
ENZ = '#9A8F80'               # processing enzymes / chaperone: warm neutral (not poster identities)
LAMP_C = '#8E7BB0'
GLCNAC = '#22407E'            # SNFG-style glycan symbols, tuned to the cobalt family
MAN = '#9DC0F2'
GLC = '#F4F1EA'
SMALL = '#4A5566'             # in-figure annotation colour
MINI_S = 4.3

# compartment palette (lumen tint, membrane tone, name colour)
ER_C = ('#D3E3F8', '#3D6AAE', '#1F4E9A')
CIS_C = ('#D4ECF6', '#2F7FA8', DGOL)
TGN_C = ('#BEDDEE', '#1F5A7E', DGOL)
END_C = ('#F5DCE7', '#A8406E', '#8A2F5A')
LYS_C = ('#E8DAF6', '#6F36A8', DLY)

K = 1.4                       # molecular scale of the sacs (poster mm per local unit)
LAB = 4.6                     # molecule label size, poster mm
CYTO_HALO = '#FDF1E8'

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



def yat(poly, x):
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1e-9)
    return poly[0][1] if x < poly[0][0] else poly[-1][1]



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


def _arc(cx, cy, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]



def _runs(flags):
    """Index runs of True in a cyclic flag list (list of index lists)."""
    n = len(flags)
    if all(flags):
        return [list(range(n)) + [0]]
    start = next(i for i in range(n) if not flags[i])
    runs, cur = [], []
    for k in range(1, n + 1):
        i = (start + k) % n
        if flags[i]:
            cur.append(i)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


def _dots_d(pts, r):
    return ''.join('M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0' % (fmt(x - r), fmt(y), fmt(r), fmt(r), fmt(2 * r), fmt(r), fmt(r), fmt(-2 * r))
                   for x, y in pts)


# ============================================================================== frames (local units -> poster mm)
FR = {}


def frame(name, old, pos, k=K, rot=0.0):
    FR[name] = (old[0], old[1], pos[0], pos[1], k, rot)


def M(name, x, y):
    ox, oy, px, py, k, r = FR[name]
    c, s = math.cos(math.radians(r)), math.sin(math.radians(r))
    dx, dy = (x - ox) * k, (y - oy) * k
    return px + dx * c - dy * s, py + dx * s + dy * c


def Minv(name, X, Y):
    ox, oy, px, py, k, r = FR[name]
    c, s = math.cos(math.radians(r)), math.sin(math.radians(r))
    dx, dy = X - px, Y - py
    return ox + (dx * c + dy * s) / k, oy + (-dx * s + dy * c) / k


def _open(doc, name):
    ox, oy, px, py, k, r = FR[name]
    doc.add('<g transform="translate(%s %s) rotate(%s) scale(%s) translate(%s %s)">' % (
        fmt(px), fmt(py), fmt(r), fmt(k), fmt(-ox), fmt(-oy)))


def _close(doc):
    endgroup(doc)


def loc(name, pts):
    return [Minv(name, *p) for p in pts]


def lab(doc, name, x, y, s, anchor='start', fill=SMALL, italic=False, halo=None, size=LAB, weight=400):
    """Molecule label at a local point of a frame (or poster point if name is None), set in poster mm."""
    X, Y = M(name, x, y) if name else (x, y)
    T(doc, X, Y, s, size=size, fill=fill, anchor=anchor, italic=italic, halo=halo or CYTO_HALO, weight=weight)
    return X, Y


def hair(doc, name, a, b, col=SMALL, op=0.7):
    (x0, y0), (x1, y1) = M(name, *a), M(name, *b)
    line(doc, x0, y0, x1, y1, col, 0.28, op=op)


def smooth01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ============================================================================== geometry
def tube(center, halfs):
    """Closed clockwise outline around a centreline with per-point half widths and round caps."""
    nm = normals(center, closed=False)
    L = [(p[0] + n[0] * h, p[1] + n[1] * h) for p, n, h in zip(center, nm, halfs)]
    R = [(p[0] - n[0] * h, p[1] - n[1] * h) for p, n, h in zip(center, nm, halfs)]

    def cap(c, n, t, h, sgn):
        return [(c[0] + sgn * (n[0] * h * math.cos(f) + t[0] * h * math.sin(f)),
                 c[1] + sgn * (n[1] * h * math.cos(f) + t[1] * h * math.sin(f))) for f in [math.pi * i / 10 for i in range(1, 10)]]

    def tan(a, b):
        L_ = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        return ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)
    te = tan(center[-2], center[-1])
    ts = tan(center[1], center[0])
    end = cap(center[-1], nm[-1], te, halfs[-1], 1)
    start = cap(center[0], (-nm[0][0], -nm[0][1]), ts, halfs[0], 1)
    return L + end + R[::-1] + start


def arc_line(cx, cy, r, xa, xb, n=60):
    """Centre line of a cisterna: an arc of radius r about (cx, cy), the bowl opening toward +y."""
    return [(xa + (xb - xa) * i / n, cy - math.sqrt(max(0.0, r * r - (xa + (xb - xa) * i / n - cx) ** 2))) for i in range(n + 1)]


def smooth_line(pts, step=0.6):
    return resample(cr_sample(pts, closed=False, per=12), step, closed=False)


def edge_y(poly, x, side='top'):
    ys = []
    for (px, py), (qx, qy) in zip(poly, poly[1:] + poly[:1]):
        if (px - x) * (qx - x) <= 0 and px != qx:
            ys.append(py + (qy - py) * (x - px) / (qx - px))
    if not ys:
        return None
    return min(ys) if side == 'top' else max(ys)


def ring_pt(poly, cx, cy, ang):
    """Point of a closed outline in direction ang (deg) from (cx, cy), with its outward angle."""
    a = math.radians(ang)
    best = max(poly, key=lambda p: (p[0] - cx) * math.cos(a) + (p[1] - cy) * math.sin(a)
               - 4 * abs(-(p[0] - cx) * math.sin(a) + (p[1] - cy) * math.cos(a)))
    return best


class Org:
    """An organelle drawn in one frame: the union of closed clockwise parts (+ optional holes), membrane widths by
    part, membranes suppressed where one part runs inside another (so branches join seamlessly)."""

    def __init__(self, colors, parts, widths, holes=(), hole_w=1.4, off=None):
        from style import inside
        self.colors = colors
        self.parts = [resample(p, 0.45, closed=True) for p in parts]
        self.holes = [resample(h, 0.4, closed=True) for h in holes]
        self.hole_w = hole_w
        self.ws, self.on = [], []
        for i, p in enumerate(self.parts):
            wf = widths[i] if callable(widths[i]) else (lambda q, w=widths[i]: w)
            self.ws.append([wf(q) for q in p])
            others = [o for j, o in enumerate(self.parts) if j != i]
            self.on.append([not any(inside(o, q[0], q[1]) for o in others) and (off is None or not off(q)) for q in p])
        xs = [q[0] for p in self.parts for q in p]
        ys = [q[1] for p in self.parts for q in p]
        self.bb = (min(xs), min(ys), max(xs), max(ys))
        self.d = ''.join(poly_d(p, True) for p in self.parts) + ''.join(poly_d(h[::-1], True) for h in self.holes)


def draw_body(doc, o, current=None, crowd=40, seed=1, shadow=True):
    lum, mem = o.colors[0], o.colors[1]
    x0, y0, x1, y1 = o.bb
    if shadow:
        soft_shadow_path(doc, o.d, dx=0.9, dy=1.6, strength=0.07, blur=4.5)
    path(doc, o.d, fill='none', stroke=lum, w=5.0, op=0.25)
    g = _ugrad(doc, 'linear', [(0, lighten(lum, 0.6), 1), (0.45, lum, 1), (1, mix(lum, mem, 0.18), 1)],
               x1=x0, y1=y0 - 4, x2=x0 + 0.45 * (x1 - x0), y2=y1 + 10)
    path(doc, o.d, fill=g)
    cid = doc.uid('orgclip')
    doc.defs.append('<clipPath id="%s" clipPathUnits="userSpaceOnUse"><path d="%s"/></clipPath>' % (cid, o.d))
    doc.add('<g clip-path="url(#%s)">' % cid)
    from style import inside
    rnd = random.Random(seed)
    k = tries = 0
    while k < crowd and tries < crowd * 30:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if not any(inside(p, x, y) for p in o.parts) or any(inside(h, x, y) for h in o.holes):
            continue
        k += 1
        rr = rnd.uniform(0.6, 1.4)
        path(doc, blob(x, y, rr, rr * rnd.uniform(0.7, 1.0), n=6, j=0.12, seed=rnd.randint(1, 999), rot=rnd.uniform(0, 180)),
             fill=mix(lum, mem, 0.32), op=0.3)
    if current:
        dd = poly_d(cr_sample(current, closed=False, per=14))
        for w_, op in ((10.0, 0.07), (7.0, 0.09), (4.2, 0.12), (2.0, 0.14)):
            path(doc, dd, stroke=lighten(HYD, 0.25), w=w_, op=op)
    gl = _ugrad(doc, 'radial', [(0, '#FFFFFF', 0.5), (1, '#FFFFFF', 0)], cx=x0 + 0.25 * (x1 - x0), cy=y0 + 0.2 * (y1 - y0),
                r=0.5 * max(x1 - x0, y1 - y0))
    path(doc, o.d, fill=gl)
    doc.add('</g>')


def bilayer_runs(doc, P_, W_, flags, mem):
    """Variable-width bilayer along a closed outline: toned leaflets, bead-like head groups, pale core."""
    nm = normals(P_, closed=True)
    for run in _runs(flags):
        pts = [P_[i] for i in run]
        ws = [W_[i] for i in run]
        ns = [nm[i] for i in run]
        if len(pts) < 2:
            continue

        def band(f):
            a = [(p[0] + n[0] * w * f, p[1] + n[1] * w * f) for p, n, w in zip(pts, ns, ws)]
            b = [(p[0] - n[0] * w * f, p[1] - n[1] * w * f) for p, n, w in zip(pts, ns, ws)]
            return poly_d(a + b[::-1], True)
        doc.add('<path d="%s" fill="%s" stroke="%s" stroke-width="0.12" stroke-linejoin="round"/>' % (
            band(0.5), mix(mem, '#FFFFFF', 0.22), tone(mem, 0.25)))
        doc.add('<path d="%s" fill="%s"/>' % (band(0.2), mix(mem, '#FFFFFF', 0.86)))
        beads = {1: [], -1: []}
        acc, last = 0.0, pts[0]
        for p, n, w in zip(pts, ns, ws):
            acc += math.hypot(p[0] - last[0], p[1] - last[1])
            last = p
            if acc >= 1.25 * w / 2.5:
                acc = 0.0
                for sg in (1, -1):
                    beads[sg].append((p[0] + n[0] * w * 0.37 * sg, p[1] + n[1] * w * 0.37 * sg, w))
        for sg in (1, -1):
            groups = {}
            for x, y, w in beads[sg]:
                groups.setdefault(round(w / 2.5 * 8) / 8, []).append((x, y))
            for q, pp in groups.items():
                doc.add('<path d="%s" fill="%s" opacity="0.8"/>' % (_dots_d(pp, max(0.08, 0.3 * q)), tone(mem, 0.15)))


def draw_membranes(doc, o):
    for p, w, f in zip(o.parts, o.ws, o.on):
        bilayer_runs(doc, p, w, f, o.colors[1])
    for h in o.holes:
        bilayer_runs(doc, h, [o.hole_w] * len(h), [True] * len(h), o.colors[1])


def ribo_dots(doc, o, keep, r, spacing, seed=5):
    """Ribosomes on the cytosolic (outer) face of every membrane point for which keep(point) is true."""
    rnd = random.Random(seed)
    for p_, w_, f_ in zip(o.parts, o.ws, o.on):
        nm = normals(p_, closed=True)
        acc = 0.0
        pts = []
        for q, n, w, f in zip(p_, nm, w_, f_):
            acc += 0.45
            if not f or not keep(q) or acc < spacing:
                continue
            acc = 0.0
            if rnd.random() < 0.18:
                continue
            off = w / 2 + r * 1.05 + rnd.uniform(-0.1, 0.2)
            pts.append((q[0] + n[0] * off, q[1] + n[1] * off))
        if pts:
            doc.add('<path d="%s" fill="#17327A"/>' % _dots_d(pts, r))
            doc.add('<path d="%s" fill="#8FA8E6" opacity="0.9"/>' % _dots_d([(x - r * 0.32, y - r * 0.34) for x, y in pts], r * 0.35))


def vesicle(doc, x, y, r, colors, w=0.9):
    """Small organelle-scale vesicle (budding at a Golgi rim, or an ILV)."""
    circ(doc, x, y, r, fill=shade(doc, colors[0], light=0.55, dark=0.1))
    circ(doc, x, y, r, stroke=mix(colors[1], '#FFFFFF', 0.2), w=w)
    circ(doc, x, y, r, stroke=mix(colors[1], '#FFFFFF', 0.85), w=w * 0.32)


def rot_g(doc, x, y, ang):
    doc.add('<g transform="rotate(%s %s %s)">' % (fmt(ang), fmt(x), fmt(y)))


def ribosome(doc, x, y, rot=0, s=1.0):
    """Large ribosome (60S + 40S) seen at molecular scale, sitting on a translocon."""
    doc.add('<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(rot), fmt(s)))
    contact_shadow(doc, 1.5, -6.6, 7.4, 4.1, strength=0.12)
    ell(doc, 1.5, -7.0, 7.4, 4.1, fill=shade(doc, '#5C6E9F', light=0.42, dark=0.18), stroke='#2E3B66', w=0.35)
    ell(doc, 0.5, -12.2, 5.6, 2.7, fill=shade(doc, '#8494C2', light=0.45, dark=0.15), stroke='#2E3B66', w=0.35)
    doc.add('</g>')


# ============================================================================== the ER: fingers join the skeleton sheets
def _sheet_edges(i):
    """Exact top/bottom edges of skeleton ER sheet i (replicates cellmod2.cisterna's width law), poster mm."""
    import cellmod2 as C
    pts, seed, w = C.ER_SHEETS[i], 10 + i, 7.6
    rnd = random.Random(seed)
    dense = resample(cr_sample(pts, closed=False, per=12), 0.8, closed=False)
    n = len(dense)
    nm = normals(dense, closed=False)
    k1, k2, ph = rnd.uniform(5, 8), rnd.uniform(11, 16), rnd.uniform(0, 6.3)
    top, bot = [], []
    for j in range(n):
        t = j / (n - 1)
        h = w / 2 * (0.82 + 0.16 * math.sin(t * k1 + ph) + 0.08 * math.sin(t * k2 + 2 * ph))
        h = max(0.9, h * min(1.0, (n - j) / 5.0) ** 0.5)
        top.append((dense[j][0] + nm[j][0] * h, dense[j][1] + nm[j][1] * h))
        bot.append((dense[j][0] - nm[j][0] * h, dense[j][1] - nm[j][1] * h))
    return dense, top, bot


def _at_x(poly, x):
    return min(poly, key=lambda p: abs(p[0] - x))


TIP_X = 733.5                 # poster x where the ER fingers end (inside the skeleton sheets, which continue left)


def small_lysosome(doc, x, y, r, seed):
    """Organelle-scale lysosome on its way to the phagolysosome: violet membrane, LAMP glycocalyx, hydrolases inside."""
    rnd = random.Random(seed)
    contact_shadow(doc, x, y, r, strength=0.14)
    circ(doc, x, y, r, fill=shade(doc, LYS_C[0], light=0.55, dark=0.12))
    for a in range(0, 360, 24):                                      # LAMP glycocalyx just inside the membrane
        aa = math.radians(a + rnd.uniform(-6, 6))
        circ(doc, x + (r - 1.3) * math.cos(aa), y + (r - 1.3) * math.sin(aa), 0.42, fill='#B9A6DA', op=0.9)
    for i in range(6):                                               # hydrolases, inside the lumen only
        aa, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.55)
        circ(doc, x + rr * math.cos(aa), y + rr * math.sin(aa), 0.95, fill=shade(doc, HYD, light=0.45, dark=0.2), stroke=tone(HYD, 0.45), w=0.18)
    circ(doc, x, y, r, stroke=LYS_C[1], w=1.0)
    circ(doc, x, y, r - 0.55, stroke=lighten(LYS_C[1], 0.7), w=0.3, op=0.8)
    vatpase(doc, x + r * math.cos(math.radians(-35)), y + r * math.sin(math.radians(-35)), -35, s=0.42)
    spec(doc, x, y, r, a0=200, a1=255, op=0.7, inset=0.78, w=0.6)


def glycan_key(doc, x, y):
    s = 4.4
    _square(doc, x, y - 1.5, 0.95, 2)
    T(doc, x + 2.6, y, 'GlcNAc', size=s, fill=SMALL)
    x2 = x + 2.6 + text_width('GlcNAc', s) + 4.0
    circ(doc, x2, y - 1.5, 1.0, fill=MAN, stroke='#1E3B6E', w=0.22)
    T(doc, x2 + 2.4, y, 'mannose', size=s, fill=SMALL)
    x3 = x2 + 2.4 + text_width('mannose', s) + 4.0
    circ(doc, x3, y - 1.5, 1.0, fill=GLC, stroke='#6E6A60', w=0.22)
    T(doc, x3 + 2.4, y, 'glucose', size=s, fill=SMALL)
    x4 = x3 + 2.4 + text_width('glucose', s) + 4.0
    phosphate(doc, x4, y - 1.5, 1.25)
    T(doc, x4 + 2.6, y, 'phosphate', size=s, fill=SMALL)




# ============================================================================== 3.1 rough ER: a broad, undulating, branching sheet
ER_OUT = [(772, 157.5), (790, 153.0), (812, 155.5), (838, 151.0), (866, 155.5), (894, 150.5), (922, 154.5), (946, 151.5),
          (958.5, 155.0), (964.0, 163.0), (958.5, 171.0), (942, 174.0), (922, 176.0),
          (906, 181.0), (914, 188.0), (920, 196.5), (921, 204.5), (913, 208.5), (904, 203.5), (895, 196.5),
          (874, 196.0), (850, 192.5), (826, 196.5), (802, 193.0), (781, 192.0)]


def er_part():
    pts = [Minv('er', *p) for p in ER_OUT]
    fingers = []
    for i in range(3):
        dense, et, eb = _sheet_edges(i)
        p_a, p_b = _at_x(dense, TIP_X), _at_x(dense, TIP_X + 5)
        ux, uy = p_b[0] - p_a[0], p_b[1] - p_a[1]
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        ta, ba = _at_x(et, TIP_X), _at_x(eb, TIP_X)
        tb, bb = _at_x(et, TIP_X + 5), _at_x(eb, TIP_X + 5)
        hb = math.hypot(tb[0] - bb[0], tb[1] - bb[1]) / 2
        mid = ((tb[0] + bb[0]) / 2, (tb[1] + bb[1]) / 2)
        ext = []
        for dd in (8.0, 15.0):
            c = (mid[0] + ux * dd, mid[1] + uy * dd)
            ext.append(((c[0] + uy * hb, c[1] - ux * hb), (c[0] - uy * hb, c[1] + ux * hb)))
        fingers.append(([Minv('er', *p) for p in [ta, tb] + [e[0] for e in ext]],
                        [Minv('er', *p) for p in [ba, bb] + [e[1] for e in ext]]))
    left = []
    for i in (2, 1, 0):
        ft, fb = fingers[i]
        left += fb[::-1] + ft
        if i:
            nt = fingers[i - 1][1][-1]
            left.append(((ft[-1][0] + nt[0]) / 2 + 4.5, (ft[-1][1] + nt[1]) / 2))
    return cr_sample(pts + left, closed=True, per=10)


def scene_er(doc):
    frame('er', (866, 157), (758, 155))

    def wfun(q):
        X = M('er', *q)[0]
        return 0.75 / K + (2.5 - 0.75 / K) * smooth01((X - 737) / (806 - 737))

    def off(q):
        return M('er', *q)[0] < TIP_X + 1.6

    holes = []
    for (cx, cy, rx, ry, sd) in [(794, 185.0, 3.4, 2.1, 2), (936, 164.0, 3.6, 2.0, 4), (873, 189.5, 2.6, 1.6, 6)]:
        c = Minv('er', cx, cy)
        holes.append(cr_sample(blob_pts(c[0], c[1], rx / K, ry / K, n=8, j=0.08, seed=sd, rot=-8), closed=True, per=6))
    o = Org(ER_C, [er_part()], [wfun], holes=holes, hole_w=1.5, off=off)
    part = o.parts[0]
    _open(doc, 'er')
    ga, gb = Minv('er', TIP_X + 0.5, 0)[0], Minv('er', TIP_X + 9.5, 0)[0]
    fg = doc.uid('erfade')
    doc.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="0" x2="%s" y2="0">'
                    '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
                    % (fg, fmt(ga), fmt(gb)))
    mk = doc.uid('ermask')
    doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="800" y="120" width="260" height="110">'
                    '<rect x="800" y="120" width="260" height="110" fill="url(#%s)"/></mask>' % (mk, fg))
    doc.add('<g mask="url(#%s)">' % mk)
    draw_body(doc, o, current=loc('er', [(796, 162), (812, 176), (842, 177), (875, 178), (898, 186), (912, 199)]), crowd=60, seed=3)
    draw_membranes(doc, o)

    def keep(q):
        X, Y = M('er', *q)
        if X < 737:
            return False
        if X < 786 and not (Y < 163.5 - 0.33 * (X - 745) or Y > 188.5 - 0.33 * (X - 745)):
            return False
        if 783 < X < 822 and Y < 166:
            return False
        if X > 899 and Y > 199:
            return False
        return True
    ribo_dots(doc, o, keep, r=0.95 / K, spacing=3.3 / K)
    # ER exit site: COPII coat assembling on the cytosolic face of the branch tip
    nm = normals(part, closed=True)
    coat = []
    acc = 0.0
    for q, n, w in zip(part, nm, o.ws[0]):
        X, Y = M('er', *q)
        acc += 0.45
        if X > 900 and Y > 200 and acc > 1.25:
            acc = 0.0
            coat.append((q[0] + n[0] * (w / 2 + 0.9), q[1] + n[1] * (w / 2 + 0.9)))
    doc.add('<path d="%s" fill="%s"/>' % (_dots_d(coat, 0.72), tone('#D98E00', 0.3)))
    doc.add('<path d="%s" fill="#E9A21A"/>' % _dots_d([(x - 0.1, y - 0.12) for x, y in coat], 0.55))
    doc.add('</g>')

    # Sec61 + ribosome + mRNA; nascent hydrolase with BiP; glucose trimming
    with actor(doc, 'm6p.er_translation', pivot=(868, 175), bbox=(735, 130, 235, 95), zone='zone_d'):
        sx = 900
        my = edge_y(part, sx, 'top')
        for dx in (-2.3, 2.3):
            rect(doc, sx + dx - 1.25, my - 2.9, 2.5, 5.8, fill=shade(doc, '#7D88A6', light=0.45, dark=0.15), stroke='#46506B', sw=0.25, r=0.9)
        mr = [(sx - 17, my - 11.4), (sx - 11, my - 12.6), (sx - 5, my - 11.6), (sx + 1, my - 12.9), (sx + 8, my - 11.8),
              (sx + 15, my - 13.0), (sx + 21, my - 12.2)]
        path(doc, cr_path(mr, False), stroke='#7A4C8A', w=0.55)
        ribosome(doc, sx, my)
        hx, hy, hr = 929, 170.0, 5.6
        path(doc, cr_path([(sx, my - 4.5), (sx, my + 2.5), (sx + 1.2, my + 7.0), (sx + 5, my + 10.5), (sx + 11, my + 13.2),
                           (hx - hr + 0.6, hy + 1.6)], False), stroke=HYD, w=0.7)
        enzyme(doc, hx - 1.4, hy + hr + 2.0, 5.0, 2.3, rot=-6, seed=5)                    # BiP
        nd = hydrolase(doc, hx, hy, hr, -12, mode='full', k=2.3, seed=3, glc_fade=True)
        gx, gy = nd['G3']
        for (dx, dy, op) in ((4.2, -2.4, 0.85), (7.0, 0.4, 0.7), (9.6, -2.8, 0.55)):
            circ(doc, gx + dx, gy + dy, 0.92, fill=GLC, stroke='#6E6A60', w=0.22, op=op)
        path(doc, 'M%s,%s q2.2,-1.2 3.2,-0.6' % (fmt(gx + 1.2), fmt(gy - 0.4)), stroke='#8A8478', w=0.3, dash='0.6 0.7')
        t = Minv('er', 911.5, 199.5)
        hydrolase(doc, t[0], t[1], 2.4, -35, mode='trim', k=0.82, seed=4)                 # folded, trimmed: at the exit site
    _close(doc)
    with actor(doc, 'm6p.er_translation'):
        lab(doc, 'er', sx - 18, my - 13.4, 'mRNA', anchor='end', fill='#6A3C7A', italic=True)
        lab(doc, 'er', sx - 6.5, my - 2.2, 'Sec61', anchor='end')
        lab(doc, 'er', sx + 9.0, my - 15.6, 'ribosome', fill='#2E3B66')
        lab(doc, 'er', hx - 8.4, hy + hr + 4.6, 'BiP', anchor='end', halo=ER_C[0])
        lab(doc, 'er', hx + 6.6, hy + 8.6, 'acid hydrolase', fill=tone(HYD, 0.3), halo=ER_C[0], weight=600)
        lab(doc, 'er', gx + 2.0, gy + 6.4, 'glucose trimming', italic=True, halo=ER_C[0])
    organelle(doc, 880, 146, 'Rough ER', ER_C[2], '3.1')


def copii_vesicle(doc, vx, vy):
    with actor(doc, 'm6p.copii_vesicle', pivot=(907, 222), bbox=(865, 200, 62, 46), zone='zone_d'):
        frame('cv', (0, 0), (vx, vy), k=0.82, rot=-20)
        _open(doc, 'cv')
        vr = 7.4
        contact_shadow(doc, 0, 0, vr + 2, strength=0.12)
        circ(doc, 0, 0, vr, fill=shade(doc, ER_C[0], light=0.6, dark=0.08))
        bil = _arc(0, 0, vr, 0, 360, 60)
        path(doc, poly_d(bil), stroke=mix(ER_C[1], '#FFFFFF', 0.22), w=2.5)
        path(doc, poly_d(bil), stroke=mix(ER_C[1], '#FFFFFF', 0.86), w=1.0)
        copii(doc, 0, 0, vr + 2.4, w=1.15)
        hydrolase(doc, -1.6, 0.6, 2.6, -15, mode='trim', k=0.9, seed=4)
        _close(doc)
        T(doc, vx - 10.5, vy - 2.0, 'COPII', size=LAB + 0.2, weight=700, fill=tone('#D98E00', 0.35), anchor='end', halo=CYTO_HALO)
        T(doc, vx - 10.5, vy + 4.2, 'vesicle', size=LAB, fill=SMALL, anchor='end', halo=CYTO_HALO)


# ============================================================================== 3.2 / 3.3 the Golgi: a cupped stack, TGN network
GC = (908.0, 373.0)                 # centre of curvature of the stack (local); the bowl opens toward the TGN
MED_C = ('#CBE6F2', '#2A6E96')
TRA_C = ('#BCDCEE', '#22648A')


def cisterna(xa, xb, r, hfun):
    c = resample(arc_line(GC[0], GC[1], r, xa, xb, 80), 0.6, closed=False)
    return tube(c, [hfun(p[0]) for p in c])


def scene_golgi(doc):
    frame('go', (908, 225), (842, 240), k=1.15, rot=20)

    def h_cis(x):
        d = abs(x - 912)
        return 4.0 + 7.5 * smooth01((48 - d) / 22) + 1.5 * smooth01((d - 50) / 9)

    def w_cis(q):
        return 1.1 + 1.4 * smooth01((46 - abs(q[0] - 912)) / 14)

    def h_rim(xc, half):
        return lambda x: 2.3 + 1.7 * smooth01((abs(x - xc) - (half - 12)) / 10)

    cis = Org(CIS_C, [cisterna(852, 972, 148, h_cis)], [w_cis])
    med = Org(MED_C, [cisterna(860, 958, 130, h_rim(909, 49))], [1.0])
    tra = Org(TRA_C, [cisterna(866, 952, 121, h_rim(909, 43))], [1.0])

    # TGN: a tubular network -- molecular-scale main tube (uncovering enzyme, clathrin bud) + organelle-scale branches
    def h_tgn(x):
        return 4.2 + 3.0 * smooth01((46 - abs(x - 916)) / 8)
    main_c = resample(arc_line(GC[0], GC[1], 105, 870, 962, 80), 0.6, closed=False)
    main = tube(main_c, [h_tgn(p[0]) for p in main_c])
    bx, br, nh = 892.0, 10.5, 4.8
    yb = GC[1] - math.sqrt(105 ** 2 - (bx - GC[0]) ** 2) + h_tgn(bx)
    by = yb + math.sqrt(br * br - nh * nh)
    bulb = _arc(bx, by, br, -90, 270, 140)[:-1]
    neck = tube([(bx, yb - 4.0), (bx, (yb + by) / 2), (bx, by - 4.0)], [nh, nh * 0.92, nh])
    branches = [loc('go', [(783, 283), (771, 279.5), (759, 281.5), (751, 288.5)]),
                loc('go', [(847, 311), (845, 323.5), (851.5, 333), (865, 336.5), (881, 333.5)]),
                loc('go', [(875, 322), (882.5, 330.5), (885, 340.5), (882, 347.5)]),
                loc('go', [(874, 320), (886, 317.5), (896, 310.5)])]
    bparts = [tube(smooth_line(b, 0.5), [2.5] * len(smooth_line(b, 0.5))) for b in branches]

    def w_main(q):
        return 1.0 + 1.5 * smooth01((44 - abs(q[0] - 916)) / 8)
    tgn = Org(TGN_C, [main, bulb, neck] + bparts, [w_main, 2.5, 2.5] + [1.0] * len(bparts))

    _open(doc, 'go')
    for org, cur, sd in ((tgn, [(952, 270), (926, 272), (905, 274), (893, 280), (892, 291)], 7), (tra, None, 5), (med, None, 6)):
        draw_body(doc, org, current=cur, crowd=30 if org is tgn else 12, seed=sd)
        draw_membranes(doc, org)
    for (x, y, r, c) in [(852.5, 260.0, 2.1, MED_C), (967.0, 260.0, 1.9, MED_C), (858.0, 270.5, 1.9, TRA_C),
                         (960.5, 267.5, 1.8, TRA_C), (972.5, 254.0, 1.6, MED_C)]:
        vesicle(doc, x, y, r, c, w=0.75)                  # vesicles budding at the dilated rims
    draw_body(doc, cis, current=[(958, 218), (935, 226), (912, 229), (885, 231), (866, 236)], crowd=40, seed=4)
    draw_membranes(doc, cis)

    # --- cis-Golgi scene: GlcNAc-phosphotransferase reads the lysine patch and adds GlcNAc-P to a mannose
    with actor(doc, 'm6p.golgi_enzymes', pivot=(835, 285), bbox=(735, 210, 215, 145), zone='zone_d'):
        cpart = cis.parts[0]
        hx, hy, hr = 903, 227.5, 5.4
        nd = hydrolase(doc, hx, hy, hr, 4, mode='gnp', k=2.25, patch=True, seed=6)
        ex = 914
        ey = edge_y(cpart, ex, 'top')
        tm_stub(doc, ex, ey, ENZ)
        pt = nd['patch'][1]
        enzyme(doc, pt[0] + 0.6, pt[1] - 3.3, 4.6, 2.2, rot=-4, seed=8)
        enzyme(doc, nd['PN'][0] - 1.6, nd['PN'][1] - 4.2, 5.0, 2.3, rot=8, seed=9)
        path(doc, cr_path([(pt[0] + 4.6, pt[1] - 4.2), (ex, ey + 2.6), (nd['PN'][0] - 5.5, nd['PN'][1] - 5.2)], False), stroke=tone(ENZ, 0.3), w=0.9)

        # --- TGN scene: uncovering enzyme exposes M6P; M6PR in the bud binds it (luminal side); clathrin/AP-1/GGA outside
        ca0, ca1 = -12, 192
        coat = _arc(bx, by, br + 4.2, ca0, ca1, 60)
        path(doc, poly_d(coat), stroke=CLATH, w=1.5, dash='2.2 1.0')
        path(doc, poly_d(coat), stroke=lighten(CLATH, 0.6), w=0.4, dash='2.2 1.0')
        for a in range(ca0 + 4, ca1, 13):
            p_, q_ = _arc(bx, by, br + 1.5, a, a, 1)[0], _arc(bx, by, br + 4.2, a, a, 1)[0]
            line(doc, p_[0], p_[1], q_[0], q_[1], CLATH, 0.45, op=0.8)
        for a in range(ca0 + 10, ca1 - 2, 13):
            p_ = _arc(bx, by, br + 2.5, a, a, 1)[0]
            circ(doc, p_[0], p_[1], 0.95, fill=shade(doc, '#A9B4C4', light=0.5, dark=0.15), stroke='#5E6B80', w=0.22)
        ra = 36
        rx_, ry_ = bx + br * math.cos(math.radians(ra)), by + br * math.sin(math.radians(ra))
        head = receptor_tm(doc, rx_, ry_, ra + 180, s=0.78)
        gang, k, hr2 = 40, 1.25, 3.2
        f = _uv(0, 0, gang, k)
        pu = f(*_GN['P'])
        ax, ay = head[0] - pu[0], head[1] - pu[1] - 1.1
        hydrolase(doc, ax - hr2 * 0.92 * math.cos(math.radians(gang)), ay - hr2 * 0.92 * math.sin(math.radians(gang)), hr2, gang,
                  mode='m6p', k=k, seed=7)
        receptor_tm(doc, bx + br * math.cos(math.radians(144)), by + br * math.sin(math.radians(144)), 324, s=0.78)
        mpart = tgn.parts[0]
        for rx2 in (906, 913):                                 # unoccupied M6PRs gather in the TGN membrane
            receptor_tm(doc, rx2, edge_y(mpart, rx2, 'bot'), 270, s=0.72)
        ux = 941
        uy = edge_y(mpart, ux, 'top')
        tm_stub(doc, ux, uy, ENZ)
        enzyme(doc, ux - 0.6, uy + 4.0, 4.0, 2.0, rot=12, seed=11)
        n2 = hydrolase(doc, 924.5, uy + 5.6, 3.2, 12, mode='m6p', k=1.25, seed=13)
        gq = (ux + 6.0, uy + 9.0)
        _square(doc, gq[0], gq[1], 0.85, 2)
        path(doc, 'M%s,%s q2.0,1.6 4.6,1.4' % (fmt(n2['P'][0] + 1.2), fmt(n2['P'][1] + 0.6)), stroke='#8A8478', w=0.3, dash='0.6 0.7')
    _close(doc)
    with actor(doc, 'm6p.golgi_enzymes'):
        # cisternal maturation: the enzyme moves cis -> trans through the stack
        journey(doc, [M('go', 876, 238.5), M('go', 874, 250), M('go', 877, 262)], w=1.0, head=3.4, op=0.8)

        lab(doc, 'go', pt[0] - 8.6, pt[1] - 0.2, 'Lys patch', anchor='end', halo=CIS_C[0])
        lab(doc, 'go', nd['PN'][0] + 1.0, nd['PN'][1] + 4.2, 'GlcNAc-P', fill='#7A5A00', halo=CIS_C[0], size=LAB - 0.2)
        X, Y = M('go', ex, ey)
        T(doc, X - 9, Y - 13.6, 'GlcNAc-', size=LAB, fill=SMALL, anchor='end', halo=CYTO_HALO)
        T(doc, X - 9, Y - 7.4, 'phosphotransferase', size=LAB, fill=SMALL, anchor='end', halo=CYTO_HALO)
        line(doc, X - 8.2, Y - 8.6, X - 1.2, Y - 1.8, SMALL, 0.28, op=0.7)
        U = M('go', ux, uy)
        T(doc, U[0] + 9.0, U[1] - 9.2, 'uncovering', size=LAB, fill=SMALL, halo=CYTO_HALO)
        T(doc, U[0] + 9.0, U[1] - 2.9, 'enzyme', size=LAB, fill=SMALL, halo=CYTO_HALO)
        line(doc, U[0] + 8.4, U[1] - 4.6, U[0] + 1.4, U[1] - 0.6, SMALL, 0.28, op=0.7)
        lab(doc, 'go', gq[0] + 1.4, gq[1] + 4.6, 'GlcNAc', fill=GLCNAC, italic=True, halo=TGN_C[0], size=LAB - 0.3)
        lab(doc, 'go', n2['P'][0] - 1.5, n2['P'][1] + 5.6, 'M6P', fill='#8A6A10', halo=TGN_C[0], weight=600, anchor='middle')
        B = M('go', bx, by)
        T(doc, B[0] - 19.5, B[1] - 4.2, 'clathrin', size=LAB, fill=tone(CLATH, 0.35), anchor='end', halo=CYTO_HALO)
        T(doc, B[0] - 19.5, B[1] + 2.2, 'AP-1 · GGA', size=LAB, fill=tone(CLATH, 0.35), anchor='end', halo=CYTO_HALO)
        lab(doc, 'go', bx + 1.5, by + 4.4, 'M6PR', fill=tone(M6PR_C, 0.25), halo=TGN_C[0], weight=600, size=LAB - 0.3)
    organelle(doc, 768, 229.5, 'cis-Golgi', CIS_C[2], '3.2', anchor='end')
    organelle(doc, 893, 338, 'TGN', TGN_C[2], '3.3')
    organelle(doc, B[0] - 19.5, B[1] + 13.5, 'Clathrin bud', TGN_C[2], '3.4', anchor='end')
    return B, br * 1.15


# ============================================================================== 3.5 late endosome: a round multivesicular body
def scene_le(doc):
    frame('le', (0, 0), (718, 374), k=1.2)
    ring = cr_sample(blob_pts(0, 0, 25.8, 24.6, n=12, j=0.035, seed=41, rot=20), closed=True, per=10)
    o = Org(END_C, [ring], [2.4])
    part = o.parts[0]
    _open(doc, 'le')
    draw_body(doc, o, current=[(-5, -24), (0, -16), (7, -9), (8, 1), (9, 11), (13, 20)], crowd=40, seed=9)
    for (ix, iy, ir) in [(-11, 11, 3.6), (-2.5, 17.5, 2.6), (-18.5, 11, 2.2), (6.5, 18.5, 2.0), (-5.5, 6.5, 1.9),
                         (-15, 3.5, 1.7)]:
        circ(doc, ix, iy, ir, fill=lighten(END_C[0], 0.5), stroke=mix(END_C[1], '#FFFFFF', 0.25), w=0.75)
        circ(doc, ix, iy, ir, stroke=mix(END_C[1], '#FFFFFF', 0.85), w=0.25)
        spec(doc, ix, iy, ir, a0=205, a1=250, op=0.6, inset=0.7, w=0.3)
    draw_membranes(doc, o)
    with actor(doc, 'm6p.le_interior', pivot=(718, 374), bbox=(660, 330, 115, 90), zone='zone_d'):
        for a in (198, 228):
            p = ring_pt(part, 0, 0, a)
            vatpase(doc, p[0], p[1], a, s=1.0)
        for (px, py) in [(-17, -7), (-10, -14), (-20, 1.5), (-7, -6), (-2, -19), (-13, -1), (1, -6), (14, 2)]:
            hplus(doc, px, py, 0.9)
        rp = ring_pt(part, 0, 0, -30)
        head = receptor_tm(doc, rp[0], rp[1], 150, s=0.9)
        hydrolase(doc, 1.5, -12.5, 3.6, 8, mode='m6p', k=1.4, seed=15)                    # just released at acid pH
        hx, hy, hr = 2.0, 3.0, 4.2
        nd = hydrolase(doc, hx, hy, hr, -10, mode='trim', k=1.6, seed=12)
        pa = nd['A3']
        enzyme(doc, pa[0] + 2.2, pa[1] - 3.3, 3.2, 1.7, rot=-25, seed=17)               # phosphatase
        phosphate(doc, pa[0] + 3.0, pa[1] + 4.6, 1.1)
        path(doc, 'M%s,%s l1.6,2.6' % (fmt(pa[0] + 0.6), fmt(pa[1] + 1.0)), stroke='#8A8478', w=0.3, dash='0.6 0.7')
    _close(doc)
    with actor(doc, 'm6p.le_interior'):
        V1 = M('le', *ring_pt(part, 0, 0, 213))
        T(doc, V1[0] - 8.5, V1[1] - 4.0, 'V-ATPase', size=LAB, fill=tone('#E75A8B', 0.4), anchor='end', halo=CYTO_HALO)
        R = M('le', *rp)
        T(doc, R[0] + 1.0, R[1] - 6.5, 'M6PR', size=LAB, weight=600, fill=tone(M6PR_C, 0.25), halo=CYTO_HALO)
        lab(doc, 'le', pa[0] + 4.6, pa[1] + 5.8, 'Pi', halo=END_C[0])
        lab(doc, 'le', hx + 1.0, hy + hr + 6.0, 'later: phosphatase', halo=END_C[0], anchor='middle')
        hair(doc, 'le', (hx + 6.0, hy + hr + 2.6), (pa[0] + 2.0, pa[1] - 1.6))
        T(doc, R[0] + 5.5, R[1] + 8.8, 'acid pH: hydrolase', size=LAB - 0.2, fill='#8A6A10', halo=CYTO_HALO)
        T(doc, R[0] + 5.5, R[1] + 14.6, 'leaves M6PR', size=LAB - 0.2, fill='#8A6A10', halo=CYTO_HALO)
    organelle(doc, 684, 380, 'Late endosome', END_C[2], '3.5', anchor='end')
    return part, rp


# ============================================================================== 3.6 lysosome: plump, tilted
def scene_lys(doc):
    frame('ly', (0, 0), (757, 433), k=1.15, rot=-14)
    ring = cr_sample(blob_pts(0, 0, 33.0, 19.8, n=14, j=0.03, seed=57, rot=0), closed=True, per=10)
    o = Org(LYS_C, [ring], [2.4])
    part = o.parts[0]
    _open(doc, 'ly')
    draw_body(doc, o, current=[(-20, -17), (-14, -6), (-4, 1), (4, 2), (-12, 9), (-31, 4)], crowd=55, seed=11)
    draw_membranes(doc, o)
    with actor(doc, 'm6p.lys_interior', pivot=(757, 433), bbox=(695, 390, 125, 90), zone='zone_d'):
        for a in (194, 333):
            p = ring_pt(part, 0, 0, a)
            vatpase(doc, p[0], p[1], a, s=0.95)
        for a in (226, 256, 286, 316, 142):
            p = ring_pt(part, 0, 0, a)
            nx, ny = -p[0] / 33.0 ** 2, -p[1] / 19.8 ** 2
            ang = math.degrees(math.atan2(ny, nx))
            rot_g(doc, p[0], p[1], ang - 90)
            lamp(doc, p[0], p[1], seed=a)
            doc.add('</g>')
        for (px, py) in [(-23, 3), (-17, -6), (-26, -3), (20, 8), (24, -2), (15, -7), (-7, 11), (8, 10)]:
            hplus(doc, px, py, 0.85)
        hx, hy, hr = 5.0, 0.5, 4.4
        hydrolase(doc, hx, hy, hr, 0, mode='trim', k=1.7, seed=14)
        for (sx_, sy_) in [(hx - hr - 1.0, hy + 0.2), (hx - hr - 3.3, hy - 1.2), (hx - hr - 9.6, hy + 1.0), (hx - hr - 12.0, hy - 0.2),
                           (hx - hr - 14.3, hy + 0.9)]:
            circ(doc, sx_, sy_, 0.95, fill='#C9CF8A', stroke='#6A741E', w=0.22)
    _close(doc)
    with actor(doc, 'm6p.lys_interior'):
        L1 = M('ly', *ring_pt(part, 0, 0, 256))
        T(doc, L1[0] + 1.0, L1[1] - 4.0, 'LAMP', size=LAB, weight=600, fill=tone(LAMP_C, 0.35), anchor='middle', halo=CYTO_HALO)
        V1 = M('ly', *ring_pt(part, 0, 0, 333))
        T(doc, V1[0] + 8.0, V1[1] + 1.0, 'V-ATPase', size=LAB, fill=tone('#E75A8B', 0.4), halo=CYTO_HALO)
        lab(doc, 'ly', hx + 1.0, hy + hr + 6.6, 'active hydrolase', anchor='middle', fill=tone(HYD, 0.3), halo=LYS_C[0], weight=600)
        lab(doc, 'ly', hx - hr - 13.0, hy - 4.2, 'substrate', anchor='middle', fill='#5A6418', halo=LYS_C[0], italic=True, size=LAB - 0.2)
    E = M('ly', 33.5, 0)
    organelle(doc, E[0] + 6, E[1] + 6, 'Lysosome', LYS_C[2], '3.6')
    return part


# ============================================================================== transport carriers
def clathrin_vesicle(doc, x, y):
    r = 5.2
    contact_shadow(doc, x, y, r + 2, strength=0.12)
    circ(doc, x, y, r, fill=shade(doc, TGN_C[0], light=0.55, dark=0.1))
    circ(doc, x, y, r, stroke=mix(TGN_C[1], '#FFFFFF', 0.2), w=1.4)
    circ(doc, x, y, r, stroke=mix(TGN_C[1], '#FFFFFF', 0.85), w=0.45)
    m6pr(doc, x + 1.6, y + 3.6, s=0.42, rot=200)
    circ(doc, x - 0.8, y - 0.4, 1.5, fill=shade(doc, HYD, light=0.45, dark=0.2), stroke=tone(HYD, 0.45), w=0.2)
    from bio import clathrin
    clathrin(doc, x, y, r + 2.0, color=CLATH, w=1.0)


def recycling_carrier(doc, x, y):
    r = 4.4
    contact_shadow(doc, x, y, r + 1.5, strength=0.1)
    circ(doc, x, y, r, fill=shade(doc, '#DDEFE5', light=0.55, dark=0.1))
    circ(doc, x, y, r, stroke=mix(M6PR_C, '#FFFFFF', 0.25), w=1.2)
    circ(doc, x, y, r, stroke=mix(M6PR_C, '#FFFFFF', 0.85), w=0.38)
    for a in (40, 160, 280):
        px, py = x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))
        m6pr(doc, px, py, s=0.36, rot=a - 90)


# ============================================================================== draw
def draw(doc):
    marks.section(doc, 597, 131, 3, 'Lysosome biogenesis', marks.color_of(3))
    glycan_key(doc, 606, 143.8)

    scene_er(doc)
    B, rb = scene_golgi(doc)
    vx, vy = 907.0, 222.0
    copii_vesicle(doc, vx, vy)
    le_part, rp = scene_le(doc)
    scene_lys(doc)

    jw, jh = 1.1, 3.6
    with actor(doc, 'm6p.copii_vesicle'):
        journey(doc, [(915.5, 210.5), (913.5, 213)], w=jw, head=2.6)                              # ER exit -> COPII
        journey(doc, [(901, 229.5), (895, 234), (890.5, 238.5)], w=jw, head=jh)                     # COPII -> cis face
    cvx, cvy = 770.0, 326.0
    with actor(doc, 'm6p.clathrin_vesicle', pivot=(770, 326), bbox=(720, 300, 90, 125), zone='zone_d'):
        journey(doc, [(B[0] - 9, B[1] + rb + 2.0), (783, 319), (cvx + 6.5, cvy - 4.0)], w=jw, head=jh)   # bud -> clathrin vesicle
        clathrin_vesicle(doc, cvx, cvy)
        journey(doc, [(cvx - 4.5, cvy + 7.5), (742, 342), (733, 349.5)], w=jw, head=jh)             # -> late endosome
        journey(doc, [M('le', 12.0, 22.0), (737, 404), (742.5, 414.5)], w=jw, head=jh)              # LE -> lysosome
    # M6PR recycles to the TGN in its own carrier (green dashed)
    r0 = M('le', rp[0] + 3.5, rp[1] - 2.0)
    cx_, cy_ = 803.0, 352.0
    with actor(doc, 'm6p.recycling_carrier', pivot=(803, 352), bbox=(740, 330, 120, 36), zone='zone_d'):
        arrow(doc, [r0, (764, 352), (cx_ - 6, cy_ + 1)], RECY, 'recycle', w=1.1, head=3.6)
        recycling_carrier(doc, cx_, cy_)
        T(doc, cx_, cy_ + 10.5, 'M6PR recycles', size=LAB - 0.2, fill=tone(RECY, 0.35), anchor='middle', halo=CYTO_HALO)
        arrow(doc, [(cx_ + 5.5, cy_ - 2), (822, 346), (839, 341), (848.5, 337)], RECY, 'recycle', w=1.1, head=3.8)

    # lysosomes leave toward the phagolysosome along the blue route
    (ax, ay), (bx2, by2) = V.BLUE_ROUTE[4], V.BLUE_ROUTE[5]

    def on_route(yy):
        return ax + (bx2 - ax) * (yy - ay) / (by2 - ay), yy
    s0 = M('ly', -30.5, 9.0)
    l1, l2 = on_route(484), on_route(521)
    with actor(doc, 'm6p.blue_lysosomes', pivot=(662, 512), bbox=(620, 445, 110, 125), zone='zone_d'):
        journey(doc, [s0, (s0[0] - 12, s0[1] + 12), (l1[0] + 2.0, l1[1] - 8.4)], w=1.3, head=4.0)
        small_lysosome(doc, l1[0], l1[1], 7.0, seed=3)
        journey(doc, [(l1[0] - 1.6, l1[1] + 8.2), (on_route(503)[0] - 0.8, 503), (l2[0] + 0.4, l2[1] - 8.2)], w=1.3, head=4.0)
        small_lysosome(doc, l2[0], l2[1], 6.6, seed=8)
        journey(doc, [(l2[0] - 1.4, l2[1] + 7.6), (on_route(541)[0] - 1.0, 541), (on_route(559)[0], 559)], w=1.4, head=4.4)
