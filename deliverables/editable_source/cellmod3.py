"""Arrows, antigen route and the pathology vignettes inside the macrophage."""
import math, random
from lib import *
from bio import *
from cellmod import *
from cellmod2 import *
from style import shade, contact_shadow, spec, tone, lighten


def ang_pt(c, ang, dr=0):
    return on_circle(c[0], c[1], c[2] + dr, ang)


def pathways(doc):
    # ----------------- phagocytic pathway (vermilion): closure -> maturation
    arrow(doc, [(314, 432), (326, 448), (334, 460)], PHAG, 'transport', w=2.2)
    arrow(doc, [(369, 513), (382, 533)], PHAG, 'transport', w=2.2)
    arrow(doc, [(429, 579), (450, 593)], PHAG, 'transport', w=2.2)
    # membrane fusion (violet, open head): late phagosome + lysosome -> phagolysosome
    arrow(doc, [(512, 634), (528, 640), (542, 641)], CONV, 'fusion', w=1.7)
    arrow(doc, [(676, 597), (662, 604), (650, 611)], CONV, 'fusion', w=1.7)
    # docking of the lysosome on the late phagosome (focus of the Rab/SNARE inset)
    arrow(doc, [(516, 596), (509, 599)], CONV, 'fusion', w=1.2, head=5)
    # early-endosome interactions (kiss-and-run exchange, orange) and late-endosome fusion
    # transient (kiss-and-run) contacts with early endosomes: exchange, not emptying
    arrow(doc, [(449, 532), (433, 543)], CONV, 'fusion', w=0.9, head=4.2, smooth=False)
    arrow(doc, [(378, 594), (387, 589)], CONV, 'fusion', w=0.9, head=3.6, smooth=False)
    arrow(doc, [(527, 538), (516, 556), (506, 578)], CONV, 'fusion', w=1.2, head=5)
    # ----------------- biosynthetic pathway (cobalt)
    arrow(doc, [(614, 309), (614, 325)], BIO, 'transport', w=1.3, head=5)
    arrow(doc, [(656, 318), (656, 337)], BIO, 'transport', w=1.3, head=5)
    arrow(doc, [(614, 346), (613, 364)], BIO, 'transport', w=1.5, head=6)
    arrow(doc, [(656, 358), (655, 366)], BIO, 'transport', w=1.5, head=5)
    arrow(doc, [(566, 458), (566, 469)], BIO, 'transport', w=1.3, head=5)
    arrow(doc, [(630, 458), (630, 469)], BIO, 'transport', w=1.3, head=5)
    arrow(doc, [(563, 489), (552, 501)], BIO, 'transport', w=1.8, head=7)
    arrow(doc, [(624, 487), (598, 500), (570, 511)], BIO, 'transport', w=1.8, head=7)
    arrow(doc, [(541, 548), (532, 575)], BIO, 'transport', w=2.0, head=7)
    arrow(doc, [(568, 538), (628, 562), (675, 579)], BIO, 'transport', w=1.3, head=5.5)
    # M6PR recycling (green dashed) back to the TGN
    arrow(doc, [(527, 512), (512, 492), (514, 468), (536, 449)], RECY, 'recycle', w=1.5)
    # ----------------- breakdown-product export (green dashed)
    px_, py_, pr = PL
    for a in (18, 40, 62):
        x0, y0 = on_circle(px_, py_, pr - 16, a)
        x1, y1 = on_circle(px_, py_, pr + 12, a)
        arrow(doc, [(x0, y0), (x1, y1)], RECY, 'recycle', w=1.5, head=6.5)
        xm, ym = on_circle(px_, py_, pr, a)
        circ(doc, xm, ym, 2.1, fill='#D7F0E4', stroke=RECY, w=0.7)
        for (dx, dy, c) in [(0, 0, '#2E7D32'), (2.6, -2.2, '#F9A825'), (-2.6, 2.4, '#1565C0')]:
            circ(doc, x1 + math.cos(math.radians(a)) * 4 + dx, y1 + math.sin(math.radians(a)) * 4 + dy, 1.2, fill=c)


def silica_vignette(doc):
    x, y, r = SPL
    g = doc.radgrad([(0, '#FFFBF6'), (0.45, '#F5EADF'), (0.85, '#E8D4C1'), (1, '#DCC3AC')], cx=.42, cy=.38, r=.66, fx=.34, fy=.28)
    a0, a1 = 100, 150            # torn arc (towards the NLRP3 inflammasome)
    def ap(a, dr=0):
        return on_circle(x, y, r + dr, a)
    p0, p1 = ap(a1), ap(a0 + 360)
    big = 'M%s,%s A%s,%s 0 1 1 %s,%s' % (fmt(p0[0]), fmt(p0[1]), r, r, fmt(p1[0]), fmt(p1[1]))
    contact_shadow(doc, x, y, r, strength=0.12)
    circ(doc, x, y, r - 0.5, fill=g)
    rim_shade(doc, x, y, r - 1.2, '#8A6A55', op=0.18, w=4.5)
    path(doc, big, stroke=CONV, w=2.1)
    path(doc, big, stroke=lighten(CONV, 0.85), w=0.75)
    spec(doc, x, y, r, a0=200, a1=240, op=0.65, inset=0.84, w=1.4)
    for a, d in ((a1 + 1, 1), (a0 - 1, -1)):
        px, py = ap(a)
        path(doc, 'M%s,%s l%s,%s l%s,%s' % (fmt(px), fmt(py), fmt(d * 2.2), fmt(1.8), fmt(d * -1.2), fmt(2.2)), stroke=CONV, w=1.0)
    circ(doc, x, y, r - 2.8, fill='none', stroke='#6A4C8A', w=0.6, dash='0.2 1.0', op=0.5)
    silica(doc, x + 3, y - 3, s=1.75, rot=-15)
    silica(doc, x + 9, y + 13, s=0.8, rot=30)
    for a in (190, 240, 290, 340, 30, 70):
        px, py = ap(a)
        vatpase(doc, px, py, a, s=0.6)
    # leaking cathepsins and H+ through the tear
    for (a, dr) in ((112, 5), (124, 10), (136, 6), (118, 15), (130, 19), (108, 12)):
        px, py = ap(a, dr)
        enzyme_dot(doc, px, py, 1.9)
    for (a, dr) in ((128, 3), (114, 20)):
        px, py = ap(a, dr)
        hplus(doc, px, py, 0.9)
    nlrp3(doc, NLRP[0], NLRP[1], s=1.45)
    # IL-1beta release (inflammatory signal) through the plasma membrane
    arrow(doc, [(NLRP[0] + 9, NLRP[1] + 2), (790, 530), (836, 528), (858, 524)], INFL, 'signal', w=1.3, head=6)
    for (cx, cy, rt) in [(850, 512, 20), (866, 536, 0), (874, 518, -10)]:
        cytokine(doc, cx, cy, s=1.15, rot=rt)


def asbestos_vignette(doc):
    (x1, y1), (x2, y2) = FIBRE
    # actin-driven pseudopods spreading along the fibre (they cannot meet: the cup stays open)
    up = [(842, 330), (856, 341), (866, 346)]
    dn = [(842, 394), (858, 379), (868, 371)]
    actin_cortex(doc, cr_sample(up, False, 8), seed=12, spacing=2.0, inward=1, lens=(4, 8), w=0.55, spread=30)
    actin_cortex(doc, cr_sample(dn, False, 8), seed=13, spacing=2.0, inward=-1, lens=(4, 8), w=0.55, spread=30)
    asbestos_fibre(doc, x1, y1, x2, y2, w=5.4, color='#D6B676', frays=True)
    # NOX2 on the pocket membrane: ROS released into the open pocket and outside
    from cellmod2 import nox2
    for xx, yy, a in ((800, 357.5, 90 + 180), (790, 372.4, 90)):
        nox2(doc, xx, yy, a, s=0.75)
    for (px, py) in [(878, 338), (890, 372), (876, 380)]:
        ros(doc, px, py, s=1.05)
    for (px, py) in [(886, 330), (898, 366)]:
        enzyme_dot(doc, px, py, 1.8)


def draw_extras(doc):
    pathways(doc)
    silica_vignette(doc)
    asbestos_vignette(doc)
