"""V2 stage furniture (typography owner): hand-lettered title, header (course, speaking order, painted arrow key),
the section-1 locator sketch in the air, the closing statement (6) and the references.

build_poster calls header(), intro(), conclusion(), references(); caption()/placeholder() stay for module code."""
import math, random
from lib import *
from style import mix
import geom_v2 as G2
import marks as M
from marks import HAND, BANNER, SWASH, INKC, ink, ink_d, ink_circle, brush, hand, badge
from layout2 import REFS, S_BODY

CAPTION = '#3F4A57'
SOFT_INK = '#3A4150'
TITLE_VARIANT = 'D'


# ===================================================================== shared helpers (kept for module code)
def caption(doc, x, y, text, width, size=S_BODY, boldfill=None):
    """Short serif caption.  Returns the height used."""
    return PS(doc, x, y, text, width, size=size, lh=1.2, fill=CAPTION, boldfill=boldfill)


def placeholder(doc, box, name):
    x0, y0, x1, y1 = box
    rect(doc, x0, y0, x1 - x0, y1 - y0, fill='none', stroke='#B9AE9B', sw=0.35, r=3, dash='2.2 2.2', op=0.55)
    T(doc, x0 + 3, y0 + 6, name, size=4.6, fill='#A69B88', italic=True)


# ===================================================================== hand-set text
def jitter_text(doc, x, y, s, size, fill, family=BANNER, seed=0, rot=0.9, bounce=0.012, weight=None, spacing=None,
                spread=None, anchor='start', extra=''):
    """Text whose glyphs sit a little off a ruled line: each letter gets its own tiny rotation and baseline bounce
    (a smooth random walk, not noise), like letters drawn one by one.  spread = ink-gain stroke width."""
    rnd = random.Random(seed)
    rots, dys, prev = [], [], 0.0
    ph = rnd.uniform(0, 6.28)
    for k, ch in enumerate(s):
        b = size * bounce * (math.sin(k * 0.9 + ph) + rnd.uniform(-0.6, 0.6))
        dys.append(b - prev)
        prev = b
        rots.append(rnd.uniform(-rot, rot))
    a = ''
    if weight:
        a += ' font-weight="%s"' % weight
    if spacing is not None:
        a += ' letter-spacing="%s"' % fmt(spacing)
    if spread:
        a += ' stroke="%s" stroke-width="%s" stroke-linejoin="round"' % (fill, fmt(spread))
    doc.add('<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" text-anchor="%s" dy="%s" rotate="%s"%s%s>%s</text>'
            % (fmt(x), fmt(y), family, fmt(size), fill, anchor, ' '.join(fmt(v) for v in dys),
               ' '.join(fmt(v) for v in rots), a, extra, esc(s)))


# ===================================================================== title
RED = '#C0392B'
TITLE_INK = '#1E2433'
# advance widths per 1 unit of font size, measured in Chrome (Sitka Banner regular; Gabriola ss07)
W_HOW, W_WHAT, W_DESTROYS, W_SPACE = 7.3512, 5.64, 2.5342, 0.235


def _destroys(doc, x, y, G, under=True, seed=3):
    """'destroys' in Gabriola swash, red, with a soft watercolour bloom behind it and a painted underline."""
    import texture
    w = W_DESTROYS * G
    if under:
        # pale red wash behind the word, a little off-register (painted after the lettering, under it)
        d = cr_path(blob_pts(x + w * 0.52, y - G * 0.17, w * 0.56, G * 0.2, n=11, j=0.12, seed=seed, rot=-3), True)
        texture.wash(doc, d, ['#F2B4A6', '#F6C9B8', '#EBA08F'], seed=seed + 11, ppm=3, strength=0.55, edge=1.6,
                     clip=False, wobble=1.3)
    hand(doc, x, y, 'destroys', size=G, fill=RED, swash=True,
         extra=' stroke="%s" stroke-width="%s" stroke-linejoin="round"' % (RED, fmt(G * 0.0065)))


def _brush_under(doc, x0, x1, y, w, color, seed=0, rise=-1.8):
    xm = (x0 + x1) / 2
    pts = [(x0, y + 0.6), (x0 + (x1 - x0) * 0.3, y - 0.2), (xm + (x1 - x0) * 0.15, y + rise * 0.4), (x1, y + rise)]
    brush(doc, pts, w, color, seed=seed, op=0.9, dry=0.7)


def title(doc, variant=None):
    v = variant or TITLE_VARIANT
    x0, y0, x1, y1 = G2.TITLE_BOX
    if v == 'A':       # one line, the swash word dropped a little below the line
        S, G = 38, 74
        y = 70
        x = x0 + 50
        jitter_text(doc, x, y, 'How a macrophage', S, TITLE_INK, seed=1, spacing=-0.5, spread=0.12)
        x += W_HOW * S - 8 + 30
        _destroys(doc, x, y + 3, G)
        x += W_DESTROYS * G + 8
        jitter_text(doc, x, y, 'what it engulfs', S, TITLE_INK, seed=2, spacing=-0.5, spread=0.12)
    elif v in ('D', 'C'):     # staggered: line 1 set in, the swash word starts line 2 and its loop fills the margin
        S, G = 43, 77
        jitter_text(doc, x0 + 98, 53, 'How a macrophage', S, TITLE_INK, seed=1, spacing=-0.6, spread=0.14)
        xd = x0 + 64
        if v == 'C':
            _brush_under(doc, xd + 14, xd + W_DESTROYS * G * 0.8, 99, 2.8, RED, seed=4)
        _destroys(doc, xd, 94, G, under=(v == 'D'))
        jitter_text(doc, xd + W_DESTROYS * G + 9, 94, 'what it engulfs', S, TITLE_INK, seed=2, spacing=-0.6, spread=0.14)
    else:              # 'B': two lines flush left
        S, G = 42, 74
        jitter_text(doc, x0 + 2, 50, 'How a macrophage', S, TITLE_INK, seed=1, spacing=-0.6, spread=0.14)
        xd = x0 + 52
        _destroys(doc, xd, 94, G)
        jitter_text(doc, xd + W_DESTROYS * G + 10, 94, 'what it engulfs', S, TITLE_INK, seed=2, spacing=-0.6, spread=0.14)

# ===================================================================== header right
SPEAKERS = [(1, 'Aitor'), (2, 'Nerea'), ('2.7', None), (3, 'Urtzi'), (4, 'Eneritz'), (5, 'Nora'), (6, 'Aitor')]
KEY = [('Phagocytic route', PHAG, None), ('Enzyme route', BIO, None), ('Recycling', RECY, (2.6, 1.8)),
       ('Membrane fusion', CONV, None), ('Pathological effect', PATH, None), ('Inflammatory signal', INFL, (1.2, 1.4))]
# Gabriola advance per unit size (Chrome): used to right-align runs of hand lettering
GAB_W = {'Aitor': 1.62, 'Nerea': 1.80, 'Urtzi': 1.55, 'Eneritz': 2.02, 'Nora': 1.60}


def header(doc):
    title(doc)
    x0, y0, x1, y1 = G2.HEADER_RIGHT
    R = x1 - 2
    hand(doc, R, 29, 'Cell Biology seminar <tspan fill="%s">·</tspan> First-year Medicine' % '#A0937C', size=11.5,
         fill=SOFT_INK, anchor='end')
    # speaking order: hand-inked numbers in the section colours
    r, sz = 3.7, 9.6
    items = [(1, 'Aitor'), (2, 'Nerea'), ('2.7', ''), (3, 'Urtzi'), (4, 'Eneritz'), (5, 'Nora'), (6, 'Aitor')]
    widths = []
    for n, name in items:
        tw = GAB_W.get(name, 0) * sz if name else 0
        widths.append(2 * r + (2.4 + tw if name else 0))
    gaps = [1.6 if items[k + 1][0] == '2.7' else 5.6 for k in range(len(items) - 1)]
    x = R - sum(widths) - sum(gaps)
    y = 48
    for k, (n, name) in enumerate(items):
        rr = r * (0.86 if n == '2.7' else 1.0)
        badge(doc, x + rr, y - 2.6, rr, M.color_of(n), n, seed=40 + k)
        if name:
            hand(doc, x + 2 * rr + 2.4, y, name, size=sz, fill=INKC)
        x += widths[k] + (gaps[k] if k < len(gaps) else 0)
    # the arrow key: painted swatches that match the route ribbons
    cw = [86, 92, 108]
    xs = [R - sum(cw) + 4, R - sum(cw[1:]) + 4, R - cw[2] + 4]
    for k, (label, col, dash) in enumerate(KEY):
        c, row = k % 3, k // 3
        cx, cy = xs[c], 66 + row * 12
        pts = [(cx, cy - 1.6), (cx + 9, cy - 2.3), (cx + 18, cy - 1.7)]
        if dash:
            brush(doc, pts, 1.9 if col == RECY else 1.5, col, seed=60 + k, op=0.95, dash=dash, head=4.2)
        else:
            brush(doc, pts, 2.6, col, seed=60 + k, op=0.9, dry=0.6, head=5.0)
        hand(doc, cx + 24, cy + 0.6, label, size=9.4, fill=INKC)
    # dashed = possible
    py = 91.5
    px = R - 74
    brush(doc, [(px, py - 1.7), (px + 9, py - 2.3), (px + 18, py - 1.8)], 1.3, '#6B6457', seed=77, op=0.9, dash=(2.2, 1.8),
          head=3.6)
    hand(doc, px + 24, py + 0.6, 'dashed = possible', size=8.6, fill='#5E5748')


# ===================================================================== 1: locator sketch (lung -> alveolus)
LUNG_W = ['#E9A9A0', '#F3C6BC', '#DE9488']
AIRC = ['#D7E6EE', '#E8F0F2', '#C9DCE6']
PENCIL = '#2B3040'


def _outline(doc, pts, w, seed, color=PENCIL, closed=True, **kw):
    """Closed ink outline drawn as one or two strokes that overlap where they meet (pen lifted once)."""
    P = list(pts) + ([pts[0], pts[1]] if closed else [])
    ink(doc, P, w=w, color=color, seed=seed, **kw)


def _lungs(doc, ox, oy, s=1.0, seed=10):
    """Trachea, bronchial tree, two lungs.  Returns the point on the right lung chosen for the zoom."""
    import texture
    def T_(p):
        return (ox + p[0] * s, oy + p[1] * s)
    Lp = [(-4, 8), (-10, 7), (-17, 14), (-22, 28), (-25, 44), (-26, 60), (-22, 70), (-12, 70), (-5, 64), (-3, 44), (-3, 22)]
    Rp = [(4, 8), (11, 7), (18, 14), (23, 27), (26, 44), (27, 60), (24, 69), (13, 71), (6, 66), (3, 54), (5, 36), (3, 22)]
    Lp = [T_(p) for p in Lp]
    Rp = [T_(p) for p in Rp]
    for k, P in enumerate((Lp, Rp)):
        texture.wash(doc, cr_path(P, True), LUNG_W, seed=seed + k, ppm=5, strength=0.62, edge=2.0, grain=0.35, clip=False, wobble=1.2)
    for k, P in enumerate((Lp, Rp)):
        _outline(doc, cr_sample(P, True, per=8), 0.55, seed + 3 + k, smooth=False, wobble=0.12, var=0.5)
    # lobar fissures (oblique on both sides, horizontal on the right lung = viewer's left)
    ink(doc, [T_((-24, 30)), T_((-15, 42)), T_((-6, 56))], w=0.3, color=PENCIL, seed=seed + 31, op=0.6, taper=(0.3, 0.3))
    ink(doc, [T_((-23, 38)), T_((-14, 39)), T_((-5, 41))], w=0.26, color=PENCIL, seed=seed + 32, op=0.5, taper=(0.3, 0.3))
    ink(doc, [T_((24, 28)), T_((15, 42)), T_((7, 58))], w=0.3, color=PENCIL, seed=seed + 33, op=0.6, taper=(0.3, 0.3))
    # trachea with cartilage rings
    tr = [T_((0, -12)), T_((0, 4))]
    ink(doc, [T_((-1.6, -12)), T_((-1.6, 3.5))], w=0.45, color=PENCIL, seed=seed + 7)
    ink(doc, [T_((1.6, -12)), T_((1.6, 3.5))], w=0.45, color=PENCIL, seed=seed + 8)
    for k in range(5):
        yy = -10 + k * 3
        ink(doc, [T_((-1.4, yy)), T_((0, yy + 0.5)), T_((1.4, yy))], w=0.22, color=PENCIL, seed=seed + 20 + k, op=0.7)
    # bronchial tree (recursive, thinning)
    rnd = random.Random(seed)

    def branch(p, ang, L, w, depth):
        q = (p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L)
        mid = ((p[0] + q[0]) / 2 + rnd.uniform(-0.6, 0.6), (p[1] + q[1]) / 2 + rnd.uniform(-0.6, 0.6))
        ink(doc, [T_(p), T_(mid), T_(q)], w=w * s, color=PENCIL, seed=rnd.randint(0, 999), taper=(0.0, 0.4), w_end=0.5,
            wobble=0.05, op=0.85)
        if depth > 0:
            for da in (-0.42, 0.38):
                branch(q, ang + da + rnd.uniform(-0.12, 0.12), L * rnd.uniform(0.62, 0.74), w * 0.68, depth - 1)
    for side in (-1, 1):
        a0 = math.pi / 2 + side * -0.62
        branch((side * 1.0, 4.5), a0 if side > 0 else math.pi - (math.pi / 2 - 0.62), 10.5, 0.75, 3)
    return T_((19, 52))


def _alveoli(doc, cx, cy, s=1.0, seed=30):
    """Terminal bronchiole ending in an alveolar sac (a cluster of pale air sacs with pink walls).
    Returns the centre and radius of the alveolus chosen for the zoom."""
    import texture
    rnd = random.Random(seed)
    tube = [(cx - 40 * s, cy - 30 * s), (cx - 27 * s, cy - 24 * s), (cx - 15 * s, cy - 13 * s), (cx - 6 * s, cy - 4 * s)]
    cells = [(-4, 0, 7.4), (6, -9, 7.0), (11, 4, 7.6), (1, 12, 7.2), (-10, 12, 6.6), (17, -6, 6.4), (20, 9, 6.6),
             (12, 18, 6.8), (-1, 23, 6.2), (-12, 1, 5.6)]
    cells = [(cx + x * s, cy + y * s, r * s) for x, y, r in cells]
    # tissue wash behind the sac
    hull = cr_path(blob_pts(cx + 4 * s, cy + 6 * s, 30 * s, 26 * s, n=12, j=0.12, seed=seed), True)
    texture.wash(doc, hull, LUNG_W, seed=seed + 1, ppm=4, strength=0.42, edge=2.0, grain=0.4, clip=False, wobble=1.3)
    # bronchiole tube (two walls) with a pale lumen wash
    tl = offset_poly(cr_sample(tube, False, per=8), 1.9 * s, closed=False)
    tr = offset_poly(cr_sample(tube, False, per=8), -1.9 * s, closed=False)
    texture.wash(doc, poly_d(tl + tr[::-1], True), ['#EFC3B8', '#F5D6CC'], seed=seed + 2, ppm=6, strength=0.8, grain=0.4, clip=False)
    ink(doc, tl, w=0.5, color=PENCIL, seed=seed + 3, smooth=False, wobble=0.1)
    ink(doc, tr, w=0.5, color=PENCIL, seed=seed + 4, smooth=False, wobble=0.1)
    for k, (x, y, r) in enumerate(cells):
        texture.wash(doc, cr_path(blob_pts(x, y, r * 0.92, r * 0.9, n=8, j=0.05, seed=seed + 10 + k), True), AIRC,
                     seed=seed + 40 + k, ppm=6, strength=0.75, clip=False, edge=1.4)
    for k, (x, y, r) in enumerate(cells):
        ink(doc, M.circle_pts(x, y, r, seed=seed + 60 + k, turns=1.04, wob=0.05), w=0.42, color=PENCIL, seed=seed + 80 + k,
            smooth=False, wobble=0.05, var=0.5, taper=(0.2, 0.2), w_end=0.2)
    # capillaries winding over the sac
    for k in range(3):
        pts = [(cx - 12 * s + k * 8 * s + rnd.uniform(-2, 2), cy - 14 * s + rnd.uniform(-2, 2))]
        for j in range(5):
            pts.append((pts[-1][0] + rnd.uniform(-3, 5) * s, pts[-1][1] + 8 * s))
        ink(doc, pts, w=0.32, color='#B8473C', seed=seed + 100 + k, op=0.75, wobble=0.3)
    return cells[6]


def _hatch(doc, cx, cy, r, a0, a1, seed, n=7, color=PENCIL, op=0.5):
    """A few pencil hatch strokes along an arc (shading on the lower-right of a sphere)."""
    rnd = random.Random(seed)
    for k in range(n):
        a = math.radians(a0 + (a1 - a0) * (k + 0.5) / n)
        r0 = r * rnd.uniform(0.74, 0.82)
        p = (cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        q = (cx + math.cos(a) * r * 0.97, cy + math.sin(a) * r * 0.97)
        ink(doc, [p, q], w=0.22, color=color, seed=seed + k, op=op, taper=(0.3, 0.5), wobble=0.02)


def _alveolus(doc, cx, cy, r, seed=50):
    """The enlarged alveolus: air inside, a pink wall, and a tiny macrophage resting on the wall = this scene."""
    import texture
    texture.wash(doc, cr_path(blob_pts(cx, cy, r + 2.4, r + 2.2, n=12, j=0.04, seed=seed), True), LUNG_W, seed=seed + 1,
                 ppm=5, strength=0.9, edge=1.6, clip=False)
    texture.wash(doc, cr_path(blob_pts(cx, cy, r - 0.6, r - 0.7, n=12, j=0.03, seed=seed + 2), True),
                 ['#E4EEF2', '#F4F7F5', '#D6E5EC'], seed=seed + 3, ppm=5, strength=0.9, edge=1.2, clip=False)
    ink(doc, M.circle_pts(cx, cy, r + 2.6, seed=seed + 4, turns=1.05, wob=0.025), w=0.55, color=PENCIL, seed=seed + 5,
        smooth=False, wobble=0.08, var=0.5, taper=(0.2, 0.2), w_end=0.2)
    ink(doc, M.circle_pts(cx, cy, r - 0.4, seed=seed + 6, turns=1.03, wob=0.02), w=0.4, color=PENCIL, seed=seed + 7,
        smooth=False, wobble=0.06, var=0.5, taper=(0.2, 0.2), w_end=0.2, op=0.85)
    _hatch(doc, cx, cy, r + 2.4, 10, 80, seed + 8, n=9, op=0.45)
    # the macrophage: a small amoeboid cell on the lower wall, with a nucleus and a pseudopod
    mx, my = cx - r * 0.12, cy + r * 0.62
    body = [(mx - 7.0, my + 2.6), (mx - 8.6, my - 0.2), (mx - 5.6, my - 3.4), (mx - 1.0, my - 4.6), (mx + 3.8, my - 3.8),
            (mx + 6.6, my - 1.2), (mx + 9.4, my - 2.6), (mx + 8.6, my + 0.4), (mx + 6.2, my + 2.8), (mx, my + 3.4)]
    texture.wash(doc, cr_path(body, True), ['#F6C4A6', '#FADBC6', '#EFAE8C'], seed=seed + 9, ppm=10, strength=1.15,
                 edge=1.5, clip=False, wobble=0.5, inset=0.1)
    _outline(doc, cr_sample(body, True, per=6), 0.4, seed + 10, color='#7A3B2A', smooth=False, wobble=0.04, var=0.4)
    ink(doc, M.circle_pts(mx - 1.6, my - 0.4, 1.9, seed=seed + 11, turns=1.05), w=0.3, color='#4E3F86', seed=seed + 12,
        smooth=False, wobble=0.02)
    texture.wash(doc, cr_path(blob_pts(mx - 1.6, my - 0.4, 1.8, 1.7, n=7, j=0.05, seed=seed + 13), True), ['#B9AEE0'],
                 seed=seed + 14, ppm=14, strength=1.0, clip=False, wobble=0.3)
    # a bacterium being approached, in the air
    bx, by = mx + 11.5, my - 7.5
    ink(doc, [(bx - 2.0, by + 0.8), (bx + 2.0, by - 0.8)], w=1.7, color='#8C9A3A', seed=seed + 15, taper=(0.1, 0.1), w_end=0.7,
        wobble=0.02)


def intro(doc):
    """Section 1: the locator, floating in the air at the top left."""
    x0, y0, x1, y1 = G2.LOCATOR
    M.section(doc, x0 + 3, y0 + 14, 1, 'Alveolar macrophage', M.COLORS[1], size=14)
    lung_pt = _lungs(doc, x0 + 34, y0 + 42, s=1.0)
    ax, ay = x0 + 98, y0 + 72
    acx, acy, ar = _alveoli(doc, ax, ay, s=1.0)
    zx, zy, zr = x1 - 22, y0 + 80, 19.5
    # zoom leaders: lung spot -> sac, alveolus -> enlarged alveolus (pencil, dashed, hand-drawn)
    ink_circle(doc, lung_pt[0], lung_pt[1], 3.4, color=RED, w=0.5, seed=91)
    brush(doc, [(lung_pt[0] + 3.6, lung_pt[1] - 2.0), (lung_pt[0] + 12, lung_pt[1] - 10), (ax - 30, ay - 23)], 0.55, PENCIL,
          seed=92, op=0.8, dash=(1.6, 1.4), head=2.4)
    ink_circle(doc, acx, acy, ar + 1.6, color=RED, w=0.5, seed=93)
    for sgn in (-1, 1):
        a = math.atan2(zy - acy, zx - acx) + sgn * math.pi / 2
        p = (acx + math.cos(a) * (ar + 1.6), acy + math.sin(a) * (ar + 1.6))
        q = (zx + math.cos(a) * (zr + 2.8), zy + math.sin(a) * (zr + 2.8))
        ink(doc, [p, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.5 * sgn), q], w=0.3, color=PENCIL, seed=94 + sgn, op=0.55,
            taper=(0.1, 0.3))
    _alveolus(doc, zx, zy, zr)
    # labels (hand)
    lab = '#4B4F5C'
    hand(doc, x0 + 4, y0 + 118, 'lung', size=9, fill=lab)
    hand(doc, ax - 44, ay - 33, 'bronchiole', size=8.6, fill=lab)
    hand(doc, ax - 18, ay + 45, 'alveolar sac', size=8.6, fill=lab)
    hand(doc, ax + 14, ay + 53, '~200 µm', size=7.4, fill='#8A7F6C')
    hand(doc, zx, zy + zr + 13, 'this scene', size=11, fill=RED, anchor='middle')
    hand(doc, zx, zy + zr + 20.5, 'one cell ~20 µm', size=7.4, fill='#8A7F6C', anchor='middle')


# ===================================================================== 6: conclusion
def conclusion(doc):
    y, x = G2.CONCL_Y, 25
    sz = 14
    r = 5.8
    badge(doc, x + r, y - sz * 0.2 - 0.4, r, M.COLORS[6], 6, seed=66)
    txt = ('Two routes <tspan fill="%s">converge to destroy</tspan>; when the cargo persists, the same machinery '
           '<tspan fill="%s">injures the lung</tspan>.' % (RED, '#9A560A'))
    hand(doc, x + 2 * r + 5, y, txt, size=sz, fill=INKC)


# ===================================================================== references
def references(doc):
    x0, y0, x1, y1 = G2.REFS
    sz, lh = 3.1, 1.2
    cols, gap = 3, 12
    cw = (x1 - x0 - gap * (cols - 1)) / cols
    split = [0, 5, 9, 13]
    fam = "'Sitka Text',Georgia,serif"
    for c in range(cols):
        yy = y0 + 5.5
        x = x0 + c * (cw + gap)
        for n in range(split[c], split[c + 1]):
            T(doc, x, yy, '%d' % (n + 1), size=sz, weight=600, fill='#8F846F', family=SERIF)
            hh = P(doc, x + 4.6, yy, REFS[n], cw - 5, size=sz, lh=lh, fill='#6F6757', family=SERIF)
            yy += hh + 0.35
    hand(doc, x1, y0 + 5.5 + 4 * (sz * lh + 0.35) + 0.6, 'Original illustration · schematic, not to scale; molecular detail enlarged',
         size=6.4, fill='#857A66', anchor='end')
