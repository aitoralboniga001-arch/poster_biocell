"""Macrophage poster generator (V2: one giant mixed-scale macrophage).
python build_poster.py [--out PATH]  (default ../Macrophage_poster.svg).  Canvas 1100 x 900 units (1 unit = 1 mm).

Draw order: paper -> scene air -> alveolar wall -> the cell (skeleton: cytoplasm, routes, organelles, membrane,
labels; poster mm, no transform) -> zone modules (or their placeholders) -> stage (header, intro, conclusion, refs).
"""
import argparse, os
from lib import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Zone modules: switch each on when its V2 version lands (the integrator flips these).
# NOTE: the V1 m_patho.draw() also paints scene.wall() + scene.labels(); in V2 the wall is drawn here, before the
# cell, so the V2 patho module must not draw it again.
LIVE = {'recognition': True, 'vesicles': True, 'm6p': True, 'patho': True}
PLACEHOLDERS = False         # dashed outlines of the zones while their modules are off



def build():
    import cellmod, cellmod2, cellmod3, annot2, lenses, scene, stage
    doc = Doc(1100, 900)
    lenses.paper(doc)
    scene.draw(doc)                    # air space
    scene.wall(doc)                    # alveolar septum (healthy -> fibrotic)
    scene.labels(doc)
    group(doc, transform=cellmod.cell_transform())
    cellmod2.draw_cell(doc)
    cellmod3.draw_extras(doc)
    annot2.draw_annotations(doc)
    endgroup(doc)
    if LIVE['recognition']:
        import m_recognition
        m_recognition.draw(doc)
    if LIVE['vesicles']:
        import m_vesicles
        m_vesicles.draw(doc)
    if LIVE['m6p']:
        import m_m6p
        m_m6p.draw(doc)
    if LIVE['patho']:
        import m_patho
        m_patho.draw(doc)
    if PLACEHOLDERS and not all(LIVE.values()):
        import placeholders
        placeholders.draw(doc)
    stage.header(doc)
    stage.intro(doc)                   # 1  locator sketch (LOCATOR box)
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
