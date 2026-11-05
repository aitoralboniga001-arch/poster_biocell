"""Helper library for the macrophage poster generator.
Units: 1 SVG unit = 1 mm on the final 1100 x 900 mm sheet (110 x 90 cm).
"""
import math, random, re
from PIL import ImageFont

# ---------------------------------------------------------------- palette
INK = '#1B2430'
INK2 = '#4A5563'
PAPER = '#F7F3EA'
CYTO = '#FCEFE7'
CYTO2 = '#F7DCCD'
LUMEN = '#E9F1F4'
PHAG = '#E0452B'      # phagocytic pathway
BIO = '#1F58C8'       # biosynthetic / hydrolase pathway
CONV = '#7A3FB5'      # convergence: lysosome / phagolysosome
RECY = '#1E9B6B'      # recycling
PATH = '#B4690E'      # pathology (particles)
INFL = '#C81D63'      # inflammation / ROS
M6P = '#E2B33C'   # M6P phosphate: gold (V1.2 identity colour)
HPLUS = '#19B5E8'
BACT = '#8C9A3A'

SANS = "'Segoe UI Variable Text','Segoe UI',Arial,sans-serif"
SERIF = "'Sitka Text',Georgia,serif"
COND = "'Bahnschrift','Segoe UI',Arial,sans-serif"

# Optical-size type system (both families are variable fonts shipped with Windows 11 and embed in the PDF):
#   serif  Sitka      Banner (title) / Display (headings) / Subheading / Text (narrative)
#   sans   Segoe UI Variable  Display (names) / Text (notes) / Small (tags, fine print)
# Italics are always true Sitka italics; sans bold is set semibold.
_SITKA = 'C:/Windows/Fonts/SitkaVF.ttf'
_SITKA_I = 'C:/Windows/Fonts/SitkaVF-Italic.ttf'
_SEGVAR = 'C:/Windows/Fonts/SegUIVar.ttf'
_fcache = {}


def serif_cut(size):
    return 'Banner' if size >= 16 else 'Display' if size >= 8.5 else 'Subheading' if size >= 6.8 else 'Text'


def sans_cut(size):
    return 'Display' if size >= 6.8 else 'Text' if size >= 4.4 else 'Small'


def resolve(family, size, weight, italic=False):
    """Map a generic family + size to the optical cut actually rendered. Returns (family css, weight, kind)."""
    if family == SANS and italic:
        family = SERIF
    if family == SERIF:
        return "'Sitka %s',Georgia,serif" % serif_cut(size), weight, ('seriti' if italic else 'serif')
    if family == SANS:
        return "'Segoe UI Variable %s','Segoe UI',Arial,sans-serif" % sans_cut(size), (600 if weight >= 600 else weight), 'sans'
    return family, weight, 'sans'


def _font(kind, weight, size=6):
    if kind == 'sans':
        cut = sans_cut(size)
        semi = weight >= 600
        if cut == 'Text':
            var = 'Semibold Text' if semi else 'Regular'
        else:
            var = '%s %s' % ('Semibold' if semi else 'Regular', cut)
        path = _SEGVAR
    else:
        w = 'Bold' if weight >= 700 else 'Semibold' if weight >= 600 else ''
        var = ' '.join(x for x in (serif_cut(size), w) if x)
        path = _SITKA
        if kind in ('seriti', 'sansi'):
            path, var = _SITKA_I, var + ' Italic'
    key = (path, var)
    if key not in _fcache:
        f = ImageFont.truetype(path, 100)
        f.set_variation_by_name(var)
        _fcache[key] = f
    return _fcache[key]


def text_width(s, size, weight=400, kind='sans'):
    return _font(kind, weight, size).getlength(s) * size / 100.0


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


# ---------------------------------------------------------------- svg doc
class Doc:
    def __init__(self, w=1100, h=900):
        self.w, self.h = w, h
        self.defs = []
        self.body = []
        self._n = 0

    def uid(self, p='i'):
        self._n += 1
        return '%s%d' % (p, self._n)

    def add(self, s):
        self.body.append(s)

    def lingrad(self, stops, x1=0, y1=0, x2=0, y2=1, id=None):
        id = id or self.uid('lg')
        st = ''.join('<stop offset="%s" stop-color="%s"%s/>' % (o, c, (' stop-opacity="%s"' % a) if a is not None else '')
                     for o, c, a in [(s + (None,))[:3] if len(s) == 2 else s for s in stops])
        self.defs.append('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (id, x1, y1, x2, y2, st))
        return 'url(#%s)' % id

    def radgrad(self, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, id=None):
        id = id or self.uid('rg')
        st = ''.join('<stop offset="%s" stop-color="%s"%s/>' % (o, c, (' stop-opacity="%s"' % a) if a is not None else '')
                     for o, c, a in [(s + (None,))[:3] if len(s) == 2 else s for s in stops])
        f = '' if fx is None else ' fx="%s" fy="%s"' % (fx, fy)
        self.defs.append('<radialGradient id="%s" cx="%s" cy="%s" r="%s"%s>%s</radialGradient>' % (id, cx, cy, r, f, st))
        return 'url(#%s)' % id

    def render(self, title='Macrophage poster'):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="%dmm" height="%dmm" viewBox="0 0 %d %d">\n'
                '<title>%s</title>\n<defs>\n<style>text{font-kerning:normal;font-variant-ligatures:common-ligatures;'
                'font-variant-numeric:lining-nums}</style>\n%s\n</defs>\n%s\n</svg>\n' % (
                    self.w, self.h, self.w, self.h, esc(title), '\n'.join(self.defs), '\n'.join(self.body)))


# ---------------------------------------------------------------- text
def _tok(text):
    """Tokenise markup: **bold**, ~~italic~~ ; returns list of (word, bold, italic)."""
    out = []
    bold = ital = False
    for part in re.split(r'(\*\*|~~)', text):
        if part == '**':
            bold = not bold
        elif part == '~~':
            ital = not ital
        elif part:
            out.append((part, bold, ital))
    return out


def _words(text):
    """list of (word, bold, ital, space_before)"""
    ws = []
    for seg, b, i in _tok(text):
        for k, w in enumerate(re.split(r'( +)', seg)):
            if w == '':
                continue
            if w.strip() == '':
                ws.append((None, b, i))
            else:
                ws.append((w, b, i))
    # merge: word following None gets space_before True
    res = []
    space = False
    for w, b, i in ws:
        if w is None:
            space = True
        else:
            res.append((w, b, i, space))
            space = False
    return res


def wrap(text, size, width, weight=400, kind='sans'):
    """Return list of lines; each line = list of (word,bold,ital,space_before)."""
    lines = []
    for para in text.split('\n'):
        cur, curw = [], 0
        for w, b, i, sp in _words(para):
            ww = text_width(w, size, 700 if b else weight, ('seriti' if i else kind))
            sw = text_width(' ', size, weight, kind) if (cur and sp) else 0
            if cur and curw + sw + ww > width:
                lines.append(cur)
                cur, curw = [(w, b, i, False)], ww
            else:
                cur.append((w, b, i, sp if cur else False))
                curw += sw + ww
        lines.append(cur)
    return lines


def _line_tspans(line, boldfill=None, weight=400, size=5, sans=True):
    parts = []
    for w, b, i, sp in line:
        attrs = ''
        if b:
            attrs += ' font-weight="%s"' % (600 if sans else 700)
            if boldfill:
                attrs += ' fill="%s"' % boldfill
        if i:
            attrs += ' font-style="italic"'
            if sans:
                attrs += " font-family=\"'Sitka %s',Georgia,serif\"" % serif_cut(size)
        txt = (' ' if sp else '') + esc(w)
        if (i or not sans) and '→' in txt:   # Sitka has no arrow glyph: borrow Segoe's instead of a Times fallback
            txt = txt.replace('→', "<tspan font-family=\"'Segoe UI Variable Text','Segoe UI',sans-serif\" font-style=\"normal\">→</tspan>")
        if attrs:
            parts.append('<tspan%s>%s</tspan>' % (attrs, txt))
        else:
            parts.append(txt)
    return ''.join(parts)


def T(doc, x, y, s, size=5, weight=400, fill=INK, anchor='start', family=SANS, italic=False,
      spacing=None, opacity=None, rot=None, kind='sans', extra='', halo=None):
    """Single-line text (supports ** and ~~ markup)."""
    sans = family == SANS and not italic
    family, weight, kind = resolve(family, size, weight, italic)
    a = ' font-style="italic"' if italic else ''
    if halo:
        a += ' stroke="%s" stroke-width="%s" stroke-linejoin="round" paint-order="stroke"' % (halo, fmt(size * 0.28))
    if spacing is not None:
        a += ' letter-spacing="%s"' % spacing
    if opacity is not None:
        a += ' opacity="%s"' % opacity
    if rot is not None:
        a += ' transform="rotate(%s %s %s)"' % (rot, fmt(x), fmt(y))
    line = [(w, b, i, sp) for w, b, i, sp in _words(s)]
    inner = _line_tspans(line, boldfill=None, size=size, sans=sans)
    doc.add('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s %s>%s</text>' % (
        fmt(x), fmt(y), family, fmt(size), weight, fill, anchor, a, extra, inner))


def P(doc, x, y, s, width, size=4.4, weight=400, fill=INK, lh=1.28, anchor='start', family=SANS,
      boldfill=None, kind='sans', italic=False, opacity=None, align='left', halo=None):
    """Wrapped paragraph. Returns height used."""
    sans = family == SANS and not italic
    family, weight, kind = resolve(family, size, weight, italic)
    lines = wrap(s, size, width, weight, kind)
    a = ' font-style="italic"' if italic else ''
    if halo:
        a += ' stroke="%s" stroke-width="%s" stroke-linejoin="round" paint-order="stroke"' % (halo, fmt(size * 0.28))
    if opacity is not None:
        a += ' opacity="%s"' % opacity
    tx = x
    if anchor == 'middle':
        tx = x
    out = ['<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s"%s>' % (
        fmt(x), fmt(y), family, fmt(size), weight, fill, anchor, a)]
    for k, ln in enumerate(lines):
        out.append('<tspan x="%s" dy="%s">%s</tspan>' % (fmt(tx), 0 if k == 0 else fmt(size * lh), _line_tspans(ln, boldfill, size=size, sans=sans)))
    out.append('</text>')
    doc.add(''.join(out))
    return len(lines) * size * lh


def PS(doc, *a, **k):
    """Narrative paragraph in the serif (Sitka Text)."""
    k.setdefault('family', SERIF)
    return P(doc, *a, **k)


def para_height(s, width, size=4.4, weight=400, lh=1.28, kind='sans'):
    return len(wrap(s, size, width, weight, kind)) * size * lh


# ---------------------------------------------------------------- geometry
def cr_path(pts, closed=True, tension=0.5):
    """Catmull-Rom spline through points -> cubic bezier path string."""
    n = len(pts)
    if n < 3:
        return 'M%s,%s L%s,%s' % (fmt(pts[0][0]), fmt(pts[0][1]), fmt(pts[-1][0]), fmt(pts[-1][1]))
    d = ['M%s,%s' % (fmt(pts[0][0]), fmt(pts[0][1]))]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3 * 2 / 2 * 1.0, p1[1] + (p2[1] - p0[1]) * tension / 3 * 2 / 2 * 1.0)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3 * 2 / 2 * 1.0, p2[1] - (p3[1] - p1[1]) * tension / 3 * 2 / 2 * 1.0)
        d.append('C%s,%s %s,%s %s,%s' % (fmt(c1[0]), fmt(c1[1]), fmt(c2[0]), fmt(c2[1]), fmt(p2[0]), fmt(p2[1])))
    if closed:
        d.append('Z')
    return ''.join(d)


def cr_sample(pts, closed=True, per=12, tension=0.5):
    """Sample the Catmull-Rom curve into a dense polyline."""
    n = len(pts)
    out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        for k in range(per):
            t = k / per
            mt = 1 - t
            x = mt ** 3 * p1[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * p2[0]
            y = mt ** 3 * p1[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * p2[1]
            out.append((x, y))
    if not closed:
        out.append(pts[-1])
    return out


def poly_d(pts, closed=False):
    return 'M' + 'L'.join('%s,%s' % (fmt(x), fmt(y)) for x, y in pts) + ('Z' if closed else '')


def blob_pts(cx, cy, rx, ry, n=10, j=0.08, seed=1, rot=0):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rnd.uniform(-j, j)
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def blob(cx, cy, rx, ry, n=10, j=0.08, seed=1, rot=0):
    return cr_path(blob_pts(cx, cy, rx, ry, n, j, seed, rot), True)


def normals(poly, closed=True):
    n = len(poly)
    out = []
    for i in range(n):
        a = poly[(i - 1) % n] if (closed or i > 0) else poly[0]
        b = poly[(i + 1) % n] if (closed or i < n - 1) else poly[-1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((dy / L, -dx / L))   # right-hand normal
    return out


def offset_poly(poly, d, closed=True):
    nm = normals(poly, closed)
    return [(p[0] + n[0] * d, p[1] + n[1] * d) for p, n in zip(poly, nm)]


def resample(poly, step, closed=True):
    """Resample a polyline at constant arc-length spacing."""
    pts = list(poly) + ([poly[0]] if closed else [])
    out = [pts[0]]
    acc = 0.0
    need = step
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        pos = 0.0
        while seg - pos >= need - acc:
            pos += need - acc
            t = pos / seg if seg else 0
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
            acc = 0.0
            need = step
        acc += seg - pos
        need = step
    return out


def poly_len(poly, closed=False):
    pts = list(poly) + ([poly[0]] if closed else [])
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def pt_on(poly, t):
    """point + tangent angle (deg) at fraction t along polyline."""
    L = poly_len(poly)
    target = L * t
    acc = 0
    for i in range(len(poly) - 1):
        seg = math.hypot(poly[i + 1][0] - poly[i][0], poly[i + 1][1] - poly[i][1])
        if acc + seg >= target or i == len(poly) - 2:
            u = (target - acc) / seg if seg else 0
            x = poly[i][0] + (poly[i + 1][0] - poly[i][0]) * u
            y = poly[i][1] + (poly[i + 1][1] - poly[i][1]) * u
            ang = math.degrees(math.atan2(poly[i + 1][1] - poly[i][1], poly[i + 1][0] - poly[i][0]))
            return x, y, ang
        acc += seg
    return poly[-1][0], poly[-1][1], 0


# ---------------------------------------------------------------- arrows
def _soften(pts, bow):
    """Organic routing: a 2-point arrow gets a gentle bow; corners of longer routes become smooth curves."""
    pts = list(pts)
    if len(pts) == 2:
        (x0, y0), (x1, y1) = pts
        L = math.hypot(x1 - x0, y1 - y0) or 1
        b = math.copysign(min(abs(bow) * L, 7.0), bow)
        pts = [(x0, y0), ((x0 + x1) / 2 - (y1 - y0) / L * b, (y0 + y1) / 2 + (x1 - x0) / L * b), (x1, y1)]
    return cr_sample(pts, closed=False, per=14)


def _ribbon(poly, w0, w1, ease=0.6):
    """Closed outline of a stroke that tapers from width w0 (tail) to w1 (end) along poly."""
    poly = resample(poly, 0.8, closed=False) if poly_len(poly) > 1.6 else poly
    nm = normals(poly, closed=False)
    n = max(1, len(poly) - 1)
    left, right = [], []
    for i, (p, q) in enumerate(zip(poly, nm)):
        h = (w0 + (w1 - w0) * (i / n) ** ease) / 2
        left.append((p[0] + q[0] * h, p[1] + q[1] * h))
        right.append((p[0] - q[0] * h, p[1] - q[1] * h))
    return poly_d(left + right[::-1], True)


def arrow(doc, pts, color, kind='transport', w=1.6, head=None, smooth=True, opacity=1, dash=None, label=None, bow=0.07):
    """Directional arrow drawn as a soft, tapered brush stroke along a smooth curve, with a rounded head.
    kinds: transport (solid), fusion (thick, open white head), modify (thin, dot tail), recycle (round-capped dashes),
           path (bold swoosh, pathology), signal (dotted)."""
    cp = _soften(pts, bow)
    hl = head if head else {'transport': 2.3 * w + 2.4, 'fusion': 2.2 * w + 2.4, 'modify': 3.0 * w + 1.8,
                            'recycle': 2.6 * w + 2.4, 'path': 2.2 * w + 3, 'signal': 3 * w + 1.5}[kind]
    _tl = poly_len(cp)
    if hl > 0.55 * _tl:
        hl = 0.55 * _tl
    end = cp[-1]
    acc = 0
    k = len(cp) - 1
    base = cp[0]
    shaft = [cp[0], cp[0]]
    while k > 0:
        seg = math.hypot(cp[k][0] - cp[k - 1][0], cp[k][1] - cp[k - 1][1])
        if acc + seg >= hl:
            u = (hl - acc) / seg if seg else 1
            base = (cp[k][0] + (cp[k - 1][0] - cp[k][0]) * u, cp[k][1] + (cp[k - 1][1] - cp[k][1]) * u)
            shaft = cp[:k] + [base]
            break
        acc += seg
        k -= 1
    ang = math.atan2(end[1] - base[1], end[0] - base[0])
    ca, sa = math.cos(ang), math.sin(ang)
    tip = end
    hw = {'transport': 0.40, 'fusion': 0.52, 'modify': 0.36, 'recycle': 0.40, 'path': 0.62, 'signal': 0.38}[kind] * hl
    rj = hl * 0.16                       # corner rounding of the head (round-joined outline)
    hl_ = hl - rj * 0.6
    tp = (tip[0] - ca * rj * 0.55, tip[1] - sa * rj * 0.55)
    bx, by = tp[0] - ca * hl_, tp[1] - sa * hl_
    hw_ = hw - rj * 0.4
    l = (bx - sa * hw_, by + ca * hw_)
    r = (bx + sa * hw_, by - ca * hw_)
    notch = (tp[0] - ca * hl_ * 0.74, tp[1] - sa * hl_ * 0.74)
    # shaft runs into the head's notch
    shaft = shaft[:-1] + [(tp[0] - ca * hl_ * 0.66, tp[1] - sa * hl_ * 0.66)]
    op = ' opacity="%s"' % opacity if opacity != 1 else ''

    def soft_head(fill, stroke=None, sw=None):
        k = 0.12 * hw_
        c1 = ((tp[0] + l[0]) / 2 - sa * k, (tp[1] + l[1]) / 2 + ca * k)     # flanks bulge slightly outward
        c2 = ((tp[0] + r[0]) / 2 + sa * k, (tp[1] + r[1]) / 2 - ca * k)
        cn = (notch[0] - ca * hl_ * 0.08, notch[1] - sa * hl_ * 0.08)
        d_ = 'M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z' % (
            fmt(tp[0]), fmt(tp[1]), fmt(c1[0]), fmt(c1[1]), fmt(l[0]), fmt(l[1]),
            fmt(cn[0]), fmt(cn[1]), fmt(notch[0]), fmt(notch[1]),
            fmt(cn[0]), fmt(cn[1]), fmt(r[0]), fmt(r[1]), fmt(c2[0]), fmt(c2[1]), fmt(tp[0]), fmt(tp[1]))
        return '<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
            d_, fill, stroke or fill, fmt(sw if sw is not None else rj * 1.2))

    out = []
    if kind in ('transport', 'modify'):
        out.append('<path d="%s" fill="%s"/>' % (_ribbon(shaft, w * 0.42, w * 1.08), color))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fmt(shaft[0][0]), fmt(shaft[0][1]), fmt(w * 0.21), color))
        out.append(soft_head(color))
        if kind == 'modify':
            out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fmt(cp[0][0]), fmt(cp[0][1]), fmt(w * 1.3), color))
    elif kind == 'fusion':
        out.append('<path d="%s" fill="%s"/>' % (_ribbon(shaft, w * 0.7, w * 1.6), color))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fmt(shaft[0][0]), fmt(shaft[0][1]), fmt(w * 0.35), color))
        out.append(soft_head('#fff', color, w * 0.9))
    elif kind == 'path':
        out.append('<path d="%s" fill="%s"/>' % (_ribbon(shaft, w * 0.8, w * 2.2, ease=0.5), color))
        out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fmt(shaft[0][0]), fmt(shaft[0][1]), fmt(w * 0.4), color))
        hw, hl_s = hw, hl_
        out.append(soft_head(color))
    elif kind == 'recycle':
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-dasharray="%s %s" stroke-linecap="round"/>' % (
            poly_d(shaft), color, fmt(w), fmt(w * 1.5), fmt(w * 2.3)))
        out.append(soft_head(color))
    elif kind == 'signal':
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-dasharray="%s %s" stroke-linecap="round"/>' % (
            poly_d(shaft), color, fmt(w), '0.01', fmt(w * 2.4)))
        out.append(soft_head(color))
    doc.add('<g%s>%s</g>' % (op, ''.join(out)))


def line(doc, x1, y1, x2, y2, color=INK, w=0.5, dash=None, op=None, cap='round'):
    a = ''
    if dash:
        a += ' stroke-dasharray="%s"' % dash
    if op is not None:
        a += ' opacity="%s"' % op
    doc.add('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="%s"%s/>' % (
        fmt(x1), fmt(y1), fmt(x2), fmt(y2), color, fmt(w), cap, a))


def path(doc, d, fill='none', stroke=None, w=0.5, dash=None, op=None, cap='round', join='round', extra=''):
    a = ' fill="%s"' % fill
    if stroke:
        a += ' stroke="%s" stroke-width="%s" stroke-linecap="%s" stroke-linejoin="%s"' % (stroke, fmt(w), cap, join)
    if dash:
        a += ' stroke-dasharray="%s"' % dash
    if op is not None:
        a += ' opacity="%s"' % op
    doc.add('<path d="%s"%s %s/>' % (d, a, extra))


def circ(doc, x, y, r, fill='none', stroke=None, w=0.5, op=None, dash=None):
    a = ' fill="%s"' % fill
    if stroke:
        a += ' stroke="%s" stroke-width="%s"' % (stroke, fmt(w))
    if dash:
        a += ' stroke-dasharray="%s" stroke-linecap="round"' % dash
    if op is not None:
        a += ' opacity="%s"' % op
    doc.add('<circle cx="%s" cy="%s" r="%s"%s/>' % (fmt(x), fmt(y), fmt(r), a))


def ell(doc, x, y, rx, ry, fill='none', stroke=None, w=0.5, rot=0, op=None):
    a = ' fill="%s"' % fill
    if stroke:
        a += ' stroke="%s" stroke-width="%s"' % (stroke, fmt(w))
    if op is not None:
        a += ' opacity="%s"' % op
    if rot:
        a += ' transform="rotate(%s %s %s)"' % (rot, fmt(x), fmt(y))
    doc.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s"%s/>' % (fmt(x), fmt(y), fmt(rx), fmt(ry), a))


def rect(doc, x, y, w, h, fill='none', stroke=None, sw=0.5, r=0, op=None, dash=None):
    a = ' fill="%s"' % fill
    if stroke:
        a += ' stroke="%s" stroke-width="%s"' % (stroke, fmt(sw))
    if r:
        a += ' rx="%s"' % fmt(r)
    if op is not None:
        a += ' opacity="%s"' % op
    if dash:
        a += ' stroke-dasharray="%s"' % dash
    doc.add('<rect x="%s" y="%s" width="%s" height="%s"%s/>' % (fmt(x), fmt(y), fmt(w), fmt(h), a))


def badge(doc, x, y, n, r=6.2, fill=INK, fg='#fff', size=None):
    circ(doc, x, y, r, fill=fill)
    T(doc, x, y + (size or r * 1.25) * 0.36, str(n), size=size or r * 1.25, weight=700, fill=fg, anchor='middle', family=SANS)


def group(doc, transform=None, opacity=None, extra=''):
    a = ''
    if transform:
        a += ' transform="%s"' % transform
    if opacity is not None:
        a += ' opacity="%s"' % opacity
    doc.add('<g%s %s>' % (a, extra))


def endgroup(doc):
    doc.add('</g>')


def leader(doc, pts, color=INK2, w=0.35, dot=True, dash=None, bow=0.06):
    if len(pts) == 2:
        (x0, y0), (x1, y1) = pts
        L = math.hypot(x1 - x0, y1 - y0) or 1
        b = min(bow * L, 3.5)
        mx, my = (x0 + x1) / 2 - (y1 - y0) / L * b, (y0 + y1) / 2 + (x1 - x0) / L * b
        d = 'M%s,%s Q%s,%s %s,%s' % (fmt(x0), fmt(y0), fmt(mx), fmt(my), fmt(x1), fmt(y1))
    else:
        d = cr_path(pts, False)
    a = ' stroke-dasharray="%s"' % dash if dash else ''
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"%s/>' % (d, color, fmt(w), a))
    if dot:
        circ(doc, pts[0][0], pts[0][1], w * 2.2, fill=color)
