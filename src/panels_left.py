"""Left column: introduction, receptor recognition inset, engulfment signalling, molecule key."""
import math, random
from lib import *
from bio import *
from panels_common import *
from annot import step, DPHAG, DBIO
from cellmod2 import nox2

SLATE = '#3E5C86'
TEAL2 = '#1F8F8A'
BROWN = '#8F5A2A'


# ------------------------------------------------------------------------------------------ 1. introduction
def alveolus_mini(doc, cx, cy):
    r = 33
    g = doc.radgrad([(0, '#F3F8FB'), (1, '#DDEAF1')], cx=.5, cy=.5, r=.6)
    # capillary ring (outer) with red blood cells
    circ(doc, cx, cy, r + 8, fill='none', stroke='#E8A9A0', w=7.5)
    circ(doc, cx, cy, r + 8, fill='none', stroke='#F6D3CD', w=4.4)
    rnd = random.Random(3)
    for k in range(10):
        a = math.radians(k * 36 + 12)
        ell(doc, cx + (r + 8) * math.cos(a), cy + (r + 8) * math.sin(a), 2.4, 1.4, fill='#C0392B', rot=math.degrees(a) + 90, op=0.9)
    circ(doc, cx, cy, r, fill=g, stroke='#D6A79A', w=2.0)       # alveolar wall (type I pneumocytes)
    circ(doc, cx, cy, r, fill='none', stroke='#fff', w=0.6, dash='4 3')
    # alveolar macrophage on the wall
    mx, my = cx - 13, cy + 22
    path(doc, blob(mx, my, 12, 9.5, n=9, j=0.12, seed=4), fill='#F8DCCD', stroke='#B2594A', w=1.2)
    circ(doc, mx - 1, my - 1, 4.2, fill='#CFC7EA', stroke='#6A5FA6', w=0.5)
    # inhaled particles: bacterium and dust
    bacterium(doc, cx + 8, cy - 8, L=14, W=6, rot=25, lps=False, flagella=False, scale=1.0)
    silica(doc, cx + 20, cy + 8, s=0.7, rot=20)
    silica(doc, cx - 6, cy - 16, s=0.5, rot=-10)
    T(doc, cx, cy + 2, 'air', size=4.0, italic=True, fill='#6B8A99', anchor='middle')
    T(doc, cx - 22, cy + 50, 'capillary', size=3.6, fill='#B15B50', anchor='middle', italic=True)
    arrow(doc, [(mx + 12, my - 5), (cx + 8, cy + 8)], PHAG, 'modify', w=0.7)


def intro(doc):
    x, y, w, h = 25, 108, 260, 140
    card(doc, x, y, w, h)
    panel_title(doc, x + 4, y + 3, 1, 'The alveolar macrophage', speaker='AITOR · INTRODUCTION', w=w - 8)
    alveolus_mini(doc, 82, 190)
    tx = 136
    bul = [
        '**Professional phagocyte** of innate immunity, resident in tissues throughout the body.',
        '**Roles:** kills pathogens, clears dead cells and debris, releases cytokines, supports tissue repair.',
        '**Alveolar macrophages** patrol the air–blood barrier where gas exchange takes place.',
        'Cytokines and antigen display link them to the adaptive immune response.',
    ]
    yy = y + 31
    for b in bul:
        circ(doc, tx + 1.5, yy - 1.3, 1.1, fill=PHAG)
        hh = P(doc, tx + 6, yy, b, 138, size=5.0, fill=INK, lh=1.2, boldfill='#A24A3B')
        yy += hh + 3.6
    # siblings
    yy = y + h - 17
    T(doc, tx, yy - 2.8, 'TISSUE-SPECIFIC FAMILY', size=3.6, weight=700, fill='#8A93A3', spacing=0.7)
    cx = tx
    for txt, hl in (('Alveolar · lung', True), ('Kupffer · liver', False), ('Microglia · brain', False)):
        w_ = chip(doc, cx, yy, txt, '#A24A3B' if hl else '#EFE7D8', fg='#fff' if hl else '#5A5240', size=4.0, weight=700 if hl else 600)
        cx += w_ + 2.6


# ------------------------------------------------------------------------------------------ 2.1 recognition inset
IX, IY, IW, IH = 25, 256, 211, 188


def bilayer_h(doc, x0, x1, y, color='#B2594A'):
    path(doc, 'M%s,%s L%s,%s' % (x0, y, x1, y), stroke=color, w=5.0, cap='butt')
    path(doc, 'M%s,%s L%s,%s' % (x0, y, x1, y), stroke='#FBE3D8', w=1.9, cap='butt')
    for off in (-1.7, 1.7):
        path(doc, 'M%s,%s L%s,%s' % (x0, y + off, x1, y + off), stroke='#7A2E22', w=1.3, dash='0.01 2.1', cap='round')


def bracket(doc, x0, x1, y, text, color, size=4.0):
    path(doc, 'M%s,%s v2.2 H%s v-2.2' % (fmt(x0), fmt(y), fmt(x1)), stroke=color, w=0.7)
    T(doc, (x0 + x1) / 2, y + 7, text, size=size, weight=700, fill=color, anchor='middle')


def recognition(doc):
    card(doc, IX, IY, IW, IH)
    panel_title(doc, IX + 4, IY + 3, 2, 'Recognition', speaker='NEREA · 2.1', w=IW - 8, sub='opsonins bridge bacterium and receptor')
    top, mem = IY + 30, IY + 138
    path(doc, 'M%s,%s L%s,%s L%s,%s L%s,%s Z' % (IX + 5, top, IX + IW - 5, top, IX + IW - 5, top + 20, IX + 5, top + 20), fill='#B9C561', stroke='#556116', w=0.9)
    path(doc, 'M%s,%s L%s,%s' % (IX + 5, top + 16, IX + IW - 5, top + 16), stroke='#7C8A24', w=0.7)
    T(doc, IX + 10, top + 11, 'Gram-negative bacterium', size=4.4, weight=700, fill='#3F4A0E')
    for k in range(int((IW - 14) / 6.5)):
        x = IX + 9 + k * 6.5
        line(doc, x, top + 20, x, top + 24.5, '#5E6B1F', 0.6)
        circ(doc, x, top + 25.6, 0.9, fill='#7C8A24')
    bilayer_h(doc, IX + 5, IX + IW - 5, mem)
    rect(doc, IX + 5, mem + 3, IW - 10, 38, fill=CYTO)
    xs = [IX + 34, IX + 82, IX + 130, IX + 180]
    for dx in (-9, 9):
        antibody(doc, xs[0] + dx, top + 46, s=3.1, rot=0)
    receptor(doc, xs[0], mem - 3, h=51, color='#5A6B85', kind='fc')
    c3b(doc, xs[1], top + 47, s=3.4, rot=0)
    receptor(doc, xs[1], mem - 3, h=60, color=TEAL2, kind='cr')
    for dx in (-7, 7):
        circ(doc, xs[2] + dx, top + 32, 1.7, fill='#E0B84C', stroke='#8A6A12', w=0.3)
    receptor(doc, xs[2], mem - 3, h=70, color=BROWN, kind='lectin')
    circ(doc, xs[3], top + 44, 2.3, fill='#7C8A24')
    path(doc, 'M%s,%s L%s,%s' % (xs[3], top + 27, xs[3], top + 42), stroke='#7C8A24', w=0.9, dash='1 1.2')
    receptor(doc, xs[3], mem - 3, h=40, color=INFL, kind='tlr')
    for dx in (-3, 3):
        phos_dot(doc, xs[0] + dx, mem + 6.5, 1.5)
    labs = [('FcγR', 'binds IgG', '#4A5C78'), ('CR3 · CR1', 'binds C3b/iC3b', '#15706C'), ('MR · SR-A', 'bind microbe', '#6E4220'), ('TLR4', 'senses LPS', '#A3144F')]
    for x, (a, b, c) in zip(xs, labs):
        T(doc, x, mem + 13, a, size=5.0, weight=700, fill=c, anchor='middle')
        T(doc, x, mem + 19, b, size=3.8, fill=c, anchor='middle')
    by = mem + 25
    bracket(doc, xs[0] - 16, xs[1] + 22, by, 'opsonin-dependent uptake', SLATE, 4.1)
    bracket(doc, xs[2] - 18, xs[2] + 18, by, 'direct uptake', BROWN, 4.1)
    bracket(doc, xs[3] - 14, xs[3] + 20, by, 'signals only', INFL, 4.1)


# ------------------------------------------------------------------------------------------ 2.2 signalling
def signalling(doc):
    x, y, w, h = 25, 452, 225, 120
    card(doc, x, y, w, h)
    panel_title(doc, x + 4, y + 3, 2, 'Engulfment', speaker='NEREA · 2.2', w=w - 8, sub='receptor signalling builds the phagocytic cup')
    bw, bh = 64, 17
    cols = [x + 6, x + 80, x + 154]
    row1, row2 = y + 30, y + 58
    items = [
        ('FcγR clusters\nITAM-P', '#5A6B85'), ('Src kinases\n→ Syk', '#5A6B85'), ('PI3K → PIP₃\nat the cup', '#5A6B85'),
        ('Rac · Cdc42\nGTPases', '#B8531A'), ('WASP + Arp2/3\ncomplex', '#B8531A'), ('Branched actin\n→ pseudopods', '#B8531A'),
    ]
    for k, (t, c) in enumerate(items):
        bx = cols[k % 3]
        by = row1 if k < 3 else row2
        rect(doc, bx, by, bw, bh, fill='#FBF3EE' if k >= 3 else '#EEF2F8', stroke=c, sw=0.7, r=3)
        l1, l2 = t.split('\n')
        T(doc, bx + bw / 2, by + 7.4, l1, size=4.4, weight=700, fill=c, anchor='middle')
        T(doc, bx + bw / 2, by + 13.8, l2, size=4.1, fill=INK2, anchor='middle')
    for r_ in (row1, row2):
        for c0 in (0, 1):
            arrow(doc, [(cols[c0] + bw + 1, r_ + bh / 2), (cols[c0 + 1] - 1, r_ + bh / 2)], INK, 'modify', w=0.7, head=4)
    arrow(doc, [(cols[2] + bw / 2, row1 + bh + 1), (cols[2] + bw / 2, row1 + bh + 5), (cols[0] + bw / 2, row1 + bh + 5), (cols[0] + bw / 2, row2 - 1)], INK, 'modify', w=0.7, head=4)
    P(doc, x + 6, y + 91, 'Zipper: receptors engage the particle step by step; pseudopods rise around it and the cup seals into a **phagosome**.', w - 12, size=4.5, lh=1.2, fill=INK2, boldfill=DPHAG)


# ------------------------------------------------------------------------------------------ molecule key
def key(doc):
    x, y, w, h = 25, 580, 262, 126
    card(doc, x, y, w, h)
    T(doc, x + 8, y + 10, 'MOLECULE KEY', size=4.6, weight=700, fill=NAVY, spacing=1.0)
    col = [x + 10, x + 136]
    rows = [y + 27 + k * 16 for k in range(6)]
    def lab(cx, cy, t):
        T(doc, cx + 19, cy + 1.5, t, size=4.4, fill=INK)
    items = [
        (lambda c, r: hydrolase(doc, c + 5, r, s=1.0), 'Acid hydrolase + N-glycan'),
        (lambda c, r: hydrolase(doc, c + 5, r, s=1.0, p=True), 'M6P tag on the glycan'),
        (lambda c, r: m6pr(doc, c + 5, r + 5, s=1.1), 'M6P receptor (MPR)'),
        (lambda c, r: vatpase(doc, c + 5, r + 3, 0, s=1.0) if False else (path(doc, 'M%s,%s h10' % (c, r + 5), stroke='#C23B2A', w=0.5, op=0), vatpase(doc, c + 5, r + 4, -90, s=0.95)), 'V-ATPase proton pump'),
        (lambda c, r: (hplus(doc, c + 4, r, 1.4), hplus(doc, c + 9, r + 2, 1.4)), 'H⁺ (acidification)'),
        (lambda c, r: clathrin(doc, c + 6, r, 4.6), 'Clathrin coat'),
        (lambda c, r: copii(doc, c + 6, r, 4.6), 'COPII coat'),
        (lambda c, r: tag(doc, c + 7, r + 1.5, 'Rab-GTP', '#C23B2A', 3.3), 'active Rab GTPase'),
        (lambda c, r: (circ(doc, c + 6, r, 4.6, fill='#F9D5CA', stroke='#C23B2A', w=0.9), circ(doc, c + 6, r, 2.7, fill='none', stroke='#8A5A4A', w=0.7, dash='0.2 1.0')), 'LAMP1/2 inner lining'),
        (lambda c, r: nox2(doc, c + 6, r + 2, -90, s=0.9), 'NADPH oxidase (NOX2)'),
        (lambda c, r: (ros(doc, c + 3, r, s=1.2), ros(doc, c + 9, r + 1, s=1.0)), 'ROS (O₂•⁻, H₂O₂)'),
        (lambda c, r: (antibody(doc, c + 3, r + 1, s=1.2), c3b(doc, c + 11, r, s=1.2)), 'IgG · C3b opsonins'),
    ]
    from cellmod import tag
    for k, (fn, t) in enumerate(items):
        c = col[k // 6]
        r = rows[k % 6]
        fn(c, r)
        lab(c, r, t)
