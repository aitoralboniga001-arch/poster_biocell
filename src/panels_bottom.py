"""Bottom strip: Rab/SNARE integration inset, two killing systems, conclusion."""
import math, random
from lib import *
from bio import *
from panels_common import *
from annot import step, DLY, DLE, DBIO
from cellmod import tag, on_circle
from cellmod2 import nox2

BY0, BY1 = 714, 846
RABC = '#C23B2A'
HOPSC = '#6E3FB0'
QA, QB, QC, RS = '#2F6FDB', '#5AA3F0', '#1A4FAE', '#E08A00'


def helix(doc, x0, y0, x1, y1, color, amp=1.3, turns=3.0, w=1.1, phase=0.0):
    n = 28
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts = []
    for i in range(n + 1):
        t = i / n
        s = amp * math.sin(2 * math.pi * turns * t + phase)
        pts.append((x0 + ux * L * t + nx * s, y0 + uy * L * t + ny * s))
    path(doc, poly_d(pts), stroke=color, w=w, cap='round')


def mem_path(pts):
    return cr_path(pts, False)


def mem_draw(doc, pts, color='#9B3F8A', fillside=None):
    d = mem_path(pts)
    path(doc, d, stroke=color, w=4.0, cap='butt')
    path(doc, d, stroke='#fff', w=1.4, cap='butt')
    dense = cr_sample(pts, closed=False, per=10)
    for off in (-1.5, 1.5):
        path(doc, poly_d(offset_poly(dense, off, closed=False)), stroke='#5E2A57', w=1.1, dash='0.01 1.9', cap='round')


def rab_pin(doc, x, y, side=1, r=2.6):
    """Rab GTPase anchored by its geranylgeranyl tail; side=+1 body to the right of the membrane."""
    path(doc, 'M%s,%s q%s,%s %s,%s' % (fmt(x), fmt(y), fmt(side * -1.5), fmt(-1.6), fmt(side * 1.6), fmt(-2.2)), stroke=RABC, w=0.7)
    circ(doc, x + side * (r + 1.2), y, r, fill=RABC, stroke='#7a1d12', w=0.35)


def lumen_fill(doc, left_pts, x_left, y0, y1, color):
    dense = cr_sample(left_pts, closed=False, per=10)
    poly = [(x_left, y0)] + dense + [(x_left, y1)]
    path(doc, poly_d(poly, True), fill=color)


def rab_snare(doc):
    x, y, w, h = 25, BY0, 540, BY1 - BY0
    card(doc, x, y, w, h)
    panel_title(doc, x + 4, y + 3, 4, 'Integration: Rab GTPases and SNAREs fuse the membranes', speaker='ENERITZ · 4.1 – 4.3', w=w - 8)
    T(doc, x + 17, y + 22, 'magnified view of the late phagosome (left) docking on a lysosome (right)', size=4.2, italic=True, fill=INK2)
    top, bot = y + 28, y + 100
    mid = (top + bot) / 2
    LUMA, LUMB = '#F9D5CA', '#E4D3F3'
    stages = [(30, 'a'), (162, 'b'), (294, 'c')]
    # ---------------- stage a: tethering
    x0 = 30
    A = [(x0 + 22, top), (x0 + 30, mid), (x0 + 22, bot)]
    B = [(x0 + 98, top), (x0 + 90, mid), (x0 + 98, bot)]
    lumen_fill(doc, A, x0, top, bot, LUMA)
    lumen_fill(doc, B, x0 + 120, top, bot, LUMB)
    mem_draw(doc, A, '#C23B2A')
    mem_draw(doc, B, '#7A3FB5')
    # Rab7 on both membranes
    rab_pin(doc, x0 + 27, top + 12, 1)
    rab_pin(doc, x0 + 30, mid + 22, 1)
    rab_pin(doc, x0 + 93, mid + 22, -1)
    T(doc, x0 + 36, top + 22, 'Rab7-GTP', size=4.0, weight=700, fill=RABC, halo='#fff')
    # RILP -> dynein
    path(doc, 'M%s,%s l8,-1' % (x0 + 33, top + 11), stroke='#2E8B57', w=1.6)
    circ(doc, x0 + 42, top + 10, 2.2, fill='#2E8B57')
    T(doc, x0 + 47, top + 11.4, 'RILP → dynein', size=3.8, weight=700, fill='#2E8B57', halo='#fff')
    # HOPS tether bridging the two Rab7 (purple multi-subunit)
    for k, dx in enumerate((38, 48, 58, 68, 78)):
        circ(doc, x0 + dx + 3, mid + 22 + (0.8 if k % 2 else -0.8), 3.5, fill=HOPSC, stroke='#3E1E70', w=0.4, op=0.95)
    T(doc, x0 + 60, mid + 36, 'HOPS', size=4.2, weight=700, fill=HOPSC, anchor='middle', halo='#fff')
    # SNAREs, not yet paired
    for k, (c, yy, nm) in enumerate(((QA, mid - 12, 'Qa'), (QB, mid - 5, 'Qb'), (QC, mid + 2, 'Qc'))):
        helix(doc, x0 + 31, yy, x0 + 49, yy - 2 * (k - 1), c, amp=0.9, turns=3, w=1.1, phase=k)
        T(doc, x0 + 52, yy - 2 * (k - 1) + 1.3, nm, size=3.4, weight=700, fill=c, halo='#fff')
    helix(doc, x0 + 89, mid - 5, x0 + 71, mid - 5, RS, amp=0.9, turns=3, w=1.1)
    T(doc, x0 + 69, mid - 3.5, 'R', size=3.4, weight=700, fill=RS, anchor='end', halo='#fff')
    T(doc, x0 + 12, bot + 5.5, 'late phagosome', size=3.5, weight=700, fill=DLE, anchor='start')
    T(doc, x0 + 116, bot + 5.5, 'lysosome', size=3.5, weight=700, fill=DLY, anchor='end')
    # ---------------- stage b: trans-SNARE complex
    x0 = 162
    A = [(x0 + 22, top), (x0 + 38, mid - 14), (x0 + 51, mid), (x0 + 38, mid + 14), (x0 + 22, bot)]
    B = [(x0 + 98, top), (x0 + 82, mid - 14), (x0 + 69, mid), (x0 + 82, mid + 14), (x0 + 98, bot)]
    lumen_fill(doc, A, x0, top, bot, LUMA)
    lumen_fill(doc, B, x0 + 120, top, bot, LUMB)
    mem_draw(doc, A, '#C23B2A')
    mem_draw(doc, B, '#7A3FB5')
    ell(doc, x0 + 60, mid, 15, 9.5, fill=HOPSC, op=0.22)
    for k, c in enumerate((QA, QB, QC, RS)):
        helix(doc, x0 + 52, mid + (k - 1.5) * 1.5, x0 + 68, mid + (k - 1.5) * 1.5, c, amp=1.5, turns=2.2, w=1.0, phase=k * 1.57)
    T(doc, x0 + 60, top + 8, 'trans-SNARE complex', size=4.0, weight=700, fill=INK, anchor='middle', halo='#fff')
    leader(doc, [(x0 + 60, top + 11), (x0 + 60, mid - 6)], color=INK2, w=0.4, dot=False)
    T(doc, x0 + 60, mid + 27, 'HOPS proofreads', size=3.9, weight=700, fill=HOPSC, anchor='middle', halo='#fff')
    for xx, yy, s in ((x0 + 33, top + 12, 1), (x0 + 87, top + 12, -1), (x0 + 33, bot - 12, 1), (x0 + 87, bot - 12, -1)):
        rab_pin(doc, xx - 1, yy, s)
    T(doc, x0 + 12, bot + 5.5, 'late phagosome', size=3.5, weight=700, fill=DLE)
    T(doc, x0 + 116, bot + 5.5, 'lysosome', size=3.5, weight=700, fill=DLY, anchor='end')
    # ---------------- stage c: fusion
    x0 = 294
    pts = [(x0 + 10, top), (x0 + 36, top + 3), (x0 + 60, mid - 24), (x0 + 84, top + 3), (x0 + 110, top),
           (x0 + 112, mid), (x0 + 110, bot), (x0 + 84, bot - 3), (x0 + 60, mid + 24), (x0 + 36, bot - 3), (x0 + 10, bot), (x0 + 8, mid)]
    g = doc.lingrad([(0, '#F9D5CA'), (1, '#E4D3F3')], 0, 0, 1, 0)
    path(doc, cr_path(pts, True), fill=g)
    path(doc, cr_path(pts, True), stroke='#8A3A8A', w=3.6)
    path(doc, cr_path(pts, True), stroke='#fff', w=1.2)
    for (dx, dy) in [(88, 14), (98, 36), (80, 40), (74, 26)]:
        enzyme_dot(doc, x0 + dx, top + dy, 1.9)
    for (dx, dy) in [(22, 20), (30, 38), (44, 30), (16, 44), (54, 22)]:
        hplus(doc, x0 + dx, top + dy, 1.1)
    arrow(doc, [(x0 + 90, mid + 14), (x0 + 70, mid + 14), (x0 + 36, mid + 14)], BIO, 'transport', w=1.0, head=5, smooth=False)
    T(doc, x0 + 60, mid - 29 + 5, 'pore', size=3.6, weight=700, fill=INK, anchor='middle', halo=None) if False else None
    T(doc, x0 + 60, bot + 5.5, 'phagolysosome', size=3.7, weight=700, fill=DLY, anchor='middle')
    T(doc, x0 + 60, mid - 4, 'fusion pore', size=4.0, weight=700, fill='#4A2A5A', anchor='middle')
    T(doc, x0 + 60, mid + 2, '(lumens connect)', size=3.5, fill='#4A2A5A', anchor='middle')
    # cis-SNARE bundle lying in the fused membrane
    helix(doc, x0 + 44, top + 3.5, x0 + 62, top + 8, QB, amp=0.8, turns=2, w=0.9)
    # NSF disassembly
    arrow(doc, [(x0 + 40, bot + 10), (x0 + 22, bot + 16)], RECY, 'recycle', w=0.9, head=0) if False else None
    # stage arrows
    for xa in (151, 283):
        arrow(doc, [(xa - 3, mid), (xa + 9, mid)], CONV, 'fusion', w=1.5, head=6, smooth=False)
    # ---------------- captions
    caps = [
        (30, '**a  Tethering.** Rab7-GTP binds RILP (dynein) and **HOPS**, which bridges the two membranes.'),
        (162, '**b  Zippering.** R-SNARE (VAMP7; VAMP8 in some contexts) twists with Qa/Qb/Qc (syntaxin-7, Vti1b, syntaxin-8).'),
        (294, '**c  Fusion.** Bilayers merge, a pore opens; hydrolases and H⁺ mix with the cargo. NSF/α-SNAP then disassemble the SNAREs for reuse.'),
    ]
    for cx, t in caps:
        P(doc, cx, bot + 14, t, 126, size=4.0, lh=1.14, boldfill=NAVY)
    # ---------------- Rab switch
    rx = 430
    rect(doc, rx - 6, y + 26, 135, h - 32, fill='#FAF6EE', stroke='#E6DCC6', sw=0.5, r=4)
    T(doc, rx, y + 35, 'RAB SWITCH', size=4.2, weight=700, fill=NAVY, spacing=0.9)
    # GDP -> GTP cycle
    chip(doc, rx, y + 41, 'Rab·GDP', '#8E96A5', size=4.0, pad=2.6)
    chip(doc, rx + 72, y + 41, 'Rab·GTP', RABC, size=4.0, pad=2.6)
    arrow(doc, [(rx + 36, y + 44), (rx + 70, y + 44)], INK, 'modify', w=0.8, head=4, smooth=False)
    T(doc, rx + 53, y + 41.5, 'GEF', size=3.8, weight=700, fill=INK, anchor='middle')
    arrow(doc, [(rx + 96, y + 52), (rx + 85, y + 58), (rx + 58, y + 58), (rx + 36, y + 52)], INK, 'modify', w=0.8, head=4)
    T(doc, rx + 66, y + 63.5, 'GAP', size=3.8, weight=700, fill=INK, anchor='middle')
    P(doc, rx, y + 70, '**inactive** (cytosol, bound to GDI)', 62, size=3.7, lh=1.1, fill=INK2, boldfill='#6B7380')
    P(doc, rx + 70, y + 70, '**active** (on membrane): recruits effectors: tethers, motors', 62, size=3.7, lh=1.1, fill=INK2, boldfill=RABC)
    # Rab5 -> Rab7 conversion
    line(doc, rx, y + 89, rx + 122, y + 89, '#E6DCC6', 0.5)
    chip(doc, rx, y + 94, 'Rab5-GTP', '#E8892D', size=3.9, pad=2.6)
    chip(doc, rx + 72, y + 94, 'Rab7-GTP', RABC, size=3.9, pad=2.6)
    arrow(doc, [(rx + 37, y + 97), (rx + 70, y + 97)], PHAG, 'transport', w=1.2, head=5, smooth=False)
    T(doc, rx + 53.5, y + 94.4, 'Mon1–Ccz1', size=3.5, weight=700, fill=INK2, anchor='middle')
    P(doc, rx, y + 107, 'Early → late phagosome identity switch (EEA1 and PI(3)P give way to RILP and HOPS).', 124, size=3.7, lh=1.12, fill=INK2)


def killing(doc):
    x, y, w, h = 574, BY0, 240, BY1 - BY0
    card(doc, x, y, w, h)
    panel_title(doc, x + 4, y + 3, 2, 'Killing: two separate systems', speaker='NEREA · 2.5', w=w - 8)
    cw = (w - 20) / 2
    lx, rx = x + 8, x + 12 + cw
    # ---- left: phagolysosome with hydrolases
    chip(doc, lx, y + 23, 'ACID HYDROLASES', CONV, size=4.0, pad=2.8)
    cxl, cyl = lx + 22, y + 50
    g = doc.radgrad([(0, '#F5ECFB'), (1, '#DCC8F0')], cx=.5, cy=.5, r=.6)
    vesicle(doc, cxl, cyl, 17, fill=g, stroke=CONV, w=0.9)
    for (dx, dy) in [(-6, -3), (4, -7), (7, 5), (-3, 8), (-9, 6)]:
        enzyme_dot(doc, cxl + dx, cyl + dy, 2.1)
    for (dx, dy) in [(0, 0), (-8, -8), (8, -1), (1, 10)]:
        hplus(doc, cxl + dx, cyl + dy, 1.0)
    for a in (200, 270, 340, 60, 130):
        px, py = on_circle(cxl, cyl, 17, a)
        vatpase(doc, px, py, a, s=0.55)
    bacterium(doc, cxl + 1, cyl + 1, L=14, W=5.6, rot=-20, lps=False, flagella=False, scale=1.0) if False else None
    ty = y + 73
    for t in ['**V-ATPase** pumps H⁺ in: pH 4.5–5.0',
              '**Cathepsins**, glycosidases, nucleases, lipases',
              'cut protein, sugar, DNA and lipid into **fragments**']:
        hh = P(doc, lx, ty, t, cw - 2, size=4.4, lh=1.14, boldfill=DLY)
        ty += hh + 2.2
    # ---- right: NOX2 oxidative burst
    chip(doc, rx, y + 23, 'OXIDATIVE BURST', INFL, size=4.0, pad=2.8)
    cxr, cyr = rx + 22, y + 50
    vesicle(doc, cxr, cyr, 17, fill='#FBE4EC', stroke='#B03060', w=0.9)
    nox2(doc, cxr, cyr - 17, 90, s=0.95)
    for (dx, dy) in [(-6, -3), (5, -6), (8, 6), (-4, 8), (0, 1)]:
        ros(doc, cxr + dx, cyr + dy, s=0.9)
    arrow(doc, [(cxr + 18, cyr - 19), (cxr + 18, cyr - 10)], INFL, 'modify', w=0.7, head=3.5, smooth=False) if False else None
    ty = y + 73
    for t in ['**NOX2**: electrons from cytosolic NADPH reduce O₂ to O₂•⁻',
              'O₂•⁻ → H₂O₂ (dismutation)',
              '**Complementary** to hydrolysis, a different chemistry']:
        hh = P(doc, rx, ty, t, cw - 2, size=4.4, lh=1.14, boldfill=INFL)
        ty += hh + 2.2
    line(doc, x + w / 2 + 1, y + 24, x + w / 2 + 1, y + 104, '#E6DCC6', 0.6)
    rect(doc, x + 6, y + 108, w - 12, 20, fill='#E3F3F4', stroke='#9CCFD3', sw=0.5, r=3)
    P(doc, x + 10, y + 114, '**Optional route:** peptides → MIIC → MHC II → CD4⁺ T cell (not every fragment).', w - 20, size=4.2, lh=1.14, boldfill='#0B6B72')


def conclusion(doc):
    x, y, w, h = 825, BY0, 250, BY1 - BY0
    rect(doc, x, y, w, h, fill=NAVY, r=5)
    badge(doc, x + 11, y + 11, 6, r=6.6, fill='#F2C94C', fg=NAVY, size=8.2)
    T(doc, x + 22, y + 14.2, 'Conclusion', size=8.6, weight=700, fill='#fff', family=SERIF, kind='serif')
    T(doc, x + w - 6, y + 12.5, 'AITOR', size=3.8, weight=600, fill='#9FB0C6', anchor='end', spacing=0.6)
    hw = (w - 18) / 2
    # clearance
    cx0 = x + 6
    rect(doc, cx0, y + 22, hw, 56, fill='#1E2E42', r=3)
    T(doc, cx0 + hw / 2, y + 31, 'CLEARANCE', size=4.2, weight=700, fill='#8FE3B6', anchor='middle', spacing=0.8)
    bacterium(doc, cx0 + 18, y + 52, L=22, W=9, rot=0, lps=False, flagella=False, scale=1.0)
    arrow(doc, [(cx0 + 33, y + 52), (cx0 + 46, y + 52)], '#E9C0B5', 'transport', w=1.0, head=5, smooth=False)
    circ(doc, cx0 + 60, y + 52, 11, fill='#E4D3F3', stroke=CONV, w=1.3)
    for (dx, dy) in [(-3, -2), (3, 3), (-4, 4)]:
        enzyme_dot(doc, cx0 + 60 + dx, y + 52 + dy, 1.5)
    arrow(doc, [(cx0 + 60, y + 65), (cx0 + 60, y + 73)], '#8FE3B6', 'recycle', w=0.9, head=4, smooth=False)
    T(doc, cx0 + hw / 2, y + 76, 'digested · recycled', size=3.6, fill='#CFE9DA', anchor='middle') if False else None
    T(doc, cx0 + hw - 4, y + 72, '✓', size=10, weight=700, fill='#8FE3B6', anchor='end')
    # persistence
    cx1 = x + 12 + hw
    rect(doc, cx1, y + 22, hw, 56, fill='#2E1F26', r=3)
    T(doc, cx1 + hw / 2, y + 31, 'PERSISTENCE', size=4.2, weight=700, fill='#FF9DB8', anchor='middle', spacing=0.8)
    circ(doc, cx1 + 30, y + 52, 12, fill='#3A2A33', stroke='#B79AB0', w=1.0, dash='2 1.6')
    silica(doc, cx1 + 30, y + 52, s=0.95, rot=10)
    for (dx, dy) in [(52, 40), (62, 49), (56, 60), (47, 55)]:
        ros(doc, cx1 + dx, y + dy + 2, s=0.9) if dx < 60 else cytokine(doc, cx1 + dx, y + dy + 2, s=1.0)
    arrow(doc, [(cx1 + 44, y + 52), (cx1 + 52, y + 52)], '#FF9DB8', 'signal', w=0.9, head=4, smooth=False)
    T(doc, cx1 + hw - 4, y + 72, '✗', size=10, weight=700, fill='#FF9DB8', anchor='end')
    P(doc, x + 8, y + 90, 'Defence needs **coordinated** uptake, vesicular transport, enzyme delivery and degradation. When particles persist, the same machinery turns **protection into injury**.', w - 16, size=5.9, lh=1.2,
      fill='#F1F4F8', boldfill='#F2C94C', family=SERIF, kind='serif')


REFS = [
    'Alberts B et al. Molecular Biology of the Cell, 7th ed. W.W. Norton, 2022.',
    'Alberts B et al. Essential Cell Biology, 5th ed. W.W. Norton, 2019.',
    'Flannagan RS, Jaumouillé V, Grinstein S. The cell biology of phagocytosis. Annu Rev Pathol 2012;7:61-98.',
    'Uribe-Querol E, Rosales C. Phagocytosis: our current understanding of a universal biological process. Front Immunol 2020;11:1066.',
    'Kinchen JM, Ravichandran KS. Phagosome maturation: going through the acid test. Nat Rev Mol Cell Biol 2008;9:781-795.',
    'Haas A. The phagosome: compartment with a license to kill. Traffic 2007;8:311-330.',
    'Braulke T, Bonifacino JS. Sorting of lysosomal proteins. Biochim Biophys Acta 2009;1793:605-614.',
    'Ghosh P, Dahms NM, Kornfeld S. Mannose 6-phosphate receptors: new twists in the tale. Nat Rev Mol Cell Biol 2003;4:202-212.',
    'Luzio JP, Pryor PR, Bright NA. Lysosomes: fusion and function. Nat Rev Mol Cell Biol 2007;8:622-632.',
    'Hutagalung AH, Novick PJ. Role of Rab GTPases in membrane traffic and cell physiology. Physiol Rev 2011;91:119-149.',
    'Langemeyer L, Fröhlich F, Ungermann C. Rab GTPase function in endosome and lysosome biogenesis. Trends Cell Biol 2018;28:957-970.',
    'Jahn R, Scheller RH. SNAREs: engines for membrane fusion. Nat Rev Mol Cell Biol 2006;7:631-643.',
    'Hornung V et al. Silica crystals and aluminum salts activate the NALP3 inflammasome through phagosomal destabilization. Nat Immunol 2008;9:847-856.',
    'Leung CC, Yu ITS, Chen W. Silicosis. Lancet 2012;379:2008-2018.',
    'Donaldson K et al. Asbestos, carbon nanotubes and the pleural mesothelium: long fibre retention, inflammation and mesothelioma. Part Fibre Toxicol 2010;7:5.',
    'Wynn TA, Ramalingam TR. Mechanisms of fibrosis: therapeutic translation for fibrotic disease. Nat Med 2012;18:1028-1040.',
]


def footer(doc):
    y0 = 852
    rect(doc, 0, y0, 1100, 48, fill='#EDE5D3')
    path(doc, 'M0,%s L1100,%s' % (y0, y0), stroke='#D8CDB8', w=0.8)
    T(doc, 25, y0 + 10, 'AUTHORS', size=3.8, weight=700, fill='#8A7A55', spacing=1.0)
    T(doc, 25, y0 + 19, 'Aitor · Nerea · Urtzi · Eneritz · Nora', size=6.2, weight=700, fill=NAVY, family=SERIF, kind='serif')
    T(doc, 25, y0 + 26.5, 'First-year Medicine · Cell Biology seminar', size=4.2, fill=INK2)
    T(doc, 25, y0 + 32.5, '[University / Faculty] · [Academic year]  (placeholders: edit in the SVG)', size=3.6, fill='#8A7A55', italic=True)
    T(doc, 25, y0 + 40, 'Original figure drawn for this seminar; schematic, not to scale.', size=3.5, fill='#8A7A55')
    T(doc, 262, y0 + 10, 'REFERENCES', size=3.8, weight=700, fill='#8A7A55', spacing=1.0)
    cols = 4
    cw = (1075 - 262) / cols
    per = int(math.ceil(len(REFS) / cols))
    for c in range(cols):
        yy = y0 + 15
        for r_ in REFS[c * per:(c + 1) * per]:
            hh = P(doc, 262 + c * cw, yy, r_, cw - 7, size=3.2, lh=1.12, fill='#4A4538')
            yy += hh + 1.3
