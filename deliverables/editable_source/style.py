"""Rendering style for the illustrations: one light model for the whole poster.

Light comes from the top-left. Everything is plain vector (gradients only, no SVG filters), so the PDF stays
sharp at any print size.
  shade()          radial body fill: lit top-left, base colour in the middle, slightly deeper bottom-right
  sheen()          linear fill across an elongated body (ER, Golgi, fibres, bacteria)
  contact_shadow() soft shadow ellipse under an object (draw it BEFORE the object)
  spec()           specular highlight arc on a rounded body (draw it AFTER the object)
  tone()           a darker or lighter tint of a hue for strokes (avoid pure saturated outlines)
"""
import math
from lib import fmt

SHADOW = '#5B3426'   # warm shadow tone that sits on the peach cytoplasm and the paper


def _rgb(c):
    c = c.lstrip('#')
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(v):
    return '#%02X%02X%02X' % tuple(max(0, min(255, int(round(x)))) for x in v)


def mix(c1, c2, t):
    a, b = _rgb(c1), _rgb(c2)
    return _hex([a[i] + (b[i] - a[i]) * t for i in range(3)])


def lighten(c, t):
    return mix(c, '#FFFFFF', t)


def darken(c, t, ink='#1B1020'):
    return mix(c, ink, t)


def tone(c, t):
    """t > 0 darker, t < 0 lighter."""
    return darken(c, t) if t >= 0 else lighten(c, -t)


def _cache(doc):
    if not hasattr(doc, '_style_cache'):
        doc._style_cache = {}
    return doc._style_cache


def shade(doc, base, light=0.5, dark=0.12, cx=0.36, cy=0.3, r=0.8):
    """Radial body gradient (objectBoundingBox): highlight at the top-left, base, deeper rim."""
    key = ('sh', base, light, dark, cx, cy, r)
    c = _cache(doc)
    if key not in c:
        c[key] = doc.radgrad([(0, lighten(base, light)), (0.55, base), (1, darken(base, dark))],
                             cx=cx, cy=cy, r=r, fx=cx - 0.04, fy=cy - 0.04)
    return c[key]


def sheen(doc, base, light=0.45, dark=0.14, angle=90):
    """Linear gradient across an elongated body; angle 90 = lit from the top."""
    key = ('sn', base, light, dark, angle)
    c = _cache(doc)
    if key not in c:
        a = math.radians(angle)
        x1, y1 = 0.5 - 0.5 * math.cos(a), 0.5 - 0.5 * math.sin(a)
        x2, y2 = 0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)
        c[key] = doc.lingrad([(0, lighten(base, light)), (0.45, base), (1, darken(base, dark))],
                             fmt(x1), fmt(y1), fmt(x2), fmt(y2))
    return c[key]


def _shadow_grad(doc, strength):
    key = ('cs', strength)
    c = _cache(doc)
    if key not in c:
        c[key] = doc.radgrad([(0, SHADOW, strength), (0.6, SHADOW, strength * 0.45), (1, SHADOW, 0)], r=0.5)
    return c[key]


def contact_shadow(doc, x, y, rx, ry=None, rot=0, strength=0.16, spread=1.18, dx=None, dy=None):
    """Soft shadow under a body centred at (x, y) with radii rx, ry. Offset down-right (light is top-left)."""
    ry = rx if ry is None else ry
    dx = rx * 0.07 + 0.5 if dx is None else dx
    dy = ry * 0.14 + 0.9 if dy is None else dy
    g = _shadow_grad(doc, strength)
    t = ' transform="rotate(%s %s %s)"' % (fmt(rot), fmt(x + dx), fmt(y + dy)) if rot else ''
    doc.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s/>' % (
        fmt(x + dx), fmt(y + dy), fmt(rx * spread), fmt(ry * spread), g, t))


def spec(doc, x, y, r, a0=200, a1=262, w=None, op=0.75, inset=0.72, color='#FFFFFF'):
    """Specular highlight: a short soft arc inside a round body (angles in screen degrees, 270 = up)."""
    w = w if w is not None else max(0.35, r * 0.11)
    rr = r * inset
    p0 = (x + rr * math.cos(math.radians(a0)), y + rr * math.sin(math.radians(a0)))
    p1 = (x + rr * math.cos(math.radians(a1)), y + rr * math.sin(math.radians(a1)))
    doc.add('<path d="M%s,%s A%s,%s 0 0 1 %s,%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/>' % (
        fmt(p0[0]), fmt(p0[1]), fmt(rr), fmt(rr), fmt(p1[0]), fmt(p1[1]), color, fmt(w), op))
    # a small glint dot past the end of the arc
    pg = (x + rr * math.cos(math.radians(a1 + 14)), y + rr * math.sin(math.radians(a1 + 14)))
    doc.add('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>' % (fmt(pg[0]), fmt(pg[1]), fmt(w * 0.55), color, fmt(op * 0.9)))


# ------------------------------------------------------------------ helpers for rotated / irregular bodies
def shade_rot(doc, base, rot=0, light=0.5, dark=0.12, r=0.8, step=15):
    """shade() for a body drawn inside a rotate(rot) group: keeps the highlight at the screen top-left."""
    a = math.radians(-round(rot / step) * step)
    ox, oy = -0.14, -0.2
    cx = 0.5 + ox * math.cos(a) - oy * math.sin(a)
    cy = 0.5 + ox * math.sin(a) + oy * math.cos(a)
    return shade(doc, base, light, dark, cx=round(cx, 3), cy=round(cy, 3), r=r)


def lit_side(rot):
    """For a body elongated along local x inside rotate(rot): -1 if the lit (screen top-left) side is local -y, else +1."""
    a = math.radians(rot)
    return -1 if (math.cos(a) - math.sin(a)) >= 0 else 1


def sheen_rot(doc, base, rot=0, light=0.45, dark=0.14):
    """sheen() across the short axis of a body drawn along local x inside rotate(rot), lit from the screen top-left."""
    return sheen(doc, base, light, dark, angle=90 if lit_side(rot) < 0 else 270)


def soft_shadow_path(doc, d, dx=2.2, dy=3.6, strength=0.06, blur=9.0, steps=4):
    """Soft vector shadow of an arbitrary closed path: filled core plus stacked translucent strokes (no filters)."""
    t = 'translate(%s %s)' % (fmt(dx), fmt(dy))
    out = ['<g transform="%s">' % t]
    out.append('<path d="%s" fill="%s" opacity="%s"/>' % (d, SHADOW, fmt(strength)))
    for i in range(steps):
        wdt = blur * (1 - i / steps)
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" opacity="%s"/>' % (
            d, SHADOW, fmt(wdt), fmt(strength / steps * 0.9)))
    out.append('</g>')
    doc.add(''.join(out))


def signed_area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def inside(poly, x, y):
    """Point-in-polygon (even-odd)."""
    c = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            c = not c
        j = i
    return c


def dots_path(pts):
    """Many tiny dots as one path (zero-length segments with round caps); stroke width = dot diameter."""
    return ''.join('M%s,%sh0.01' % (fmt(x), fmt(y)) for x, y in pts)
