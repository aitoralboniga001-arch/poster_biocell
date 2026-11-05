"""Shared panel styling helpers."""
from lib import *
from bio import *

CARD_FILL = '#FFFFFF'
CARD_LINE = '#D8CDB8'
NAVY = '#14202E'


def card(doc, x, y, w, h, fill=CARD_FILL, stroke=CARD_LINE, sw=0.7, r=5, op=0.86):
    rect(doc, x, y, w, h, fill=fill, stroke=stroke, sw=sw, r=r)


def panel_title(doc, x, y, num, title, speaker=None, sub=None, w=None, color=NAVY, size=8.6):
    badge(doc, x + 6.5, y + 6.5, num, r=6.6, fill=color, size=8.2)
    T(doc, x + 17, y + 9.4, title, size=size, weight=700, fill=color, family=SERIF, kind='serif')
    if speaker and w:
        T(doc, x + w, y + 8.2, speaker, size=3.8, weight=600, fill='#6B7380', anchor='end', spacing=0.6)
    if sub:
        T(doc, x + 17, y + 16.4, sub, size=4.4, fill='#4A5563', italic=True)


def chip(doc, x, y, text, fill, fg='#fff', size=4.0, weight=600, h=None, pad=2.6, stroke=None):
    w = text_width(text, size, weight) + pad * 2
    hh = h or size * 1.75
    rect(doc, x, y, w, hh, fill=fill, r=hh / 2, stroke=stroke, sw=0.5)
    T(doc, x + w / 2, y + hh / 2 + size * 0.34, text, size=size, weight=weight, fill=fg, anchor='middle')
    return w
