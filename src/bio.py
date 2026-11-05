"""Biological glyph library (all vector, hand-parametrised)."""
import math, random
from lib import *
from style import shade, sheen, contact_shadow, spec, tone, lighten, darken, mix, shade_rot, sheen_rot, lit_side


# ------------------------------------------------------------ membranes
def bilayer(doc, d, color, w=1.0, inner='#fff', fill='none', op=None):
    """Closed/open path drawn as a two-line membrane (dark outer stroke + light core)."""
    path(doc, d, fill=fill, stroke=color, w=w * 2.1, op=op)
    path(doc, d, fill='none', stroke=inner, w=w * 0.75, op=op)


def rim_shade(doc, x, y, r, color, w=None, op=0.32):
    """Inner rim shading: transparent on the lit (top-left) side, deeper on the far side -> reads as volume."""
    key = ('rim', color, op)
    c = doc.__dict__.setdefault('_style_cache', {})
    if key not in c:
        c[key] = doc.lingrad([(0, color, 0), (0.55, color, 0), (1, color, op)], 0, 0, 1, 1)
    w = w if w is not None else max(0.8, r * 0.16)
    circ(doc, x, y, r - w / 2, fill='none', stroke=c[key], w=w)


def vesicle(doc, x, y, r, fill, stroke, w=0.7, inner='#fff', op=None, lit=True):
    plain = isinstance(fill, str) and fill.startswith('#')
    body = shade(doc, fill, light=0.55, dark=0.05) if (lit and plain) else fill
    if r < 4.5:
        circ(doc, x, y, r, fill=body, stroke=stroke, w=w * 1.3, op=op)
        if lit and op is None and r >= 2.2:
            spec(doc, x, y, r, a0=205, a1=250, op=0.6, inset=0.55)
    else:
        if lit and op is None:
            contact_shadow(doc, x, y, r, strength=0.12)
        circ(doc, x, y, r, fill=body, stroke=stroke, w=w * 2.6, op=op)
        if lit and op is None:
            rim_shade(doc, x, y, r - w * 1.3, tone(stroke, 0.25), op=0.22)
        circ(doc, x, y, r, fill='none', stroke=inner if inner != '#fff' else lighten(stroke, 0.82), w=w * 0.8, op=op)
        if lit and op is None:
            spec(doc, x, y, r, a0=196, a1=246, op=0.7, inset=0.84, w=max(0.4, r * 0.05))


def clathrin(doc, x, y, r, color='#3C4553', w=1.1):
    """Clathrin lattice: crisp dark facets with a light top edge, plus the outer triskelion legs."""
    circ(doc, x, y, r, fill='none', stroke=color, w=w * 1.05, dash='1.7 0.9')
    circ(doc, x, y, r - w * 0.18, fill='none', stroke='#A7B0BF', w=w * 0.32, dash='1.7 0.9', op=0.9)
    circ(doc, x, y, r + w * 1.1, fill='none', stroke=color, w=w * 0.45, dash='0.8 1.8')


def copii(doc, x, y, r, color='#D98E00', w=1.1):
    """COPII coat: crisp beaded shell (toned rim + lit core per bead)."""
    circ(doc, x, y, r, fill='none', stroke=tone(color, 0.35), w=w * 1.62, dash='0.1 1.7')
    circ(doc, x, y, r, fill='none', stroke=color, w=w * 1.3, dash='0.1 1.7')
    circ(doc, x - w * 0.12, y - w * 0.14, r, fill='none', stroke=lighten(color, 0.6), w=w * 0.45, dash='0.1 1.7')


# ------------------------------------------------------------ molecules
def hydrolase(doc, x, y, s=1.0, rot=0, p=False, glycan=True, color=BIO, pro=False):
    """Acid hydrolase: blue protein body with active-site notch and N-glycan tree; p=True adds the M6P tag."""
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), rot, fmt(s))]
    if glycan:
        sug = shade_rot(doc, '#6FA5F0', rot, light=0.5, dark=0.15)
        g.append('<path d="M2.4,0 L6.6,0 M6.6,0 L8.6,-1.9 M6.6,0 L8.6,1.9" stroke="#1E3B6E" stroke-width="0.5" fill="none" stroke-linecap="round"/>')
        for (gx, gy) in ((6.6, 0), (8.7, -1.95), (8.7, 1.95)):
            g.append('<circle cx="%s" cy="%s" r="0.95" fill="%s" stroke="#1E3B6E" stroke-width="0.22"/>' % (gx, gy, sug))
    g.append('<circle cx="0" cy="0" r="3.3" fill="%s" stroke="%s" stroke-width="0.4"/>' % (shade_rot(doc, color, rot, light=0.42, dark=0.2), tone(color, 0.5)))
    if not pro:
        g.append('<path d="M-3.35,0 L-0.6,-1.15 L-0.6,1.15 Z" fill="#F3F6FF"/>')
    else:
        g.append('<path d="M-3.0,-1.6 Q0,0.5 3.0,-1.6" fill="none" stroke="#F3F6FF" stroke-width="0.7"/>')
    if p:
        g.append('<circle cx="8.7" cy="-1.95" r="1.7" fill="%s" stroke="#6b5200" stroke-width="0.3"/>' % shade_rot(doc, M6P, rot, light=0.45, dark=0.12))
    g.append('</g>')
    if p:
        # the 'P' letter is set outside the rotated group so it always stays upright (never reads as a mirrored 'd')
        a = math.radians(rot)
        px = x + s * (8.7 * math.cos(a) + 1.95 * math.sin(a))
        py = y + s * (8.7 * math.sin(a) - 1.95 * math.cos(a))
        g.append('<text x="%s" y="%s" font-family="Segoe UI,Arial" font-weight="700" font-size="%s" text-anchor="middle" fill="#3b2d00">P</text>' % (
            fmt(px), fmt(py + 0.6 * s), fmt(2.1 * s)))
    doc.add(''.join(g))


def enzyme_dot(doc, x, y, r=1.6, color=BIO):
    circ(doc, x, y, r, fill=shade(doc, color, light=0.42, dark=0.2), stroke=tone(color, 0.5), w=0.25)
    doc.add('<path d="M%s,%s L%s,%s L%s,%s Z" fill="#fff"/>' % (fmt(x - r), fmt(y), fmt(x - r * .1), fmt(y - r * .45), fmt(x - r * .1), fmt(y + r * .45)))
    if r >= 1.6:
        circ(doc, x + r * 0.05, y - r * 0.55, r * 0.18, fill='#fff', op=0.75)


def m6pr(doc, x, y, s=1.0, rot=0, color='#1E8A5A', bound=False):
    """Mannose-6-phosphate receptor: Y-shaped membrane receptor (toned outline + body)."""
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), rot, fmt(s))]
    yd = 'M0,0 L0,-4.2 M0,-4.2 L-2.2,-7 M0,-4.2 L2.2,-7'
    g.append('<path d="%s" stroke="%s" stroke-width="1.35" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' % (yd, tone(color, 0.45)))
    g.append('<path d="%s" stroke="%s" stroke-width="0.9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' % (yd, color))
    head = shade_rot(doc, color, rot, light=0.45, dark=0.18)
    g.append('<circle cx="-2.3" cy="-7.2" r="1.1" fill="%s" stroke="%s" stroke-width="0.22"/><circle cx="2.3" cy="-7.2" r="1.1" fill="%s" stroke="%s" stroke-width="0.22"/>' % (
        head, tone(color, 0.45), head, tone(color, 0.45)))
    g.append('</g>')
    doc.add(''.join(g))


def vatpase(doc, x, y, cyt_deg, s=1.0, color='#E75A8B'):
    """V-ATPase on a membrane at (x,y). cyt_deg = direction (screen angle, deg) pointing to the cytosolic side."""
    rot = cyt_deg + 90
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(rot), fmt(s))]
    g.append('<rect x="-2.7" y="-1.8" width="5.4" height="3.6" rx="1.2" fill="%s" stroke="#8c1040" stroke-width="0.38"/>' % shade_rot(doc, '#F6C9D8', rot, light=0.5, dark=0.12))
    g.append('<path d="M0,-1.8 L0,-4.5" stroke="#8c1040" stroke-width="0.9"/>')
    g.append('<circle cx="0" cy="-7.2" r="3.0" fill="%s" stroke="#8c1040" stroke-width="0.38"/>' % shade_rot(doc, '#E75A8B', rot, light=0.45, dark=0.2))
    g.append('<path d="M0,-7.2 L0,-9.8 M0,-7.2 L-2.3,-5.9 M0,-7.2 L2.3,-5.9" stroke="#8c1040" stroke-width="0.32" opacity="0.85"/>')
    g.append('</g>')
    doc.add(''.join(g))


def hplus(doc, x, y, s=1.0):
    circ(doc, x, y, 1.45 * s, fill=shade(doc, HPLUS, light=0.4, dark=0.18), stroke='#0A6E92', w=0.2)
    doc.add('<path d="M%s,%s h%s M%s,%s v%s" stroke="#fff" stroke-width="%s" stroke-linecap="round"/>' % (
        fmt(x - .75 * s), fmt(y), fmt(1.5 * s), fmt(x), fmt(y - .75 * s), fmt(1.5 * s), fmt(.35 * s)))


def antibody(doc, x, y, s=1.0, rot=0, color='#3E5C86'):
    """IgG: Fc stem (towards +y local) and two Fab arms (towards -y local = antigen)."""
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), rot, fmt(s))]
    yd = 'M0,3.5 L0,0 M0,0 L-3.2,-3.2 M0,0 L3.2,-3.2'
    g.append('<path d="%s" stroke="%s" stroke-width="2.0" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' % (yd, tone(color, 0.4)))
    g.append('<path d="%s" stroke="%s" stroke-width="1.45" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' % (yd, color))
    g.append('<path d="%s" stroke="%s" stroke-width="0.4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>' % (yd, lighten(color, 0.45)))
    g.append('<circle cx="-3.4" cy="-3.5" r="1.0" fill="#fff" stroke="%s" stroke-width="0.4"/><circle cx="3.4" cy="-3.5" r="1.0" fill="#fff" stroke="%s" stroke-width="0.4"/>' % (color, color))
    g.append('</g>')
    doc.add(''.join(g))


def c3b(doc, x, y, s=1.0, rot=0, color='#1F8F8A'):
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), rot, fmt(s))]
    g.append('<path d="M0,0 L2.4,-2.4 A3.4,3.4 0 1 1 -2.4,-2.4 Z" fill="%s" stroke="#0e6764" stroke-width="0.35" stroke-linejoin="round" transform="rotate(180)"/>' % (
        shade_rot(doc, color, rot + 180, light=0.45, dark=0.18)))
    g.append('</g>')
    doc.add(''.join(g))


def receptor(doc, x, y, h=7, rot=0, color='#5A6B85', kind='fc', tail=True):
    """Membrane receptor, extracellular side = local -y. kind: fc (Ig domains), cr (beta-propeller head),
    lectin (Y-head), tlr (curved horseshoe), sr (collagenous stalk + head)."""
    g = ['<g transform="translate(%s %s) rotate(%s)">' % (fmt(x), fmt(y), rot)]
    sw = 0.9
    hd = shade_rot(doc, color, rot, light=0.42, dark=0.18)
    dk = tone(color, 0.4)
    if kind == 'fc':
        g.append('<path d="M0,0 L0,%s" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (-h, color, sw))
        g.append('<ellipse cx="0" cy="%s" rx="1.7" ry="2.1" fill="%s" stroke="%s" stroke-width="0.25"/><ellipse cx="0.2" cy="%s" rx="1.7" ry="2.1" fill="%s" stroke="%s" stroke-width="0.25"/>' % (
            -h + 1.6, hd, dk, -h * 0.5, hd, dk))
    elif kind == 'cr':
        g.append('<path d="M0,0 L0,%s" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (-h * 0.7, color, sw))
        g.append('<circle cx="0" cy="%s" r="2.8" fill="%s" stroke="%s" stroke-width="0.3"/><circle cx="0" cy="%s" r="1.0" fill="#fff"/>' % (-h * 0.7 - 1.2, hd, dk, -h * 0.7 - 1.2))
    elif kind == 'lectin':
        g.append('<path d="M0,0 L0,%s M0,%s L-2.3,%s M0,%s L2.3,%s" stroke="%s" stroke-width="%s" fill="none" stroke-linecap="round"/>' % (
            -h * 0.6, -h * 0.6, -h, -h * 0.6, -h, color, sw))
        g.append('<circle cx="-2.4" cy="%s" r="1.0" fill="%s" stroke="%s" stroke-width="0.22"/><circle cx="2.4" cy="%s" r="1.0" fill="%s" stroke="%s" stroke-width="0.22"/>' % (
            -h - 0.2, hd, dk, -h - 0.2, hd, dk))
    elif kind == 'sr':
        g.append('<path d="M0,0 Q1.4,%s -0.4,%s Q-1.2,%s 0.3,%s" stroke="%s" stroke-width="%s" fill="none" stroke-linecap="round"/>' % (
            -h * 0.3, -h * 0.55, -h * 0.75, -h * 0.9, color, sw))
        g.append('<ellipse cx="0.3" cy="%s" rx="2.1" ry="1.7" fill="%s" stroke="%s" stroke-width="0.25"/>' % (-h * 0.95, hd, dk))
    elif kind == 'tlr':
        g.append('<path d="M-1.8,0 L-1.8,%s M1.8,0 L1.8,%s" stroke="%s" stroke-width="%s" fill="none" stroke-linecap="round"/>' % (-h * 0.35, -h * 0.35, color, sw))
        hs = 'M-2.2,%s C-4,%s -3.5,%s 0,%s C3.5,%s 4,%s 2.2,%s' % (-h * 0.35, -h * 0.9, -h * 1.15, -h * 1.1, -h * 1.15, -h * 0.9, -h * 0.35)
        g.append('<path d="%s" stroke="%s" stroke-width="1.9" fill="none" stroke-linecap="round"/>' % (hs, dk))
        g.append('<path d="%s" stroke="%s" stroke-width="1.4" fill="none" stroke-linecap="round"/>' % (hs, color))
        g.append('<path d="%s" stroke="%s" stroke-width="0.4" fill="none" stroke-linecap="round" opacity="0.8"/>' % (hs, lighten(color, 0.5)))
    if tail:
        g.append('<path d="M0,0 L0,2.6" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (color, sw * 0.9))
    g.append('</g>')
    doc.add(''.join(g))


def phos_dot(doc, x, y, r=1.1):
    circ(doc, x, y, r, fill=shade(doc, M6P, light=0.45, dark=0.12), stroke='#6b5200', w=0.2)


# ------------------------------------------------------------ cell parts
def mito(doc, x, y, L=24, W=11, rot=0, seed=3):
    """Mitochondrion (polish pass): a gently bent bean in world-aligned top-left light, outer membrane + inner
    membrane with deep lamellar cristae (pale intracristal space), a few matrix granules and a rim highlight."""
    rnd = random.Random(seed)
    contact_shadow(doc, x, y, L / 2, W / 2, rot=rot, strength=0.15)
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    bend = W * rnd.uniform(0.08, 0.16) * rnd.choice((-1, 1))

    def P(u, v):
        v += bend * (1 - (2 * u / L) ** 2)
        return (x + u * ca - v * sa, y + u * sa + v * ca)

    def capsule(l, w, n=10):
        r = w / 2
        pts = []
        for k in range(n + 1):                                   # right cap
            a = -math.pi / 2 + math.pi * k / n
            pts.append((l / 2 - r + r * math.cos(a), r * math.sin(a)))
        for k in range(1, 8):                                    # bottom side
            pts.append((l / 2 - r - (l - w) * k / 8, r))
        for k in range(n + 1):                                   # left cap
            a = math.pi / 2 + math.pi * k / n
            pts.append((-l / 2 + r + r * math.cos(a), r * math.sin(a)))
        for k in range(1, 8):                                    # top side
            pts.append((-l / 2 + r + (l - w) * k / 8, -r))
        return [P(u, v) for u, v in pts]

    outer = capsule(L, W)
    inner = capsule(L - 2.3, W - 2.3)
    body = doc.lingrad([(0, '#F8E2B8'), (0.5, '#EBC488'), (1, '#CF9A55')], 0, 0, 1, 1)
    matrix = doc.lingrad([(0, '#FBEBCB'), (0.55, '#F1D29E'), (1, '#DDAE6C')], 0, 0, 1, 1)
    doc.add('<path d="%s" fill="%s" stroke="#7C5222" stroke-width="0.75" stroke-linejoin="round"/>' % (poly_d(outer, True), body))
    doc.add('<path d="%s" fill="%s" stroke="#9A6A30" stroke-width="0.42" stroke-linejoin="round"/>' % (poly_d(inner, True), matrix))
    # cristae: lamellae folding in alternately from both sides of the inner membrane
    n = max(3, int(L / 3.1))
    walls, lumens = [], []
    hw = (W - 2.3) / 2
    for i in range(n):
        u = -L / 2 + 3.4 + i * (L - 6.8) / max(1, n - 1) + rnd.uniform(-0.35, 0.35)
        side = -1 if i % 2 == 0 else 1
        dep = (W - 2.3) * rnd.uniform(0.52, 0.7)
        lean = rnd.uniform(-0.7, 0.7)
        a = P(u, side * hw)
        m = P(u + lean * 0.5, side * (hw - dep * 0.55))
        b = P(u + lean, side * (hw - dep))
        d = 'M%s,%sQ%s,%s %s,%s' % (fmt(a[0]), fmt(a[1]), fmt(m[0]), fmt(m[1]), fmt(b[0]), fmt(b[1]))
        walls.append(d)
        lumens.append(d)
    doc.add('<path d="%s" fill="none" stroke="#9A6A30" stroke-width="1.3" stroke-linecap="round"/>' % ''.join(walls))
    doc.add('<path d="%s" fill="none" stroke="#FFF4DD" stroke-width="0.5" stroke-linecap="round"/>' % ''.join(lumens))
    for _ in range(3):
        g = P(rnd.uniform(-L / 3, L / 3), rnd.uniform(-W / 6, W / 6))
        doc.add('<circle cx="%s" cy="%s" r="0.42" fill="#7C5222" opacity="0.55"/>' % (fmt(g[0]), fmt(g[1])))
    # rim highlight on the side that faces the top-left light
    cx_, cy_ = x, y
    lit = []
    for (px, py) in capsule(L - 1.0, W - 1.0, n=16):
        nx, ny = px - cx_, py - cy_
        lit.append(((nx * -0.7071 + ny * -0.7071) / (math.hypot(nx, ny) or 1) > 0.35, (px, py)))
    run, best = [], []
    for ok, p_ in lit + lit:
        if ok:
            run.append(p_)
            if len(run) > len(best):
                best = list(run)
        else:
            run = []
    if len(best) > 2:
        doc.add('<path d="%s" fill="none" stroke="#FFFFFF" stroke-width="0.6" stroke-linecap="round" opacity="0.65"/>'
                % poly_d(best[:len(lit)], False))


def ribosomes_along(doc, poly, spacing=3.4, off=1.9, r=0.72, color='#17327A', side=1, seed=1, skip=0.0):
    """Ribosomes as small two-tone dots (dark body + a light top-left glint), drawn as two compact paths."""
    from style import dots_path
    rnd = random.Random(seed)
    res = resample(poly, spacing, closed=False)
    nm = normals(res, closed=False)
    pts = []
    for p, n in zip(res, nm):
        if rnd.random() < skip:
            continue
        j = rnd.uniform(-.25, .25)
        pts.append((p[0] + n[0] * (off * side + j), p[1] + n[1] * (off * side + j)))
    if not pts:
        return
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (dots_path(pts), color, fmt(2 * r)))
    hl = [(x - r * 0.32, y - r * 0.34) for x, y in pts]
    doc.add('<path d="%s" fill="none" stroke="#8FA8E6" stroke-width="%s" stroke-linecap="round" opacity="0.9"/>' % (dots_path(hl), fmt(r * 0.7)))


def _lit_offset(dense, k):
    """Offset of a centreline toward the lit (top-left) side by k."""
    a, b = offset_poly(dense, k, closed=False), offset_poly(dense, -k, closed=False)
    sa = sum(x + y for x, y in a) / len(a)
    sb = sum(x + y for x, y in b) / len(b)
    return (a, b) if sa < sb else (b, a)


def er_sheet(doc, pts, w=3.4, fill='#D6E6FA', line_c='#2D5FA8', ribo=True, both=True, seed=1, ribo_r=0.72):
    """Rough ER cisterna drawn along smoothed centreline: toned outline, lumen with a top-lit sheen, ribosomes."""
    dense = cr_sample(pts, closed=False, per=10)
    d = poly_d(dense)
    path(doc, d, stroke=tone(line_c, 0.18), w=w + 0.9, cap='round')
    path(doc, d, stroke=fill, w=w - 0.4, cap='round')
    lit, dark = _lit_offset(dense[1:-1], w * 0.2)
    path(doc, poly_d(dark), stroke=darken(fill, 0.1), w=w * 0.34, cap='round', op=0.75)
    path(doc, poly_d(lit), stroke=lighten(fill, 0.7), w=w * 0.24, cap='round', op=0.9)
    if ribo:
        rr = ribo_r * 0.84
        ribosomes_along(doc, offset_poly(dense, (w + 0.9) / 2 + rr * 0.55, closed=False), spacing=3.5, off=0.0, r=rr, side=1, seed=seed, skip=0.12)
        if both:
            ribosomes_along(doc, offset_poly(dense, -(w + 0.9) / 2 - rr * 0.55, closed=False), spacing=3.5, off=0.0, r=rr, side=1, seed=seed + 7, skip=0.12)
    return dense


def golgi(doc, cx, cy, w=104, n=5, gap=7.0, thick=3.3, tilt=0, seed=1):
    """Golgi stack; cis face at top, trans at bottom. Returns list of (y, x0, x1) for cisternae (cis->trans)."""
    cols = ['#BFE3F2', '#9ED2EA', '#7FC0E0', '#5FAAD2', '#4294C0']
    out = []
    for i in range(n):
        yy = cy + (i - (n - 1) / 2) * gap
        ww = w * (1 - 0.05 * abs(i - 2))
        sag = 4.2 - 0.5 * i
        x0, x1 = cx - ww / 2, cx + ww / 2
        # cisterna: a flattened sac of even thickness, gently arched, with dilated rounded rims at both ends
        mid_y = yy + thick * 0.4
        h_mid, h_end = thick * 0.36, thick * 0.56
        N = 40
        cen, hh = [], []
        for k in range(N + 1):
            u = k / N
            e = (2 * u - 1) ** 2
            cen.append((x0 + ww * u, mid_y + sag * 0.32 * e))
            hh.append(h_mid + (h_end - h_mid) * e ** 4)
        topp = [(x, y - h) for (x, y), h in zip(cen, hh)]
        botp = [(x, y + h) for (x, y), h in zip(cen, hh)]
        capR = [(cen[-1][0] + h_end * math.sin(t * math.pi / 12), cen[-1][1] - h_end * math.cos(t * math.pi / 12)) for t in range(1, 12)]
        capL = [(cen[0][0] - h_end * math.sin(t * math.pi / 12), cen[0][1] + h_end * math.cos(t * math.pi / 12)) for t in range(1, 12)]
        d = poly_d(topp + capR + botp[::-1] + capL, True)
        st = tone(cols[i], 0.5)
        contact_shadow(doc, cx, mid_y, ww / 2 + h_end, thick * 0.7, strength=0.07, spread=1.02, dx=0.6, dy=1.3)
        path(doc, d, fill=sheen(doc, cols[i], light=0.5, dark=0.16), stroke=st, w=0.5)
        # highlight just under the upper membrane
        hl = [(x, y + 0.75) for (x, y) in topp[3:-3]]
        path(doc, poly_d(hl), stroke='#FFFFFF', w=0.55, op=0.7)
        out.append((yy, x0, x1))
    return out


def centrosome(doc, x, y):
    g = ['<g transform="translate(%s %s)">' % (fmt(x), fmt(y))]
    g.append('<rect x="-5.5" y="-1.6" width="8" height="3.2" rx="1.2" fill="#6B7380" transform="rotate(-20)"/>')
    g.append('<rect x="-2" y="-5.5" width="3.2" height="8" rx="1.2" fill="#6B7380" transform="rotate(-20)"/>')
    g.append('</g>')
    doc.add(''.join(g))


def nuclear_pores(doc, poly, n=14, seed=2):
    res = resample(poly, poly_len(poly, True) / n, closed=True)
    for p in res:
        circ(doc, p[0], p[1], 1.25, fill='#F1EFFA', stroke='#6A5FA6', w=0.35)


# ------------------------------------------------------------ pathogens & particles
def bacterium(doc, x, y, L=50, W=22, rot=0, lps=True, flagella=True, seed=4, ops=False, scale=1.0):
    """Gram-negative rod drawn in local frame (long axis = x): lit body, double envelope, fine LPS fringe."""
    rnd = random.Random(seed)
    contact_shadow(doc, x, y, L / 2 * scale, W / 2 * scale, rot=rot, strength=0.13, spread=1.08)
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), rot, fmt(scale))]
    r = W / 2
    ls = lit_side(rot)                    # -1: lit side is local -y
    # LPS / surface PAMPs: finer and a little sparser
    if lps:
        n = int(L / 3.3)
        per = 2 * (L - W) + math.pi * W
        a = L - W
        strokes, tips = [], []
        for i in range(n):
            s_ = (i + 0.5) / n * per
            if s_ < a:
                px, py, nx, ny = -a / 2 + s_, -r, 0, -1
            elif s_ < a + math.pi * r:
                th = (s_ - a) / r
                px, py = a / 2 + r * math.sin(th), -r * math.cos(th)
                nx, ny = math.sin(th), -math.cos(th)
            elif s_ < 2 * a + math.pi * r:
                px, py, nx, ny = a / 2 - (s_ - a - math.pi * r), r, 0, 1
            else:
                th = (s_ - 2 * a - math.pi * r) / r
                px, py = -a / 2 - r * math.sin(th), r * math.cos(th)
                nx, ny = -math.sin(th), math.cos(th)
            ln = 1.9 + rnd.uniform(-0.3, 0.3)
            strokes.append('M%s,%s l%s,%s' % (fmt(px + nx * 0.3), fmt(py + ny * 0.3), fmt(nx * ln), fmt(ny * ln)))
            tips.append((px + nx * (ln + 0.45), py + ny * (ln + 0.45)))
        g.append('<path d="%s" stroke="#66741E" stroke-width="0.36" stroke-linecap="round" fill="none"/>' % ''.join(strokes))
        g.append('<path d="%s" stroke="#7C8A24" stroke-width="0.85" stroke-linecap="round" fill="none"/>' % ''.join('M%s,%sh0.01' % (fmt(tx), fmt(ty)) for tx, ty in tips))
    # outer membrane + periplasm + inner membrane
    g.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="#4E5A16" stroke-width="0.8"/>' % (
        fmt(-L / 2), fmt(-r), fmt(L), fmt(W), fmt(r), sheen_rot(doc, '#B4C05A', rot, light=0.35, dark=0.16)))
    g.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="#6A781E" stroke-width="0.45"/>' % (
        fmt(-L / 2 + 1.5), fmt(-r + 1.5), fmt(L - 3.0), fmt(W - 3.0), fmt(r - 1.5), sheen_rot(doc, '#D6DE98', rot, light=0.5, dark=0.12)))
    # nucleoid
    pts = []
    for i in range(9):
        pts.append((-L / 2 + 0.22 * W + (L - 0.44 * W) * i / 8, rnd.uniform(-r * .4, r * .4)))
    g.append('<path d="%s" fill="none" stroke="#6B5A98" stroke-width="0.65" stroke-linecap="round" opacity="0.9"/>' % cr_path(pts, False))
    # highlight along the lit long edge
    hy = ls * (r - 2.6)
    g.append('<path d="M%s,%s L%s,%s" stroke="#FFFFFF" stroke-width="%s" stroke-linecap="round" opacity="0.6"/>' % (
        fmt(-L / 2 + r * 0.9), fmt(hy), fmt(L / 2 - r * 1.1), fmt(hy), fmt(max(0.6, W * 0.06))))
    g.append('</g>')
    doc.add(''.join(g))
    if flagella:
        rad = math.radians(rot)
        ex = x + math.cos(rad) * (-L / 2) * scale
        ey = y + math.sin(rad) * (-L / 2) * scale
        pts = [(ex, ey)]
        for i in range(1, 6):
            pts.append((ex + math.cos(rad + math.pi) * i * 5.5 * scale + math.sin(rad) * (4 if i % 2 else -4) * scale,
                        ey + math.sin(rad + math.pi) * i * 5.5 * scale - math.cos(rad) * (4 if i % 2 else -4) * scale))
        path(doc, cr_path(pts, False), stroke='#6E7C20', w=0.6)


def silica(doc, x, y, s=1.0, rot=0, seed=1, fill='#B9C6D6'):
    """Crystalline silica: angular quartz shard; facets shaded light/mid/dark by their orientation to the light."""
    pts = [(-9, 1), (-4, -7), (3, -9), (9, -2), (7, 6), (-1, 9), (-8, 6)]
    c = (-1, 0)
    rad = math.radians(-rot)
    lx, ly = -math.cos(rad) + math.sin(rad), -math.sin(rad) - math.cos(rad)   # screen top-left light, in local frame
    ln = math.hypot(lx, ly)
    lx, ly = lx / ln, ly / ln
    hi, lo, edge = lighten(fill, 0.75), darken(fill, 0.42), '#3F4C64'
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), rot, fmt(s))]
    g.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (poly_d(pts, True), fill, edge, fmt(0.85 / max(s, 0.5) * 0.9)))
    best = None
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        mx, my = (p[0] + q[0]) / 2 - c[0], (p[1] + q[1]) / 2 - c[1]
        m = math.hypot(mx, my) or 1
        t = (mx * lx + my * ly) / m              # +1 facing the light
        col = mix(fill, hi, t * 0.85) if t > 0 else mix(fill, lo, -t * 0.9)
        g.append('<path d="M%s,%s L%s,%s L%s,%s Z" fill="%s" stroke="%s" stroke-width="0.3" stroke-linejoin="round"/>' % (
            c[0], c[1], p[0], p[1], q[0], q[1], col, mix(col, edge, 0.35)))
        if best is None or t > best[0]:
            best = (t, p, q)
    # crisp light ridges on the lit side, then the outline
    g.append('<path d="M%s,%s L%s,%s M%s,%s L%s,%s" stroke="#FFFFFF" stroke-width="0.45" stroke-linecap="round" opacity="0.85"/>' % (
        c[0], c[1], best[1][0], best[1][1], c[0], c[1], best[2][0], best[2][1]))
    g.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (poly_d(pts, True), edge, fmt(0.75 if s < 1.2 else 0.55)))
    # glint: small four-point star on the most lit vertex
    vx, vy = max(pts, key=lambda v: (v[0] - c[0]) * lx + (v[1] - c[1]) * ly)
    gx, gy = c[0] + (vx - c[0]) * 0.72, c[1] + (vy - c[1]) * 0.72
    k = 1.5
    g.append('<path d="M%s,%s Q%s,%s %s,%s Q%s,%s %s,%s Q%s,%s %s,%s Q%s,%s %s,%s Z" fill="#FFFFFF" opacity="0.95"/>' % (
        fmt(gx), fmt(gy - k), fmt(gx), fmt(gy), fmt(gx + k), fmt(gy), fmt(gx), fmt(gy), fmt(gx), fmt(gy + k),
        fmt(gx), fmt(gy), fmt(gx - k), fmt(gy), fmt(gx), fmt(gy), fmt(gx), fmt(gy - k)))
    g.append('</g>')
    doc.add(''.join(g))


def asbestos_fibre(doc, x1, y1, x2, y2, w=4.0, color='#C9A66B', frays=True, seed=2):
    """Long needle-like fibre bundle: lengthwise sheen, fibril lines and splayed fibril ends."""
    rnd = random.Random(seed)
    ang = math.atan2(y2 - y1, x2 - x1)
    L = math.hypot(x2 - x1, y2 - y1)
    deg = math.degrees(ang)
    ls = lit_side(deg)
    dk = '#6A4E1F'
    contact_shadow(doc, (x1 + x2) / 2, (y1 + y2) / 2, L / 2, w / 2, rot=deg, strength=0.12, spread=1.04, dx=0.6, dy=1.5)
    g = ['<g transform="translate(%s %s) rotate(%s)">' % (fmt(x1), fmt(y1), fmt(deg))]
    if frays:
        fr = []
        for k, a in enumerate((-12, -5, 6, 13)):
            y0 = (k - 1.5) * w / 4
            for (x0, sx, ln) in ((L - 1, 1, 7), (1, -1, 6)):
                ex, ey = sx * ln * math.cos(math.radians(a)), sx * ln * math.sin(math.radians(a))
                fr.append('M%s,%s q%s,%s %s,%s' % (fmt(x0), fmt(y0), fmt(ex * 0.5), fmt(ey * 0.2), fmt(ex), fmt(ey)))
        g.append('<path d="%s" stroke="%s" stroke-width="0.75" stroke-linecap="round" fill="none"/>' % (''.join(fr), dk))
        g.append('<path d="%s" stroke="%s" stroke-width="0.35" stroke-linecap="round" fill="none"/>' % (''.join(fr), lighten(color, 0.4)))
    g.append('<rect x="0" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="0.65"/>' % (
        fmt(-w / 2), fmt(L), fmt(w), fmt(w / 2), sheen_rot(doc, color, deg, light=0.5, dark=0.22), dk))
    for k in range(5):
        yy = (k - 2) * w / 6
        x0 = 2 + rnd.uniform(0, 6)
        x1_ = L - 2 - rnd.uniform(0, 8)
        dark = (k % 2 == 1)
        g.append('<path d="M%s,%s L%s,%s" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="%s"/>' % (
            fmt(x0), fmt(yy), fmt(x1_), fmt(yy), dk if dark else '#FFF6E0', '0.25' if dark else '0.3', '0.55' if dark else '0.6'))
    hy = ls * w * 0.3
    g.append('<path d="M%s,%s L%s,%s" stroke="#FFFFFF" stroke-width="%s" stroke-linecap="round" opacity="0.75"/>' % (
        fmt(3), fmt(hy), fmt(L - 4), fmt(hy), fmt(w * 0.11)))
    g.append('</g>')
    doc.add(''.join(g))


def ros(doc, x, y, s=1.0, rot=0):
    pts = []
    for i in range(10):
        a = math.pi * 2 * i / 10 + math.radians(rot)
        rr = (3.0 if i % 2 == 0 else 1.2) * s
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    path(doc, poly_d(pts, True), fill=shade(doc, INFL, light=0.4, dark=0.2), stroke='#7a0c37', w=0.22 * s)
    circ(doc, x, y, 0.55 * s, fill='#fff')


def cytokine(doc, x, y, s=1.0, rot=0, color=INFL):
    g = ['<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), rot, fmt(s))]
    g.append('<path d="M0,-2.8 L2.1,0 L0,2.8 L-2.1,0 Z" fill="%s" stroke="#7a0c37" stroke-width="0.35" stroke-linejoin="round"/>' % shade_rot(doc, color, rot, light=0.45, dark=0.18))
    g.append('</g>')
    doc.add(''.join(g))


def actin_cortex(doc, centerline, depth=9, spacing=2.2, seed=5, color='#C2571A', w=0.55, inward=1, lens=(5, 11), spread=38):
    """Branched actin filaments below a membrane segment. centerline = polyline along membrane; inward=+1 uses
    right-hand normal as the direction into the cytoplasm."""
    rnd = random.Random(seed)
    res = resample(centerline, spacing, closed=False)
    nm = normals(res, closed=False)
    out = []
    for p, n in zip(res, nm):
        dirx, diry = n[0] * inward, n[1] * inward
        a0 = math.atan2(diry, dirx) + math.radians(rnd.uniform(-spread, spread))
        L = rnd.uniform(*lens)
        x0, y0 = p[0] + dirx * 0.8, p[1] + diry * 0.8
        x1, y1 = x0 + math.cos(a0) * L, y0 + math.sin(a0) * L
        out.append('M%s,%s L%s,%s' % (fmt(x0), fmt(y0), fmt(x1), fmt(y1)))
        if rnd.random() < 0.75:
            t = rnd.uniform(0.35, 0.8)
            bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            a1 = a0 + math.radians(70 * rnd.choice((-1, 1)))
            L2 = L * rnd.uniform(0.4, 0.8)
            out.append('M%s,%s L%s,%s' % (fmt(bx), fmt(by), fmt(bx + math.cos(a1) * L2), fmt(by + math.sin(a1) * L2)))
    doc.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" opacity="0.9"/>' % (' '.join(out), color, fmt(w)))


def microtubule(doc, pts, color='#8A93A3', w=0.55, dash='3 1.4'):
    path(doc, cr_path(pts, False), stroke=color, w=w, dash=dash, op=0.9)


def nlrp3(doc, x, y, s=1.0):
    """NLRP3 inflammasome wheel: ring of NLRP3 + ASC speck + caspase-1."""
    if s >= 1:
        contact_shadow(doc, x, y, 5.7 * s, strength=0.1)
    body = shade(doc, INFL, light=0.42, dark=0.2)
    for i in range(7):
        a = 2 * math.pi * i / 7
        cx, cy = x + math.cos(a) * 4.2 * s, y + math.sin(a) * 4.2 * s
        circ(doc, cx, cy, 1.55 * s, fill=body, stroke='#7a0c37', w=0.25 * s)
        if s >= 1:
            circ(doc, cx - 0.5 * s, cy - 0.55 * s, 0.36 * s, fill='#fff', op=0.7)
    circ(doc, x, y, 2.3 * s, fill=shade(doc, '#F7B6CF', light=0.5, dark=0.15), stroke='#7a0c37', w=0.3 * s)
    circ(doc, x, y, 0.8 * s, fill='#7a0c37')


def membrane_tag(doc, x, y, text, color, size=3.4):
    w = text_width(text, size, 700) + 3.2
    rect(doc, x - w / 2, y - size * 0.95, w, size * 1.55, fill=color, r=size * 0.775)
    T(doc, x, y + size * 0.0, text, size=size, weight=700, fill='#fff', anchor='middle')
