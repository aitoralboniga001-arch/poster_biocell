"""Zone E (V2): 4 Fusion on the late phagosome, 2.6 the giant phagolysosome (the point of the V), 2.7 Killing.

Everything is drawn in poster mm, inside the cell, at the place where it happens (no strips, no windows):
  * four lysosomes dock around LATE's free upper-right arc, each one a later moment of the same event
    (a tether -> b zipper -> c pore -> d recycle).  Where a lysosome meets LATE both membranes thicken smoothly from
    organelle scale to a molecular bilayer (head groups visible), and the molecules are drawn in that contact;
  * the phagolysosome: violet membrane, glowing acidic lumen, a bacterium breaking apart under four hydrolase
    families, ROS remnants, products leaving for reuse.  Its rim is enlarged locally for V-ATPase and NOX2;
  * a thin painted pH gauge threads the existing pH 6.5 / 5.5 tags and ends at pH 4.5 by the phagolysosome.
"""
import math, random
from lib import *
from style import shade, shade_rot, spec, tone, lighten, darken, mix, contact_shadow, SHADOW
import geom_v2 as V
import marks
from bio import hplus, enzyme_dot, hydrolase, ros, bacterium

LE_C = '#C23B2A'             # late phagosome membrane (skeleton LE_STROKE)
LY_C = '#6F36A8'             # lysosomal violet (skeleton LY_STROKE)
LY_FILL = '#E4D3F3'
DLY = '#5A2A8C'              # violet ink for names
RAB7, HOPS = '#C0392B', '#7A3FB5'
ARL8 = '#9B6A3C'
QA, QB, QC, RS = '#2E86AB', '#3FA796', '#8BAF3A', '#E07A5F'
NSF = '#6E7787'
VATP, NOX = '#E75A8B', '#C81D63'
HYD = BIO
RAC = '#8A4F6A'
LAB = 4.5                    # molecule label size
STEP = '#6E6556'

CX, CY, CR = V.LATE
# Contract bend: the phagolysosome is moved 22 mm right, 3 mm up and drawn 4 mm smaller (V: (600, 668, 68)) so that the
# late phagosome -> phagolysosome gap is wide enough for the c/d contacts and the fusion arrow.  The two route
# ribbons still end inside it (their convergence point (600, 668) lies 22 mm from its centre).
PLX, PLY, PLR = 622.0, 665.0, 64.0

W_LATE, CORE_LATE = 2.73, 0.84     # skeleton LATE membrane (vesicle(..., w=1.05)): band and light core
W_LY = 2.1                          # lysosome membrane at organelle scale
W_PL = 3.0                          # phagolysosome membrane at organelle scale
WM = 6.0                            # molecular-scale bilayer (~5 nm)


# ===================================================================== small helpers
def _ug(doc, kind, stops, **a):
    gid = doc.uid('zg')
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


def inkc(c, ratio=4.8, bg=CYTO):
    """Darken a label colour (same hue) until it reaches the contrast ratio on the cytoplasm."""
    lb = _lum(bg)
    k, out = 0.0, c
    while (lb + 0.05) / (_lum(out) + 0.05) < ratio and k < 0.9:
        k += 0.03
        out = darken(c, k)
    return out


def lab(doc, x, y, s, color, size=LAB, anchor='start', weight=600, halo=CYTO, italic=False):
    T(doc, x, y, s, size=size, weight=weight, fill=inkc(color), anchor=anchor, halo=halo, italic=italic)


def step(doc, x, y, letter, word, anchor='start'):
    """Quiet step mark: italic serif letter + word."""
    w = text_width(word, 4.6, 600) + 4.4
    x0 = x - w if anchor == 'end' else x
    T(doc, x0, y, letter, size=5.6, weight=400, fill=inkc(STEP), italic=True, family=SERIF, halo=CYTO)
    T(doc, x0 + 4.4, y, word, size=4.6, weight=600, fill=inkc(STEP), spacing=0.15, halo=CYTO)


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def bump(delta, half, flat=0.35):
    """1 on the central plateau, smooth fall to 0 at |delta| = half."""
    a = abs(delta) / half
    if a <= flat:
        return 1.0
    return smooth(1 - (a - flat) / (1 - flat))


def glob(doc, x, y, rx, ry, color, rot=0, light=0.5, w=0.3, sp=True):
    """Volumetric protein domain lit from the top-left."""
    ell(doc, x, y, rx, ry, fill=shade(doc, color, light=light, dark=0.16), stroke=tone(color, 0.42), w=w, rot=rot)
    if sp and min(rx, ry) >= 1.5:
        spec(doc, x, y, min(rx, ry), a0=205, a1=245, op=0.55, inset=0.6, w=max(0.28, min(rx, ry) * 0.16))


def rod(doc, pts, color, w=1.1, smooth_=True):
    d = cr_path(pts, False) if (smooth_ and len(pts) > 2) else poly_d(pts)
    path(doc, d, stroke=tone(color, 0.38), w=w + 0.38)
    path(doc, d, stroke=color, w=w)
    path(doc, d, stroke=lighten(color, 0.5), w=w * 0.3, op=0.7, extra='transform="translate(-0.1 -0.16)"')


def coil(doc, pts, color, amp=0.55, lam=1.7, w=0.75, phase=0.0, ramp=None):
    """Alpha helix drawn as a sine ribbon along a polyline; ramp(t) scales the amplitude (0..1 along the path)."""
    dense = resample(cr_sample(pts, closed=False, per=12) if len(pts) > 2 else pts, 0.2, closed=False)
    nm = normals(dense, closed=False)
    L = poly_len(dense) or 1
    out, s = [], 0.0
    for i, (p, n) in enumerate(zip(dense, nm)):
        if i:
            s += math.hypot(p[0] - dense[i - 1][0], p[1] - dense[i - 1][1])
        a = amp * (ramp(s / L) if ramp else 1) * math.sin(2 * math.pi * s / lam + phase)
        out.append((p[0] + n[0] * a, p[1] + n[1] * a))
    d = poly_d(out)
    path(doc, d, stroke=tone(color, 0.38), w=w + 0.34)
    path(doc, d, stroke=color, w=w)
    path(doc, poly_d([(x - 0.07, y - 0.14) for x, y in out]), stroke=lighten(color, 0.55), w=w * 0.28, op=0.75)


def gtp(doc, x, y, r=0.8):
    circ(doc, x, y, r, fill='#F4C542', stroke='#8A6A10', w=0.2)


# ===================================================================== membranes that change scale
def band(doc, pts, ws, color, closed=False, core=None, bead=None, shadow=0.0, core_k=0.31, bead_step=3):
    """A bilayer of varying thickness along pts (dense, ~0.35 mm spacing): leaflet band, light hydrophobic core and,
    where it is thick, a row of head-group beads on each face.  color/core may be gradients; bead(p) -> colour."""
    nm = normals(pts, closed)

    ss = [smooth((w - 3.0) / (WM - 3.0)) for w in ws]

    def ring(k):
        ks = [k if k == 1.0 else k + (0.6 - k) * q for q in ss]      # thick parts: wider pale tail region
        lf = [(p[0] + n[0] * w * kk / 2, p[1] + n[1] * w * kk / 2) for p, n, w, kk in zip(pts, nm, ws, ks)]
        rt = [(p[0] - n[0] * w * kk / 2, p[1] - n[1] * w * kk / 2) for p, n, w, kk in zip(pts, nm, ws, ks)]
        if closed:
            return poly_d(lf, True) + ' ' + poly_d(rt, True)
        return poly_d(lf + rt[::-1], True)
    d = ring(1.0)
    if shadow:
        doc.add('<path d="%s" fill="%s" fill-rule="evenodd" opacity="%s" transform="translate(0.45 0.75)"/>' % (d, SHADOW, fmt(shadow)))
    doc.add('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, color))
    doc.add('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (ring(core_k), core or lighten(color, 0.82)))
    if bead is None:
        return
    out = []
    for i in range(0, len(pts), bead_step):
        p, n, w = pts[i], nm[i], ws[i]
        s = ss[i]
        if s < 0.08:
            continue
        for sg in (1, -1):
            off = sg * (w / 2 - 0.75)
            out.append('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="%s"/>' % (
                fmt(p[0] + n[0] * off), fmt(p[1] + n[1] * off), fmt(0.62 * (0.6 + 0.4 * s)), bead(p), fmt(0.95 * s)))
    doc.add(''.join(out))


def _arc_pts(cx, cy, r, a0, a1, step=0.35):
    n = max(8, int(abs(math.radians(a1 - a0)) * r / step))
    return [pol(cx, cy, r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def lyso_lumen(doc):
    return doc.radgrad([(0, '#F8F1FD'), (0.55, LY_FILL), (1, '#C6A2E6')], cx=0.38, cy=0.32, r=0.78)


def lysosome(doc, x, y, r, toward, half=62, seed=1, n_enz=3, n_h=3):
    """Organelle-scale lysosome whose membrane swells to molecular scale on the side facing angle `toward`."""
    contact_shadow(doc, x, y, r, strength=0.12)
    circ(doc, x, y, r, fill=lyso_lumen(doc))
    rnd = random.Random(seed)
    k = 0
    while k < n_enz + n_h:
        a = rnd.uniform(0, 360)
        if abs(((a - toward) + 180) % 360 - 180) < 70:
            continue
        rr = rnd.uniform(2.0, r - 4.2)
        px, py = pol(x, y, rr, a)
        if k < n_enz:
            enzyme_dot(doc, px, py, 1.45, HYD)
        else:
            hplus(doc, px, py, 0.72)
        k += 1
    pts = _arc_pts(x, y, r, toward - 180, toward + 180)[:-1]
    n = len(pts)
    ws = [W_LY + (WM - W_LY) * bump(360 * i / n - 180, half) for i in range(n)]
    band(doc, pts, ws, LY_C, closed=True, core=lighten(LY_C, 0.8), bead=lambda p: lighten(LY_C, 0.55), shadow=0.08)
    spec(doc, x, y, r, a0=198, a1=244, op=0.65, inset=0.8, w=0.55)


def lyso_v(L, rl, deg):
    """Distance (from LATE's membrane mid-plane, along the ray from LATE's centre at angle deg) to the near
    mid-plane of a lysosome centred at L with radius rl."""
    d = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
    ox, oy = L[0] - CX, L[1] - CY
    b = d[0] * ox + d[1] * oy
    c = ox * ox + oy * oy - rl * rl
    disc = b * b - c
    return b - math.sqrt(max(disc, 0.0)) - CR


class Frame:
    """Local contact frame on LATE at angle th: u along the membrane (clockwise), v outward from the mid-plane."""

    def __init__(self, th):
        self.th = th

    def ang(self, u):
        return self.th + math.degrees(u / CR)

    def __call__(self, u, v):
        return pol(CX, CY, CR + v, self.ang(u))

    def rot(self, u=0):
        return self.ang(u) + 90


# ===================================================================== 4  fusion stations
TH_A, TH_B, TH_C, TH_D = -96.0, -62.0, -31.0, 8.0
RL = 14.0
GAP_A, GAP_B = 28.0, 15.0                     # membrane mid-plane separations (tether, zipper)
L_A = pol(CX, CY, CR + GAP_A + RL, TH_A)
L_B = pol(CX, CY, CR + GAP_B + RL, TH_B)
D_C = CR + RL - 3.5
L_C = pol(CX, CY, D_C, TH_C)
C_ALPHA = math.degrees(math.acos((CR * CR + D_C * D_C - RL * RL) / (2 * CR * D_C)))   # pore half-angle on LATE
G1 = 6.0                                      # the neck fillets leave LATE's circle G1 deg before the intersection


def late_w(phi):
    """Thickness of LATE's membrane at angle phi: molecular across the docking arc, organelle scale elsewhere."""
    b = max(bump(phi - TH_A, 27), bump(phi - TH_B, 27), bump(phi - TH_D, 25),
            bump(phi - (TH_C - C_ALPHA), 22, flat=0.3), bump(phi - (TH_C + C_ALPHA), 22, flat=0.3))
    return W_LATE + (WM - W_LATE) * b


def late_membrane(doc):
    """Over-draw LATE's docking arc in one piece (no seams), open at the fusion pore of station c."""
    for a0, a1 in ((TH_A - 44, TH_C - C_ALPHA - G1), (TH_C + C_ALPHA + G1, TH_D + 36)):
        pts = _arc_pts(CX, CY, CR, a0, a1)
        n = len(pts) - 1
        ws = [late_w(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
        band(doc, pts, ws, LE_C, core=lighten(LE_C, 0.82), bead=lambda p: lighten(LE_C, 0.5), core_k=CORE_LATE / W_LATE)
S0 = WM / 2                                   # cytosolic face of LATE's bilayer (v)


def hops(doc, pts, n=7, cradle=None, r0=2.2):
    dense = cr_sample(pts, closed=False, per=10)
    path(doc, cr_path(pts, False), stroke=tone(HOPS, 0.35), w=r0 * 1.7, op=0.28)
    for k in range(n):
        t = (k + 0.5) / n
        x, y, ang = pt_on(dense, t)
        r = r0 + 0.35 * math.sin(math.pi * t)
        col = lighten(HOPS, 0.32) if (cradle is not None and k == cradle) else HOPS
        glob(doc, x, y, r * 1.12, r * 0.88, col, rot=ang, light=0.48)


def snare_up(doc, F, u, c, top, phase=0.0, habc=False):
    """Unpaired Q-SNARE on LATE: TMD in the bilayer, SNARE motif standing into the cytosol."""
    rod(doc, [F(u, -S0 - 0.4), F(u, S0 + 0.4)], c, w=1.25, smooth_=False)
    coil(doc, [F(u, S0), F(u + 0.4, S0 + top * 0.5), F(u - 0.3, S0 + top)], c, amp=0.5, lam=1.9, w=0.88, phase=phase)
    if habc:
        p = F(u - 2.6, S0 + top + 0.6)
        glob(doc, p[0], p[1], 1.8, 2.6, c, rot=F.rot(u) - 70, sp=False)


def station_a(doc):
    """a  tether: Rab7-GTP (LATE) and Arl8b-GTP (lysosome) are bridged by the HOPS complex; SNAREs still apart."""
    F = Frame(TH_A)
    lysosome(doc, L_A[0], L_A[1], RL, TH_A + 180, seed=3, n_enz=4, n_h=4)

    def ls(u):                       # lysosome cytosolic surface (v)
        return lyso_v(L_A, RL, F.ang(u)) - WM / 2
    # unpaired SNAREs waiting: Qa (closed, Habc folded back), Qb, Qc on LATE; VAMP7 (longin) on the lysosome
    for k, (u, c) in enumerate(((6.6, QA), (8.8, QB), (11.0, QC))):
        snare_up(doc, F, u, c, 9.0, phase=k, habc=(k == 0))
    u = 5.2
    rod(doc, [F(u, ls(u) + WM * 0.85), F(u, ls(u) - 0.3)], RS, w=1.25, smooth_=False)
    coil(doc, [F(u, ls(u)), F(u + 0.4, ls(u) - 4.2), F(u - 0.1, ls(u) - 7.6)], RS, amp=0.5, lam=1.9, w=0.88)
    p = F(u + 0.2, ls(u) - 9.6)
    glob(doc, p[0], p[1], 2.2, 1.9, RS, sp=False)                                # longin domain
    # Rab7-GTP on LATE, Arl8b-GTP on the lysosome, bridged by HOPS (an elongated, arched hexamer)
    ur, ua = -8.0, 0.2
    rod(doc, [F(ur, S0 - 0.8), F(ur + 0.3, S0 + 2.2)], tone(RAB7, 0.1), w=0.7)
    pr = F(ur + 0.4, S0 + 5.2)
    glob(doc, pr[0], pr[1], 3.4, 3.0, RAB7, rot=F.rot(ur))
    gtp(doc, *F(ur - 1.8, S0 + 6.2), r=1.1)
    va = ls(ua)
    rod(doc, [F(ua, va + 0.8), F(ua - 0.2, va - 2.2)], tone(ARL8, 0.1), w=0.7)
    pa = F(ua - 0.3, va - 5.0)
    glob(doc, pa[0], pa[1], 3.3, 2.9, ARL8, rot=F.rot(ua))
    gtp(doc, *F(ua + 2.0, va - 6.0), r=1.1)
    hops(doc, [F(ur + 0.8, S0 + 8.6), F(ur + 1.2, S0 + 12.6), F(-4.6, (S0 + va) / 2 + 2.4), F(ua - 3.0, va - 8.4)],
         n=5, r0=1.85)
    return F


def station_b(doc):
    """b  zipper: HOPS still holds the membranes; trans-SNAREs zipper from the N-termini toward the membranes."""
    F = Frame(TH_B)
    lysosome(doc, L_B[0], L_B[1], RL, TH_B + 180, seed=8, n_enz=4, n_h=4)

    def ls(u):
        return lyso_v(L_B, RL, F.ang(u)) - WM / 2
    vm = (S0 + ls(0)) / 2                          # middle of the gap
    # HOPS (still bound, now cradling the bundle: its SM subunit Vps33 lighter) on the left
    ur, ua = -11.0, -7.2
    rod(doc, [F(ur, S0 - 0.8), F(ur, S0 + 1.6)], tone(RAB7, 0.1), w=0.7)
    p = F(ur, S0 + 3.6)
    glob(doc, p[0], p[1], 2.7, 2.3, RAB7, rot=F.rot(ur))
    rod(doc, [F(ua, ls(ua) + 0.8), F(ua, ls(ua) - 1.6)], tone(ARL8, 0.1), w=0.7)
    p = F(ua, ls(ua) - 3.6)
    glob(doc, p[0], p[1], 2.6, 2.2, ARL8, rot=F.rot(ua))
    hops(doc, [F(ur - 1.2, S0 + 6.0), F(ur - 2.6, vm + 0.6), F(ua - 3.4, ls(ua) - 6.0)], n=4, r0=1.8)
    p = F(-6.6, vm)
    glob(doc, p[0], p[1], 2.4, 2.0, lighten(HOPS, 0.34), rot=F.rot(-6.6), light=0.45)    # Vps33 templates the bundle
    # four-helix bundle: N-terminal half zipped (left), C-terminal ends still splayed toward their membranes
    offs = (-1.5, -0.5, 0.5, 1.5)
    cols = (QA, QB, QC, RS)
    u0, uz = -4.4, 2.4
    ends = [(6.0, S0), (7.6, S0), (9.2, S0), (7.4, ls(7.4))]
    for i, (o, c, e) in enumerate(zip(offs, cols, ends)):
        pz = [F(u0, vm + o), F(uz, vm + o), F((uz + e[0]) / 2 + 0.8, (vm + o + e[1]) / 2), F(*e)]
        b = (uz - u0) / (poly_len(pz) or 1)
        coil(doc, pz, c, amp=0.62, lam=2.0, w=0.92, phase=i * math.pi / 2,
             ramp=lambda t, b=b: 1.0 if t < b else max(0.35, 1 - (t - b) * 2.2))
    for i, e in enumerate(ends):
        if i < 3:
            rod(doc, [F(e[0], -S0 - 0.4), F(e[0], S0 + 0.2)], cols[i], w=1.15, smooth_=False)
        else:
            rod(doc, [F(e[0], e[1] - 0.2), F(e[0], e[1] + WM + 0.4)], cols[i], w=1.15, smooth_=False)
    return F, vm


def station_c(doc):
    """c  pore: the bilayers have merged, the fusion pore is open and lysosomal contents pour into LATE."""
    F = Frame(TH_C)
    x, y = L_C
    alpha = C_ALPHA
    toC = math.degrees(math.atan2(CY - y, CX - x))
    beta = math.degrees(math.acos((RL * RL + D_C * D_C - CR * CR) / (2 * RL * D_C)))
    g1, g2 = G1, 26.0                              # gaps (deg) left open so the spline forms the neck fillets
    arc1 = _arc_pts(CX, CY, CR, TH_C - alpha - g1 - 9, TH_C - alpha - g1, 1.2)
    lys = _arc_pts(x, y, RL, toC + beta + g2, toC + 360 - beta - g2, 1.2)
    arc2 = _arc_pts(CX, CY, CR, TH_C + alpha + g1, TH_C + alpha + g1 + 9, 1.2)
    contour = resample(cr_sample(arc1 + lys + arc2, closed=False, per=8), 0.35, closed=False)
    # lumen: lysosome + the neck, opaque where LATE's old membrane was, fading into LATE's lumen
    inner = _arc_pts(CX, CY, CR - 8, TH_C + alpha + 12, TH_C - alpha - 12, 1.0)
    neck = resample(cr_sample(arc1[-2:] + lys + arc2[:2], closed=False, per=8), 0.5, closed=False)
    jc = pol(CX, CY, CR - 1, TH_C)
    fade = _ug(doc, 'radial', [(0, mix(LY_FILL, '#F4CFC8', 0.35), 1), (0.45, mix(LY_FILL, '#F4CFC8', 0.6), 1),
                               (0.62, '#F3CCC4', 0.9), (1, '#F3CCC4', 0)], cx=jc[0], cy=jc[1], r=15)
    contact_shadow(doc, x, y, RL, strength=0.1)
    circ(doc, x, y, RL, fill=lyso_lumen(doc))
    path(doc, poly_d(neck + inner, True), fill=fade)
    # contents streaming through the pore, plus a soft violet stream
    s1 = [F(0, 20), F(0.6, 8), F(-0.4, -2), F(0.4, -11)]
    path(doc, cr_path(s1, False), stroke=LY_C, w=5.5, op=0.08)
    arrow(doc, [F(1.8, 15.5), F(2.2, 5.0), F(1.6, -6.5)], mix(LY_C, HYD, 0.3), 'transport', w=0.7, head=2.6, bow=0,
          opacity=0.75)
    for (u, v, k) in ((-2.4, 21.0, 'e'), (-4.8, 14.0, 'h'), (-1.6, 8.6, 'e'), (-3.0, 2.2, 'h'), (-0.8, -4.0, 'e'),
                      (-3.6, -8.6, 'h'), (3.6, 22.0, 'h'), (5.0, 17.0, 'e'), (4.4, -9.2, 'h'), (0.6, -13.0, 'e')):
        p = F(u, v)
        if k == 'e':
            enzyme_dot(doc, p[0], p[1], 1.7, HYD)
        else:
            hplus(doc, p[0], p[1], 0.82)
    # merged bilayer: thick at the neck, tapering back to each organelle's own scale; red -> violet across it
    n_c = pol(0, 0, 1, TH_C)
    ga = dict(x1=CX + n_c[0] * (CR - 2), y1=CY + n_c[1] * (CR - 2), x2=CX + n_c[0] * (CR + 12), y2=CY + n_c[1] * (CR + 12))
    gcol = _ug(doc, 'linear', [(0, LE_C, 1), (0.4, mix(LE_C, LY_C, 0.5), 1), (1, LY_C, 1)], **ga)
    gcore = _ug(doc, 'linear', [(0, lighten(LE_C, 0.82), 1), (1, lighten(LY_C, 0.8), 1)], **ga)
    j1 = pol(CX, CY, CR, TH_C - alpha)
    j2 = pol(CX, CY, CR, TH_C + alpha)
    ws = []
    for p in contour:
        dj = min(math.hypot(p[0] - j1[0], p[1] - j1[1]), math.hypot(p[0] - j2[0], p[1] - j2[1]))
        rr = math.hypot(p[0] - CX, p[1] - CY)
        if rr < CR + 0.3:
            ws.append(late_w(math.degrees(math.atan2(p[1] - CY, p[0] - CX))))
            continue
        base = W_LY + (W_LATE - W_LY) * max(0.0, 1 - (rr - CR - 1.5) / 6)
        ws.append(base + (WM - base) * bump(dj, 17, flat=0.3))

    def bead(p):
        t = ((p[0] - CX) * n_c[0] + (p[1] - CY) * n_c[1] - CR + 2) / 14
        return lighten(mix(LE_C, LY_C, max(0, min(1, t))), 0.52)
    band(doc, contour, ws, gcol, core=gcore, bead=bead, core_k=0.31)
    spec(doc, x, y, RL, a0=200, a1=246, op=0.6, inset=0.8, w=0.6)
    return F


def station_d(doc):
    """d  recycle: after fusion the cis-SNARE complex sits in one membrane; NSF + alpha-SNAP pull it apart (ATP)."""
    F = Frame(TH_D)
    offs = (-1.4, -0.47, 0.47, 1.4)
    cols = (QA, QB, QC, RS)
    vb = S0 + 2.6
    for i, (o, c) in enumerate(zip(offs, cols)):                # cis bundle lying on the membrane
        coil(doc, [F(-7.0, vb + o * 0.8), F(4.2, vb + o * 0.8), F(6.4 + 0.7 * i, S0)], c, amp=0.55, lam=1.9, w=0.85,
             phase=i * math.pi / 2)
    for i in range(4):
        rod(doc, [F(6.4 + 0.7 * i, -S0 - 0.4), F(6.4 + 0.7 * i, S0 + 0.2)], cols[i], w=0.95, smooth_=False)
    for k in range(3):                                          # alpha-SNAPs coating the bundle
        u = -5.2 + k * 4.2
        p = F(u, vb + 4.6)
        glob(doc, p[0], p[1], 1.6, 3.0, '#A3AAB8', rot=F.rot(u) + 90, sp=False)
    for row, (vv, rr) in enumerate(((vb + 10.4, 2.45), (vb + 15.2, 2.55))):  # NSF hexamer: D1 and D2 rings
        for k in (-1, 0, 1):
            u = -1.0 + k * 4.9
            p = F(u, vv)
            glob(doc, p[0], p[1], rr, rr * 0.92, NSF if row == 0 else tone(NSF, -0.18), light=0.45)
    u = 13.0                                                    # a freed SNARE, ready for reuse
    snare_up(doc, F, u, QB, 8.0, phase=1.0)
    return F, vb


def arriving(doc):
    """Two lysosomes still on their way down the enzyme route toward the docking arc."""
    trail = [(640, 562), (612, 580), (586, 592), (558, 579), (534, 584), (521, 593)]
    path(doc, cr_path(trail, False), stroke=LY_C, w=1.3, op=0.32, dash='0.1 3.2')
    for (x, y, r, sd) in ((588, 592, 7.5, 21), (557, 578, 8.5, 22)):
        contact_shadow(doc, x, y, r, strength=0.12)
        circ(doc, x, y, r, fill=lyso_lumen(doc), stroke=LY_C, w=W_LY)
        circ(doc, x, y, r, fill='none', stroke=lighten(LY_C, 0.8), w=0.65)
        rnd = random.Random(sd)
        for k in range(4):
            px, py = pol(x, y, rnd.uniform(1.0, r - 3.4), rnd.uniform(0, 360))
            if k < 2:
                enzyme_dot(doc, px, py, 1.35, HYD)
            else:
                hplus(doc, px, py, 0.65)
        spec(doc, x, y, r, a0=198, a1=244, op=0.65, inset=0.78, w=0.5)


def fusion(doc):
    arriving(doc)
    late_membrane(doc)
    station_a(doc)
    station_b(doc)
    station_c(doc)
    Fd, vb = station_d(doc)
    # ---------------------------------------------------------------- labels
    lab(doc, 455.0, 612.0, 'Arl8b', ARL8, anchor='end')
    lab(doc, 451.0, 625.5, 'HOPS', HOPS, anchor='end')
    lab(doc, 448.5, 637.0, 'Rab7', RAB7, anchor='end')
    step(doc, L_A[0] - 11.0, L_A[1] - RL - 5.0, 'a', 'tether')
    step(doc, L_B[0] - 7.0, L_B[1] - RL - 5.0, 'b', 'zipper')
    xs, ys = L_B[0] + RL + 5.0, L_B[1] - 13.5       # SNARE names stacked beside the bundle, each in its own colour
    for k, (s, c) in enumerate((('syntaxin-7', QA), ('Vti1b', QB), ('syntaxin-8', QC), ('VAMP7', RS))):
        lab(doc, xs, ys + k * 5.5, s, c, size=4.4)
    lab(doc, xs, ys + 4 * 5.5 + 0.8, 'N → C', '#5E5648', size=4.4)
    step(doc, L_C[0] + RL + 3.5, L_C[1] - 1.0, 'c', 'pore')
    p = Fd(-1.0, vb + 15.2)
    lab(doc, p[0] + 5.2, p[1] - 3.5, 'NSF', NSF)
    p = Fd(9.5, vb + 5.0)
    lab(doc, p[0] + 5.0, p[1] + 5.0, 'α-SNAP', tone(NSF, 0.15), size=4.4)
    step(doc, p[0] + 5.0, p[1] + 11.0, 'd', 'recycle')


# ===================================================================== 2.6 the phagolysosome
def pl_pt(phi, v=0.0):
    return pol(PLX, PLY, PLR + v, phi)


PHI_V, PHI_N, PHI_E = -40.0, 12.0, 64.0          # V-ATPase, NOX2, product exporter sites on the rim
KS = 1.3                                         # enlargement of the two rim machines


def pl_body(doc):
    aura = doc.radgrad([(0, '#A060C8', 0.0), (0.62, '#A060C8', 0.0), (0.74, '#9C5CC6', 0.16), (1, '#9C5CC6', 0)])
    circ(doc, PLX, PLY, PLR * 1.42, fill=aura)
    contact_shadow(doc, PLX, PLY, PLR, strength=0.14, spread=1.06)
    lum = doc.radgrad([(0, '#FFF4F8'), (0.32, '#FADCEA'), (0.7, '#EDC0E2'), (0.92, '#D9A6DD'), (1, '#C894D8')],
                      cx=0.43, cy=0.4, r=0.62, fx=0.38, fy=0.33)
    circ(doc, PLX, PLY, PLR, fill=lum)
    glow = doc.radgrad([(0, '#FF7FB0', 0.24), (0.5, '#FF8FBF', 0.12), (1, '#FF8FBF', 0)])
    circ(doc, PLX - 4, PLY - 2, PLR * 0.72, fill=glow)
    rim = doc.lingrad([(0, '#7B3FA8', 0), (0.55, '#7B3FA8', 0), (1, '#7B3FA8', 0.22)], 0, 0, 1, 1)
    circ(doc, PLX, PLY, PLR - 5.5, fill='none', stroke=rim, w=9)


def pl_membrane(doc):
    pts = _arc_pts(PLX, PLY, PLR, -180, 180, 0.35)[:-1]
    n = len(pts)
    ws = []
    for i in range(n):
        a = -180 + 360 * i / n
        b = max(bump(((a - PHI_V) + 180) % 360 - 180, 17), bump(((a - PHI_N) + 180) % 360 - 180, 18),
                bump(((a - PHI_E) + 180) % 360 - 180, 9))
        ws.append(W_PL + (WM - W_PL) * b)
    band(doc, pts, ws, LY_C, closed=True, core=lighten(LY_C, 0.8), bead=lambda p: lighten(LY_C, 0.55), shadow=0.1)
    spec(doc, PLX, PLY, PLR, a0=196, a1=236, op=0.7, inset=0.93, w=1.0)


# ----------------------------------------------------------------- lumen contents
def broken_bacterium(doc, x, y, L, W, rot):
    """The bacterium snapping in two: the halves drift apart, envelope torn, debris spilling between them."""
    r = W / 2
    jag = [(1.0, -r - 1), (-1.6, -r * 0.5), (1.8, -r * 0.15), (-1.2, r * 0.2), (1.6, r * 0.55), (-0.4, r + 1)]
    for side, (dx, dr, op) in ((-1, (-4.2, -10, 1.0)), (1, (4.6, 13, 0.85))):
        cid = doc.uid('bk')
        poly = ([(-L, -r - 1)] if side < 0 else [(L, -r - 1)]) + jag + ([(-L, r + 1)] if side < 0 else [(L, r + 1)])
        doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, poly_d(poly, True)))
        doc.add('<g transform="translate(%s %s) rotate(%s) translate(%s 0) rotate(%s)" opacity="%s"><g clip-path="url(#%s)">' % (
            fmt(x), fmt(y), fmt(rot), fmt(dx), fmt(dr), fmt(op), cid))
        bacterium(doc, 0, 0, L=L, W=W, rot=0, lps=side < 0, flagella=False, seed=21 + side)
        rnd = random.Random(40 + side)
        for _ in range(4 if side < 0 else 7):                  # pale, digested patches
            u = side * rnd.uniform(3, L * 0.42)
            v = rnd.choice((-1, 1)) * r * rnd.uniform(0.55, 0.85)
            ell(doc, u, v, rnd.uniform(1.4, 2.8), rnd.uniform(0.8, 1.3), fill='#F7E6EE', op=0.85)
        lip = [(p[0] + side * 0.7, max(-r + 0.8, min(r - 0.8, p[1]))) for p in jag]
        path(doc, cr_path(lip, False), stroke='#4E5A16', w=0.8)                   # torn envelope edge
        path(doc, cr_path([(p[0] + side * 1.8, p[1]) for p in lip], False), stroke='#E8EFC0', w=0.6, op=0.8)
        doc.add('</g></g>')
    rnd = random.Random(7)                                     # debris between and around the halves
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    for k in range(20):
        u, v = rnd.uniform(-7, 8), rnd.uniform(-r * 1.6, r * 1.6)
        px, py = x + u * ca - v * sa, y + u * sa + v * ca
        if k < 8:
            r0 = rnd.uniform(1.0, 2.0)
            a0 = rnd.uniform(0, 360)
            p1, p2 = pol(px, py, r0, a0), pol(px, py, r0, a0 + 100)
            path(doc, 'M%s,%s A%s,%s 0 0 1 %s,%s' % (fmt(p1[0]), fmt(p1[1]), fmt(r0), fmt(r0), fmt(p2[0]), fmt(p2[1])),
                 stroke='#6A781E', w=0.65, op=0.85)
        else:
            circ(doc, px, py, rnd.uniform(0.35, 0.75), fill='#8C9A3A', op=0.8)
    path(doc, cr_path([(x - 3 * ca, y - 3 * sa - 1.2), (x + 0.6, y + 1.2), (x + 3 * ca + 1, y + 3 * sa - 0.4)], False),
         stroke='#6B5A98', w=0.6, op=0.85)


def pg_fragment(doc, x, y, s=1.0):
    """Peptidoglycan: glycan strands (beads) cross-linked by short peptides."""
    for j in range(3):
        yy = y + j * 3.0 * s
        pts = [(x - 5.5 * s + k * 2.2 * s + (j % 2) * 1.1 * s, yy + (0.3 if k % 2 else -0.3) * s) for k in range(5)]
        path(doc, poly_d(pts), stroke=tone(BACT, 0.35), w=0.5)
        for (px, py) in pts:
            circ(doc, px, py, 0.72 * s, fill=lighten(BACT, 0.15), stroke=tone(BACT, 0.4), w=0.18)
        if j < 2:
            for (px, py) in pts[::2]:
                line(doc, px, py + 0.7 * s, px + 0.5 * s, py + 2.3 * s, tone(BACT, 0.2), 0.32)


def protein_chain(doc, xa, ya, xb, yb, cut=5):
    pts = [(xa + (xb - xa) * k / 9, ya + (yb - ya) * k / 9 + (1.0 if k % 2 else -1.0)) for k in range(10)]
    path(doc, cr_path(pts[:cut], False), stroke=tone(BACT, 0.3), w=0.45)
    path(doc, cr_path(pts[cut:], False), stroke=tone(BACT, 0.3), w=0.45)
    for (px, py) in pts:
        circ(doc, px, py, 0.82, fill=lighten(BACT, 0.05), stroke=tone(BACT, 0.4), w=0.18)


def lipid_flake(doc, x, y, n=5):
    for k in range(n):
        px = x - n + k * 1.9
        for sg in (-1, 1):
            line(doc, px, y + sg * 0.5, px, y + sg * 2.1, tone(BACT, 0.25), 0.3)
            circ(doc, px, y + sg * 2.5, 0.72, fill=lighten(BACT, 0.1), stroke=tone(BACT, 0.4), w=0.18)


def dna(doc, xa, ya, xb, yb):
    """A DNA duplex cut in two."""
    for ph in (0, math.pi):
        for t0, t1 in ((0.0, 0.44), (0.56, 1.0)):
            pts = []
            for k in range(16):
                t = t0 + (t1 - t0) * k / 15
                pts.append((xa + (xb - xa) * t, ya + (yb - ya) * t + 1.2 * math.sin(t * 2 * math.pi * 2.2 + ph)))
            path(doc, poly_d(pts), stroke='#6B5A98', w=0.55)
    for k in range(9):
        t = (k + 0.5) / 9
        if abs(t - 0.5) < 0.08:
            continue
        x0, y0 = xa + (xb - xa) * t, ya + (yb - ya) * t
        s = 1.0 * math.sin(t * 2 * math.pi * 2.2)
        line(doc, x0, y0 - s, x0, y0 + s, '#9A8CC4', 0.3, op=0.8)


def product(doc, x, y, k):
    c = tone(RECY, 0.05)
    if k % 3 == 0:
        circ(doc, x, y, 0.9, fill=lighten(c, 0.25), stroke=tone(c, 0.35), w=0.2)
    elif k % 3 == 1:
        pts = [(x + 1.0 * math.cos(math.pi / 3 * i), y + 1.0 * math.sin(math.pi / 3 * i)) for i in range(6)]
        path(doc, poly_d(pts, True), fill=lighten(c, 0.4), stroke=tone(c, 0.35), w=0.2)
    else:
        path(doc, poly_d([(x, y - 1.1), (x + 1.0, y), (x, y + 1.1), (x - 1.0, y)], True), fill=lighten(c, 0.1),
             stroke=tone(c, 0.35), w=0.2)


def whorl(doc, x, y, r):
    """Membrane whorl (myelin figure): bacterial lipids rolling up as they are digested."""
    for k, rr in enumerate((r, r * 0.68, r * 0.38)):
        a0 = 40 + 70 * k
        p1, p2 = pol(x, y, rr, a0), pol(x, y, rr, a0 + 290)
        d = 'M%s,%s A%s,%s 0 1 1 %s,%s' % (fmt(p1[0]), fmt(p1[1]), fmt(rr), fmt(rr), fmt(p2[0]), fmt(p2[1]))
        path(doc, d, stroke=tone(BACT, 0.3), w=1.25, op=0.8)
        path(doc, d, stroke=lighten(BACT, 0.6), w=0.45, op=0.9)


def shard(doc, x, y, a):
    """A torn fragment of the bacterial envelope (outer membrane with its LPS fringe)."""
    p = [pol(x, y, 0, 0)]
    pts = [(x + 3.4 * math.cos(math.radians(a + t)) - 3.4 * math.cos(math.radians(a)),
            y + 3.4 * math.sin(math.radians(a + t)) - 3.4 * math.sin(math.radians(a))) for t in range(-40, 41, 10)]
    path(doc, poly_d(pts), stroke='#4E5A16', w=0.95, op=0.85)
    path(doc, poly_d(pts), stroke='#D6DE98', w=0.35, op=0.9)
    nm = normals(pts, closed=False)
    for q, n in list(zip(pts, nm))[::2]:
        line(doc, q[0], q[1], q[0] - n[0] * 1.3, q[1] - n[1] * 1.3, '#66741E', 0.3, op=0.8)


def peptide(doc, x, y, a, n=3):
    for k in range(n):
        px, py = pol(x, y, k * 1.5, a + (12 if k % 2 else -12))
        circ(doc, px, py, 0.72, fill=lighten(BACT, 0.05), stroke=tone(BACT, 0.4), w=0.18)


def ros_faint(doc, x, y, s=0.8, op=0.5):
    doc.add('<g opacity="%s">' % fmt(op))
    ros(doc, x, y, s=s, rot=x * 7 % 36)
    doc.add('</g>')


LH = mix('#FADCEA', '#FFFFFF', 0.35)          # label halo on the glowing lumen


def pl_contents(doc):
    X, Y = PLX, PLY
    broken_bacterium(doc, X - 4, Y + 4, 52, 21, -22)
    pg_fragment(doc, X - 30, Y - 36, 1.15)                 # lysozyme on peptidoglycan (upper left)
    hydrolase(doc, X - 19.5, Y - 30.0, s=0.74, rot=200)
    lab(doc, X - 49, Y - 21, 'lysozyme', HYD, size=4.4, halo=LH)
    protein_chain(doc, X + 6, Y - 42, X + 30, Y - 34)      # cathepsins on a protein chain (upper right)
    hydrolase(doc, X + 17.5, Y - 46.0, s=0.74, rot=-70)
    hydrolase(doc, X + 35, Y - 28.5, s=0.66, rot=150)
    lab(doc, X - 8, Y - 51, 'cathepsins', HYD, size=4.4, halo=LH)
    lipid_flake(doc, X + 18, Y + 38, n=6)                  # lipases on a lipid flake (lower right)
    hydrolase(doc, X + 30, Y + 31.5, s=0.72, rot=210)
    lab(doc, X + 6, Y + 51, 'lipases', HYD, size=4.4, halo=LH)
    dna(doc, X - 34, Y + 30, X - 8, Y + 36)                # nucleases on DNA (lower left)
    hydrolase(doc, X - 21, Y + 42.5, s=0.72, rot=-100)
    lab(doc, X - 36, Y + 52, 'nucleases', HYD, size=4.4, halo=LH)
    whorl(doc, X - 49, Y + 4, 5.6)                         # lipid whorl from the digested envelope
    whorl(doc, X + 27, Y - 17, 3.6)
    for (dx, dy, a) in ((-22, -18, 30), (-46, 26, 200), (8, 34, -20), (36, 2, 70), (-8, -40, 160)):
        shard(doc, X + dx, Y + dy, a)
    for (dx, dy, a) in ((-10, -26, 20), (4, 46, -30), (-52, -14, 80), (44, 30, 10)):
        peptide(doc, X + dx, Y + dy, a)
    for (dx, dy, r) in ((-50, -4, 200), (-8, 48, 30), (42, -8, 160), (-30, -16, 90), (14, 26, 300), (-44, 34, 20),
                        (-2, -36, 250)):
        hydrolase(doc, X + dx, Y + dy, s=0.56, rot=r, glycan=True)
    rnd = random.Random(12)
    k = 0
    while k < 20:
        a, rr = rnd.uniform(0, 360), rnd.uniform(8, PLR - 6)
        px, py = pol(X, Y, rr, a)
        if math.hypot(px - (X - 4), py - (Y + 4)) < 19:
            continue
        hplus(doc, px, py, 0.78)
        k += 1
    for (dx, dy, s, op) in ((-24, -14, 0.8, 0.55), (22, 8, 0.65, 0.45), (-46, 14, 0.6, 0.4), (0, -22, 0.55, 0.35),
                            (38, 18, 0.55, 0.5)):
        ros_faint(doc, X + dx, Y + dy, s, op)              # ROS remnants from the burst
    for k_, (dx, dy) in enumerate(((16, 48), (21, 44), (12, 53), (24, 50))):
        product(doc, X + dx, Y + dy, k_)                   # products gathering at the exporter


# ----------------------------------------------------------------- molecular sites on the rim
def _glob_pt(phi, lx, ly, s=1.0):
    x0, y0 = pl_pt(phi)
    a = math.radians(phi + 90)
    return x0 + s * (lx * math.cos(a) - ly * math.sin(a)), y0 + s * (lx * math.sin(a) + ly * math.cos(a))


def _local(doc, phi, v=0.0, s=1.0):
    """Open a group whose local frame sits on the rim at angle phi: x along the membrane, -y = cytosol (outward)."""
    x, y = pl_pt(phi, v)
    doc.add('<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(phi + 90), fmt(s)))
    return phi + 90


def vatpase_big(doc, phi):
    rot = _local(doc, phi, s=KS)
    c = VATP

    def sh(col, **k):
        return shade_rot(doc, col, rot, **k)
    path(doc, 'M-4.4,-3.3 h8.8 a1.7,1.7 0 0 1 1.7,1.7 v3.2 a1.7,1.7 0 0 1 -1.7,1.7 h-8.8 a1.7,1.7 0 0 1 -1.7,-1.7 '
              'v-3.2 a1.7,1.7 0 0 1 1.7,-1.7 Z', fill=sh(lighten(c, 0.3), light=0.45, dark=0.12), stroke=tone(c, 0.42), w=0.3)
    for k in range(-2, 3):
        line(doc, k * 1.9, -2.6, k * 1.9, 2.6, tone(c, 0.25), 0.25, op=0.6)
    ell(doc, 7.4, -0.4, 1.7, 3.5, fill=sh(tone(c, 0.12), light=0.4, dark=0.16), stroke=tone(c, 0.42), w=0.3)   # a
    rod(doc, [(7.8, -3.8), (8.4, -9.6), (6.6, -15.4)], tone(c, 0.18), w=0.75)                                 # stator
    rod(doc, [(0, -3.3), (0, -8.0)], tone(c, 0.3), w=1.15, smooth_=False)                                      # rotor
    for dx, col in ((-3.7, c), (0, lighten(c, 0.25)), (3.7, c)):
        ell(doc, dx, -11.8, 2.2, 3.3, fill=sh(col, light=0.45, dark=0.16), stroke=tone(col, 0.42), w=0.3)
    ell(doc, 0, -15.9, 2.9, 1.35, fill=sh(lighten(c, 0.15), light=0.45, dark=0.16), stroke=tone(c, 0.42), w=0.3)
    arrow(doc, [(10.4, -3.8), (5.6, 1.4), (4.6, 6.6)], HPLUS, 'transport', w=0.5, head=2.0, bow=0)
    doc.add('</g>')
    for lx, ly in ((11.6, -6.4), (2.4, 9.0), (6.8, 11.2), (-1.8, 7.6), (-6.0, 11.0)):   # upright H+ (outside the turn)
        hplus(doc, *_glob_pt(phi, lx, ly, KS), 0.85)


def nox2_big(doc, phi):
    rot = _local(doc, phi, s=KS)

    def sh(col, **k):
        return shade_rot(doc, col, rot, **k)
    # gp91phox (6-TM, two hemes) + p22phox in the membrane
    path(doc, 'M-3.4,-2.6 h6.8 a2,2 0 0 1 2,2 v1.2 a2,2 0 0 1 -2,2 h-6.8 a2,2 0 0 1 -2,-2 v-1.2 a2,2 0 0 1 2,-2 Z',
         fill=sh(NOX, light=0.42, dark=0.16), stroke=tone(NOX, 0.42), w=0.32)
    ell(doc, 1.0, -7.4, 4.3, 2.8, fill=sh(tone(NOX, -0.12), light=0.45, dark=0.16), stroke=tone(NOX, 0.42), w=0.3)  # FAD/NADPH
    path(doc, 'M6.6,-3.0 h1.6 a1.4,1.4 0 0 1 1.4,1.4 v3.2 a1.4,1.4 0 0 1 -1.4,1.4 h-1.6 a1.4,1.4 0 0 1 -1.4,-1.4 v-3.2 '
              'a1.4,1.4 0 0 1 1.4,-1.4 Z', fill=sh(lighten(NOX, 0.35), light=0.4, dark=0.12), stroke=tone(NOX, 0.4), w=0.3)
    # cytosolic subunits: p47phox on p22, p67phox on the dehydrogenase, p40phox, Rac-GTP at the membrane
    ell(doc, 10.2, -7.6, 2.2, 3.3, fill=sh(tone(NOX, 0.12), light=0.45, dark=0.16), stroke=tone(NOX, 0.42), w=0.3, rot=-18)
    ell(doc, -1.6, -13.2, 3.5, 2.7, fill=sh(lighten(NOX, 0.18), light=0.45, dark=0.16), stroke=tone(NOX, 0.42), w=0.3)
    ell(doc, 4.8, -15.0, 2.2, 2.0, fill=sh(lighten(NOX, 0.4), light=0.45, dark=0.16), stroke=tone(NOX, 0.42), w=0.3)
    rod(doc, [(-9.2, -2.0), (-8.6, -6.4)], RAC, w=0.5)
    ell(doc, -8.0, -9.0, 2.5, 2.2, fill=sh(RAC, light=0.45, dark=0.16), stroke=tone(RAC, 0.42), w=0.3)
    gtp(doc, -6.6, -7.9, 0.8)
    # electron path NADPH -> FAD -> two hemes -> O2 in the lumen
    circ(doc, 1.6, -7.2, 0.95, fill='#F2D35B', stroke='#8A6A10', w=0.2)
    for hy in (-1.4, 1.4):
        doc.add('<rect x="-1.1" y="%s" width="2.2" height="1.0" rx="0.3" fill="#B3262E" stroke="#5E0F19" stroke-width="0.2"/>' % fmt(hy - 0.5))
    ep = [(1.6, -7.2), (0.3, -3.8), (-0.2, 0), (0.6, 4.2), (3.6, 7.8)]
    path(doc, cr_path(ep, False), stroke='#7A0C37', w=0.4, dash='0.9 0.7')
    ros(doc, 5.4, 9.6, s=0.62)
    ros(doc, 9.6, 13.0, s=0.5)
    doc.add('</g>')


def exporter(doc, phi):
    rot = _local(doc, phi)
    for dx in (-1.8, 1.8):
        ell(doc, dx, 0, 1.9, 3.4, fill=shade_rot(doc, lighten(RECY, 0.2), rot, light=0.45, dark=0.14),
            stroke=tone(RECY, 0.4), w=0.3)
    doc.add('</g>')


def phagolysosome(doc):
    pl_body(doc)
    pl_contents(doc)
    pl_membrane(doc)
    vatpase_big(doc, PHI_V)
    nox2_big(doc, PHI_N)
    exporter(doc, PHI_E)
    e0 = pl_pt(PHI_E, 4.0)                                  # products leave for the cytosol (green dashed)
    arrow(doc, [e0, (e0[0] + 12, e0[1] + 3), (e0[0] + 27, e0[1] + 1)], RECY, 'recycle', w=0.75, head=2.8, bow=0)
    arrow(doc, [e0, (e0[0] + 6, e0[1] + 9), (e0[0] + 15, e0[1] + 17)], RECY, 'recycle', w=0.75, head=2.8, bow=0)
    for k, (dx, dy) in enumerate(((30, -2.5), (19, 18.5), (17, 14.5))):
        product(doc, e0[0] + dx, e0[1] + dy, k)
    lab(doc, e0[0] + 30.5, e0[1] + 2.6, 'reuse', RECY, size=4.4)
    lab(doc, e0[0] + 22, e0[1] + 21.5, 'recycled', RECY, size=4.4)


def phago_labels(doc):
    import annot2
    annot2.organelle(doc, PLX - 4, PLY - PLR - 10, 'Phagolysosome', DLY, '2.6')
    p = pl_pt(PHI_V, 22)
    lab(doc, p[0] + 3.5, p[1] + 2.5, 'V-ATPase', VATP, size=4.6)
    q = pl_pt(PHI_V - 2, -17)
    lab(doc, q[0] - 8, q[1] + 1, 'H⁺', '#0A6E92', size=4.6, halo=LH)
    mx = PLX + PLR + 10
    marks.section(doc, mx, PLY - 22, '2.7', 'Killing', marks.color_of('2.7'))
    x = PLX + PLR + 25
    lab(doc, x, PLY + 2.5, 'NOX2', NOX, size=4.8, weight=700)
    lab(doc, x, PLY + 8.3, 'gp91phox · p22phox', NOX, size=4.4)
    lab(doc, x, PLY + 13.9, 'p47 · p67 · p40phox', tone(NOX, 0.1), size=4.4)
    lab(doc, x, PLY + 19.5, 'Rac-GTP', RAC, size=4.4)
    lab(doc, x, PLY + 25.6, 'NADPH → NADP⁺', '#7A0C37', size=4.4)
    q = pl_pt(PHI_N + 3, -9)
    p = _glob_pt(PHI_N, 8.0, 8.0, KS)
    lab(doc, p[0], p[1] + 1.6, 'e⁻', '#7A0C37', size=4.4, anchor='middle', halo=LH)
    lab(doc, q[0] - 6, q[1] + 13.2, 'O₂ → O₂•⁻ → H₂O₂', '#7A0C37', size=4.4, anchor='end', halo=LH)


# ===================================================================== pH gauge along the red route
def ph_gauge(doc):
    """Thin painted ribbon threading the skeleton's pH 6.5 and 5.5 tags and ending at a pH 4.5 tag."""
    import annot2
    seg1 = [(309, 667), (311, 688), (322, 707), (343, 719), (370, 724), (398, 723.5)]
    seg2 = [(422, 723.2), (446, 731), (474, 738.5), (506, 743), (536, 744.2)]
    grad = _ug(doc, 'linear', [(0, '#E8892D', 1), (0.45, '#D2452E', 1), (1, '#8E3BB0', 1)], x1=309, y1=0, x2=540, y2=0)
    for seg, (w0, w1) in ((seg1, (1.0, 1.5)), (seg2, (1.5, 2.1))):
        dense = resample(cr_sample(seg, closed=False, per=12), 0.4, closed=False)
        n = len(dense) - 1
        nm = normals(dense, closed=False)
        ws = [(w0 + (w1 - w0) * i / n) * (min(1.0, i / 6.0, (n - i) / 6.0) * 0.6 + 0.4) for i in range(n + 1)]
        lf = [(p[0] + q[0] * w / 2, p[1] + q[1] * w / 2) for p, q, w in zip(dense, nm, ws)]
        rt = [(p[0] - q[0] * w / 2, p[1] - q[1] * w / 2) for p, q, w in zip(dense, nm, ws)]
        path(doc, poly_d(dense), stroke=grad, w=w1 * 3.2, op=0.13)                # soft wash under the stroke
        path(doc, poly_d(lf + rt[::-1], True), fill=grad, op=0.9)
        path(doc, poly_d([(x - 0.1, y - 0.25) for x, y in dense]), stroke='#FFFFFF', w=0.35, op=0.45)
    for (x, y, s) in ((330, 715.5, 0.55), (452, 727.3, 0.6), (488, 735.6, 0.62), (512, 738.6, 0.66), (527, 739.6, 0.66)):
        hplus(doc, x, y, s)
    annot2.ph_tag(doc, 538.5, 747.3, 'pH 4.5', DLY)


# ===================================================================== draw
def draw(doc):
    ph_gauge(doc)
    phagolysosome(doc)
    fusion(doc)
    arrow(doc, [pol(CX, CY, CR + 6, 56), (532, 731.5), (566, 713)], CONV, 'fusion', w=1.0, head=4.4, bow=0)
    phago_labels(doc)
    marks.section(doc, 486, 567, 4, 'Fusion', marks.color_of(4))
