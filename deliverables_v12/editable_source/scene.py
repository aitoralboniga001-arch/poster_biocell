"""Tissue scale: the alveolar air space and the alveolar wall the macrophage rests on (V1.2, pathology specialist).

The wall runs the full width as a histological cross-section: lining fluid / surfactant film, type I and type II
pneumocytes, basement membrane, capillaries (endothelium, red blood cells) and interstitium.  It changes continuously
from a thin healthy septum (left) to a thickened fibrotic one (right, geom.fibrosis): wavy collagen bundles,
fibroblasts turning into alpha-SMA myofibroblasts, type II hyperplasia, recruited neutrophils / monocytes leaving
the capillaries toward the injured epithelium.  No outline frame: the lower edge feathers into the paper.

Draw order: draw(doc) paints only the air space (and the inhaled particles drifting in it) BEFORE the cell.
The wall itself is painted by wall(doc), which m_patho calls AFTER the cell group, so the epithelium sits cleanly
under the cell base (the cell's paper halo and shadow do not wash over the tissue)."""
import math, random
from lib import *
from style import shade, tone, lighten, darken, mix, contact_shadow, spec, shade_rot, sheen_rot, SHADOW
from bio import silica, asbestos_fibre, bacterium
import geom as G

# ----------------------------------------------------------------------------------------- palette (calm, desaturated)
TISSUE_H = '#F3E4DF'     # healthy interstitium (pale rose-greige)
TISSUE_F = '#EEDCC6'     # fibrotic interstitium (warmer tan)
EPI = '#F6E3DD'          # type I pneumocyte cytoplasm
EPI_LINE = '#BF8D83'     # apical plasma membrane of the epithelium
EPI_NUC = '#9A8AA8'      # nuclei (haematoxylin-like, muted)
BM = '#A98378'           # basement membrane
LINING = '#DCEAF0'       # alveolar lining fluid (hypophase)
FILM = '#8FB5C6'         # surfactant film at the air interface
COLLAGEN = '#C7A170'     # collagen bundles (tan / ochre, quieter than PATH)
COLL_HI = '#EAD7B4'
ENDO = '#DDB2A6'         # endothelium
PLASMA = '#FBF1EC'
RBC = '#BF3A2E'
ASMA = '#B0503F'         # alpha-SMA stress fibres
LAB = '#7C5F56'          # label colour for anatomy

CELL_BASE_DIP = 1.9      # under the cell base the drawn epithelium sits this much below geom.wall_top (lining space)
LIN = 1.2                # lining fluid thickness


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def _ug(doc, kind, stops, **a):
    gid = doc.uid('sg')
    st = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (fmt(o), c, fmt(op)) for o, c, op in stops)
    at = ' '.join('%s="%s"' % (k, fmt(v)) for k, v in a.items())
    doc.defs.append('<%sGradient id="%s" gradientUnits="userSpaceOnUse" %s>%s</%sGradient>' % (kind, gid, at, st, kind))
    return 'url(#%s)' % gid


def _xs(x0, x1, step=2.0):
    n = max(1, int((x1 - x0) / step))
    return [x0 + (x1 - x0) * i / n for i in range(n + 1)]


# ----------------------------------------------------------------------------------------- surface profile
# type II pneumocytes bulge into the air space: (x, half-width, height)
TYPE2 = [(122, 11.5, 10.5), (262, 10.5, 9.5)]
TYPE2_HYPER = [(1071, 9.0, 8.4), (1089, 9.0, 9.2), (1107, 9.0, 8.6)]
DAMAGE = (906, 990)      # injured type I epithelium under the open asbestos cup (ROS + enzymes leak here)


def dip(x):
    """Depression of the drawn surface under the cell base (thin lining-fluid layer between cell and epithelium)."""
    return CELL_BASE_DIP * smooth((x - 352) / 50) * (1 - smooth((x - 905) / 40))


def surface(x):
    """Apical (air-side) surface of the flat type I epithelium."""
    return G.wall_top(x) + dip(x)


def bulge(x):
    h = 0.0
    for (cx, hw, hh) in TYPE2 + TYPE2_HYPER:
        t = abs(x - cx) / hw
        if t < 1:
            h = max(h, hh * (1 - t ** 4) ** 0.75)
    return h


def apical(x):
    """Apical surface including type II bulges."""
    return surface(x) - bulge(x)


# ----------------------------------------------------------------------------------------- air space + inhaled particles
def air_space(doc):
    """The sheet is the inside of one alveolus: a whisper of cool air tone above the wall."""
    g = _ug(doc, 'linear', [(0, '#E6F0F4', 0.0), (0.66, '#E6F0F4', 0.0), (1, '#E1EDF2', 0.42)], x1=0, y1=92, x2=0, y2=775)
    rect(doc, 0, 92, 1100, 685, fill=g)


def _drift(doc, pts, op=0.32):
    """Very faint dotted drift trail."""
    path(doc, cr_path(pts, False), stroke='#8FA9B5', w=0.32, dash='0.01 1.6', op=op)


def _small_fibre(doc, x, y, L, rot, w=1.25, seed=3):
    a = math.radians(rot)
    asbestos_fibre(doc, x - math.cos(a) * L / 2, y - math.sin(a) * L / 2, x + math.cos(a) * L / 2, y + math.sin(a) * L / 2,
                   w=w, color='#D2B27A', frays=False, seed=seed)


def inhaled(doc):
    """A sparse drift of inhaled material entering from the top-left toward the cell: silica crystals, fibres,
    a bacterium.  Quiet, small, like dust in a light beam."""
    _drift(doc, [(262, 92), (300, 108), (352, 118), (402, 128)], op=0.3)
    _drift(doc, [(270, 140), (286, 160), (300, 170)], op=0.25)
    silica(doc, 279, 100, s=0.42, rot=18)
    _small_fibre(doc, 318, 107, 15, 24, w=1.1, seed=5)
    silica(doc, 352, 121, s=0.42, rot=-30)
    bacterium(doc, 384, 113, L=13, W=5.6, rot=-14, lps=False, flagella=False, seed=11)
    _small_fibre(doc, 431, 128, 30, 8, w=1.15, seed=6)
    silica(doc, 283, 152, s=0.42, rot=40)
    # some particles are cleared back up the airways (mucociliary clearance): a faint return arrow toward the top-left
    arrow(doc, [(338, 136), (310, 128), (284, 118), (268, 112)], '#9DB3BD', 'transport', w=0.5, head=2.6, opacity=0.8)
    T(doc, 300, 139.5, 'cleared ↑', size=4.6, weight=700, fill='#4F6874', halo=PAPER)


def draw(doc):
    """Under the cell: air space and inhaled particles.  (The wall is drawn by wall(), called from m_patho.)"""
    air_space(doc)
    inhaled(doc)


# ----------------------------------------------------------------------------------------- cells of the wall
def rbc(doc, x, y, r=3.3, rot=0, edge=0.0):
    """Red blood cell: biconcave disc.  edge=0 face-on (pale centre), edge=1 seen edge-on (dumbbell)."""
    base = RBC
    if edge < 0.5:
        ry = r * 0.9
        ell(doc, x + 0.25, y + 0.45, r, ry, fill='#6A1A12', rot=rot, op=0.10)
        ell(doc, x, y, r, ry, fill=shade(doc, base, light=0.32, dark=0.14), stroke=tone(base, 0.3), w=0.18, rot=rot)
        ell(doc, x + r * 0.06, y + ry * 0.08, r * 0.46, ry * 0.42, fill='#E08B7C', rot=rot, op=0.55)
    else:
        a = math.radians(rot)
        ca, sa = math.cos(a), math.sin(a)
        L, t = r, r * 0.42
        pts = [(-L, 0), (-L * 0.75, -t), (-L * 0.15, -t * 0.55), (0, -t * 0.5), (L * 0.15, -t * 0.55), (L * 0.75, -t),
               (L, 0), (L * 0.75, t), (L * 0.15, t * 0.55), (0, t * 0.5), (-L * 0.15, t * 0.55), (-L * 0.75, t)]
        P_ = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
        path(doc, cr_path(P_, True), fill=shade(doc, base, light=0.32, dark=0.14), stroke=tone(base, 0.3), w=0.18)


def capillary(doc, cx, cy, rx, ry, rot, seed, n_rbc=3, leuko=None):
    """Capillary in section: endothelium (thin wall with flattened bulging nuclei), plasma lumen, RBCs."""
    rnd = random.Random(seed)
    contact_shadow(doc, cx, cy, rx, ry, rot=rot, strength=0.07, spread=1.08)
    outer = blob(cx, cy, rx, ry, n=12, j=0.035, seed=seed, rot=rot)
    path(doc, outer, fill=shade(doc, ENDO, light=0.35, dark=0.08), stroke=tone(ENDO, 0.18), w=0.35)
    path(doc, blob(cx, cy, rx - 1.15, ry - 1.15, n=12, j=0.035, seed=seed, rot=rot), fill=PLASMA)
    a = math.radians(rot)
    for (u, side) in ((rnd.uniform(-0.55, -0.2), -1), (rnd.uniform(0.25, 0.6), 1)):
        px, py = u * (rx - 1.6), side * (ry - 1.5)
        x, y = cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)
        ell(doc, x, y, min(4.0, rx * 0.22), 0.95, fill=EPI_NUC, rot=rot, op=0.8)
    for k in range(n_rbc):
        t = (k + 0.5) / n_rbc
        px = -rx * 0.68 + t * rx * 1.36 + rnd.uniform(-1.2, 1.2)
        py = rnd.uniform(-ry * 0.22, ry * 0.22)
        x, y = cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)
        r = min(3.4, ry * 0.52)
        rbc(doc, x, y, r=r, rot=rot + rnd.uniform(-35, 35), edge=rnd.choice((0, 0, 1)))
    if leuko:
        for (kind, u, v) in leuko:
            px, py = u * rx, v * ry
            x, y = cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)
            (neutrophil if kind == 'n' else monocyte)(doc, x, y, 3.2)


def neutrophil(doc, x, y, r=3.6, squeeze=1.0, rot=0):
    """Neutrophil: pale granular cytoplasm, multilobed (3-4 lobes) nucleus joined by fine chromatin bridges."""
    contact_shadow(doc, x, y, r * squeeze, r / squeeze, rot=rot, strength=0.1)
    ell(doc, x, y, r * squeeze, r / squeeze, fill=shade(doc, '#E4E3EE', light=0.6, dark=0.07), stroke='#8E8DA8', w=0.3, rot=rot)
    k = r / 3.6
    lobes = [(-1.6, -0.6), (-0.2, 0.9), (1.3, -0.3), (0.6, -1.5)]
    a = math.radians(rot)
    P_ = [(x + (dx * squeeze * math.cos(a) - dy / squeeze * math.sin(a)) * k, y + (dx * squeeze * math.sin(a) + dy / squeeze * math.cos(a)) * k)
          for dx, dy in lobes]
    path(doc, cr_path(P_[:3], False), stroke='#55507E', w=0.35 * k)
    path(doc, 'M%s,%s L%s,%s' % (fmt(P_[2][0]), fmt(P_[2][1]), fmt(P_[3][0]), fmt(P_[3][1])), stroke='#55507E', w=0.3 * k)
    for (px, py) in P_:
        circ(doc, px, py, 0.82 * k, fill=shade(doc, '#6C6699', light=0.35, dark=0.12))
    spec(doc, x, y, r, a0=205, a1=240, op=0.6, inset=0.78, w=0.3)


def monocyte(doc, x, y, r=4.0, squeeze=1.0, rot=0):
    """Monocyte: larger, kidney-shaped nucleus."""
    contact_shadow(doc, x, y, r * squeeze, r / squeeze, rot=rot, strength=0.1)
    ell(doc, x, y, r * squeeze, r / squeeze, fill=shade(doc, '#E7DFEC', light=0.6, dark=0.07), stroke='#8F84A6', w=0.3, rot=rot)
    k = r / 4.0
    path(doc, blob(x - 0.3 * k, y + 0.1 * k, 2.3 * k * squeeze, 1.7 * k / squeeze, n=8, j=0.12, seed=5, rot=rot),
         fill=shade(doc, '#766C9E', light=0.35, dark=0.12))
    ell(doc, x + 1.5 * k, y + 0.15 * k, 0.8 * k, 0.65 * k, fill='#E7DFEC', rot=rot)     # nuclear notch
    spec(doc, x, y, r, a0=205, a1=240, op=0.6, inset=0.78, w=0.3)


def fibroblast(doc, x, y, L, rot, myo=0.0, seed=1):
    """Spindle fibroblast; myo -> 1 turns it into a larger alpha-SMA myofibroblast (stress fibres, denser body)."""
    rnd = random.Random(seed)
    L = L * (1 + 0.25 * myo)
    W = L * (0.12 + 0.05 * myo)
    body = mix('#EBD5C9', '#E2BFAD', myo)
    d = 'M%s,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s %s,0 C%s,%s %s,%s 0,%s C%s,%s %s,%s %s,0 Z' % (
        fmt(-L / 2), fmt(-L * 0.36), fmt(-W * 0.35), fmt(-L * 0.2), fmt(-W), fmt(-W),
        fmt(L * 0.2), fmt(-W), fmt(L * 0.36), fmt(-W * 0.3), fmt(L / 2),
        fmt(L * 0.36), fmt(W * 0.3), fmt(L * 0.2), fmt(W), fmt(W),
        fmt(-L * 0.2), fmt(W), fmt(-L * 0.36), fmt(W * 0.35), fmt(-L / 2))
    doc.add('<g transform="translate(%s %s) rotate(%s)">' % (fmt(x), fmt(y), fmt(rot)))
    path(doc, d, fill=shade_rot(doc, body, rot, light=0.45, dark=0.1), stroke=tone(body, 0.3), w=0.32)
    for s_ in (-1, 1):
        path(doc, 'M%s,0 q%s,%s %s,%s' % (fmt(s_ * L / 2 * 0.98), fmt(s_ * 3), fmt(rnd.uniform(-1, 1)), fmt(s_ * 6), fmt(rnd.uniform(-1.5, 1.5))),
             stroke=tone(body, 0.25), w=0.35)
    ell(doc, -L * 0.04, 0, L * 0.17, W * 0.42, fill=EPI_NUC, op=0.85)
    if myo > 0.35:
        n = 3 if myo > 0.7 else 2
        for i in range(n):
            dy = (i - (n - 1) / 2) * W * 0.55
            path(doc, 'M%s,%s L%s,%s' % (fmt(-L * 0.42), fmt(dy * 0.8), fmt(L * 0.42), fmt(dy * 0.8)),
                 stroke=ASMA, w=0.32, op=0.55 + 0.35 * myo)
    doc.add('</g>')


def collagen_bundle(doc, x, y, L, rot, n, f, seed):
    """Wavy collagen bundle: a few parallel strands with a lit edge.  f = fibrosis (density / contrast)."""
    rnd = random.Random(seed)
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    amp = rnd.uniform(0.6, 1.1)
    wl = rnd.uniform(11, 15)
    ph = rnd.uniform(0, 6.3)
    for i in range(n):
        off = (i - (n - 1) / 2) * 0.85
        pts = []
        steps = int(L / 2.0)
        for k in range(steps + 1):
            u = -L / 2 + L * k / steps
            v = off + amp * math.sin(2 * math.pi * u / wl + ph) * (1 - (2 * u / L) ** 6)
            pts.append((x + u * ca - v * sa, y + u * sa + v * ca))
        op = (0.2 + 0.26 * f) * (0.8 + 0.2 * rnd.random())
        path(doc, poly_d(pts), stroke=COLLAGEN, w=0.6, op=op)
        if i == 0:
            path(doc, poly_d([(px + sa * 0.3, py - ca * 0.3) for px, py in pts]), stroke=COLL_HI, w=0.35, op=op * 0.9)


# ----------------------------------------------------------------------------------------- the wall
def _fade_mask(doc, x0, x1, top_fn, fs_fn, fe_fn, K=22):
    """Luminance mask: opaque down to fs(x), then a smooth linear fade to 0 at fe(x).  Built from K nested regions
    (each below a curve between fs and fe) filled black at opacity 1/(K-k+1): luminance falls linearly, with smooth
    curved band edges (no vertical seams, no filters)."""
    mid = doc.uid('wfade')
    xs = _xs(x0, x1, 3.0)
    out = ['<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="600" width="%s" height="300">' % (mid, fmt(x0 - 5), fmt(x1 - x0 + 10)),
           '<rect x="%s" y="600" width="%s" height="300" fill="#fff"/>' % (fmt(x0 - 5), fmt(x1 - x0 + 10))]
    for k in range(1, K + 1):
        t = (k - 0.5) / K
        curve = [(x, fs_fn(x) + (fe_fn(x) - fs_fn(x)) * t) for x in xs]
        d = poly_d(curve + [(x1 + 5, 900), (x0 - 5, 900)], True)
        out.append('<path d="%s" fill="#000" fill-opacity="%s"/>' % (d, fmt(1.0 / (K - k + 1))))
    out.append('</mask>')
    doc.defs.append(''.join(out))
    return mid


H0 = 21.0                # healthy septum thickness: epithelium + one capillary + epithelium


def depth(x):
    """Septum thickness: thin healthy septum (one capillary between two epithelia) -> thick fibrotic septum."""
    full = G.wall_bottom(x) - surface(x)
    return H0 + (full - H0) * G.fibrosis(x)


def lower(x):
    """Lower epithelial (air-side) surface, facing the neighbouring alveolus."""
    return surface(x) + depth(x) - lbulge(x)


TYPE2_LOW = [(150, 10.0, 7.5), (452, 9.5, 7.0)]      # type II cells on the lower face (bulge downward)


def lbulge(x):
    h = 0.0
    for (cx, hw, hh) in TYPE2_LOW:
        t = abs(x - cx) / hw
        if t < 1:
            h = max(h, hh * (1 - t ** 4) ** 0.75)
    return -h


def wall(doc):
    X0, X1 = -10, 1110
    xs = _xs(X0, X1, 1.5)
    flat = [(x, surface(x)) for x in xs]
    bot = [(x, surface(x) + depth(x)) for x in xs]
    _neighbour_alveolus(doc, xs)
    band = poly_d(flat + bot[::-1], True)
    fill = _ug(doc, 'linear', [(0, TISSUE_H, 1), (G.HEALTHY_X / 1100, TISSUE_H, 1), (G.FIBROTIC_X / 1100, TISSUE_F, 1),
                               (1, mix(TISSUE_F, '#E6CDAE', 0.35), 1)], x1=0, y1=0, x2=1100, y2=0)
    path(doc, band, fill=fill)
    sh = _ug(doc, 'linear', [(0, '#A87C64', 0.0), (0.35, '#A87C64', 0.0), (1, '#A87C64', 0.08)], x1=0, y1=752, x2=0, y2=845)
    path(doc, band, fill=sh)
    cid = doc.uid('wallclip')
    doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, band))
    doc.add('<g clip-path="url(#%s)">' % cid)
    _collagen(doc)
    _capillaries(doc)
    _fibroblasts(doc)
    _leukocytes(doc)
    doc.add('</g>')
    bm = [(x, surface(x) + 2.7 + 0.5 * G.fibrosis(x)) for x in xs]
    path(doc, poly_d(bm), stroke=BM, w=0.45, op=0.65)
    bm2 = [(x, y + 0.9) for x, y in bm if G.fibrosis(x) > 0.05]
    path(doc, poly_d(bm2), stroke=BM, w=0.35, op=0.35)
    _epithelium(doc, xs)
    _lower_epithelium(doc, xs)
    _cell_contact(doc)
    _free_particle(doc)


def _collagen(doc):
    rnd = random.Random(7)
    for k in range(190):
        x = rnd.uniform(-10, 1110)
        f = G.fibrosis(x)
        if rnd.random() > 0.1 + f * 0.9:
            continue
        s, d = surface(x), depth(x)
        y = rnd.uniform(s + 5, s + d - 4)
        quiet = in_label_zone(x, y)
        n = 1 if f < 0.2 else rnd.choice((2, 3, 3, 4))
        L = rnd.uniform(22, 30) + 30 * f
        rot = rnd.uniform(-5, 5) + (rnd.uniform(-22, 22) if rnd.random() < 0.12 else 0)
        collagen_bundle(doc, x, y, L, rot, n, f * (0.12 if quiet else 1.0), seed=k)


HEALTHY_END = 585
GAPS_FIBRO = (2, 6, 11)       # indices of the wider gaps that hold a fibroblast (sparse healthy interstitium)


def _healthy_caps():
    """Single row of capillaries filling the thin septum, touching both basement membranes (thin air-blood barrier)."""
    rnd = random.Random(31)
    out, gaps = [], []
    x, k = -12.0, 0
    while True:
        rx = rnd.choice((13, 16, 19, 22, 25)) if rnd.random() > 0.2 else 8.5
        cx = x + rx
        if cx + rx > HEALTHY_END:
            break
        out.append((cx, rx))
        gap = 12.0 if k in GAPS_FIBRO else rnd.uniform(2.5, 5.0)
        if k in GAPS_FIBRO:
            gaps.append(cx + rx + gap / 2)
        x = cx + rx + gap
        k += 1
    return out, gaps


CAPS = [  # (x, depth below the basement membrane of the capillary centre, rx, ry, rot, n_rbc, leukocytes)
    (612, 16, 8, 6.2, -8, 1, None),
    (660, 18, 24, 7.0, -4, 3, None), (742, 24, 20, 6.6, 5, 2, None), (810, 30, 12, 6.0, -12, 1, None),
    (842, 20, 22, 6.6, 3, 2, [('n', 0.5, 0.25)]), (935, 34, 23, 7.0, -3, 2, [('n', -0.45, -0.3)]),
    (1012, 27, 26, 7.2, 4, 2, [('n', 0.45, -0.35)]), (1085, 32, 20, 6.8, -6, 2, None),
]


def _capillaries(doc):
    caps, _ = _healthy_caps()
    for k, (cx, rx) in enumerate(caps):
        top, bot = surface(cx) + 2.9, surface(cx) + depth(cx) - 2.9
        ry = (bot - top) / 2
        if rx < 10:
            ry = min(ry, rx)
        capillary(doc, cx, (top + bot) / 2, rx, ry, 0, seed=70 + k, n_rbc=max(1, int(rx / 7)))
    for k, (x, dz, rx, ry, rot, n, leu) in enumerate(CAPS):
        capillary(doc, x, surface(x) + 2.8 + dz, rx, ry, rot, seed=40 + k, n_rbc=n, leuko=leu)


FIBRO = [  # (x, depth, L, rot)
    (598, 26, 22, 5), (640, 36, 24, -6), (705, 40, 26, 4),
    (700, 18, 22, -8), (770, 46, 26, -5), (790, 14, 22, 3), (860, 44, 28, 6), (884, 60, 26, -4), (964, 41, 24, -6),
    (1050, 41, 26, 4), (735, 62, 24, 7), (620, 54, 22, -3), (812, 64, 26, 3), (850, 74, 24, -5),
]


LABEL_ZONE = (880, 798, 960, 828)     # quiet patch of fibrotic interstitium that carries the 5.4 / 5.5 labels


def in_label_zone(x, y):
    x0, y0, x1, y1 = LABEL_ZONE
    return x0 - 6 < x < x1 and y > y0 - 4


def _fibroblasts(doc):
    _, gaps = _healthy_caps()
    for k, x in enumerate(gaps):
        fibroblast(doc, x, surface(x) + depth(x) / 2, 14, 78 + 10 * k, myo=0.0, seed=90 + k)
    for k, (x, dz, L, rot) in enumerate(FIBRO):
        if in_label_zone(x, surface(x) + dz):
            continue
        f = G.fibrosis(x)
        if dz > depth(x) - 6:
            continue
        myo = smooth((f - 0.35) / 0.6) * (1.0 if x > 690 else 0.75)
        fibroblast(doc, x, surface(x) + dz, L, rot, myo=myo, seed=k)


def _leukocytes(doc):
    """5.4: neutrophils and monocytes leaving capillaries (diapedesis) toward the injured epithelium."""
    s = surface
    monocyte(doc, 922, s(922) + 26.5, 3.8, squeeze=1.25, rot=-55)
    neutrophil(doc, 951, s(951) + 17, 3.4, squeeze=1.15, rot=-40)
    neutrophil(doc, 968, s(968) + 8.5, 3.3, squeeze=1.1, rot=-20)
    neutrophil(doc, 1000, s(1000) + 19.5, 3.4, squeeze=1.25, rot=-60)
    monocyte(doc, 985, s(985) + 30, 3.8, squeeze=1.1, rot=-30)
    for pts in ([(1000, s(1000) + 23), (990, s(990) + 16), (975, s(975) + 10)],
                [(935, s(935) + 30), (942, s(942) + 21), (950, s(950) + 13)]):
        path(doc, cr_path(pts, False), stroke='#8C7FA0', w=0.3, dash='0.01 1.2', op=0.6)


def _epithelium(doc, xs):
    top = [(x, apical(x)) for x in xs]
    lin = [(x, y - LIN * (1 - 0.45 * G.fibrosis(x))) for x, y in top]
    path(doc, poly_d(lin + top[::-1], True), fill=LINING, op=0.95)
    base = [(x, surface(x) + 2.6 + 0.5 * G.fibrosis(x)) for x in xs]
    epi = poly_d(top + base[::-1], True)
    path(doc, epi, fill=_ug(doc, 'linear', [(0, EPI, 1), (0.7, EPI, 1), (1, mix(EPI, '#F0D2C2', 0.6), 1)], x1=0, y1=0, x2=1100, y2=0))
    d0, d1 = DAMAGE
    left = [p for p in top if p[0] <= d0 + 6]
    right = [p for p in top if p[0] >= d1 - 4]
    for seg in (left, right):
        path(doc, poly_d(seg), stroke=EPI_LINE, w=0.6)
    path(doc, poly_d(lin), stroke=FILM, w=0.3, op=0.75)
    for x in (18, 70, 196, 318, 430, 552, 668, 790, 868, 1030):
        if any(abs(x - c[0]) < c[1] + 4 for c in TYPE2 + TYPE2_HYPER):
            continue
        ell(doc, x, surface(x) + 1.25, 5.2, 0.95, fill=EPI_NUC, op=0.72)
    for x in (48, 150, 236, 372, 494, 610, 728, 832, 896, 1040):
        path(doc, 'M%s,%s l0.25,2.4' % (fmt(x), fmt(surface(x) + 0.15)), stroke=EPI_LINE, w=0.35, op=0.7)
    for (cx, hw, hh) in TYPE2:
        type2(doc, cx, hw, hh, seed=int(cx))
    for (cx, hw, hh) in TYPE2_HYPER:
        type2(doc, cx, hw, hh, seed=int(cx), hyper=True)
    _damage(doc)


def _neighbour_alveolus(doc, xs):
    """The air space of the NEIGHBOURING alveolus below the septum: a very pale air tint (built from nested bands)."""
    K = 9
    for k in range(1, K + 1):
        h = 15.0 * k / K
        top = [(x, lower(x) + 0.5) for x in xs]
        bot = [(x, min(lower(x) + 0.5 + h * (1 - 0.55 * G.fibrosis(x)), 853)) for x in xs]
        path(doc, poly_d(top + bot[::-1], True), fill='#DCEAF0', op=0.075)


def _lower_epithelium(doc, xs):
    """Type I epithelium (and two type II cells) on the lower face, lining fluid toward the neighbouring alveolus."""
    ap = [(x, lower(x)) for x in xs]
    flat = [(x, surface(x) + depth(x)) for x in xs]
    bas = [(x, surface(x) + depth(x) - 2.6 - 0.5 * G.fibrosis(x)) for x in xs]
    lin = [(x, y + LIN * (1 - 0.45 * G.fibrosis(x))) for x, y in ap]
    path(doc, poly_d(ap + lin[::-1], True), fill=LINING, op=0.95)
    path(doc, poly_d(bas + flat[::-1], True), fill=EPI)
    path(doc, poly_d(bas), stroke=BM, w=0.45, op=0.65)
    path(doc, poly_d(ap), stroke=EPI_LINE, w=0.6)
    path(doc, poly_d(lin), stroke=FILM, w=0.3, op=0.75)
    for x in (40, 110, 228, 300, 382, 520, 640, 760, 880, 1000, 1070):
        if any(abs(x - c[0]) < c[1] + 4 for c in TYPE2_LOW):
            continue
        y = surface(x) + depth(x)
        ell(doc, x, y - 1.25, 5.2, 0.95, fill=EPI_NUC, op=0.72)
    for x in (12, 76, 190, 262, 340, 418, 560, 700, 820, 940, 1040):
        y = surface(x) + depth(x)
        path(doc, 'M%s,%s l0.25,-2.4' % (fmt(x), fmt(y - 0.15)), stroke=EPI_LINE, w=0.35, op=0.7)
    for (cx, hw, hh) in TYPE2_LOW:
        rnd = random.Random(int(cx))
        xs2 = _xs(cx - hw, cx + hw, 0.8)
        bot = [(x, lower(x)) for x in xs2]
        top = [(x, surface(x) + depth(x) - 2.6) for x in xs2]
        path(doc, poly_d(top + bot[::-1], True), fill=shade(doc, '#F4DBD0', light=0.5, dark=0.06), stroke=EPI_LINE, w=0.5)
        mv = ''.join('M%s,%s l0,0.9' % (fmt(x), fmt(lower(x))) for x in _xs(cx - hw * 0.7, cx + hw * 0.7, 1.1))
        doc.add('<path d="%s" stroke="%s" stroke-width="0.3" stroke-linecap="round" opacity="0.7"/>' % (mv, EPI_LINE))
        sy = surface(cx) + depth(cx)
        circ(doc, cx - 0.5, sy + hh * 0.2, min(2.5, hh * 0.3), fill=shade(doc, '#A796B5', light=0.3, dark=0.1))
        for (dx, dy) in ((-hw * 0.5, hh * 0.42), (hw * 0.45, hh * 0.5), (hw * 0.05, hh * 0.75)):
            r = rnd.uniform(1.1, 1.35)
            circ(doc, cx + dx, sy + dy, r, fill='#F7EED8', stroke='#B89A5A', w=0.25)
            circ(doc, cx + dx, sy + dy, r * 0.6, fill='none', stroke='#C9AE72', w=0.2)


def type2(doc, cx, hw, hh, seed=1, hyper=False):
    """Cuboidal type II pneumocyte bulging into the air space: microvilli, round nucleus, lamellar bodies."""
    rnd = random.Random(seed)
    xs = _xs(cx - hw, cx + hw, 0.8)
    top = [(x, apical(x)) for x in xs]
    bas = [(x, surface(x) + 2.6 + 0.5 * G.fibrosis(x)) for x in xs]
    body = mix('#F4DBD0', '#EFD1C2', 0.5 if hyper else 0)
    path(doc, poly_d(top + bas[::-1], True), fill=shade(doc, body, light=0.5, dark=0.06), stroke=EPI_LINE, w=0.5)
    for x in (cx - hw * 0.98, cx + hw * 0.98):
        path(doc, 'M%s,%s L%s,%s' % (fmt(x), fmt(apical(x)), fmt(x), fmt(surface(x) + 2.6)), stroke=EPI_LINE, w=0.35, op=0.7)
    mv = []
    for x in _xs(cx - hw * 0.7, cx + hw * 0.7, 1.1):
        mv.append('M%s,%s l0,-0.9' % (fmt(x), fmt(apical(x))))
    doc.add('<path d="%s" stroke="%s" stroke-width="0.3" stroke-linecap="round" opacity="0.7"/>' % (''.join(mv), EPI_LINE))
    sy = surface(cx)
    circ(doc, cx + 0.5, sy - hh * 0.22, min(2.7, hh * 0.27), fill=shade(doc, '#A796B5', light=0.3, dark=0.1))
    for (dx, dy) in ((-hw * 0.5, -hh * 0.45), (hw * 0.45, -hh * 0.55), (-hw * 0.1, -hh * 0.78), (hw * 0.12, -hh * 0.08)):
        x, y = cx + dx, sy + dy
        r = rnd.uniform(1.15, 1.45)
        circ(doc, x, y, r, fill='#F7EED8', stroke='#B89A5A', w=0.25)
        circ(doc, x, y, r * 0.6, fill='none', stroke='#C9AE72', w=0.2)
    if not hyper:
        for dx in (-3.5, 2.5, 6.5):
            x = cx + hw + 2 + dx
            path(doc, 'M%s,%s q1.0,-0.8 2.0,0' % (fmt(x), fmt(apical(x) - LIN - 0.05)), stroke=FILM, w=0.35, op=0.8)


def _damage(doc):
    """Injured type I epithelium beneath the open cup: frayed, lifting cell, a denuded patch of basement membrane."""
    d0, d1 = DAMAGE
    s = surface
    rnd = random.Random(21)
    x = d0 + 6
    while x < d1 - 6:
        L = rnd.uniform(2.5, 5.5)
        if not (938 <= x <= 958):
            pts = [(x + u, s(x + u) + rnd.uniform(-0.25, 0.35)) for u in (0, L / 2, L)]
            path(doc, poly_d(pts), stroke='#A2685D', w=0.6, op=0.9)
        x += L + rnd.uniform(1.2, 2.6)
    xs = _xs(938, 958, 1.0)
    path(doc, poly_d([(x, s(x) - 0.2) for x in xs] + [(x, s(x) + 2.4) for x in xs[::-1]], True), fill='#F2E2D6')
    path(doc, poly_d([(x, s(x) + 2.5) for x in xs]), stroke='#93685C', w=0.75, op=0.9)
    for k in range(7):
        x = rnd.uniform(939, 957)
        circ(doc, x, s(x) + rnd.uniform(0.3, 1.8), rnd.uniform(0.35, 0.6), fill='#C9A3A8', op=0.7)
    x0 = 958
    flap = [(x0, s(x0) + 0.8), (x0 + 1.6, s(x0) - 2.4), (x0 + 6, s(x0 + 6) - 2.9), (x0 + 11, s(x0 + 11) - 0.5)]
    path(doc, cr_path(flap, False) + ' L%s,%s Z' % (fmt(x0 + 1), fmt(s(x0) + 1.6)), fill='#F1D6CD', stroke='#A2685D', w=0.55)
    path(doc, cr_path([(x0 + 1, s(x0) + 1.5), (x0 + 4, s(x0 + 4) - 0.2), (x0 + 9, s(x0 + 9) + 0.5)], False), stroke=EPI_LINE, w=0.35, op=0.6)
    ell(doc, 925, s(925) + 1.3, 3.2, 1.25, fill='#7E6E92', op=0.8)
    for (x, dy, r) in ((916, -1.2, 0.8), (931, -1.5, 0.7), (970, -1.2, 0.75), (979, -1.0, 0.6)):
        circ(doc, x, s(x) + dy, r, fill='#F3DCD3', stroke=EPI_LINE, w=0.25)


def _cell_contact(doc):
    """Where the macrophage base rests on the lining fluid: a soft contact shadow on the epithelium."""
    xs = _xs(372, 905, 3)
    g = _ug(doc, 'linear', [(0, SHADOW, 0.0), (0.06, SHADOW, 0.07), (0.94, SHADOW, 0.07), (1, SHADOW, 0)], x1=372, y1=0, x2=905, y2=0)
    top = [(x, surface(x) - 0.2) for x in xs]
    bot = [(x, surface(x) + 1.6) for x in xs]
    path(doc, poly_d(top + bot[::-1], True), fill=g)


def _free_particle(doc):
    """Particle fates vary: a silica crystal left free on the epithelium (not taken up)."""
    x = 289
    silica(doc, x, surface(x) - LIN - 2.9, s=0.42, rot=10)


# ----------------------------------------------------------------------------------------- labels (healthy anatomy)
def labels(doc):
    c = LAB
    sz = 4.6

    def lab(x, y, text, tgt, anchor='start', col=c):
        T(doc, x, y, text, size=sz, fill=col, anchor=anchor, italic=True, halo=PAPER)
        tw = text_width(text, sz)
        lx = x if anchor == 'start' else (x - tw if anchor == 'end' else x - tw / 2)
        hx = min(max(tgt[0], lx + 2), lx + tw - 2)
        end = (hx, y - sz * 0.92 - 1.0) if tgt[1] < y else (lx - 1.0, y - sz * 0.3)   # target below: meet the text's side
        leader(doc, [tgt, end], color=col, w=0.28)

    lo = lambda x: surface(x) + depth(x)
    caps, gaps = _healthy_caps()
    y1, y2 = 800.5, 807.5
    lab(22, y1, 'type I', (30, lo(30) - 1.2))
    lab(140, y2, 'type II', (150, lower(150) - 1.0))
    cx, rx = min(caps, key=lambda c: abs(c[0] - 250))
    lab(cx - 6, y1, 'capillary', (cx + 4, lo(cx) - 3.5))
    T(doc, 806, 817, 'collagen', size=sz, fill=c, italic=True, halo=TISSUE_F)     # on the fibrotic bundles
    lab(298, 752.5, 'free', (292, surface(292) - 4.4))
