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
    # (V1.2) the IL-1beta / cytokine signal leaving the cell toward the wall is drawn by m_patho.cytokine_route()


def _interp_y(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if min(x0, x1) <= x <= max(x0, x1):
            return y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1e-9)
    return pts[-1][1]


def asbestos_vignette(doc):
    """Open frustrated-phagocytosis cup at the lower-right edge (the fibre itself is drawn outside the cell by m_patho).
    Actin-driven pseudopod lips spread along the fibre but cannot meet; NOX2 sits in the cup membrane, and
    lysosomes fuse with it (exocytosis), releasing their enzymes into the open gap."""
    roof_p = CUP_UPPER_LIP[-1:] + CUP_POCKET[:8]                     # inner roof, right -> left
    floor_p = CUP_POCKET[9:] + CUP_LOWER_LIP[:1]                      # inner floor, left -> right
    hood_p = CUP_UPPER_LIP[4:9]                                       # outer surface of the hood, left -> right
    roof = [to_cell(*p) for p in roof_p]
    floor = [to_cell(*p) for p in floor_p]
    hood = [to_cell(*p) for p in hood_p]
    actin_cortex(doc, cr_sample(roof, False, 8), seed=12, spacing=1.9, inward=-1, lens=(2.6, 5.2), w=0.5, spread=32)
    actin_cortex(doc, cr_sample(floor, False, 8), seed=13, spacing=2.2, inward=-1, lens=(1.4, 2.4), w=0.45, spread=28)
    actin_cortex(doc, cr_sample(hood, False, 8), seed=14, spacing=1.7, inward=-1, lens=(2.4, 4.6), w=0.5, spread=34)
    # NOX2 in the cup membrane (cytosolic subunits on the cytosolic side)
    S_ = CELL_S
    for px in (782, 846, 902):
        nox2(doc, *to_cell(px, _interp_y(roof_p, px)), 270, s=0.62)
    for px in (812, 868):
        nox2(doc, *to_cell(px, _interp_y(floor_p, px)), 90, s=0.55)
    # lysosomes docking / fusing with the cup membrane (exocytosis of hydrolases into the gap)
    for (px, r, fusing) in ((815, 3.3, True), (880, 2.9, False)):
        py = _interp_y(roof_p, px) - 1.55 - r - (0.0 if fusing else 0.9)
        x, y = to_cell(px, py)
        rr = r / S_
        vesicle(doc, x, y, rr, fill='#ECE1F7', stroke=CONV, w=0.55)
        for (dx, dy) in ((-0.9, -0.6), (0.9, -0.2), (0, 0.9)):
            enzyme_dot(doc, x + dx * rr * 0.45, y + dy * rr * 0.45, 0.62)
        if fusing:
            # open fusion pore: a gap in the lysosome + plasma membrane, enzymes spilling into the cup
            gx, gy = to_cell(px, _interp_y(roof_p, px))
            circ(doc, gx, gy - 1.2, 1.25, fill='#F7FBFD')
            enzyme_dot(doc, gx - 0.6, gy + 2.6, 0.62)


def short_fibre_phagosome(doc):
    """Fates vary: a SHORT fibre can be engulfed completely (it then persists in a phagolysosome)."""
    x, y = to_cell(818, 659)
    rot = -18
    a = math.radians(rot)
    rx, ry = 11.0, 5.6
    contact_shadow(doc, x, y, rx, ry, rot=rot, strength=0.1)
    ell(doc, x, y, rx, ry, fill=shade(doc, '#EEE4F6', light=0.5, dark=0.06), stroke=CONV, w=1.2, rot=rot)
    ell(doc, x, y, rx, ry, fill='none', stroke=lighten(CONV, 0.85), w=0.4, rot=rot)
    L = 15.0
    asbestos_fibre(doc, x - math.cos(a) * L / 2, y - math.sin(a) * L / 2, x + math.cos(a) * L / 2, y + math.sin(a) * L / 2,
                   w=1.6, color='#D6B676', frays=False, seed=8)
    for (u, v) in ((-0.55, 0.45), (0.5, -0.5)):
        enzyme_dot(doc, x + u * rx * math.cos(a) - v * ry * math.sin(a), y + u * rx * math.sin(a) + v * ry * math.cos(a), 0.62)


def contact_receptors(doc):
    """2.1: receptors engaging the opsonised bacterium at the upper phagocytic cup (magnified by m_recognition)."""
    for (y, kind, col) in CONTACT_RECEPTORS:
        if kind == 'tlr':
            col = '#8E3B8F'          # TLR4 identity colour: plum (V1.2; avoids clashing with NOX2 crimson)
        receptor(doc, 307, y, h=10, rot=-90, color=col, kind=kind, tail=True)
    for y in (318, 327):                                       # IgG engages FcγR (y 322)
        antibody(doc, 299, y, s=0.9, rot=-90)
    c3b(doc, 297, 310, s=1.0, rot=-90, color='#1F8F8A')       # iC3b on CR3 (y 310)


def draw_extras(doc):
    pathways(doc)
    silica_vignette(doc)
    asbestos_vignette(doc)
    short_fibre_phagosome(doc)
    contact_receptors(doc)
