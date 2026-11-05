"""Right column: pathology (silicosis & asbestosis) as the extension of the macrophage mechanism."""
import math, random
from lib import *
from bio import *
from panels_common import *
from annot import step, DPATH, DINFL, DPHAG

RX, RW = 880, 195
SIL = '#6C7A90'
FIB = '#9A7326'


def lane_chip(doc, x, y, text, color):
    return chip(doc, x, y, text, color, size=3.9, weight=700, pad=2.8)


def title_block(doc):
    x, y, w, h = RX, 108, RW, 40
    rect(doc, x, y, w, h, fill='#FBEFD9', stroke='#E3C487', sw=0.8, r=5)
    badge(doc, x + 10.5, y + 11, 5, r=6.6, fill=PATH, size=8.2)
    T(doc, x + 21, y + 14, 'Silicosis & asbestosis', size=8.4, weight=700, fill='#6B3E05', family=SERIF, kind='serif')
    T(doc, x + w - 6, y + 25, 'NORA · PATHOLOGY', size=3.6, weight=600, fill='#8A6A2A', anchor='end', spacing=0.6)
    P(doc, x + 8, y + 27, 'Persistent particles turn the same machinery against the lung.', w - 14, size=4.3, fill='#6B4A12', italic=True, lh=1.15)


def particles(doc):
    x, y, w, h = RX, 152, RW, 116
    card(doc, x, y, w, h)
    step(doc, x + 6, y + 10, '5.1', PATH, 3.4)
    T(doc, x + 18, y + 10.4, 'Exposure: two particles, two shapes', size=5.0, weight=700, fill=NAVY)
    hw = (w - 14) / 2
    # silica
    sx = x + 5
    rect(doc, sx, y + 16, hw, h - 20, fill='#F2F4F8', stroke='#C9D1DE', sw=0.6, r=3)
    for (dx, dy, s, r_) in [(-14, 2, 1.55, 10), (6, -4, 1.9, -20), (16, 10, 1.0, 40), (-6, 14, 1.0, 5)]:
        silica(doc, sx + hw / 2 + dx, y + 36 + dy, s=s, rot=r_)
    T(doc, sx + hw / 2, y + 62, 'Crystalline silica', size=5.0, weight=700, fill='#3E4C61', anchor='middle')
    T(doc, sx + hw / 2, y + 68.5, 'quartz, SiO₂', size=4.2, fill='#3E4C61', anchor='middle')
    P(doc, sx + 4, y + 77, 'Mining, quarrying, stone cutting, drilling', hw - 8, size=4.8, lh=1.16, fill=INK)
    P(doc, sx + 4, y + 98, '**Angular**, compact crystals', hw - 8, size=4.8, lh=1.16, boldfill='#3E4C61')
    # asbestos
    ax = x + 9 + hw
    rect(doc, ax, y + 16, hw, h - 20, fill='#FAF3E3', stroke='#E3C487', sw=0.6, r=3)
    asbestos_fibre(doc, ax + 8, y + 30, ax + hw - 14, y + 44, w=3.6, color='#D6B676')
    asbestos_fibre(doc, ax + 12, y + 46, ax + hw - 10, y + 36, w=2.8, color='#CDA95F')
    T(doc, ax + hw / 2, y + 62, 'Asbestos fibres', size=4.9, weight=700, fill='#6B4A12', anchor='middle')
    T(doc, ax + hw / 2, y + 68.5, 'serpentine · amphibole', size=4.2, fill='#6B4A12', anchor='middle')
    P(doc, ax + 4, y + 77, 'Insulation, construction materials', hw - 8, size=4.8, lh=1.16, fill=INK)
    P(doc, ax + 4, y + 98, '**Long, thin**, biopersistent fibres', hw - 8, size=4.8, lh=1.16, boldfill='#8A5A12')


def lane(doc, x, y, color, chip_text, steps, boldfill, numbered=3):
    rect_y = y
    lane_chip(doc, x + 11, y - 1, chip_text, color)
    ty = y + 12
    for k, s_ in enumerate(steps):
        if k < numbered:
            circ(doc, x + 14, ty - 1.6, 2.7, fill=color)
            T(doc, x + 14, ty - 0.2, str(k + 1), size=3.6, weight=700, fill='#fff', anchor='middle')
        hh = P(doc, x + 20, ty, s_, RW - 26, size=5.0, lh=1.15, boldfill=boldfill, fill=INK if k < numbered else INK2)
        ty += max(hh, 5.5) + 2.4
    rect(doc, x + 5, rect_y, 2.4, ty - rect_y - 3, fill=color, r=1)
    return ty


def dysfunction(doc):
    x, y, w, h = RX, 272, RW, 152
    card(doc, x, y, w, h)
    step(doc, x + 6, y + 10, '5.2', PATH, 3.4)
    T(doc, x + 18, y + 10.4, 'Why the macrophage fails', size=5.0, weight=700, fill=NAVY)
    e = lane(doc, x, y + 19, SIL, 'SILICA', ['Taken up via scavenger receptors (MARCO, SR-A)',
                                            'Phagolysosome membrane **damaged**: cathepsin B leaks',
                                            '**NLRP3 inflammasome** → caspase-1 → IL-1β',
                                            'Cell dies; crystal is released and re-ingested'], '#3E4C61', numbered=4)
    lane(doc, x, e + 4, '#B07A1E', 'ASBESTOS', ['**Long fibres** exceed the cell: **frustrated phagocytosis**, the cup cannot close',
                                                'Sustained NOX2 → ROS; enzymes spill outside',
                                                'Persistent activation: TNF-α, IL-1β',
                                                '~~Short fibres can still be engulfed and cleared~~'], '#8A5A12', numbered=3)


def inflammation(doc):
    x, y, w, h = RX, 428, RW, 100
    card(doc, x, y, w, h)
    step(doc, x + 6, y + 10, '5.3', INFL, 3.4)
    T(doc, x + 18, y + 10.4, 'Inflammation that does not resolve', size=5.0, weight=700, fill=NAVY)
    # stressed macrophage -> mediators -> recruited cells
    mx, my = x + 28, y + 44
    path(doc, blob(mx, my, 15, 13, n=9, j=0.1, seed=6), fill='#F8DCCD', stroke='#B2594A', w=1.3)
    circ(doc, mx - 2, my - 1, 5, fill='#CFC7EA', stroke='#6A5FA6', w=0.5)
    for (dx, dy) in [(22, -14), (30, -4), (26, 8), (36, -18), (38, 4)]:
        cytokine(doc, mx + dx, my + dy, s=1.1, rot=dx * 3)
    for (dx, dy) in [(20, 16), (32, 14), (13, -20)]:
        ros(doc, mx + dx, my + dy, s=1.05)
    arrow(doc, [(mx + 44, my - 4), (mx + 58, my - 4)], INFL, 'signal', w=1.2, head=5, smooth=False)
    # recruited cells
    for (cx_, cy_, c_) in [(x + 111, y + 34, '#9DB6E3'), (x + 128, y + 50, '#C9B0E6'), (x + 108, y + 58, '#9DB6E3'), (x + 146, y + 36, '#C9B0E6')]:
        circ(doc, cx_, cy_, 6.2, fill=c_, stroke='#5B6B93', w=0.6)
        circ(doc, cx_ - 1, cy_ - 1, 2.6, fill='#5B6B93', op=0.55)
    arrow(doc, [(x + 160, y + 58), (x + 164, y + 40), (x + 150, y + 26), (mx + 4, my - 22)], INFL, 'signal', w=0.9, head=4, smooth=True, opacity=0.8)
    P(doc, x + 6, y + 74, '**Cytokines** (TNF-α, IL-1β, IL-6) and **ROS** recruit and activate monocytes and neutrophils; the particle stays, so the signal persists.', w - 12, size=4.7, lh=1.14, boldfill=DINFL)


def alveoli(doc, cx, cy, fibrotic):
    pos = [(cx - 15, cy - 12, 15), (cx + 15, cy - 12, 15), (cx, cy + 15, 15)]
    if not fibrotic:
        for (px, py, r) in pos:
            circ(doc, px, py, r, fill='#EAF3F8', stroke='#D6A79A', w=1.3)
        for (px, py, r) in pos:
            a = math.atan2(py - cy, px - cx)
            ell(doc, px + math.cos(a) * r, py + math.sin(a) * r, 1.4, 0.9, fill='#C0392B', rot=math.degrees(a))
        path(doc, blob(cx - 15, cy - 12, 4.6, 3.8, n=7, j=0.1, seed=2), fill='#F8DCCD', stroke='#B2594A', w=0.7)
    else:
        pos = [(cx - 14, cy - 11, 8.5), (cx + 15, cy - 13, 7), (cx + 2, cy + 14, 8)]
        # thick collagen-rich septa
        for (px, py, r) in pos:
            circ(doc, px, py, r + 6.5, fill='#CDAE78', stroke='#8A6A33', w=0.8)
        rnd = random.Random(5)
        for k in range(26):  # collagen fibres
            a = rnd.uniform(0, 6.28)
            rr = rnd.uniform(11, 26)
            x0, y0 = cx + rr * math.cos(a), cy + rr * math.sin(a)
            ang = rnd.uniform(0, 3.14)
            path(doc, 'M%s,%s q%s,%s %s,%s' % (fmt(x0), fmt(y0), fmt(math.cos(ang) * 3), fmt(math.sin(ang) * 3 - 1.2), fmt(math.cos(ang) * 6), fmt(math.sin(ang) * 6)), stroke='#7A5320', w=0.55)
        for (px, py, r) in pos:
            circ(doc, px, py, r, fill='#EAF3F8', stroke='#8A6A33', w=0.6)
        ell(doc, cx - 4, cy + 1, 7, 2.2, fill='#8E5FB0', stroke='#5B3A78', w=0.4, rot=35)      # myofibroblast
        ell(doc, cx + 14, cy + 6, 6, 2.0, fill='#8E5FB0', stroke='#5B3A78', w=0.4, rot=-30)
        for (dx, dy) in [(-20, 4), (22, -2), (0, -20), (-8, 24)]:
            circ(doc, cx + dx, cy + dy, 1.7, fill=INFL)


def fibrosis(doc):
    x, y, w, h = RX, 532, RW, 174
    card(doc, x, y, w, h)
    step(doc, x + 6, y + 10, '5.4', PATH, 3.4)
    T(doc, x + 18, y + 10.4, 'From inflammation to fibrosis', size=5.0, weight=700, fill=NAVY)
    cx1, cx2, cy = x + 40, x + w - 40, y + 54
    alveoli(doc, cx1, cy, False)
    alveoli(doc, cx2, cy, True)
    arrow(doc, [(x + 76, cy), (x + 119, cy)], PATH, 'path', w=2.4, head=9, smooth=False)
    T(doc, cx1, y + 88, 'NORMAL', size=4.4, weight=700, fill='#4A6A7A', anchor='middle', spacing=0.8)
    T(doc, cx1, y + 94.5, 'thin septa, open air spaces', size=3.9, fill='#4A6A7A', anchor='middle')
    T(doc, cx2, y + 88, 'FIBROTIC', size=4.4, weight=700, fill='#7A5320', anchor='middle', spacing=0.8)
    T(doc, cx2, y + 94.5, 'thick, collagen-rich septa', size=3.9, fill='#7A5320', anchor='middle')
    # chain
    items = ['Chronic inflammation', 'TGF-β · PDGF activate fibroblasts', 'Myofibroblasts lay down **collagen**', 'Remodelled, stiff lung: **impaired gas exchange**']
    yy = y + 105
    for k, t in enumerate(items):
        rect(doc, x + 8, yy, w - 16, 11.2, fill='#FBF3E6' if k < 3 else '#F6E2C4', stroke='#E3C487', sw=0.5, r=2.4)
        P(doc, x + 12, yy + 7.7, t, w - 22, size=4.4, lh=1.0, boldfill='#6B3E05')
        if k < 3:
            path(doc, 'M%s,%s l2.2,2.6 l2.2,-2.6' % (x + w / 2 - 2.2, yy + 11.4), stroke=PATH, w=0.8)
        yy += 15.3


def draw(doc):
    title_block(doc)
    particles(doc)
    dysfunction(doc)
    inflammation(doc)
    fibrosis(doc)
