"""Macrophage poster generator (V1.2).  python build_poster.py [--out PATH]  (default ../Macrophage_poster.svg)
Canvas 1100 x 900 units (1 unit = 1 mm -> 110 x 90 cm).

Draw order: paper -> scene (air space + alveolar wall) -> the cell (one transform group, see cellmod.CELL_S/T)
-> modules (m_*) -> header / intro / conclusion / references."""
import argparse, os
from lib import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    import cellmod, cellmod2, cellmod3, annot2, lenses, scene, stage
    import m_recognition, m_vesicles, m_m6p, m_patho
    doc = Doc(1100, 900)
    lenses.paper(doc)
    scene.draw(doc)
    group(doc, transform=cellmod.cell_transform())
    cellmod2.draw_cell(doc)
    cellmod3.draw_extras(doc)
    annot2.draw_annotations(doc)
    endgroup(doc)
    m_recognition.draw(doc)
    m_vesicles.draw(doc)
    m_m6p.draw(doc)
    m_patho.draw(doc)
    stage.header(doc)
    stage.intro(doc)
    stage.conclusion(doc)
    stage.references(doc)
    return doc


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'Macrophage_poster.svg'))
    a = ap.parse_args()
    d = build()
    open(a.out, 'w', encoding='utf-8').write(d.render('Macrophages: phagocytosis, lysosomal biogenesis and vesicular trafficking'))
    print('wrote', a.out, os.path.getsize(a.out) // 1024, 'KB')
