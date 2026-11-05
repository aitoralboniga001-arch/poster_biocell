"""Section 5: particles.  Pathology told as PLACE (V1.2b text diet: names only, no captions or notes):
  - right column: heading, the silica / NLRP3 magnification (5.2) with its dashed (possible) outcome branch;
  - the alveolar wall (scene.wall, drawn here so it sits over the cell's paper halo), with 5.4 / 5.5 on its fibrotic right;
  - the long asbestos fibre in the open frustrated-phagocytosis cup, ROS + lysosomal enzymes leaking onto the epithelium;
  - the cytokine route: IL-1beta / TNF-alpha / chemokines leaving the cell and leading down to the inflamed wall."""
import math, random
from lib import *
from style import shade, tone, lighten, darken, mix, contact_shadow, spec, shade_rot, SHADOW
from bio import asbestos_fibre, silica, ros, enzyme_dot, cytokine, nlrp3, vatpase, hplus, hydrolase
import geom as G
import scene
from layout2 import heading
from annot2 import tag, DPATH, DINFL, DBIO
from stage import caption
from lenses import cone, LINK

S_LAB = 4.6        # in-figure labels
S_NOTE = 5.0       # short notes beside the drawings
INK_SOFT = '#4A4F57'
CASP = '#8E1D4E'   # caspase-1 (darker crimson, inflammasome family)
GSDMD = '#6A5D7B'  # gasdermin D
KCH = '#6E7FA8'    # K+ ions / channel


# ===================================================================================== small drawing helpers
def membrane(doc, pts, col, core, w=4.4, beads=True, closed=False):
    """Toned bilayer along a polyline: dark leaflets, pale hydrophobic core, beaded head groups."""
    d = poly_d(pts, closed)
    path(doc, d, stroke=col, w=w)
    path(doc, d, stroke=core, w=w * 0.42)
    if beads:
        for off in (w * 0.36, -w * 0.36):
            path(doc, poly_d(offset_poly(pts, off, closed), closed), stroke=tone(col, 0.25), w=w * 0.2, dash='0.01 %s' % fmt(w * 0.26), op=0.75)


def arc_pts(cx, cy, r, a0, a1, step=2.0):
    n = max(2, int(abs(a1 - a0) / step))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def lab(doc, x, y, text, color=INK_SOFT, size=S_LAB, weight=400, anchor='start', italic=False, halo=None):
    T(doc, x, y, text, size=size, weight=weight, fill=color, anchor=anchor, italic=italic, halo=halo)


def feather_ellipse_open(doc, cx, cy, rx, ry):
    """Frameless feathered window (ellipse): clip + radial alpha mask; content fades into the paper."""
    gid = doc.uid('pfg')
    doc.defs.append('<radialGradient id="%s" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff"/>'
                    '<stop offset="0.86" stop-color="#fff"/><stop offset="0.93" stop-color="#fff" stop-opacity="0.5"/>'
                    '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>' % gid)
    mid = doc.uid('pfm')
    doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="%s" y="%s" width="%s" height="%s">'
                    '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="url(#%s)"/></mask>'
                    % (mid, fmt(cx - rx - 1), fmt(cy - ry - 1), fmt(2 * rx + 2), fmt(2 * ry + 2), fmt(cx), fmt(cy), fmt(rx), fmt(ry), gid))
    doc.add('<g mask="url(#%s)">' % mid)


def feather_close(doc):
    doc.add('</g>')


# ===================================================================================== 5.2 silica / NLRP3 window
WIN = (975.0, 490.0, 103.0, 110.0)     # cx, cy, rx, ry  (feathered ellipse in PATHO_AREA, poster mm)
ZOOM = 1.15                            # the window content is drawn in its own coordinates and enlarged ~15%
XF = 'translate(977 492) scale(%s) translate(-976 -497)' % ZOOM     # content (976, 497) -> poster (977, 492)
PM_X = 1040.0                          # plasma membrane in the window (vertical, like the cell's right flank)
VES = (928.0, 462.0, 42.0)             # phagolysosome in the window
TEAR = (8.0, 50.0)                     # torn arc (deg) of the phagolysosome membrane, facing the cytosol


def pm_x(y):
    return PM_X + 1.4 * math.sin((y - 400) / 23.0)


def nlrp3_monomer(doc, x, y, s=1.0, rot=0):
    """Inactive NLRP3: NACHT body + curved LRR + small PYD bead."""
    doc.add('<g transform="translate(%s %s) rotate(%s) scale(%s)">' % (fmt(x), fmt(y), fmt(rot), fmt(s)))
    path(doc, 'M-1.6,-3.4 Q4.2,-2.8 3.9,0 Q4.2,3.0 -1.6,3.4 Q0.3,0 -1.6,-3.4 Z', fill=shade_rot(doc, '#E58AAE', rot, light=0.45, dark=0.12),
         stroke='#7a0c37', w=0.3)
    ell(doc, -3.4, 0, 2.0, 2.5, fill=shade_rot(doc, INFL, rot, light=0.4, dark=0.2), stroke='#7a0c37', w=0.3)
    circ(doc, -6.3, 0, 1.15, fill=shade(doc, '#F7B6CF', light=0.5, dark=0.12), stroke='#7a0c37', w=0.25)
    doc.add('</g>')


def caspase1(doc, x, y, s=1.0):
    """Active caspase-1: p20/p10 heterotetramer (two pairs of lobes)."""
    for (dx, dy, r) in ((-1.7, -1.3, 1.9), (1.7, -1.3, 1.5), (-1.7, 1.5, 1.5), (1.7, 1.5, 1.9)):
        circ(doc, x + dx * s, y + dy * s, r * s, fill=shade(doc, CASP, light=0.42, dark=0.18), stroke='#4D0A28', w=0.28)
    circ(doc, x - 2.1 * s, y - 1.8 * s, 0.45 * s, fill='#fff', op=0.7)


def pro_il(doc, x, y, s=1.0, rot=0, color=INFL):
    """Pro-cytokine: pale pro-domain + the mature domain (cytokine diamond) at its end."""
    a = math.radians(rot)
    px, py = x - math.cos(a) * 4.4 * s, y - math.sin(a) * 4.4 * s
    ell(doc, px, py, 3.7 * s, 1.75 * s, fill=shade(doc, '#F3C3D4', light=0.5, dark=0.1), stroke='#9C3A63', w=0.28, rot=rot)
    cytokine(doc, x + math.cos(a) * 0.8 * s, y + math.sin(a) * 0.8 * s, s=0.95 * s, rot=rot, color=color)


def gsdmd_subunit(doc, x, y, h=8.6, op=None):
    doc.add('<rect x="%s" y="%s" width="%s" height="1.8" rx="0.8" fill="%s" stroke="#3E3550" stroke-width="0.25"%s/>' % (
        fmt(x - h / 2), fmt(y - 0.9), fmt(h), shade(doc, GSDMD, light=0.4, dark=0.15), (' opacity="%s"' % op) if op else ''))


def gsdmd_pore(doc, x, y, h=8.6, gap=6.2):
    """GSDMD-N pore in the plasma membrane (side view): a WIDE ring (~20 nm, several times the K+ channel opening)
    of N-terminal subunits; open lumen of 2*gap."""
    doc.add('<rect x="%s" y="%s" width="%s" height="%s" fill="#FBF3EE"/>' % (fmt(x - h / 2 - 0.5), fmt(y - gap + 0.4), fmt(h + 1), fmt(2 * gap - 0.8)))
    for sy in (-1, 1):
        for k in range(2):
            yy = y + sy * (gap + k * 2.1)
            doc.add('<rect x="%s" y="%s" width="%s" height="1.8" rx="0.8" fill="%s" stroke="#3E3550" stroke-width="0.25"/>' % (
                fmt(x - h / 2), fmt(yy - 0.9), fmt(h), shade(doc, GSDMD, light=0.4, dark=0.15)))


def k_channel(doc, x, y):
    doc.add('<rect x="%s" y="%s" width="%s" height="%s" fill="#FBF3EE"/>' % (fmt(x - 5), fmt(y - 1.2), 10, 2.4))
    for dy in (-2.4, 2.4):
        doc.add('<rect x="%s" y="%s" width="9" height="2.6" rx="1.1" fill="%s" stroke="#3F4C68" stroke-width="0.25"/>' % (
            fmt(x - 4.5), fmt(y + dy - 1.3), shade(doc, '#8E9BB8', light=0.45, dark=0.15)))


def k_ion(doc, x, y, r=1.35):
    circ(doc, x, y, r, fill=shade(doc, KCH, light=0.45, dark=0.15), stroke='#3F4C68', w=0.2)
    T(doc, x, y + 0.8, '+', size=2.3, weight=700, fill='#fff', anchor='middle')


def focus_lines(doc, c1, win):
    """Two hairline focus lines from the source ring, tangent to the window, stopped where they meet the window's
    feathered edge (they never run into the window content)."""
    from lenses import _hair
    (x1, y1, r1), (cx, cy, rx, ry) = c1, win
    r2 = min(rx, ry)
    d = math.hypot(cx - x1, cy - y1)
    th = math.atan2(cy - y1, cx - x1)
    ph = math.acos(max(-1, min(1, (r1 - r2) / d)))
    col = mix(PATH, LINK, 0.55)
    for sg in (1, -1):
        a = th + sg * ph
        p = (x1 + r1 * math.cos(a), y1 + r1 * math.sin(a))
        q = (cx + r2 * math.cos(a), cy + r2 * math.sin(a))
        # walk from p toward q, stop at the outer feather edge of the ellipse
        n = 200
        end = q
        for i in range(n + 1):
            t = i / n
            x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 0.97 ** 2:
                end = (x, y)
                break
        _hair(doc, p, end, col)


def silica_window(doc):
    labels = []

    def T_(*a, **k):
        labels.append((a, k))

    cx, cy, rx, ry = WIN
    sx, sy, sr = G.SILICA_PL
    # hairline source ring at the in-cell silica phagolysosome + focus lines to the window
    circ(doc, sx, sy, sr + 3.2, fill='none', stroke=mix(PATH, LINK, 0.5), w=0.3, op=0.9)
    focus_lines(doc, (sx, sy, sr + 3.2), WIN)
    feather_ellipse_open(doc, cx, cy, rx, ry)
    g = doc.radgrad([(0, '#FEF6F0'), (0.65, '#FBEBE0'), (1, '#F6DFCF')], cx=.4, cy=.38, r=.7)
    ell(doc, cx, cy, rx, ry, fill=g)
    group(doc, XF)
    ys = [392 + i * 2 for i in range(106)]
    pm = [(pm_x(y), y) for y in ys]
    path(doc, poly_d(pm + [(1090, ys[-1]), (1090, ys[0])], True), fill='#EAF2F5')
    vx, vy, vr = VES
    t0, t1 = TEAR
    # --- phagolysosome (acidic lumen) with a crystal; the membrane is torn where the crystal presses on it
    lum = doc.radgrad([(0, '#F9F5FC'), (0.75, '#EFE6F8'), (1, '#E3D5F1')], cx=.42, cy=.38, r=.62)
    circ(doc, vx, vy, vr, fill=lum)
    intact = arc_pts(vx, vy, vr, t1, t0 + 360, 2.0)
    membrane(doc, intact, CONV, '#F3ECFA', w=4.2)
    for (a, sgn) in ((t1, 1), (t0, -1)):          # frayed, splayed leaflets at the tear edges
        for off, bend in ((-1.45, -1), (1.45, 1)):
            r_ = vr + off
            p0 = (vx + r_ * math.cos(math.radians(a)), vy + r_ * math.sin(math.radians(a)))
            p1 = (vx + (r_ + bend * 1.4) * math.cos(math.radians(a - sgn * 4)), vy + (r_ + bend * 1.4) * math.sin(math.radians(a - sgn * 4)))
            path(doc, 'M%s,%s L%s,%s' % (fmt(p0[0]), fmt(p0[1]), fmt(p1[0]), fmt(p1[1])), stroke=CONV, w=1.0)
    for (a, dr, r) in ((19, 3.0, 1.1), (33, 5.2, 0.85), (27, -2.2, 0.75), (42, 2.0, 0.7)):   # lipid fragments
        x, y = vx + (vr + dr) * math.cos(math.radians(a)), vy + (vr + dr) * math.sin(math.radians(a))
        circ(doc, x, y, r, fill='none', stroke=CONV, w=0.6, op=0.75)
    for a in (140, 185, 230, 275, 320):
        vatpase(doc, vx + vr * math.cos(math.radians(a)), vy + vr * math.sin(math.radians(a)), a, s=1.0)
    for (dx, dy) in ((-27, -4), (-14, 26), (18, -27), (-24, 17), (4, -31)):
        hplus(doc, vx + dx, vy + dy, 1.05)
    silica(doc, vx - 3, vy, s=2.05, rot=-14)
    silica(doc, vx + 20, vy + 20, s=0.6, rot=35)
    T_(doc, vx - 3, 441, 'crystal', size=S_LAB, weight=700, fill='#5A2A8C', anchor='middle', halo='#F3ECFA')
    # --- triggers: cathepsin B leaks out; ROS; K+ efflux
    for (x, y, r) in ((969, 482, 10), (979, 490, -20), (966, 495, 30), (988, 499, 0), (976, 503, 15)):
        hydrolase(doc, x, y, s=0.78, rot=r, glycan=False)
    path(doc, cr_path([(958, 476), (970, 486), (984, 497)], False), stroke=BIO, w=0.35, dash='0.01 1.2', op=0.7)
    T_(doc, 994, 488, 'cathepsin B', size=S_LAB, weight=700, fill=DBIO)
    for (x, y, s_, r) in ((996, 441, 0.95, 10), (1008, 449, 0.8, 30), (992, 452, 0.7, 0)):
        ros(doc, x, y, s=s_, rot=r)
    T_(doc, 1004, 437, 'ROS', size=S_LAB, weight=700, fill=DINFL)
    membrane(doc, pm, '#C4806C', '#FDEFE8', w=4.4)
    ky = 470
    k_channel(doc, pm_x(ky), ky)
    for (x, y) in ((pm_x(ky) - 8, ky + 2.0), (pm_x(ky) - 14, ky - 2.5), (pm_x(ky) + 7, ky - 1), (pm_x(ky) + 13, ky + 2.6)):
        k_ion(doc, x, y)
    arrow(doc, [(pm_x(ky) - 5, ky - 6.5), (pm_x(ky) + 15, ky - 7)], KCH, 'transport', w=0.75, head=3.4)
    T_(doc, pm_x(ky) - 6, ky - 9.5, 'K⁺', size=S_LAB, weight=700, fill='#3F4C68', anchor='end')
    # convergence: the triggers CAN activate NLRP3
    arrow(doc, [(990, 507), (976, 519)], '#8A7A80', 'transport', w=0.9, head=3.6)
    T_(doc, 975, 511, 'signal 2', size=S_LAB, weight=700, fill='#6F5E66', anchor='end')
    # signal 1 (priming): TLR -> NF-kB induces NLRP3 and pro-IL-1beta (silica alone gives no IL-1beta)
    T_(doc, 885, 503, 'signal 1', size=S_LAB, weight=700, fill='#5B4F78')
    T_(doc, 885, 508.2, 'TLR → NF-κB', size=S_LAB * 0.85, fill='#5B4F78')
    arrow(doc, [(892, 514), (899, 520), (903, 522)], '#7C6F9A', 'transport', w=0.6, head=2.8)
    # --- NLRP3 monomers -> inflammasome (NLRP3 + ASC + pro-caspase-1) -> caspase-1
    nlrp3_monomer(doc, 911, 523, s=1.1, rot=-20)
    nlrp3_monomer(doc, 918, 536, s=1.1, rot=15)
    T_(doc, 913, 549, 'NLRP3', size=S_LAB, weight=700, fill=DINFL, anchor='middle')
    arrow(doc, [(929, 530), (942, 530)], '#8C6A7A', 'transport', w=0.8, head=3.4)
    ix, iy = 956, 528
    nlrp3(doc, ix, iy, s=1.8)
    asc = [(ix + 2 + k * 2.7, iy + 6.5 + k * 2.0) for k in range(5)]
    for (x, y) in asc:
        circ(doc, x, y, 1.2, fill=shade(doc, '#F7B6CF', light=0.5, dark=0.15), stroke='#7a0c37', w=0.22)
    for (x, y) in asc[1::2]:
        circ(doc, x + 2.6, y - 1.8, 1.35, fill=shade(doc, '#D97AA2', light=0.4, dark=0.15), stroke='#7a0c37', w=0.22)
    T_(doc, 948, 553, 'inflammasome', size=S_LAB, weight=700, fill=DINFL, anchor='middle')
    T_(doc, 974, 547.5, 'ASC', size=S_LAB, weight=700, fill='#7a0c37')
    arrow(doc, [(974, 533), (985, 533)], CASP, 'transport', w=0.8, head=3.2)
    caspase1(doc, 992, 533, 1.2)
    T_(doc, 992, 524, 'caspase-1', size=S_LAB, weight=700, fill=CASP, anchor='middle')
    # caspase-1 cleaves pro-IL-1beta and pro-IL-18
    pro_il(doc, 1014, 529, s=1.05, rot=-8)
    pro_il(doc, 1014, 541, s=1.05, rot=8, color='#B8457A')
    for (x, y) in ((1005.2, 529.5), (1005.2, 540.2)):
        path(doc, 'M%s,%s l1.1,-1.5 l1.1,1.5' % (fmt(x - 1.1), fmt(y)), stroke=CASP, w=0.45)
    gy = 536
    gsdmd_pore(doc, pm_x(gy), gy)
    # caspase-1 also cleaves gasdermin D; GSDMD-N inserts into the membrane from the cytosolic side
    gsdmd_subunit(doc, 1027, 524.5, h=6.0)
    arrow(doc, [(1031, 524.5), (pm_x(gy) - 5.5, 527.5)], '#6A5D7B', 'transport', w=0.5, head=2.4)
    cytokine(doc, 1025, 532, s=0.95, rot=0)
    cytokine(doc, 1031, 540, s=0.95, rot=10, color='#B8457A')
    cytokine(doc, 1051, 531, s=1.0, rot=-10)
    cytokine(doc, 1057, 541, s=1.0, rot=15, color='#B8457A')
    T_(doc, 1012, 553, 'IL-1β', size=S_LAB, weight=700, fill=DINFL, anchor='middle')
    T_(doc, 1012, 558.4, 'IL-18', size=S_LAB, weight=700, fill='#9A3A66', anchor='middle')
    T_(doc, pm_x(gy), gy + 15.5, 'GSDMD pore', size=S_LAB, weight=700, fill='#4E445E', anchor='middle')
    T_(doc, pm_x(gy), gy + 20.5, '~20 nm', size=S_LAB * 0.85, fill='#4E445E', anchor='middle')
    T_(doc, 1046, 492, 'outside', size=S_LAB, fill='#4F6874', italic=True, halo='#EAF2F5')
    endgroup(doc)
    feather_close(doc)
    group(doc, XF)
    for a_, k_ in labels:                    # counter the window zoom so labels match the poster's label size
        k_.setdefault('halo', '#FCEFE6')
        k_['size'] = k_.get('size', S_LAB) / ZOOM
        T(*a_, **k_)
    endgroup(doc)


def dying_cell(doc, x, y, r=10.0):
    """Pyroptotic cell glyph: swollen, pale, membrane broken by pores, contents (cytokines) escaping."""
    circ(doc, x, y, r, fill=shade(doc, '#F4E6EA', light=0.45, dark=0.06))
    gaps = (35, 120, 200, 285)
    for a0, a1 in zip(gaps, gaps[1:] + (gaps[0] + 360,)):
        path(doc, poly_d(arc_pts(x, y, r, a0 + 13, a1 - 13, 4.0), False), stroke=GSDMD, w=0.9)
    for a in gaps:                                      # GSDMD pores in the broken membrane
        for sg in (-1, 1):
            q = math.radians(a + sg * 12)
            circ(doc, x + r * math.cos(q), y + r * math.sin(q), 0.75, fill=shade(doc, GSDMD, light=0.4, dark=0.15))
    circ(doc, x - 1.5, y + 0.5, 3.1, fill=shade(doc, '#8C7FA8', light=0.35, dark=0.2))      # condensed nucleus
    for (a, d, rot, col) in ((120, 3.2, 10, INFL), (35, 3.6, -20, '#B8457A'), (285, 3.0, 30, INFL)):
        cytokine(doc, x + (r + d) * math.cos(math.radians(a)), y + (r + d) * math.sin(math.radians(a)), s=0.75, rot=rot, color=col)


def maybe_arrow(doc, pts, col, w=0.7, head=3.2):
    """'Possible' arrow: dashed shaft along a smooth curve + a small solid head (dashed = may happen)."""
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    L = math.hypot(xb - xa, yb - ya)
    k = min(0.9, (head + 1.0) / L)
    hb = (xb - (xb - xa) * k, yb - (yb - ya) * k)
    path(doc, cr_path(pts[:-1] + [hb], False), stroke=col, w=w, dash='%s %s' % (fmt(w * 2.4), fmt(w * 2.0)))
    arrow(doc, [hb, pts[-1]], col, 'transport', w=w, head=head, bow=0.0)


def outcomes(doc):
    """Possible outcomes (dashed = may happen): the cell may die by pyroptosis, releasing the crystal,
    which may be taken up again by another macrophage."""
    col = '#7A6470'
    maybe_arrow(doc, [(1030, 590), (1024, 606), (1016, 616)], col)
    dx, dy = 1006, 628
    dying_cell(doc, dx, dy)
    T(doc, dx - 14, dy + 1.8, 'pyroptosis?', size=S_LAB, weight=700, fill='#5E4A56', anchor='end', halo=PAPER)
    maybe_arrow(doc, [(dx + 9, dy + 7), (1024, 641), (1034, 646)], col)
    silica(doc, 1044, 650, s=0.62, rot=12)
    maybe_arrow(doc, [(1050, 659), (1040, 677), (1000, 684), (930, 675), (878, 652), (853, 640)], DPATH)
    T(doc, 1004, 692, 're-uptake', size=S_LAB, weight=700, fill=DPATH, anchor='middle', halo=PAPER)


# ===================================================================================== cytokine route (cell -> wall)
def cytokine_route(doc):
    nx, ny = G.NLRP3_SITE
    pts = [(nx + 11, ny + 3), (812, 582), (852, 594), (868, 622), (873, 660), (884, 699), (915, 714), (945, 726), (963, 737),
           (970, 752), (972, 766)]
    arrow(doc, pts, INFL, 'signal', w=1.25, head=5.5, bow=0.0)
    for (x, y, r) in ((835, 589, 15), (869, 640, -5), (876, 682, 10), (924, 720, -10)):
        cytokine(doc, x, y, s=1.1, rot=r)
    T(doc, 891, 697, 'IL-1β · TNF-α', size=S_LAB, weight=700, fill=DINFL, halo=PAPER)


def fibrotic_signal(doc):
    """Macrophage TGF-beta / PDGF -> fibroblast-to-myofibroblast transition in the interstitium below the cell."""
    s = scene.surface
    pts = [(690, 736), (694, 760), (700, 784)]
    arrow(doc, pts, PATH, 'path', w=0.6, head=3.6, bow=0.0)
    T(doc, 706, 774, 'TGF-β · PDGF', size=S_LAB, weight=700, fill=DPATH, halo=scene.TISSUE_F)


# ===================================================================================== 5.3 asbestos
def fibre(doc):
    (xa, ya), (xb, yb) = G.ASB_FIBRE
    asbestos_fibre(doc, xa, ya, xb, yb, w=G.ASB_FIBRE_W, color='#D6B676', frays=True)


def leak(doc):
    """ROS (from NOX2 in the cup membrane) and released lysosomal enzymes in the open gap, spilling out of the mouth
    onto the epithelium below, where it is injured."""
    rnd = random.Random(5)
    roof = G.CUP_POCKET[:8]
    import cellmod3
    fy = lambda x: G.fibre_point((x - G.ASB_FIBRE[0][0]) / (G.ASB_FIBRE[1][0] - G.ASB_FIBRE[0][0]))[1]
    # inside the cup, between roof and fibre
    for x in (770, 790, 828, 858, 885, 912, 930):
        y = (cellmod3._interp_y(roof[::-1], x) + 1.6 + fy(x) - G.ASB_FIBRE_W / 2) / 2
        if x in (790, 858, 912):
            ros(doc, x, y, s=0.52, rot=rnd.uniform(0, 40))
        else:
            enzyme_dot(doc, x, y, 0.75)
    for x in (760, 838, 900):
        enzyme_dot(doc, x, fy(x) + G.ASB_FIBRE_W / 2 + 1.4, 0.6)
    # spilling out of the mouth onto the epithelium below (where it is injured)
    s = scene.surface
    for (x, dy, kind) in ((918, -2.2, 'e'), (925, -2.6, 'r'), (933, -2.2, 'e'), (942, -2.3, 'e'), (952, -2.6, 'r'),
                          (961, -2.3, 'e'), (980, -2.6, 'r'), (988, -2.2, 'e')):
        y = s(x) + dy
        if kind == 'r':
            ros(doc, x, y, s=0.72, rot=rnd.uniform(0, 40))
        else:
            enzyme_dot(doc, x, y, 0.95)
    arrow(doc, [(931, 751.2), (938, 753.4), (944, 754.4)], PATH, 'path', w=0.7, head=3.2, bow=0.0)


def asbestos_labels(doc):
    x0, y = 992, 726
    w = tag(doc, x0, y, '5.3', PATH)
    T(doc, x0 + w + 2.4, y, 'Asbestos', size=5.6, weight=700, fill=DPATH, halo=PAPER)
    # dimension bracket along the long fibre (it continues into the open cup, hence the open left end)
    (xa, ya), (xb, yb) = G.ASB_FIBRE
    by = 739.5
    path(doc, 'M%s,%s L%s,%s' % (fmt(948), fmt(by), fmt(xb), fmt(by)), stroke=DPATH, w=0.3)
    path(doc, 'M%s,%s l0,3.2' % (fmt(xb), fmt(by - 1.6)), stroke=DPATH, w=0.3)
    path(doc, 'M%s,%s l3,-1.4 M%s,%s l3,1.4' % (fmt(948), fmt(by), fmt(948), fmt(by)), stroke=DPATH, w=0.3)
    T(doc, 1012, by - 1.6, '> 15–20 µm', size=S_LAB, fill=DPATH, anchor='middle', halo=PAPER)
    T(doc, 872, 714.5, 'open cup', size=S_LAB, weight=700, fill=DPATH, halo=PAPER)
    T(doc, 1000, 768, 'ROS · enzymes', size=S_LAB, weight=700, fill=DPATH, halo=scene.TISSUE_F)


def wall_labels(doc):
    halo = scene.TISSUE_F
    for (y, num, title, dcol) in ((807, '5.4', 'Inflammation', DINFL), (822, '5.5', 'Fibrosis', DPATH)):
        w = tag(doc, 893, y, num, PATH)
        T(doc, 893 + w + 2.4, y, title, size=5.6, weight=700, fill=dcol, halo=halo)


def fate_tags(doc):
    """Particle fates shown as places, one word each (free / cleared in scene.py; engulfed here)."""
    w = tag(doc, 288, 101.5, '5.1', PATH)
    T(doc, 288 + w + 2.4, 101.5, 'uptake', size=5.6, weight=700, fill=DPATH, halo=PAPER)
    T(doc, 818, 673, 'engulfed', size=S_LAB, weight=700, fill=DPATH, anchor='middle', halo='#FBEDE2')


# ===================================================================================== draw
def draw(doc):
    x0, y0, x1, y1 = G.PATHO
    heading(doc, x0, G.PATHO_HEAD_Y, 5, 'Particles')
    tx, ty = 872, 371
    w = tag(doc, tx, ty, '5.2', PATH)
    T(doc, tx + w + 2.4, ty, 'Silica', size=5.6, weight=700, fill=DPATH, halo=PAPER)
    silica_window(doc)
    outcomes(doc)
    # tissue: the wall goes over the cell's paper halo, then the fibre and what leaks from the open cup
    scene.wall(doc)
    scene.labels(doc)
    fibrotic_signal(doc)
    fibre(doc)
    leak(doc)
    cytokine_route(doc)
    asbestos_labels(doc)
    wall_labels(doc)
    fate_tags(doc)
