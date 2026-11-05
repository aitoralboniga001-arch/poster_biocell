"""Phase 3 (P3) New Art generator for The Living Poster.

All new artwork is generated procedurally in Python using the exact same drawing primitives
(`marks.ink`, `marks.brush`, `marks.hand`, `texture.wash`, `style.shade`, `style.spec`, `bio.*`)
as the static poster so that every stroke, wash, and glyph is 100% native to the poster's hand.

Scientific constraint (§9): No hydrolase is ever drawn outside a membrane. In the margin doodles,
the cargo is represented strictly as a paper letter inside an envelope / sorting rack.
"""
import math, random
from lib import *
from style import shade, spec, tone, lighten, darken, mix, contact_shadow, soft_shadow_path
import marks as M
from marks import ink, ink_circle, brush, hand, badge
import texture
import bio

PENCIL = '#2B3040'
DOODLE_INK = '#5A5E66'
GOLD = '#E2B33C'
LUNG_W = ['#E9A9A0', '#F3C6BC', '#DE9488']
AIR_W = ['#D7E6EE', '#E8F0F2', '#C9DCE6']
COAT_W = ['#D8CFC0', '#E5DECF', '#C4B8A5']


def _outline(doc, pts, w, seed, color=PENCIL, closed=True, **kw):
    P = list(pts) + ([pts[0], pts[1]] if closed else [])
    ink(doc, P, w=w, color=color, seed=seed, **kw)


# ===================================================================== 7.2.1 Opening & Finale Sketches
def opening_street(w=550, h=450):
    """Pencil & watercolour sketch of a person seen from behind at a quiet street corner,
    breathing in a faint puff of city air (specks of dust + one tiny rod bacterium)."""
    doc = Doc(w, h)
    rect(doc, 0, 0, w, h, fill=PAPER)
    # Soft morning sky / street wash in background
    sky_d = cr_path(blob_pts(275, 165, 220, 130, n=12, j=0.1, seed=11), True)
    texture.wash(doc, sky_d, ['#E6ECEF', '#EFECE4', '#DAE4EA'], seed=12, ppm=3, strength=0.55, edge=2.5, clip=False)
    # Distant building corner + lamppost in light pencil
    ink(doc, [(88, 360), (88, 95), (215, 118), (215, 345)], w=0.55, color='#6A6E7A', seed=14, op=0.55, wobble=0.15)
    for wy in (145, 195, 245):
        for wx in (118, 165):
            ink(doc, [(wx, wy), (wx + 22, wy + 3), (wx + 22, wy + 32), (wx, wy + 29), (wx, wy)],
                w=0.38, color='#7A7E8A', seed=20 + wy + wx, op=0.45)
    # Cobblestone / pavement perspective lines
    ink(doc, [(40, 365), (215, 345), (495, 380)], w=0.5, color='#6A6E7A', seed=16, op=0.5)
    # Vintage street lamp on the right
    ink(doc, [(420, 372), (420, 145), (402, 132)], w=0.75, color=PENCIL, seed=18, op=0.65)
    lamp_glow = cr_path(blob_pts(398, 136, 26, 22, n=9, j=0.08, seed=19), True)
    texture.wash(doc, lamp_glow, ['#F7E7B4', '#FBF2D4'], seed=21, ppm=5, strength=0.65, clip=False)
    ink(doc, [(392, 128), (404, 128), (401, 144), (395, 144), (392, 128)], w=0.45, color=PENCIL, seed=22, op=0.7)

    # Person seen from three-quarter back view (head tilted slightly toward the air puff)
    coat_pts = [(210, 420), (216, 330), (230, 268), (255, 248), (298, 250), (316, 274), (326, 338), (332, 420)]
    texture.wash(doc, cr_path(coat_pts, True), ['#D5CBB8', '#E4DDD0', '#C2B6A0'], seed=31, ppm=4, strength=0.75,
                 edge=1.8, clip=False)
    ink(doc, cr_sample(coat_pts, False, per=8), w=0.95, color=PENCIL, seed=32, wobble=0.12)
    # Scarf & collar
    scarf_pts = [(248, 248), (276, 256), (304, 248), (308, 264), (274, 272), (244, 262)]
    texture.wash(doc, cr_path(scarf_pts, True), ['#C88A78', '#DDA494'], seed=33, ppm=5, strength=0.7, clip=False)
    ink(doc, cr_sample(scarf_pts, True, per=6), w=0.65, color=PENCIL, seed=34, wobble=0.08)
    # Head & hair (seen from behind/side, profile nose & chin facing right-upward)
    head_pts = [(254, 244), (250, 212), (258, 184), (278, 174), (300, 182), (308, 202), (313, 210),
                (307, 216), (309, 226), (301, 236), (292, 246)]
    texture.wash(doc, cr_path(head_pts, True), ['#F2D6C2', '#FAE6D8'], seed=35, ppm=5, strength=0.68, clip=False)
    hair_pts = [(252, 234), (246, 206), (256, 180), (280, 172), (298, 180), (292, 198), (276, 212), (262, 232)]
    texture.wash(doc, cr_path(hair_pts, True), ['#4A3F39', '#63554D'], seed=36, ppm=6, strength=0.78, clip=False)
    ink(doc, cr_sample(head_pts, False, per=6), w=0.8, color=PENCIL, seed=37, wobble=0.08)

    # Puff of cool morning air being inhaled toward the nose/mouth (around (325, 212))
    puff_d = cr_path(blob_pts(368, 196, 52, 32, n=11, j=0.14, seed=40, rot=-15), True)
    texture.wash(doc, puff_d, AIR_W, seed=41, ppm=5, strength=0.72, edge=2.0, clip=False)
    # Air streamlines curling into the nostrils
    for k, pts in enumerate([
        [(418, 176), (382, 188), (348, 202), (320, 208)],
        [(426, 198), (388, 204), (352, 212), (322, 214)],
        [(406, 222), (374, 220), (344, 218), (322, 217)],
    ]):
        ink(doc, pts, w=0.45, color='#4F6874', seed=45 + k, op=0.65, taper=(0.2, 0.4))
    # Specks of dust + silica crystal + one tiny olive rod bacterium in the puff
    for (dx, dy, r) in [(395, 184, 1.3), (376, 206, 1.0), (408, 208, 1.2), (362, 192, 0.9), (346, 210, 0.8), (386, 196, 1.1)]:
        circ(doc, dx, dy, r, fill='#8C7F6C', stroke='#5B5244', w=0.25, op=0.8)
    bio.silica(doc, 384, 192, s=0.38, rot=22, seed=3)
    # Tiny rod bacterium in the inhaled stream
    ink(doc, [(356, 201), (363, 198)], w=2.2, color='#8C9A3A', seed=55, taper=(0.15, 0.15), w_end=0.8)
    ink_circle(doc, 360, 200, 9.5, color='#C0392B', w=0.65, seed=56)

    # Caption hand-lettered in corner
    hand(doc, 275, 428, 'one ordinary breath · ~500 mL of air', size=13, fill='#4B4F5C', anchor='middle')
    return doc


def opening_lungs(w=550, h=450):
    """Larger anatomical pencil & watercolour lung sketch (s=3.2) with the red locator circle."""
    import stage
    doc = Doc(w, h)
    rect(doc, 0, 0, w, h, fill=PAPER)
    ox, oy, s = 275, 95, 3.2
    lung_pt = stage._lungs(doc, ox, oy, s=s, seed=10)
    ink_circle(doc, lung_pt[0], lung_pt[1], 11.0, color='#C0392B', w=1.1, seed=91)
    hand(doc, 275, 385, 'trachea → bronchi → bronchioles → alveoli', size=13.5, fill='#4B4F5C', anchor='middle')
    hand(doc, lung_pt[0] + 16, lung_pt[1] + 4, 'lower lobe', size=11, fill='#C0392B')
    return doc


def bronchi_tunnel(depth_step=0, w=550, h=450):
    """Three-step procedural bronchial tunnel diving into the airway tree:
    depth_step=0: cartilage-ringed bronchus with Y-bifurcation ahead
    depth_step=1: ciliated bronchiole with columnar cilia lining and closer bifurcation
    depth_step=2: terminal bronchiole opening into the sunlit alveolar sac cluster"""
    doc = Doc(w, h)
    rect(doc, 0, 0, w, h, fill=PAPER)
    cx, cy = w * 0.52, h * 0.48
    rnd = random.Random(100 + depth_step * 17)

    # Outer mucosal wash
    outer_d = cr_path(blob_pts(cx, cy, 235, 195, n=14, j=0.06, seed=10 + depth_step), True)
    pal = ['#E8B0A4', '#F3C9BE', '#D99588'] if depth_step < 2 else ['#EFC3B8', '#F6DCD4', '#E2A69A']
    texture.wash(doc, outer_d, pal, seed=20 + depth_step, ppm=3, strength=0.78, edge=2.4, clip=False)

    # Concentric perspective rings leading toward the bifurcation
    n_rings = 7 if depth_step == 0 else (6 if depth_step == 1 else 5)
    for i in range(n_rings):
        t = i / (n_rings - 1)
        rx = 220 * (1 - 0.68 * t)
        ry = 180 * (1 - 0.68 * t)
        ring_cx = cx + 18 * t * (1 if depth_step % 2 == 0 else -0.6)
        ring_cy = cy + 8 * t
        pts = M.circle_pts(ring_cx, ring_cy, (rx + ry) / 2, seed=30 + depth_step * 20 + i, turns=0.95, wob=0.04)
        # Scale circle_pts into ellipse
        epts = [(ring_cx + (px - ring_cx) * (rx / ((rx + ry) / 2)),
                 ring_cy + (py - ring_cy) * (ry / ((rx + ry) / 2))) for px, py in pts]
        if depth_step == 0:
            # Cartilage C-rings (crescent plates with heavier pencil shading)
            ink(doc, epts[:len(epts) * 3 // 4], w=1.4 * (1 - 0.5 * t), color='#6E4540', seed=50 + i, op=0.65 - 0.2 * t)
            ink(doc, epts, w=0.55 * (1 - 0.4 * t), color=PENCIL, seed=60 + i, op=0.75)
        elif depth_step == 1:
            # Ciliated bronchiole: mucosal folds + fine cilia fringe around the ring
            ink(doc, epts, w=0.6 * (1 - 0.4 * t), color=PENCIL, seed=70 + i, op=0.7)
            n_cil = int(42 * (1 - 0.5 * t))
            for k in range(n_cil):
                ang = 2 * math.pi * k / n_cil + rnd.uniform(-0.04, 0.04)
                p0 = (ring_cx + rx * math.cos(ang), ring_cy + ry * math.sin(ang))
                clen = (9.5 - 5.0 * t) * rnd.uniform(0.8, 1.2)
                bend = 0.25
                p1 = (p0[0] - math.cos(ang + bend) * clen, p0[1] - math.sin(ang + bend) * clen)
                ink(doc, [p0, p1], w=0.28, color='#5A3E3A', seed=200 + i * 50 + k, op=0.55)
        else:
            # Terminal bronchiole smoothing out into alveolar duct
            ink(doc, epts, w=0.5 * (1 - 0.35 * t), color=PENCIL, seed=80 + i, op=0.6)

    if depth_step < 2:
        # Y-bifurcation openings ahead (two dark-shaded bronchial mouths)
        sep = 38 if depth_step == 0 else 48
        br_r = 32 if depth_step == 0 else 40
        for side in (-1, 1):
            bx = cx + 14 + side * sep
            by = cy + 6 + side * 4
            mouth_d = cr_path(blob_pts(bx, by, br_r, br_r * 0.86, n=10, j=0.06, seed=90 + side), True)
            texture.wash(doc, mouth_d, ['#7A524E', '#5E3D3A', '#986C66'], seed=95 + side, ppm=5, strength=0.85, clip=False)
            ink(doc, M.circle_pts(bx, by, br_r, seed=98 + side, turns=1.02, wob=0.04),
                w=0.65, color=PENCIL, seed=102 + side, op=0.85)
        # Carina (central ridge dividing the two bronchi)
        ink(doc, [(cx + 14, cy - br_r * 0.85), (cx + 12, cy + 6), (cx + 15, cy + br_r * 0.9)],
            w=0.9, color=PENCIL, seed=105, op=0.85)
    else:
        # Depth step 2: sunlit alveolar sac cluster opening at the end of the terminal bronchiole
        sac_d = cr_path(blob_pts(cx + 10, cy + 6, 85, 72, n=12, j=0.08, seed=110), True)
        texture.wash(doc, sac_d, AIR_W, seed=111, ppm=5, strength=0.9, clip=False)
        alveoli = [(-28, -18, 24), (22, -22, 25), (36, 14, 26), (-22, 24, 24), (4, 4, 30)]
        for k, (ax, ay, ar) in enumerate(alveoli):
            ink(doc, M.circle_pts(cx + 10 + ax, cy + 6 + ay, ar, seed=120 + k, turns=1.03, wob=0.04),
                w=0.55, color=PENCIL, seed=130 + k, op=0.8)
        # Warm macrophage silhouette waiting on the lower alveolar wall
        mx, my = cx + 14, cy + 22
        m_pts = blob_pts(mx, my, 14, 9, n=9, j=0.12, seed=140)
        texture.wash(doc, cr_path(m_pts, True), ['#F6C4A6', '#EFAE8C'], seed=141, ppm=8, strength=1.0, clip=False)
        ink(doc, cr_sample(m_pts, True, per=6), w=0.5, color='#7A3B2A', seed=142)

    # Tumbling airborne particles & olive rod bacterium rushing down the stream
    b_scale = 1.0 + 0.35 * depth_step
    bx, by = cx + 22, cy - 8
    bio.bacterium(doc, bx, by, L=16 * b_scale, W=6.8 * b_scale, rot=-18 + depth_step * 14, lps=True, flagella=False, seed=7)
    bio.silica(doc, cx - 34, cy + 24, s=0.55 * b_scale, rot=15 + depth_step * 25, seed=4)
    for (dx, dy, r) in [(-55, -28, 1.8), (48, -32, 1.5), (-18, 42, 1.4), (58, 28, 1.6)]:
        circ(doc, cx + dx, cy + dy, r, fill='#8C7F6C', stroke='#5B5244', w=0.25, op=0.75)

    labels = [
        'bronchus · cartilage rings &amp; branching airways',
        'bronchiole · ciliated epithelium (~200 cilia / cell)',
        'terminal bronchiole → alveolar sac (~200 µm)',
    ]
    hand(doc, w / 2, h - 22, labels[depth_step], size=12.5, fill='#4B4F5C', anchor='middle')
    return doc


# ===================================================================== 7.2.2 Props
def prop_loupe(w=240, h=240):
    """Hand-drawn brass magnifying loupe (r=85, rim width 6 mm, handle at 135 deg)."""
    doc = Doc(w, h)
    cx, cy, r = 105, 105, 78
    # Handle at 135 deg (down-right: 45 deg in screen coords where +y is down)
    ang = math.radians(45)
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    # Handle shadow
    h_pts = [
        (cx + ux * (r + 2) + nx * 6, cy + uy * (r + 2) + ny * 6),
        (cx + ux * (r + 88) + nx * 9, cy + uy * (r + 88) + ny * 9),
        (cx + ux * (r + 92), cy + uy * (r + 92)),
        (cx + ux * (r + 88) - nx * 9, cy + uy * (r + 88) - ny * 9),
        (cx + ux * (r + 2) - nx * 6, cy + uy * (r + 2) - ny * 6),
    ]
    path(doc, cr_path(h_pts, True), fill=shade(doc, '#6E472B', light=0.38, dark=0.25), stroke=PENCIL, w=0.8)
    # Brass ferrule collar joining handle to rim
    f_pts = [
        (cx + ux * (r - 1) + nx * 7, cy + uy * (r - 1) + ny * 7),
        (cx + ux * (r + 16) + nx * 6.5, cy + uy * (r + 16) + ny * 6.5),
        (cx + ux * (r + 16) - nx * 6.5, cy + uy * (r + 16) - ny * 6.5),
        (cx + ux * (r - 1) - nx * 7, cy + uy * (r - 1) - ny * 7),
    ]
    path(doc, poly_d(f_pts, True), fill=shade(doc, '#C99E4C', light=0.45, dark=0.2), stroke=PENCIL, w=0.7)

    # Subtle glass lens tint + inner shadow ring
    glass_g = doc.radgrad([(0, '#F4FAFC', 0.08), (0.75, '#D8ECF2', 0.16), (1, '#8FA8B2', 0.28)])
    circ(doc, cx, cy, r - 3, fill=glass_g)
    circ(doc, cx, cy, r - 4.5, fill='none', stroke='#5A6872', w=1.2, op=0.25)

    # Brass rim (shaded annulus)
    brass_g = shade(doc, '#C99E4C', light=0.48, dark=0.22)
    circ(doc, cx, cy, r, fill='none', stroke=brass_g, w=7.0)
    circ(doc, cx, cy, r + 3.5, fill='none', stroke=PENCIL, w=0.75, op=0.85)
    circ(doc, cx, cy, r - 3.5, fill='none', stroke='#7A5B20', w=0.65, op=0.85)
    # Specular crescent on the glass and rim
    spec(doc, cx, cy, r - 6, a0=200, a1=252, op=0.75, inset=0.88, w=2.2)
    spec(doc, cx, cy, r, a0=195, a1=245, op=0.65, inset=1.0, w=1.1)
    return doc


def prop_turret(state=0, w=200, h=120):
    """Revolving microscope nosepiece with 4 objectives (1x, 100x, 1000x, 100000x) + EM mode (states 0..4)."""
    doc = Doc(w, h)
    cx, cy = 100, 18
    labels = [('1×', '#C0392B', 26), ('100×', '#D99B26', 34), ('1 000×', '#2B6CB0', 42),
              ('100 000×', '#6F36A8', 48), ('EM', '#1E8A5A', 52)]
    # Revolving turret dome
    path(doc, 'M%s,%s Q%s,%s %s,%s L%s,%s Q%s,%s %s,%s Z' % (
        fmt(cx - 58), fmt(cy), fmt(cx), fmt(cy + 14), fmt(cx + 58), fmt(cy),
        fmt(cx + 46), fmt(cy + 28), fmt(cx), fmt(cy + 38), fmt(cx - 46), fmt(cy + 28)),
        fill=shade(doc, '#4A5260', light=0.35, dark=0.25), stroke=PENCIL, w=0.8)
    # Knurled brass grip ring
    path(doc, 'M%s,%s Q%s,%s %s,%s' % (fmt(cx - 54), fmt(cy + 12), fmt(cx), fmt(cy + 24), fmt(cx + 54), fmt(cy + 12)),
         stroke='#C99E4C', w=3.2, dash='2.0 1.4')

    # Draw 3 visible objectives (-1, 0=active center, +1) around the nosepiece
    for offset in (-1, 1, 0):
        idx = (state + offset) % len(labels)
        lbl_txt, band_col, obj_len = labels[idx]
        ang = offset * 34  # degrees from vertical
        scale = 1.0 if offset == 0 else 0.82
        op = 1.0 if offset == 0 else 0.65
        ox = cx + offset * 34
        oy = cy + 28 - abs(offset) * 4
        doc.add('<g transform="translate(%s %s) rotate(%s) scale(%s)" opacity="%s">' % (
            fmt(ox), fmt(oy), fmt(-ang), fmt(scale), fmt(op)))
        # Barrel
        bw = 18
        rect(doc, -bw / 2, 0, bw, obj_len, fill=shade(doc, '#363D4A', light=0.45, dark=0.2), stroke=PENCIL, sw=0.65, r=2)
        # Brass threads at top
        rect(doc, -bw / 2 - 1, 0, bw + 2, 5, fill=shade(doc, '#C99E4C', light=0.45, dark=0.2), stroke=PENCIL, sw=0.5, r=1)
        # Colour-coded magnification band
        rect(doc, -bw / 2 + 0.5, obj_len - 13, bw - 1, 4.2, fill=band_col, stroke=PENCIL, sw=0.35)
        # Beveled nozzle tip
        path(doc, 'M%s,%s L%s,%s L%s,%s L%s,%s Z' % (
            fmt(-bw / 2 + 1), fmt(obj_len), fmt(-bw / 2 + 4), fmt(obj_len + 7),
            fmt(bw / 2 - 4), fmt(obj_len + 7), fmt(bw / 2 - 1), fmt(obj_len)),
            fill=shade(doc, '#C99E4C', light=0.45, dark=0.2), stroke=PENCIL, w=0.55)
        doc.add('</g>')

    # Active magnification label below the center objective
    act_txt, act_col, act_len = labels[state % len(labels)]
    hand(doc, cx, cy + 36 + act_len + 20, act_txt, size=14, fill=act_col, anchor='middle')
    return doc


def prop_stopwatch(w=120, h=140):
    """Pocket stopwatch in pencil and brass wash, ticks for seconds (0..60 s) and minutes (0..30 min)."""
    doc = Doc(w, h)
    cx, cy, r = 60, 78, 46
    # Bow ring & crown at top
    circ(doc, cx, cy - r - 13, 8.5, fill='none', stroke='#C99E4C', w=2.2)
    circ(doc, cx, cy - r - 13, 8.5, fill='none', stroke=PENCIL, w=0.5)
    rect(doc, cx - 5, cy - r - 7, 10, 7, fill=shade(doc, '#C99E4C', light=0.45, dark=0.2), stroke=PENCIL, sw=0.6, r=1.5)
    # Brass case + warm enamel dial
    contact_shadow(doc, cx, cy, r, strength=0.14)
    circ(doc, cx, cy, r + 4, fill=shade(doc, '#C99E4C', light=0.48, dark=0.22), stroke=PENCIL, w=0.8)
    circ(doc, cx, cy, r, fill='#FAF6EC', stroke='#8A6D2F', w=0.8)
    # Minute sub-dial (0..30 min)
    sub_y, sub_r = cy - 16, 11
    circ(doc, cx, sub_y, sub_r, fill='#F3EDE0', stroke=PENCIL, w=0.4)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        line(doc, cx + (sub_r - 2) * math.cos(a), sub_y + (sub_r - 2) * math.sin(a),
             cx + sub_r * math.cos(a), sub_y + sub_r * math.sin(a), PENCIL, 0.35)
    # Outer second ticks (0..60 s)
    for k in range(60):
        a = math.radians(k * 6 - 90)
        major = (k % 5 == 0)
        r0 = r - (5.5 if major else 3.0)
        line(doc, cx + r0 * math.cos(a), cy + r0 * math.sin(a),
             cx + (r - 1.2) * math.cos(a), cy + (r - 1.2) * math.sin(a),
             PENCIL, 0.65 if major else 0.3)
    for num, deg in (('60', -90), ('15', 0), ('30', 90), ('45', 180)):
        a = math.radians(deg)
        T(doc, cx + (r - 11) * math.cos(a), cy + (r - 11) * math.sin(a) + 2.2, num,
          size=6.5, weight=600, fill=PENCIL, anchor='middle', family=SERIF)
    # Sweeping hand (wrapped in id="stopwatch-hand" for DOM rotation)
    doc.add('<g id="stopwatch-hand" transform="translate(%s %s)">' % (fmt(cx), fmt(cy)))
    line(doc, 0, 8, 0, -(r - 6), '#C0392B', 1.2)
    circ(doc, 0, 0, 2.4, fill='#C0392B', stroke=PENCIL, w=0.4)
    doc.add('</g>')
    return doc


def prop_calendar(state=0, w=140, h=160):
    """Tear-off wall calendar for Zone G (states 0..4: day 1 -> month 1 -> year 1 -> year 10 -> year 30)."""
    doc = Doc(w, h)
    x0, y0, cw, ch = 22, 20, 96, 112
    pages = [
        ('DAY 1', 'acute injury', '#2B6CB0'),
        ('MONTH 1', 'persistent cup', '#8A560A'),
        ('YEAR 1', 'chronic IL-1β', '#B8452A'),
        ('YEAR 10', 'collagen scar', '#9A440A'),
        ('YEAR 30', 'fibrosis', '#7A2E0A'),
    ]
    title_txt, sub_txt, hdr_col = pages[state % len(pages)]
    # Drop shadow & backing board
    rect(doc, x0 + 3, y0 + 4, cw, ch, fill='#8A7E6B', op=0.25, r=4)
    rect(doc, x0, y0, cw, ch, fill='#FAF6EC', stroke=PENCIL, sw=0.85, r=3)
    # Colored header band + brass binding rings
    rect(doc, x0, y0, cw, 26, fill=hdr_col, stroke=PENCIL, sw=0.75, r=3)
    for rx in (x0 + 22, x0 + cw - 22):
        circ(doc, rx, y0 + 8, 3.2, fill='#E8E2D5', stroke=PENCIL, w=0.6)
        path(doc, 'M%s,%s A4,6 0 1 1 %s,%s' % (fmt(rx - 2), fmt(y0 + 8), fmt(rx + 2), fmt(y0 + 8)),
             stroke='#C99E4C', w=1.6)
    # Perforation line
    line(doc, x0 + 4, y0 + 28, x0 + cw - 4, y0 + 28, '#8A7F6C', 0.5, dash='2.0 1.6')
    # Main date text
    T(doc, x0 + cw / 2, y0 + 18, 'LUNG TISSUE LOG', size=6.2, weight=700, fill='#FFFFFF', anchor='middle')
    T(doc, x0 + cw / 2, y0 + 68, title_txt, size=15.5, weight=700, fill=PENCIL, anchor='middle', family=SERIF)
    hand(doc, x0 + cw / 2, y0 + 94, sub_txt, size=13, fill=hdr_col, anchor='middle')

    # If state > 0, draw a curling torn page peeling off at the bottom right
    if state > 0:
        prev_txt, _, _ = pages[(state - 1) % len(pages)]
        peel = [(x0 + 12, y0 + ch - 4), (x0 + cw - 4, y0 + ch - 18), (x0 + cw + 8, y0 + ch + 14), (x0 + 24, y0 + ch + 18)]
        path(doc, cr_path(peel, True), fill='#F2ECE0', stroke=PENCIL, w=0.55, op=0.85)
        T(doc, x0 + cw / 2 + 6, y0 + ch + 8, prev_txt, size=7.5, fill='#8A7F6C', anchor='middle', family=SERIF)
    return doc


def prop_ph_gauge_dial(w=160, h=110):
    """Semicircular litmus dial (pH 7.4 -> 6.5 -> 5.5 -> 4.5) with a pivoted needle."""
    doc = Doc(w, h)
    cx, cy, r = 80, 86, 58
    # Semicircular dial plate
    path(doc, 'M%s,%s A%s,%s 0 0 1 %s,%s L%s,%s Z' % (
        fmt(cx - r - 8), fmt(cy), fmt(r + 8), fmt(r + 8), fmt(cx + r + 8), fmt(cy), fmt(cx - r - 8), fmt(cy)),
        fill='#FAF6EC', stroke=PENCIL, w=0.85)
    # Litmus colour arc (7.4 blue-grey -> 6.5 amber -> 5.5 red-orange -> 4.5 violet)
    stops = [
        (180, 140, '#6B8BA4'),
        (140, 95, '#E8892D'),
        (95, 48, '#D2452E'),
        (48, 0, '#6F36A8'),
    ]
    for a0, a1, col in stops:
        p0 = (cx + (r - 6) * math.cos(math.radians(a0)), cy - (r - 6) * math.sin(math.radians(a0)))
        p1 = (cx + (r - 6) * math.cos(math.radians(a1)), cy - (r - 6) * math.sin(math.radians(a1)))
        path(doc, 'M%s,%s A%s,%s 0 0 1 %s,%s' % (fmt(p0[0]), fmt(p0[1]), fmt(r - 6), fmt(r - 6), fmt(p1[0]), fmt(p1[1])),
             stroke=col, w=8.5, cap='butt', op=0.88)
    for lbl_txt, deg, col in (('7.4', 165, '#4A657A'), ('6.5', 118, '#B86214'), ('5.5', 70, '#A82E1B'), ('4.5', 20, '#5A2A8C')):
        a = math.radians(deg)
        T(doc, cx + (r - 19) * math.cos(a), cy - (r - 19) * math.sin(a) + 2.5, lbl_txt,
          size=7.2, weight=700, fill=col, anchor='middle')
    hand(doc, cx, cy - 12, 'lumen pH', size=10.5, fill=PENCIL, anchor='middle')
    # Pivoted needle (default pointing straight up, rotated by JS via #ph-needle)
    doc.add('<g id="ph-needle" transform="translate(%s %s)">' % (fmt(cx), fmt(cy)))
    line(doc, 0, 0, 0, -(r - 8), PENCIL, 1.5)
    circ(doc, 0, 0, 4.0, fill='#C99E4C', stroke=PENCIL, w=0.6)
    doc.add('</g>')
    return doc


SIZE_TAGS_SPEC = [
    ('tag_you', 'you · 1.7 m', '#2B3040'),
    ('tag_alveolus', 'alveolus ≈ 200 µm', '#C0392B'),
    ('tag_macrophage', 'macrophage ≈ 20 µm', '#B8321C'),
    ('tag_bacterium', 'bacterium ≈ 2 µm', '#6E7A26'),
    ('tag_lysosome', 'lysosome ≈ 0.5 µm', '#5A2A8C'),
    ('tag_receptor', 'receptor ≈ 10 nm', '#1E4E9A'),
    ('tag_snare', 'SNARE bundle ≈ 12 nm', '#5A2A8C'),
    ('tag_gsdmd', 'GSDMD pore ≈ 20 nm', '#8E1D4E'),
    ('tag_silica', 'silica ≈ 1–5 µm', '#9A560A'),
    ('tag_asbestos', '&gt; 15–20 µm', '#9A560A'),
]


def prop_size_tag(text, color='#2B3040', w=180, h=48):
    """Hand-inked paper size tag with a pin-dot and short leader, in marks.HAND."""
    doc = Doc(w, h)
    # Pin-dot on the left + short hand-inked leader to the paper tag
    circ(doc, 8, h / 2, 2.2, fill=color, stroke=PENCIL, w=0.4)
    ink(doc, [(10, h / 2), (24, h / 2)], w=0.55, color=color, seed=11)
    # Paper tag polygon with notched left end and pin hole
    tag_pts = [(24, h / 2 - 8), (32, 7), (w - 6, 7), (w - 6, h - 7), (32, h - 7), (24, h / 2 + 8)]
    path(doc, poly_d(tag_pts, True), fill='#FAF6EC', stroke=color, w=0.75)
    circ(doc, 31, h / 2, 1.8, fill=PAPER, stroke=color, w=0.45)
    hand(doc, (34 + w - 6) / 2, h / 2 + 4.2, text, size=13.5, fill=color, anchor='middle')
    return doc


# ===================================================================== 7.2.3 Margin Doodles (Section 3, Urtzi)
def doodle_envelope(w=240, h=180):
    """Margin doodle 1 (3.2 cis-Golgi / 3.3 TGN): A paper letter Safely INSIDE an envelope
    being stamped with a gold M6P wax seal (no bare hydrolase outside a membrane)."""
    doc = Doc(w, h)
    # Soft paper backing wash
    texture.wash(doc, cr_path(blob_pts(w / 2, h / 2, 95, 68, n=10, j=0.08, seed=1), True),
                 ['#F3EFE6', '#EAE4D7'], seed=2, ppm=3, strength=0.5, clip=False)
    ex, ey, ew, eh = 42, 48, 124, 82
    # Envelope body in pencil grey
    ink(doc, [(ex, ey), (ex + ew, ey), (ex + ew, ey + eh), (ex, ey + eh), (ex, ey)],
        w=1.1, color=DOODLE_INK, seed=10, wobble=0.15)
    # Folded bottom flaps
    ink(doc, [(ex, ey + eh), (ex + ew * 0.42, ey + eh * 0.52)], w=0.7, color=DOODLE_INK, seed=11)
    ink(doc, [(ex + ew, ey + eh), (ex + ew * 0.58, ey + eh * 0.52)], w=0.7, color=DOODLE_INK, seed=12)
    # Top V-flap closed over the letter inside
    ink(doc, [(ex, ey), (ex + ew / 2, ey + eh * 0.58), (ex + ew, ey)], w=0.95, color=DOODLE_INK, seed=13)
    # Postmark wavy lines in pencil grey
    for k in range(3):
        yy = ey + 16 + k * 6
        ink(doc, [(ex + 16, yy), (ex + 28, yy - 2), (ex + 40, yy + 2), (ex + 52, yy)],
            w=0.5, color=DOODLE_INK, seed=20 + k, op=0.75)

    # Gold M6P wax seal right on the flap tip (the ONLY coloured element!)
    sx, sy = ex + ew / 2, ey + eh * 0.56
    seal_d = cr_path(blob_pts(sx, sy, 13.5, 13.0, n=10, j=0.08, seed=30), True)
    path(doc, seal_d, fill=shade(doc, GOLD, light=0.45, dark=0.18), stroke='#7A5A00', w=0.8)
    circ(doc, sx, sy, 9.2, fill='none', stroke='#7A5A00', w=0.5, op=0.8)
    T(doc, sx, sy + 4.2, 'M6P', size=9.5, weight=700, fill='#3B2D00', anchor='middle')

    # Hand-drawn rubber stamp lifting away at top right
    st_pts = [(sx + 26, sy - 22), (sx + 54, sy - 34), (sx + 58, sy - 25), (sx + 30, sy - 13)]
    ink(doc, st_pts + [st_pts[0]], w=0.85, color=DOODLE_INK, seed=40)
    ink(doc, [(sx + 42, sy - 29), (sx + 52, sy - 50), (sx + 60, sy - 46), (sx + 48, sy - 26)],
        w=0.85, color=DOODLE_INK, seed=41)
    hand(doc, w / 2, h - 14, 'postal tag: M6P address stamp', size=12, fill=DOODLE_INK, anchor='middle')
    return doc


def doodle_sorting(w=240, h=180):
    """Margin doodle 2 (3.3 TGN / 3.4 Clathrin bud): Sorting-office pigeonhole rack ('TGN')
    routing the gold-sealed envelope into the 'Lysosome (M6PR)' mailbag."""
    doc = Doc(w, h)
    texture.wash(doc, cr_path(blob_pts(w / 2, h / 2, 98, 70, n=10, j=0.08, seed=3), True),
                 ['#F3EFE6', '#EAE4D7'], seed=4, ppm=3, strength=0.5, clip=False)
    # Pigeonhole sorting cabinet on the left
    rx, ry, rw, rh = 24, 30, 86, 102
    ink(doc, [(rx, ry), (rx + rw, ry), (rx + rw, ry + rh), (rx, ry + rh), (rx, ry)],
        w=1.0, color=DOODLE_INK, seed=50)
    for dy in (34, 68):
        ink(doc, [(rx, ry + dy), (rx + rw, ry + dy)], w=0.75, color=DOODLE_INK, seed=51 + dy)
    ink(doc, [(rx + rw / 2, ry), (rx + rw / 2, ry + rh)], w=0.75, color=DOODLE_INK, seed=55)
    hand(doc, rx + rw / 2, ry - 6, 'TGN sorting rack', size=11, fill=DOODLE_INK, anchor='middle')
    hand(doc, rx + 22, ry + 22, 'secretion', size=9.5, fill=DOODLE_INK, anchor='middle')
    hand(doc, rx + 64, ry + 22, 'M6PR slot', size=9.5, fill=DOODLE_INK, anchor='middle')

    # Clathrin mailbag on the right with cross-hatched basket weave
    bx, by, br = 172, 92, 34
    bag_pts = M.circle_pts(bx, by, br, seed=60, turns=1.02, wob=0.05)
    ink(doc, bag_pts, w=1.0, color=DOODLE_INK, seed=61)
    for d in (-18, -6, 6, 18):
        ink(doc, [(bx - 22, by + d - 8), (bx + 22, by + d + 8)], w=0.45, color=DOODLE_INK, seed=70 + d, op=0.55)
        ink(doc, [(bx - 22, by + d + 8), (bx + 22, by + d - 8)], w=0.45, color=DOODLE_INK, seed=80 + d, op=0.55)
    hand(doc, bx, by + br + 14, 'clathrin mailbag', size=11, fill=DOODLE_INK, anchor='middle')

    # Envelope with gold M6P seal flying along a dashed trajectory from the M6PR slot into the mailbag
    ink(doc, [(rx + 68, ry + 48), (132, 46), (bx - 8, by - 14)], w=0.7, color=DOODLE_INK, seed=90, op=0.7)
    ex, ey, ew, eh = 114, 34, 36, 24
    ink(doc, [(ex, ey), (ex + ew, ey), (ex + ew, ey + eh), (ex, ey + eh), (ex, ey)], w=0.8, color=DOODLE_INK, seed=91)
    ink(doc, [(ex, ey), (ex + ew / 2, ey + eh * 0.6), (ex + ew, ey)], w=0.7, color=DOODLE_INK, seed=92)
    circ(doc, ex + ew / 2, ey + eh * 0.58, 4.8, fill=GOLD, stroke='#7A5A00', w=0.5)
    T(doc, ex + ew / 2, ey + eh * 0.58 + 2.0, 'P', size=5.5, weight=700, fill='#3B2D00', anchor='middle')
    return doc


def doodle_postman_home(w=240, h=180):
    """Margin doodle 3 (3.5 Late endosome -> TGN): The sealed envelope delivered inside the acidic
    'LE pH 4.9' drop-box, while the empty M6PR carrier walks back up the stairs to the TGN."""
    doc = Doc(w, h)
    texture.wash(doc, cr_path(blob_pts(w / 2, h / 2, 98, 70, n=10, j=0.08, seed=5), True),
                 ['#F3EFE6', '#EAE4D7'], seed=6, ppm=3, strength=0.5, clip=False)
    # Delivery drop-box ('LE · pH 4.9') at bottom left with the envelope safely inside its window
    bx, by, bw, bh = 26, 78, 76, 66
    ink(doc, [(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh), (bx, by)], w=1.0, color=DOODLE_INK, seed=101)
    hand(doc, bx + bw / 2, by + 16, 'LE · pH 4.9', size=11, fill=DOODLE_INK, anchor='middle')
    # Envelope inside the LE box (gold seal detached beside it inside the box)
    ex, ey, ew, eh = bx + 14, by + 26, 44, 28
    ink(doc, [(ex, ey), (ex + ew, ey), (ex + ew, ey + eh), (ex, ey + eh), (ex, ey)], w=0.75, color=DOODLE_INK, seed=102)
    ink(doc, [(ex, ey), (ex + ew / 2, ey + eh * 0.58), (ex + ew, ey)], w=0.65, color=DOODLE_INK, seed=103)
    circ(doc, ex + ew + 9, ey + 10, 4.5, fill=GOLD, stroke='#7A5A00', w=0.5)
    T(doc, ex + ew + 9, ey + 12, 'P', size=5.2, weight=700, fill='#3B2D00', anchor='middle')

    # Ascending staircase back to 'TGN' at top right
    steps = [(112, 136), (112, 116), (136, 116), (136, 96), (160, 96), (160, 76), (184, 76), (184, 56), (212, 56)]
    ink(doc, steps, w=0.9, color=DOODLE_INK, seed=105)
    hand(doc, 198, 46, 'back to TGN', size=11, fill=DOODLE_INK, anchor='middle')

    # Empty M6PR Y-shaped receptor carrier climbing the stairs with a curved return arrow
    mx, my = 152, 72
    ink(doc, [(mx, my + 12), (mx, my), (mx - 8, my - 9)], w=1.1, color=DOODLE_INK, seed=108)
    ink(doc, [(mx, my), (mx + 8, my - 9)], w=1.1, color=DOODLE_INK, seed=109)
    ink(doc, [(118, 96), (136, 68), (168, 48)], w=0.75, color=DOODLE_INK, seed=110)
    hand(doc, w / 2, h - 12, 'empty receptor recycled to TGN', size=11.5, fill=DOODLE_INK, anchor='middle')
    return doc


# ===================================================================== 7.2.4 Finale Signatures & Desk Fibre
SIGNATURES_SPEC = [
    (1, 'Aitor', 193, 224),
    (2, 'Nerea', 128, 520),
    (3, 'Urtzi', 790, 465),
    (4, 'Eneritz', 520, 735),
    (5, 'Nora', 960, 825),
]


def signature_card(sec_num, name, w=160, h=60):
    """Hand-lettered team signature in the section's identity colour."""
    doc = Doc(w, h)
    col = M.color_of(sec_num)
    badge(doc, 22, h / 2 - 2, 8.5, col, sec_num, seed=sec_num * 11)
    hand(doc, 38, h / 2 + 5, name, size=24, fill=col, swash=True)
    # Flourish underline stroke
    brush(doc, [(38, h / 2 + 12), (82, h / 2 + 10), (132, h / 2 + 13)], 1.4, col, seed=sec_num * 17, op=0.8, dry=0.6)
    return doc


def desk_fibre(w=260, h=140):
    """Off-paper extension of the asbestos fibre (poster x: 960 -> 1210, y: 700 -> 800)
    casting a drop shadow onto the wooden desk beyond x = 1100."""
    doc = Doc(w, h)
    # Local coords: x_local = x_poster - 960, y_local = y_poster - 680
    # Paper edge is at x_poster = 1100 -> x_local = 140
    # Draw subtle paper edge line + shadow at x_local = 140
    rect(doc, 140, 0, w - 140, h, fill='#3A2A1D', op=0.0)  # transparent so CSS desk shows through
    # Soft drop shadow cast by the overhanging fibre onto the desk (x_local > 140)
    xa, ya = 12, 40     # (972, 720) in poster mm
    xb, yb = 242, 76    # (1202, 756) in poster mm
    # Shadow under overhanging segment (from x=140 to 242)
    sx0, sy0 = 140, ya + (yb - ya) * (140 - xa) / (xb - xa)
    for step_i, (dx, dy, sw, op) in enumerate([(2.2, 4.2, 9.0, 0.12), (1.8, 3.4, 5.5, 0.18), (1.2, 2.4, 3.2, 0.24)]):
        path(doc, 'M%s,%s L%s,%s' % (fmt(sx0 + dx), fmt(sy0 + dy), fmt(xb + dx), fmt(yb + dy)),
             stroke='#1A110B', w=sw, op=op, cap='round')
    # The full chrysotile asbestos fibre bundle extending past x=1100 onto the desk
    bio.asbestos_fibre(doc, xa, ya, xb, yb, w=3.2, color='#D6B676', frays=True, seed=2)
    return doc


# ===================================================================== Bloom Masks & Particle Sprites
def bloom_mask_1(w=1100, h=900):
    """Soft watercolour bloom mask centred on the phagolysosome (622, 665) for Beat 2.7 / 4."""
    doc = Doc(w, h)
    g = doc.radgrad([(0, '#9C5CC6', 0.55), (0.45, '#B86EE0', 0.28), (0.78, '#D9A6F0', 0.08), (1, '#D9A6F0', 0.0)])
    circ(doc, 622, 665, 115, fill=g)
    return doc


def bloom_mask_2(w=1100, h=900):
    """Soft watercolour bloom mask centred on the silica phagolysosome & NLRP3 (890, 610) for Beat 5.2."""
    doc = Doc(w, h)
    g = doc.radgrad([(0, '#D93870', 0.50), (0.48, '#E86A95', 0.25), (0.8, '#F6B4C8', 0.07), (1, '#F6B4C8', 0.0)])
    circ(doc, 890, 610, 135, fill=g)
    return doc


def sprite_hplus(w=32, h=32):
    doc = Doc(w, h)
    bio.hplus(doc, 16, 16, s=4.5)
    return doc


def sprite_ros(w=40, h=40):
    doc = Doc(w, h)
    bio.ros(doc, 20, 20, s=2.2)
    return doc


def sprite_cytokine(w=32, h=32):
    doc = Doc(w, h)
    bio.cytokine(doc, 16, 16, s=3.2)
    return doc


def sprite_bacterium_cursor(w=48, h=48):
    doc = Doc(w, h)
    bio.bacterium(doc, 24, 24, L=28, W=12, rot=-30, lps=True, flagella=False, seed=7)
    return doc
