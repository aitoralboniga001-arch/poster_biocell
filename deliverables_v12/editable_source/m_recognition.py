"""Section 2: recognition and engulfment, magnified at the bacterium contact site 2.1 (left column).

One frameless, feathered window (rounded superellipse) left of the contact bacterium.  The macrophage bilayer is
drawn vertically, as at 2.1: bacterium envelope on the LEFT, macrophage cytosol on the RIGHT.
  left    Gram-negative envelope: inner membrane, thin peptidoglycan, outer membrane with LPS (O-antigen chains);
          surface ligands IgG (Fab on O-antigen, Fc toward the cell), covalently bound iC3b, mannose-rich glycans.
  middle  receptors spanning the bilayer: CD14 + TLR4-MD-2 (LPS), mannose receptor CD206 (CTLD chain),
          CR3 (CD11b/CD18), FcgR (IgG Fc, ITAM tail).
  right   Src -> ITAM-P -> Syk -> PI3K (PIP2 -> PIP3) -> Cdc42-GTP -> WASP and Rac-GTP -> WAVE -> Arp2/3 -> F-actin (70 deg)
          whose barbed ends push the membrane out as an incipient pseudopod (lower end of the window);
          TLR4 TIR -> MyD88 -> inflammatory signal (NF-kB -> cytokines).
Scale: bilayer ~4.6 mm = 5 nm, so ~0.9 mm per nm (filaments thinner than scale for legibility)."""
import math, random
from lib import *
import geom as G
from layout2 import heading
from style import shade, shade_rot, sheen, spec, tone, lighten, darken, mix, contact_shadow

# ------------------------------------------------------------------ identity colours
NAVY_ = G.MOL['IgG']            # IgG / FcgR
TEAL_ = G.MOL['CR3']            # iC3b / CR3
BROWN_ = G.MOL['MR']            # mannose receptor
PLUM = '#8E3B8F'                # TLR4 / MD-2 / CD14 / LPS (poster-wide override of the brief's magenta)
ACT = G.MOL['actin']            # F-actin / Arp2/3
OLIVE = BACT
PHOS = M6P                      # phosphate (gold)
MANN = '#3E9B57'                # mannose (SNFG green circle)
KIN = '#6F7A8A'                 # signalling intermediates: neutral slate
MEM = '#C4806C'                 # macrophage plasma membrane (as in the cell)
LINK_ = '#9C8F7C'
LBL = '#3B4350'                 # neutral label ink

# ------------------------------------------------------------------ window geometry (poster mm)
WX, WY, WA, WB, WN = 111.0, 381.0, 85.0, 95.0, 3.0      # superellipse centre, half-axes, exponent
FEATHER = 0.86
RING_R = 25.0

# bacterium outer membrane centre: gently convex toward the macrophage (radius ~ 260 mm)
OM_X0, OM_Y0, OM_R = 59.5, 378.0, 270.0


def om_x(y):
    return OM_X0 - (y - OM_Y0) ** 2 / (2 * OM_R)


def om_n(y):
    """unit normal of the envelope at height y, pointing toward the macrophage (right)."""
    dx = 1.0
    dy = (y - OM_Y0) / OM_R
    L = math.hypot(dx, dy)
    return dx / L, dy / L


def env_pt(y, off):
    nx, ny = om_n(y)
    return om_x(y) + nx * off, y + ny * off


# macrophage membrane centreline: straight at x 103, bulging out (pseudopod) at the lower end
MEM_CTRL = [(110, 262 + 10 * i) for i in range(14)] + [(110, 402), (109.4, 411), (106.8, 420), (102.0, 429.5), (97.2, 439),
                                                    (94.2, 449), (93.6, 458.5), (95.8, 467.5), (100.6, 475.5), (106.2, 483),
                                                    (109.6, 492), (110.5, 502)]
MEM_PTS = cr_sample(MEM_CTRL, closed=False, per=12)


def mem_x(y):
    for (x0, y0), (x1, y1) in zip(MEM_PTS, MEM_PTS[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * ((y - y0) / ((y1 - y0) or 1e-9))
    return MEM_PTS[0][0] if y < MEM_PTS[0][1] else MEM_PTS[-1][0]


# ------------------------------------------------------------------ small drawing helpers
def _se(k=1.0, N=160):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N
        c, s = math.cos(t), math.sin(t)
        pts.append((WX + k * WA * math.copysign(abs(c) ** (2 / WN), c), WY + k * WB * math.copysign(abs(s) ** (2 / WN), s)))
    return pts


def _se_at(deg):
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return WX + WA * math.copysign(abs(c) ** (2 / WN), c), WY + WB * math.copysign(abs(s) ** (2 / WN), s)


def _ug(doc, kind, stops, **a):
    gid = doc.uid('rg_')
    st = ''.join('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (fmt(o), c, fmt(op)) for o, c, op in stops)
    at = ' '.join('%s="%s"' % (k, fmt(v)) for k, v in a.items())
    doc.defs.append('<%sGradient id="%s" gradientUnits="userSpaceOnUse" %s>%s</%sGradient>' % (kind, gid, at, st, kind))
    return 'url(#%s)' % gid


def window_open(doc):
    """Frameless feathered superellipse: nested masks give a linear fade over the outer 14 %."""
    K = 26
    layers = []
    for i in range(K):
        k = 1 - (1 - FEATHER) * i / (K - 1)
        a = 1.0 / (K - i)
        layers.append('<path d="%s" fill="#fff" fill-opacity="%s"/>' % (poly_d(_se(k), True), fmt(round(a, 4))))
    mid = doc.uid('recmask')
    doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">%s</mask>' % (
        mid, fmt(WX - WA - 2), fmt(WY - WB - 2), fmt(2 * WA + 4), fmt(2 * WB + 4), ''.join(layers)))
    doc.add('<g mask="url(#%s)">' % mid)


def window_close(doc):
    doc.add('</g>')


def dom(doc, cx, cy, rx, ry, rot, color, light=0.45, dark=0.2, sw=0.28, glint=False):
    """One protein domain: lit ellipse, toned outline."""
    ell(doc, cx, cy, rx, ry, fill=shade_rot(doc, color, rot, light=light, dark=dark), stroke=tone(color, 0.45), w=sw, rot=rot)
    if glint and min(rx, ry) >= 1.6:
        spec(doc, cx, cy, min(rx, ry), a0=205, a1=245, op=0.55, inset=0.6, w=0.3)


def ball(doc, cx, cy, r, color, light=0.45, dark=0.2, sw=0.28, glint=True):
    circ(doc, cx, cy, r, fill=shade(doc, color, light=light, dark=dark), stroke=tone(color, 0.45), w=sw)
    if glint and r >= 1.7:
        spec(doc, cx, cy, r, a0=205, a1=245, op=0.6, inset=0.62, w=max(0.28, r * 0.1))


def tm_helix(doc, x0, x1, y, color, w=2.0):
    """Transmembrane helix crossing the (vertical) bilayer from x0 to x1."""
    path(doc, 'M%s,%s L%s,%s' % (fmt(x0), fmt(y), fmt(x1), fmt(y)), stroke=tone(color, 0.45), w=w + 0.5)
    path(doc, 'M%s,%s L%s,%s' % (fmt(x0), fmt(y), fmt(x1), fmt(y)), stroke=sheen(doc, color, 0.4, 0.15, angle=90), w=w)
    path(doc, 'M%s,%s L%s,%s' % (fmt(x0 + 0.3), fmt(y - w * 0.22), fmt(x1 - 0.3), fmt(y - w * 0.22)), stroke='#FFFFFF', w=0.3, op=0.45)


def bilayer_path(doc, pts, color, core, w=4.6, heads=None, shadow=True, lit=-1):
    """Toned lipid bilayer along a polyline (two leaflets of head-group beads, pale hydrophobic core).
    lit = side (+1 right-hand normal, -1 left) that gets the faint top-left highlight."""
    d = poly_d(pts)
    if shadow:
        path(doc, poly_d([(x + 0.7, y + 1.0) for x, y in pts]), stroke='#5B3426', w=w + 1.2, op=0.08, cap='butt')
    path(doc, d, stroke=tone(color, 0.2), w=w + 0.8, cap='butt')
    path(doc, d, stroke=color, w=w, cap='butt')
    path(doc, d, stroke=core, w=w * 0.38, cap='butt')
    hc = heads or tone(color, 0.42)
    for off in (-w * 0.37, w * 0.37):
        path(doc, poly_d(offset_poly(pts, off, closed=False)), stroke=hc, w=w * 0.27, dash='0.01 %s' % fmt(w * 0.46), cap='round')
    path(doc, poly_d(offset_poly(pts, lit * (w * 0.5 + 0.35), closed=False)), stroke='#FFFFFF', w=0.3, op=0.55, cap='butt')


def chain(doc, pts, r, color, sw=0.22, light=0.42):
    """Bead chain (glycan / O-antigen)."""
    path(doc, poly_d(pts), stroke=tone(color, 0.35), w=r * 0.55)
    for (x, y) in pts:
        circ(doc, x, y, r, fill=shade(doc, color, light=light, dark=0.15), stroke=tone(color, 0.45), w=sw)


def lbl(doc, x, y, s, color=LBL, size=4.6, weight=600, anchor='start', halo=None, italic=False):
    T(doc, x, y, s, size=size, weight=weight, fill=color, anchor=anchor, halo=halo, italic=italic)


def hair(doc, pts, color, w=0.25):
    leader(doc, pts, color=color, w=w, dot=False, bow=0.0)


# ------------------------------------------------------------------ backgrounds
CLEFT = '#F3F5EF'


def backgrounds(doc):
    x0, x1, y0, y1 = WX - WA - 2, WX + WA + 2, WY - WB - 2, WY + WB + 2
    # extracellular cleft (alveolar lining fluid)
    rect(doc, x0, y0, x1 - x0, y1 - y0, fill=_ug(doc, 'linear', [(0, '#F6F8F3', 1), (1, '#EEF3EF', 1)], x1=0, y1=y0, x2=0, y2=y1))
    # bacterial cytoplasm + periplasm (left of the outer membrane)
    ys = [y0 + i * 2 for i in range(int((y1 - y0) / 2) + 2)]
    left = [env_pt(y, -2.3) for y in ys]
    path(doc, poly_d([(x0, y0)] + left + [(x0, y1)], True), fill=_ug(doc, 'linear', [(0, '#DCE3B2', 1), (1, '#EEF1D8', 1)],
                                                                       x1=x0, y1=0, x2=om_x(WY), y2=0))
    # macrophage cytosol (right of the membrane): same peach as the cell
    path(doc, poly_d(MEM_PTS + [(x1 + 2, MEM_PTS[-1][1]), (x1 + 2, MEM_PTS[0][1])], True),
         fill=_ug(doc, 'linear', [(0, '#FBEDE4', 1), (0.5, '#FCEFE7', 1), (1, '#F7DFD1', 1)], x1=100, y1=0, x2=x1, y2=0))


# ------------------------------------------------------------------ bacterium envelope
def envelope(doc):
    ys = [WY - WB - 6 + i * 1.5 for i in range(int((2 * WB + 12) / 1.5) + 1)]
    im = [env_pt(y, -15.5) for y in ys]
    om = [env_pt(y, 0) for y in ys]
    # periplasm tint
    path(doc, poly_d(im + om[::-1], True), fill='#F2F4E2', op=0.85)
    bilayer_path(doc, im, tone(OLIVE, -0.1), '#F7F8E8', w=3.8, heads=tone(OLIVE, 0.5), shadow=False)
    # thin peptidoglycan: two glycan strands + peptide cross-links
    pgc = tone(OLIVE, 0.38)
    for off in (-9.4, -6.6):
        path(doc, poly_d([env_pt(y, off) for y in ys]), stroke=pgc, w=0.6, dash='1.5 0.45', cap='butt', op=0.75)
    k = 0
    for y in ys[::2]:
        k += 1
        a, b = env_pt(y, -9.4), env_pt(y, -6.6)
        if k % 2:
            path(doc, poly_d([a, b]), stroke=pgc, w=0.34, op=0.75)
    # outer membrane
    bilayer_path(doc, om, OLIVE, '#F5F7E2', w=4.2, heads=tone(OLIVE, 0.5), shadow=False)
    # lipid A heads in the outer leaflet (plum) and LPS chains (core + O-antigen) into the cleft
    rnd = random.Random(21)
    lps_light = mix(PLUM, '#FFFFFF', 0.5)
    y = WY - WB - 4
    k = 0
    while y < WY + WB + 4:
        k += 1
        base = env_pt(y, 1.55)
        circ(doc, base[0], base[1], 0.62, fill=PLUM)
        nx, ny = om_n(y)
        L = rnd.uniform(9.0, 14.5)
        pts = []
        steps = int(L / 1.45)
        ph = rnd.uniform(0, 6.28)
        for s in range(1, steps + 1):
            t = s * 1.45
            wob = 0.55 * math.sin(ph + s * 1.25)
            pts.append((base[0] + nx * t - ny * wob, base[1] + ny * t + nx * wob))
        core, oant = pts[:2], pts[1:]
        path(doc, poly_d([base] + pts), stroke=mix(PLUM, '#FFFFFF', 0.25), w=0.38)
        for (px, py) in oant:
            circ(doc, px, py, 0.5, fill=lps_light, stroke=mix(PLUM, '#FFFFFF', 0.15), w=0.14)
        for (px, py) in core:
            circ(doc, px, py, 0.55, fill=mix(PLUM, '#FFFFFF', 0.2))
        y += rnd.uniform(2.3, 3.1)


def lps_tip(y):
    """approximate O-antigen tip position at height y."""
    return env_pt(y, 15.5)


# ------------------------------------------------------------------ macrophage membrane
def macrophage_membrane(doc, pip3=(400, 450)):
    bilayer_path(doc, MEM_PTS, MEM, '#FDEFE8', w=4.6, heads='#A9604F', lit=-1)
    # PIP3 (3-phosphoinositide) head groups in the inner leaflet where PI3K acts
    inner = offset_poly(MEM_PTS, 1.7, closed=False)
    pts = [p for p in resample(inner, 2.05, closed=False) if pip3[0] <= p[1] <= pip3[1]]
    for i, (x, y) in enumerate(pts):
        if i % 2 == 0:
            circ(doc, x, y, 0.72, fill=PHOS, stroke='#8A6A12', w=0.14)


# ------------------------------------------------------------------ ligands + receptors
def igg(doc, hx, hy, ang=0.0, spread=50, k=1.15):
    """IgG: hinge at (hx, hy); Fc points along ang (deg, 0 = +x = toward the macrophage), Fabs splay back.
    Heavy chains darker, light chains paler; each Ig domain one lit ellipse."""
    hc = NAVY_
    lc = mix(NAVY_, '#FFFFFF', 0.5)

    def U(a):
        return math.cos(math.radians(a)), math.sin(math.radians(a))

    ux, uy = U(ang)
    px, py = -uy, ux
    # hinge
    path(doc, 'M%s,%s L%s,%s' % (fmt(hx), fmt(hy), fmt(hx + ux * 2.0 * k), fmt(hy + uy * 2.0 * k)), stroke=tone(hc, 0.4), w=0.6)
    tips = []
    for sgn in (-1, 1):
        a = ang + 180 + sgn * spread
        vx, vy = U(a)
        qx, qy = -vy, vx
        path(doc, 'M%s,%s L%s,%s' % (fmt(hx), fmt(hy), fmt(hx + vx * 1.8 * k), fmt(hy + vy * 1.8 * k)), stroke=tone(hc, 0.4), w=0.6)
        for dpos in (3.2, 7.2):
            for side, c in ((1, hc), (-1, lc)):
                s_ = side * sgn            # heavy chain on the inner side of each arm
                cx, cy = hx + (vx * dpos + qx * s_ * 1.12) * k, hy + (vy * dpos + qy * s_ * 1.12) * k
                dom(doc, cx, cy, 1.95 * k, 1.1 * k, a, c, light=0.42, dark=0.18, sw=0.25)
        tips.append((hx + vx * 9.4 * k, hy + vy * 9.4 * k))
    # Fc: CH2 + CH3 of the two heavy chains
    for dpos in (3.6, 7.5):
        for side in (-1, 1):
            cx, cy = hx + (ux * dpos + px * side * 1.12) * k, hy + (uy * dpos + py * side * 1.12) * k
            dom(doc, cx, cy, 1.95 * k, 1.1 * k, ang, hc, light=0.42, dark=0.18, sw=0.25)
    return tips, (hx + ux * 9.6 * k, hy + uy * 9.6 * k)


def fcgr(doc, y, fc_end):
    """FcgR (2 Ig-like domains, single TM, ITAM-bearing tail) binding the IgG Fc."""
    xo = mem_x(y)
    tm_helix(doc, xo - 3.0, xo + 3.0, y, NAVY_, w=1.7)
    d2 = (xo - 6.6, y + 1.2)
    d1 = (fc_end[0] + 2.3, fc_end[1] + 1.6)
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(xo - 3.0), fmt(y), fmt(xo - 4.4), fmt(y + 1.2), fmt(d2[0] + 2.4), fmt(d2[1])), stroke=tone(NAVY_, 0.3), w=0.9)
    dom(doc, d2[0], d2[1], 2.9, 2.1, -15, NAVY_, glint=True)
    dom(doc, d1[0], d1[1], 2.8, 2.05, -40, NAVY_, glint=True)
    return xo


def itam_tail(doc, y, xo):
    """Cytoplasmic tail with the ITAM; two phospho-tyrosines (gold P dots)."""
    pts = [(xo + 2.8, y), (xo + 7, y + 0.6), (xo + 11, y + 0.2), (xo + 15.5, y + 1.0), (xo + 19, y + 0.6)]
    path(doc, cr_path(pts, False), stroke=tone(NAVY_, 0.35), w=1.25)
    path(doc, cr_path(pts, False), stroke=NAVY_, w=0.85)
    ps = [(xo + 9.8, y + 0.3), (xo + 15.2, y + 0.95)]
    return ps


def pdot(doc, x, y, r=1.15):
    circ(doc, x, y, r, fill=shade(doc, PHOS, light=0.45, dark=0.12), stroke='#7A5A08', w=0.2)
    T(doc, x, y + r * 0.62, 'P', size=r * 1.55, weight=700, fill='#4A3500', anchor='middle')


def cr3(doc, y):
    """CR3 = CD11b (alpha_M, with the I domain) + CD18 (beta2), extended-open, binding iC3b."""
    xo = mem_x(y)
    ca, cb = mix(TEAL_, '#FFFFFF', 0.18), tone(TEAL_, 0.12)
    ya, yb = y - 2.3, y + 2.3
    tm_helix(doc, xo - 3.0, xo + 3.0, ya, ca, w=1.5)
    tm_helix(doc, xo - 3.0, xo + 3.0, yb, cb, w=1.5)
    # CD18 leg: I-EGF beads + beta-tail, hybrid, beta-I
    for (x_, r_) in ((xo - 4.6, 1.15), (xo - 7.0, 1.15), (xo - 9.4, 1.15), (xo - 11.8, 1.15)):
        ball(doc, x_, yb + 0.3, r_, cb, glint=False, sw=0.22)
    dom(doc, xo - 15.0, yb + 0.6, 2.0, 1.45, 8, cb)
    dom(doc, xo - 19.0, yb - 0.2, 2.2, 1.7, -10, cb, glint=True)
    # CD11b leg: calf-2, calf-1, thigh, beta-propeller head, alpha-I domain
    for (x_, rx_, rot_) in ((xo - 5.4, 2.3, -4), (xo - 10.0, 2.3, -6), (xo - 14.6, 2.3, -10)):
        dom(doc, x_, ya - 0.3, rx_, 1.45, rot_, ca, glint=False)
    px, py = xo - 21.0, ya - 2.4
    ball(doc, px, py, 3.0, ca)
    for k in range(7):
        a = math.radians(k * 360 / 7 + 10)
        path(doc, 'M%s,%s L%s,%s' % (fmt(px + math.cos(a) * 1.0), fmt(py + math.sin(a) * 1.0), fmt(px + math.cos(a) * 2.7),
                                     fmt(py + math.sin(a) * 2.7)), stroke=tone(ca, 0.35), w=0.22, op=0.8)
    ai = (px - 4.2, py - 1.0)
    ball(doc, ai[0], ai[1], 1.9, tone(TEAL_, 0.05))
    return xo, ai, (px, py)


def ic3b(doc, ai, y):
    """iC3b: TED (C3d) domain covalently (thioester-derived ester bond) bound to the surface, contacted by the alpha-I
    domain; the MG-ring core rides on the opened CUB linker."""
    col = mix(TEAL_, '#FFFFFF', 0.45)
    ted = (ai[0] - 3.6, ai[1] + 2.4)
    # covalent bond to an O-antigen sugar
    anchor = env_pt(ted[1] + 2.0, 10.0)
    path(doc, 'M%s,%s L%s,%s' % (fmt(anchor[0]), fmt(anchor[1]), fmt(ted[0] - 1.8), fmt(ted[1] + 0.8)), stroke=tone(TEAL_, 0.35), w=0.55)
    circ(doc, anchor[0], anchor[1], 0.65, fill=tone(TEAL_, 0.35))
    # MG ring
    mg = (ted[0] - 1.0, ted[1] - 7.6)
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(ted[0]), fmt(ted[1] - 1.5), fmt(ted[0] + 2.6), fmt(ted[1] - 4.5), fmt(mg[0] + 1.5), fmt(mg[1] + 2.2)),
         stroke=tone(col, 0.35), w=0.55)
    for k in range(6):
        a = math.radians(k * 60 + 15)
        ball(doc, mg[0] + math.cos(a) * 2.35, mg[1] + math.sin(a) * 2.2, 1.25, col, glint=False, sw=0.22)
    ball(doc, mg[0], mg[1], 1.05, tone(col, 0.1), glint=False, sw=0.2)
    dom(doc, ted[0], ted[1], 2.5, 2.1, -20, col, glint=True)
    return ted, mg


def mannose_receptor(doc, y):
    """CD206: TM + 8 CTLDs + FN-II + Cys-rich N-terminal domain, bent so a middle CTLD meets the glycan."""
    xo = mem_x(y)
    tm_helix(doc, xo - 3.0, xo + 3.0, y, BROWN_, w=1.6)
    path(doc, 'M%s,%s L%s,%s' % (fmt(xo + 2.8), fmt(y), fmt(xo + 6.0), fmt(y + 0.8)), stroke=BROWN_, w=0.8)
    ctrl = [(xo - 3.0, y), (xo - 8, y - 0.5), (xo - 14, y - 0.9), (xo - 20, y - 0.5), (xo - 26, y + 0.4), (xo - 31.5, y + 0.8)]
    sp = cr_sample(ctrl, closed=False, per=10)
    beads = resample(sp, 2.85, closed=False)[1:11]
    path(doc, poly_d(sp[:len(sp)]), stroke=tone(BROWN_, 0.3), w=0.6)
    out = []
    for i, (bx, by) in enumerate(beads):
        if i < 8:
            dom(doc, bx, by, 1.55, 1.3, 0, BROWN_, light=0.42, dark=0.2, sw=0.22)
        elif i == 8:
            dom(doc, bx, by, 1.2, 1.0, 0, tone(BROWN_, -0.15), sw=0.22)
        else:
            dom(doc, bx, by, 1.35, 1.2, 0, tone(BROWN_, 0.1), sw=0.22)
        out.append((bx, by))
    return xo, out


def glycan(doc, root, tip_dir, n=4, seed=1, reach=1):
    """Mannose-rich glycan: short stem from the surface with a branched head of mannoses (SNFG green circles)."""
    rnd = random.Random(seed)
    ux, uy = tip_dir
    stem = [(root[0] + ux * s, root[1] + uy * s) for s in [0] + [1.6 + i * 1.75 for i in range(int(reach))]]
    path(doc, poly_d(stem), stroke=tone(MANN, 0.35), w=0.4)
    circ(doc, stem[1][0], stem[1][1], 0.62, fill='#2A62C0', stroke='#173B7A', w=0.14)      # GlcNAc (SNFG blue square-ish)
    nodes = [stem[-1]]
    head = stem[-1]
    pts = []
    for k, (a, L) in enumerate(((-38, 1.7), (36, 1.7), (-70, 3.1), (4, 3.2), (68, 3.0), (-18, 4.6), (30, 4.6))[:n + 2]):
        aa = math.atan2(uy, ux) + math.radians(a)
        pts.append((head[0] + math.cos(aa) * L, head[1] + math.sin(aa) * L))
    for p in pts:
        path(doc, poly_d([head, p]), stroke=tone(MANN, 0.35), w=0.32)
    for p in [head] + pts:
        circ(doc, p[0], p[1], 0.72, fill=shade(doc, MANN, light=0.4, dark=0.15), stroke=tone(MANN, 0.45), w=0.16)
    return pts


def _horseshoe(doc, cx, cy, r, a0, a1, color, hw=1.35):
    """LRR solenoid: a thick lit crescent along a circular arc (screen degrees a0 -> a1), with LRR striations."""
    n = 28
    sp = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
          for i in range(n + 1)]
    nm = normals(sp, closed=False)
    hs = [hw * (0.8 + 0.35 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    left = [(p[0] + q[0] * h, p[1] + q[1] * h) for p, q, h in zip(sp, nm, hs)]
    right = [(p[0] - q[0] * h, p[1] - q[1] * h) for p, q, h in zip(sp, nm, hs)]
    path(doc, poly_d(left + right[::-1], True), fill=shade(doc, color, light=0.42, dark=0.2), stroke=tone(color, 0.45), w=0.28)
    for i in range(2, n - 1, 3):
        p, q, h = sp[i], nm[i], hs[i]
        path(doc, 'M%s,%s L%s,%s' % (fmt(p[0] + q[0] * h * 0.7), fmt(p[1] + q[1] * h * 0.7), fmt(p[0] - q[0] * h * 0.7),
                                     fmt(p[1] - q[1] * h * 0.7)), stroke=lighten(color, 0.55), w=0.2, op=0.75)
    return sp


def tlr4_complex(doc, y1, y2):
    """Activated (TLR4-MD-2-LPS)2 'm'-shaped dimer.  Each TLR4 is single-pass: ONE TM bar, one LRR horseshoe whose
    opening faces the dimer centre, its own MD-2 in the opening; lipid A in each MD-2 bridges to the partner TLR4.
    Two TIR domains inside."""
    xo = mem_x((y1 + y2) / 2)
    yc = (y1 + y2) / 2
    r = 4.4
    md = mix(PLUM, '#FFFFFF', 0.42)
    cols = (PLUM, tone(PLUM, 0.14))
    for k, (ytm, sgn) in enumerate(((y1, -1), (y2, 1))):
        col = cols[k]
        ccx, ccy = xo - 10.4, ytm + sgn * 0.6          # horseshoe centre, just outside its own TM
        # opening faces the dimer centre (down for the upper receptor, up for the lower)
        if sgn < 0:
            sp = _horseshoe(doc, ccx, ccy, r, 28, -208, col)
        else:
            sp = _horseshoe(doc, ccx, ccy, r, -28, 208, col)
        # juxtamembrane stalk from the horseshoe's C-terminal end to the single TM helix
        path(doc, poly_d([sp[0], (xo - 3.0, ytm)]), stroke=tone(col, 0.3), w=0.85)
        tm_helix(doc, xo - 3.0, xo + 3.0, ytm, col, w=1.6)
        ball(doc, xo + 5.3, ytm, 1.8, col, glint=False)           # TIR domain
        # MD-2 seated in the opening of its own TLR4
        dom(doc, ccx - 0.4, ccy - sgn * 2.6, 2.0, 1.45, 0, md, glint=True)
    # lipid A of each LPS sits in an MD-2 pocket; acyl chains reach across the dimer interface to the partner
    for sgn in (-1, 1):
        lx, ly = xo - 12.6, yc + sgn * 2.4
        for j in range(3):
            yy = ly - sgn * (0.4 + j * 0.75)
            path(doc, 'M%s,%s l1.8,0 l0.9,%s l0.9,%s l0.9,%s' % (fmt(lx + 0.6), fmt(yy), fmt(-sgn * 0.5), fmt(sgn * 0.5), fmt(-sgn * 0.5)),
                 stroke=tone(PLUM, 0.5), w=0.28)
        circ(doc, lx, ly, 0.85, fill=tone(PLUM, 0.2))
        chain(doc, [(lx - 1.8, ly + sgn * 0.4), (lx - 3.6, ly + sgn * 0.9), (lx - 5.4, ly + sgn * 0.6), (lx - 7.2, ly + sgn * 1.1)],
              0.55, mix(PLUM, '#FFFFFF', 0.3), sw=0.14)
    return xo, (xo + 5.3, y1), (xo + 5.3, y2)


def cd14(doc, y):
    """CD14: GPI-anchored horseshoe that hands an LPS monomer to MD-2."""
    xo = mem_x(y)
    col = mix(PLUM, '#FFFFFF', 0.18)
    # GPI anchor in the outer leaflet
    path(doc, 'M%s,%s L%s,%s' % (fmt(xo - 1.0), fmt(y), fmt(xo - 5.0), fmt(y)), stroke=tone(col, 0.35), w=0.5)
    circ(doc, xo - 1.2, y, 0.7, fill=tone(col, 0.35))
    c = [(xo - 5.0, y + 3.0), (xo - 8.6, y + 3.4), (xo - 11.2, y + 1.0), (xo - 10.8, y - 2.4), (xo - 7.6, y - 3.6)]
    sp = cr_sample(c, closed=False, per=10)
    nm = normals(sp, closed=False)
    h = 1.5
    left = [(p[0] + n[0] * h, p[1] + n[1] * h) for p, n in zip(sp, nm)]
    right = [(p[0] - n[0] * h, p[1] - n[1] * h) for p, n in zip(sp, nm)]
    path(doc, poly_d([(xo - 5.0, y)] + [sp[0]]), stroke=tone(col, 0.3), w=0.6)
    path(doc, poly_d(left + right[::-1], True), fill=shade(doc, col, light=0.42, dark=0.2), stroke=tone(col, 0.45), w=0.26)
    # LPS monomer in the hydrophobic pocket
    lx, ly = xo - 8.4, y
    for k in range(3):
        path(doc, 'M%s,%s l1.6,0.25 l0.7,-0.4' % (fmt(lx), fmt(ly - 0.8 + k * 0.8)), stroke=tone(PLUM, 0.5), w=0.26)
    chain(doc, [(lx - 1.2, ly), (lx - 3.0, ly - 0.5), (lx - 4.8, ly + 0.2), (lx - 6.6, ly - 0.4)], 0.55, mix(PLUM, '#FFFFFF', 0.3), sw=0.14)
    return xo


# ------------------------------------------------------------------ cytosolic machinery
def kinase(doc, x, y, r, color, rot=0):
    """Bilobed kinase: smaller N-lobe on top-left of a larger C-lobe."""
    dom(doc, x + r * 0.25, y + r * 0.25, r, r * 0.86, rot, color, glint=False)
    dom(doc, x - r * 0.5, y - r * 0.45, r * 0.68, r * 0.6, rot, mix(color, '#FFFFFF', 0.15), glint=True)


def gtpase(doc, x, y, r, anchor):
    """Small GTPase (Rac/Cdc42) prenyl-anchored in the inner leaflet, with bound GTP."""
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(anchor[0]), fmt(anchor[1]), fmt((anchor[0] + x) / 2), fmt(y + 1.5), fmt(x - r * 0.8), fmt(y + r * 0.3)),
         stroke=tone(KIN, 0.3), w=0.5)
    ball(doc, x, y, r, mix(KIN, '#7FA6A0', 0.35))
    circ(doc, x + r * 0.62, y - r * 0.55, r * 0.42, fill=shade(doc, '#F2C14E', light=0.4, dark=0.1), stroke='#8A6A12', w=0.16)


def filament(doc, a, b, w=1.35):
    """F-actin: toned rod with subunit beading; barbed end at b."""
    d = poly_d([a, b])
    path(doc, d, stroke=tone(ACT, 0.42), w=w + 0.45, cap='round')
    path(doc, d, stroke=ACT, w=w, cap='round')
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    path(doc, poly_d([(a[0] - uy * w * 0.18, a[1] + ux * w * 0.18), (b[0] - uy * w * 0.18, b[1] + ux * w * 0.18)]),
         stroke=lighten(ACT, 0.55), w=w * 0.3, dash='%s %s' % (fmt(w * 0.45), fmt(w * 0.4)), cap='butt', op=0.9)


def _seg_hit(p, q, a, b):
    """parameter t on p->q where it crosses segment a->b, or None."""
    d1 = (q[0] - p[0], q[1] - p[1]); d2 = (b[0] - a[0], b[1] - a[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t = ((a[0] - p[0]) * d2[1] - (a[1] - p[1]) * d2[0]) / den
    u = ((a[0] - p[0]) * d1[1] - (a[1] - p[1]) * d1[0]) / den
    return t if (0 < t <= 1 and 0 <= u <= 1) else None


def actin_network(doc, seed=120):
    """Dendritic F-actin under the bulging membrane.  One mother per front point runs 35 deg off the local membrane
    normal with its barbed end at the inner leaflet; Arp2/3 complexes on it nucleate daughters at 70 deg (so they run
    35 deg the other way, barbed ends again toward the membrane), and long daughters branch once more.  Filaments that
    would cross an existing one are rejected, so the array reads as Y-shaped trees, not a lattice."""
    rnd = random.Random(seed)
    fil, nodes = [], []
    gap = 3.0

    def free(x, y):
        return x >= mem_x(y) + gap and 431 <= y <= 492

    def grow(p, ang, maxL):
        ux, uy = math.cos(ang), math.sin(ang)
        L, x, y = 0.0, p[0], p[1]
        while L < maxL and free(x + ux * 0.3, y + uy * 0.3):
            x, y, L = x + ux * 0.3, y + uy * 0.3, L + 0.3
        return (x, y), L

    nm_in = normals(MEM_PTS, closed=False)          # right-hand normal = into the cytosol

    def out_normal(y):
        i = min(range(len(MEM_PTS)), key=lambda k: abs(MEM_PTS[k][1] - y))
        return math.atan2(-nm_in[i][1], -nm_in[i][0])

    def crosses(p, q, a, b):
        d1 = (q[0] - p[0], q[1] - p[1]); d2 = (b[0] - a[0], b[1] - a[1])
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            return False
        t = ((a[0] - p[0]) * d2[1] - (a[1] - p[1]) * d2[0]) / den
        u = ((a[0] - p[0]) * d1[1] - (a[1] - p[1]) * d1[0]) / den
        return 0.02 < t < 0.98 and 0.02 < u < 0.98

    def ok(p, q, skip=()):
        return all(not crosses(p, q, a, b) for i, (a, b) in enumerate(fil) if i not in skip)

    s = 1
    for yk in [434 + i * 6.0 for i in range(10)]:
        d = out_normal(yk) + s * math.radians(35 + rnd.uniform(-4, 4))
        Lm = rnd.uniform(12, 22)
        F = (mem_x(yk) + gap + 0.3, yk)
        P = (F[0] - math.cos(d) * Lm, F[1] - math.sin(d) * Lm)
        end, L = grow(P, d, Lm + 4)
        if not ok(P, end):
            s = -s
            continue
        fil.append((P, end)); mi = len(fil) - 1
        for frac in (rnd.uniform(0.25, 0.4), rnd.uniform(0.6, 0.7)):
            q = (P[0] + math.cos(d) * L * frac, P[1] + math.sin(d) * L * frac)
            a2 = d - s * math.radians(70 + rnd.uniform(-4, 4))
            e2, L2 = grow(q, a2, 30)
            if L2 < 3 or not ok(q, e2, skip=(mi,)):
                continue
            fil.append((q, e2)); di = len(fil) - 1; nodes.append((q, d, a2))
            if L2 > 9:
                q3 = (q[0] + math.cos(a2) * L2 * 0.45, q[1] + math.sin(a2) * L2 * 0.45)
                a3 = a2 + s * math.radians(70 + rnd.uniform(-4, 4))
                e3, L3 = grow(q3, a3, 30)
                if L3 >= 3 and ok(q3, e3, skip=(di,)):
                    fil.append((q3, e3)); nodes.append((q3, a2, a3))
        s = -s
    for a, b in fil:
        filament(doc, a, b, w=1.0)
    for (q, a1, a2) in nodes:
        x, y = q
        dx, dy = math.cos(a2), math.sin(a2)
        ball(doc, x + dx * 0.5, y + dy * 0.5, 0.95, tone(ACT, 0.38), glint=False, sw=0.18)
        ball(doc, x + dx * 0.5 + math.cos(a1) * 1.1, y + dy * 0.5 + math.sin(a1) * 1.1, 0.75, tone(ACT, 0.58), glint=False, sw=0.18)
    for a, b in fil:
        if b[0] < mem_x(b[1]) + 3.6:
            circ(doc, b[0], b[1], 0.5, fill=lighten(ACT, 0.6))
    return fil, nodes


# ------------------------------------------------------------------ source ring + focus lines
def _tangent_pt(P, C, r, side):
    dx, dy = P[0] - C[0], P[1] - C[1]
    d = math.hypot(dx, dy)
    th = math.atan2(dy, dx)
    a = math.acos(r / d)
    t = th + side * a
    return C[0] + r * math.cos(t), C[1] + r * math.sin(t)


def focus(doc):
    cx, cy = G.CONTACT_21
    cx -= 3.0
    col = mix(PHAG, LINK_, 0.55)
    W1, W2 = zmap(_se_at(-27)), zmap(_se_at(8))
    T1 = _tangent_pt(W1, (cx, cy), RING_R, +1)
    T2 = _tangent_pt(W2, (cx, cy), RING_R, -1)
    for (p, q) in ((T1, W1), (T2, W2)):
        g = _ug(doc, 'linear', [(0, col, 0.8), (1, col, 0.1)], x1=p[0], y1=p[1], x2=q[0], y2=q[1])
        path(doc, 'M%s,%s L%s,%s' % (fmt(p[0]), fmt(p[1]), fmt(q[0]), fmt(q[1])), stroke=g, w=0.25, cap='butt')
    circ(doc, cx, cy, RING_R, fill='none', stroke='#FFFFFF', w=0.9, op=0.5)
    circ(doc, cx, cy, RING_R, fill='none', stroke=col, w=0.3, op=0.95)


# ------------------------------------------------------------------ the window
Y_CD14, Y_TLR = 302.0, (315.5, 328.5)
Y_MR, Y_CR3, Y_FC = 350.0, 370.0, 391.0
COL_X = 141.5                    # left edge of the cytosolic label column


def window(doc):
    window_open(doc)
    backgrounds(doc)
    envelope(doc)
    fil, nodes = actin_network(doc)
    macrophage_membrane(doc, pip3=(408, 456))

    # ---- TLR4 / CD14 (top)
    xt, tir1, tir2 = tlr4_complex(doc, *Y_TLR)
    cd14(doc, Y_CD14)
    my = (xt + 12.5, (Y_TLR[0] + Y_TLR[1]) / 2)
    mc = mix(PLUM, '#6A6A8A', 0.45)
    path(doc, poly_d([(tir1[0] + 1.2, tir1[1] + 1.0), (my[0] - 1.5, my[1] - 0.8)]), stroke=tone(mc, 0.3), w=0.5)
    path(doc, poly_d([(tir2[0] + 1.2, tir2[1] - 1.0), (my[0] - 1.5, my[1] + 0.8)]), stroke=tone(mc, 0.3), w=0.5)
    ball(doc, my[0], my[1], 2.1, mc)                          # MyD88 TIR
    ball(doc, my[0] + 3.9, my[1] - 0.4, 1.9, tone(mc, 0.12))  # MyD88 death domain
    arrow(doc, [(my[0] + 7.0, my[1] - 0.8), (my[0] + 26, my[1] - 4.0), (my[0] + 46, my[1] - 10.5)], INFL, 'signal', w=1.25, head=5.0)

    # ---- mannose receptor + glycans
    xm, beads = mannose_receptor(doc, Y_MR)
    gy = beads[4][1] + 0.5
    glycan(doc, env_pt(gy + 1.0, 2.6), om_n(gy), n=5, seed=3, reach=7)
    for yy in (Y_MR - 16.5, Y_CR3 + 9.5, Y_FC + 40, Y_FC + 52):
        glycan(doc, env_pt(yy, 2.6), om_n(yy), n=3, seed=int(yy), reach=int(yy) % 3 + 4)

    # ---- CR3 + iC3b
    xc, ai, prop = cr3(doc, Y_CR3)
    ic3b(doc, ai, Y_CR3)

    # ---- IgG + FcgR
    tips, fc_end = igg(doc, 83.2, Y_FC - 1.6, ang=0, spread=54)
    xf = fcgr(doc, Y_FC, fc_end)
    ps = itam_tail(doc, Y_FC, xf)

    # ---- cytosolic cascade, in order: Src -> ITAM-P -> Syk -> PI3K -> Cdc42/WASP + Rac/WAVE -> Arp2/3
    srcc = mix(KIN, '#8C7CA8', 0.3)
    src = (xf + 12.5, Y_FC - 7.0)
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(xf + 2.6), fmt(Y_FC - 7.6), fmt(xf + 6.0), fmt(Y_FC - 8.8), fmt(src[0] - 2.4), fmt(src[1] - 0.6)),
         stroke=tone(srcc, 0.3), w=0.5)                                      # myristoyl anchor
    kinase(doc, src[0], src[1], 2.3, srcc)
    for (px, py) in ps:
        pdot(doc, px, py + 0.1)
    arrow(doc, [(src[0] - 1.6, src[1] + 2.4), (ps[0][0] + 0.2, ps[0][1] - 1.5)], tone(srcc, 0.2), 'transport', w=0.45, head=1.7, bow=0.0)
    sykc = mix(KIN, '#4E7FA8', 0.35)
    sh = [(ps[0][0] + 0.2, ps[0][1] + 2.8), (ps[1][0] + 0.1, ps[1][1] + 2.8)]
    syk = (ps[1][0] + 7.6, Y_FC + 8.2)
    path(doc, poly_d([sh[0], sh[1], (syk[0] - 1.6, syk[1] - 0.6)]), stroke=tone(sykc, 0.3), w=0.55)
    for p in sh:
        ball(doc, p[0], p[1], 1.25, sykc, glint=False, sw=0.22)
    kinase(doc, syk[0], syk[1], 2.5, sykc)
    pi3k = (xf + 12.5, 412.0)
    pc = mix(KIN, '#A08C6E', 0.4)
    ball(doc, pi3k[0] - 4.4, pi3k[1] - 0.2, 1.7, tone(pc, 0.08), glint=False)
    ball(doc, pi3k[0], pi3k[1], 2.9, pc)
    # two parallel GTPase -> NPF modules feeding the same Arp2/3
    cdc = (119.6, 420.6)
    wasp = (128.6, 421.0)
    rac = (119.6, 429.6)
    wave = (128.6, 430.0)
    gtpase(doc, cdc[0], cdc[1], 2.1, (mem_x(cdc[1]) + 2.3, cdc[1] - 0.6))
    gtpase(doc, rac[0], rac[1], 2.0, (mem_x(rac[1]) + 2.3, rac[1] - 0.6))
    wc = mix(KIN, '#A86E8C', 0.3)
    vc = mix(KIN, '#8E7AA8', 0.25)
    arp = min(nodes, key=lambda nd: math.hypot(nd[0][0] - 125, nd[0][1] - 439))[0]
    for (npf, c) in ((wasp, wc), (wave, vc)):
        path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(npf[0] - 0.5), fmt(npf[1] + 1.6), fmt(npf[0] - 1.0), fmt(arp[1] - 2.0),
                                          fmt(arp[0] + 1.2), fmt(arp[1] - 0.5)), stroke=tone(c, 0.3), w=0.55)   # VCA arm
    dom(doc, wasp[0], wasp[1], 2.8, 1.7, 0, wc, glint=True)
    dom(doc, wave[0], wave[1], 2.8, 1.7, 0, vc, glint=True)

    # ---- flow arrows (neutral ink, small)
    ink = '#5E6672'
    arrow(doc, [(syk[0] - 1.0, syk[1] + 2.8), (pi3k[0] + 2.4, pi3k[1] - 3.2)], ink, 'transport', w=0.6, head=2.4, bow=0.0)
    arrow(doc, [(pi3k[0] - 0.6, pi3k[1] + 2.9), (cdc[0] + 0.6, cdc[1] - 2.2)], ink, 'transport', w=0.55, head=2.0, bow=0.0)
    arrow(doc, [(pi3k[0] - 3.4, pi3k[1] + 2.2), (115.4, 421.8), (rac[0] - 1.6, rac[1] - 1.9)], ink, 'transport', w=0.55, head=2.0)
    arrow(doc, [(cdc[0] + 2.4, cdc[1]), (wasp[0] - 3.0, wasp[1])], ink, 'transport', w=0.55, head=2.0, bow=0.0)
    arrow(doc, [(rac[0] + 2.4, rac[1]), (wave[0] - 3.0, wave[1])], ink, 'transport', w=0.55, head=2.0, bow=0.0)
    window_close(doc)
    return dict(xt=xt, my=my, xm=xm, beads=beads, xc=xc, ai=ai, prop=prop, tips=tips, fc_end=fc_end, xf=xf, ps=ps, src=src,
                syk=syk, pi3k=pi3k, rac=rac, wasp=wasp, wave=wave, cdc=cdc, tir1=tir1, arp=arp)


def labels(doc, g):
    sz, s2 = 3.9, 3.7          # drawn inside the x1.20 group: effective 4.7 / 4.4 mm
    hl = '#FCEFE7'       # halo on the cytosol
    hc = CLEFT           # halo in the cleft
    # TLR4 module
    lbl(doc, g['xt'] - 17.5, Y_CD14 + 0.6, 'CD14', tone(PLUM, 0.25), sz, anchor='end', halo=hc)
    lbl(doc, g['xt'] - 17.0, Y_TLR[0] + 1.0, 'TLR4–MD-2', tone(PLUM, 0.25), sz, anchor='end', halo=hc)
    lbl(doc, g['my'][0] - 2.4, g['my'][1] + 7.8, 'MyD88', tone(PLUM, 0.35), s2, halo=hl)
    lbl(doc, COL_X, g['my'][1] + 3.0, 'NF-κB → inflammation', tone(INFL, 0.15), sz, halo=hl)
    # receptors (cytosolic side, next to their tails)
    lbl(doc, g['xm'] + 7.5, Y_MR + 1.6, 'MR', tone(BROWN_, 0.15), sz, halo=hl)
    lbl(doc, g['xc'] + 7.5, Y_CR3 + 1.6, 'CR3', tone(TEAL_, 0.15), sz, halo=hl)
    # ligands (in the cleft, clear of the LPS fringe)
    lbl(doc, 79.3, Y_MR - 5.6, 'glycans', tone(MANN, 0.3), s2, weight=400)
    lbl(doc, 84.0, Y_CR3 - 12.4, 'iC3b', tone(TEAL_, 0.25), sz, halo=hc)
    lbl(doc, 80.6, Y_FC + 10.6, 'IgG', tone(NAVY_, 0.15), sz)
    lbl(doc, g['xt'] - 22.5, (Y_TLR[0] + Y_TLR[1]) / 2 + 9.0, 'LPS', tone(PLUM, 0.25), sz, anchor='end', halo=hc)
    lbl(doc, g['xf'] - 6.0, Y_FC + 9.0, 'FcγR', tone(NAVY_, 0.15), sz, anchor='end', halo=hc)
    # cascade column, in signalling order
    lbl(doc, COL_X, g['src'][1] + 1.6, 'Src', LBL, sz, halo=hl)
    lbl(doc, g['ps'][1][0] + 5.8, Y_FC + 1.8, 'ITAM', tone(NAVY_, 0.15), s2, halo=hl)
    lbl(doc, COL_X, g['syk'][1] + 1.6, 'Syk', LBL, sz, halo=hl)
    lbl(doc, COL_X, g['pi3k'][1] + 1.6, 'PI3K', LBL, sz, halo=hl)
    lbl(doc, COL_X, g['wasp'][1] + 1.6, 'Cdc42 → WASP', LBL, sz, halo=hl)
    lbl(doc, COL_X, g['wave'][1] + 1.6, 'Rac → WAVE', LBL, sz, halo=hl)
    lbl(doc, COL_X, 443.0, 'Arp2/3', tone(ACT, 0.3), sz, halo=hl)
    hair(doc, [(g['arp'][0] + 1.6, g['arp'][1]), (COL_X - 1.2, 441.4)], tone(ACT, 0.1))
    lbl(doc, COL_X, 449.5, 'F-actin', tone(ACT, 0.3), sz, halo=hl)
    for key, dx in (('src', 3.0), ('pi3k', 3.6), ('wasp', 3.2), ('wave', 3.2)):
        x, y = g[key]
        if COL_X - (x + dx) > 3:
            hair(doc, [(x + dx, y), (COL_X - 1.2, y)], '#9AA0A8')
    # pseudopod
    lbl(doc, 66.0, 462.5, 'pseudopod', tone(ACT, 0.35), sz, halo=hc)
    hair(doc, [(87.4, 460.6), (mem_x(456) - 2.9, 456.0)], tone(ACT, 0.2))
    # scale bar: 10 nm (bilayer 4.6 mm = 5 nm)
    sb = 9.2
    path(doc, 'M%s,%s h%s' % (fmt(COL_X), fmt(461.0), fmt(sb)), stroke='#6B6455', w=0.4, cap='butt')
    for xx in (COL_X, COL_X + sb):
        path(doc, 'M%s,%s v-1.4' % (fmt(xx), fmt(461.7)), stroke='#6B6455', w=0.3, cap='butt')
    lbl(doc, COL_X + sb + 2.0, 462.4, '10 nm', '#6B6455', s2, weight=400)
    T(doc, 38.6, WY, 'bacterium', size=s2, fill=tone(OLIVE, 0.5), italic=True, anchor='middle', rot=-90)


# The whole window (art, labels, scale bar) is drawn in its native coordinates and enlarged as one group, so the scale
# bar stays true.  ZS / ZC: zoom factor and where the native window centre (WX, WY) lands on the sheet.
ZS = 1.2
ZC = (127.0, 380.0)


def zmap(p):
    return (ZC[0] + ZS * (p[0] - WX), ZC[1] + ZS * (p[1] - WY))


def draw(doc):
    x0, y0, x1, y1 = G.RECOG
    heading(doc, x0, G.RECOG_HEAD_Y, 2, 'Recognition')
    focus(doc)
    doc.add('<g transform="translate(%s,%s) scale(%s)">' % (fmt(ZC[0] - ZS * WX), fmt(ZC[1] - ZS * WY), fmt(ZS)))
    g = window(doc)
    labels(doc, g)
    doc.add('</g>')
