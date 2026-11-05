"""V2 skeleton: the silhouette of the one giant macrophage (poster mm, no cell transform).

The outline is an amoeboid dome built clockwise from a list of control points (Catmull-Rom), with two contract
segments spliced in EXACTLY (geom_v2.LEAD_MEM, geom_v2.RIGHT_MEM: sampled as open Catmull-Rom splines, i.e. what
cr_sample(seg, closed=False) gives), plus filopodia and dorsal ruffles inserted as part of the same membrane.

    top-left notch (locator in the air) -> dome over the nucleus -> shallow saddle -> right lobe -> round shoulder
    -> right flank (RIGHT_MEM) -> open frustrated-phagocytosis cup at the right base (thick actin hood above the
    asbestos fibre, thin lamella below it on the epithelium; lips never meet, mouth opens to the right)
    -> ventral base resting on the wall (wallgeom.base_y) -> left heel -> lower pseudopod arm around the bacterium
    -> leading edge (LEAD_MEM) -> upper pseudopod arm -> back to the notch.
"""
import math, os, random
from lib import *
from bio import *
import geom_v2 as V
import wallgeom as W

# ----------------------------------------------------------------------------------------------- transform (V2: none)
CELL_S = 1.0
CELL_T = (0.0, 0.0)


def to_poster(x, y):
    return CELL_S * x + CELL_T[0], CELL_S * y + CELL_T[1]


def to_cell(x, y):
    return (x - CELL_T[0]) / CELL_S, (y - CELL_T[1]) / CELL_S


def cell_transform():
    return 'matrix(1 0 0 1 0 0)'


# ----------------------------------------------------------------------------------------------- control points
# leading lamella (low, over zone A) -> steep rise over the nucleus -> dome -> saddle -> right lobe -> round shoulder
TOP = [(318, 236), (321, 216), (328, 197), (340, 178), (356, 159), (376, 141), (402, 125), (430, 113), (458, 110), (490, 114),
       (524, 124), (558, 140), (592, 153), (624, 159), (654, 158), (684, 155), (712, 147), (742, 132), (776, 120),
       (818, 114), (854, 114), (890, 116), (924, 121), (956, 131), (981, 146), (997, 166), (1003, 190)]
# right flank: steps inward with the zone-D staircase into a concave waist (a bay of air), then bulges out around
# the silica zone to meet RIGHT_MEM exactly
FLANK = [(999, 212), (990, 236), (977, 258), (966, 278), (963, 302), (958, 326), (947, 346), (941, 368), (938, 388),
         (929, 408), (915, 430), (909, 456), (911, 476), (921, 492), (941, 502), (967, 508), (990, 517)]
# open cup around the asbestos fibre (fibre axis y ~746-747 here, half-width 2.2)
CUP_UPPER_LIP = [(996, 709), (991, 722), (994, 731), (1001, 736), (1007, 739.3)]           # outer hood surface -> tip
CUP_POCKET = [(1001, 742.0), (978, 741.6), (952, 741.0), (926, 740.4), (906, 740.6), (893, 743.0), (888.5, 747.0),
              (891, 750.6), (901, 752.0), (924, 752.6), (948, 752.9)]                       # roof -> back -> floor
CUP_LOWER_LIP = [(964, 753.4), (973, 754.6)]                                                # lamella tip
ASB_FIBRE_POSTER = V.ASB_FIBRE
ASB_FIBRE_W = V.ASB_FIBRE_W
HOOD_TIP = CUP_UPPER_LIP[-1]
LAMELLA_TIP = CUP_LOWER_LIP[-1]


def _base():
    xs = [966] + list(range(940, 236, -28)) + [232]
    return [(x, W.base_y(x)) for x in xs]


HEEL = [(224, W.base_y(224) - 0.6), (204, W.base_y(204) - 2.6), (184, 755), (172, 738), (174, 716)]
LEFT_FLANK = [(186, 692), (202, 664), (214, 634), (218, 604), (210, 578)]
# lower pseudopod arm, traversed upward: outer (lower) surface leftward -> tip -> inner surface rightward -> cleft
LOWER_ARM = [(178, 556), (164, 541), (142, 532), (116, 528), (90, 524), (66, 516), (48, 505), (37, 493), (31, 482),
             (31, 475), (38, 484), (54, 492), (72, 499), (92, 505), (114, 509), (134, 508.5), (145.5, 503)]
# upper arm = mirror image (about the bacterium's axis), slightly varied, with its own root into the notch
_MY = V.BACT[1]
UPPER_ARM = [(x + (1.5 if i > 8 else 0), 2 * _MY - y - (1.5 if 1 < i < 7 else 0)) for i, (x, y) in enumerate(LOWER_ARM[::-1][:-2])]
UPPER_ROOT = [(166, 258), (196, 265), (224, 264), (252, 272), (280, 274), (300, 268), (312, 256)]


def _sequence():
    """Closed control list as (point, tag) pairs; consecutive 'lead' / 'right' points are the contract segments."""
    seq = []
    seq += [(p, None) for p in TOP + FLANK]
    seq += [(p, 'right') for p in V.RIGHT_MEM]
    seq += [(p, None) for p in CUP_UPPER_LIP + CUP_POCKET + CUP_LOWER_LIP + _base() + HEEL + LEFT_FLANK + LOWER_ARM]
    seq += [(p, 'lead') for p in V.LEAD_MEM[::-1]]          # traversed upward (clockwise on screen)
    seq += [(p, None) for p in UPPER_ARM + UPPER_ROOT]
    return seq


def _bez(p0, p1, p2, p3, n, tension=0.5):
    c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
    c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
    out = []
    for k in range(n):
        t = k / n
        mt = 1 - t
        out.append((mt ** 3 * p1[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * p2[0],
                    mt ** 3 * p1[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * p2[1]))
    return out


def _sample(seq):
    """Closed Catmull-Rom through all points; spans inside a contract segment use open-spline end conditions so they
    coincide exactly with cr_sample(segment, closed=False).  Returns dense points and a parallel list of tags."""
    n = len(seq)
    pts, tags = [], []
    for i in range(n):
        (p1, t1), (p2, t2) = seq[i], seq[(i + 1) % n]
        p0, t0 = seq[(i - 1) % n]
        p3, t3 = seq[(i + 2) % n]
        fixed = t1 is not None and t1 == t2
        if fixed:
            if t0 != t1:
                p0 = p1
            if t3 != t1:
                p3 = p2
        L = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        m = max(3, int(L / 0.7))
        seg = _bez(p0, p1, p2, p3, m)
        pts += seg
        tags += [t1 if fixed else None] * len(seg)
    return pts, tags


# ----------------------------------------------------------------------------------------------- protrusions
# filopodia: (anchor on the outline, length, lean from the outward normal in degrees, seed)
FILOPODIA = [((236, 270), 18, -18, 1), ((345, 170), 22, -38, 2), ((522, 124), 12, 6, 3), ((742, 132), 20, 18, 4),
             ((890, 116), 12, 10, 5), ((1000, 178), 10, 30, 6), ((931, 400), 13, 40, 7), ((205, 655), 20, -50, 8),
             ((978, 144), 12, 25, 9), ((290, 274), 12, 12, 10), ((963, 300), 11, 35, 11)]
RUFFLES = [((556, 139), 1, 1.1), ((812, 115), -1, 0.75), ((388, 133), 1, 0.75), ((180, 262), 1, 0.7)]   # (anchor, curl direction, scale)


def _nearest(poly, p):
    return min(range(len(poly)), key=lambda i: (poly[i][0] - p[0]) ** 2 + (poly[i][1] - p[1]) ** 2)


def _frame(poly, i):
    a, b = poly[(i - 3) % len(poly)], poly[(i + 3) % len(poly)]
    tx, ty = b[0] - a[0], b[1] - a[1]
    L = math.hypot(tx, ty) or 1
    tx, ty = tx / L, ty / L
    return (tx, ty), (ty, -tx)        # tangent (clockwise travel), outward normal


def _insert(poly, tags, anchor, local, half):
    """Replace the outline around `anchor` (half-width `half` mm of arclength) by `local` points given in the
    (tangent, outward-normal) frame of the anchor."""
    i = _nearest(poly, anchor)
    (tx, ty), (nx, ny) = _frame(poly, i)
    ox, oy = poly[i]
    n = len(poly)
    j0, acc = i, 0.0
    while acc < half:
        acc += math.hypot(poly[j0][0] - poly[j0 - 1][0], poly[j0][1] - poly[j0 - 1][1])
        j0 -= 1
    j1, acc = i, 0.0
    while acc < half:
        acc += math.hypot(poly[(j1 + 1) % n][0] - poly[j1][0], poly[(j1 + 1) % n][1] - poly[j1][1])
        j1 += 1
    new = [(ox + tx * u + nx * v, oy + ty * u + ny * v) for u, v in local]
    return poly[:j0 + 1] + new + poly[j1:], tags[:j0 + 1] + [None] * len(new) + tags[j1:]


def _filopodium_local(L, lean, seed, base=4.6, tip=1.1):
    rnd = random.Random(seed)
    a = math.radians(lean)
    bend = rnd.uniform(-0.12, 0.12) * L
    dx, dy = math.sin(a), math.cos(a)            # direction in the (tangent, normal) frame
    px, py = dy, -dx                              # its perpendicular
    left, right = [], []
    N = 14
    for k in range(N + 1):
        s = k / N
        w = base / 2 * (1 - s) ** 0.9 + tip / 2 * s + base * 0.45 * (1 - s) ** 8
        cx = dx * L * s + px * bend * math.sin(math.pi * s)
        cy = dy * L * s + py * bend * math.sin(math.pi * s)
        left.append((cx - px * w, cy - py * w))
        right.append((cx + px * w, cy + py * w))
    cap = (dx * (L + tip * 0.5), dy * (L + tip * 0.5))
    pts = left + [cap] + right[::-1]
    # the outline runs along +tangent: order from the -u side to the +u side
    if pts[0][0] > pts[-1][0]:
        pts = pts[::-1]
    return [(pts[0][0] - 2.2, -0.4)] + pts + [(pts[-1][0] + 2.2, -0.4)]


def _ruffle_local(curl, k):
    """A dorsal ruffle seen in profile: a thin sheet that rises and curls over (curl = +1 toward travel, -1 against)."""
    outer = [(-9, -0.4), (-7.5, 3.5), (-6, 8.5), (-3.5, 13.2), (0.5, 16.4), (5, 17.2), (9, 15.2), (10.6, 12.0), (9.8, 9.6)]
    inner = [(7.8, 10.6), (5.2, 12.6), (1.8, 12.2), (-1.0, 9.6), (-2.6, 5.2), (-3.0, 1.0), (-2.4, -0.4)]
    pts = [(u * k * curl, v * k) for u, v in outer + inner]
    if curl < 0:
        pts = pts[::-1]
    return pts


FILO_AXES = []           # (base point inside the cell, tip) of each filopodium, filled by build_outline


def build_outline():
    pts, tags = _sample(_sequence())
    for (anchor, L, lean, seed) in FILOPODIA:
        i = _nearest(pts, anchor)
        (tx, ty), (nx, ny) = _frame(pts, i)
        a = math.radians(lean)
        dx, dy = math.sin(a), math.cos(a)
        ox, oy = pts[i]
        FILO_AXES.append(((ox - nx * 7, oy - ny * 7), (ox + (tx * dx + nx * dy) * (L - 1.5), oy + (ty * dx + ny * dy) * (L - 1.5)),
                          (ox + (tx * dx + nx * dy) * L * 0.5, oy + (ty * dx + ny * dy) * L * 0.5)))
        pts, tags = _insert(pts, tags, anchor, _filopodium_local(L, lean, seed), 4.4)
    for (anchor, curl, k) in RUFFLES:
        loc = _ruffle_local(curl, k)
        half = max(abs(loc[0][0]), abs(loc[-1][0])) + 0.6
        pts, tags = _insert(pts, tags, anchor, loc, half)
    return pts, tags


OUT, OUT_TAGS = build_outline()
CELL_D = poly_d(OUT, True)
CELL_PTS = OUT             # (V1 name) dense outline

_DEFAULT_ARMS = (list(LOWER_ARM), list(UPPER_ARM))
_DEFAULT_CUP = (list(CUP_UPPER_LIP), list(CUP_POCKET), list(CUP_LOWER_LIP))
_DEFAULT_OUT = (list(OUT), list(OUT_TAGS), CELL_D, list(FILO_AXES))


def set_outline_state(arms_state=1, hood_state=1):
    """Switch pseudopod arms (0=open, 1=printed, 2=closing, 3=sealed) and asbestos hood (0=rest, 1=printed, 2=max)."""
    global CELL_D, CELL_PTS
    if arms_state == 1 and hood_state == 1:
        LOWER_ARM[:], UPPER_ARM[:] = _DEFAULT_ARMS[0], _DEFAULT_ARMS[1]
        CUP_UPPER_LIP[:], CUP_POCKET[:], CUP_LOWER_LIP[:] = _DEFAULT_CUP[0], _DEFAULT_CUP[1], _DEFAULT_CUP[2]
        OUT[:], OUT_TAGS[:] = _DEFAULT_OUT[0], _DEFAULT_OUT[1]
        CELL_D = _DEFAULT_OUT[2]
        CELL_PTS = OUT
        FILO_AXES[:] = _DEFAULT_OUT[3]
        return
    base_low = _DEFAULT_ARMS[0]
    if arms_state == 0:
        low = [(x + max(0.0, 145.0 - x) * 0.28, y + max(0.0, 145.0 - x) * 0.14) for x, y in base_low]
    elif arms_state == 2:
        low = [
            (178, 556), (164, 541), (142, 532), (114, 529), (84, 524), (56, 514), (34, 498), (21, 476), (16, 448),
            (17, 434), (24, 444), (32, 468), (52, 488), (74, 499), (96, 505), (116, 509), (134, 508.5), (145.5, 503)
        ]
    elif arms_state == 3:
        low = [
            (178, 556), (164, 541), (142, 532), (112, 530), (80, 524), (50, 512), (28, 492), (16, 460), (13, 424),
            (15, 394), (22, 395), (23, 424), (28, 458), (46, 484), (72, 499), (96, 505), (116, 509), (134, 508.5), (145.5, 503)
        ]
    else:
        low = list(base_low)
    LOWER_ARM[:] = low
    UPPER_ARM[:] = [(x + (1.5 if i > 8 else 0), 2 * _MY - y - (1.5 if 1 < i < 7 else 0)) for i, (x, y) in enumerate(low[::-1][:-2])]

    u_def, p_def, l_def = _DEFAULT_CUP
    if hood_state == 0:
        CUP_UPPER_LIP[:] = [(996, 709), (990, 722), (988, 731), (990, 736), (993, 739.0)]
        CUP_POCKET[:] = [(989, 741.8), (970, 741.5), (948, 741.0), (924, 740.4), (906, 740.6), (893, 743.0), (888.5, 747.0),
                         (891, 750.6), (901, 752.0), (924, 752.6), (942, 752.9)]
        CUP_LOWER_LIP[:] = [(954, 753.3), (961, 754.4)]
    elif hood_state == 2:
        CUP_UPPER_LIP[:] = [(996, 709), (993, 722), (1002, 730), (1018, 735.5), (1034, 740.2)]
        CUP_POCKET[:] = [(1027, 742.6), (998, 742.0), (966, 741.2), (932, 740.5), (906, 740.6), (893, 743.0), (888.5, 747.0),
                         (891, 750.6), (901, 752.0), (926, 752.6), (958, 753.1)]
        CUP_LOWER_LIP[:] = [(976, 753.8), (989, 755.0)]
    else:
        CUP_UPPER_LIP[:], CUP_POCKET[:], CUP_LOWER_LIP[:] = list(u_def), list(p_def), list(l_def)

    FILO_AXES.clear()
    pts, tags = build_outline()
    OUT[:], OUT_TAGS[:] = pts, tags
    CELL_D = poly_d(OUT, True)
    CELL_PTS = OUT


def segment(tag):
    """Dense run of the outline that belongs to a contract segment ('lead' or 'right'), in traversal order."""
    return [p for p, t in zip(OUT, OUT_TAGS) if t == tag]


def run_between(a, b):
    """Dense outline run from the point nearest a to the point nearest b (clockwise)."""
    i, j = _nearest(OUT, a), _nearest(OUT, b)
    return OUT[i:j + 1] if i <= j else OUT[i:] + OUT[:j + 1]


def on_circle(x, y, r, ang):
    a = math.radians(ang)
    return x + r * math.cos(a), y + r * math.sin(a)


def tag(doc, x, y, text, color, size=3.3):
    membrane_tag(doc, x, y, text, color, size)


def lab(doc, x, y, text, size=4.2, weight=600, fill=INK, anchor='start', halo=CYTO, **kw):
    T(doc, x, y, text, size=size, weight=weight, fill=fill, anchor=anchor, halo=halo, **kw)


# ----------------------------------------------------------------------------------------------- painting
MEM = '#C07A66'          # plasma-membrane leaflets (warm rose-terracotta)
MEM_CORE = '#FDF0E8'


def _air_clip(doc):
    """Clip region = everything above the epithelium (the cell's halo / shadow never washes over the wall)."""
    c = doc.__dict__.setdefault('_style_cache', {})
    if 'airclip' not in c:
        cid = doc.uid('airclip')
        top = [(x, W.surface(x) - W.LIN - 0.2) for x in range(-10, 1114, 4)]
        doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, poly_d([(-10, 0), (1112, 0)] + top[::-1], True)))
        c['airclip'] = cid
    return c['airclip']


def cell_clip(doc):
    c = doc.__dict__.setdefault('_style_cache', {})
    if 'cellclipV2' not in c:
        cid = doc.uid('cellclipV2')
        doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, CELL_D))
        c['cellclipV2'] = cid
    return c['cellclipV2']


def ug(doc, kind, stops, **a):
    """User-space gradient (absolute mm)."""
    gid = doc.uid('cg')
    st = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (fmt(o), col, fmt(op)) for o, col, op in stops)
    at = ' '.join('%s="%s"' % (k, fmt(v)) for k, v in a.items())
    doc.defs.append('<%sGradient id="%s" gradientUnits="userSpaceOnUse" %s>%s</%sGradient>' % (kind, gid, at, st, kind))
    return 'url(#%s)' % gid


V13 = os.environ.get('POSTER_V13', '1') != '0'     # Nov 2026 light & weight pass (set POSTER_V13=0 for the v12 look)


def contact_shadow(doc):
    """Ambient occlusion where the cell rests on the alveolar wall: a soft warm-dark pool on the epithelium under the
    cell's flattened base, deepest at the contact and fading outwards, so the cell has weight (it sits, not floats)."""
    base = [(x, y) for x, y in OUT if y > W.surface(x) - 9]
    if not base:
        return
    x0, x1 = min(p[0] for p in base), max(p[0] for p in base)
    cx, w = (x0 + x1) / 2, (x1 - x0) / 2
    cid = doc.uid('wallclip')
    top = [(x, W.surface(x) - W.LIN - 0.2) for x in range(-10, 1114, 4)]
    doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, poly_d(top + [(1112, 920), (-10, 920)], True)))
    doc.add('<g clip-path="url(#%s)">' % cid)
    # a band along the contact line: dark right under the base, fading downwards (stacked strokes) and towards both
    # ends of the footprint (a horizontal gradient)
    line = [(x, W.surface(x) - W.LIN) for x in range(int(x0 - 50), int(x1 + 51), 4)]
    fade = ug(doc, 'linear', [(0, '#5E2C20', 0), (0.12, '#5E2C20', 1), (0.88, '#5E2C20', 1), (1, '#5E2C20', 0)],
              x1=x0 - 50, y1=0, x2=x1 + 50, y2=0)
    for wd, op in ((26, 0.06), (14, 0.07), (6, 0.09)):
        path(doc, poly_d(line, False), fill='none', stroke=fade, w=wd, op=op)
    doc.add('</g>')


def _radial_unit(doc):
    c = doc.__dict__.setdefault('_style_cache', {})
    if 'aoGrad' not in c:
        gid = doc.uid('ao')
        doc.defs.append('<radialGradient id="%s"><stop offset="0" stop-color="#6B3426" stop-opacity="1"/>'
                        '<stop offset="0.5" stop-color="#6B3426" stop-opacity="0.5"/><stop offset="1" stop-color="#6B3426" stop-opacity="0"/></radialGradient>' % gid)
        c['aoGrad'] = gid
    return c['aoGrad']


def plasma_membrane(doc):
    """Cytoplasm body (warm, luminous, deeper toward the cortex).  The membrane line is drawn by membrane_line()."""
    from style import soft_shadow_path
    d = CELL_D
    if V13:
        contact_shadow(doc)
    doc.add('<g clip-path="url(#%s)">' % _air_clip(doc))
    soft_shadow_path(doc, d, dx=3.2, dy=5.0, strength=0.045, blur=16, steps=6)
    path(doc, d, fill='none', stroke='#FFFDF8', w=14, op=0.5)
    path(doc, d, fill='none', stroke='#EBCFC0', w=7.0, op=0.3)
    doc.add('</g>')
    body = ug(doc, 'radial', [(0, '#FFFAF4', 1), (0.36, '#FEF3E9', 1), (0.7, '#FBE7D8', 1), (1, '#F3D2BE', 1)],
              cx=500, cy=400, r=620, fx=430, fy=310)
    path(doc, d, fill=body)
    doc.add('<g clip-path="url(#%s)">' % cell_clip(doc))
    for k in range(16):                         # depth toward the cortex (inner glow, deeper at the rim)
        path(doc, d, fill='none', stroke='#E8B79E', w=92 - k * 5.5, op=0.033 if V13 else 0.026)
    # key light from the top left, the far side of the cell turning away from it
    hi, lo = (0.42, 0.17) if V13 else (0.32, 0.10)
    sh = ug(doc, 'linear', [(0, '#FFFFFF', hi), (0.42, '#FFFFFF', 0.0), (0.68, '#C98E7A', 0.0), (1, '#B87A68', lo)],
            x1=160, y1=120, x2=900, y2=780)
    path(doc, d, fill=sh)
    _cytoskeleton(doc)
    doc.add('</g>')


def _cytoskeleton(doc):
    """Faint cross-linked filament mesh (cytosol texture)."""
    from style import inside, dots_path
    rnd = random.Random(77)
    pts = [(rnd.uniform(150, 1005), rnd.uniform(115, 760)) for _ in range(1100)]
    pts = [p for p in pts if inside(OUT, p[0], p[1])]
    segs = []
    for p in pts:
        near = sorted(pts, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)[1:4]
        for q in near[:rnd.choice((2, 3))]:
            if q < p:
                continue
            mx, my = (p[0] + q[0]) / 2 + rnd.uniform(-3, 3), (p[1] + q[1]) / 2 + rnd.uniform(-3, 3)
            segs.append('M%s,%sQ%s,%s %s,%s' % (fmt(p[0]), fmt(p[1]), fmt(mx), fmt(my), fmt(q[0]), fmt(q[1])))
    doc.add('<path d="%s" fill="none" stroke="#A9705C" stroke-width="0.24" stroke-linecap="round" opacity="0.05"/>' % ''.join(segs))
    doc.add('<path d="%s" fill="none" stroke="#A9705C" stroke-width="0.7" stroke-linecap="round" opacity="0.05"/>' % dots_path(pts))


def protrusion_actin(doc):
    """A parallel F-actin bundle in each filopodium (under the membrane)."""
    for (s0, tip, mid) in FILO_AXES:
        vx, vy = tip[0] - s0[0], tip[1] - s0[1]
        L = math.hypot(vx, vy) or 1
        px, py = -vy / L, vx / L
        for off, w, op in ((-0.5, 0.3, 0.5), (0.0, 0.42, 0.7), (0.5, 0.3, 0.5)):
            path(doc, cr_path([(s0[0] + px * off * 2, s0[1] + py * off * 2), (mid[0] + px * off, mid[1] + py * off),
                               (tip[0] + px * off * 0.2, tip[1] + py * off * 0.2)], False), stroke='#D0652A', w=w, op=op)


def membrane_line(doc):
    """Plasma-membrane bilayer drawn on top of the interior: tinted leaflets, light core, fine head-group beading."""
    from style import signed_area
    d = CELL_D
    sg = 1 if signed_area(OUT) > 0 else -1
    path(doc, d, fill='none', stroke=MEM, w=2.9)
    path(doc, d, fill='none', stroke=MEM_CORE, w=1.2)
    for off in (1.0, -1.0):
        path(doc, poly_d(offset_poly(OUT, off), True), stroke='#A45E4D', w=0.7, dash='0.01 1.5', op=0.65)
    lit = ug(doc, 'linear', [(0, '#FFFFFF', 0.85), (0.5, '#FFFFFF', 0.25), (1, '#FFFFFF', 0.0)], x1=150, y1=110, x2=700, y2=600)
    path(doc, poly_d(offset_poly(OUT, sg * 2.1), True), stroke=lit, w=0.6)
