"""Crowded cytosol (polish pass, Nov 2026): a faint Goodsell-style texture so the cytoplasm reads as a living, packed
cell rather than an empty wash.  Drawn by cellmod2.draw_cell() right after the route ribbons, under every organelle,
clipped to the cell.  Plate-only (no actor), low contrast on purpose: it must not compete with labels, and
export_life.py still has to find "quiet" cytosol for the living poster's particles.

Layers (all seeded, deterministic):
  soluble proteins  small rounded globules, some two-domain, lit from the top left (shadow down-right, tiny highlight)
  polysomes         short mRNA threads carrying a few two-subunit ribosomes
  filaments         short wavy F-actin wisps + a few long, gentle intermediate filaments (vimentin)
"""
import math, random
from lib import fmt, cr_path
import cellmod as CM

# pale tones of the poster's own palette (peach cytoplasm, rose, lavender, cobalt-grey, amber)
PROT = [('#E2A68C', 0.46), ('#D99AA0', 0.16), ('#B7A6CF', 0.15), ('#A9B6CF', 0.14), ('#DDB873', 0.09)]
import os
V13 = os.environ.get('POSTER_V13', '1') != '0'
PROT_OP = 0.21 if V13 else 0.15        # v13: crowding you can see from a metre away, still well under the labels
SHADOW, SHADOW_OP = '#B4725C', 0.06
RIBO, RIBO_OP = '#8F7FB5', (0.26 if V13 else 0.2)
MRNA = '#9A86B8'
ACTIN_W = '#C58C73'
IF_C = '#B79A8A'


def _inside_fn():
    """Point-in-cell test from a 4 px/mm raster of the outline (fast; exact enough for texture placement)."""
    from PIL import Image, ImageDraw
    k = 4
    im = Image.new('1', (1100 * k, 900 * k), 0)
    ImageDraw.Draw(im).polygon([(x * k, y * k) for x, y in CM.OUT], fill=1)
    px = im.load()

    def ins(x, y):
        X, Y = int(x * k), int(y * k)
        return 0 <= X < 1100 * k and 0 <= Y < 900 * k and px[X, Y] == 1
    return ins


def _density(x, y, ph):
    """Smooth clustered field in [0, 1]: a few crossing low-frequency waves."""
    v = 0.0
    for (kx, ky, p) in ph:
        v += math.sin(x * kx + y * ky + p)
    v = 0.5 + v / (2.0 * len(ph))
    # quieter where the leading-edge molecular scene lives (zone A) and right under the membrane
    if x < 236 and 250 < y < 545:
        v *= 0.35
    return max(0.0, min(1.0, v))


def _circle_d(x, y, r):
    return 'M%s,%sa%s,%s 0 1,0 %s,0a%s,%s 0 1,0 %s,0' % (fmt(x - r), fmt(y), fmt(r), fmt(r), fmt(2 * r), fmt(r), fmt(r), fmt(-2 * r))


def proteins(doc, ins, rnd):
    ph = [(rnd.uniform(0.012, 0.03) * rnd.choice((-1, 1)), rnd.uniform(0.012, 0.03) * rnd.choice((-1, 1)), rnd.uniform(0, 6.3))
          for _ in range(4)]
    shapes = {c: [] for c, _ in PROT}
    shadows, highs = [], []
    cols = [c for c, _ in PROT]
    wts = [w for _, w in PROT]
    n = 0
    tries = 0
    while n < 15000 and tries < 60000:
        tries += 1
        x, y = rnd.uniform(150, 1006), rnd.uniform(112, 760)
        d = _density(x, y, ph)
        if rnd.random() > 0.12 + 0.88 * d * d:
            continue
        if not ins(x, y):
            continue
        n += 1
        r = min(1.5, 0.36 + rnd.expovariate(2.9))
        c = rnd.choices(cols, wts)[0]
        lobes = [(x, y, r)]
        if r > 0.8 and rnd.random() < 0.45:          # two-domain protein
            a = rnd.uniform(0, 6.283)
            lobes.append((x + math.cos(a) * r * 0.85, y + math.sin(a) * r * 0.85, r * rnd.uniform(0.55, 0.75)))
        for (lx, ly, lr) in lobes:
            shapes[c].append(_circle_d(lx, ly, lr))
            shadows.append(_circle_d(lx + lr * 0.32, ly + lr * 0.42, lr))
        if r > 0.95:
            highs.append(_circle_d(x - r * 0.35, y - r * 0.38, r * 0.3))
    doc.add('<path d="%s" fill="%s" opacity="%s"/>' % (''.join(shadows), SHADOW, fmt(SHADOW_OP)))
    for c, _ in PROT:
        doc.add('<path d="%s" fill="%s" opacity="%s"/>' % (''.join(shapes[c]), c, fmt(PROT_OP)))
    doc.add('<path d="%s" fill="#FFFFFF" opacity="0.45"/>' % ''.join(highs))


def polysomes(doc, ins, rnd):
    threads, ribos, small = [], [], []
    made = 0
    while made < 46:
        x, y = rnd.uniform(240, 1000), rnd.uniform(130, 750)
        if not ins(x, y):
            continue
        made += 1
        a = rnd.uniform(0, 6.283)
        pts = [(x, y)]
        for k in range(4):
            a += rnd.uniform(-0.9, 0.9)
            pts.append((pts[-1][0] + math.cos(a) * 2.6, pts[-1][1] + math.sin(a) * 2.6))
        threads.append(cr_path(pts, False))
        for k, (px, py) in enumerate(pts[:-1]):
            if rnd.random() < 0.85:
                ribos.append(_circle_d(px + 0.4, py - 0.5, 0.72))
                small.append(_circle_d(px - 0.25, py + 0.35, 0.45))
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="0.2" stroke-linecap="round" opacity="0.3"/>'
            % (''.join(threads), MRNA))
    doc.add('<path d="%s" fill="%s" opacity="%s"/>' % (''.join(small), RIBO, fmt(RIBO_OP * 0.8)))
    doc.add('<path d="%s" fill="%s" opacity="%s"/>' % (''.join(ribos), RIBO, fmt(RIBO_OP)))


def filaments(doc, ins, rnd):
    act, inter = [], []
    made = 0
    while made < 70:
        x, y = rnd.uniform(220, 1000), rnd.uniform(130, 750)
        if not ins(x, y):
            continue
        made += 1
        a = rnd.uniform(0, 6.283)
        L = rnd.uniform(12, 34)
        pts = [(x, y)]
        for k in range(5):
            a += rnd.uniform(-0.35, 0.35)
            pts.append((pts[-1][0] + math.cos(a) * L / 5, pts[-1][1] + math.sin(a) * L / 5))
        if all(ins(px, py) for px, py in pts):
            act.append(cr_path(pts, False))
    made = 0
    while made < 16:
        x, y = rnd.uniform(260, 960), rnd.uniform(160, 720)
        if not ins(x, y):
            continue
        a = rnd.uniform(0, 6.283)
        L = rnd.uniform(70, 150)
        pts = [(x, y)]
        for k in range(7):
            a += rnd.uniform(-0.22, 0.22)
            pts.append((pts[-1][0] + math.cos(a) * L / 7, pts[-1][1] + math.sin(a) * L / 7))
        if all(ins(px, py) for px, py in pts):
            made += 1
            inter.append(cr_path(pts, False))
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="0.42" stroke-linecap="round" opacity="0.14"/>'
            % (''.join(inter), IF_C))
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="0.26" stroke-linecap="round" opacity="0.2"/>'
            % (''.join(act), ACTIN_W))


def draw(doc):
    ins = _inside_fn()
    rnd = random.Random(2026)
    doc.add('<g clip-path="url(#%s)">' % CM.cell_clip(doc))
    filaments(doc, ins, rnd)
    proteins(doc, ins, rnd)
    polysomes(doc, ins, rnd)
    doc.add('</g>')
