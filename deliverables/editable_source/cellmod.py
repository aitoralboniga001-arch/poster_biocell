"""The central macrophage: membrane, organelles, both pathways, pathology vignettes, labels."""
import math, random
from lib import *
from bio import *

# ----------------------------------------------------------------------------------------------- outline
CELL_PTS = [
    (330, 190), (352, 165), (395, 150), (430, 142), (470, 150), (520, 138), (575, 132), (630, 140), (690, 134),
    (745, 150), (790, 175), (812, 215), (824, 262), (834, 300), (842, 326),
    (856, 340), (868, 346), (858, 351.2),                     # upper pseudopod reaching along the asbestos fibre
    (830, 353.4), (796, 356.0), (766, 358.4), (750, 361.5),     # open pocket around the fibre (frustrated phagocytosis)
    (746, 366.5), (751, 371.2), (766, 373.6), (796, 371.6), (830, 369.2),
    (860, 368.5), (870, 372.5), (856, 381), (842, 396),       # lower pseudopod
    (838, 440), (846, 484),
    (836, 525), (826, 565), (832, 600), (812, 640), (770, 672), (722, 696), (665, 704), (610, 714), (545, 708),
    (490, 712), (430, 700), (385, 688), (350, 666), (332, 640), (324, 600), (326, 560), (312, 525), (292, 490),
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
    pts = [(rnd.uniform(300, 860), rnd.uniform(125, 720)) for _ in range(420)]
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
        path(doc, d_, fill='#F6DCCE', stroke='#A9584A', w=1.0)
        line(doc, x0, y0, x1 - (x1 - x0) * 0.12, y1 - (y1 - y0) * 0.12, '#C2571A', 0.4, op=0.6)
    # plasma membrane bilayer: tinted leaflets, light hydrophobic core, fine head-group beading
    path(doc, d, fill='none', stroke='#A6503F', w=4.6)
    path(doc, d, fill='none', stroke='#FCEAE1', w=2.0)
    for off, c in ((1.55, '#8A3A2B'), (-1.55, '#8A3A2B')):
        path(doc, poly_d(offset_poly(OUT, off), True), stroke=c, w=1.05, dash='0.01 1.9', op=0.85)
    # a faint top-left highlight on the outer leaflet (lit side)
    path(doc, poly_d(offset_poly(OUT, 3.0), True), stroke='#FFFFFF', w=0.6, op=0.35)
