"""V2 section 5: particles, drawn IN the scene (no windows).

  ZONE_F  5.2  the silica phagolysosome inside the cell (a crystal tears its membrane, cathepsin B leaks out) and the
               NLRP3 cascade in the cytosol beside it: signal 1 (TLR -> NF-kB priming) + signal 2 (cathepsin B, K+
               efflux, ROS) -> NLRP3 + ASC -> caspase-1 -> IL-1b / IL-18 + GSDMD; GSDMD pores drawn at molecular
               scale IN the cell's own right membrane (RIGHT_MEM, tapering into the skeleton's bilayer).
  AIR_RIGHT    inhaled particles (5.1 uptake), "cleared", released IL-1b / IL-18 and K+, possible outcomes (dashed):
               pyroptosis? -> released crystal -> re-uptake.
  zone G  5.3  the long asbestos fibre in the open cup, its length, ROS + enzymes leaking from the cup mouth.
  wall    5.4 / 5.5  IL-1b . TNF-a (dotted) -> inflammation; TGF-b . PDGF -> fibrosis.
The wall itself (scene.wall / scene.labels) is drawn by build_poster before the cell: never here."""
import math, random
from lib import *
from style import shade, tone, lighten, darken, mix, contact_shadow, shade_rot
from bio import asbestos_fibre, silica, ros, enzyme_dot, cytokine, nlrp3, vatpase, hplus, hydrolase
import geom as G
import scene
import marks
from annot2 import tag, hand as ghand, hand_width, TAGS, DPATH, DINFL, DBIO

S = 4.6                 # molecule labels (sans)
ORG = 12.0              # Gabriola step names
INK_SOFT = '#4A4F57'
CASP = '#8E1D4E'        # caspase-1
GSDMD = '#6A5D7B'       # gasdermin D
KCH = '#5F73A3'         # K+ ions / channel
PLUM = '#8E3B8F'        # TLR (poster-wide TLR4 colour)
NFKB = '#5B4F78'
DPL = '#5A2A8C'         # silica phagolysosome name
CYTO_HALO = '#F6DCCD'
AIR = '#EEEBE2'         # paper / air tone just outside the right membrane
MEM = '#C07A66'
MEM_DK = '#A45E4D'
MEM_CORE = '#FDF0E8'
MAYBE = '#7A6470'       # 'possible' (dashed) arrows


# ===================================================================================== small helpers
def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def lab(doc, x, y, text, color=INK_SOFT, size=S, weight=600, anchor='start', italic=False, halo=CYTO_HALO):
    T(doc, x, y, text, size=size, weight=weight, fill=color, anchor=anchor, italic=italic, halo=halo)


def step_name(doc, x, y, step, name, color, size=ORG, halo='#FEF3EA', anchor='start'):
    """Step tag + name in Gabriola (like the skeleton's 2.x labels); (x, y) = baseline start (or end)."""
    tw = hand_width(name, size)
    sw = text_width(step, TAGS, 700) + 3.4 + 2.2
    x0 = x - tw - sw if anchor == 'end' else x
    tag(doc, x0, y - size * 0.24, step, PATH)
    ghand(doc, x0 + sw, y, name, color, size=size, halo=halo)
    doc.register_label('%s %s' % (step, name), x0, y, size, color, anchor='start')
    return x0, x0 + sw + tw


def arc_pts(cx, cy, r, a0, a1, step=2.0):
    n = max(2, int(abs(a1 - a0) / step))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def bilayer_run(doc, pts, w, col, core, closed=False, beads=True):
    d = poly_d(pts, closed)
    path(doc, d, stroke=col, w=w)
    path(doc, d, stroke=core, w=w * 0.42)
    if beads:
        for off in (w * 0.36, -w * 0.36):
            path(doc, poly_d(offset_poly(pts, off, closed), closed), stroke=tone(col, 0.25), w=w * 0.2,
                 dash='0.01 %s' % fmt(w * 0.26), op=0.75)


def maybe_arrow(doc, pts, col=MAYBE, w=0.7, head=3.2):
    """'Possible' arrow: dashed shaft + small solid head (dashed = may happen)."""
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    L = math.hypot(xb - xa, yb - ya)
    k = min(0.9, (head + 1.0) / L)
    hb = (xb - (xb - xa) * k, yb - (yb - ya) * k)
    path(doc, cr_path(pts[:-1] + [hb], False), stroke=col, w=w, dash='%s %s' % (fmt(w * 2.4), fmt(w * 2.0)))
    arrow(doc, [hb, pts[-1]], col, 'transport', w=w, head=head, bow=0.0)


def soft_pool(doc, cx, cy, rx, ry, color, op):
    """Very soft feathered tint pool (no edge) behind a molecular area."""
    gid = doc.uid('pp')
    doc.defs.append('<radialGradient id="%s"><stop offset="0" stop-color="%s" stop-opacity="%s"/>'
                    '<stop offset="0.55" stop-color="%s" stop-opacity="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/>'
                    '</radialGradient>' % (gid, color, fmt(op), color, fmt(op * 0.6), color))
    ell(doc, cx, cy, rx, ry, fill='url(#%s)' % gid)


# ===================================================================================== the right membrane (molecular)
MEMW = 7.2               # full molecular bilayer width along RIGHT_MEM
SKW = 2.9                # the skeleton's membrane width (taper target)
PORES = (646.0, 668.0)   # GSDMD pores (y on RIGHT_MEM)
PORE_G = 3.3             # pore half-opening (~20 nm at this local scale, ~4x the K+ channel)
K_Y = 604.0              # K+ channel
K_G = 0.9
TLR_Y = 560.0


def _mem():
    pts = resample(G.RIGHT_MEM_DENSE, 0.5, closed=False)
    nm = normals(pts, closed=False)
    if nm[len(nm) // 2][0] < 0:                    # outward (air) normal points to +x
        nm = [(-a, -b) for a, b in nm]
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    return pts, nm, L


MPTS, MNRM, MLEN = _mem()


def mem_w(s):
    tot = MLEN[-1]
    return SKW + (MEMW - SKW) * smooth(s / 16.0) * smooth((tot - s) / 14.0)


def mem_at(y):
    """(point, outward normal, tangent, width) of RIGHT_MEM at height y."""
    i = min(range(len(MPTS)), key=lambda k: abs(MPTS[k][1] - y))
    n = MNRM[i]
    return MPTS[i], n, (-n[1], n[0]), mem_w(MLEN[i])


def _gaps():
    return [(y, PORE_G) for y in PORES] + [(K_Y, K_G)]


def right_membrane(doc):
    """Over-draw RIGHT_MEM as a molecular-scale bilayer (tapering smoothly into the skeleton's line), with the pores
    and the K+ channel cut through it."""
    gaps = _gaps()

    def in_gap(p):
        return any(abs(p[1] - y) < g for y, g in gaps)

    runs, cur = [], []
    for k, p in enumerate(MPTS):
        if in_gap(p):
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        else:
            cur.append(k)
    if len(cur) > 1:
        runs.append(cur)
    # pore / channel lumens: cover the skeleton's line with a cytosol -> air blend
    for y, g in gaps:
        (px, py), n, _, w = mem_at(y)
        gid = doc.uid('pl')
        doc.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="0" x2="%s" y2="0">'
                        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
                        % (gid, fmt(px - w / 2 - 1.5), fmt(px + w / 2 + 1.5), '#EFC4AF', AIR))
        rect(doc, px - w / 2 - 1.8, y - g - 0.2, w + 3.6, 2 * g + 0.4, fill='url(#%s)' % gid)

    def side(k, f):
        w = mem_w(MLEN[k])
        return (MPTS[k][0] + MNRM[k][0] * w * f, MPTS[k][1] + MNRM[k][1] * w * f)

    for run in runs:
        path(doc, poly_d([side(k, 0.5) for k in run] + [side(k, -0.5) for k in run[::-1]], True), fill=MEM)
        path(doc, poly_d([side(k, 0.2) for k in run] + [side(k, -0.2) for k in run[::-1]], True), fill=MEM_CORE)
        tails = []
        for k in run[::3]:
            w = mem_w(MLEN[k])
            if w < 4.6:
                continue
            (x, y), (nx, ny) = MPTS[k], MNRM[k]
            for sg in (1, -1):
                a, b = 0.06 * w, 0.30 * w
                tails.append('M%s,%sL%s,%s' % (fmt(x + sg * nx * a), fmt(y + sg * ny * a), fmt(x + sg * nx * b), fmt(y + sg * ny * b)))
        if tails:
            path(doc, ''.join(tails), stroke='#D9A08E', w=0.28, op=0.9)
        for k in run:
            if k % 4:
                continue
            w = mem_w(MLEN[k])
            if w < 3.6:
                continue
            r = 0.13 * w
            (x, y), (nx, ny) = MPTS[k], MNRM[k]
            for sg in (1, -1):
                circ(doc, x + sg * nx * (w / 2 - r * 0.9), y + sg * ny * (w / 2 - r * 0.9), r, fill='#D88D78', stroke=MEM_DK, w=0.18,
                     op=smooth((w - 3.6) / 1.6))
        path(doc, poly_d([side(k, -0.5) for k in run]), stroke=MEM_DK, w=0.35, op=0.7)
    for y in PORES:
        gsdmd_pore(doc, y)
    k_channel(doc, K_Y)
    tlr(doc, TLR_Y)


def _frame(y):
    (px, py), n, t, w = mem_at(y)
    return px, py, n, t, w


def gsdmd_pore(doc, y):
    """GSDMD-N pore (side view): a wide ring of N-terminal subunits lining the opening across the bilayer."""
    px, py, n, t, w = _frame(y)
    ang = math.degrees(math.atan2(n[1], n[0]))
    fill = shade(doc, GSDMD, light=0.42, dark=0.15)
    for sg in (-1, 1):
        for k in range(3):
            off = sg * (PORE_G + 0.75 + k * 1.55)
            cx, cy = px + t[0] * off, py + t[1] * off
            L = w + 1.8 - k * 0.5
            doc.add('<rect x="%s" y="%s" width="%s" height="1.35" rx="0.6" fill="%s" stroke="#3E3550" stroke-width="0.22" '
                    'transform="rotate(%s %s %s)"/>' % (fmt(cx - L / 2), fmt(cy - 0.675), fmt(L), fill, fmt(ang), fmt(cx), fmt(cy)))


def k_channel(doc, y):
    px, py, n, t, w = _frame(y)
    ang = math.degrees(math.atan2(n[1], n[0]))
    fill = shade(doc, '#8E9BB8', light=0.45, dark=0.15)
    for sg in (-1, 1):
        cx, cy = px + t[0] * sg * (K_G + 1.3), py + t[1] * sg * (K_G + 1.3)
        L = w + 1.2
        doc.add('<rect x="%s" y="%s" width="%s" height="2.5" rx="1.1" fill="%s" stroke="#3F4C68" stroke-width="0.25" '
                'transform="rotate(%s %s %s)"/>' % (fmt(cx - L / 2), fmt(cy - 1.25), fmt(L), fill, fmt(ang), fmt(cx), fmt(cy)))


def tlr(doc, y):
    """Single-pass TLR: LRR horseshoe outside, one TM helix, TIR inside, MyD88 beneath."""
    px, py, n, t, w = _frame(y)
    ang = math.degrees(math.atan2(n[1], n[0])) + 90           # local -y = outward
    g = ['<g transform="translate(%s %s) rotate(%s)">' % (fmt(px), fmt(py), fmt(ang))]
    hd = shade_rot(doc, PLUM, ang, light=0.42, dark=0.18)
    g.append('<rect x="-0.7" y="%s" width="1.4" height="%s" rx="0.6" fill="%s" stroke="%s" stroke-width="0.2"/>'
             % (fmt(-w / 2 - 1.0), fmt(w + 2.0), hd, tone(PLUM, 0.4)))
    top = -w / 2 - 1.0
    hs = 'M-0.2,%s C-5.4,%s -6.2,%s -1.6,%s C2.6,%s 5.6,%s 4.2,%s' % (
        fmt(top), fmt(top - 2.0), fmt(top - 8.6), fmt(top - 10.6), fmt(top - 12.2), fmt(top - 9.0), fmt(top - 5.8))
    g.append('<path d="%s" stroke="%s" stroke-width="2.6" fill="none" stroke-linecap="round"/>' % (hs, tone(PLUM, 0.4)))
    g.append('<path d="%s" stroke="%s" stroke-width="1.9" fill="none" stroke-linecap="round"/>' % (hs, PLUM))
    g.append('<path d="%s" stroke="%s" stroke-width="0.5" fill="none" stroke-linecap="round" opacity="0.8"/>' % (hs, lighten(PLUM, 0.55)))
    bot = w / 2 + 1.0
    g.append('<ellipse cx="0" cy="%s" rx="2.2" ry="1.8" fill="%s" stroke="%s" stroke-width="0.25"/>' % (fmt(bot + 1.6), hd, tone(PLUM, 0.4)))
    g.append('<circle cx="0.6" cy="%s" r="1.7" fill="%s" stroke="#3C3358" stroke-width="0.25"/>'
             % (fmt(bot + 4.8), shade(doc, '#8F86B0', light=0.45, dark=0.15)))
    g.append('</g>')
    doc.add(''.join(g))


# ===================================================================================== molecules of the cascade
def nlrp3_monomer(doc, x, y, s=1.0, rot=0):
    """Inactive NLRP3: NACHT body + curved LRR + small PYD bead."""
    doc.add('<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(rot), fmt(s)))
    path(doc, 'M-1.6,-3.4 Q4.2,-2.8 3.9,0 Q4.2,3.0 -1.6,3.4 Q0.3,0 -1.6,-3.4 Z', fill=shade_rot(doc, '#E58AAE', rot, light=0.45, dark=0.12),
         stroke='#7a0c37', w=0.3)
    ell(doc, -3.4, 0, 2.0, 2.5, fill=shade_rot(doc, INFL, rot, light=0.4, dark=0.2), stroke='#7a0c37', w=0.3)
    circ(doc, -6.3, 0, 1.15, fill=shade(doc, '#F7B6CF', light=0.5, dark=0.12), stroke='#7a0c37', w=0.25)
    doc.add('</g>')


def caspase1(doc, x, y, s=1.0):
    """Active caspase-1: p20/p10 heterotetramer."""
    for (dx, dy, r) in ((-1.7, -1.3, 1.9), (1.7, -1.3, 1.5), (-1.7, 1.5, 1.5), (1.7, 1.5, 1.9)):
        circ(doc, x + dx * s, y + dy * s, r * s, fill=shade(doc, CASP, light=0.42, dark=0.18), stroke='#4D0A28', w=0.28)
    circ(doc, x - 2.1 * s, y - 1.8 * s, 0.45 * s, fill='#fff', op=0.7)


def pro_il(doc, x, y, s=1.0, rot=0, color=INFL):
    """Pro-cytokine: pale pro-domain + the mature domain, with caspase-1's cut mark between them."""
    a = math.radians(rot)
    px, py = x - math.cos(a) * 4.6 * s, y - math.sin(a) * 4.6 * s
    ell(doc, px, py, 3.5 * s, 1.6 * s, fill=shade(doc, '#F3C3D4', light=0.5, dark=0.1), stroke='#9C3A63', w=0.28, rot=rot)
    cytokine(doc, x + math.cos(a) * 0.8 * s, y + math.sin(a) * 0.8 * s, s=0.95 * s, rot=rot, color=color)
    cx, cy = x - math.cos(a) * 1.3 * s, y - math.sin(a) * 1.3 * s
    path(doc, 'M%s,%s l%s,%s' % (fmt(cx - math.sin(a) * 2.6), fmt(cy + math.cos(a) * 2.6), fmt(math.sin(a) * 5.2), fmt(-math.cos(a) * 5.2)),
         stroke=CASP, w=0.4, dash='0.9 0.7')


def gsdmd_full(doc, x, y, s=1.0, rot=0):
    """Full-length gasdermin D: N-domain (pore-forming) + C-domain (autoinhibitory), cut between them."""
    doc.add('<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(rot), fmt(s)))
    ell(doc, -2.2, 0, 2.9, 1.9, fill=shade(doc, GSDMD, light=0.45, dark=0.15), stroke='#3E3550', w=0.25)
    ell(doc, 2.6, 0.2, 2.2, 1.6, fill=shade(doc, '#B9B0C8', light=0.5, dark=0.1), stroke='#3E3550', w=0.25)
    path(doc, 'M0.4,-2.6 L0.4,2.6', stroke=CASP, w=0.4, dash='0.9 0.7')
    doc.add('</g>')


def gsdmd_n(doc, x, y, rot=0):
    doc.add('<rect x="%s" y="%s" width="5.6" height="1.4" rx="0.6" fill="%s" stroke="#3E3550" stroke-width="0.22" transform="rotate(%s %s %s)"/>'
            % (fmt(x - 2.8), fmt(y - 0.7), shade(doc, GSDMD, light=0.42, dark=0.15), fmt(rot), fmt(x), fmt(y)))


def k_ion(doc, x, y, r=1.35):
    circ(doc, x, y, r, fill=shade(doc, KCH, light=0.45, dark=0.15), stroke='#3F4C68', w=0.2)
    T(doc, x, y + 0.8, '+', size=2.3, weight=700, fill='#fff', anchor='middle')


def nfkb(doc, x, y):
    for dx, r, c in ((-1.5, 1.9, '#7468A0'), (1.6, 1.7, '#9A8FC2')):
        circ(doc, x + dx, y, r, fill=shade(doc, c, light=0.45, dark=0.15), stroke='#3C3358', w=0.25)


# ===================================================================================== 5.2 silica phagolysosome
TEAR = (12.0, 44.0)      # torn arc (deg, y down) facing the cytosolic cascade


def silica_pl(doc):
    vx, vy, vr = G.SILICA_PL
    t0, t1 = TEAR
    soft_pool(doc, vx + 6, vy + 4, vr + 30, vr + 26, '#E9DDF3', 0.55)
    contact_shadow(doc, vx + 2.5, vy + 4.5, vr * 1.02, strength=0.10, spread=1.12)
    lum = doc.radgrad([(0, '#FBF7FD'), (0.72, '#F0E6F8'), (1, '#E1D2F0')], cx=.4, cy=.36, r=.66)
    circ(doc, vx, vy, vr, fill=lum)
    silica(doc, vx - 14, vy + 22, s=0.95, rot=40, seed=3)
    silica(doc, vx - 22, vy - 18, s=0.75, rot=-25, seed=4)
    tip_ang = math.radians(27)
    s_ = 2.05
    rr = 9.49 * s_
    cx, cy = vx + (vr + 5.5 - rr) * math.cos(tip_ang), vy + (vr + 5.5 - rr) * math.sin(tip_ang)
    silica(doc, cx, cy, s=s_, rot=27 + 71.6, seed=2)
    for (dx, dy, r) in ((-30, 4, 10), (-8, -30, -30), (8, 30, 40), (-34, -6, 70), (14, -14, 0)):
        hydrolase(doc, vx + dx, vy + dy, s=0.62, rot=r, glycan=False)
    for (dx, dy) in ((-26, -30), (-36, 18), (2, -38), (-12, 36), (24, -32), (-40, -8)):
        hplus(doc, vx + dx, vy + dy, 1.0)
    with actor(doc, 'silica_membrane', pivot=(vx, vy), bbox=(785, 500, 125, 125), zone='zone_f', states=3, rest_state=1):
        st = doc.state_overrides.get('silica_membrane', 1)
        if st == 0:
            intact = arc_pts(vx, vy, vr, 0, 360, 2.0)
            bilayer_run(doc, intact, 4.4, CONV, '#F3ECFA', closed=True)
        else:
            if st == 2:
                t0, t1 = 4.0, 54.0
            intact = arc_pts(vx, vy, vr, t1, t0 + 360, 2.0)
            bilayer_run(doc, intact, 4.4, CONV, '#F3ECFA')
            for (a, sgn) in ((t1, 1), (t0, -1)):
                for off, bend in ((-1.5, -1), (1.5, 1)):
                    r_ = vr + off
                    p0 = (vx + r_ * math.cos(math.radians(a)), vy + r_ * math.sin(math.radians(a)))
                    p1 = (vx + (r_ + bend * 1.6) * math.cos(math.radians(a - sgn * 5)), vy + (r_ + bend * 1.6) * math.sin(math.radians(a - sgn * 5)))
                    path(doc, 'M%s,%s L%s,%s' % (fmt(p0[0]), fmt(p0[1]), fmt(p1[0]), fmt(p1[1])), stroke=CONV, w=1.1)
            blebs = ((18, 4.0, 1.1), (33, 6.0, 0.85), (25, -3.0, 0.7), (40, 3.2, 0.75), (14, 7.5, 0.6))
            if st == 2:
                blebs = blebs + ((8, 5.2, 0.9), (48, 4.8, 0.8), (28, 9.0, 0.7))
            for (a, dr, r) in blebs:
                x, y = vx + (vr + dr) * math.cos(math.radians(a)), vy + (vr + dr) * math.sin(math.radians(a))
                circ(doc, x, y, r, fill='none', stroke=CONV, w=0.55, op=0.75)
            if st == 2:
                for (x_, y_, r_) in ((892, 578, -15), (896, 586, 25)):
                    hydrolase(doc, x_, y_, s=0.68, rot=r_, glycan=False)
        for a in (150, 196, 242, 288, 334, 104, 70):
            vatpase(doc, vx + vr * math.cos(math.radians(a)), vy + vr * math.sin(math.radians(a)), a, s=1.0)
        path(doc, poly_d(arc_pts(vx, vy, vr - 3.4, 190, 260, 3)), stroke='#FFFFFF', w=0.9, op=0.7)


def silica_names(doc):
    vx, vy, vr = G.SILICA_PL
    step_name(doc, vx - 70, vy - vr - 9, '5.2', 'Silica phagolysosome', DPL, size=ORG)
    lab(doc, vx - 57, vy - vr - 22.5, 'silicosis: crystalline-silica lung disease', DPATH, weight=700)


# ===================================================================================== NLRP3 cascade (cytosol)
def cascade(doc):
    soft_pool(doc, 945, 628, 62, 70, '#F6C9D8', 0.32)
    # ---- signal 2: cathepsin B leaking from the tear, ROS, K+ efflux
    with actor(doc, 'patho.signal2', pivot=(935, 585), bbox=(870, 535, 130, 95), zone='zone_f'):
        for (x, y, r) in ((901, 588, 10), (909, 595, -20), (916, 589, 30), (921, 599, 0), (907, 604, 15)):
            hydrolase(doc, x, y, s=0.72, rot=r, glycan=False)
        lab(doc, 885, 618, 'cathepsin B', DBIO)
        for (x, y, s_, r) in ((906, 549, 0.95, 10), (915, 560, 0.8, 30), (921, 547, 0.7, 0)):
            ros(doc, x, y, s=s_, rot=r)
        lab(doc, 928, 559, 'ROS', DINFL)
        (kx, ky), n, _, w = mem_at(K_Y)
        for (dx, dy) in ((-9, 2.4), (-15, -2.0), (-21, 3.0)):
            k_ion(doc, kx + dx, ky + dy)
        # ---- signal 1: TLR -> MyD88 -> NF-kB (priming: NLRP3 and pro-IL-1b are made)
        (tx, ty), _, _, _ = mem_at(TLR_Y)
        nfkb(doc, tx - 21, ty + 4)
        arrow(doc, [(tx - 9.5, ty + 1.5), (tx - 17, ty + 3.2)], NFKB, 'transport', w=0.55, head=2.4, bow=0)
        lab(doc, tx - 21, ty + 13, 'NF-κB', NFKB, anchor='middle')
        lab(doc, tx - 5, ty - 22, 'signal 1 · priming (e.g. LPS)', NFKB, anchor='end')
        lab(doc, tx - 5, ty - 16.5, 'NF-κB → NLRP3 + pro-IL-1β made', NFKB, anchor='end', weight=400, italic=True)
        arrow(doc, [(tx - 25, ty + 16), (966, 590), (949, 603)], NFKB, 'transport', w=0.75, head=3.0)
    # ---- NLRP3 monomers (signal 2 arrows converge on them)
    with actor(doc, 'nlrp3', pivot=(918, 655), bbox=(885, 595, 95, 95), zone='zone_f', states=3, rest_state=2):
        st_n = doc.state_overrides.get('nlrp3', 2)
        nlrp3_monomer(doc, 939, 611, s=1.15, rot=-15)
        nlrp3_monomer(doc, 946, 624, s=1.15, rot=20)
        if st_n == 0:
            nlrp3_monomer(doc, 925, 642, s=1.15, rot=45)
            nlrp3_monomer(doc, 914, 654, s=1.15, rot=-60)
            nlrp3_monomer(doc, 930, 660, s=1.15, rot=110)
        lab(doc, 955, 622, 'NLRP3', DINFL)
    with actor(doc, 'patho.signal2'):
        arrow(doc, [(922, 606), (930, 611)], '#8A6A78', 'transport', w=0.6, head=2.4, bow=0)
        arrow(doc, [(919, 562), (928, 580), (934, 600)], '#8A6A78', 'transport', w=0.6, head=2.4)
        arrow(doc, [(kx - 24, ky + 1), (966, 607), (955, 612)], KCH, 'transport', w=0.6, head=2.4)
        lab(doc, 965, 600, 'signal 2', '#6F5E66')
    # ---- inflammasome: NLRP3 + ASC (+ pro-caspase-1)
    ix, iy = 918, 655
    asc = [(ix + 6 + k * 2.6, iy + 9 + k * 1.6) for k in range(6)]
    with actor(doc, 'nlrp3'):
        if st_n == 2:
            arrow(doc, [(936, 632), (928, 640)], '#8C6A7A', 'transport', w=0.75, head=3.0, bow=0)
            nlrp3(doc, ix, iy, s=2.0)
            for (x, y) in asc:
                circ(doc, x, y, 1.15, fill=shade(doc, '#F7B6CF', light=0.5, dark=0.15), stroke='#7a0c37', w=0.22)
            for (x, y) in asc[1::2]:
                circ(doc, x + 2.2, y - 2.1, 1.3, fill=shade(doc, '#D97AA2', light=0.4, dark=0.15), stroke='#7a0c37', w=0.22)
            lab(doc, ix, iy + 22, 'NLRP3 + ASC', DINFL, anchor='middle')
            lab(doc, ix, iy + 27.4, 'inflammasome', DINFL, anchor='middle', weight=400, italic=True)
        elif st_n == 1:
            arrow(doc, [(936, 632), (928, 640)], '#8C6A7A', 'transport', w=0.75, head=3.0, bow=0)
            for k_s in range(4):
                ang_s = k_s * 360.0 / 7.0
                nlrp3_monomer(doc, ix + 6.5 * math.cos(math.radians(ang_s)), iy + 6.5 * math.sin(math.radians(ang_s)), s=1.05, rot=ang_s)
            circ(doc, ix, iy, 3.2, fill=shade(doc, '#F7B6CF', light=0.5, dark=0.15), stroke='#7a0c37', w=0.3)
            for (x, y) in asc[:2]:
                circ(doc, x, y, 1.15, fill=shade(doc, '#F7B6CF', light=0.5, dark=0.15), stroke='#7a0c37', w=0.22)
    # ---- caspase-1
    with actor(doc, 'patho.caspase_gsdmd', pivot=(968, 668), bbox=(930, 590, 165, 115), zone='zone_f'):
        arrow(doc, [(asc[-1][0] + 2, asc[-1][1] - 2), (950, 664)], CASP, 'transport', w=0.75, head=3.0, bow=0)
        caspase1(doc, 955, 662, 1.25)
        lab(doc, 955, 675.5, 'caspase-1', CASP, anchor='middle')
        pro_il(doc, 976, 650, s=1.0, rot=-12)
        pro_il(doc, 978, 659, s=1.0, rot=6, color='#B8457A')
        cytokine(doc, 991, 646, s=0.95, rot=0)
        cytokine(doc, 991, 655, s=0.95, rot=12, color='#B8457A')
        gsdmd_full(doc, 967, 684, s=1.0, rot=-10)
        gsdmd_n(doc, 984, 676, rot=-30)
        gsdmd_n(doc, 990, 670, rot=-55)
        # caspase-1 cleaves both substrates: pro-IL-1b / pro-IL-18 -> mature cytokines; GSDMD -> GSDMD-N (the pore)
        arrow(doc, [(961, 659), (970, 654)], CASP, 'transport', w=0.6, head=2.4, bow=0)
        arrow(doc, [(963.5, 665), (967.5, 678.5)], CASP, 'transport', w=0.6, head=2.4, bow=0)
        arrow(doc, [(982, 652), (986, 651)], CASP, 'transport', w=0.45, head=2.0, bow=0)
        lab(doc, 978, 642.5, 'pro-IL-1β / -18', '#8A2E5E', anchor='middle')
        lab(doc, 997, 696, 'GSDMD → GSDMD-N', GSDMD, anchor='end')


def air_release(doc):
    """Out of the pores: IL-1b / IL-18 into the air, K+ out of its channel."""
    with actor(doc, 'patho.caspase_gsdmd'):
        for y in PORES:
            (px, py), n, _, w = mem_at(y)
            arrow(doc, [(px - 2, y), (px + 11, y + 0.5)], INFL, 'transport', w=0.55, head=2.4, bow=0)
        for (x, y, r, c) in ((1018, 641, 10, INFL), (1026, 650, -15, '#B8457A'), (1021, 663, 20, INFL), (1031, 672, 0, '#B8457A'),
                             (1036, 657, 30, INFL), (1043, 668, -10, INFL)):
            cytokine(doc, x, y, s=1.05, rot=r, color=c)
        lab(doc, 1049, 667, 'IL-1β · IL-18', DINFL, halo=PAPER)
        (kx, ky), n, _, w = mem_at(K_Y)
        for (dx, dy) in ((8, -2.6), (14, 2.4), (20, -1.0)):
            k_ion(doc, kx + dx, ky + dy)
        arrow(doc, [(kx + 5, ky + 6), (kx + 22, ky + 6.5)], KCH, 'transport', w=0.55, head=2.4, bow=0)
        lab(doc, kx + 25, ky + 1.6, 'K⁺ efflux', '#3F4C68', halo=PAPER)
    (tx, ty), _, _, _ = mem_at(TLR_Y)
    lab(doc, tx + 12, ty - 10, 'TLR', PLUM, halo=PAPER)
    with actor(doc, 'patho.caspase_gsdmd'):
        (px, py), _, _, _ = mem_at(PORES[1])
        lab(doc, px + 8, 690, 'GSDMD pore', '#4E445E', halo=PAPER)
        lab(doc, px + 8, 695.4, '~20 nm', '#4E445E', weight=400, halo=PAPER)


# ===================================================================================== right air
def dying_cell(doc, x, y, r=10.0):
    """Pyroptotic macrophage glyph: swollen, pale, membrane broken by pores, contents escaping."""
    circ(doc, x, y, r, fill=shade(doc, '#F4E6EA', light=0.45, dark=0.06))
    gaps = (35, 120, 200, 285)
    for a0, a1 in zip(gaps, gaps[1:] + (gaps[0] + 360,)):
        path(doc, poly_d(arc_pts(x, y, r, a0 + 13, a1 - 13, 4.0), False), stroke=GSDMD, w=0.9)
    for a in gaps:
        for sg in (-1, 1):
            q = math.radians(a + sg * 12)
            circ(doc, x + r * math.cos(q), y + r * math.sin(q), 0.75, fill=shade(doc, GSDMD, light=0.4, dark=0.15))
    circ(doc, x - 1.5, y + 0.5, 3.1, fill=shade(doc, '#8C7FA8', light=0.35, dark=0.2))
    silica(doc, x + 3.5, y - 3, s=0.32, rot=20)
    for (a, d, rot, col) in ((120, 3.2, 10, INFL), (35, 3.6, -20, '#B8457A'), (285, 3.0, 30, INFL)):
        cytokine(doc, x + (r + d) * math.cos(math.radians(a)), y + (r + d) * math.sin(math.radians(a)), s=0.75, rot=rot, color=col)


def drift(doc, pts, op=0.45):
    path(doc, cr_path(pts, False), stroke='#8FA9B5', w=0.35, dash='0.01 1.6', op=op)


def small_fibre(doc, x, y, L, rot, w=1.3, seed=3):
    a = math.radians(rot)
    asbestos_fibre(doc, x - math.cos(a) * L / 2, y - math.sin(a) * L / 2, x + math.cos(a) * L / 2, y + math.sin(a) * L / 2,
                   w=w, color='#D2B27A', frays=False, seed=seed)


def air(doc):
    marks.section(doc, 1012, 134, 5, 'Particles', marks.color_of(5), size=16.5)
    with actor(doc, 'patho.air_inhaled', pivot=(1055, 290), bbox=(995, 140, 105, 320), zone='air_right'):
        drift(doc, [(1086, 182), (1089, 166), (1093, 150)], op=0.5)
        silica(doc, 1085, 186, s=0.42, rot=-20)
        lab(doc, 1096, 160, 'cleared ↑', '#4F6874', anchor='end', halo=PAPER)
        drift(doc, [(1094, 200), (1070, 222), (1050, 248), (1034, 278), (1022, 308)])
        drift(doc, [(1060, 186), (1046, 214), (1040, 236)])
        silica(doc, 1072, 220, s=0.55, rot=15)
        silica(doc, 1043, 240, s=0.5, rot=-35)
        small_fibre(doc, 1060, 262, 20, 62, seed=5)
        silica(doc, 1028, 288, s=0.6, rot=40)
        drift(doc, [(1096, 330), (1080, 360), (1064, 392), (1046, 418), (1024, 436), (1004, 448)], op=0.4)
        silica(doc, 1082, 352, s=0.45, rot=-10)
        small_fibre(doc, 1052, 410, 16, -38, w=1.15, seed=7)
        silica(doc, 1018, 440, s=0.5, rot=25)
        arrow(doc, [(1030, 300), (1019, 318), (1010, 330)], PATH, 'transport', w=0.8, head=3.2)
        step_name(doc, 1032, 326, '5.1', 'uptake', DPATH, size=11.0, halo=PAPER)
        lab(doc, 1036, 334.5, 'via MARCO / SR-A', DPATH, halo=PAPER)
    with actor(doc, 'patho.pyroptosis', pivot=(1060, 600), bbox=(985, 505, 115, 155), zone='air_right'):
        dx, dy = 1080, 622
        maybe_arrow(doc, [(1047, 648), (1058, 636), (dx - 11, dy + 2)])
        dying_cell(doc, dx, dy, 9.0)
        lab(doc, 1097, 645, 'possible lytic death', '#5E4A56', anchor='end', halo=PAPER)
        maybe_arrow(doc, [(dx + 1, dy - 11), (dx + 2, 598), (dx + 2, 588)])
        silica(doc, dx + 2, 579, s=0.7, rot=12)
        maybe_arrow(doc, [(dx - 6, 572), (1056, 546), (1022, 524), (994, 512)], DPATH)
        lab(doc, 1040, 524, 'possible re-uptake', DPATH, halo=PAPER)


# ===================================================================================== zone G: asbestos
def fibre(doc):
    (xa, ya), (xb, yb) = G.ASB_FIBRE
    asbestos_fibre(doc, xa, ya, xb, yb, w=G.ASB_FIBRE_W, color='#D6B676', frays=True)


def leak(doc):
    """ROS and lysosomal enzymes released into the open cup, spilling from its mouth onto the injured epithelium."""
    with actor(doc, 'patho.leak', pivot=(1010, 745), bbox=(845, 670, 255, 135), zone='zone_g'):
        rnd = random.Random(5)
        fy = lambda x: G.fibre_point((x - G.ASB_FIBRE[0][0]) / (G.ASB_FIBRE[1][0] - G.ASB_FIBRE[0][0]))[1]
        for x in (912, 930, 948, 966, 984, 998):
            y = fy(x) - G.ASB_FIBRE_W / 2 - 1.3
            if x in (930, 966, 998):
                ros(doc, x, y - 0.1, s=0.42, rot=rnd.uniform(0, 40))
            else:
                enzyme_dot(doc, x, y, 0.6)
        s = scene.surface
        for (x, dy, kind) in ((1012, -1.9, 'e'), (1018, -2.3, 'r'), (1025, -1.8, 'e'), (1032, -2.2, 'e'), (1040, -2.4, 'r'),
                              (1048, -1.8, 'e')):
            y = s(x) + dy
            if kind == 'r':
                ros(doc, x, y, s=0.6, rot=rnd.uniform(0, 40))
            else:
                enzyme_dot(doc, x, y, 0.85)
        arrow(doc, [(1004, 744.5), (1012, 748.5), (1019, 751)], PATH, 'path', w=0.6, head=2.8, bow=0.0)


def asbestos_labels(doc):
    (xa, ya), (xb, yb) = G.ASB_FIBRE
    by = 737.5
    path(doc, 'M%s,%s L%s,%s' % (fmt(xa), fmt(by), fmt(1007), fmt(by)), stroke=DPATH, w=0.42, dash='0.01 1.2', op=0.95)
    path(doc, 'M%s,%s L%s,%s' % (fmt(1009), fmt(by), fmt(1094), fmt(by)), stroke=DPATH, w=0.32)
    path(doc, 'M%s,%s l0,%s' % (fmt(xa), fmt(by - 2.2), fmt(ya - by + 0.4)), stroke=DPATH, w=0.4)
    arrow(doc, [(1088, by), (1098, by)], DPATH, 'transport', w=0.4, head=2.4, bow=0)
    lab(doc, 1046, by - 1.8, 'long fibre, e.g. >15 µm', DPATH, anchor='middle', halo=PAPER)
    lab(doc, 1018, 768, 'ROS · enzymes', DPATH, halo=scene.TISSUE_F)


def open_cup_label(doc):
    step_name(doc, 902, 718, '5.3', 'Asbestos', DPATH, size=11.0, halo=CYTO_HALO)
    lab(doc, 902, 725, 'asbestosis: asbestos fibrosis', DPATH, weight=700, halo=CYTO_HALO)
    lab(doc, 932, 733, 'open cup', DPATH, halo=CYTO_HALO)


# ===================================================================================== lung injury on the wall
def inflammation(doc):
    with actor(doc, 'patho.leak'):
        pts = [(1050, 676), (1078, 694), (1089, 722), (1090, 748), (1088, 770)]
        arrow(doc, pts, INFL, 'signal', w=1.1, head=4.6, bow=0.0)
        lab(doc, 1080, 712, 'IL-1β · TNF-α', DINFL, anchor='end', halo=PAPER)


def fibrosis_signal(doc):
    with actor(doc, 'patho.leak'):
        arrow(doc, [(852, 722), (864, 760), (870, 796)], PATH, 'path', w=0.6, head=3.6, bow=0.0)
        lab(doc, 875, 784, 'TGF-β · PDGF', DPATH, halo=scene.TISSUE_F)


def wall_labels(doc):
    halo = scene.TISSUE_F
    step_name(doc, 1032, 816, '5.4', 'Inflammation', DINFL, size=11.0, halo=halo)
    step_name(doc, 884, 818, '5.5', 'Fibrosis', DPATH, size=11.0, halo=halo)


# ===================================================================================== draw
def draw(doc):
    silica_pl(doc)
    cascade(doc)
    right_membrane(doc)
    air_release(doc)
    silica_names(doc)
    air(doc)
    fibre(doc)
    leak(doc)
    open_cup_label(doc)
    asbestos_labels(doc)
    inflammation(doc)
    fibrosis_signal(doc)
    wall_labels(doc)
