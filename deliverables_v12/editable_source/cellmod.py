"""The central macrophage: membrane, organelles, both pathways, pathology vignettes, labels."""
import math, random
from lib import *
from bio import *

# ----------------------------------------------------------------------------------------------- outline
# The whole cell (outline, organelles, in-cell labels) is drawn in "cell coordinates" inside one transform group;
# poster = CELL_S * cell + CELL_T.  geom.py converts every cell anchor to poster mm with to_poster().
CELL_S = 1.04
CELL_T = (-20.0, 19.0)


def to_poster(x, y):
    return CELL_S * x + CELL_T[0], CELL_S * y + CELL_T[1]


def to_cell(x, y):
    return (x - CELL_T[0]) / CELL_S, (y - CELL_T[1]) / CELL_S


def cell_transform():
    return 'matrix(%s 0 0 %s %s %s)' % (CELL_S, CELL_S, CELL_T[0], CELL_T[1])


# Lower outline in POSTER mm (easier to fit against the wall and the asbestos fibre), converted below.
# Right flank -> open frustrated-phagocytosis cup (upper lip over the fibre, pocket, lower lip on the epithelium,
# lips do not meet; mouth opens to the right, toward the fibre's far end) -> base flattened on the wall -> left heel.
# V1.2 (pathology): the cup is a long tubular invagination along the fibre: a thick actin-driven hood (upper lip)
# reaching out along the fibre, a thin lamella (lower lip) creeping under it on the lining fluid; the lips never meet.
CUP_UPPER_LIP = [(843, 645), (847, 679), (852, 701), (861, 714), (878, 722), (902, 726.5), (926, 730.5), (940, 735),
                 (944, 739.2), (937, 741.2)]
CUP_POCKET = [(918, 739.6), (895, 738.2), (870, 737.2), (840, 736.6), (805, 736.4), (770, 736.6), (748, 737.4), (735, 739.4),
              (729, 744.2), (731, 749.2), (740, 752.2), (760, 752.8), (790, 752.8), (820, 752.6), (850, 752.6), (876, 752.8),
              (893, 753.2)]
CUP_LOWER_LIP = [(900, 753.7), (905, 755.4), (900, 757.3), (880, 757.8), (860, 758.2), (840, 758.6), (820, 759.0)]
BASE_POSTER = [(800, 759.3), (740, 759.5), (660, 759.6), (580, 759.7), (500, 759.6), (440, 759.1), (398, 756.6),
               (366, 749), (343, 734), (330, 713), (325.5, 690)]
# Asbestos fibre (poster mm): near end inside the open cup (clear of both lips), far end resting on the epithelium.
ASB_FIBRE_POSTER = ((742.0, 745.2), (1050.0, 749.6))
ASB_FIBRE_W = 4.4
_LOWER = [to_cell(*p) for p in CUP_UPPER_LIP + CUP_POCKET + CUP_LOWER_LIP + BASE_POSTER]

CELL_PTS = [
    (330, 190), (352, 165), (395, 150), (430, 142), (470, 150), (520, 138), (575, 132), (630, 140), (690, 134),
    (745, 150), (790, 175), (812, 215), (824, 262), (834, 300), (842, 332), (848, 368), (845, 404), (840, 440),
    (846, 484), (836, 525), (826, 565)] + _LOWER + [
    (324, 600), (326, 560), (312, 525), (292, 490),
    (272, 455),                       # lower lip of phagocytic cup
    (300, 440), (313, 407), (299, 376),
    (270, 366),                       # upper lip of phagocytic cup
    (296, 342), (310, 318), (306, 290), (316, 262), (320, 226),
]
OUT = cr_sample(CELL_PTS, closed=True, per=14)


def on_circle(x, y, r, ang):
    a = math.radians(ang)
    return x + r * math.cos(a), y + r * math.sin(a)


def tag(doc, x, y, text, color, size=3.3):
    membrane_tag(doc, x, y, text, color, size)


def lab(doc, x, y, text, size=4.2, weight=600, fill=INK, anchor='start', halo=CYTO, **kw):
    T(doc, x, y, text, size=size, weight=weight, fill=fill, anchor=anchor, halo=halo, **kw)


def plasma_membrane(doc):
    from style import soft_shadow_path, dots_path, inside, SHADOW
    d = cr_path(CELL_PTS, True)
    # lift off the paper: very soft contact shadow (down-right) + pale halo on the paper side
    soft_shadow_path(doc, d, dx=3.0, dy=4.8, strength=0.05, blur=14, steps=5)
    path(doc, d, fill='none', stroke='#FFFDF8', w=13, op=0.55)
    path(doc, d, fill='none', stroke='#EBCFC0', w=7.5, op=0.35)
    grad = doc.radgrad([(0, '#FFF9F5'), (0.55, '#FDF2EB'), (0.85, CYTO), (1, '#F6DCCD')], cx=.5, cy=.45, r=.62)
    path(doc, d, fill=grad)
    # depth: deeper peach toward the cortex fading to a lighter centre (inner glow), clipped to the cell
    cid = doc.uid('cellclip')
    doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
    doc.add('<g clip-path="url(#%s)">' % cid)
    for k in range(14):
        path(doc, d, fill='none', stroke='#EFC8B3', w=76 - k * 5.2, op=0.032)
    # faint cytoskeletal mesh (thin, random cross-linked filaments)
    rnd = random.Random(77)
    pts = [(rnd.uniform(300, 860), rnd.uniform(125, 730)) for _ in range(420)]
    pts = [p for p in pts if inside(OUT, p[0], p[1])]
    segs = []
    for i, p in enumerate(pts):
        near = sorted(pts, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)[1:4]
        for q in near[:rnd.choice((2, 3))]:
            if q < p:
                continue
            mx, my = (p[0] + q[0]) / 2 + rnd.uniform(-3, 3), (p[1] + q[1]) / 2 + rnd.uniform(-3, 3)
            segs.append('M%s,%sQ%s,%s %s,%s' % (fmt(p[0]), fmt(p[1]), fmt(mx), fmt(my), fmt(q[0]), fmt(q[1])))
    doc.add('<path d="%s" fill="none" stroke="#A9705C" stroke-width="0.24" stroke-linecap="round" opacity="0.045"/>' % ''.join(segs))
    doc.add('<path d="%s" fill="none" stroke="#A9705C" stroke-width="0.7" stroke-linecap="round" opacity="0.05"/>' % dots_path(pts))
    doc.add('</g>')
    # filopodia: thin, actin-filled, tapering protrusions
    for (x0, y0, x1, y1) in [(338, 178, 308, 152), (356, 166, 342, 138), (812, 218, 840, 200), (772, 162, 790, 138), (632, 142, 638, 118)]:
        L = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        b, t = 2.6, 0.9
        d_ = 'M%s,%s Q%s,%s %s,%s L%s,%s Q%s,%s %s,%s Z' % (
            fmt(x0 + nx * b), fmt(y0 + ny * b), fmt((x0 + x1) / 2 + nx * 1.6), fmt((y0 + y1) / 2 + ny * 1.6), fmt(x1 + nx * t), fmt(y1 + ny * t),
            fmt(x1 - nx * t), fmt(y1 - ny * t), fmt((x0 + x1) / 2 - nx * 1.6), fmt((y0 + y1) / 2 - ny * 1.6), fmt(x0 - nx * b), fmt(y0 - ny * b))
        path(doc, d_, fill='#F6DCCE', stroke='#C4806C', w=0.7)
        line(doc, x0, y0, x1 - (x1 - x0) * 0.12, y1 - (y1 - y0) * 0.12, '#C2571A', 0.4, op=0.6)
    # plasma membrane bilayer: tinted leaflets, light hydrophobic core, fine head-group beading
    # v5: lighter rose/terracotta, ~40% less weight, so it reads as a membrane rather than a frame
    path(doc, d, fill='none', stroke='#C4806C', w=3.0)
    path(doc, d, fill='none', stroke='#FDEFE8', w=1.25)
    for off in (1.05, -1.05):
        path(doc, poly_d(offset_poly(OUT, off), True), stroke='#A9604F', w=0.72, dash='0.01 1.5', op=0.7)
    # a faint top-left highlight on the outer leaflet (lit side)
    path(doc, poly_d(offset_poly(OUT, 2.1), True), stroke='#FFFFFF', w=0.5, op=0.35)
