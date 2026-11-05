"""Thin dashed grey stand-ins for the zone modules (V2 skeleton phase).  build_poster calls draw(doc) while the zone
modules are switched off; each zone owner's module replaces its own outline."""
from lib import *
import geom_v2 as V

GREY = '#8F8A80'


def _box(doc, b, name, dy=5.5):
    x0, y0, x1, y1 = b
    rect(doc, x0, y0, x1 - x0, y1 - y0, fill='none', stroke=GREY, sw=0.4, dash='2.4 2.0', op=0.7)
    T(doc, x0 + 2.5, y0 + dy, name, size=4.4, fill=GREY, italic=True)


def _circle(doc, c, name):
    x, y, r = c
    circ(doc, x, y, r, fill='none', stroke=GREY, w=0.4, dash='2.4 2.0', op=0.7)
    T(doc, x, y + 1.5, name, size=4.4, fill=GREY, italic=True, anchor='middle')


def draw(doc):
    _box(doc, V.ZONE_A, 'ZONE_A  2 Recognition')
    bx, by, br, bh = V.BACT
    rect(doc, bx - br, by - bh, 2 * br, 2 * bh, fill='none', stroke=GREY, sw=0.4, r=br, dash='2.4 2.0', op=0.7)
    T(doc, bx, by, 'BACT', size=4.4, fill=GREY, italic=True, anchor='middle')
    _box(doc, V.ZONE_D, 'ZONE_D  3 Lysosome biogenesis')
    for name, b in V.BANDS.items():
        _box(doc, b, name, dy=5.0)
    _box(doc, V.ZONE_E, 'ZONE_E  4 Fusion + 2.7 Killing')
    _circle(doc, V.PHAGOLYSOSOME, 'PHAGOLYSOSOME 2.6')
    _box(doc, V.ZONE_F, 'ZONE_F  5 Silica / NLRP3')
    _circle(doc, V.SILICA_PL, 'SILICA_PL')
    (x0, y0), (x1, y1) = V.ASB_FIBRE
    path(doc, 'M%s,%s L%s,%s' % (fmt(x0), fmt(y0), fmt(x1), fmt(y1)), stroke=GREY, w=V.ASB_FIBRE_W, dash='3 2', op=0.45)
    T(doc, x0 + 14, y0 - 4, 'ASB_FIBRE (zone G)', size=4.4, fill=GREY, italic=True)
    _box(doc, V.AIR_RIGHT, 'AIR_RIGHT')
    _box(doc, V.LOCATOR, 'LOCATOR  1')
