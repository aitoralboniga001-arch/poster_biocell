"""Magnifier-lens language for everything outside the central cell (v3): round insets + zoom cones."""
import math, random
from lib import *
from bio import *
from cellmod import on_circle
from cellmod2 import nox2
import layout2 as L
from layout2 import (heading, bullet_list, NAVY, SEC, S_BODY, S_SMALL, RX, RW, BY, IX, SLATE, TEAL2, BROWN,
                     helix, mem_draw, lumen_fill, rab_pin, RABC, HOPSC, QA, QB, QC, RS, neutrophil, monocyte, bilayer_h)
from annot2 import tag, DPHAG, DLY, DPATH, DINFL, DREC

AIR = '#EEF5F8'
TISSUE = '#F4DCD3'


# ------------------------------------------------------------------------------------------- primitives
from style import shade, sheen, contact_shadow, spec, tone, lighten, darken, mix

GLASS_SH = '#3A2A1A'


def _ugrad(doc, kind, stops, **a):
    """Gradient in user space (absolute mm), for fills whose bounding box would distort the ramp."""
    gid = doc.uid('ug')
    st = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (fmt(o), c, fmt(op)) for o, c, op in stops)
    at = ' '.join('%s="%s"' % (k, fmt(v)) for k, v in a.items())
    doc.defs.append('<%sGradient id="%s" gradientUnits="userSpaceOnUse" %s>%s</%sGradient>' % (kind, gid, at, st, kind))
    return 'url(#%s)' % gid


def paper(doc):
    """V2: painted cotton paper with watercolour blooms in the alveolar air (procedural raster, see texture.py)."""
    import texture
    texture.paper(doc)


LINK = '#9C8F7C'          # warm neutral for zoom hairlines
FEATHER = 0.87           # vignette stays opaque to this fraction of r, then dissolves into the paper


def _glass_shadow(doc, cx, cy, r):
    """(v5: frameless vignettes) kept for API compatibility; draws nothing."""
    return None


def _feather_mask(doc, cx, cy, r):
    c = doc.__dict__.setdefault('_style_cache', {})
    if 'feather' not in c:
        gid = doc.uid('fg')
        doc.defs.append('<radialGradient id="%s" cx="0.5" cy="0.5" r="0.5">'
                        '<stop offset="0" stop-color="#fff"/><stop offset="%s" stop-color="#fff"/>'
                        '<stop offset="%s" stop-color="#fff" stop-opacity="0.55"/>'
                        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
                        % (gid, fmt(FEATHER), fmt(FEATHER + (1 - FEATHER) * 0.45)))
        c['feather'] = gid
    mid = doc.uid('fm')
    doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
                    '<circle cx="%s" cy="%s" r="%s" fill="url(#%s)"/></mask>'
                    % (mid, fmt(cx - r - 1), fmt(cy - r - 1), fmt(2 * r + 2), fmt(2 * r + 2), fmt(cx), fmt(cy), fmt(r), c['feather']))
    return mid


def lens_open(doc, cx, cy, r, bg='#FFFFFF'):
    """Frameless circular vignette: content is clipped to the circle and feathered into the paper at the edge."""
    cid = doc.uid('clip')
    doc.defs.append('<clipPath id="%s"><circle cx="%s" cy="%s" r="%s"/></clipPath>' % (cid, fmt(cx), fmt(cy), fmt(r)))
    mid = _feather_mask(doc, cx, cy, r)
    doc.add('<g mask="url(#%s)"><g clip-path="url(#%s)">' % (mid, cid))
    if isinstance(bg, str) and bg.startswith('#'):
        base = mix(bg, PAPER, 0.45)
        fill = _ugrad(doc, 'radial', [(0, mix(base, '#FFFFFF', 0.35), 1), (0.7, base, 1), (1, mix(base, PAPER, 0.3), 1)],
                      cx=cx - r * 0.2, cy=cy - r * 0.25, r=r * 1.25)
    else:
        fill = bg
    circ(doc, cx, cy, r, fill=fill)


def _glass(doc, cx, cy, r):
    """(v5: frameless vignettes) kept for API compatibility; draws nothing."""
    return None


def lens_close(doc, cx, cy, r, color=None):
    doc.add('</g></g>')


def _hair(doc, p, q, color, op0=0.75, op1=0.12, w=0.25):
    g = _ugrad(doc, 'linear', [(0, color, op0), (1, color, op1)], x1=p[0], y1=p[1], x2=q[0], y2=q[1])
    path(doc, 'M%s,%s L%s,%s' % (fmt(p[0]), fmt(p[1]), fmt(q[0]), fmt(q[1])), stroke=g, w=w, cap='butt')


def beam(doc, quad, color, op=0.13, a=None, b=None):
    """Zoom link: two fine tangent hairlines in a warm neutral (tinted by the section), fading along their length,
    over a barely-there wash.  quad = (p1a, p2a, p2b, p1b); a = dense (source) end, b = faded end."""
    p1a, p2a, p2b, p1b = quad
    a = a or ((p1a[0] + p1b[0]) / 2, (p1a[1] + p1b[1]) / 2)
    b = b or ((p2a[0] + p2b[0]) / 2, (p2a[1] + p2b[1]) / 2)
    col = mix(color, LINK, 0.55)
    g = _ugrad(doc, 'linear', [(0, col, 0.035), (1, col, 0.0)], x1=a[0], y1=a[1], x2=b[0], y2=b[1])
    path(doc, poly_d([p1a, p2a, p2b, p1b], True), fill=g)
    for p, q in ((p1a, p2a), (p1b, p2b)):
        _hair(doc, p, q, col)


def cone(doc, c1, c2, color, op=0.13):
    """Zoom link between a source ring c1=(x,y,r) and a lens c2=(x,y,r) along the outer tangents."""
    (x1, y1, r1), (x2, y2, r2) = c1, c2
    d = math.hypot(x2 - x1, y2 - y1)
    th = math.atan2(y2 - y1, x2 - x1)
    ph = math.acos(max(-1, min(1, (r1 - r2) / d)))
    pts = []
    for s in (1, -1):
        a = th + s * ph
        pts.append(((x1 + r1 * math.cos(a), y1 + r1 * math.sin(a)), (x2 + (r2 * 0.97) * math.cos(a), y2 + (r2 * 0.97) * math.sin(a))))
    (p1a, p2a), (p1b, p2b) = pts
    beam(doc, (p1a, p2a, p2b, p1b), color, op=op, a=(x1, y1), b=(x2, y2))


def rbc(doc, x, y, rx, ry, rot=0, op=None):
    """Red blood cell: lit disc (shaded body + paler centre)."""
    ell(doc, x, y, rx, ry, fill=shade(doc, '#C0392B', light=0.35, dark=0.15), stroke=tone('#C0392B', 0.3), w=0.2, rot=rot, op=op)
    ell(doc, x - rx * 0.1, y - ry * 0.12, rx * 0.45, ry * 0.4, fill='#E8796A', rot=rot, op=0.55 if op is None else op * 0.55)


def cell_body(doc, d, cx, cy, rx, ry, base, stroke, w, rot=0):
    """Shaded cell silhouette (path d) with a soft contact shadow and a darker-toned outline."""
    contact_shadow(doc, cx, cy, rx, ry, rot=rot, strength=0.15)
    path(doc, d, fill=shade(doc, base, light=0.55, dark=0.07), stroke=stroke, w=w)


def nucleus(doc, x, y, r, base='#CFC7EA', stroke='#6A5FA6', w=0.5):
    circ(doc, x, y, r, fill=shade(doc, base, light=0.5, dark=0.12), stroke=stroke, w=w)
    spec(doc, x, y, r, a0=205, a1=245, op=0.6, inset=0.62, w=max(0.3, r * 0.09))


def lens_label(doc, x, y, text, tx, ty, color=INK, size=S_SMALL, weight=700, anchor='start'):
    T(doc, x, y, text, size=size, weight=weight, fill=color, anchor=anchor, halo=L.PAPER_HALO if hasattr(L, 'PAPER_HALO') else None)
    sx = x + (text_width(text, size, weight) + 1.5 if anchor == 'start' else -1.5)
    leader(doc, [(tx, ty), (sx, y - size * 0.33)], color=color, w=0.45)


# ------------------------------------------------------------------------------------------- 1 introduction
L1 = (204, 226, 50)


def intro(doc):
    x, w = 25, 237
    heading(doc, x, 112, 1, 'Alveolar macrophages', 'AITOR', x + w)
    bullet_list(doc, x, 126, [
        '**Tissue-resident phagocytes** of the innate immune system',
        'Live **in the alveolar lumen**, on the epithelium, bathed in surfactant-rich lining fluid',
        'Clear **microbes, dust and dead cells**; their cytokines alert other immune cells',
    ], w, boldfill='#8E2F1F')
    cx, cy, r = L1
    # zoom: the macrophage in this alveolus is the cell magnified in the centre
    mx, my = cx + 7, cy + 16
    beam(doc, ((mx + 4, my - 8), (334, 176), (312, 268), (mx + 6, my + 6)), '#D95C3F', op=0.15, a=(323, 222), b=(mx + 5, my - 1))
    lens_open(doc, cx, cy, r, AIR)
    ac, ar = (cx - 30, cy - 60), 95         # large, gently curved alveolus: its wall crosses the lower right of the vignette
    tg = _ugrad(doc, 'radial', [(0, TISSUE, 1), (0.8, TISSUE, 1), (0.9, mix(TISSUE, '#EBC6BB', 0.5), 1), (1, mix('#E6BAAE', PAPER, 0.3), 1)],
                cx=ac[0], cy=ac[1], r=ar + 24)
    circ(doc, ac[0], ac[1], ar + 24, fill=tg)
    circ(doc, ac[0], ac[1], ar + 10, fill='none', stroke='#EFC6BC', w=6.6)          # capillary wall
    circ(doc, ac[0], ac[1], ar + 10, fill='none', stroke='#F9E0D9', w=5.0)          # capillary lumen
    circ(doc, ac[0], ac[1], ar + 8.8, fill='none', stroke='#FFFFFF', w=0.8, op=0.35)
    for k in range(12):
        a = math.radians(30 + k * 6.5)
        rbc(doc, ac[0] + (ar + 10) * math.cos(a), ac[1] + (ar + 10) * math.sin(a), 2.1, 1.3, rot=math.degrees(a) + 90, op=0.8)
    ag = _ugrad(doc, 'radial', [(0, '#FFFFFF', 1), (0.45, mix(AIR, '#FFFFFF', 0.3), 1), (0.8, AIR, 1), (1, mix(AIR, PAPER, 0.5), 1)],
                cx=cx - 6, cy=cy - 10, r=62)
    circ(doc, ac[0], ac[1], ar, fill=ag, stroke='#D7A397', w=1.0)
    circ(doc, ac[0], ac[1], ar - 1.8, fill='none', stroke='#DCEBF2', w=2.0)       # lining fluid
    circ(doc, ac[0], ac[1], ar - 2.9, fill='none', stroke='#FFFFFF', w=0.35, op=0.7)
    for k in range(5):
        a = math.radians(38 + k * 13)
        ell(doc, ac[0] + ar * math.cos(a), ac[1] + ar * math.sin(a), 3.4, 0.9, fill='#A67F99', rot=math.degrees(a) + 90)
    a = math.radians(64)
    mx, my = ac[0] + (ar - 10) * math.cos(a), ac[1] + (ar - 10) * math.sin(a)
    pd = 'M%s,%s q6,-10 17,-9' % (fmt(mx + 11), fmt(my - 7))
    contact_shadow(doc, mx, my, 18, 10.5, rot=-24, strength=0.15)
    path(doc, pd, stroke='#B2594A', w=2.4, cap='round')
    path(doc, pd, stroke='#E9A58E', w=0.7, cap='round', op=0.6)
    path(doc, blob(mx, my, 18, 10.5, n=11, j=0.12, seed=4, rot=-24), fill=shade(doc, '#F8DCCD', light=0.55, dark=0.07), stroke='#B2594A', w=1.4)
    nucleus(doc, mx - 3, my + 0.5, 4.6)
    spec(doc, mx - 1, my - 1, 11, a0=205, a1=240, op=0.55, inset=0.8, w=0.45)
    silica(doc, mx + 7, my - 1, s=0.35, rot=0)
    bacterium(doc, cx - 18, cy - 22, L=15, W=6.2, rot=25, lps=False, flagella=False, scale=1.0)
    silica(doc, cx + 14, cy - 30, s=0.7, rot=20)
    silica(doc, cx - 28, cy + 2, s=0.5, rot=-10)
    asbestos_fibre(doc, cx + 2, cy - 6, cx + 26, cy - 14, w=1.6, color='#C9A66B', frays=False)
    lens_close(doc, cx, cy, r, '#A24A3B')
    lens_label(doc, 25, 196, 'Air space (alveolus)', cx - 22, cy - 10, '#4E6E7E')
    lens_label(doc, 25, 224, 'Alveolar macrophage', mx - 8, my, '#A24A3B')
    lens_label(doc, 25, 252, 'Epithelium + capillary', cx - 12, cy + 38, '#A0463A')
    return mx, my


# ------------------------------------------------------------------------------------------- 2 recognition + engulfment
L2 = (148, 381, 79)
RING = (301, 302, 26)


def contact_site(doc):
    for (y, kind, col) in [(284, 'fc', '#5A6B85'), (297, 'cr', '#1F8F8A'), (310, 'lectin', '#8F5A2A'), (322, 'tlr', '#C81D63')]:
        receptor(doc, 307, y, h=10, rot=-90, color=col, kind=kind, tail=True)
    for y in (291, 303):
        antibody(doc, 299, y, s=0.9, rot=-90)
    c3b(doc, 297, 316, s=1.0, rot=-90)
    cone(doc, RING, L2, PHAG, op=0.14)
    circ(doc, RING[0], RING[1], RING[2], fill='none', stroke='#FFFFFF', w=0.9, op=0.5)
    circ(doc, RING[0], RING[1], RING[2], fill='none', stroke=mix(PHAG, LINK, 0.55), w=0.3, op=0.9)
    tag(doc, RING[0] - 8, RING[1] - RING[2] - 4, '2.1', PHAG)


def recognition(doc):
    heading(doc, IX, 294, 2, 'Recognition and engulfment', 'NEREA', IX + 237)
    cx, cy, r = L2
    lens_open(doc, cx, cy, r, '#F4F8FA')
    top = cy - r
    bg_ = _ugrad(doc, 'linear', [(0, '#DCE59E', 1), (0.55, '#B9C561', 1), (1, '#A3B14C', 1)], x1=0, y1=top, x2=0, y2=top + 36)
    rect(doc, cx - r, top, 2 * r, 36, fill=bg_)
    rect(doc, cx - r, top + 36, 2 * r, 2.4, fill='#5B3426', op=0.08)
    line(doc, cx - r, top + 32, cx + r, top + 32, '#7C8A24', 0.7)
    line(doc, cx - r, top + 33.1, cx + r, top + 33.1, '#E4EBB4', 0.35, op=0.8)
    path(doc, 'M%s,%s H%s' % (cx - r, top + 36, cx + r), stroke='#556116', w=1.0)
    T(doc, cx, top + 24, 'Bacterium', size=6.4, weight=700, fill='#3F4A0E', anchor='middle')
    for k in range(26):
        xx = cx - r + 3 + k * 6
        line(doc, xx, top + 36, xx, top + 40.5, '#5E6B1F', 0.6)
        circ(doc, xx, top + 41.6, 0.9, fill='#7C8A24')
    mem = cy + 26
    cg = _ugrad(doc, 'linear', [(0, CYTO, 1), (1, '#F6DCCD', 1)], x1=0, y1=mem, x2=0, y2=cy + r)
    rect(doc, cx - r, mem, 2 * r, r, fill=cg)
    bilayer_h(doc, cx - r, cx + r, mem)
    xs = [cx - 48, cx - 16, cx + 16, cx + 48]
    for dx in (-7, 7):
        antibody(doc, xs[0] + dx, cy - 22, s=2.4, rot=0)
    receptor(doc, xs[0], mem - 3, h=34, color='#5A6B85', kind='fc')
    c3b(doc, xs[1], cy - 20, s=2.6, rot=0)
    receptor(doc, xs[1], mem - 3, h=38, color=TEAL2, kind='cr')
    for dx in (-5, 5):
        circ(doc, xs[2] + dx, cy - 28, 1.8, fill='#E0B84C', stroke='#8A6A12', w=0.3)
    receptor(doc, xs[2], mem - 3, h=50, color=BROWN, kind='lectin')
    path(doc, 'M%s,%s L%s,%s' % (xs[3], top + 42, xs[3], cy - 14), stroke='#7C8A24', w=0.9, dash='1 1.2')
    circ(doc, xs[3], cy - 13, 2.2, fill='#7C8A24')
    receptor(doc, xs[3], mem - 3, h=30, color=INFL, kind='tlr')
    for dx in (-3, 3):
        phos_dot(doc, xs[0] + dx, mem + 6.5, 1.5)
    for xx, (a, b, c) in zip(xs, [('FcγR', 'IgG', SLATE), ('CR3', 'iC3b', '#15706C'), ('MR', 'sugars', '#6E4220'), ('TLR4', 'LPS', '#A3144F')]):
        T(doc, xx, mem + 15, a, size=6.4, weight=700, fill=c, anchor='middle')
        T(doc, xx, mem + 22, b, size=5.4, fill=c, anchor='middle')
    lens_close(doc, cx, cy, r, PHAG)
    PS(doc, IX, cy + r + 14, 'Opsonins (**IgG**, **iC3b**) bridge bacterium and receptor; FcγR, CR3 and the mannose receptor trigger uptake. **TLR4** senses LPS and only signals. CR1 binds C3b/C4b.',
      237, size=S_BODY, lh=1.18, boldfill=DPHAG)
    # engulfment
    ey = cy + r + 66
    tag(doc, IX, ey, '2.2', PHAG)
    T(doc, IX + 15, ey, 'Engulfment: a receptor “zipper”', size=6.8, weight=700, fill=DPHAG)
    x_, y_ = IX, ey + 7
    for k, t in enumerate(['FcγR cluster', 'Syk', 'PI3K', 'Rac · Cdc42', 'Arp2/3']):
        cw = text_width(t, 5.8, 700) + 6
        rect(doc, x_, y_, cw, 9.6, fill='#FFFFFF' if k < 3 else '#FBE3D8', stroke='#5A6B85' if k < 3 else '#C2571A', sw=0.7, r=4.8)
        T(doc, x_ + cw / 2, y_ + 6.7, t, size=5.8, weight=700, fill='#3E4C61' if k < 3 else '#9A3B12', anchor='middle')
        x_ += cw
        if k < 4:
            arrow(doc, [(x_ + 0.8, y_ + 4.8), (x_ + 5.4, y_ + 4.8)], '#4A5563', 'transport', w=0.8, head=3.0, smooth=False)
            x_ += 6.2
    PS(doc, IX, y_ + 19, 'Branched F-actin pushes **pseudopods** around the particle (2.2, the cup in the cell) until the membrane seals into a **phagosome** (2.3).',
      237, size=S_BODY, lh=1.18, boldfill=DPHAG)
    return y_ + 19


# ------------------------------------------------------------------------------------------- 4 fusion (three lenses)
def fusion(doc):
    x0, w = 25, 415
    heading(doc, x0, BY, 4, 'Docking and fusion', 'ENERITZ', x0 + w, sub='magnified at 4: a lysosome meets the late phagosome')
    mid = BY + 46
    top, bot = mid - 36, mid + 36
    LUMA, LUMB = '#F9D5CA', '#E4D3F3'
    R = 31
    centres = [x0 + 52, x0 + 196, x0 + 340]
    sw = 94
    caps = ['~~a~~  **Tethering.** Rab7-GTP recruits the HOPS complex, which bridges both membranes',
            '~~b~~  **Zipping.** Syntaxin-7, Vti1b and syntaxin-8 coil with VAMP7',
            '~~c~~  **Fusion.** A pore opens and contents mix; NSF later recycles the SNAREs']
    for k, cxs in enumerate(centres):
        a = cxs - 47
        lens_open(doc, cxs, mid, R, '#FFFFFF')
        if k == 0:
            A = [(a + 18, top), (a + 25, mid), (a + 18, bot)]
            B = [(a + 76, top), (a + 69, mid), (a + 76, bot)]
            lumen_fill(doc, A, a, top, bot, LUMA)
            lumen_fill(doc, B, a + sw, top, bot, LUMB)
            mem_draw(doc, A, '#C23B2A')
            mem_draw(doc, B, '#7A3FB5')
            rab_pin(doc, a + 25, mid + 13, 1)
            rab_pin(doc, a + 69, mid + 13, -1)
            for j, dx in enumerate((32, 39.5, 47, 54.5, 62)):
                hy = mid + 13 + (0.8 if j % 2 else -0.8)
                circ(doc, a + dx + 0.4, hy + 0.7, 3.5, fill='#3E1E70', op=0.12)
                circ(doc, a + dx, hy, 3.4, fill=shade(doc, HOPSC, light=0.45, dark=0.12), stroke=tone(HOPSC, 0.4), w=0.35)
                spec(doc, a + dx, hy, 3.4, a0=205, a1=245, op=0.55, inset=0.58, w=0.4)
            for j, c in enumerate((QA, QB, QC)):
                helix(doc, a + 26, mid - 9 + j * 4.5, a + 39, mid - 10 + j * 4.5, c, amp=0.9, turns=2.3, w=1.1, phase=j)
            helix(doc, a + 68, mid - 4.5, a + 55, mid - 4.5, RS, amp=0.9, turns=2.3, w=1.1)
            T(doc, a + 47, mid + 24, 'HOPS', size=5.8, weight=700, fill=HOPSC, anchor='middle', halo='#fff')
            T(doc, a + 47, mid - 16, 'Rab7-GTP', size=5.6, weight=700, fill=RABC, anchor='middle', halo='#fff')
        elif k == 1:
            A = [(a + 18, top), (a + 30, mid - 11), (a + 41, mid), (a + 30, mid + 11), (a + 18, bot)]
            B = [(a + 76, top), (a + 64, mid - 11), (a + 53, mid), (a + 64, mid + 11), (a + 76, bot)]
            lumen_fill(doc, A, a, top, bot, LUMA)
            lumen_fill(doc, B, a + sw, top, bot, LUMB)
            mem_draw(doc, A, '#C23B2A')
            mem_draw(doc, B, '#7A3FB5')
            ell(doc, a + 47, mid, 11, 8, fill=doc.radgrad([(0, HOPSC, 0.26), (0.7, HOPSC, 0.16), (1, HOPSC, 0)], r=0.5))
            for j, c in enumerate((QA, QB, QC, RS)):
                helix(doc, a + 41, mid + (j - 1.5) * 1.5, a + 53, mid + (j - 1.5) * 1.5, c, amp=1.4, turns=2.0, w=1.0, phase=j * 1.57)
            T(doc, a + 47, mid - 16, 'SNAREs', size=5.8, weight=700, fill=NAVY, anchor='middle', halo='#fff')
        else:
            pts = [(a + 6, top), (a + 28, top + 8), (a + 47, mid - 15), (a + 66, top + 8), (a + 88, top),
                   (a + 90, mid), (a + 88, bot), (a + 66, bot - 8), (a + 47, mid + 15), (a + 28, bot - 8), (a + 6, bot), (a + 4, mid)]
            g = doc.lingrad([(0, LUMA), (1, LUMB)], 0, 0, 1, 0)
            rect(doc, a, top, sw, bot - top, fill=g)
            lg = doc.radgrad([(0, '#FFFFFF', 0.55), (1, '#FFFFFF', 0)], cx=0.35, cy=0.3, r=0.6)
            rect(doc, a, top, sw, bot - top, fill=lg)
            pd = cr_path(pts, True)
            doc.add('<g transform="translate(0.6 0.9)">')
            path(doc, pd, fill='none', stroke='#5B3426', w=4.6, op=0.10)
            doc.add('</g>')
            path(doc, pd, fill='none', stroke=tone('#8A3A8A', 0.2), w=4.2)
            path(doc, pd, fill='none', stroke='#8A3A8A', w=3.5)
            path(doc, pd, fill='none', stroke=lighten('#8A3A8A', 0.88), w=1.3)
            dense = cr_sample(pts, closed=True, per=10)
            for off in (-1.45, 1.45):
                path(doc, poly_d(offset_poly(dense, off, closed=True), True), stroke=tone('#8A3A8A', 0.45), w=1.0, dash='0.01 1.9')
            for (dx, dy) in [(66, -8), (72, 6), (60, 12)]:
                enzyme_dot(doc, a + dx, mid + dy, 1.9)
            for (dx, dy) in [(28, -6), (34, 8), (22, 4)]:
                hplus(doc, a + dx, mid + dy, 1.1)
            arrow(doc, [(a + 62, mid + 2), (a + 32, mid + 2)], BIO, 'transport', w=1.0, head=4.5, smooth=False)
            T(doc, a + 47, mid - 8, 'pore', size=5.8, weight=700, fill='#4A2A5A', anchor='middle', halo='#fff')
        lens_close(doc, cxs, mid, R, CONV)
        PS(doc, cxs, mid + R + 9, caps[k], 128, size=5.8, lh=1.16, boldfill=NAVY, anchor='middle')
        if k < 2:
            arrow(doc, [(cxs + R + 6, mid), (cxs + 144 - R - 6, mid)], CONV, 'fusion', w=0.75, head=4.4, smooth=False, bow=0)


# ------------------------------------------------------------------------------------------- 2 killing (two lenses)
def killing(doc):
    x0, w = 456, 410
    heading(doc, x0, BY, 2, 'Killing and digestion', 'NEREA', None, sub='step 2.7: two separate mechanisms, magnified from 2.3–2.6', label='2.7')
    cy = BY + 42
    R = 27.5
    cx = x0 + 27
    lens_open(doc, cx, cy, R, CYTO)
    vesicle(doc, cx, cy + 3, 18.5, fill='#FDEAF0', stroke='#CF7F99', w=0.5)
    bacterium(doc, cx, cy + 4, L=21, W=9, rot=-20, lps=False, flagella=False, scale=1.0)
    nox2(doc, cx, cy - 15.5, -90, s=1.2)
    for (dx, dy) in [(-10, 0), (10, -4), (9, 12), (-7, 13)]:
        ros(doc, cx + dx, cy + dy, s=1.1)
    lens_close(doc, cx, cy, R, INFL)
    PS(doc, x0 + 58, cy - 10, '**Oxidative burst** (from 2.3): NOX2 passes electrons from cytosolic NADPH to O₂ → superoxide → H₂O₂', 140,
      size=6.0, lh=1.16, boldfill=DINFL)
    x1 = x0 + 208
    cx = x1 + 27
    lens_open(doc, cx, cy, R, CYTO)
    g = doc.radgrad([(0, '#F5ECFB'), (1, '#DCC8F0')], cx=.5, cy=.5, r=.6)
    vesicle(doc, cx, cy, 18.5, fill=g, stroke='#A98BCB', w=0.5)
    for (dx, dy) in [(-7, -4.5), (5.5, -9), (9, 7), (-4.5, 10), (0, 1)]:
        enzyme_dot(doc, cx + dx, cy + dy, 2.3)
    for (dx, dy) in [(-10, 3.5), (3.5, -1), (-1, 11)]:
        hplus(doc, cx + dx, cy + dy, 1.1)
    for a in (200, 270, 340, 50, 120):
        px, py = on_circle(cx, cy, 18.5, a)
        vatpase(doc, px, py, a, s=0.62)
    lens_close(doc, cx, cy, R, CONV)
    PS(doc, x1 + 58, cy - 10, '**Acid hydrolysis** (after fusion, 2.6): V-ATPase pumps H⁺ in; cathepsins, lipases, nucleases and glycosidases dismantle the bacterium', 146,
      size=6.0, lh=1.16, boldfill=DLY)
    PS(doc, x0, BY + 84, '**Products** (amino acids, sugars, nucleotides) leave for reuse; some peptides are presented on **MHC II** to T cells.', w,
      size=6.0, lh=1.16, boldfill='#0B6B72', fill=INK2)


# ------------------------------------------------------------------------------------------- 5 pathology lenses
def histology(doc, cx, cy, r, fibrotic):
    """Round, histology-like view of lung parenchyma: air spaces (pale) separated by septa."""
    lens_open(doc, cx, cy, r, '#E9B4AA' if not fibrotic else '#DDB57E')
    rnd = random.Random(11 if not fibrotic else 12)
    sp = 17.5
    # septal tissue: soft depth (lit top-left, deeper toward the lower right)
    base = '#E9B4AA' if not fibrotic else '#DDB57E'
    circ(doc, cx, cy, r, fill=_ugrad(doc, 'radial', [(0, lighten(base, 0.3), 1), (0.6, base, 1), (1, darken(base, 0.1), 1)],
                                     cx=cx - r * 0.35, cy=cy - r * 0.4, r=r * 1.6))
    air_fill = shade(doc, '#F5F9FB', light=0.7, dark=0.05, cx=0.62, cy=0.66, r=0.8)
    rim_key = ('hrim', fibrotic)
    cache = doc.__dict__.setdefault('_style_cache', {})
    if rim_key not in cache:
        sc = '#6B3A2A' if not fibrotic else '#5E3E14'
        cache[rim_key] = doc.lingrad([(0, sc, 0.32), (0.45, sc, 0), (1, '#FFFFFF', 0)], 0, 0, 1, 1)
    rim_g = cache[rim_key]
    for i in range(-3, 4):
        for j in range(-3, 4):
            px = cx + i * sp + (sp / 2 if j % 2 else 0) + rnd.uniform(-2, 2)
            py = cy + j * sp * 0.88 + rnd.uniform(-2, 2)
            if fibrotic:
                if rnd.random() < 0.35:
                    continue
                rr = rnd.uniform(3.5, 6.2)
            else:
                rr = rnd.uniform(9.4, 10.2)
            bd = blob(px, py, rr, rr * rnd.uniform(0.8, 1.0), n=8, j=0.12, seed=i * 7 + j)
            edge = '#C98B7E' if not fibrotic else '#9E7240'
            path(doc, bd, fill=air_fill, stroke=edge, w=0.7)
            path(doc, bd, fill='none', stroke=rim_g, w=1.5 if not fibrotic else 1.1)    # recessed: shadow on the top-left inner wall
    if not fibrotic:
        for _ in range(26):
            a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r)
            rbc(doc, cx + rr * math.cos(a), cy + rr * math.sin(a), 1.1, 0.7, op=0.85)
    else:
        for k in range(30):     # collagen bundles: a few fine parallel fibrils in two tones
            x0 = cx + rnd.uniform(-r, r)
            y0 = cy + rnd.uniform(-r, r)
            ang = rnd.uniform(-0.5, 0.5)
            pts = [(x0 + t * 2.4 * math.cos(ang), y0 + t * 2.4 * math.sin(ang) + 0.7 * math.sin(t * 1.3 + k)) for t in range(7)]
            path(doc, poly_d(pts), stroke='#C99555', w=1.5, op=0.35)
            for o, c, ww in ((-0.45, '#8F5A22', 0.32), (0.05, '#A86E2C', 0.38), (0.5, '#94602A', 0.3)):
                path(doc, poly_d([(px_ - o * math.sin(ang), py_ + o * math.cos(ang)) for px_, py_ in pts]), stroke=c, w=ww, op=0.9)
            path(doc, poly_d([(px_ + 0.3 * math.sin(ang), py_ - 0.3 * math.cos(ang) - 0.25) for px_, py_ in pts]), stroke='#F2D6A8', w=0.25, op=0.8)
        for _ in range(7):      # myofibroblasts
            ex, ey = cx + rnd.uniform(-r * 0.7, r * 0.7), cy + rnd.uniform(-r * 0.7, r * 0.7)
            ro = rnd.uniform(-40, 40)
            contact_shadow(doc, ex, ey, 4.6, 1.2, rot=ro, strength=0.16)
            ell(doc, ex, ey, 4.6, 1.2, fill=shade(doc, '#8E5FB0', light=0.4, dark=0.12), stroke=tone('#8E5FB0', 0.35), w=0.25, rot=ro)
        for _ in range(8):
            ix, iy = cx + rnd.uniform(-r * 0.8, r * 0.8), cy + rnd.uniform(-r * 0.8, r * 0.8)
            circ(doc, ix, iy, 1.2, fill=shade(doc, INFL, light=0.4), stroke=tone(INFL, 0.35), w=0.2)
    lens_close(doc, cx, cy, r, '#4A6A7A' if not fibrotic else PATH)


def inflammation_lens(doc, cx, cy, r):
    lens_open(doc, cx, cy, r, AIR)
    ep = cy + 12
    rect(doc, cx - r, ep, 2 * r, r, fill=_ugrad(doc, 'linear', [(0, lighten(TISSUE, 0.2), 1), (1, darken(TISSUE, 0.06), 1)], x1=0, y1=ep, x2=0, y2=cy + r))
    path(doc, 'M%s,%s H%s' % (cx - r, ep + 13, cx + r), stroke='#E9B3A8', w=7.6)
    path(doc, 'M%s,%s H%s' % (cx - r, ep + 13, cx + r), stroke='#F6D3CB', w=5.8)
    for k in range(6):
        rbc(doc, cx - r + 6 + k * 12, ep + 13, 2.2, 1.4)
    rect(doc, cx - r, ep + 0.5, 2 * r, 2.2, fill='#5B3426', op=0.07)
    for k in range(5):
        rect(doc, cx - r + 2 + k * 14.5, ep - 5, 13, 5.5, fill=sheen(doc, '#F1D3C6', light=0.5, dark=0.08), stroke='#C98B7E', sw=0.6, r=1.4)
    path(doc, 'M%s,%s l2.5,-3 l2,4 l2.5,-3' % (fmt(cx + 15), fmt(ep - 6)), stroke=INFL, w=0.9)
    mx, my = cx - 14, ep - 12
    cell_body(doc, blob(mx, my, 11, 7, n=9, j=0.1, seed=6), mx, my, 11, 7, '#F8DCCD', '#B2594A', 1.2)
    nucleus(doc, mx - 3, my, 3, w=0.4)
    silica(doc, mx + 4, my + 1, s=0.45, rot=10)
    for (dx, dy) in [(-6, -14), (4, -18), (12, -10), (16, -20)]:
        cytokine(doc, mx + dx + 6, my + dy, s=0.95, rot=dx * 4)
    neutrophil(doc, cx + 10, cy - 12, r=5.2)
    monocyte(doc, cx + 22, cy - 2, r=5.4)
    neutrophil(doc, cx + 4, ep + 12, r=4.6)
    for (dx, dy) in [(12, -2), (18, 3), (26, -9)]:
        ros(doc, cx + dx, ep + dy - 9, s=0.85)
    lens_close(doc, cx, cy, r, INFL)


def pathology(doc):
    x, w = RX, RW
    heading(doc, x, 112, 5, 'When particles persist', 'NORA', x + w, sub='occupational silicosis and asbestosis')
    for (dx, dy, s, rt) in [(14, 150, 1.5, 10), (34, 144, 1.9, -20), (48, 158, 1.1, 40), (26, 166, 0.9, 5)]:
        silica(doc, x + dx, dy, s=s, rot=rt)
    asbestos_fibre(doc, x + 108, 156, x + 186, 140, w=3.4, color='#D6B676')
    asbestos_fibre(doc, x + 112, 166, x + 184, 156, w=2.6, color='#CDA95F')
    T(doc, x + 32, 184, 'Crystalline silica', size=S_BODY, weight=700, fill='#3E4C61', anchor='middle')
    T(doc, x + 32, 191.5, 'quarrying, stone cutting', size=5.6, fill='#3E4C61', anchor='middle')
    T(doc, x + 146, 184, 'Asbestos fibres', size=S_BODY, weight=700, fill='#6B4A12', anchor='middle')
    T(doc, x + 146, 191.5, 'insulation, construction', size=5.6, fill='#6B4A12', anchor='middle')
    PS(doc, x, 205, 'Inhaled particles reach the alveoli, where macrophages take them up but cannot digest them.', w, size=S_BODY, lh=1.18, fill=INK2)
    y = 262
    tag(doc, x, y, '5.2', PATH)
    T(doc, x + 15, y, 'Long fibres: frustrated phagocytosis', size=6.6, weight=700, fill=DPATH)
    PS(doc, x, y + 9, 'Pseudopods spread along a fibre too long to enclose, but the cup never closes: ROS and lysosomal enzymes leak out. Short fibres can be engulfed yet still persist.',
      w, size=S_BODY, lh=1.18)
    y = 404
    tag(doc, x, y, '5.3', PATH)
    T(doc, x + 15, y, 'Silica: lysosomal injury', size=6.6, weight=700, fill=DPATH)
    PS(doc, x, y + 9, 'Crystals can rupture the phagolysosome membrane. Leaked cathepsins, K⁺ efflux and ROS can activate the **NLRP3 inflammasome** → caspase-1 → IL-1β. Cells that die release the crystal, which is engulfed again.',
      w, size=S_BODY, lh=1.18, boldfill=DINFL)
    from cellmod2 import SPL
    leader(doc, [(SPL[0] + SPL[2] + 1.5, SPL[1] - 6), (RX - 7.6, y + 12)], color=DPATH, w=0.5)
    # 5.4 inflammation
    y = 482
    tag(doc, x, y, '5.4', INFL)
    T(doc, x + 15, y, 'Persistent inflammation', size=6.6, weight=700, fill=DINFL)
    inflammation_lens(doc, x + 36, y + 42, 34)
    yy = y + 14
    yy += PS(doc, x + 78, yy, '**Signalling:** IL-1β, TNF-α and chemokines recruit neutrophils and monocytes.', w - 78, size=S_BODY, lh=1.16, boldfill=DINFL) + 1.6
    PS(doc, x + 78, yy, '**Injury:** their ROS and proteases damage the epithelium; the particle stays.', w - 78, size=S_BODY, lh=1.16, boldfill=DPATH)
    # 5.5 fibrosis
    y = 596
    tag(doc, x, y, '5.5', PATH)
    T(doc, x + 15, y, 'Fibrotic remodelling', size=6.6, weight=700, fill=DPATH)
    histology(doc, x + 36, y + 42, 34, False)
    histology(doc, x + w - 36, y + 42, 34, True)
    arrow(doc, [(x + 76, y + 42), (x + w - 76, y + 42)], PATH, 'path', w=0.9, head=4.6, smooth=False, bow=0)
    T(doc, x + 36, y + 87, 'Normal lung', size=6.0, weight=700, fill='#4A6A7A', anchor='middle')
    T(doc, x + w - 36, y + 87, 'Fibrotic lung', size=6.0, weight=700, fill='#7A5320', anchor='middle')
    T(doc, x + w / 2, y + 36, 'TGF-β', size=5.6, weight=700, fill='#7A5320', anchor='middle')
    T(doc, x + w / 2, y + 53, 'PDGF', size=5.6, weight=700, fill='#7A5320', anchor='middle')
    PS(doc, x, y + 97, 'Myofibroblasts deposit **collagen**: septa thicken and stiffen, air spaces shrink and gas exchange fails.',
      w, size=S_BODY, lh=1.16, boldfill='#7A5320')


def flows(doc, engulf_y):
    # engulfment text -> nascent phagosome in the cell (2.2 -> 2.3)
    arrow(doc, [(258, engulf_y + 2), (272, engulf_y - 8), (282, 500), (280, 472)], PHAG, 'transport', w=1.0, head=4.6, opacity=0.9)
    # pathology: fibrotic lung flows into the persistence row of the take-home
    arrow(doc, [(RX + 1, BY - 39), (RX - 6, BY - 8), (RX - 5, BY + 24), (RX + 3.5, BY + 34)], PATH, 'path', w=0.45, head=3.6, bow=0.02)
    # clearance: acid hydrolysis flows into the degraded-and-recycled row
    path(doc, cr_path([(869, BY + 47), (871, BY + 27), (RX - 8, BY + 18.5), (RX + 1, BY + 16)], False), stroke=PAPER, w=2.0)
    arrow(doc, [(869, BY + 47), (871, BY + 27), (RX - 8, BY + 18.5), (RX + 3, BY + 16)], RECY, 'recycle', w=0.6, head=3.4, bow=0.02)
    # cell -> magnified panels: soft curved dashed links
    for (pts, col, end) in [([(500, 613), (492, 660), (380, 700), (236, BY + 16)], CONV, (236, BY + 16)),
                            ([(614, 689), (640, 716), (684, BY + 16)], PHAG, (684, BY + 16))]:
        c_ = mix(col, LINK, 0.55)
        path(doc, cr_path(pts, False), stroke=c_, w=0.3, op=0.75)
        circ(doc, pts[0][0], pts[0][1], 0.8, fill=c_)
        circ(doc, end[0], end[1], 0.8, fill=c_)
