"""Seed points for the life under the loupe (Living_poster_v3/data/life.js).

python src/export_life.py      (after build_v3_assets.py and export_paths.py: it reads poster.jpg and geom.js)

The poster is classified on a jittered grid: open cytosol (inside the cell, peach, nothing drawn nearby), open air
(outside the cell, above the alveolar wall, away from the title / legend / locator) and septal tissue.  Only quiet
spots are kept, so the drifting particles never sit on an organelle or a label.
"""
import json, os, random, sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LP = os.path.join(ROOT, 'Living_poster_v3')
OUT = os.path.join(LP, 'data', 'life.js')


def load_geom():
    s = open(os.path.join(LP, 'data', 'geom.js'), encoding='utf-8').read()
    return json.loads(s[s.index('{'):s.rindex('}') + 1])


def inside(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def main():
    g = load_geom()
    im = Image.open(os.path.join(LP, 'assets', 'poster.jpg')).convert('RGB')     # the rest composite, actors included
    k = im.size[0] / 1100.0
    rgb = np.asarray(im, np.float32)
    # local busyness: a max-min range over ~3 mm, so lines and small drawings count as "busy"
    lum = im.convert('L')
    rad = max(3, int(round(3.0 * k)) | 1)
    busy = np.asarray(lum.filter(ImageFilter.MaxFilter(rad)), np.float32) - np.asarray(lum.filter(ImageFilter.MinFilter(rad)), np.float32)
    H, W = busy.shape
    wt = dict((int(x), y) for x, y in g['wallTop'])

    def wall_top(x):
        xs = sorted(wt)
        for a, b in zip(xs, xs[1:]):
            if a <= x <= b:
                return wt[a] + (wt[b] - wt[a]) * (x - a) / (b - a)
        return wt[xs[-1]]

    zones = g['zones']
    keep_out = [zones['title'], zones['loc'], [870, 15, 1100, 105]]     # title, locator sketch, legend
    cell = g['cell']
    rnd = random.Random(11)
    out = {'cyto': [], 'air': [], 'tissue': []}
    step = {'cyto': 9.0, 'air': 11.0, 'tissue': 12.0}

    def px(x, y):
        return min(W - 1, max(0, int(x * k))), min(H - 1, max(0, int(y * k)))

    for kind, s in step.items():
        y = 4.0
        while y < 880:
            x = 4.0
            while x < 1096:
                jx, jy = x + rnd.uniform(-s * 0.4, s * 0.4), y + rnd.uniform(-s * 0.4, s * 0.4)
                X, Y = px(jx, jy)
                r, gg, b = rgb[Y, X]
                quiet = busy[Y, X] < 14
                inc = inside(cell, jx, jy)
                wy = wall_top(jx)
                if kind == 'cyto':
                    ok = inc and quiet and r > 238 and 10 < r - b < 48 and b <= gg <= r
                elif kind == 'air':
                    ok = (not inc) and quiet and jy < wy - 4 and not any(z[0] <= jx <= z[2] and z[1] <= jy <= z[3] for z in keep_out)
                else:
                    ok = (not inc) and wy + 4 < jy < 860 and busy[Y, X] < 40
                if ok:
                    out[kind].append([round(jx, 1), round(jy, 1)])
                x += s
            y += s
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('window.LIFE = ' + json.dumps(out, separators=(',', ':')) + ';\n')
    print('wrote', OUT, {k: len(v) for k, v in out.items()})


if __name__ == '__main__':
    main()
