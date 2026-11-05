"""Hand-made marks (V2): section marks, inked lines and circles, painted brush strokes.

Zone owners call only section(doc, x, y, num, name, color, size=13, anchor='start').
The other helpers (ink, ink_circle, brush, hand, badge) are shared by the stage furniture."""
import math, random
from lib import fmt, esc, cr_sample, resample, normals, blob_pts, cr_path
from style import mix

HAND = "Gabriola,'Segoe Print',serif"              # display hand for section names and organelle names
BANNER = "'Sitka Banner','Sitka Display',Georgia,serif"
SWASH = "font-feature-settings:'ss07'"
INKC = '#1E2433'
PAPER_HALO = '#F8F3E8'

COLORS = {1: '#1E2433', 2: '#C0392B', '2.7': '#C0392B', 3: '#1F58C8', 4: '#7A3FB5', 5: '#B4690E', 6: '#1E9B6B'}


def color_of(num):
    k = str(num)
    for key, c in COLORS.items():
        if str(key) == k:
            return c
    try:
        return COLORS.get(int(float(k)), INKC)
    except ValueError:
        return INKC


def _txt(s):
    """Escape plain text; pass through strings that already carry markup or entities."""
    return s if ('<tspan' in s or '&' in s and ';' in s) else esc(s)


# ----------------------------------------------------------------------------------------------- ink
def _wave(rnd, comps):
    """1-D smooth noise along arc length: sum of sines (wavelength mm, amplitude)."""
    ph = [(lam, a, rnd.uniform(0, 2 * math.pi)) for lam, a in comps]
    return lambda s: sum(a * math.sin(2 * math.pi * s / lam + p) for lam, a, p in ph)


def ink_poly(pts, w=0.6, seed=0, closed=False, smooth=True, wobble=0.22, var=0.35, taper=(0.18, 0.3), step=0.35,
             w_end=0.25):
    """Outline polygon of a wobbly, pressure-varying pen stroke along pts."""
    rnd = random.Random(seed)
    line = cr_sample(pts, closed=False, per=10) if (smooth and len(pts) > 2) else list(pts)
    line = resample(line, step, closed=False)
    if len(line) < 3:
        line = list(pts)
    L = [0.0]
    for i in range(1, len(line)):
        L.append(L[-1] + math.hypot(line[i][0] - line[i - 1][0], line[i][1] - line[i - 1][1]))
    tot = L[-1] or 1.0
    j = _wave(rnd, [(5.5, 0.35), (13, 0.45), (29, 0.6)])
    pv = _wave(rnd, [(4.0, 0.3), (11, 0.5), (23, 0.5)])
    nm = normals(line, closed=False)
    left, right = [], []
    t0, t1 = taper
    for p, n, s in zip(line, nm, L):
        u = s / tot
        f = 1.0
        if t0 > 0 and u < t0:
            f = w_end + (1 - w_end) * math.sin(0.5 * math.pi * u / t0)
        if t1 > 0 and u > 1 - t1:
            f = min(f, w_end + (1 - w_end) * math.sin(0.5 * math.pi * (1 - u) / t1))
        ww = max(0.04, w * f * (1 + var * pv(s)) / 2)
        off = wobble * j(s)
        cx, cy = p[0] + n[0] * off, p[1] + n[1] * off
        left.append((cx + n[0] * ww, cy + n[1] * ww))
        right.append((cx - n[0] * ww, cy - n[1] * ww))
    return left + right[::-1]


def _d(poly):
    return 'M' + 'L'.join('%s,%s' % (fmt(x), fmt(y)) for x, y in poly) + 'Z'


def ink(doc, pts, w=0.6, color=INKC, seed=0, op=None, **kw):
    """A hand-inked line (filled outline, so it prints crisp): wobbly, tapered, pressure-varying."""
    poly = ink_poly(pts, w, seed, **kw)
    a = (' opacity="%s"' % fmt(op)) if op is not None else ''
    doc.add('<path d="%s" fill="%s"%s/>' % (_d(poly), color, a))


def ink_d(pts, w=0.6, seed=0, **kw):
    return _d(ink_poly(pts, w, seed, **kw))


def circle_pts(cx, cy, r, seed=0, turns=1.08, start=None, squash=0.05, wob=0.035, n=None):
    """Points of a pen-drawn circle: starts at `start` (deg), runs `turns` times round, slightly elliptic and tilted,
    radius drifting so the two ends overlap without meeting."""
    rnd = random.Random(seed)
    a0 = math.radians(start if start is not None else rnd.uniform(-160, -100))
    tilt = rnd.uniform(0, math.pi)
    n = n or max(28, int(2 * math.pi * r * turns / 0.5))
    j = _wave(rnd, [(2.1, 0.5), (3.3, 0.5)])
    out = []
    for i in range(n + 1):
        t = i / n
        a = a0 + 2 * math.pi * turns * t
        rr = r * (1 + wob * j(t * 6.0) + 0.045 * (t - 0.5))
        x, y = rr * math.cos(a) * (1 + squash), rr * math.sin(a) * (1 - squash)
        out.append((cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)))
    return out


def ink_circle(doc, cx, cy, r, color=INKC, w=0.5, seed=0, turns=1.08, op=None):
    ink(doc, circle_pts(cx, cy, r, seed, turns), w=w, color=color, seed=seed + 1, smooth=False, wobble=0.06, var=0.45,
        taper=(0.25, 0.2), w_end=0.15, op=op)


def hand(doc, x, y, s, size=8, fill=INKC, anchor='start', swash=False, halo=None, op=None, extra='', spacing=None,
         family=HAND, style=''):
    """Text in the display hand (Gabriola).  s may contain tspans (pre-escaped)."""
    a = ''
    st = (SWASH + ';' if swash else '') + style
    if st:
        a += ' style="%s"' % st
    if halo:
        a += (' stroke="%s" stroke-width="%s" stroke-opacity="0.8" stroke-linejoin="round" paint-order="stroke"'
              % (halo, fmt(size * 0.16)))
    if op is not None:
        a += ' opacity="%s"' % fmt(op)
    if spacing is not None:
        a += ' letter-spacing="%s"' % fmt(spacing)
    doc.add('<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" text-anchor="%s"%s%s>%s</text>'
            % (fmt(x), fmt(y), family, fmt(size), fill, anchor, a, extra, s))


# ----------------------------------------------------------------------------------------------- brush
def brush(doc, pts, w, color, seed=0, op=0.85, dry=0.55, head=None, passes=2, dash=None):
    """A painted brush stroke along pts: a tapered body of a couple of translucent passes plus dry-brush streaks
    (paper showing through).  head=size draws a painted arrowhead at the end.  dash=(on, off) mm paints dabs."""
    rnd = random.Random(seed)
    line = cr_sample(pts, closed=False, per=10) if len(pts) > 2 else list(pts)
    segs = [line]
    if dash:
        on, off = dash
        seq = resample(line, 0.3, closed=False)
        segs, cur, acc, drawing = [], [], 0.0, True
        for i, p in enumerate(seq):
            if drawing:
                cur.append(p)
            if i:
                acc += math.hypot(p[0] - seq[i - 1][0], p[1] - seq[i - 1][1])
            if acc >= (on if drawing else off):
                if drawing and len(cur) > 1:
                    segs.append(cur)
                cur, acc, drawing = [], 0.0, not drawing
        if drawing and len(cur) > 1:
            segs.append(cur)
    for k, sg in enumerate(segs):
        sd = seed * 13 + k * 7
        for p in range(passes):
            poly = ink_poly(sg, w * (1 - 0.18 * p), sd + p, smooth=False, wobble=0.12 * w, var=0.22,
                            taper=(0.12, 0.3) if not dash else (0.3, 0.35), w_end=0.35 if not dash else 0.45, step=0.3)
            doc.add('<path d="%s" fill="%s" opacity="%s"/>' % (_d(poly), color, fmt(op * (0.62 if p == 0 else 0.55))))
        if dry and not dash:
            # dry-brush streaks: thin paper-coloured lines running with the stroke, broken toward the tail
            base = resample(sg, 0.3, closed=False)
            nm = normals(base, closed=False)
            for q in range(3):
                off = rnd.uniform(-0.33, 0.33) * w
                i0 = int(len(base) * rnd.uniform(0.35, 0.7))
                seg = [(p[0] + n[0] * off, p[1] + n[1] * off) for p, n in zip(base[i0:], nm[i0:])]
                if len(seg) > 3:
                    ink(doc, seg, w=w * rnd.uniform(0.05, 0.11), color=PAPER_HALO, seed=sd + q, smooth=False,
                        wobble=0.02 * w, taper=(0.4, 0.1), op=dry)
    if head:
        (x0, y0), (x1, y1) = line[-2], line[-1]
        a = math.atan2(y1 - y0, x1 - x0)
        ca, sa = math.cos(a), math.sin(a)
        L, Wd = head, head * 0.55
        tip = (x1 + ca * L * 0.6, y1 + sa * L * 0.6)
        b1 = (x1 - ca * L * 0.4 - sa * Wd, y1 - sa * L * 0.4 + ca * Wd)
        b2 = (x1 - ca * L * 0.4 + sa * Wd, y1 - sa * L * 0.4 - ca * Wd)
        mid = (x1 - ca * L * 0.05, y1 - sa * L * 0.05)
        for p in range(2):
            jit = [(px + rnd.uniform(-1, 1) * head * 0.04, py + rnd.uniform(-1, 1) * head * 0.04) for px, py in (b1, tip, b2, mid)]
            doc.add('<path d="M%s,%sL%s,%sL%s,%sQ%s,%s %s,%sZ" fill="%s" opacity="%s"/>' % (
                fmt(jit[0][0]), fmt(jit[0][1]), fmt(jit[1][0]), fmt(jit[1][1]), fmt(jit[2][0]), fmt(jit[2][1]),
                fmt(jit[3][0]), fmt(jit[3][1]), fmt(jit[0][0]), fmt(jit[0][1]), color, fmt(op * 0.6)))


# ----------------------------------------------------------------------------------------------- section mark
def badge(doc, cx, cy, r, color, label, seed=0, numeral='#FFFFFF', wash=True):
    """Hand-inked circle with a watercolour fill and a numeral."""
    import texture
    lab = str(label)
    if wash:
        d = cr_path(blob_pts(cx + r * 0.05, cy + r * 0.06, r * 1.04, r * 1.0, n=9, j=0.05, seed=seed + 5), True)
        texture.wash(doc, d, [color, mix(color, '#FFFFFF', 0.22), mix(color, '#000000', 0.12)], seed=seed, ppm=12,
                     strength=1.45, edge=1.2, grain=1.2, inset=0.2, wobble=0.6, clip=False)
    ink_circle(doc, cx, cy, r * 1.04, color=mix(color, '#000000', 0.35), w=max(0.35, r * 0.11), seed=seed + 2)
    small = len(lab) > 1
    fs = r * (1.05 if small else 1.5)
    dy = r * (0.36 if small else 0.5)
    doc.add('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="600" font-style="italic" fill="%s" '
            'text-anchor="middle" letter-spacing="%s">%s</text>'
            % (fmt(cx - r * 0.03), fmt(cy + dy), BANNER, fmt(fs), numeral, fmt(-0.04 * fs if small else 0), esc(lab)))


def section(doc, x, y, num, name, color, size=13.0, anchor='start'):
    """Number in a hand-inked, watercolour-filled circle + name in Gabriola; (x, y) = baseline start of the mark
    (baseline end when anchor='end')."""
    r = size * 0.42
    cy = y - size * 0.21
    cx = x + r if anchor == 'start' else x - r
    seed = sum(ord(ch) for ch in str(num) + str(name)) % 997
    badge(doc, cx, cy, r, color, num, seed=seed)
    if name:
        tx = cx + r + size * 0.32 if anchor == 'start' else cx - r - size * 0.32
        hand(doc, tx, y, _txt(name), size=size, fill=mix(color, '#000000', 0.12), anchor=anchor, halo=PAPER_HALO)
