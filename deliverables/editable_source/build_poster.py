"""Macrophage poster generator.  python build_poster.py  ->  ../Macrophage_poster.svg
Canvas 1100 x 900 units (1 unit = 1 mm -> 110 x 90 cm)."""
import math, random, sys, os
from lib import *
from bio import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    import cellmod2, cellmod3, annot2, layout2 as L, lenses as N
    doc = Doc(1100, 900)
    N.paper(doc)
    cellmod2.draw_cell(doc)
    cellmod3.draw_extras(doc)
    N.contact_site(doc)
    annot2.draw_annotations(doc)
    L.header(doc)
    N.intro(doc)
    ey = N.recognition(doc)
    N.pathology(doc)
    L.key(doc, 618)
    N.fusion(doc)
    N.killing(doc)
    L.conclusion(doc)
    N.flows(doc, ey)
    L.footer(doc)
    return doc


if __name__ == '__main__':
    d = build()
    out = os.path.join(ROOT, 'Macrophage_poster.svg')
    open(out, 'w', encoding='utf-8').write(d.render('Macrophages: phagocytosis, lysosomal biogenesis and vesicular trafficking'))
    print('wrote', out, os.path.getsize(out) // 1024, 'KB')
