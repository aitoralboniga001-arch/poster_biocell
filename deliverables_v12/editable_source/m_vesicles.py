"""Section 4 fusion strip (magnified from site 4) and section 2.7 maturation/killing strip (magnified from 2.3-2.6),
both in the lower left column.  V1.2 phase 2 (vesicle specialist).

Both strips are drawn at one molecular scale: a bilayer is BW = 4.4 mm thick (~5 nm, so ~0.9 mm per nm).  Each strip is
one continuous membrane scene read left -> right in time, feathered into the paper by an in-module mask (no frame)."""
import math
from lib import *
from style import shade, spec, tone, lighten, darken, mix, contact_shadow
import geom as G
from layout2 import heading, NAVY
from lenses import beam, LINK
from bio import hplus, enzyme_dot

BW = 4.4                     # bilayer thickness (mm), both strips
MOL = G.MOL
PH_MEM = '#C23B2A'           # late phagosome membrane (cell: LE_STROKE)
LY_MEM = '#6F36A8'           # lysosome membrane (cell: LY_STROKE)
NP_MEM = '#D9563A'           # nascent / early phagosome membrane
CYT = '#FBE9DE'              # cytosol tint
LUM_PH = '#F7D9CF'           # late phagosome lumen
LUM_LY = '#E7DAF4'           # lysosome / phagolysosome lumen
RAB7 = MOL['Rab7']
ARL8 = '#9B6A3C'
HOPS = MOL['HOPS']
QA, QB, QC, RS = MOL['Qa_syntaxin7'], MOL['Qb_Vti1b'], MOL['Qc_syntaxin8'], MOL['R_VAMP7']
NSF = '#6E7787'
VATP = MOL['VATPase']
NOX = MOL['NOX2']
HYD = MOL['hydrolase']
RAC = '#8A4F6A'
LAB = 4.4                    # molecule label size (>= 4.2)
STEP = '#7D7466'             # quiet step-letter colour
NOTE = '#5E5648'             # neutral annotation ink


# ===================================================================== small helpers
def _ug(doc, kind, stops, **a):
    gid = doc.uid('vg')
    st = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (fmt(o), c, fmt(op)) for o, c, op in stops)
    at = ' '.join('%s="%s"' % (k, fmt(v)) for k, v in a.items())
    doc.defs.append('<%sGradient id="%s" gradientUnits="userSpaceOnUse" %s>%s</%sGradient>' % (kind, gid, at, st, kind))
    return 'url(#%s)' % gid


def _lum(c):
    v = []
    for i in (1, 3, 5):
        u = int(c[i:i + 2], 16) / 255
        v.append(u / 12.92 if u <= 0.03928 else ((u + 0.055) / 1.055) ** 2.4)
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def ink(c, ratio=4.6, bg=PAPER):
    """Darken a label colour (same hue) until it reaches the contrast ratio on the paper."""
    lb = _lum(bg)
    k = 0.0
    out = c
    while (lb + 0.05) / (_lum(out) + 0.05) < ratio and k < 0.9:
        k += 0.03
        out = darken(c, k)
    return out


def halo(doc, pts, side, color, depth=15.0, op=0.6, n=9):
    """Soft lumen tint hugging a membrane on one side (side=+1/-1 along the polyline normal), fading to paper."""
    st = depth / n
    for k in range(n):
        off = side * (BW / 2 + st * (k + 0.5))
        o = offset_poly(pts, off, closed=False)
        a = max(0.004, op * (1 - k / n) ** 1.6)
        path(doc, poly_d(o), stroke=color, w=st * 1.15, cap='butt', op=round(a, 3))


def curved_link(doc, pts, color, op0=0.7, op1=0.12, w=0.25):
    """Fine focus hairline routed as a smooth curve through empty cytoplasm, fading toward the strip."""
    col = mix(color, LINK, 0.55)
    p, q = pts[0], pts[-1]
    g = _ug(doc, 'linear', [(0, col, op0), (1, col, op1)], x1=p[0], y1=p[1], x2=q[0], y2=q[1])
    path(doc, cr_path(pts, False), stroke=g, w=w, cap='butt')


def _strip_open(doc, x0, y0, x1, y1, fx=14, fy=None):
    """Frameless capsule: content fades into the paper over fx at the ends and fy at the top and bottom."""
    hx = _ug(doc, 'linear', [(0, '#fff', 0), (fx / (x1 - x0), '#fff', 1), (1 - fx / (x1 - x0), '#fff', 1), (1, '#fff', 0)],
             x1=x0, y1=0, x2=x1, y2=0)
    hy = _ug(doc, 'linear', [(0, '#fff', 0), (fy / (y1 - y0), '#fff', 1), (1 - fy / (y1 - y0), '#fff', 1), (1, '#fff', 0)],
             x1=0, y1=y0, x2=0, y2=y1) if fy else None
    if not fy:                       # no vertical fade: let the content (which fades by itself) breathe past the box
        y0, y1 = y0 - 25, y1 + 25
    ids = []
    for g in ((hx, hy) if fy else (hx,)):
        mid = doc.uid('vm')
        doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
                        '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/></mask>' % (
                            mid, fmt(x0), fmt(y0), fmt(x1 - x0), fmt(y1 - y0), fmt(x0), fmt(y0), fmt(x1 - x0), fmt(y1 - y0), g))
        ids.append(mid)
    doc.add(''.join('<g mask="url(#%s)">' % i for i in ids))
    doc._vstrip_depth = len(ids)


def _oval_open(doc, cx, cy, rx, ry, lx0=None):
    """Organic, frameless vignette: a wide elliptical feather (no straight edges), so the scene emerges from the paper."""
    c = doc.__dict__.setdefault('_style_cache', {})
    if 'vfeather' not in c:
        gid = doc.uid('vf')
        doc.defs.append('<radialGradient id="%s" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff"/>'
                        '<stop offset="0.78" stop-color="#fff"/><stop offset="0.9" stop-color="#fff" stop-opacity="0.5"/>'
                        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>' % gid)
        c['vfeather'] = gid
    mid = doc.uid('vm')
    doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s"><ellipse cx="%s" cy="%s" '
                    'rx="%s" ry="%s" fill="url(#%s)"/></mask>' % (mid, fmt(cx - rx), fmt(cy - ry), fmt(2 * rx), fmt(2 * ry),
                                                                fmt(cx), fmt(cy), fmt(rx), fmt(ry), c['vfeather']))
    doc.add('<g mask="url(#%s)">' % mid)
    doc._vstrip_depth = 1
    if lx0 is not None:              # extra soft fade so the left ends dissolve inside the column edge
        g = _ug(doc, 'linear', [(0, '#fff', 0), (1, '#fff', 1)], x1=lx0, y1=0, x2=lx0 + 12, y2=0)
        m2 = doc.uid('vm')
        doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s"><rect x="%s" y="%s" '
                        'width="%s" height="%s" fill="%s"/></mask>' % (m2, fmt(lx0), fmt(cy - ry), fmt(2 * rx), fmt(2 * ry),
                                                                     fmt(lx0), fmt(cy - ry), fmt(2 * rx), fmt(2 * ry), g))
        doc.add('<g mask="url(#%s)">' % m2)
        doc._vstrip_depth = 2


def _strip_close(doc):
    doc.add('</g>' * getattr(doc, '_vstrip_depth', 2))


def _interp(poly, x):
    for (xa, ya), (xb, yb) in zip(poly, poly[1:]):
        if min(xa, xb) <= x <= max(xa, xb):
            return ya + (yb - ya) * ((x - xa) / ((xb - xa) or 1e-9))
    return poly[0][1] if x < poly[0][0] else poly[-1][1]


def _paint(doc, spec_, f):
    """spec_ is a hex colour or ('v', c_top, c_bot, y0, y1) / ('h', c_left, c_right, x0, x1): apply f to the colour(s)."""
    if isinstance(spec_, str):
        return f(spec_)
    k, ca, cb, a, b = spec_
    if k == 'v':
        return _ug(doc, 'linear', [(0, f(ca), 1), (1, f(cb), 1)], x1=0, y1=a, x2=0, y2=b)
    return _ug(doc, 'linear', [(0, f(ca), 1), (1, f(cb), 1)], x1=a, y1=0, x2=b, y2=0)


def bilayers(doc, mems, beads_skip=()):
    """Several bilayers drawn pass by pass (shadow, leaflets, core, head groups) so where they meet the leaflets merge.
    mems: list of (dense polyline, colour spec, cap).  beads_skip: [(x, y, r)] zones without head-group beads."""
    for pts, c, cap in mems:
        d = poly_d(pts)
        doc.add('<g transform="translate(0.5 0.8)">')
        path(doc, d, stroke='#5B3426', w=BW + 0.5, cap=cap, op=0.08)
        doc.add('</g>')
    for pts, c, cap in mems:
        path(doc, poly_d(pts), stroke=_paint(doc, c, lambda q: tone(q, 0.16)), w=BW + 0.35, cap=cap)
    for pts, c, cap in mems:
        path(doc, poly_d(pts), stroke=_paint(doc, c, lambda q: lighten(q, 0.12)), w=BW - 0.35, cap=cap)
    for pts, c, cap in mems:
        path(doc, poly_d(pts), stroke=_paint(doc, c, lambda q: lighten(q, 0.88)), w=1.45, cap=cap)
    for pts, c, cap in mems:
        for off in (-1.5, 1.5):
            o = offset_poly(pts, off, closed=False)
            o = resample(o, 0.4, closed=False)
            segs, cur = [], []
            for p in o:
                if any(math.hypot(p[0] - sx, p[1] - sy) < sr for sx, sy, sr in beads_skip):
                    if len(cur) > 1:
                        segs.append(cur)
                    cur = []
                else:
                    cur.append(p)
            if len(cur) > 1:
                segs.append(cur)
            for s in segs:
                path(doc, poly_d(s), stroke=_paint(doc, c, lambda q: tone(q, 0.42)), w=0.95, dash='0.01 1.75', op=0.9)


def glob(doc, x, y, rx, ry, color, rot=0, light=0.5, w=0.32, sp=True):
    """Volumetric protein domain lit from the top-left."""
    ell(doc, x, y, rx, ry, fill=shade(doc, color, light=light, dark=0.16), stroke=tone(color, 0.42), w=w, rot=rot)
    if sp and min(rx, ry) >= 1.6:
        spec(doc, x, y, min(rx, ry), a0=205, a1=245, op=0.55, inset=0.6, w=max(0.3, min(rx, ry) * 0.16))


def rod(doc, pts, color, w=1.2, smooth=True):
    d = cr_path(pts, False) if (smooth and len(pts) > 2) else poly_d(pts)
    path(doc, d, stroke=tone(color, 0.38), w=w + 0.4)
    path(doc, d, stroke=color, w=w)
    path(doc, d, stroke=lighten(color, 0.5), w=w * 0.3, op=0.7, extra='transform="translate(-0.12 -0.18)"')


def coil(doc, pts, color, amp=0.7, lam=1.9, w=0.85, phase=0.0, ramp=None):
    """Helix drawn as a sine ribbon along a polyline; ramp(t) scales the amplitude along the path (0..1)."""
    dense = resample(cr_sample(pts, closed=False, per=12) if len(pts) > 2 else pts, 0.22, closed=False)
    nm = normals(dense, closed=False)
    L = poly_len(dense) or 1
    out, s = [], 0.0
    for i, (p, n) in enumerate(zip(dense, nm)):
        if i:
            s += math.hypot(p[0] - dense[i - 1][0], p[1] - dense[i - 1][1])
        a = amp * (ramp(s / L) if ramp else 1) * math.sin(2 * math.pi * s / lam + phase)
        out.append((p[0] + n[0] * a, p[1] + n[1] * a))
    d = poly_d(out)
    path(doc, d, stroke=tone(color, 0.38), w=w + 0.38)
    path(doc, d, stroke=color, w=w)
    path(doc, poly_d([(x - 0.08, y - 0.16) for x, y in out]), stroke=lighten(color, 0.55), w=w * 0.28, op=0.75)


def tmd(doc, x, y, color, ang=90, h=BW + 0.6, w=1.25):
    """Transmembrane helix across a bilayer centred at (x, y); ang = membrane normal direction (deg)."""
    a = math.radians(ang)
    dx, dy = math.cos(a) * h / 2, math.sin(a) * h / 2
    rod(doc, [(x - dx, y - dy), (x + dx, y + dy)], color, w=w, smooth=False)


_LATER = []


def lab(doc, x, y, s, color, size=LAB, weight=600, anchor='start', halo=None, italic=False):
    """Labels are queued and drawn after the strip mask closes, so the feathered edges never fade them."""
    _LATER.append((x, y, s, dict(size=size, weight=weight, fill=color, anchor=anchor, halo=halo, italic=italic)))


def _flush(doc):
    for x, y, s, k in _LATER:
        k = dict(k)
        k['fill'] = ink(k['fill'])
        T(doc, x, y, s, **k)
    del _LATER[:]


def step(doc, x, y, letter, title):
    T(doc, x, y, letter, size=5.4, weight=400, fill=ink(STEP), italic=True, family=SERIF)
    T(doc, x + 4.2, y, title, size=4.6, weight=600, fill=ink(STEP), spacing=0.15)


def source_ring(doc, c, r, color):
    circ(doc, c[0], c[1], r, fill='none', stroke=mix(color, LINK, 0.45), w=0.3, op=0.85)


def focus(doc, c, r, p_a, p_b, color):
    """Two fine focus hairlines from a source ring (perpendicular to the mean direction) to two points on a strip edge."""
    x, y = c
    mx, my = (p_a[0] + p_b[0]) / 2, (p_a[1] + p_b[1]) / 2
    base = math.atan2(my - y, mx - x)
    sa = (x + r * math.cos(base - math.pi / 2), y + r * math.sin(base - math.pi / 2))
    sb = (x + r * math.cos(base + math.pi / 2), y + r * math.sin(base + math.pi / 2))
    if math.hypot(sa[0] - p_a[0], sa[1] - p_a[1]) + math.hypot(sb[0] - p_b[0], sb[1] - p_b[1]) > \
            math.hypot(sa[0] - p_b[0], sa[1] - p_b[1]) + math.hypot(sb[0] - p_a[0], sb[1] - p_a[1]):
        sa, sb = sb, sa
    beam(doc, (sa, p_a, p_b, sb), color, a=(x, y), b=(mx, my))


def _hops(doc, pts, cradle=False):
    """HOPS: elongated, arched hexamer (~30 nm) drawn as a chain of lobes; with cradle=True the middle lobe (Vps33,
    the SM subunit that templates the SNAREs) is lighter."""
    dense = cr_sample(pts, closed=False, per=10)
    path(doc, cr_path(pts, False), stroke=tone(HOPS, 0.35), w=3.6, op=0.35)
    n = 7
    for k in range(n):
        t = (k + 0.5) / n
        x, y, ang = pt_on(dense, t)
        r = 2.25 + 0.35 * math.sin(math.pi * t)
        col = lighten(HOPS, 0.3) if (cradle and k == 3) else HOPS
        glob(doc, x, y, r * 1.12, r * 0.9, col, rot=ang, light=0.48)


ZS = 1.13                   # V1.2b: captions are gone, both strips are drawn 13 % larger (same factor -> same molecular scale)
ZX = 146.0                  # horizontal pivot of the enlargement


def _zoom_open(doc, y_from, y_to):
    """Enlarge everything drawn until _zoom_close by ZS about x = ZX, moving strip-coordinate y_from to poster y_to."""
    doc.add('<g transform="translate(%s %s) scale(%s)">' % (fmt(ZX - ZX * ZS), fmt(y_to - y_from * ZS), fmt(ZS)))
    return lambda q: (ZX + (q[0] - ZX) * ZS, y_to + (q[1] - y_from) * ZS)


# ===================================================================== 4: docking and fusion
def fusion(doc):
    x0, y0, x1, y1 = G.FUSION
    heading(doc, x0, 510, 4, 'Fusion')
    SX0, SX1, SY0, SY1 = 25, 263, 523, 619
    M = 572.0

    # ---------------------------------------------------------------- membrane geometry (bilayer mid-planes)
    top_c = [(10, M - 20.5), (40, M - 19.5), (70, M - 18), (96, M - 15.5), (120, M - 11.2), (138, M - 7.6), (152, M - 4.9),
             (161, M - 3.6), (167, M - 2.2), (171.5, M)]
    TOP = [q for q in cr_sample(top_c, closed=False, per=14) if q[0] >= 38]
    BOT = [(x, 2 * M - y) for x, y in TOP]
    J = (171.5, M)
    DIA = [(171.5, M), (176, M), (182.5, M)]                      # hemifusion diaphragm; the pore opens at its right end
    rim_c = [(275, M - 25), (252, M - 16), (232, M - 10), (217, M - 6.4), (209.5, M - 4.2), (206.3, M - 1.6), (206, M)]
    RT = cr_sample(rim_c, closed=False, per=14)
    RT = [q for q in RT if q[0] <= 262]
    RIM = RT + [(x, 2 * M - y) for x, y in reversed(RT[:-1])]

    def top_s(x):                                              # cytosolic surface of the phagosome membrane
        return _interp(TOP, x) + BW / 2

    def bot_s(x):                                              # cytosolic surface of the lysosome membrane
        return _interp(BOT, x) - BW / 2

    def rt_s(x):
        return _interp(RT, x) + BW / 2

    def rb_s(x):
        return 2 * M - _interp(RT, x) - BW / 2

    xf = _zoom_open(doc, 524.0, 517.0)
    _oval_open(doc, 146, M, 116, 62, lx0=37)
    # lumens: tinted only near their membranes, fading to paper (late phagosome above, lysosome below)
    lum_ph = mix(LUM_PH, '#E8A595', 0.35)
    lum_ly = mix(LUM_LY, '#B79BDB', 0.35)
    halo(doc, [p for p in TOP if p[0] < 172], 1, lum_ph, depth=15, op=0.75)
    halo(doc, [p for p in BOT if p[0] < 172], -1, lum_ly, depth=15, op=0.75)
    halo(doc, RIM, -1, lum_ly, depth=15, op=0.75)
    halo(doc, DIA, 1, mix(lum_ph, lum_ly, 0.5), depth=8, op=0.6)
    halo(doc, DIA, -1, lum_ly, depth=8, op=0.6)
    # cytosol pockets (bounded by the membranes themselves)
    cyt = mix(CYT, PAPER, 0.1)
    path(doc, poly_d(TOP + BOT[::-1], True), fill=cyt)
    path(doc, poly_d(RIM, True), fill=cyt)

    def lum_below(x, d):
        yb = _interp(BOT, x) if x < 172 else (2 * M - _interp(RT, x) if x > 206 else M)
        return yb + BW / 2 + d
    # lumen contents near the membranes: hydrolases + H+ in the lysosome, a few in the phagosome after the pore
    for (hx, d) in [(40, 7), (62, 11), (92, 6), (122, 10), (150, 6.5), (176, 9), (248, 8), (110, 13)]:
        enzyme_dot(doc, hx, lum_below(hx, d), 1.7, HYD)
    for (hx, d) in [(50, 4), (80, 8), (137, 10), (163, 4), (240, 3.5)]:
        hplus(doc, hx, lum_below(hx, d), 0.85)
    for (hx, hy) in [(213, 556), (203, 550)]:
        enzyme_dot(doc, hx, hy, 1.6, HYD)
    for (hx, hy) in [(244, 556)]:
        hplus(doc, hx, hy, 0.8)
    # ---------------------------------------------------------------- membranes
    mc = ('v', PH_MEM, LY_MEM, M - 5, M + 5)
    bilayers(doc, [(TOP, PH_MEM, 'butt'), (BOT, LY_MEM, 'butt'), (DIA, mc, 'round'), (RIM, mc, 'butt')],
             beads_skip=[(J[0] - 1, J[1], 6.5), (182.5, M, 2.6)])

    # ---------------------------------------------------------------- (a) tethering
    rx, ax = 54, 57
    ry = top_s(rx) + 2.6
    rod(doc, [(rx - 0.6, top_s(rx) - 1.6), (rx, ry - 1.4)], tone(RAB7, 0.1), w=0.55)           # prenyl anchor
    glob(doc, rx, ry, 3.0, 2.6, RAB7)
    circ(doc, rx + 1.7, ry + 1.2, 0.9, fill='#F4C542', stroke='#8A6A10', w=0.2)              # GTP
    ay = bot_s(ax) - 2.5
    rod(doc, [(ax + 0.6, bot_s(ax) + 1.6), (ax, ay + 1.3)], tone(ARL8, 0.1), w=0.55)
    glob(doc, ax, ay, 2.9, 2.5, ARL8)
    circ(doc, ax + 1.7, ay - 1.1, 0.9, fill='#F4C542', stroke='#8A6A10', w=0.2)
    _hops(doc, [(rx + 2.2, ry + 2.8), (rx + 7.5, ry + 6.0), (rx + 10.2, M - 3.5), (rx + 10.6, M + 3.0), (ax + 7.2, ay - 6.4),
                (ax + 2.3, ay - 2.8)])
    lab(doc, rx - 3.8, ry + 1.6, 'Rab7', RAB7, anchor='end')
    lab(doc, ax - 3.8, ay + 1.6, 'Arl8b', ARL8, anchor='end')
    lab(doc, rx + 14.0, M + 5.0, 'HOPS', HOPS)
    # unpaired SNAREs waiting on each membrane
    for k, (sx, c) in enumerate(((80, QA), (85.5, QB), (91, QC))):
        sy = _interp(TOP, sx)
        tmd(doc, sx, sy, c)
        coil(doc, [(sx, top_s(sx)), (sx + 0.4, top_s(sx) + 4), (sx - 0.4, top_s(sx) + 9.5)], c, amp=0.45, lam=1.6, w=0.8, phase=k)
        if k == 0:                                             # syntaxin-7 Habc domain
            glob(doc, sx - 2.6, top_s(sx) + 9.6, 1.9, 2.6, c, rot=-15)
    sx = 87.5
    tmd(doc, sx, _interp(BOT, sx), RS)
    coil(doc, [(sx, bot_s(sx)), (sx - 0.4, bot_s(sx) - 4.5), (sx + 0.4, bot_s(sx) - 10)], RS, amp=0.45, lam=1.6, w=0.8)
    glob(doc, sx + 0.3, bot_s(sx) - 12.4, 2.2, 2.0, RS)        # longin domain

    # ---------------------------------------------------------------- (b) HOPS-chaperoned trans-SNARE zippering
    hx_t, hx_b = 104.0, 105.5
    r2y = top_s(hx_t) + 2.5
    rod(doc, [(hx_t - 0.6, top_s(hx_t) - 1.6), (hx_t, r2y - 1.3)], tone(RAB7, 0.1), w=0.55)
    glob(doc, hx_t, r2y, 2.9, 2.5, RAB7)
    a2y = bot_s(hx_b) - 2.4
    rod(doc, [(hx_b + 0.6, bot_s(hx_b) + 1.6), (hx_b, a2y + 1.3)], tone(ARL8, 0.1), w=0.55)
    glob(doc, hx_b, a2y, 2.8, 2.4, ARL8)
    # the bundle: N-terminal half zipped (left), C-terminal halves still splayed toward their membranes
    bx0, bz, bc = 109.5, 119.0, 128.0
    offs = (-1.35, -0.45, 0.45, 1.35)
    cols = (QA, QB, QC, RS)
    ends = [(bc + 1.0, top_s(bc + 1.0)), (bc + 3.4, top_s(bc + 3.4)), (bc + 5.8, top_s(bc + 5.8)), (bc + 3.0, bot_s(bc + 3.0))]
    _hops(doc, [(hx_t - 0.6, r2y + 2.6), (hx_t - 5.0, M - 7.5), (hx_t - 6.6, M), (hx_b - 7.0, M + 6.5), (hx_b - 1.0, a2y - 2.6)])
    glob(doc, bx0 - 3.0, M - 0.3, 2.9, 2.5, lighten(HOPS, 0.32), light=0.45)          # Vps33 (SM subunit) templating the bundle
    for i, (o, c, e) in enumerate(zip(offs, cols, ends)):
        p = [(bx0, M + o), (bz, M + o), ((bz + e[0]) / 2 + 1.5, (M + o + e[1]) / 2 + (1.0 if i < 3 else -1.0)), e]
        b = (bz - bx0) / (poly_len(p) or 1)
        coil(doc, p, c, amp=0.6, lam=1.9, w=0.85, phase=i * math.pi / 2,
             ramp=lambda t, b=b: 1.0 if t < b else max(0.35, 1 - (t - b) * 2.2))
    for i, e in enumerate(ends):
        tmd(doc, e[0], e[1] + (-BW / 2 if i < 3 else BW / 2), cols[i])
    lab(doc, bx0 + 0.4, M + 7.4, 'N', NOTE, size=4.4)
    arrow(doc, [(bx0 + 4.2, M + 5.9), (bz + 2.0, M + 5.9)], NOTE, 'transport', w=0.42, head=2.0, smooth=False, bow=0)
    lab(doc, bz + 2.8, M + 7.4, 'C', NOTE, size=4.4)
    # fully zipped trans-complex pulls the bilayers into contact
    zx0, zx1 = 138.0, 150.0
    for i, (o, c) in enumerate(zip(offs, cols)):
        e = (zx1 + 2.0 + (i % 3) * 0.8, top_s(zx1 + 2.0 + (i % 3) * 0.8) if i < 3 else bot_s(zx1 + 2.4))
        coil(doc, [(zx0, M + o * 0.85), (zx1 - 1, M + o * 0.85), e], c, amp=0.55, lam=1.9, w=0.8, phase=i * math.pi / 2)
    for i in range(4):
        xx = zx1 + 2.0 + (i % 3) * 0.8 if i < 3 else zx1 + 2.4
        tmd(doc, xx, _interp(TOP, xx) if i < 3 else _interp(BOT, xx), cols[i], h=BW + 0.4, w=1.05)

    # ---------------------------------------------------------------- (c) hemifusion -> fusion pore, contents mix
    for (px, py) in [(194, M + 4.5), (197.5, M - 3.0)]:
        enzyme_dot(doc, px, py, 1.7, HYD)
    hplus(doc, 190.5, M - 1.0, 0.85)
    hplus(doc, 200.5, M + 1.6, 0.85)
    arrow(doc, [(186.5, M + 9.5), (188.5, M - 10.5)], HYD, 'transport', w=0.75, head=3.0, bow=0.12)




    # ---------------------------------------------------------------- (d) NSF + alpha-SNAP recycle the cis-SNARE complex
    cx0, cx1 = 225.0, 238.0
    by = rb_s(232) - 1.3
    for i, (o, c) in enumerate(zip(offs, cols)):
        coil(doc, [(cx0, by + o * 0.55 - 0.6), (cx1, by + o * 0.55 - 0.6), (cx1 + 2.6, rb_s(cx1 + 2.6) + 0.4)], c, amp=0.5, lam=1.9,
             w=0.72, phase=i * math.pi / 2)
    for i in range(2):
        xx = cx1 + 2.4 + i * 1.3
        tmd(doc, xx, 2 * M - _interp(RT, xx), cols[i * 3], w=0.95)
    for k in range(3):                                          # alpha-SNAPs coating the bundle
        glob(doc, cx0 + 2.5 + k * 4.4, by - 3.9, 1.4, 2.7, '#A3AAB8', rot=12, sp=False)
    ny = by - 12.6
    for row, (yy, rr) in enumerate(((ny + 3.1, 2.15), (ny - 1.4, 2.3))):   # NSF hexamer, side view: D1 and D2 rings
        for k in (-1, 0, 1):
            glob(doc, cx0 + 6.9 + k * 4.2, yy, rr, rr * 0.92, NSF if row else tone(NSF, -0.18), light=0.45)
    lab(doc, 228.0, M - 21.0, 'NSF', tone(NSF, 0.2), anchor='middle')
    leader(doc, [(229.5, M - 18.6), (231.0, M - 8.5)], color='#8A8170', w=0.25, dot=False)
    lab(doc, 222.0, M + 22.0, 'α-SNAP', tone(NSF, 0.2), anchor='middle')
    leader(doc, [(225.0, M + 18.2), (227.6, by - 3.6)], color='#8A8170', w=0.25, dot=False)

    # a released, recycled SNARE
    coil(doc, [(244.5, rt_s(244.5) + 0.2), (246.5, rt_s(246.5) + 4.0), (249.5, rt_s(249.5) + 6.5)], QB, amp=0.4, lam=1.6, w=0.75)
    tmd(doc, 244.5, _interp(RT, 244.5), QB, w=0.95)

    _strip_close(doc)
    _flush(doc)
    # ---------------------------------------------------------------- labels outside the mask
    step(doc, 42, 529.5, 'a', 'tether')
    step(doc, 104, 529.5, 'b', 'zipper')
    step(doc, 176, 529.5, 'c', 'pore')
    step(doc, 222, 529.5, 'd', 'recycle')


    xq = 66
    for k, (s, c) in enumerate((('syntaxin-7', QA), ('Vti1b', QB), ('syntaxin-8', QC))):
        lab(doc, xq, 539.5, s, tone(c, 0.15), size=4.4)
        xq += text_width(s, 4.4, 600) + 3.2
    lab(doc, 78, 612.0, 'VAMP7', tone(RS, 0.12), size=4.4)
    leader(doc, [(86.0, 608.4), (87.5, _interp(BOT, 87.5) + 2.4)], color=tone(RS, 0.12), w=0.25, dot=False)
    _flush(doc)
    doc.add('</g>')
    # focus link from site 4
    c4 = G.FUSION_4
    source_ring(doc, c4, 8.5, HOPS)
    cx, cy = c4[0], c4[1]
    # leave the ring at its lower right, slip between lysosome L1 and the "4" badge, then pass below 2.5 through empty cytoplasm
    routes = [(10, [(520, 648.6), (531, 648.8), (537, 666), (527, 697), (490, 712), (430, 714), (360, 712), (300, 688), (270, 630),
                    xf((250, 572))]),
              (35, [(520, 650.6), (533, 652.4), (542, 668), (532, 702), (494, 718), (430, 720), (358, 718), (295, 693), (264, 632),
                    xf((250, 600))])]
    for a, rest in routes:
        p0 = (cx + 8.5 * math.cos(math.radians(a)), cy + 8.5 * math.sin(math.radians(a)))
        curved_link(doc, [p0] + rest, HOPS)


# ===================================================================== 2.7: killing and digestion
def killing(doc):
    x0, y0, x1, y1 = G.KILL
    heading(doc, x0, 641, 2, 'Killing', label='2.7')
    SX0, SX1, SY0, SY1 = 25, 263, 656, 745
    MK = 690.0
    MEM = [(x, MK) for x in range(40, 262, 4)]
    mc = ('h', NP_MEM, CONV, 108, 140)

    xf = _zoom_open(doc, 656.0, 648.5)
    _oval_open(doc, 146, MK + 8, 116, 58, lx0=37)
    # cytosol glow above, lumen glow below carrying the pH tint ramp (near-neutral -> acid); both fade to paper
    cg = _ug(doc, 'linear', [(0, '#fff', 0), (0.55, '#fff', 0.5), (1, '#fff', 1)], x1=0, y1=MK - 22, x2=0, y2=MK)
    lg = _ug(doc, 'linear', [(0, '#fff', 1), (0.35, '#fff', 0.7), (1, '#fff', 0)], x1=0, y1=MK, x2=0, y2=MK + 44)
    for gid_, (ya, yb) in ((cg, (MK - 22, MK)), (lg, (MK, MK + 44))):
        mid = doc.uid('vm')
        doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="0" y="%s" width="1100" height="%s"><rect x="0" y="%s" width="1100" '
                        'height="%s" fill="%s"/></mask>' % (mid, fmt(ya), fmt(yb - ya), fmt(ya), fmt(yb - ya), gid_))
        doc.add('<g mask="url(#%s)">' % mid)
        if ya < MK:
            rect(doc, SX0, ya, SX1 - SX0, yb - ya, fill=mix(CYT, '#F3C9B5', 0.25))
        else:
            lum = _ug(doc, 'linear', [(0, '#EFE6D6', 1), (0.25, '#F5D7B8', 1), (0.45, '#F2C6BC', 1), (0.7, '#E2C2E6', 1),
                                      (1, '#D6BDEB', 1)], x1=SX0, y1=0, x2=SX1, y2=0)
            rect(doc, SX0, ya, SX1 - SX0, yb - ya, fill=lum)
        doc.add('</g>')
    bilayers(doc, [(MEM, mc, 'butt')])
    cs = MK - BW / 2                                            # cytosolic surface

    # ---------------------------------------------------------------- early: NOX2 oxidative burst
    gx = 66.0
    _bact_rod(doc, 40, 124, MK + 31.5, 14.0)

    # gp91phox + p22phox in the membrane
    path(doc, 'M%s,%s h%s a2,2 0 0 1 2,2 v%s a2,2 0 0 1 -2,2 h%s a2,2 0 0 1 -2,-2 v%s a2,2 0 0 1 2,-2 Z' % (
        fmt(gx - 3.4), fmt(MK - 4.4), fmt(6.8), fmt(4.8), fmt(-6.8), fmt(-4.8)),
        fill=shade(doc, NOX, light=0.42, dark=0.16), stroke=tone(NOX, 0.42), w=0.32)
    glob(doc, gx + 1.0, MK - 7.6, 4.4, 2.9, tone(NOX, -0.12))                 # gp91 dehydrogenase (FAD / NADPH) domain
    path(doc, 'M%s,%s h%s a1.4,1.4 0 0 1 1.4,1.4 v%s a1.4,1.4 0 0 1 -1.4,1.4 h%s a1.4,1.4 0 0 1 -1.4,-1.4 v%s a1.4,1.4 0 0 1 1.4,-1.4 Z' % (
        fmt(gx + 6.6), fmt(MK - 3.4), fmt(1.6), fmt(4.0), fmt(-1.6), fmt(-4.0)),
        fill=shade(doc, lighten(NOX, 0.35), light=0.4, dark=0.12), stroke=tone(NOX, 0.4), w=0.3)
    # cytosolic subunits: p67phox on the dehydrogenase, p47phox on p22, p40phox above, Rac-GTP at the membrane
    glob(doc, gx + 10.4, MK - 8.0, 2.3, 3.4, tone(NOX, 0.12), rot=-18)               # p47
    glob(doc, gx - 1.6, MK - 13.6, 3.6, 2.8, lighten(NOX, 0.18))                     # p67
    glob(doc, gx + 4.8, MK - 15.4, 2.3, 2.1, lighten(NOX, 0.4))                      # p40
    rod(doc, [(gx - 9.4, cs + 1.0), (gx - 8.7, MK - 6.6)], RAC, w=0.55)
    glob(doc, gx - 8.0, MK - 9.4, 2.6, 2.3, RAC)                                     # Rac-GTP
    circ(doc, gx - 6.6, MK - 8.2, 0.85, fill='#F4C542', stroke='#8A6A10', w=0.2)
    # electron path NADPH -> FAD -> two hemes -> O2
    circ(doc, gx + 1.6, MK - 7.4, 1.0, fill='#F2D35B', stroke='#8A6A10', w=0.22)     # FAD
    for hy in (MK - 1.6, MK + 1.6):
        doc.add('<rect x="%s" y="%s" width="2.2" height="1.1" rx="0.3" fill="#B3262E" stroke="#5E0F19" stroke-width="0.2"/>' % (
            fmt(gx - 1.1), fmt(hy - 0.55)))
    ep = [(gx + 1.6, MK - 7.4), (gx + 0.3, MK - 3.8), (gx - 0.2, MK), (gx + 0.6, MK + 4.4), (gx + 4.0, MK + 8.4)]
    path(doc, cr_path(ep, False), stroke='#7A0C37', w=0.42, dash='0.9 0.7')
    lab(doc, gx - 1.2, MK + 8.8, 'e⁻', '#7A0C37', size=4.4, anchor='end')
    arrow(doc, [(gx + 18.0, MK - 17.6), (gx + 10.0, MK - 13.8), (gx + 4.6, MK - 9.6)], tone(NOX, 0.2), 'transport', w=0.45, head=2.2, bow=0)
    lab(doc, gx + 19.0, MK - 16.4, 'NADPH', tone(NOX, 0.3), size=4.4)
    lab(doc, gx + 5.2, MK + 9.9, 'O₂ → O₂•⁻ → H₂O₂', tone(NOX, 0.3), size=4.4)
    for (rx_, ry_, s) in [(gx + 3.0, MK + 16.0, 0.9), (gx + 14.5, MK + 17.2, 0.75), (gx + 27.0, MK + 16.0, 0.85),
                          (gx + 40, MK + 18.0, 0.7)]:
        _ros(doc, rx_, ry_, s)
    lab(doc, gx - 12.4, MK - 8.0, 'NOX2', tone(NOX, 0.25), size=4.6, anchor='end')


    # ---------------------------------------------------------------- lysosome fusion (section 4) between the two zones
    arrow(doc, [(125.5, SY0 + 13.2), (126.5, cs - 1.0)], CONV, 'fusion', w=0.55, head=3.2, bow=0.1)


    # ---------------------------------------------------------------- late: V-ATPase acidifies, hydrolases digest
    _vatpase(doc, 147.0, MK)
    lab(doc, 155.0, MK - 20.5, 'V-ATPase', tone(VATP, 0.3), size=4.4)

    hplus(doc, 139.0, MK - 7.4, 0.9)
    arrow(doc, [(140.2, MK - 5.2), (145.6, MK + 7.6)], HPLUS, 'transport', w=0.5, head=2.2, bow=-0.18)
    for (hx, hy) in [(150, MK + 8), (160, MK + 12), (171, MK + 6.5), (182, MK + 9.5), (196, MK + 6.5), (206, MK + 12.5), (219, MK + 7.5),
                     (232, MK + 11.5), (244, MK + 6.5), (252, MK + 14), (176, MK + 37), (198, MK + 35), (238, MK + 36), (158, MK + 31)]:
        hplus(doc, hx, hy, 0.8)
    lab(doc, 158.0, MK + 9.2, 'H⁺', '#0A6E92', size=4.4)
    # free acid hydrolases throughout the phagolysosome lumen
    for (hx, hy) in [(134, MK + 14), (190, MK + 13.5), (226, MK + 17.5), (163, MK + 37.5), (208, MK + 31.5), (186, MK + 41),
                        (247, MK + 30)]:
        _hydrolase(doc, hx, hy, 1.7, (hx * 37) % 360)
    # bacterial fragments being cut
    _pg_fragment(doc, 142, MK + 26)
    _hydrolase(doc, 150.2, MK + 32.8, 2.4, 140)
    lab(doc, 138.5, MK + 41.5, 'lysozyme', tone(HYD, 0.1), size=4.4)
    _protein_chain(doc, 166, MK + 19, 186, MK + 24)
    _hydrolase(doc, 176.2, MK + 18.0, 2.3, 60)
    lab(doc, 168.0, MK + 33.0, 'cathepsins', tone(HYD, 0.1), size=4.4)
    _lipid_flake(doc, 198, MK + 27)
    _hydrolase(doc, 203.6, MK + 21.4, 2.1, 100)
    lab(doc, 192.0, MK + 39.5, 'lipases', tone(HYD, 0.1), size=4.4)
    _dna(doc, 213, MK + 26.5, 228, MK + 24.0)
    _hydrolase(doc, 221.0, MK + 30.4, 2.1, -60)
    lab(doc, 214.0, MK + 39.5, 'nucleases', tone(HYD, 0.1), size=4.4)
    # transporter exports the products to the cytosol for reuse
    tx = 243.0
    for dx in (-1.9, 1.9):
        glob(doc, tx + dx, MK, 2.1, 3.6, lighten(RECY, 0.2), light=0.45)
    for k, (px, py) in enumerate([(235.5, MK + 17), (239.5, MK + 12.5), (245.5, MK + 18.5), (233, MK + 11)]):
        _product(doc, px, py, k)
    arrow(doc, [(238.0, MK + 9.0), (243.0, MK + 1.5), (246.5, MK - 10.0)], RECY, 'recycle', w=0.75, head=2.8, bow=0)
    for k, (px, py) in enumerate([(251.5, MK - 9.5), (248.5, MK - 15.0), (254.5, MK - 14.0)]):
        _product(doc, px, py, k)
    lab(doc, 242.0, MK - 13.0, 'reuse', tone(RECY, 0.2), size=4.4, anchor='end')

    # pH ticks along the lumen floor
    _strip_close(doc)
    _flush(doc)
    for (px, s) in ((46, 'pH 7'), (86, '6.5'), (126, '6'), (166, '5.5'), (206, '5'), (244, '4.5')):
        line(doc, px, MK + 45.0, px, MK + 46.8, '#8A8170', 0.25)
        T(doc, px, MK + 51.2, s, size=4.4, fill=ink('#7D7466'), anchor='middle')
    # zone titles (the two weapons)
    T(doc, 42, SY0 + 5.2, 'ROS', size=4.8, weight=600, fill=ink(tone(NOX, 0.1)))
    T(doc, 146, SY0 + 5.2, 'acid hydrolases', size=4.8, weight=600, fill=ink(tone(HYD, 0.05)))
    doc.add('</g>')
    # focus links from 2.3 and 2.6, routed as gentle curves through empty cytoplasm (not across 2.4 / 2.5)
    n_, p_ = G.NASCENT_23, G.PHAGOLYSOSOME_26
    rn, rp = n_[2] + 3.0, p_[2] + 3.0
    source_ring(doc, n_, rn, PHAG)
    source_ring(doc, p_, rp, PHAG)
    a = math.radians(160)
    s0 = (n_[0] + rn * math.cos(a), n_[1] + rn * math.sin(a))
    curved_link(doc, [s0, (s0[0] - 14, s0[1] + 30), (292, 625), xf((250, 664))], PHAG)
    a = math.radians(140)
    s1 = (p_[0] + rp * math.cos(a), p_[1] + rp * math.sin(a))
    curved_link(doc, [s1, (520, 734), (430, 740), (330, 738), xf((250, 728))], PHAG)


# ----------------------------------------------------------------- killing-strip glyphs
def _ros(doc, x, y, s=1.0):
    pts = []
    for i in range(10):
        a = math.pi * 2 * i / 10 + 0.3
        rr = (2.6 if i % 2 == 0 else 1.0) * s
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    path(doc, poly_d(pts, True), fill=shade(doc, NOX, light=0.4, dark=0.2), stroke='#7A0C37', w=0.2)
    circ(doc, x, y, 0.45 * s, fill='#fff')


def _hydrolase(doc, x, y, r, rot):
    """Acid hydrolase (BIO cobalt) with its active-site cleft facing rot (deg)."""
    a = math.radians(rot)
    glob(doc, x, y, r, r, HYD, light=0.42)
    p0 = (x + math.cos(a) * r * 1.05, y + math.sin(a) * r * 1.05)
    pa = (x + math.cos(a + 0.5) * r * 0.25, y + math.sin(a + 0.5) * r * 0.25)
    pb = (x + math.cos(a - 0.5) * r * 0.25, y + math.sin(a - 0.5) * r * 0.25)
    q1 = (p0[0] + math.cos(a + 1.57) * r * 0.55, p0[1] + math.sin(a + 1.57) * r * 0.55)
    q2 = (p0[0] - math.cos(a + 1.57) * r * 0.55, p0[1] - math.sin(a + 1.57) * r * 0.55)
    path(doc, poly_d([q1, pa, pb, q2], True), fill='#F5F1FA')


def _bact_rod(doc, xa, xb, y, h):
    """Bacterium in the lumen: intact rounded end at the left, envelope breaking up toward the right."""
    r = h / 2
    contact_shadow(doc, (xa + xb) / 2, y, (xb - xa) / 2, r, strength=0.1, spread=1.04)
    top = [(xa + r, y - r)]
    for k in range(1, 12):
        xx = xa + r + (xb - xa - r) * k / 11
        top.append((xx, y - r + (0.0 if xx < xb - 26 else (0.5 if k % 2 else -0.4))))
    bot = [(x_, 2 * y - y_) for x_, y_ in top]
    jag = [(xb, y - r + 1.5), (xb - 3.5, y - 2.0), (xb + 1.0, y + 0.8), (xb - 2.5, y + 3.5), (xb + 0.5, y + r - 1.5)]
    d = 'M%s,%s ' % (fmt(top[0][0]), fmt(top[0][1])) + ' '.join('L%s,%s' % (fmt(p[0]), fmt(p[1])) for p in top[1:] + jag + bot[::-1]) + \
        ' A%s,%s 0 0 1 %s,%s Z' % (fmt(r), fmt(r), fmt(top[0][0]), fmt(top[0][1]))
    g = _ug(doc, 'linear', [(0, lighten(BACT, 0.45), 1), (0.45, lighten(BACT, 0.22), 1), (1, tone(BACT, 0.08), 1)], x1=0, y1=y - r, x2=0, y2=y + r)
    path(doc, d, fill=g, stroke=tone(BACT, 0.42), w=0.7)
    for yy in (y - r + 1.6, y + r - 1.6):
        path(doc, 'M%s,%s L%s,%s' % (fmt(xa + r * 0.75), fmt(yy), fmt(xb - 5), fmt(yy)), stroke=tone(BACT, 0.25), w=0.55, dash='1.4 0.5', op=0.8)
    for lx in (52, 66, 80, 96, 108):
        circ(doc, lx, y - r, 0.9, fill=lighten(NOX, 0.6), stroke=tone(NOX, 0.2), w=0.25)
    path(doc, 'M%s,%s L%s,%s' % (fmt(xa + r), fmt(y - r + 2.6), fmt(xb - 12), fmt(y - r + 2.6)), stroke='#fff', w=0.6, op=0.5)
    nuc = [(xa + 44 + k * 9, y + (1.6 if k % 2 else -1.6)) for k in range(int((xb - xa - 56) / 9))]
    path(doc, cr_path(nuc, False), stroke='#6B5A98', w=0.55, op=0.8)


def _pg_fragment(doc, x, y):
    """Peptidoglycan: glycan strands (beads) cross-linked by short peptides."""
    for j in range(3):
        yy = y + j * 3.2
        pts = [(x - 6 + k * 2.4 + (j % 2) * 1.2, yy + (0.3 if k % 2 else -0.3)) for k in range(6)]
        path(doc, poly_d(pts), stroke=tone(BACT, 0.35), w=0.5)
        for (px, py) in pts:
            circ(doc, px, py, 0.75, fill=lighten(BACT, 0.15), stroke=tone(BACT, 0.4), w=0.18)
        if j < 2:
            for (px, py) in pts[::2]:
                line(doc, px, py + 0.7, px + 0.5, py + 2.5, tone(BACT, 0.2), 0.35)


def _protein_chain(doc, xa, ya, xb, yb):
    pts = [(xa + (xb - xa) * k / 9, ya + (yb - ya) * k / 9 + (1.1 if k % 2 else -1.1)) for k in range(10)]
    path(doc, cr_path(pts[:5], False), stroke=tone(BACT, 0.3), w=0.45)
    path(doc, cr_path(pts[5:], False), stroke=tone(BACT, 0.3), w=0.45)
    for (px, py) in pts:
        circ(doc, px, py, 0.85, fill=lighten(BACT, 0.05), stroke=tone(BACT, 0.4), w=0.18)


def _lipid_flake(doc, x, y):
    for k in range(6):
        px = x - 6 + k * 1.9
        for sgn in (-1, 1):
            line(doc, px, y + sgn * 0.5, px, y + sgn * 2.2, tone(BACT, 0.25), 0.3)
            circ(doc, px, y + sgn * 2.6, 0.75, fill=lighten(BACT, 0.1), stroke=tone(BACT, 0.4), w=0.18)


def _dna(doc, xa, ya, xb, yb):
    for ph in (0, math.pi):
        pts = []
        for k in range(30):
            t = k / 29
            pts.append((xa + (xb - xa) * t, ya + (yb - ya) * t + 1.3 * math.sin(t * 2 * math.pi * 2.2 + ph)))
        path(doc, poly_d(pts), stroke='#6B5A98', w=0.55)


def _product(doc, x, y, k):
    c = tone(RECY, 0.05)
    if k % 3 == 0:
        circ(doc, x, y, 0.9, fill=lighten(c, 0.25), stroke=tone(c, 0.35), w=0.2)
    elif k % 3 == 1:
        pts = [(x + 1.0 * math.cos(math.pi / 3 * i), y + 1.0 * math.sin(math.pi / 3 * i)) for i in range(6)]
        path(doc, poly_d(pts, True), fill=lighten(c, 0.4), stroke=tone(c, 0.35), w=0.2)
    else:
        path(doc, poly_d([(x, y - 1.1), (x + 1.0, y), (x, y + 1.1), (x - 1.0, y)], True), fill=lighten(c, 0.1), stroke=tone(c, 0.35), w=0.2)


def _vatpase(doc, x, y):
    """V-ATPase side view: V0 c-ring + subunit a in the bilayer, central stalk, V1 A3B3 head in the cytosol."""
    c = VATP
    path(doc, 'M%s,%s h%s a1.8,1.8 0 0 1 1.8,1.8 v%s a1.8,1.8 0 0 1 -1.8,1.8 h%s a1.8,1.8 0 0 1 -1.8,-1.8 v%s a1.8,1.8 0 0 1 1.8,-1.8 Z' % (
        fmt(x - 4.4), fmt(y - 3.4), fmt(8.8), fmt(3.2), fmt(-8.8), fmt(3.2)),
        fill=shade(doc, lighten(c, 0.3), light=0.45, dark=0.12), stroke=tone(c, 0.42), w=0.3)
    for k in range(-2, 3):
        line(doc, x + k * 1.9, y - 2.6, x + k * 1.9, y + 2.6, tone(c, 0.25), 0.25, op=0.6)
    glob(doc, x + 7.6, y - 0.6, 1.8, 3.6, tone(c, 0.12), light=0.4)                    # subunit a
    rod(doc, [(x + 8.0, y - 4.0), (x + 8.6, y - 10.0), (x + 6.8, y - 15.8)], tone(c, 0.18), w=0.8)   # peripheral stalk
    rod(doc, [(x, y - 3.4), (x, y - 8.0)], tone(c, 0.3), w=1.2, smooth=False)                      # central rotor stalk
    for k, (dx, col) in enumerate(((-3.8, c), (0, lighten(c, 0.25)), (3.8, c))):                 # V1: A/B alternating
        glob(doc, x + dx, y - 12.0, 2.3, 3.4, col, light=0.45)
    glob(doc, x, y - 16.2, 3.0, 1.4, lighten(c, 0.15), light=0.45)


def draw(doc):
    fusion(doc)
    killing(doc)
