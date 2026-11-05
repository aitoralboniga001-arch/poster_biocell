"""v2 composition: open title, connected callouts around the macrophage, pathology narrative, integrated conclusion.
Units: mm on the 1100 x 900 sheet."""
import math, random
from lib import *
from bio import *
from cellmod import on_circle
from cellmod2 import nox2, SPL, PL, LP, L2
from annot2 import tag, DPHAG, DBIO, DLY, DLE, DPATH, DINFL, DREC
from style import shade, sheen, contact_shadow, spec, tone, lighten, darken, mix

NAVY = '#1F2C3B'
RULE = '#D9CDB6'
SPK = '#8A8170'
S_BODY = 6.2      # body text  (~18 pt)
S_SMALL = 5.6     # secondary labels (~16 pt)
S_HEAD = 10.6     # section headings (~30 pt)
SEC = {1: NAVY, 2: PHAG, 3: BIO, 4: CONV, 5: PATH, 6: RECY}
SLATE, TEAL2, BROWN = '#3E5C86', '#1F8F8A', '#8F5A2A'


def heading(doc, x, y, num, title, speaker=None, right=None, sub=None, label=None):
    c = SEC[num]
    lab = label or str(num)
    circ(doc, x + 7.2, y - 3.7, 7.2, fill=c)
    circ(doc, x + 7.2, y - 3.7, 6.2, fill='none', stroke='#fff', w=0.3, op=0.55)
    fs = 9.6 if len(lab) == 1 else 6.4
    T(doc, x + 7.2, y - 3.7 + fs * 0.34, lab, size=fs, weight=600, fill='#fff', anchor='middle', family=SERIF)
    T(doc, x + 18.5, y, title, size=S_HEAD, weight=600, fill=NAVY, family=SERIF, halo=PAPER, spacing=-0.08)
    if speaker:
        tw = text_width(title, S_HEAD, 600, 'serif') - 0.08 * len(title)
        T(doc, x + 18.5 + tw + 4.5, y - 0.4, speaker, size=4.6, weight=600, fill=c, spacing=1.1, halo=PAPER, opacity=0.85)
    if sub:
        T(doc, x + 18.5, y + 8.6, sub, size=S_SMALL, fill='#5C6672', italic=True)


def bullet_list(doc, x, y, items, width, size=S_BODY, color=PHAG, boldfill=None, gap=2.2):
    for b in items:
        circ(doc, x + 1.6, y - size * 0.32, 1.3, fill=color)
        h = PS(doc, x + 6, y, b, width - 6, size=size, lh=1.2, boldfill=boldfill)
        y += h + gap
    return y


# ===================================================================================== header
def header(doc):
    T(doc, 30, 24, 'CELL BIOLOGY SEMINAR  ·  FIRST-YEAR MEDICINE', size=4.8, weight=600, fill='#A24A3B', spacing=1.5)
    fam = resolve(SERIF, 31, 600)[0]
    doc.add('<text x="28" y="58" font-family="%s" font-size="31" font-weight="600" fill="%s" letter-spacing="-0.35">'
            'How a macrophage <tspan font-style="italic" fill="%s">destroys</tspan> what it engulfs</text>' % (fam, NAVY, '#C23A22'))
    T(doc, 30, 75.5, 'Phagocytosis, lysosomal biogenesis and vesicular trafficking, and what happens when particles cannot be cleared',
      size=8.0, fill='#4A5563', family=SERIF)
    T(doc, 1072, 30, 'Aitor · Nerea · Urtzi · Eneritz · Nora', size=7.6, weight=600, fill=NAVY, anchor='end', family=SERIF)
    T(doc, 1072, 40, 'First-year Medicine · Cell Biology', size=5.6, fill='#4A5563', anchor='end')
    T(doc, 1072, 49, '[Faculty · University · Academic year: to complete]', size=5.4, fill='#B4690E', anchor='end', italic=True)
    line(doc, 28, 89, 1072, 89, RULE, 0.35)


# ===================================================================================== 1 introduction
def alveolar_wall(doc, x, y, w, h):
    """Cross-section: air space above, thin epithelium + capillary below; macrophage resting on the luminal surface."""
    ep = y + h * 0.66
    g = doc.lingrad([(0, '#F4F8FA'), (1, '#E2EEF4')], 0, 0, 0, 1)
    rect(doc, x, y, w, ep - y, fill=g, r=4)
    # interstitium + capillary
    rect(doc, x, ep, w, y + h - ep, fill='#F6E6DE', r=0)
    path(doc, 'M%s,%s H%s' % (x, y + h, x + w), stroke='#E9D2C6', w=0.6)
    cap_y = ep + 9
    path(doc, 'M%s,%s H%s' % (x + 2, cap_y, x + w - 2), stroke='#F2C4BB', w=11, cap='round')
    path(doc, 'M%s,%s H%s' % (x + 2, cap_y, x + w - 2), stroke='#FBE3DD', w=8.6, cap='round')
    for k in range(9):
        ell(doc, x + 12 + k * (w - 24) / 8, cap_y + (0.6 if k % 2 else -0.6), 3.0, 1.9, fill='#C0392B', op=0.9)
    # epithelium: flat type I cells + one cuboidal type II cell
    path(doc, 'M%s,%s H%s' % (x, ep, x + w), stroke='#C98B7E', w=2.2, cap='butt')
    for k in range(4):
        ell(doc, x + 22 + k * 58, ep - 0.2, 5, 1.2, fill='#9A6A8C')
    tx = x + 72
    rect(doc, tx, ep - 11, 15, 12, fill='#F1D3C6', stroke='#C98B7E', sw=0.9, r=2.5)
    circ(doc, tx + 7.5, ep - 4.5, 2.6, fill='#9A6A8C')
    for (dx, dy) in [(3, -8.5), (11, -8), (7, -9.5)]:
        circ(doc, x + 72 + dx, ep + dy, 1.0, fill='#E8B04C')
    # macrophage on the luminal surface (bathed in lining fluid)
    rect(doc, x, ep - 3.2, w, 3.2, fill='#D7E8F0', op=0.8)
    mx, my = x + w - 62, ep - 11
    path(doc, blob(mx, my, 20, 10.5, n=11, j=0.12, seed=4), fill='#F8DCCD', stroke='#B2594A', w=1.4)
    circ(doc, mx - 4, my - 0.5, 5, fill='#CFC7EA', stroke='#6A5FA6', w=0.6)
    path(doc, 'M%s,%s q8,-9 18,-6' % (fmt(mx + 14), fmt(my - 5)), stroke='#B2594A', w=2.4, cap='round')
    # inhaled particles in the air
    bacterium(doc, x + 52, y + 22, L=16, W=6.6, rot=25, lps=False, flagella=False, scale=1.0)
    silica(doc, x + 108, y + 18, s=0.75, rot=20)
    asbestos_fibre(doc, x + 140, y + 30, x + 172, y + 22, w=1.8, color='#C9A66B', frays=False)
    silica(doc, x + 24, y + 38, s=0.5, rot=-10)
    # labels
    T(doc, x + 5, y + 9, 'Air space (alveolar lumen)', size=S_SMALL, italic=True, fill='#4E6E7E')
    T(doc, mx, my - 16, 'Alveolar macrophage', size=S_SMALL, weight=700, fill='#A24A3B', anchor='middle')
    T(doc, x + 5, ep + 21, 'Capillary', size=S_SMALL, italic=True, fill='#A0463A')
    T(doc, x + 79.5, ep - 14, 'Type II', size=5.4, fill='#7A4E6E', anchor='middle')
    T(doc, x + 30, ep - 4.5, 'Type I', size=5.4, fill='#7A4E6E', anchor='middle')
    return mx, my


def intro(doc):
    x, w = 25, 237
    heading(doc, x, 112, 1, 'Alveolar macrophages', 'AITOR', x + w)
    y = bullet_list(doc, x, 126, [
        '**Tissue-resident phagocytes** of the innate immune system',
        'Lie **in the alveolar lumen**, on the epithelial surface, bathed in surfactant-rich lining fluid',
        'Clear **microbes, dust and dead cells**; release cytokines that alert other immune cells',
    ], w, boldfill='#8E2F1F')
    mx, my = alveolar_wall(doc, x, 176, w, 94)
    # zoom: this macrophage is the cell magnified in the centre
    for (tx, ty) in [(322, 222), (318, 246)]:
        line(doc, mx + 8, my - 6, tx, ty, '#B2594A', 0.45, dash='2 1.6')
    T(doc, 268, 226, 'magnified', size=5.4, italic=True, fill='#A24A3B', anchor='middle', rot=-14)


# ===================================================================================== 2 recognition & engulfment
IX, IY, IW, IH = 25, 302, 237, 200


def bilayer_h(doc, x0, x1, y, color='#B2594A'):
    """Horizontal lipid bilayer: soft cast shadow, darker-toned leaflets with head-group beads, pale lit core."""
    path(doc, 'M%s,%s L%s,%s' % (x0, y + 1.1, x1, y + 1.1), stroke='#5B3426', w=5.6, cap='butt', op=0.10)
    path(doc, 'M%s,%s L%s,%s' % (x0, y, x1, y), stroke=tone(color, 0.18), w=5.2, cap='butt')
    path(doc, 'M%s,%s L%s,%s' % (x0, y, x1, y), stroke=color, w=4.4, cap='butt')
    path(doc, 'M%s,%s L%s,%s' % (x0, y, x1, y), stroke='#FCEBE2', w=1.7, cap='butt')
    for off, op in ((-1.7, 0.9), (1.7, 1)):
        path(doc, 'M%s,%s L%s,%s' % (x0, y + off, x1, y + off), stroke=tone(color, 0.42), w=1.25, dash='0.01 2.1', cap='round', op=op)
    path(doc, 'M%s,%s L%s,%s' % (x0, y - 2.45, x1, y - 2.45), stroke='#FFFFFF', w=0.3, cap='butt', op=0.55)


def bracket(doc, x0, x1, y, text, color, size=5.4):
    path(doc, 'M%s,%s v2.4 H%s v-2.4' % (fmt(x0), fmt(y), fmt(x1)), stroke=color, w=0.8)
    T(doc, (x0 + x1) / 2, y + 8, text, size=size, weight=700, fill=color, anchor='middle')


def recognition(doc):
    heading(doc, IX, 292, 2, 'Recognition and engulfment', 'NEREA', IX + IW)
    x, y, w, h = IX, IY, IW, IH
    rect(doc, x, y, w, h, fill='#FBEEE7', r=6)
    rect(doc, x, y, w, h, fill='none', stroke=PHAG, sw=0.7, r=6, dash='3 1.6')
    tag(doc, x + 5, y + 9, '2.1', PHAG)
    T(doc, x + 21, y + 9, 'magnified contact site', size=5.4, italic=True, fill='#8E2F1F')
    top, mem = y + 15, y + 138
    rect(doc, x + 6, top, w - 12, 20, fill='#B9C561', stroke='#556116', sw=0.9)
    line(doc, x + 6, top + 16, x + w - 6, top + 16, '#7C8A24', 0.7)
    T(doc, x + 11, top + 11.5, 'Bacterium', size=6.0, weight=700, fill='#3F4A0E')
    for k in range(int((w - 16) / 6.5)):
        xx = x + 10 + k * 6.5
        line(doc, xx, top + 20, xx, top + 24.5, '#5E6B1F', 0.6)
        circ(doc, xx, top + 25.6, 0.9, fill='#7C8A24')
    bilayer_h(doc, x + 6, x + w - 6, mem)
    rect(doc, x + 6, mem + 3, w - 12, h - (mem - y) - 9, fill=CYTO)
    xs = [x + 32, x + 89, x + 146, x + 206]
    for dx in (-9, 9):
        antibody(doc, xs[0] + dx, top + 50, s=3.1, rot=0)
    receptor(doc, xs[0], mem - 3, h=50, color='#5A6B85', kind='fc')
    c3b(doc, xs[1], top + 50, s=3.4, rot=0)
    receptor(doc, xs[1], mem - 3, h=60, color=TEAL2, kind='cr')
    for dx in (-7, 7):
        circ(doc, xs[2] + dx, top + 32, 1.9, fill='#E0B84C', stroke='#8A6A12', w=0.3)
    receptor(doc, xs[2], mem - 3, h=74, color=BROWN, kind='lectin')
    circ(doc, xs[3], top + 52, 2.4, fill='#7C8A24')
    path(doc, 'M%s,%s L%s,%s' % (xs[3], top + 27, xs[3], top + 50), stroke='#7C8A24', w=0.9, dash='1 1.2')
    receptor(doc, xs[3], mem - 3, h=44, color=INFL, kind='tlr')
    for dx in (-3, 3):
        phos_dot(doc, xs[0] + dx, mem + 7, 1.6)
    # ligand labels above the membrane
    for xx, t, c in ((xs[0] + 20, 'IgG', SLATE), (xs[1] + 16, 'iC3b', '#15706C'), (xs[2] + 8, 'sugars', '#6E4220'), (xs[3] + 6, 'LPS', '#556116')):
        T(doc, xx, top + 56, t, size=5.4, weight=700, fill=c, halo='#FBEEE7')
    labs = [('FcγR', SLATE), ('CR3', '#15706C'), ('MR · SR-A', '#6E4220'), ('TLR4', '#A3144F')]
    for xx, (a, c) in zip(xs, labs):
        T(doc, xx, mem + 15, a, size=6.4, weight=700, fill=c, anchor='middle')
    by = mem + 20
    bracket(doc, xs[0] - 18, xs[1] + 18, by, 'uptake (opsonin-dependent)', SLATE)
    bracket(doc, xs[2] - 22, xs[2] + 22, by, 'direct uptake', BROWN)
    bracket(doc, xs[3] - 18, xs[3] + 22, by, 'signalling only', '#A3144F')
    P(doc, x + 8, mem + 40, 'CR1 binds C3b/C4b; CR3 binds the cleaved fragment iC3b.', w - 16, size=5.6, fill='#4A5563', italic=True)
    # ---------------- engulfment
    ey = y + h + 15
    tag(doc, x, ey, '2.2', PHAG)
    T(doc, x + 15, ey, 'Engulfment: a receptor “zipper”', size=6.8, weight=700, fill=DPHAG)
    cx = x
    cy = ey + 7
    chain = ['FcγR cluster', 'Syk', 'PI3K', 'Rac · Cdc42', 'Arp2/3']
    for k, t in enumerate(chain):
        cw = text_width(t, 5.6, 700) + 6
        rect(doc, cx, cy, cw, 9.4, fill='#FFFFFF' if k < 3 else '#FBE3D8', stroke='#5A6B85' if k < 3 else '#C2571A', sw=0.7, r=2.6)
        T(doc, cx + cw / 2, cy + 6.6, t, size=5.6, weight=700, fill='#3E4C61' if k < 3 else '#9A3B12', anchor='middle')
        cx += cw
        if k < len(chain) - 1:
            arrow(doc, [(cx + 0.8, cy + 4.7), (cx + 6.2, cy + 4.7)], '#4A5563', 'transport', w=0.8, head=3.0, smooth=False)
            cx += 7
    P(doc, x, cy + 18, 'Branched F-actin pushes **pseudopods** over the particle until the membrane seals into a **phagosome**.', w,
      size=S_BODY, lh=1.18, boldfill=DPHAG)
    zipper_steps(doc, x, cy + 34)


def _membrane(doc, pts, closed=False):
    d = cr_path(pts, closed)
    path(doc, d, stroke='#B2594A', w=3.2)
    path(doc, d, stroke='#FBE3D8', w=1.1)


def zipper_steps(doc, x, y):
    """Three-frame engulfment: contact -> pseudopods zip round -> sealed phagosome."""
    pw, base = 70, y + 38
    caps = ['contact', 'pseudopods zip up', 'sealed phagosome']
    for k in range(3):
        x0 = x + k * 83.5
        cx = x0 + pw / 2
        rect(doc, x0, y, pw, 54, fill='#F4F8FA', r=3)
        if k == 0:
            rect(doc, x0, base, pw, 54 - (base - y), fill=CYTO)
            _membrane(doc, [(x0, base), (x0 + pw, base)])
            bacterium(doc, cx, base - 9, L=26, W=10, rot=0, lps=False, flagella=False, scale=1.0)
            for dx in (-8, 0, 8):
                line(doc, cx + dx, base - 1, cx + dx, base - 3.6, '#5A6B85', 1.0)
        elif k == 1:
            pts = [(x0, base), (cx - 20, base), (cx - 18, base - 14), (cx - 14.5, base - 22), (cx - 12, base - 13), (cx - 7, base - 4),
                   (cx, base - 2.5), (cx + 7, base - 4), (cx + 12, base - 13), (cx + 14.5, base - 22), (cx + 18, base - 14), (cx + 20, base), (x0 + pw, base)]
            dense = cr_sample(pts, closed=False, per=10)
            path(doc, poly_d(dense + [(x0 + pw, y + 54), (x0, y + 54)], True), fill=CYTO)
            _membrane(doc, pts)
            bacterium(doc, cx, base - 10.5, L=24, W=9.6, rot=0, lps=False, flagella=False, scale=1.0)
            for sx in (-1, 1):
                for j in range(5):
                    line(doc, cx + sx * (16.5 - j * 0.3), base - 4 - j * 3.4, cx + sx * (14.5 - j * 0.2), base - 6 - j * 3.4, '#C2571A', 0.6)
        else:
            top_ = y + 16
            rect(doc, x0, top_, pw, 54 - (top_ - y), fill=CYTO)
            _membrane(doc, [(x0, top_), (x0 + pw, top_)])
            circ(doc, cx, base - 2, 13, fill='#FFE1D8', stroke=PHAG, w=1.0)
            bacterium(doc, cx, base - 2, L=20, W=8, rot=-10, lps=False, flagella=False, scale=1.0)
        T(doc, cx, y + 60, caps[k], size=5.6, weight=700, fill=DPHAG, anchor='middle')
        if k < 2:
            arrow(doc, [(x0 + pw + 2, y + 27), (x0 + pw + 11.5, y + 27)], PHAG, 'transport', w=1.2, head=4.4, smooth=False)


def contact_site(doc):
    """Receptors and opsonins on the plasma membrane at bacterium A; magnifier ring linked to the 2.1 inset."""
    for (y, kind, col) in [(284, 'fc', '#5A6B85'), (297, 'cr', '#1F8F8A'), (310, 'lectin', '#8F5A2A'), (322, 'tlr', '#C81D63')]:
        receptor(doc, 307, y, h=10, rot=-90, color=col, kind=kind, tail=True)
    for y in (291, 303):
        antibody(doc, 299, y, s=0.9, rot=-90)
    c3b(doc, 297, 316, s=1.0, rot=-90)
    cx, cy, r = 301, 302, 26
    g = doc.lingrad([(0, '#D95C3F', 0.03), (1, '#D95C3F', 0.16)], 0, 0, 1, 0)
    path(doc, 'M%s,%s L%s,%s L%s,%s L%s,%s Z' % (fmt(cx), fmt(cy - r), IX + IW, IY + 2, IX + IW, IY + IH - 2, fmt(cx), fmt(cy + r)), fill=g)
    circ(doc, cx, cy, r, fill='none', stroke=PHAG, w=1.4, dash='3 1.6')
    line(doc, cx - 6, cy - r + 0.7, IX + IW, IY + 2, PHAG, 0.5, dash='2 1.4')
    line(doc, cx - 6, cy + r - 0.7, IX + IW, IY + IH - 2, PHAG, 0.5, dash='2 1.4')
    tag(doc, cx - 8, cy - r - 4, '2.1', PHAG)


# ===================================================================================== 5 pathology (right column)
RX, RW = 884, 191


def septum(doc, x, y, w, h, fibrotic):
    """Alveolar septum between two air spaces (cross-section)."""
    g = doc.lingrad([(0, '#EAF3F8'), (1, '#F4F8FA')], 0, 0, 0, 1)
    rect(doc, x, y, w, h, fill=g, r=3)
    th = h * (0.18 if not fibrotic else 0.58)
    sy = y + (h - th) / 2
    rect(doc, x, sy, w, th, fill='#F6E2D8' if not fibrotic else '#EBCFA8')
    for yy in (sy, sy + th):
        path(doc, 'M%s,%s H%s' % (x, yy, x + w), stroke='#C98B7E', w=1.6, cap='butt')
    if not fibrotic:
        capy = sy + th / 2
        path(doc, 'M%s,%s H%s' % (x + 3, capy, x + w - 3), stroke='#F2C4BB', w=th * 0.62, cap='round')
        for k in range(5):
            ell(doc, x + 10 + k * (w - 20) / 4, capy, 2.4, 1.4, fill='#C0392B', op=0.9)
        for k in range(3):
            ell(doc, x + 12 + k * 30, sy - 0.1, 4, 0.9, fill='#9A6A8C')
            ell(doc, x + 26 + k * 30, sy + th + 0.1, 4, 0.9, fill='#9A6A8C')
    else:
        rnd = random.Random(7)
        for k in range(15):     # collagen bundles
            yy = sy + 3 + rnd.uniform(0, th - 6)
            x0 = x + rnd.uniform(-6, w * 0.55)
            L = rnd.uniform(w * 0.35, w * 0.6)
            amp = rnd.uniform(0.8, 1.8)
            pts = [(x0 + L * t / 8, yy + amp * math.sin(t * 1.4 + k)) for t in range(9)]
            pts = [(max(x + 1, min(x + w - 1, px)), py) for px, py in pts]
            path(doc, poly_d(pts), stroke='#A86E2C', w=0.9, op=0.85)
        for (dx, dy, rot) in [(0.25, 0.35, 12), (0.62, 0.62, -10), (0.4, 0.75, 6), (0.8, 0.3, -18)]:
            ell(doc, x + w * dx, sy + th * dy, 7, 1.7, fill='#8E5FB0', stroke='#5B3A78', w=0.4, rot=rot)
        path(doc, 'M%s,%s H%s' % (x + w * 0.15, sy + th * 0.52, x + w * 0.35), stroke='#F2C4BB', w=3.2, cap='round')   # squeezed capillary
        ell(doc, x + w * 0.25, sy + th * 0.52, 1.6, 1.0, fill='#C0392B')
        for k in range(4):      # hyperplastic type II cells
            rect(doc, x + 6 + k * 24, sy - 5, 8, 5, fill='#F1D3C6', stroke='#C98B7E', sw=0.6, r=1.4)
        for (dx, dy) in [(0.1, 0.2), (0.9, 0.8)]:
            circ(doc, x + w * dx, sy + th * dy, 1.5, fill=INFL)


def neutrophil(doc, x, y, r=6):
    """Shaded neutrophil with a multilobed nucleus (lobes joined by fine chromatin bridges)."""
    contact_shadow(doc, x, y, r, strength=0.14)
    circ(doc, x, y, r, fill=shade(doc, '#D9E3F5', light=0.6, dark=0.08), stroke=tone('#5B6B93', 0.05), w=0.5)
    k = r / 6.0
    lobes = [(-2.5, -1.2), (0.2, 1.5), (2.7, -0.8)]
    path(doc, cr_path([(x + dx * k, y + dy * k) for dx, dy in lobes], False), stroke='#4E5D85', w=0.55 * k)
    for (dx, dy) in lobes:
        ell(doc, x + dx * k, y + dy * k, 1.65 * k, 1.35 * k, fill=shade(doc, '#6B7AA3', light=0.35, dark=0.15), rot=dx * 12)
    spec(doc, x, y, r, a0=200, a1=245, op=0.75, inset=0.78, w=max(0.35, r * 0.08))


def monocyte(doc, x, y, r=6.4):
    """Shaded monocyte with a kidney-shaped nucleus."""
    contact_shadow(doc, x, y, r, strength=0.14)
    circ(doc, x, y, r, fill=shade(doc, '#E3D7F1', light=0.6, dark=0.08), stroke=tone('#6A5FA6', 0.05), w=0.5)
    k = r / 6.4
    path(doc, blob(x - 0.6 * k, y + 0.2 * k, 3.4 * k, 2.5 * k, n=7, j=0.25, seed=3), fill=shade(doc, '#7468AE', light=0.35, dark=0.15))
    ell(doc, x + 2.2 * k, y + 0.3 * k, 1.1 * k, 0.9 * k, fill=shade(doc, '#E3D7F1', light=0.4))   # nuclear notch
    spec(doc, x, y, r, a0=200, a1=245, op=0.75, inset=0.78, w=max(0.35, r * 0.08))


def pathology(doc):
    x, w = RX, RW
    heading(doc, x, 112, 5, 'When particles persist', 'NORA', x + w, sub='occupational silicosis and asbestosis')
    # ---- exposure
    for (dx, dy, s, rt) in [(14, 150, 1.5, 10), (34, 144, 1.9, -20), (48, 158, 1.1, 40), (26, 166, 0.9, 5)]:
        silica(doc, x + dx, dy, s=s, rot=rt)
    asbestos_fibre(doc, x + 108, 156, x + 186, 140, w=3.4, color='#D6B676')
    asbestos_fibre(doc, x + 112, 166, x + 184, 156, w=2.6, color='#CDA95F')
    T(doc, x + 32, 184, 'Crystalline silica', size=S_BODY, weight=700, fill='#3E4C61', anchor='middle')
    T(doc, x + 32, 191.5, 'quarrying, stone cutting', size=5.6, fill='#3E4C61', anchor='middle')
    T(doc, x + 146, 184, 'Asbestos fibres', size=S_BODY, weight=700, fill='#6B4A12', anchor='middle')
    T(doc, x + 146, 191.5, 'insulation, construction', size=5.6, fill='#6B4A12', anchor='middle')
    P(doc, x, 205, 'Inhaled particles reach the alveoli, where macrophages take them up, but cannot digest them.', w, size=S_BODY, lh=1.18, fill=INK2)
    # ---- 5.2 asbestos (the fibre itself crosses from the cell into this column at y ~350)
    y = 248
    tag(doc, x, y, '5.2', PATH)
    T(doc, x + 15, y, 'Long fibres: frustrated phagocytosis', size=6.6, weight=700, fill=DPATH)
    P(doc, x, y + 9, 'Pseudopods spread along a fibre too long to enclose, but the cup never closes: ROS and lysosomal enzymes leak out. Short fibres can be engulfed yet still persist.',
      w, size=S_BODY, lh=1.18)
    # ---- 5.3 silica
    y = 394
    tag(doc, x, y, '5.3', PATH)
    T(doc, x + 15, y, 'Silica: lysosomal injury', size=6.6, weight=700, fill=DPATH)
    hh = P(doc, x, y + 9, 'Crystals can rupture the phagolysosome membrane. Leaked cathepsins, K⁺ efflux and ROS can activate the **NLRP3 inflammasome** → caspase-1 → IL-1β. Cells that die release the crystal, which is engulfed again.',
           w, size=S_BODY, lh=1.18, boldfill=DINFL)
    leader(doc, [(SPL[0] + SPL[2] + 1.5, SPL[1] - 6), (x - 4, y + 12)], color=DPATH, w=0.5)
    # ---- 5.4 inflammation
    y = 482
    tag(doc, x, y, '5.4', INFL)
    T(doc, x + 15, y, 'Persistent inflammation', size=6.6, weight=700, fill=DINFL)
    dy = y + 26
    path(doc, blob(x + 18, dy, 15, 12, n=9, j=0.1, seed=6), fill='#F8DCCD', stroke='#B2594A', w=1.3)
    circ(doc, x + 16, dy - 1, 4.6, fill='#CFC7EA', stroke='#6A5FA6', w=0.5)
    silica(doc, x + 23, dy + 4, s=0.55, rot=10)
    for (ddx, ddy) in [(40, -11), (47, -1), (40, 9), (55, -7)]:
        cytokine(doc, x + ddx, dy + ddy, s=1.1, rot=ddx * 3)
    arrow(doc, [(x + 62, dy - 4), (x + 82, dy - 9)], INFL, 'signal', w=1.2, head=5, smooth=False)
    neutrophil(doc, x + 95, dy - 12)
    monocyte(doc, x + 110, dy - 4)
    neutrophil(doc, x + 124, dy - 13)
    for (ddx, ddy) in [(136, 2), (142, -6), (146, 6)]:
        ros(doc, x + ddx, dy + ddy, s=1.0)
    arrow(doc, [(x + 131, dy + 4), (x + 152, dy + 9)], PATH, 'path', w=1.4, head=6.5, smooth=False)
    # damaged epithelium
    for k in range(3):
        rect(doc, x + 156 + k * 11.5, dy + 5, 10.5, 8, fill='#F1D3C6', stroke='#C98B7E', sw=0.6, r=1.4)
    path(doc, 'M%s,%s l3,-3 l2,4 l3,-3' % (fmt(x + 167), fmt(dy + 4)), stroke=INFL, w=0.8)
    T(doc, x + 104, dy + 14, 'recruited cells', size=5.4, italic=True, fill='#5B6B93', anchor='middle')
    T(doc, x + 173, dy + 21, 'epithelium', size=5.4, italic=True, fill='#8E5A4E', anchor='middle')
    yy = dy + 30
    yy += P(doc, x, yy, '**Signalling:** IL-1β, TNF-α and chemokines recruit neutrophils and monocytes.', w, size=S_BODY, lh=1.18, boldfill=DINFL) + 1.6
    P(doc, x, yy, '**Injury:** their ROS and proteases damage the epithelium; the particle stays, so the stimulus persists.', w, size=S_BODY, lh=1.18, boldfill=DPATH)
    # ---- 5.5 fibrosis
    y = 598
    tag(doc, x, y, '5.5', PATH)
    T(doc, x + 15, y, 'Fibrotic remodelling', size=6.6, weight=700, fill=DPATH)
    sw_ = 84
    septum(doc, x, y + 6, sw_, 62, False)
    septum(doc, x + w - sw_, y + 6, sw_, 62, True)
    arrow(doc, [(x + sw_ + 3, y + 37), (x + w - sw_ - 3, y + 37)], PATH, 'path', w=1.8, head=7, smooth=False)
    T(doc, x + sw_ / 2, y + 76, 'Normal septum', size=5.6, weight=700, fill='#4A6A7A', anchor='middle')
    T(doc, x + w - sw_ / 2, y + 76, 'Fibrotic septum', size=5.6, weight=700, fill='#7A5320', anchor='middle')
    P(doc, x, y + 86, '**TGF-β** and **PDGF** turn fibroblasts into **myofibroblasts**, which deposit collagen: thick, stiff septa impair gas exchange.',
      w, size=S_BODY, lh=1.18, boldfill='#7A5320')


# ===================================================================================== bottom band
BY = 742


def helix(doc, x0, y0, x1, y1, color, amp=1.3, turns=3.0, w=1.1, phase=0.0):
    n = 28
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts = []
    for i in range(n + 1):
        t = i / n
        s = amp * math.sin(2 * math.pi * turns * t + phase)
        pts.append((x0 + ux * L * t + nx * s, y0 + uy * L * t + ny * s))
    d = poly_d(pts)
    path(doc, d, stroke=tone(color, 0.35), w=w + 0.45, cap='round')
    path(doc, d, stroke=color, w=w, cap='round')
    hl = [(px - w * 0.08, py - w * 0.2) for px, py in pts]
    path(doc, poly_d(hl), stroke=lighten(color, 0.55), w=w * 0.3, cap='round', op=0.8)


def mem_draw(doc, pts, color):
    """Curved bilayer: soft shadow, toned leaflets with head-group beads in a darker tone of the membrane hue."""
    d = cr_path(pts, False)
    doc.add('<g transform="translate(0.6 0.9)">')
    path(doc, d, stroke='#5B3426', w=4.8, cap='butt', op=0.10)
    doc.add('</g>')
    path(doc, d, stroke=tone(color, 0.2), w=4.4, cap='butt')
    path(doc, d, stroke=color, w=3.7, cap='butt')
    path(doc, d, stroke=lighten(color, 0.88), w=1.4, cap='butt')
    dense = cr_sample(pts, closed=False, per=10)
    for off in (-1.5, 1.5):
        path(doc, poly_d(offset_poly(dense, off, closed=False)), stroke=tone(color, 0.45), w=1.05, dash='0.01 1.9', cap='round')


def lumen_fill(doc, pts, x_edge, y0, y1, color):
    dense = cr_sample(pts, closed=False, per=10)
    fill = shade(doc, color, light=0.55, dark=0.05, cx=0.4, cy=0.3, r=0.85) if color.startswith('#') else color
    path(doc, poly_d([(x_edge, y0)] + dense + [(x_edge, y1)], True), fill=fill)


RABC, HOPSC = '#C23B2A', '#6E3FB0'
QA, QB, QC, RS = '#2F6FDB', '#5AA3F0', '#1A4FAE', '#E08A00'


def rab_pin(doc, x, y, side=1, r=2.6):
    path(doc, 'M%s,%s q%s,%s %s,%s' % (fmt(x), fmt(y), fmt(side * -1.5), fmt(-1.6), fmt(side * 1.6), fmt(-2.2)), stroke=RABC, w=0.7)
    circ(doc, x + side * (r + 1.2), y, r, fill=shade(doc, RABC, light=0.45), stroke=tone(RABC, 0.4), w=0.35)
    spec(doc, x + side * (r + 1.2), y, r, a0=205, a1=245, op=0.6, inset=0.55, w=0.35)


def fusion(doc):
    x0, w = 25, 415
    heading(doc, x0, BY, 4, 'Docking and fusion', 'ENERITZ', x0 + w, sub='magnified at 4: a lysosome meets the late phagosome')
    top, bot = BY + 16, BY + 70
    mid = (top + bot) / 2
    LUMA, LUMB = '#F9D5CA', '#E4D3F3'
    sx = [x0 + 6, x0 + 146, x0 + 286]
    sw = 94
    # a: tethering
    a = sx[0]
    A = [(a + 18, top), (a + 25, mid), (a + 18, bot)]
    B = [(a + 76, top), (a + 69, mid), (a + 76, bot)]
    lumen_fill(doc, A, a, top, bot, LUMA)
    lumen_fill(doc, B, a + sw, top, bot, LUMB)
    mem_draw(doc, A, '#C23B2A')
    mem_draw(doc, B, '#7A3FB5')
    rab_pin(doc, a + 25, mid + 14, 1)
    rab_pin(doc, a + 69, mid + 14, -1)
    for k, dx in enumerate((32, 39.5, 47, 54.5, 62)):
        circ(doc, a + dx, mid + 14 + (0.8 if k % 2 else -0.8), 3.4, fill=HOPSC, stroke='#3E1E70', w=0.4)
    T(doc, a + 47, mid + 26, 'HOPS', size=5.6, weight=700, fill=HOPSC, anchor='middle', halo='#fff')
    T(doc, a + 47, top + 7, 'Rab7-GTP', size=5.8, weight=700, fill=RABC, anchor='middle', halo='#fff')
    leader(doc, [(a + 40, top + 9), (a + 30, mid + 10)], color=RABC, w=0.4, dot=False)
    for k, c in enumerate((QA, QB, QC)):
        helix(doc, a + 26, mid - 10 + k * 5, a + 40, mid - 11 + k * 5, c, amp=0.9, turns=2.5, w=1.1, phase=k)
    helix(doc, a + 68, mid - 5, a + 54, mid - 5, RS, amp=0.9, turns=2.5, w=1.1)
    # b: zippering
    b = sx[1]
    A = [(b + 18, top), (b + 30, mid - 11), (b + 41, mid), (b + 30, mid + 11), (b + 18, bot)]
    B = [(b + 76, top), (b + 64, mid - 11), (b + 53, mid), (b + 64, mid + 11), (b + 76, bot)]
    lumen_fill(doc, A, b, top, bot, LUMA)
    lumen_fill(doc, B, b + sw, top, bot, LUMB)
    mem_draw(doc, A, '#C23B2A')
    mem_draw(doc, B, '#7A3FB5')
    ell(doc, b + 47, mid, 11, 8, fill=HOPSC, op=0.2)
    for k, c in enumerate((QA, QB, QC, RS)):
        helix(doc, b + 41, mid + (k - 1.5) * 1.5, b + 53, mid + (k - 1.5) * 1.5, c, amp=1.4, turns=2.0, w=1.0, phase=k * 1.57)
    T(doc, b + 47, top + 7, 'trans-SNARE', size=5.8, weight=700, fill=NAVY, anchor='middle', halo='#fff')
    # c: fusion pore
    c_ = sx[2]
    pts = [(c_ + 6, top), (c_ + 28, top + 3), (c_ + 47, mid - 17), (c_ + 66, top + 3), (c_ + 88, top),
           (c_ + 90, mid), (c_ + 88, bot), (c_ + 66, bot - 3), (c_ + 47, mid + 17), (c_ + 28, bot - 3), (c_ + 6, bot), (c_ + 4, mid)]
    g = doc.lingrad([(0, LUMA), (1, LUMB)], 0, 0, 1, 0)
    path(doc, cr_path(pts, True), fill=g)
    path(doc, cr_path(pts, True), stroke='#8A3A8A', w=3.4)
    path(doc, cr_path(pts, True), stroke='#fff', w=1.1)
    for (dx, dy) in [(72, 12), (80, 30), (66, 38)]:
        enzyme_dot(doc, c_ + dx, top + dy, 1.9)
    for (dx, dy) in [(18, 16), (24, 34), (12, 40)]:
        hplus(doc, c_ + dx, top + dy, 1.1)
    arrow(doc, [(c_ + 70, mid + 8), (c_ + 26, mid + 8)], BIO, 'transport', w=1.0, head=4.5, smooth=False)
    T(doc, c_ + 47, mid - 2, 'pore', size=5.6, weight=700, fill='#4A2A5A', anchor='middle')
    for xa in (x0 + 110, x0 + 250):
        arrow(doc, [(xa, mid), (xa + 18, mid)], CONV, 'fusion', w=1.4, head=6, smooth=False)
    caps = ['**a Tethering**: Rab7-GTP recruits the HOPS complex, which bridges both membranes',
            '**b Zipping**: syntaxin-7, Vti1b and syntaxin-8 coil with VAMP7',
            '**c Fusion**: a pore opens and contents mix; NSF later recycles the SNAREs']
    for xx, t in zip(sx, caps):
        P(doc, xx, bot + 9, t, 128, size=5.8, lh=1.16, boldfill=NAVY)


def killing(doc):
    x0, w = 456, 410
    heading(doc, x0, BY, 2, 'Killing and digestion', None, None, sub='two separate mechanisms, magnified from 2.3–2.6')
    cy = BY + 39
    # oxidative burst
    cx = x0 + 20
    vesicle(doc, cx, cy, 17, fill='#FDEAF0', stroke='#B03060', w=1.0)
    bacterium(doc, cx, cy + 1, L=19, W=8, rot=-20, lps=False, flagella=False, scale=1.0)
    nox2(doc, cx, cy - 17, -90, s=1.15)
    for (dx, dy) in [(-9, -3), (9, -6), (8, 8), (-6, 9)]:
        ros(doc, cx + dx, cy + dy, s=1.0)
    P(doc, x0 + 44, cy - 10, '**Oxidative burst** (from 2.3): NOX2 passes electrons from cytosolic NADPH to O₂ → superoxide → H₂O₂', 152,
      size=6.0, lh=1.16, boldfill=DINFL)
    # acid hydrolysis
    x1 = x0 + 208
    cx = x1 + 20
    g = doc.radgrad([(0, '#F5ECFB'), (1, '#DCC8F0')], cx=.5, cy=.5, r=.6)
    vesicle(doc, cx, cy, 17, fill=g, stroke=CONV, w=1.0)
    for (dx, dy) in [(-6, -4), (5, -8), (8, 6), (-4, 9), (0, 1)]:
        enzyme_dot(doc, cx + dx, cy + dy, 2.1)
    for (dx, dy) in [(-9, 3), (3, -1), (-1, 10)]:
        hplus(doc, cx + dx, cy + dy, 1.0)
    for a in (200, 270, 340, 50, 120):
        px, py = on_circle(cx, cy, 17, a)
        vatpase(doc, px, py, a, s=0.6)
    P(doc, x1 + 44, cy - 10, '**Acid hydrolysis** (after fusion, 2.6): V-ATPase pumps H⁺ in; cathepsins, lipases, nucleases and glycosidases dismantle the bacterium', 158,
      size=6.0, lh=1.16, boldfill=DLY)
    line(doc, x0 + 202, BY + 16, x0 + 202, BY + 60, RULE, 0.5)
    P(doc, x0, BY + 80, '**Products** (amino acids, sugars, nucleotides) leave for reuse; some peptides are presented on **MHC II** to T cells.', w,
      size=6.0, lh=1.16, boldfill='#0B6B72', fill=INK2)


def conclusion(doc):
    x0, w = RX, RW
    heading(doc, x0, BY, 6, 'Take-home', 'AITOR', x0 + w)
    y1 = BY + 16
    # cleared
    bacterium(doc, x0 + 12, y1, L=16, W=6.6, rot=0, lps=False, flagella=False, scale=1.0)
    arrow(doc, [(x0 + 23, y1), (x0 + 33, y1)], PHAG, 'transport', w=1.0, head=4, smooth=False)
    contact_shadow(doc, x0 + 42, y1, 7.5, strength=0.12)
    circ(doc, x0 + 42, y1, 7.5, fill=shade(doc, '#E4D3F3', light=0.6, dark=0.06), stroke=CONV, w=1.1)
    circ(doc, x0 + 42, y1, 6.6, fill='none', stroke=lighten(CONV, 0.82), w=0.35)
    for (dx, dy) in [(-2.5, -2), (2.5, 2.4), (-2.6, 2.8)]:
        enzyme_dot(doc, x0 + 42 + dx, y1 + dy, 1.3)
    spec(doc, x0 + 42, y1, 7.5, a0=200, a1=245, op=0.7, inset=0.78, w=0.45)
    arrow(doc, [(x0 + 51, y1), (x0 + 61, y1)], RECY, 'recycle', w=1.0, head=4, smooth=False)
    T(doc, x0 + 66, y1 + 2.2, 'degraded and recycled', size=5.6, weight=700, fill=DREC)
    # persistent
    y2 = BY + 34
    silica(doc, x0 + 12, y2, s=0.8, rot=10)
    arrow(doc, [(x0 + 23, y2), (x0 + 33, y2)], PHAG, 'transport', w=1.0, head=4, smooth=False)
    contact_shadow(doc, x0 + 42, y2, 7.5, strength=0.12)
    circ(doc, x0 + 42, y2, 7.5, fill=shade(doc, '#F2E6DA', light=0.6, dark=0.06), stroke=CONV, w=1.1, dash='3 1.4')
    silica(doc, x0 + 42, y2, s=0.5, rot=-10)
    spec(doc, x0 + 42, y2, 7.5, a0=200, a1=245, op=0.7, inset=0.78, w=0.45)
    arrow(doc, [(x0 + 51, y2), (x0 + 61, y2)], PATH, 'path', w=1.0, head=4.6, smooth=False)
    T(doc, x0 + 66, y2 + 2.2, 'inflammation and fibrosis', size=5.6, weight=700, fill=DPATH)
    PS(doc, x0, BY + 52, 'Clearing a microbe needs two routes to converge: the maturing phagosome and lysosomal enzyme delivery. When the cargo cannot be degraded, the same machinery drives lung injury.',
      w, size=6.3, lh=1.2, family=SERIF, kind='serif', fill=NAVY)


def zoom_links(doc):
    # fusion site (marker 4) -> docking and fusion panel
    line(doc, 496, 612, 432, BY - 14, CONV, 0.6, dash='2.2 1.6')
    circ(doc, 432, BY - 14, 1.3, fill=CONV)
    # phagolysosome -> killing panel
    line(doc, 590, 689, 540, BY - 14, PHAG, 0.6, dash='2.2 1.6')
    circ(doc, 540, BY - 14, 1.3, fill=PHAG)
    flows(doc)


# ===================================================================================== key + footer
def key(doc, y=650):
    x = 25
    T(doc, x, y, 'READING THE FIGURE', size=5.4, weight=700, fill=NAVY, spacing=1.0)
    arrows = [('transport', PHAG, 'Phagocytic route'), ('transport', BIO, 'Enzyme (biosynthetic) route'), ('fusion', CONV, 'Membrane fusion'),
              ('recycle', RECY, 'Recycling'), ('path', PATH, 'Pathological effect'), ('signal', INFL, 'Inflammatory signal')]
    for k, (kind, col, t) in enumerate(arrows):
        cx = x + (k // 3) * 122
        cy = y + 9.5 + (k % 3) * 8.6
        arrow(doc, [(cx, cy - 1.8), (cx + 15, cy - 1.8)], col, kind, w=1.3 if kind != 'path' else 1.2, head=5, smooth=False)
        T(doc, cx + 19, cy, t, size=5.8, fill=INK)
    sy = y + 41
    syms = [(lambda c, r: hydrolase(doc, c - 4, r, s=1.1, p=True), 'hydrolase + M6P'),
            (lambda c, r: m6pr(doc, c, r + 4.5, s=1.1), 'M6P receptor'),
            (lambda c, r: vatpase(doc, c, r + 3.5, -90, s=1.0), 'V-ATPase'),
            (lambda c, r: nox2(doc, c, r + 3, -90, s=0.9), 'NOX2'),
            (lambda c, r: (ros(doc, c - 3, r, s=1.1), ros(doc, c + 3, r + 1, s=0.9)), 'ROS'),
            (lambda c, r: (hplus(doc, c - 3, r, 1.3), hplus(doc, c + 3, r + 1.5, 1.3)), 'H⁺')]
    for k, (fn, t) in enumerate(syms):
        cx = x + 6 + (k % 3) * 82
        cy = sy + (k // 3) * 11
        fn(cx, cy - 2)
        T(doc, cx + 12, cy, t, size=5.6, fill=INK)
    P(doc, x, sy + 22, 'Steps 2.1 → 2.6 happen in sequence, while the enzyme route 3.1 → 3.6 runs continuously alongside them.', 237, size=5.6, lh=1.15, fill=INK2, italic=True)


def flows(doc):
    """Continuous process lines that carry the story from one stage to the next (no hard section breaks)."""
    # 1 -> 2 (left margin)
    arrow(doc, [(16, 120), (16, 200), (16, 280)], NAVY, 'transport', w=0.9, head=4.5, smooth=False, opacity=0.55)
    # engulfment frames -> nascent phagosome inside the cell (2.2 -> 2.3)
    arrow(doc, [(250, 620), (290, 600), (318, 548), (330, 512)], PHAG, 'transport', w=1.4, head=6, opacity=0.9)
    T(doc, 256, 634, 'continues as 2.3 in the cell', size=5.4, italic=True, fill=DPHAG)
    # fusion panel -> killing panel
    arrow(doc, [(436, BY + 43), (452, BY + 43)], CONV, 'fusion', w=1.3, head=5.5, smooth=False)
    # pathology timeline (5.2 -> 5.5 -> take-home, persistence row)
    x = RX - 6
    for (y0, y1) in [(232, 342), (362, 386), (402, 474), (490, 590), (606, BY - 14)]:
        line(doc, x, y0, x, y1, PATH, 1.2, op=0.75)
    for yy in (242.2, 390.2, 478.2, 594.2):
        path(doc, 'M%s,%s l-2.2,-3 h4.4 z' % (fmt(x), fmt(yy)), fill=PATH)
    arrow(doc, [(x, BY - 14), (x, BY + 30), (RX + 4, BY + 34)], PATH, 'path', w=1.0, head=4.6, smooth=False)
    # killing -> take-home, clearance row
    arrow(doc, [(846, BY + 66), (868, BY + 58), (RX - 12, BY + 26), (RX + 4, BY + 16)], RECY, 'recycle', w=1.0, head=4.6)


REFS = [
    'Alberts B, Heald R, Johnson A, et al. Molecular Biology of the Cell, 7th ed. New York: W.W. Norton; 2022.',
    'Hussell T, Bell TJ. Alveolar macrophages: plasticity in a tissue-specific context. Nat Rev Immunol 2014;14:81–93.',
    'Flannagan RS, Jaumouillé V, Grinstein S. The cell biology of phagocytosis. Annu Rev Pathol 2012;7:61–98.',
    'Kinchen JM, Ravichandran KS. Phagosome maturation: going through the acid test. Nat Rev Mol Cell Biol 2008;9:781–795.',
    'Nunes P, Demaurex N, Dinauer MC. Regulation of the NADPH oxidase and associated ion fluxes during phagocytosis. Traffic 2013;14:1118–1131.',
    'Braulke T, Bonifacino JS. Sorting of lysosomal proteins. Biochim Biophys Acta 2009;1793:605–614.',
    'Luzio JP, Pryor PR, Bright NA. Lysosomes: fusion and function. Nat Rev Mol Cell Biol 2007;8:622–632.',
    'Jahn R, Scheller RH. SNAREs: engines for membrane fusion. Nat Rev Mol Cell Biol 2006;7:631–643.',
    'Hornung V, Bauernfeind F, Halle A, et al. Silica crystals and aluminum salts activate the NALP3 inflammasome through phagosomal destabilization. Nat Immunol 2008;9:847–856.',
    'Leung CC, Yu ITS, Chen W. Silicosis. Lancet 2012;379:2008–2018.',
    'Donaldson K, Murphy FA, Duffin R, Poland CA. Asbestos, carbon nanotubes and the pleural mesothelium: a review of the hypothesis regarding the role of long fibre retention in the parietal pleura, inflammation and mesothelioma. Part Fibre Toxicol 2010;7:5.',
    'Wynn TA, Ramalingam TR. Mechanisms of fibrosis: therapeutic translation for fibrotic disease. Nat Med 2012;18:1028–1040.',
]


def footer(doc):
    y0 = 864
    line(doc, 25, y0 - 6, 1075, y0 - 6, RULE, 0.6)
    T(doc, 25, y0, 'REFERENCES', size=4.6, weight=700, fill=NAVY, spacing=1.0)
    cols, cw = 3, 352
    per = 4
    for c in range(cols):
        yy = y0 + 6.5
        for i in range(per):
            n = c * per + i
            if n >= len(REFS):
                break
            T(doc, 25 + c * cw, yy, '%d' % (n + 1), size=4.0, weight=700, fill='#8A8170')
            hh = P(doc, 31.5 + c * cw, yy, REFS[n], cw - 12, size=4.0, lh=1.12, fill='#4A4538')
            yy += hh + 0.6
    T(doc, 1075, y0, 'Original illustration · schematic, not to scale', size=4.6, italic=True, fill='#6B6455', anchor='end')
