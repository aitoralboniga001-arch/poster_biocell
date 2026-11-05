"""Labels and callouts drawn on the macrophage (Level 1 names large, Level 2 annotations medium)."""
from lib import *
from bio import *
from cellmod import *
from cellmod2 import *
from panels_common import chip

DBIO = '#143F96'
DGOL = '#14527A'
DEE = '#A85A0C'
DLE = '#A8301F'
DLY = '#5A2A8C'
DPHAG = '#B8321C'
DPATH = '#8A4F0B'
DINFL = '#A3144F'
DREC = '#0E7F58'
TEALD = '#0B6B72'


def step(doc, x, y, txt, color=INK, size=3.3):
    w = text_width(txt, size, 700) + 3.2
    rect(doc, x, y - size * 1.02, w, size * 1.6, fill=color, r=size * 0.8)
    T(doc, x + w / 2, y + size * 0.1, txt, size=size, weight=700, fill='#fff', anchor='middle')
    return w


def name(doc, x, y, text, color, size=5.4, tagtxt=None, tagcolor=None, anchor='start', halo=CYTO):
    off = 0
    if tagtxt:
        off = step(doc, x, y - 0.5, tagtxt, tagcolor or color) + 1.8
    T(doc, x + off, y, text, size=size, weight=700, fill=color, anchor=anchor, halo=halo)
    return off + text_width(text, size, 700)


def note(doc, x, y, text, width, size=4.2, fill=INK2, lh=1.2, anchor='start', halo=CYTO, boldfill=None):
    return P(doc, x, y, text, width, size=size, fill=fill, lh=lh, anchor=anchor, halo=halo, boldfill=boldfill)


def draw_annotations(doc):
    gx = GOLGI_C[0]
    # -------- whole cell
    T(doc, 478, 170, 'ALVEOLAR MACROPHAGE', size=9.5, weight=700, fill='#A24A3B', anchor='middle', spacing=1.8, opacity=0.92)
    T(doc, 478, 178, 'professional phagocyte of the lung  ·  15–20 µm', size=4.2, fill='#A24A3B', anchor='middle', opacity=0.92)
    T(doc, 468, 292, 'Nucleus', size=6.2, weight=700, fill='#4B418A')

    # -------- biosynthetic pathway
    name(doc, 628, 160, 'Rough ER', DBIO, 6.4, '3.1')
    note(doc, 628, 167, 'Bound ribosomes thread new hydrolases through Sec61 into the lumen', 150, size=4.2, fill=DBIO)
    step(doc, 626, 234, '3.2', DBIO, 3.2)
    T(doc, 641, 234.4, 'N-glycosylation · folding · quality control', size=4.2, weight=600, fill=DBIO)

    name(doc, 676, 335, 'COPII vesicles', DBIO, 4.8)
    note(doc, 676, 341, 'ER exit site → cis-Golgi', 110, size=4.1, fill=DBIO)
    name(doc, 700, 384, 'Golgi apparatus', DGOL, 6.0, '3.3')
    note(doc, 700, 391, '**cis**: GlcNAc-1-phosphotransferase adds P-GlcNAc to mannose', 125, size=4.2, fill=DGOL, boldfill=DGOL)
    T(doc, 505, 377, 'cis', size=4.6, weight=700, fill=DGOL, anchor='end', halo=CYTO)
    T(doc, 505, 423, 'trans', size=4.6, weight=700, fill=DGOL, anchor='end', halo=CYTO)
    name(doc, 700, 446, 'trans-Golgi network', DGOL, 5.6, '3.4')
    note(doc, 700, 453, '**Uncovering enzyme** exposes **M6P**; M6P receptors bind it; AP-1/GGA recruit clathrin', 128, size=4.2, fill=DGOL, boldfill=DGOL)
    name(doc, 648, 488, 'Clathrin-coated vesicles', DGOL, 4.6)

    # -------- endosomes / lysosomes
    name(doc, 574, 518, 'Late endosome', DLE, 5.4, '3.5')
    note(doc, 574, 525, 'acid pH frees hydrolase from M6PR', 120, size=4.1, fill=DLE)
    T(doc, 508, 484, 'M6PR recycling', size=4.7, weight=700, fill=DREC, anchor='end', halo=CYTO)
    note(doc, 508, 490.5, 'receptor returns to TGN', 80, size=4.0, fill=DREC, anchor='end')
    T(doc, 712, 572, 'Lysosome', size=5.2, weight=700, fill=DLY, halo=CYTO)
    note(doc, 712, 578.5, 'hydrolase-rich, LAMP-lined', 100, size=4.0, fill=DLY)
    note(doc, 712, 584.5, '(classical “primary” lysosome)', 100, size=4.0, fill=DLY)

    # -------- phagocytic route labels
    name(doc, 386, 474, 'Nascent phagosome', DPHAG, 5.4, '2.3')
    note(doc, 386, 481, 'plasma-membrane derived,\nFcγR still on board', 92, size=4.1)
    name(doc, 436, 546, 'Early phagosome', DEE, 5.4)
    note(doc, 436, 553, 'EEA1 · PI(3)P · pH ≈ 6–6.5', 92, size=4.1, fill=DEE)
    T(doc, 472, 520, 'Early endosome', size=4.4, weight=700, fill=DEE, halo=CYTO)
    name(doc, 424, 676, 'Late phagosome', DLE, 5.4)
    note(doc, 424, 683, 'LAMP1/2 · V-ATPase · pH ≈ 5.5', 100, size=4.1, fill=DLE)
    name(doc, 552, 568, 'Phagolysosome', DLY, 6.0, '2.4')
    note(doc, 552, 575, 'pH 4.5–5.0 · acid hydrolases', 110, size=4.2, fill=DLY)
    # Rab pills on the phagosome membranes
    tag(doc, EP[0], EP[1] - EP[2] - 4, 'Rab5-GTP', '#E8892D', 3.6)
    tag(doc, LP[0], LP[1] - LP[2] - 4, 'Rab7-GTP', '#C23B2A', 3.6)
    tag(doc, LE[0] - 4, LE[1] - LE[2] - 4, 'Rab7', '#C23B2A', 3.3)

    # -------- microtubule + centrosome
    T(doc, 578, 337, 'Centrosome', size=4.0, weight=700, fill='#6B7380', halo=CYTO)
    note(doc, 424, 398, 'microtubules: dynein hauls phagosomes and lysosomes towards the centre', 108, size=4.0, fill='#6B7380')

    # -------- antigen presentation / products
    T(doc, 392, 666, 'MIIC', size=4.4, weight=700, fill=TEALD, anchor='middle', halo=CYTO)
    note(doc, 668, 664, 'amino acids, sugars, nucleotides, fatty acids → cytosol', 74, size=4.0, fill=DREC)

    # -------- engulfment label at the cup, Rab switch, pathology tags
    name(doc, 326, 374, 'Actin-rich pseudopods', DPHAG, 4.8, '2.2')
    note(doc, 326, 380.5, 'branched F-actin (Arp2/3) drives the cup', 100, size=4.0, fill=DPHAG)
    T(doc, 436, 572, 'Rab5 → Rab7', size=3.9, weight=700, fill=DLE, halo=CYTO)
    chip(doc, 708, 506, 'ASBESTOS', '#B07A1E', size=3.9, pad=2.6)
    T(doc, 708, 520, 'Frustrated phagocytosis', size=4.8, weight=700, fill=DPATH, halo=CYTO)
    note(doc, 708, 526.5, 'fibre longer than the cell: the cup cannot close', 112, size=4.0, fill=DPATH)
    chip(doc, 738, 598, 'SILICA', '#6C7A90', size=3.9, pad=2.6)
    T(doc, 726, 631, 'NLRP3', size=4.4, weight=700, fill=DINFL, anchor='middle', halo=CYTO)
    note(doc, 472, 527, 'cargo exchange', 70, size=3.8, fill=DEE)
    # section navigation discs
    for (x, y, n, c) in [(614, 153, 3, DBIO), (306, 352, 2, DPHAG), (697, 513, 5, PATH), (730, 603, 5, PATH)]:
        badge(doc, x, y, n, r=6.2, fill=c, size=7.6)
    # fusion-site marker -> magnified inset 4
    circ(doc, 503, 598, 15, fill='none', stroke=CONV, w=1.3, dash='3 1.6')
    badge(doc, 503, 578, 4, r=6.2, fill=CONV, size=7.6)
    T(doc, 503, 626, '', size=3)
    # -------- plasma membrane
    T(doc, 478, 126, 'Plasma membrane', size=4.6, weight=700, fill='#8A3A2E')
    leader(doc, [(478, 128), (470, 143)], color='#8A3A2E', w=0.35)
