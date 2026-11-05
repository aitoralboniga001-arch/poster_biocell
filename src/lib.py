"""Helper library for the macrophage poster generator.
Units: 1 SVG unit = 1 mm on the final 1100 x 900 mm sheet (110 x 90 cm).
"""
import math, random, re
from contextlib import contextmanager
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


# Print legibility (polish pass, Nov 2026): every small sans molecule label (nominal 3.9-4.85 mm) is set larger, so it
# reads at arm's length on the 1100 mm sheet.  Applied centrally in T()/P()/text_width() so that layouts which measure
# their own labels stay consistent.  White text (inside pills / badges) is never scaled.
LABEL_SCALE = 1.2
LABEL_RANGE = (3.9, 4.85)


def label_size(size, family=SANS, fill=None):
    if family == SANS and LABEL_RANGE[0] <= size <= LABEL_RANGE[1] and str(fill).lower() not in ('#fff', '#ffffff', 'white'):
        return size * LABEL_SCALE
    return size


def _tw_raw(s, size, weight=400, kind='sans'):
    return _font(kind, weight, size).getlength(s) * size / 100.0


def text_width(s, size, weight=400, kind='sans'):
    if kind == 'sans':
        size = label_size(size)
    return _tw_raw(s, size, weight, kind)


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


# ---------------------------------------------------------------- svg doc
_G_TAG_RE = re.compile(r'<g\b[^>]*>|</g>')
_TR_OP_RE = re.compile(r'(translate|rotate|scale|matrix)\s*\(([^)]*)\)')
_MARKUP_RE = re.compile(r'<[^>]+>|\*\*|~~')


def _mat_mul(A, B):
    """Multiply two 2D affine matrices (a, b, c, d, tx, ty)."""
    a1, b1, c1, d1, tx1, ty1 = A
    a2, b2, c2, d2, tx2, ty2 = B
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * tx2 + c1 * ty2 + tx1,
        b1 * tx2 + d1 * ty2 + ty1,
    )


def _parse_transform(g_stack):
    """Compose active <g transform="..."> stack into (a, b, c, d, tx, ty)."""
    M = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    for tag in g_stack:
        m = re.search(r'transform="([^"]+)"', tag)
        if not m:
            continue
        for op, args_s in _TR_OP_RE.findall(m.group(1)):
            vals = [float(v) for v in re.split(r'[\s,]+', args_s.strip()) if v]
            if op == 'translate':
                tx = vals[0] if vals else 0.0
                ty = vals[1] if len(vals) > 1 else 0.0
                M = _mat_mul(M, (1.0, 0.0, 0.0, 1.0, tx, ty))
            elif op == 'scale':
                sx = vals[0] if vals else 1.0
                sy = vals[1] if len(vals) > 1 else sx
                M = _mat_mul(M, (sx, 0.0, 0.0, sy, 0.0, 0.0))
            elif op == 'rotate':
                ang = math.radians(vals[0] if vals else 0.0)
                ca, sa = math.cos(ang), math.sin(ang)
                if len(vals) >= 3:
                    cx, cy = vals[1], vals[2]
                    M = _mat_mul(M, (1.0, 0.0, 0.0, 1.0, cx, cy))
                    M = _mat_mul(M, (ca, sa, -sa, ca, 0.0, 0.0))
                    M = _mat_mul(M, (1.0, 0.0, 0.0, 1.0, -cx, -cy))
                else:
                    M = _mat_mul(M, (ca, sa, -sa, ca, 0.0, 0.0))
            elif op == 'matrix' and len(vals) == 6:
                M = _mat_mul(M, tuple(vals))
    return M


def _infer_zone(x, y):
    if y < 104:
        return 'header'
    if 22 <= x <= 220 and 104 <= y <= 245:
        return 'locator'
    if y >= 866:
        return 'refs'
    if y >= 842 and x < 780:
        return 'conclusion'
    if 15 <= x <= 338 and 245 <= y <= 535:
        return 'zone_a'
    if 555 <= x <= 995 and 125 <= y <= 472:
        return 'zone_d'
    if 418 <= x <= 775 and 555 <= y <= 758:
        return 'zone_e'
    if 758 <= x <= 1100 and 472 <= y <= 712:
        return 'zone_f'
    if 875 <= x <= 1100 and 712 <= y <= 775:
        return 'zone_g'
    if x >= 1005 and 104 <= y < 472:
        return 'zone_f'
    if y >= 745:
        return 'wall'
    if 235 <= x <= 535 and 505 <= y <= 745:
        return 'zone_b'
    if 320 <= x <= 575 and 140 <= y <= 360:
        return 'zone_c'
    return 'cell'


def _clean_label_text(s):
    txt = _MARKUP_RE.sub('', str(s))
    return txt.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()


class Doc:
    def __init__(self, w=1100, h=900, mode='poster', state_overrides=None):
        self.w, self.h = w, h
        self.mode = mode
        self.state_overrides = dict(state_overrides) if state_overrides else {}
        self.defs = []
        self.body = []
        self._poster_body = []
        self._n = 0
        self.labels = []
        self.actors = {}
        self._active_actors = []
        self._g_stack = []
        self._actor_chunks = {}
        self._current_zone = None

    def uid(self, p='i'):
        self._n += 1
        return '%s%d' % (p, self._n)

    def get_state(self, actor_id, default=0):
        return self.state_overrides.get(actor_id, default)

    def is_suppressed(self):
        if self.mode == 'poster':
            return False
        if self.mode == 'plate':
            return any(self.actors.get(a, {}).get('skip_in_plate', True) for a in self._active_actors)
        if self.mode.startswith('actor:'):
            target = self.mode.split(':', 1)[1]
            return target not in self._active_actors
        return False

    def add(self, s):
        self._poster_body.append(s)
        if self._active_actors:
            for aid in self._active_actors:
                self._actor_chunks.setdefault(aid, []).append(s)
        if not self.is_suppressed():
            self.body.append(s)
        for m in _G_TAG_RE.finditer(s):
            tok = m.group(0)
            if tok == '</g>':
                if self._g_stack:
                    self._g_stack.pop()
            elif not tok.endswith('/>'):
                self._g_stack.append(tok)

    def register_label(self, s, x, y, size=5.0, weight=400, fill=INK, anchor='start', kind='sans',
                       width=None, height=None, zone=None, step=None):
        clean = _clean_label_text(s)
        if not clean:
            return
        M = _parse_transform(self._g_stack)
        px = M[0] * x + M[2] * y + M[4]
        py = M[1] * x + M[3] * y + M[5]
        sc = math.hypot(M[0], M[1]) or 1.0
        psize = size * sc
        if width is not None:
            w = width * sc
        elif kind == 'hand':
            w = len(clean) * psize * 0.39
        else:
            try:
                w = _tw_raw(clean, psize, weight, kind)
            except Exception:
                w = len(clean) * psize * 0.5
        h = (height * sc) if height is not None else (psize * 1.18)
        if anchor == 'middle':
            bx = px - w / 2.0
        elif anchor == 'end':
            bx = px - w
        else:
            bx = px
        by = py - psize * 0.88
        zn = zone or self._current_zone
        if not zn and self._active_actors:
            for aid in reversed(self._active_actors):
                if self.actors.get(aid, {}).get('zone'):
                    zn = self.actors[aid]['zone']
                    break
        if not zn:
            zn = _infer_zone(bx + w / 2.0, by + h / 2.0)
        entry = {
            'text': clean,
            'bbox': [round(bx, 2), round(by, 2), round(max(1.0, w), 2), round(max(1.0, h), 2)],
            'x': round(px, 2),
            'y': round(py, 2),
            'size': round(psize, 2),
            'color': fill,
            'anchor': anchor,
            'zone': zn,
        }
        if step is not None:
            entry['step'] = str(step)
        self.labels.append(entry)

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

    def render_poster(self, title='Macrophage poster'):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="%dmm" height="%dmm" viewBox="0 0 %d %d">\n'
                '<title>%s</title>\n<defs>\n<style>text{font-kerning:normal;font-variant-ligatures:common-ligatures;'
                'font-variant-numeric:lining-nums}</style>\n%s\n</defs>\n%s\n</svg>\n' % (
                    self.w, self.h, self.w, self.h, esc(title), '\n'.join(self.defs), '\n'.join(self._poster_body)))

    def render_actor(self, actor_id, title=None):
        chunks = self._actor_chunks.get(actor_id, [])
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="%dmm" height="%dmm" viewBox="0 0 %d %d">\n'
                '<title>%s</title>\n<defs>\n<style>text{font-kerning:normal;font-variant-ligatures:common-ligatures;'
                'font-variant-numeric:lining-nums}</style>\n%s\n</defs>\n%s\n</svg>\n' % (
                    self.w, self.h, self.w, self.h, esc(title or ('actor:' + actor_id)), '\n'.join(self.defs), '\n'.join(chunks)))


@contextmanager
def actor(doc, actor_id, pivot=None, bbox=None, zone=None, states=1, rest_state=0, skip_in_plate=True):
    """Context manager tagging a moving or multi-state actor. Byte-identical in 'poster' mode."""
    if actor_id not in doc.actors:
        doc.actors[actor_id] = {
            'id': actor_id,
            'pivot': list(pivot) if pivot is not None else None,
            'bbox': list(bbox) if bbox is not None else None,
            'zone': zone or doc._current_zone,
            'states': states,
            'rest_state': rest_state,
            'skip_in_plate': skip_in_plate,
        }
    else:
        meta = doc.actors[actor_id]
        if pivot is not None and meta.get('pivot') is None:
            meta['pivot'] = list(pivot)
        if bbox is not None and meta.get('bbox') is None:
            meta['bbox'] = list(bbox)
        if zone is not None and meta.get('zone') is None:
            meta['zone'] = zone
        if states != 1:
            meta['states'] = states
            meta['rest_state'] = rest_state
    g_open = list(doc._g_stack)
    chunks = doc._actor_chunks.setdefault(actor_id, [])
    chunks.extend(g_open)
    is_target = (doc.mode == 'actor:' + actor_id)
    if is_target:
        doc.body.extend(g_open)
    doc._active_actors.append(actor_id)
    try:
        yield doc.get_state(actor_id, rest_state)
    finally:
        doc._active_actors.pop()
        g_close = ['</g>'] * len(g_open)
        chunks.extend(g_close)
        if is_target:
            doc.body.extend(g_close)


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
            ww = _tw_raw(w, size, 700 if b else weight, ('seriti' if i else kind))
            sw = _tw_raw(' ', size, weight, kind) if (cur and sp) else 0
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
    size = label_size(size, family, fill)
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
    if hasattr(doc, 'register_label'):
        doc.register_label(s, x, y, size=size, weight=weight, fill=fill, anchor=anchor, kind=kind)


def P(doc, x, y, s, width, size=4.4, weight=400, fill=INK, lh=1.28, anchor='start', family=SANS,
      boldfill=None, kind='sans', italic=False, opacity=None, align='left', halo=None):
    """Wrapped paragraph. Returns height used."""
    size = label_size(size, family, fill)
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
    h_used = len(lines) * size * lh
    if hasattr(doc, 'register_label'):
        doc.register_label(s, x, y, size=size, weight=weight, fill=fill, anchor=anchor, kind=kind, width=width, height=h_used)
    return h_used


def PS(doc, *a, **k):
    """Narrative paragraph in the serif (Sitka Text)."""
    k.setdefault('family', SERIF)
    return P(doc, *a, **k)


def para_height(s, width, size=4.4, weight=400, lh=1.28, kind='sans'):
    if kind == 'sans':
        size = label_size(size)
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
