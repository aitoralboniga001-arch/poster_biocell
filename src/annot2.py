"""V2 skeleton: in-cell labels.  Organelle names in Gabriola (hand), larger than the molecule labels and coloured like
the organelle; small numbered step tags (2.2-2.5) where they belong; Rab / pH data tags on the phagosome chain.
Labels of things that moved to the zones (Golgi, TGN, CCV, late endosome, lysosome, phagolysosome, silica, NLRP3)
are drawn by the zone owners."""
import math
from lib import *
from bio import *
from cellmod import *
from cellmod2 import *
from marks import HAND

DBIO = '#143F96'
DGOL = '#14527A'
DEE = '#A85A0C'
DLE = '#A8301F'
DLY = '#5A2A8C'
DPHAG = '#B8321C'
DPATH = '#8A4F0B'
DINFL = '#A3144F'
DREC = '#0E7F58'
DNUC = '#4B3F8F'
DER = '#1F4E9A'
DMITO = '#8A5A22'

NAME, NOTE, TAGS = 7.0, 6.0, 5.0
ORG = 13.0                     # organelle-name size (Gabriola)

_GAB = 'C:/Windows/Fonts/Gabriola.ttf'
_gab = {}


def hand_width(s, size):
    try:
        from PIL import ImageFont
        if 'f' not in _gab:
            _gab['f'] = ImageFont.truetype(_GAB, 100)
        return _gab['f'].getlength(s) * size / 100
    except Exception:
        return len(s) * size * 0.4


def tag(doc, x, y, txt, color, size=TAGS):
    """Small rounded step tag; (x, y) = left end of the baseline. Returns its width."""
    w = text_width(txt, size, 700) + 3.4
    rect(doc, x, y - size * 1.05, w, size * 1.62, fill=color, r=size * 0.8)
    T(doc, x + w / 2, y + size * 0.08, txt, size=size, weight=700, fill='#fff', anchor='middle')
    return w


def label(doc, x, y, title, color, step=None, note=None, width=110, anchor='start', size=NAME, nsize=NOTE, halo=CYTO, nfill=None):
    """(V1 API, used by zone modules) Title (bold) with optional step tag and note underneath."""
    tw = text_width(title, size, 700)
    sw = (text_width(step, TAGS, 700) + 3.4 + 2.0) if step else 0
    x0 = x - tw - sw if anchor == 'end' else x
    if step:
        tag(doc, x0, y - size * 0.14, step, color)
    T(doc, x0 + sw, y, title, size=size, weight=700, fill=color, halo=halo)
    h = 0
    if note:
        h = P(doc, x, y + nsize * 1.22, note, width, size=nsize, fill=nfill or color, lh=1.16, anchor=anchor, halo=halo)
    return y + nsize * 1.22 + h


def ph_tag(doc, x, y, txt, color, anchor='start'):
    """Compact pH data tag (outlined pill)."""
    size = 5.0
    w = text_width(txt, size, 700) + 3.6
    x0 = x - w if anchor == 'end' else x
    rect(doc, x0, y - size * 1.0, w, size * 1.5, fill='#FFFFFF', stroke=color, sw=0.5, r=size * 0.75, op=0.92)
    T(doc, x0 + w / 2, y + size * 0.1, txt, size=size, weight=700, fill=color, anchor='middle')
    return w


def hand(doc, x, y, text, color, size=ORG, anchor='start', halo='#FEF3EA', op=None):
    """Organelle name in Gabriola with a soft cytoplasm-coloured halo."""
    a = ' opacity="%s"' % fmt(op) if op is not None else ''
    if halo:
        a += ' stroke="%s" stroke-width="%s" stroke-linejoin="round" paint-order="stroke"' % (halo, fmt(size * 0.16))
    doc.add('<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>'
            % (fmt(x), fmt(y), HAND, fmt(size), color, anchor, a, esc(text)))
    hw = hand_width(text, size)
    if hasattr(doc, 'register_label'):
        doc.register_label(text, x, y, size=size, fill=color, anchor=anchor, kind='hand', width=hw)
    return hw


def organelle(doc, x, y, name, color, step=None, anchor='start', size=ORG):
    """Step tag + organelle name; (x, y) = baseline start (anchor 'end': baseline end).  Returns (x0, x1)."""
    tw = hand_width(name, size)
    sw = (text_width(step, TAGS, 700) + 3.4 + 2.2) if step else 0
    x0 = x - tw - sw if anchor == 'end' else x
    if step:
        tag(doc, x0, y - size * 0.24, step, color)
    hand(doc, x0 + sw, y, name, color, size)
    if step and hasattr(doc, 'register_label'):
        doc.register_label('%s %s' % (step, name), x0, y, size=size, fill=color, anchor='start', kind='hand', width=sw + tw, step=step)
    return x0, x0 + sw + tw


def draw_annotations(doc):
    cx, cy, rx, ry = V.NUCLEUS
    hand(doc, cx + 6, cy + 58, 'Nucleus', DNUC, size=17, anchor='middle', halo='#EAE4F7')
    hand(doc, 566, 268, 'Rough ER', DER, size=ORG)

    # ------------------------------------------------ 2: phagocytic route (organelle scale)
    # 2.2 written along the lower pseudopod arm, inside it (baseline follows the arm's axis)
    group(doc, transform='rotate(10.5 76 512.5)')
    organelle(doc, 76, 512.5, 'Pseudopod', DPHAG, '2.2', size=9.0)
    endgroup(doc)
    x, y, r = NP
    organelle(doc, x + r + 8, y - 22, 'Nascent phagosome', DPHAG, '2.3')
    x, y, r = EP
    organelle(doc, x - r - 12, y + 4, 'Early phagosome', DEE, '2.4', anchor='end')
    ph_tag(doc, x - r - 12, y + 15, 'pH 6.5', DEE, anchor='end')
    membrane_tag(doc, x - 4, y - r - 6, 'Rab5-GTP', RAB5, 5.0)
    x, y, r = LP
    organelle(doc, x - r - 4, y + 32, 'Late phagosome', DLE, '2.5', anchor='end')
    ph_tag(doc, x - r - 4, y + 44, 'pH 5.5', DLE, anchor='end')
    px, py = on_circle(x, y, r + 8.5, 158)
    membrane_tag(doc, px - 2, py, 'Rab7-GTP', RAB7, 5.0)
    hand(doc, 268, 744, 'Mitochondrion', DMITO, size=10.5, anchor='middle')
