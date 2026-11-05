"""Export the poster geometry the living poster animates along (poster mm) to Living_poster_v3/data/geom.js."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom as G
import geom_v2 as V
import wallgeom as WG
from lib import resample
import random
import cellmod2 as C2


def microtubules():
    """The same rays cellmod2.microtubules() draws (same seeded random sequence): [centre, mid, tip] each."""
    cx, cy = C2.CENTRO
    rnd = random.Random(4)
    out = []
    for (tx, ty) in [(330, 420), (300, 520), (380, 560), (470, 610), (560, 600), (700, 520), (860, 300), (900, 420),
                     (760, 160), (640, 470), (230, 600), (420, 700)]:
        rnd.uniform(-18, 18), rnd.uniform(-18, 18)
        tx, ty = cx + (tx - cx) * 0.62, cy + (ty - cy) * 0.62
        mx, my = (cx + tx) / 2 + rnd.uniform(-10, 10), (cy + ty) / 2 + rnd.uniform(-10, 10)
        out.append([[cx, cy], [round(mx, 2), round(my, 2)], [round(tx, 2), round(ty, 2)]])
    return out

OUT = os.path.join(os.path.dirname(HERE), 'Living_poster_v3', 'data', 'geom.js')


def r2(pts, step=None, closed=False):
    if step:
        pts = resample(list(pts), step, closed=closed)
    return [[round(x, 2), round(y, 2)] for x, y in pts]


def main():
    caps = [[round(cx, 2), round(WG.surface(cx) + WG.BM_D + 0.25 + ry, 2), rx, ry] for cx, rx, ry in WG.SEPT_CAPS]
    d = {
        'cell': r2(G.CELL_OUTLINE, 2.0, closed=True),
        'lead': r2(G.LEAD_MEM_DENSE, 1.5),
        'right': r2(G.RIGHT_MEM_DENSE, 1.5),
        'red': r2(V.RED_ROUTE),
        'blue': r2(V.BLUE_ROUTE),
        'wallTop': [[x, round(WG.wall_top(x), 2)] for x in range(-10, 1121, 8)],
        'wallBot': [[x, round(WG.wall_bottom(x), 2)] for x in range(-10, 1121, 8)],
        'caps': caps,
        'cupUpper': r2(G.CUP_UPPER_LIP, 1.5),
        'cupPocket': r2(G.CUP_POCKET, 1.5),
        'cupLower': r2(G.CUP_LOWER_LIP, 1.5),
        'cupUpperTip': list(G.CUP_UPPER_TIP), 'cupLowerTip': list(G.CUP_LOWER_TIP),
        'fibre': [list(p) for p in V.ASB_FIBRE], 'fibreW': V.ASB_FIBRE_W,
        'bact': list(V.BACT), 'nascent': list(V.NASCENT), 'early': list(V.EARLY), 'late': list(V.LATE),
        'phago': [622, 665, 64], 'silica': list(V.SILICA_PL), 'nucleus': list(V.NUCLEUS),
        'bands': {k: list(v) for k, v in V.BANDS.items()},
        'zones': {'A': list(V.ZONE_A), 'D': list(V.ZONE_D), 'E': list(V.ZONE_E), 'F': list(V.ZONE_F),
                  'airR': list(V.AIR_RIGHT), 'loc': list(V.LOCATOR), 'title': list(V.TITLE_BOX)},
        'lysoDock': list(G.LYSO_DOCKING), 'lysoDeliver': list(G.LYSO_DELIVER),
        'earlyEndo': [list(e) for e in G.EARLY_ENDOSOMES],
        'copii': [list(c) for c in G.COPII_VESICLES],
        'centro': list(G.CENTROSOME),
        'conclY': V.CONCL_Y,
        'mts': microtubules(),
        'mitos': [list(m[:5]) for m in C2.MITOS],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('window.GEOM = ' + json.dumps(d, separators=(',', ':')) + ';\n')
    print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()
