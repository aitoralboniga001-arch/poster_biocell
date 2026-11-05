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


def ph_tag(doc, x, y, txt, color, anchor='start'):
    """Compact pH data tag (outlined pill) carrying the acidification story."""
    size = 5.0
    w = text_width(txt, size, 700) + 3.6
    x0 = x - w if anchor == 'end' else x
    rect(doc, x0, y - size * 1.0, w, size * 1.5, fill='#FFFFFF', stroke=color, sw=0.5, r=size * 0.75, op=0.92)
    T(doc, x0 + w / 2, y + size * 0.1, txt, size=size, weight=700, fill=color, anchor='middle')


def draw_annotations(doc):
    # V1.2b text diet: step tag + NAME only; pH as data tags on the maturation path; Rab tags kept.
    T(doc, 470, 290, 'Nucleus', size=NAME, weight=700, fill='#4B418A', halo='#E6E1F5')

    # ---------------------------------------------------------------- 3: biosynthetic route (cobalt)
    label(doc, 640, 182, 'Rough ER', DBIO, '3.1')
    T(doc, 672, 345, 'COPII', size=6.4, weight=700, fill=DBIO, halo=CYTO)
    label(doc, 523, 396, 'Golgi', DGOL, '3.2', anchor='end')
    T(doc, 682, 375.5, 'cis', size=5.4, fill=DGOL, italic=True, halo=CYTO)
    T(doc, 682, 417.5, 'trans', size=5.4, fill=DGOL, italic=True, halo=CYTO)
    label(doc, 533, 440, 'TGN', DGOL, '3.3', anchor='end')
    label(doc, 646, 491, 'Clathrin vesicle', DGOL, '3.4', size=6.6)
    label(doc, 588, 520, 'Late endosome', DLE, '3.5')
    label(doc, 712, 579, 'Lysosome', DLY, '3.6')

    tag(doc, CONTACT[0] - 12, CONTACT[1] - 28, '2.1', PHAG)

    # ---------------------------------------------------------------- 2: phagocytic route (vermilion)
    label(doc, 324, 372, 'Pseudopod', DPHAG, '2.2')
    label(doc, 388, 470, 'Nascent phagosome', DPHAG, '2.3')
    label(doc, 442, 509, 'Early endosome', DEE, None, anchor='end', size=6.0)
    label(doc, 436, 554, 'Early phagosome', DEE, '2.4')
    ph_tag(doc, 451, 563, 'pH 6.5', DEE)
    label(doc, 444, 636, 'Late phagosome', DLE, '2.5', anchor='end')
    ph_tag(doc, 444, 645, 'pH 5.5', DLE, anchor='end')
    label(doc, 662, 624, 'Phagolysosome', DLY, '2.6', size=7.6)
    ph_tag(doc, 677, 634, 'pH 4.5', DLY)
    T(doc, 676, 664, 'recycled', size=6.0, weight=700, fill=DREC, halo=CYTO)
    membrane_tag(doc, EP[0], EP[1] - EP[2] - 4.5, 'Rab5-GTP', '#E3A21A', 5.0)
    membrane_tag(doc, LP[0], LP[1] - LP[2] - 4.5, 'Rab7-GTP', '#C0392B', 5.0)
    membrane_tag(doc, LE[0] - 4, LE[1] - LE[2] - 4.5, 'Rab7', '#C0392B', 4.8)

    # ---------------------------------------------------------------- 4: fusion site (source ring drawn by m_vesicles)
    badge(doc, 521, 614, 4, r=6.0, fill=CONV, size=7.4)

    # ---------------------------------------------------------------- 5: particles inside the cell
    label(doc, 762, 430, 'Silica', DPATH, '5.2', size=6.4)
    T(doc, 744, 545, 'NLRP3', size=6.0, weight=700, fill=DINFL, anchor='middle', halo=CYTO)
