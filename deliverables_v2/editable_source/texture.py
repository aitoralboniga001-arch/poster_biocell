"""Procedural painted textures (V2), embedded as data-URI raster images.

paper(doc)                       warm cotton paper + watercolour blooms in the alveolar air (one JPEG, ~2 px/mm)
wash(doc, d, colors, seed, ...)  watercolour wash clipped to an SVG path (RGBA PNG), for use inside the cell
All textures are soft, so they are generated at low resolution and scaled up by the renderer."""
import base64, io, math, re
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, zoom
from lib import fmt

PAPER_RGB = (247, 241, 229)          # warm cotton
_cache = {}


# ----------------------------------------------------------------------------------------------- noise
def _rgb(c):
    if isinstance(c, str):
        c = c.lstrip('#')
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(c)


def _field(h, w, cell, rng, order=3):
    """Smooth value noise with feature size ~cell px, zero mean, unit std."""
    gh, gw = max(3, int(math.ceil(h / cell)) + 3), max(3, int(math.ceil(w / cell)) + 3)
    g = rng.standard_normal((gh, gw))
    f = zoom(g, (h / (gh - 3) * 1.0, w / (gw - 3) * 1.0), order=order, mode='reflect')[:h, :w]
    if f.shape != (h, w):
        f = np.pad(f, ((0, h - f.shape[0]), (0, w - f.shape[1])), mode='edge')
    f -= f.mean()
    return f / (f.std() + 1e-9)


def _fbm(h, w, cell, rng, octaves=4, gain=0.5):
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(1.5, cell / (2 ** o))
        out += amp * _field(h, w, c, rng)
        tot += amp
        amp *= gain
    return out / tot


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _uri(img, kind='jpeg', q=86):
    buf = io.BytesIO()
    if kind == 'jpeg':
        img.convert('RGB').save(buf, 'JPEG', quality=q, optimize=True, subsampling=0)
        mime = 'image/jpeg'
    else:
        img.save(buf, 'PNG', optimize=True)
        mime = 'image/png'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(buf.getvalue()).decode('ascii'))


def _pool(dens, sigma, k):
    """Watercolour edge darkening: pigment collects where the wet area ends."""
    return dens + k * np.clip(dens - gaussian_filter(dens, sigma), 0, None)


def _paint(rgb, dens, col):
    """Subtractive (multiply-like) glaze of colour col with density dens (0..1)."""
    c = np.array(_rgb(col), dtype=float) / 255.0
    d = np.clip(dens, 0, 1)[..., None]
    return rgb * (1 - d * (1 - c))


# ----------------------------------------------------------------------------------------------- paper
def _paper_img(W=1100, H=900, ppm=2.0, seed=7):
    h, w = int(H * ppm), int(W * ppm)
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w] / ppm                  # mm
    rgb = np.ones((h, w, 3)) * (np.array(PAPER_RGB) / 255.0)

    # cotton mottling + fine grain + a few long fibres
    mott = _fbm(h, w, 70 * ppm, rng, octaves=3)
    rgb *= (1 + 0.010 * mott)[..., None]
    grain = gaussian_filter(rng.standard_normal((h, w)), 0.55)
    grain /= grain.std()
    rgb *= (1 + 0.016 * grain)[..., None]
    fib = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(fib)
    for _ in range(2600):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(2, 9) * ppm
        bend = rng.uniform(-0.25, 0.25)
        pts = [(x + math.cos(a + bend * t) * L * t, y + math.sin(a + bend * t) * L * t) for t in np.linspace(0, 1, 5)]
        dr.line(pts, fill=int(rng.uniform(60, 160)), width=1)
    fib = gaussian_filter(np.asarray(fib, float) / 255.0, 0.45)
    light = fib * (rng.uniform(size=(h, w)) > 0.5)
    rgb = rgb * (1 - 0.05 * (fib - light))[..., None] + 0.05 * light[..., None]

    # ------------------------------------------------ the air: inside one alveolus
    air = 1 - _smooth(yy, 735, 800)                        # fades out behind the septum
    cx, cy = 560, 430
    rad = np.sqrt(((xx - cx) / 640) ** 2 + ((yy - cy) / 470) ** 2)
    corner = _smooth(rad, 0.55, 1.25)                      # darker toward the corners, like the alveolar wall curving round
    layers = [  # colour, feature mm, threshold, strength, seed offset
        ('#C6D6E1', 260, -0.35, 0.34, 1),   # cool blue, broad
        ('#E6D9BC', 200, 0.20, 0.26, 2),    # cream
        ('#C8CADB', 230, 0.35, 0.26, 3),    # blue-grey lilac
        ('#AFC4D4', 150, 0.75, 0.28, 4),    # deeper blue pools toward the corners
    ]
    for col, feat, thr, k, so in layers:
        r2 = np.random.default_rng(seed * 31 + so)
        f = _fbm(h, w, feat * ppm, r2, octaves=3, gain=0.38) + 1.6 * corner - 0.45
        wet = _smooth(f, thr, thr + 0.14)
        wet = gaussian_filter(wet, 0.7 * ppm)
        dens = 0.75 * _pool(wet, 4 * ppm, 1.3) + 0.25 * gaussian_filter(_smooth(f, thr - 0.5, thr + 0.6), 3 * ppm)
        gran = gaussian_filter(r2.standard_normal((h, w)), 0.8)
        dens *= (0.86 + 0.14 * gran / (gran.std() + 1e-9))
        dens *= k * (0.25 + 0.95 * corner) * air
        rgb = _paint(rgb, dens, col)    # warm, faint glow of light from the top-left
    glow = np.exp(-(((xx - 150) / 520) ** 2 + ((yy - 40) / 360) ** 2))
    rgb = rgb + (np.array([1.0, 0.985, 0.95]) - rgb) * (0.35 * glow)[..., None]
    # a soft warm wash under the septum, where the conclusion and references sit
    low = _smooth(yy, 820, 900)
    rgb = _paint(rgb, 0.10 * low * (0.8 + 0.2 * mott), '#E3D3B5')
    img = Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8), 'RGB')
    return img


PAPER_VERSION = 3        # bump when _paper_img changes (invalidates the on-disk cache)


def paper(doc, ppm=2.0, seed=7):
    """Full-sheet painted paper.  The JPEG is cached in src/_texcache (takes ~20 s to generate)."""
    import os
    key = ('paper', ppm, seed)
    if key not in _cache:
        cdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_texcache')
        fn = os.path.join(cdir, 'paper_v%d_%s_%d_%dx%d.jpg' % (PAPER_VERSION, fmt(ppm), seed, doc.w, doc.h))
        if not os.path.exists(fn):
            os.makedirs(cdir, exist_ok=True)
            _paper_img(doc.w, doc.h, ppm, seed).save(fn, 'JPEG', quality=84, optimize=True, subsampling=0)
        _cache[key] = 'data:image/jpeg;base64,' + base64.b64encode(open(fn, 'rb').read()).decode('ascii')
    doc.add('<rect x="0" y="0" width="%d" height="%d" fill="#F7F1E5"/>' % (doc.w, doc.h))
    doc.add('<image x="0" y="0" width="%d" height="%d" preserveAspectRatio="none" href="%s"/>' % (doc.w, doc.h, _cache[key]))


# ----------------------------------------------------------------------------------------------- path -> polygons
_TOK = re.compile(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')
_NARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7, 'Z': 0}


def path_polys(d, n=10):
    """Flatten an SVG path string into a list of closed polygons (lists of (x, y))."""
    toks = _TOK.findall(d)
    polys, cur = [], []
    x = y = sx = sy = 0.0
    lc = None   # last control point
    cmd = None
    i = 0

    def bez(p0, p1, p2, p3):
        return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
                 (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1])
                for t in np.linspace(0, 1, n + 1)[1:]]

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in 'Zz':
                if cur:
                    polys.append(cur)
                cur = []
                x, y = sx, sy
                continue
        rel = cmd.islower()
        C = cmd.upper()
        k = _NARGS[C]
        a = [float(v) for v in toks[i:i + k]]
        i += k
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if C == 'M':
            if cur:
                polys.append(cur)
            x, y = a[0] + ox, a[1] + oy
            sx, sy = x, y
            cur = [(x, y)]
            cmd = 'l' if rel else 'L'
            lc = None
        elif C == 'L':
            x, y = a[0] + ox, a[1] + oy
            cur.append((x, y)); lc = None
        elif C == 'H':
            x = a[0] + ox; cur.append((x, y)); lc = None
        elif C == 'V':
            y = a[0] + oy; cur.append((x, y)); lc = None
        elif C == 'C':
            p1, p2, p3 = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy), (a[4] + ox, a[5] + oy)
            cur += bez((x, y), p1, p2, p3); lc = p2; x, y = p3
        elif C == 'S':
            p1 = (2 * x - lc[0], 2 * y - lc[1]) if lc else (x, y)
            p2, p3 = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy)
            cur += bez((x, y), p1, p2, p3); lc = p2; x, y = p3
        elif C == 'Q':
            q, p3 = (a[0] + ox, a[1] + oy), (a[2] + ox, a[3] + oy)
            p1 = (x + 2 / 3 * (q[0] - x), y + 2 / 3 * (q[1] - y))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            cur += bez((x, y), p1, p2, p3); lc = None; x, y = p3
        else:   # T, A: straight segment to the end point (good enough for a wash mask)
            x, y = a[-2] + ox, a[-1] + oy
            cur.append((x, y)); lc = None
    if cur:
        polys.append(cur)
    return [p for p in polys if len(p) > 2]


# ----------------------------------------------------------------------------------------------- wash
def wash_img(polys, colors, bbox, ppm=3.0, seed=0, edge=1.0, grain=1.0, inset=0.35, wobble=1.0, strength=1.0):
    """RGBA watercolour wash filling polys (mm) inside bbox; returns PIL image."""
    x0, y0, x1, y1 = bbox
    w, h = max(4, int(round((x1 - x0) * ppm))), max(4, int(round((y1 - y0) * ppm)))
    rng = np.random.default_rng(seed)
    m = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(m)
    for p in polys:            # even-odd: holes punch through
        tmp = Image.new('L', (w, h), 0)
        ImageDraw.Draw(tmp).polygon([((px - x0) * ppm, (py - y0) * ppm) for px, py in p], fill=255)
        m = Image.fromarray(np.bitwise_xor(np.asarray(m), np.asarray(tmp)))
    mask = np.asarray(m, float) / 255.0
    size = min(x1 - x0, y1 - y0)
    # wobbly, slightly receding wet edge
    bl = gaussian_filter(mask, max(0.6, 0.6 * ppm))
    wob = _fbm(h, w, max(3.0, size * 0.18 * ppm), rng, octaves=3)
    thr = 0.5 + 0.08 * wobble * wob + 0.12 * inset
    wet = _smooth(bl - thr + 0.5, 0.47, 0.53)
    wet = gaussian_filter(wet, 0.35 * ppm)
    # pigment density: uneven flow, granulation, pooled edges
    flow = _fbm(h, w, max(4.0, size * 0.45 * ppm), rng, octaves=3)
    dens = wet * (0.62 + 0.16 * flow)
    g = gaussian_filter(rng.standard_normal((h, w)), 0.7)
    dens *= 1 + 0.10 * grain * g / (g.std() + 1e-9)
    dens = _pool(dens, max(1.0, size * 0.06 * ppm), 1.4 * edge)
    # back-run bloom: a paler cauliflower patch with a dark rim
    if size > 12:
        bf = _fbm(h, w, max(4.0, size * 0.3 * ppm), rng, octaves=2)
        bloom = _smooth(bf, 0.9, 1.1)
        rim = np.clip(bloom - gaussian_filter(bloom, 0.8 * ppm), 0, None)
        dens = dens * (1 - 0.35 * bloom) + 0.6 * rim * wet
    dens = np.clip(dens * strength, 0, 1) * wet
    # colour: blend the given colours with large soft noise fields
    cols = [np.array(_rgb(c), float) / 255.0 for c in colors]
    if len(cols) == 1:
        rgb = np.ones((h, w, 3)) * cols[0]
    else:
        ws = [np.exp(1.6 * _fbm(h, w, max(4.0, size * 0.5 * ppm), rng, octaves=2)) for _ in cols]
        tot = sum(ws)
        rgb = sum(wk[..., None] * c for wk, c in zip(ws, cols)) / tot[..., None]
    # pigment is darker where it pools
    rgb = rgb * (1 - 0.18 * np.clip(dens - 0.6, 0, 1)[..., None] * 2)
    a = np.clip(dens, 0, 1)
    out = np.dstack([np.clip(rgb * 255, 0, 255), a * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def wash(doc, d, colors, seed=0, opacity=1.0, bbox=None, ppm=3.0, clip=True, edge=1.0, grain=1.0, blend=None,
         strength=1.0, wobble=1.0, inset=0.35):
    """Paint a watercolour wash clipped to SVG path d.  colors: one or more hex colours blended by soft noise.
    bbox (x0, y0, x1, y1) in poster mm defaults to the path bounds.  Returns the bbox used."""
    if isinstance(colors, str):
        colors = [colors]
    polys = path_polys(d)
    if bbox is None:
        xs = [p[0] for q in polys for p in q]
        ys = [p[1] for q in polys for p in q]
        bbox = (min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1)
    x0, y0, x1, y1 = bbox
    # keep the embedded image small: cap at ~1.4 Mpx
    area = (x1 - x0) * (y1 - y0)
    ppm = min(ppm, math.sqrt(1.4e6 / max(area, 1)))
    img = wash_img(polys, colors, bbox, ppm, seed, edge=edge, grain=grain, inset=inset, wobble=wobble, strength=strength)
    uri = _uri(img, 'png')
    a = ''
    if clip:
        cid = doc.uid('wc')
        doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
        a += ' clip-path="url(#%s)"' % cid
    if opacity != 1.0:
        a += ' opacity="%s"' % fmt(opacity)
    if blend:
        a += ' style="mix-blend-mode:%s"' % blend
    doc.add('<image x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="none"%s href="%s"/>'
            % (fmt(x0), fmt(y0), fmt(x1 - x0), fmt(y1 - y0), a, uri))
    return bbox
