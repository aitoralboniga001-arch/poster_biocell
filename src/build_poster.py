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



def build(mode='poster', state_overrides=None):
    import cellmod, cellmod2, cellmod3, annot2, lenses, scene, stage, wallgeom
    doc = Doc(1100, 900, mode=mode, state_overrides=state_overrides)
    ov = doc.state_overrides
    need_wall = ('fibrosis_wall' in ov and ov['fibrosis_wall'] != 3) or ('alveolar_lumen' in ov and ov['alveolar_lumen'] != 0)
    need_out = ('pseudopod_arms' in ov and ov['pseudopod_arms'] != 1) or ('asbestos_hood' in ov and ov['asbestos_hood'] != 1)
    if need_wall:
        wallgeom.set_wall_state(fib_state=ov.get('fibrosis_wall', 3), lumen_state=ov.get('alveolar_lumen', 0))
    if need_out:
        cellmod.set_outline_state(arms_state=ov.get('pseudopod_arms', 1), hood_state=ov.get('asbestos_hood', 1))
    try:
        with actor(doc, 'fibrosis_wall', pivot=(890, 795), bbox=(680, 735, 410, 105), zone='zone_g', states=5, rest_state=3, skip_in_plate=False):
            pass
        with actor(doc, 'alveolar_lumen', pivot=(380, 775), bbox=(15, 735, 720, 105), zone='wall', states=2, rest_state=0, skip_in_plate=False):
            pass
        with actor(doc, 'pseudopod_arms', pivot=(125, 395), bbox=(10, 220, 210, 350), zone='zone_a', states=4, rest_state=1, skip_in_plate=False):
            pass
        with actor(doc, 'asbestos_hood', pivot=(955, 735), bbox=(875, 675, 165, 95), zone='zone_g', states=3, rest_state=1, skip_in_plate=False):
            pass
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
    finally:
        if need_wall:
            wallgeom.set_wall_state(3, 0)
        if need_out:
            cellmod.set_outline_state(1, 1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'Macrophage_poster.svg'))
    a = ap.parse_args()
    d = build()
    open(a.out, 'w', encoding='utf-8').write(d.render('Macrophages: phagocytosis, lysosomal biogenesis and vesicular trafficking'))
    print('wrote', a.out, os.path.getsize(a.out) // 1024, 'KB')
