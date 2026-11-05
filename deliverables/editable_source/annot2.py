"""Labels on the central macrophage (v2): fewer words, larger type, step tags give the sequence."""
from lib import *
from bio import *
from cellmod import *
from cellmod2 import *

DBIO = '#143F96'
DGOL = '#14527A'
DEE = '#A85A0C'
DLE = '#A8301F'
DLY = '#5A2A8C'
DPHAG = '#B8321C'
DPATH = '#8A4F0B'
DINFL = '#A3144F'
DREC = '#0E7F58'

NAME, NOTE, TAGS = 7.0, 6.0, 5.0


def tag(doc, x, y, txt, color, size=TAGS):
    """Small rounded step tag; (x, y) = left end of the baseline. Returns its width."""
    w = text_width(txt, size, 700) + 3.4
    rect(doc, x, y - size * 1.05, w, size * 1.62, fill=color, r=size * 0.8)
    T(doc, x + w / 2, y + size * 0.08, txt, size=size, weight=700, fill='#fff', anchor='middle')
    return w


def label(doc, x, y, title, color, step=None, note=None, width=110, anchor='start', size=NAME, nsize=NOTE, halo=CYTO, nfill=None):
    """Title (bold) with optional step tag and note underneath. anchor 'end' right-aligns the block on x."""
    tw = text_width(title, size, 700)
    sw = (text_width(step, TAGS, 700) + 3.4 + 2.0) if step else 0
    if anchor == 'end':
        x0 = x - tw - sw
    else:
        x0 = x
    if step:
        tag(doc, x0, y - size * 0.14, step, color)
    T(doc, x0 + sw, y, title, size=size, weight=700, fill=color, halo=halo)
    h = 0
    if note:
        h = P(doc, x, y + nsize * 1.22, note, width, size=nsize, fill=nfill or color, lh=1.16, anchor=anchor, halo=halo)
    return y + nsize * 1.22 + h


def draw_annotations(doc):
    # ---------------------------------------------------------------- whole cell
    T(doc, 478, 170, 'ALVEOLAR MACROPHAGE', size=7.6, weight=600, fill='#A24A3B', anchor='middle', spacing=2.6, opacity=0.85)
    T(doc, 470, 290, 'Nucleus', size=NAME, weight=700, fill='#4B418A', halo='#E6E1F5')
    T(doc, 452, 127, 'Plasma membrane', size=6.0, weight=700, fill='#8A3A2E')
    leader(doc, [(470, 129.5), (466, 143)], color='#8A3A2E', w=0.45)

    # ---------------------------------------------------------------- 3: biosynthetic route (cobalt)
    circ(doc, 625.2, 154.3, 6.4, fill=BIO)
    T(doc, 625.2, 157.4, '3', size=8.4, weight=700, fill='#fff', anchor='middle')
    T(doc, 635, 158, 'Lysosome biogenesis', size=8.6, weight=600, fill='#1F2C3B', family=SERIF, halo=CYTO, spacing=-0.05)
    T(doc, 635, 166, 'URTZI', size=5.4, weight=700, fill='#8A8170', spacing=0.9)
    label(doc, 640, 180, 'Rough ER', DBIO, '3.1', 'hydrolases are made and N-glycosylated', 175)
    T(doc, 672, 345, 'COPII vesicles', size=6.0, weight=700, fill=DBIO, halo=CYTO)
    label(doc, 503, 374, 'Golgi apparatus', DGOL, '3.2', '**cis**: P-GlcNAc added to mannose', 112, anchor='end')
    label(doc, 503, 434, 'trans-Golgi network', DGOL, '3.3', 'M6P uncovered; binds the M6P receptor', 112, anchor='end')
    label(doc, 646, 489, 'Clathrin-coated vesicles', DGOL, '3.4', 'AP-1 · GGA adaptors', 100, size=6.4)
    label(doc, 576, 520, 'Late endosome', DLE, '3.5', 'pH ≈ 5.5–6: hydrolase released, M6PR recycled', 118)
    label(doc, 712, 577, 'Lysosome', DLY, '3.6', 'hydrolases inside; heavily glycosylated LAMPs in its membrane', 112)

    # ---------------------------------------------------------------- 2: phagocytic route (vermilion)
    label(doc, 324, 372, 'Pseudopods', DPHAG, '2.2', 'Arp2/3-branched F-actin', 100)
    label(doc, 388, 468, 'Nascent phagosome', DPHAG, '2.3', 'NOX2 assembles: ROS burst starts', 104)
    label(doc, 442, 509, 'Early endosome', DEE, None, 'kiss-and-run exchange', 66, anchor='end', size=6.0, nsize=5.6)
    label(doc, 436, 552, 'Early phagosome', DEE, '2.4', 'Rab5 · pH ≈ 6–6.5', 100)
    label(doc, 444, 632, 'Late phagosome', DLE, '2.5', 'Rab7 · V-ATPase · pH ≈ 5.5–6', 104, anchor='end')
    label(doc, 662, 622, 'Phagolysosome', DLY, '2.6', 'pH ≈ 4.5–5: acid hydrolases digest the bacterium', 116, size=7.6)
    label(doc, 700, 656, 'Products recycled', DREC, None, 'amino acids, sugars, nucleotides → cytosol', 82, size=6.0, nsize=5.6)
    membrane_tag(doc, EP[0], EP[1] - EP[2] - 4.5, 'Rab5-GTP', '#E8892D', 5.0)
    membrane_tag(doc, LP[0], LP[1] - LP[2] - 4.5, 'Rab7-GTP', '#C23B2A', 5.0)
    membrane_tag(doc, LE[0] - 4, LE[1] - LE[2] - 4.5, 'Rab7', '#C23B2A', 4.8)

    # ---------------------------------------------------------------- 4: fusion site (magnified below)
    circ(doc, 503, 598, 15, fill='none', stroke=CONV, w=1.4, dash='3 1.6')
    badge(doc, 521, 614, 4, r=6.0, fill=CONV, size=7.4)

    # ---------------------------------------------------------------- 5: particles inside the cell
    tag(doc, 756, 391, '5.2', PATH)
    T(doc, 770, 391, 'ASBESTOS', size=5.6, weight=700, fill=DPATH, halo=CYTO, spacing=0.4)
    tag(doc, 764, 433, '5.3', PATH)
    T(doc, 778, 433, 'SILICA', size=5.6, weight=700, fill=DPATH, halo=CYTO, spacing=0.4)
    T(doc, 744, 545, 'NLRP3', size=6.0, weight=700, fill=DINFL, anchor='middle', halo=CYTO)
