"""Poster sections. Each function draws into the Doc."""
import math, random
from lib import *
from bio import *
import cellmod2 as cellmod
import cellmod3
import annot
import panels_top, panels_left, panels_right, panels_bottom


def background(doc):
    rect(doc, 0, 0, 1100, 900, fill=PAPER)
    # faint alveolar septa hinting at the lung environment behind the cell
    for (cx, cy, r) in [(120, 520, 150), (60, 380, 90), (210, 690, 110)]:
        circ(doc, cx, cy, r, fill='none', stroke='#E6DDCB', w=1.2, op=0.7)


def contact_site(doc):
    """Opsonised bacterium A meets receptors on the plasma membrane; magnifier ring leads to the 2.1 inset."""
    for (y, kind, col) in [(284, 'fc', '#5A6B85'), (297, 'cr', '#1F8F8A'), (310, 'lectin', '#8F5A2A'), (322, 'tlr', '#C81D63')]:
        receptor(doc, 307, y, h=10, rot=-90, color=col, kind=kind, tail=True)
    for y in (291, 303):
        antibody(doc, 299, y, s=0.9, rot=-90)
    c3b(doc, 297, 316, s=1.0, rot=-90)
    cx, cy, r = 301, 302, 26
    wedge = 'M%s,%s L236,262 L236,340 L%s,%s Z' % (fmt(cx - 2), fmt(cy - r + 1), fmt(cx - 2), fmt(cy + r - 1))
    g = doc.lingrad([(0, '#D95C3F', 0.0), (1, '#D95C3F', 0.14)], 1, 0, 0, 0)
    path(doc, wedge, fill=g)
    circ(doc, cx, cy, r, fill='none', stroke=PHAG, w=1.4, dash='3 1.6')
    line(doc, cx - 18, cy - 18, 236, 262, PHAG, 0.5, dash='2 1.4')
    line(doc, cx - 18, cy + 18, 236, 340, PHAG, 0.5, dash='2 1.4')
    annot.step(doc, cx - 12, cy - r - 4, '2.1', PHAG, 3.4)


def cell(doc):
    cellmod.draw_cell(doc)
    cellmod3.draw_extras(doc)
    annot.draw_annotations(doc)
    contact_site(doc)


def header(doc):
    panels_top.header(doc)


def left_column(doc):
    panels_left.intro(doc)
    panels_left.recognition(doc)
    panels_left.signalling(doc)
    panels_left.key(doc)


def right_column(doc):
    panels_right.draw(doc)


def bottom_strip(doc):
    panels_bottom.rab_snare(doc)
    panels_bottom.killing(doc)
    panels_bottom.conclusion(doc)


def footer(doc):
    panels_bottom.footer(doc)
