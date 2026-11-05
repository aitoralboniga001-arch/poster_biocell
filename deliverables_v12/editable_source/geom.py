"""V1.2 composition grid and anchors (poster mm, sheet 1100 x 900).  READ-ONLY in phase 2.

Regions are (x0, y0, x1, y1).  Circles are (x, y, r).  Every cell anchor is read from the cell code (cellmod*.py) and
converted from cell coordinates to poster mm with cellmod.to_poster, so the numbers live in one place only.
"""
import math
from lib import cr_sample
import cellmod as _cm
import cellmod2 as _c2

S = _cm.CELL_S                      # cell drawing scale (cell group transform: poster = S * cell + T)
T = _cm.CELL_T
to_poster = _cm.to_poster
to_cell = _cm.to_cell


def _p(pt):
    return to_poster(pt[0], pt[1])


def _c(c):
    x, y = to_poster(c[0], c[1])
    return (x, y, c[2] * S)


# ===================================================================== sheet grid
SHEET = (0, 0, 1100, 900)
HEADER = (0, 0, 1100, 84)

LEFT_COL = (25, 92, 262, 745)
INTRO = (25, 96, 262, 232)          # 1  intro text + scale cue
RECOG = (25, 240, 262, 480)         # 2  recognition + actin window
FUSION = (25, 495, 262, 610)        # 4  fusion strip
KILL = (25, 625, 262, 745)          # 2.7 maturation + killing strip

RIGHT_COL = (872, 92, 1078, 750)
M6P = (872, 96, 1078, 335)          # 3  hydrolase-journey strip
PATHO = (872, 345, 1078, 750)       # 5  particles

CELL_BOX = (265, 92, 860, 770)      # nominal box for the macrophage

# heading baselines and the drawing area each module owns (below its heading + caption)
INTRO_HEAD_Y = 110
RECOG_HEAD_Y = 254
FUSION_HEAD_Y = 508
KILL_HEAD_Y = 638
M6P_HEAD_Y = 110
PATHO_HEAD_Y = 358

INTRO_CUE_AREA = (25, 150, 262, 232)
RECOG_AREA = (25, 284, 262, 480)
FUSION_AREA = (25, 538, 262, 612)
KILL_AREA = (25, 668, 262, 746)
M6P_AREA = (872, 146, 1078, 335)
PATHO_AREA = (872, 396, 1078, 716)
PATHO_WALL_LABELS = (880, 762, 1078, 842)    # 5.4 / 5.5 labels on the fibrotic wall (and just above it)

# ===================================================================== alveolar wall (full width)
WALL_Y = (748, 845)
WALL_TOP_PTS = [(-10, 769), (60, 773), (140, 767.5), (220, 771), (290, 764), (345, 760.8), (420, 760.4), (560, 760.5),
                (700, 760.4), (790, 760.2), (850, 759.2), (920, 757.4), (1005, 755.2), (1060, 752.5), (1110, 750)]
WALL_BOT_PTS = [(-10, 822), (80, 826.5), (180, 821), (300, 825.5), (420, 823), (540, 827), (650, 831), (760, 835),
                (860, 839), (960, 842.5), (1040, 844), (1110, 843)]
HEALTHY_X = 520                     # wall is healthy left of this ...
FIBROTIC_X = 760                    # ... and fully fibrotic right of this (continuous blend between)

_TOP = cr_sample(WALL_TOP_PTS, closed=False, per=24)
_BOT = cr_sample(WALL_BOT_PTS, closed=False, per=24)


def _interp(poly, x):
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * ((x - x0) / ((x1 - x0) or 1e-9))
    return poly[0][1] if x < poly[0][0] else poly[-1][1]


def wall_top(x):
    """y of the epithelial (air-side) surface of the wall at poster x."""
    return _interp(_TOP, x)


def wall_bottom(x):
    """y of the lower edge of the wall band at poster x."""
    return _interp(_BOT, x)


def fibrosis(x):
    """0 = healthy, 1 = fibrotic; smooth blend between HEALTHY_X and FIBROTIC_X."""
    t = min(1.0, max(0.0, (x - HEALTHY_X) / (FIBROTIC_X - HEALTHY_X)))
    return t * t * (3 - 2 * t)


CONCL_Y = 857                       # baseline of the conclusion sentence (6)
REFS_Y = 867                        # top of the references block (y 867-897)

# ===================================================================== the cell (poster mm)
CELL_OUTLINE = [to_poster(x, y) for (x, y) in _cm.OUT]       # dense outline polygon of the plasma membrane
_xs = [p[0] for p in CELL_OUTLINE]
_ys = [p[1] for p in CELL_OUTLINE]
CELL_BOUNDS = (min(_xs), min(_ys), max(_xs), max(_ys))
CELL_BASE_Y = max(_ys)              # the flattened base rests on the epithelium here

# --- section 2: phagocytic route
CONTACT_21 = _p(_c2.CONTACT)                 # 2.1 contact site: receptors meet the opsonised bacterium (left cell edge;
                                             #     membrane is vertical here, extracellular side = left)
NASCENT_23 = _c(_c2.NP)                      # 2.3 nascent phagosome (x, y, r)
EARLY_24 = _c(_c2.EP)                        # 2.4 early phagosome
LATE_25 = _c(_c2.LP)                         # 2.5 late phagosome
PHAGOLYSOSOME_26 = _c(_c2.PL)                # 2.6 phagolysosome
EARLY_ENDOSOMES = [_c(_c2.EE1), _c(_c2.EE2)]
MATURATION_PATH = [NASCENT_23, EARLY_24, LATE_25, PHAGOLYSOSOME_26]   # source of the 2.7 strip

# --- section 4: fusion
FUSION_4 = _c(_c2.FUSION_4)                  # docking of lysosome L1 on the late phagosome (source ring for the strip)
LYSO_DOCKING = _c(_c2.L1)                    # lysosome docking on the late phagosome
LYSO_DELIVER = _c(_c2.L2)                    # lysosome delivering to the phagolysosome

# --- section 3: biosynthetic route
NUCLEUS_C = _p(_c2.NUC_C)
ER_SHEETS = [[_p(q) for q in sheet] for sheet in _c2.ER_SHEETS]     # rough ER sheet centrelines (top -> bottom)
ER_31 = _p((715, 252))                        # 3.1 rough ER (centre of the sheet stack)
COPII_VESICLES = [_p(q) for q in _c2.COPII_V]
GOLGI_32 = _p(_c2.GOLGI_C)                    # 3.2 Golgi stack centre (cis face on top)
TGN_33 = _p((_c2.GOLGI_C[0], _c2.TGN_Y))      # 3.3 trans-Golgi network
CCV_34 = [_p(q) for q in _c2.CCV]             # 3.4 clathrin / AP-1 / GGA vesicles
LATE_ENDOSOME_35 = _c(_c2.LE)                 # 3.5 late endosome (hydrolase released, M6PR returns)
LYSOSOME_36 = LYSO_DELIVER                    # 3.6 lysosome
CENTROSOME = _p(_c2.CENTRO)

# --- section 5: particles
SILICA_PL = _c(_c2.SPL)                       # 5.3 silica-loaded, damaged phagolysosome
NLRP3_SITE = _p(_c2.NLRP)                     # in-cell NLRP3 inflammasome
ASB_FIBRE = _cm.ASB_FIBRE_POSTER              # 5.2 fibre ((x near end, y), (x far end, y)); near end inside the open cup
ASB_FIBRE_W = _cm.ASB_FIBRE_W
CUP_POCKET = _cm.CUP_POCKET                   # inner (extracellular) surface of the open cup, upper lip -> lower lip
CUP_UPPER_TIP = _cm.CUP_UPPER_LIP[-2]
CUP_LOWER_TIP = _cm.CUP_LOWER_LIP[1]
CUP_MOUTH = ((CUP_UPPER_TIP[0] + CUP_LOWER_TIP[0]) / 2, (CUP_UPPER_TIP[1] + CUP_LOWER_TIP[1]) / 2)


def fibre_point(t):
    """Point on the fibre axis, t = 0 (near end, in the cup) .. 1 (far end, on the epithelium)."""
    (x0, y0), (x1, y1) = ASB_FIBRE
    return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t


# ===================================================================== molecule identity colours (whole poster)
MOL = {
    'IgG': '#3E5C86', 'FcgR': '#3E5C86',
    'iC3b': '#1F8F8A', 'CR3': '#1F8F8A',
    'MR': '#8F5A2A',
    'TLR4': '#8E3B8F', 'MD2': '#8E3B8F', 'LPS': '#8E3B8F', 'CD14': '#8E3B8F',
    'MARCO': '#B4690E',
    'actin': '#E07B39', 'Arp23': '#E07B39',
    'Rab5': '#E3A21A', 'Rab7': '#C0392B',
    'HOPS': '#7A3FB5',
    'Qa_syntaxin7': '#2E86AB', 'Qb_Vti1b': '#3FA796', 'Qc_syntaxin8': '#8BAF3A', 'R_VAMP7': '#E07A5F',
    'VATPase': '#E75A8B', 'Hplus': '#19B5E8',
    'NOX2': '#C81D63',
    'M6P': '#E2B33C', 'M6PR': '#1E8A5A',
    'clathrin': '#6B7C93',
    'hydrolase': '#1F58C8',
}
