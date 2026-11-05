"""Non-specialist parts of the V1.2 stage: header, section-1 intro with scale cue, conclusion (6), references,
plus small shared helpers for the module stubs (caption, placeholder)."""
import math
from lib import *
from style import shade, tone, lighten, mix
import geom as G
from layout2 import heading, NAVY, SEC, S_BODY, REFS

CAPTION = '#3F4A57'


# ===================================================================== shared helpers
def caption(doc, x, y, text, width, size=S_BODY, boldfill=None):
    """Short serif caption under a section heading.  Returns the height used."""
    return PS(doc, x, y, text, width, size=size, lh=1.2, fill=CAPTION, boldfill=boldfill)


def placeholder(doc, box, name):
    """Phase-1 stand-in for a specialist drawing area: very light dashed outline + module name."""
    x0, y0, x1, y1 = box
    rect(doc, x0, y0, x1 - x0, y1 - y0, fill='none', stroke='#B9AE9B', sw=0.35, r=3, dash='2.2 2.2', op=0.55)
    T(doc, x0 + 3, y0 + 6, name, size=4.6, fill='#A69B88', italic=True)


# ===================================================================== header
ARROW_KEY = [('transport', PHAG, 'Phagocytic route'), ('transport', BIO, 'Enzyme route'), ('fusion', CONV, 'Membrane fusion'),
             ('recycle', RECY, 'Recycling'), ('path', PATH, 'Pathological effect'), ('signal', INFL, 'Inflammatory signal')]
SPEAKERS = [(1, 'Aitor'), (2, 'Nerea · 2.7'), (3, 'Urtzi'), (4, 'Eneritz'), (5, 'Nora'), (6, 'Aitor')]


def header(doc):
    fam = resolve(SERIF, 36, 600)[0]
    doc.add('<text x="27" y="55" font-family="%s" font-size="36" font-weight="600" fill="%s" letter-spacing="-0.4">'
            'How a macrophage <tspan font-style="italic" fill="%s">destroys</tspan> what it engulfs</text>' % (fam, NAVY, '#C23A22'))
    R = 1072
    T(doc, R, 24, 'Cell Biology seminar · First-year Medicine', size=6.0, fill='#4A5563', anchor='end', family=SERIF, italic=True)
    # speaking order: badge colour = section colour
    sz, r = 6.2, 3.6
    items = []
    for n, name in SPEAKERS:
        items.append((n, name, text_width(name, sz, 600, 'serif')))
    gap, sep = 2.2, 6.5
    total = sum(2 * r + gap + w for _, _, w in items) + sep * (len(items) - 1)
    x = R - total
    y = 38
    for k, (n, name, w) in enumerate(items):
        circ(doc, x + r, y - 2.1, r, fill=SEC[n])
        T(doc, x + r, y - 2.1 + 1.6, str(n), size=4.6, weight=700, fill='#fff', anchor='middle')
        T(doc, x + 2 * r + gap, y, name, size=sz, weight=600, fill=NAVY, family=SERIF)
        x += 2 * r + gap + w + sep
    # compact 2-row arrow key
    cw = 98
    last = max(text_width(t, 5.2) for _, _, t in ARROW_KEY[2::3])
    x0 = R - 2 * cw - 18 - last
    for k, (kind, col, t) in enumerate(ARROW_KEY):
        cx = x0 + (k % 3) * cw
        cy = 56 + (k // 3) * 10
        arrow(doc, [(cx, cy - 1.7), (cx + 14, cy - 1.7)], col, kind, w=1.2 if kind != 'path' else 1.1, head=4.6, smooth=False)
        T(doc, cx + 18, cy, t, size=5.4, fill=INK)


# ===================================================================== 1: intro + scale cue
WALL_T = '#E2B7A6'      # toned alveolar wall (tissue)
WALL_L = '#A9766A'      # wall hairline
AIR_T = '#F6FAFB'       # alveolar air
CUE_INK = '#6F6457'     # cue labels


def _tube(doc, pts, w_wall, w_lumen):
    d = cr_path(pts, False)
    path(doc, d, stroke=WALL_L, w=w_wall + 0.7, cap='butt')
    path(doc, d, stroke=WALL_T, w=w_wall, cap='butt')
    path(doc, d, stroke=AIR_T, w=w_lumen, cap='butt')
    # cut end of the bronchiole: an elliptical section face (wall ring around the lumen)
    (x0, y0), (x1, y1) = pts[0], pts[1]
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    ell(doc, x0, y0, 1.6, (w_wall + 0.7) / 2, fill=WALL_T, stroke=WALL_L, w=0.35, rot=ang)
    ell(doc, x0, y0, 0.9, w_lumen / 2, fill='#DCE8EC', rot=ang)
    return d


CUE_S, CUE_T = 1.25, (-7.0, -64.0)       # the cue is drawn at 1.25x into the space freed by the text diet


def _cue_pt(x, y):
    return CUE_S * x + CUE_T[0], CUE_S * y + CUE_T[1]


def _scale_cue(doc):
    """Bronchiole -> alveolar duct -> alveolar sac; one alveolus cut open (= this scene, with a macrophage)."""
    acc = PHAG
    r, dx = 9.4, 20.0
    dy = dx * 0.866
    rows = [(176.0, [96, 116]), (176.0 + dy, [86, 106, 126]), (176.0 + 2 * dy, [96, 116, 136]), (176.0 + 3 * dy, [106, 126])]
    alv = [(x, y, r) for y, xs in rows for x in xs]
    hx, hy, hr = 146.5, 199.0, 12.4             # highlighted, cut-open alveolus (outer edge of the sac)
    group(doc, transform='matrix(%s 0 0 %s %s %s)' % (CUE_S, CUE_S, CUE_T[0], CUE_T[1]))
    _tube(doc, [(30, 153), (52, 156), (74, 166), (92, 180)], 8.4, 4.6)
    for (x, y, rr) in alv + [(hx, hy, hr)]:
        circ(doc, x, y, rr + 2.0, fill=WALL_L)
    for (x, y, rr) in alv + [(hx, hy, hr)]:
        circ(doc, x, y, rr + 1.4, fill=WALL_T)
    path(doc, cr_path([(40, 154.5), (52, 156), (74, 166), (92, 180), (106, 194)], False), stroke=AIR_T, w=4.6)
    for k, (x, y, rr) in enumerate(alv):
        g = doc.radgrad([(0, '#FFFFFF'), (0.7, AIR_T), (1, '#E9F0F2')], cx=.42, cy=.38, r=.62)
        circ(doc, x, y, rr - 0.2, fill=g)
        circ(doc, x, y, rr - 0.2, fill='none', stroke=WALL_L, w=0.25, op=0.6)
    circ(doc, hx, hy, hr + 1.4, fill=mix(acc, WALL_T, 0.45))
    g = doc.radgrad([(0, '#FFFFFF'), (0.75, mix(acc, '#FFFFFF', 0.9)), (1, mix(acc, '#FFFFFF', 0.75))], cx=.42, cy=.38, r=.62)
    circ(doc, hx, hy, hr - 0.4, fill=g)
    circ(doc, hx, hy, hr - 0.4, fill='none', stroke=acc, w=0.6)
    circ(doc, hx, hy, hr + 1.4, fill='none', stroke=acc, w=0.35, op=0.7)
    mx, my = hx - 1.0, hy + hr - 3.6
    path(doc, blob(mx, my, 4.2, 2.3, n=9, j=0.12, seed=3), fill=mix(acc, '#FFFFFF', 0.6), stroke=acc, w=0.35)
    circ(doc, mx - 0.6, my - 0.2, 1.1, fill='#8A7CC0')
    endgroup(doc)
    # labels in poster mm (3 words in total)
    s = 5.0
    T(doc, 28, 147, 'bronchiole', size=s, fill=CUE_INK, italic=True)
    T(doc, 28, 229, 'alveolar sac', size=s, fill=CUE_INK, italic=True)
    leader(doc, [_cue_pt(100, 233), (59, 227.4)], color=CUE_INK, w=0.3, dot=False)
    px, py = _cue_pt(hx + 5.5, hy + hr + 0.6)
    T(doc, px + 5, 230, 'this scene', size=5.6, weight=700, fill=acc)
    leader(doc, [(px, py), (px + 6.5, 225.5)], color=acc, w=0.35, dot=False)


def _scale_key(doc, x, y):
    """Three scales: glyph + one word + size."""
    rows = [('tissue', '~200 µm'), ('cell', '~20 µm'), ('molecules', '~10 nm')]
    for k, (word, size) in enumerate(rows):
        yy = y + k * 24
        gx, cy = x + 9, yy - 1.8
        group(doc, transform='translate(%s %s) scale(1.45)' % (fmt(gx), fmt(cy)))
        if k == 0:      # wall band: epithelium line over toned tissue with a capillary
            path(doc, 'M-7,-1.5 Q0,-3.2 7,-1.8 L7,3.4 Q0,2.2 -7,3.6 Z', fill=WALL_T)
            path(doc, 'M-7,-1.5 Q0,-3.2 7,-1.8', stroke=WALL_L, w=0.45)
            ell(doc, 1, 0.8, 3.4, 1.3, fill='#FBEAE4', stroke='#C98B7E', w=0.3)
            ell(doc, 1, 0.8, 1.2, 0.6, fill='#C0392B')
        elif k == 1:    # cell with nucleus
            path(doc, blob(0, 0, 6.4, 4.2, n=10, j=0.1, seed=5), fill='#FBE3D6', stroke='#C4806C', w=0.5)
            circ(doc, -1.3, -0.3, 1.9, fill='#D9D2F0', stroke='#6A5FA6', w=0.3)
        else:           # feathered molecular window: bilayer with one protein
            gd = doc.radgrad([(0, '#FFFFFF', 1), (0.7, '#FFFFFF', 1), (1, '#FFFFFF', 0)])
            circ(doc, 0, 0, 6.0, fill=gd)
            for dy_ in (-0.9, 0.9):
                line(doc, -4.8, dy_, 4.8, dy_, '#B5735F', 0.55)
            line(doc, -4.8, 0, 4.8, 0, '#FDEFE8', 0.5)
            ell(doc, 0.6, 0, 1.3, 2.6, fill='#3E5C86')
            circ(doc, 0, 0, 6.0, fill='none', stroke=CUE_INK, w=0.2, op=0.5)
        endgroup(doc)
        T(doc, x + 22, yy, word, size=5.8, weight=700, fill=NAVY)
        T(doc, x + 22 + text_width(word, 5.8, 700) + 3, yy, size, size=5.2, fill=CUE_INK)


def intro(doc):
    x0, y0, x1, y1 = G.INTRO
    heading(doc, x0, G.INTRO_HEAD_Y, 1, 'Alveolar macrophage')
    _scale_cue(doc)
    _scale_key(doc, 210, 172)


# ===================================================================== 6: conclusion
CONCLUSION = 'Two routes converge to destroy; when the cargo persists, the same machinery injures the lung.'


def conclusion(doc):
    # closing statement under the healthy septum (left), where the wall is thin and the paper is open
    y, x = 829, 25
    sz, r = 8.4, 5.2
    circ(doc, x + r, y - 2.8, r, fill=SEC[6])
    T(doc, x + r, y - 2.8 + 2.4, '6', size=6.8, weight=600, fill='#fff', anchor='middle', family=SERIF)
    T(doc, x + 2 * r + 5, y, CONCLUSION, size=sz, fill=NAVY, family=SERIF, italic=True)


# ===================================================================== references
def references(doc):
    y0 = G.REFS_Y + 4.2
    sz, lh = 3.2, 1.16
    cols, gap = 3, 14
    cw = (1075 - 25 - gap * (cols - 1)) / cols
    per = int(math.ceil(len(REFS) / cols))
    for c in range(cols):
        yy = y0
        x = 25 + c * (cw + gap)
        for i in range(per):
            n = c * per + i
            if n >= len(REFS):
                break
            T(doc, x, yy, '%d' % (n + 1), size=sz, weight=700, fill='#776E5C')
            hh = P(doc, x + 5, yy, REFS[n], cw - 5, size=sz, lh=lh, fill='#6B6455')
            yy += hh + 0.5
    T(doc, 1075, G.REFS_Y - 2.4, 'Original illustration · schematic, not to scale', size=3.4, italic=True, fill='#8A8170', anchor='end')
