"""Composition anchors (poster mm, sheet 1100 x 900), V2.

V2 re-exports the layout contract (geom_v2) and keeps every V1 name importable, re-pointed at the new positions where
that makes sense (NASCENT_23, LATE_25, PHAGOLYSOSOME_26, NUCLEUS_C, ...).  The V1 column grid (LEFT_COL, RECOG, ...)
is kept only so that the V1 modules still import; it no longer describes the layout.
Circles are (x, y, r); regions are (x0, y0, x1, y1).  The cell has no transform in V2 (S = 1, T = (0, 0)).
"""
import math
from geom_v2 import *                      # noqa: F401,F403  (the V2 contract)
import geom_v2 as _V
from wallgeom import (WALL_Y, WALL_TOP_PTS, WALL_BOT_PTS, HEALTHY_X, FIBROTIC_X, wall_top, wall_bottom, fibrosis,
                      surface, base_y, dip, CELL_FOOT)

S = 1.0
T = (0.0, 0.0)


def to_poster(x, y):
    return x, y


def to_cell(x, y):
    return x, y


# ===================================================================== sheet grid (V1 names, kept for imports)
SHEET = (0, 0, 1100, 900)
HEADER = (0, 0, 1100, 104)

LEFT_COL = (25, 92, 262, 745)
INTRO = _V.LOCATOR
RECOG = _V.ZONE_A
FUSION = _V.ZONE_E
KILL = _V.ZONE_E
RIGHT_COL = (1010, 104, 1098, 742)
M6P = _V.ZONE_D
PATHO = _V.ZONE_F
CELL_BOX = (22, 104, 1010, 770)

INTRO_HEAD_Y = 110
RECOG_HEAD_Y = 254
FUSION_HEAD_Y = 508
KILL_HEAD_Y = 638
M6P_HEAD_Y = 110
PATHO_HEAD_Y = 358

INTRO_CUE_AREA = _V.LOCATOR
RECOG_AREA = _V.ZONE_A
FUSION_AREA = _V.ZONE_E
KILL_AREA = _V.ZONE_E
M6P_AREA = _V.ZONE_D
PATHO_AREA = _V.ZONE_F
PATHO_WALL_LABELS = (880, 762, 1078, 842)    # 5.4 / 5.5 labels on the fibrotic wall (particles owner places them)

CONCL_Y = _V.CONCL_Y
REFS_Y = 867                        # top of the references block (y 867-897)

# ===================================================================== the cell (poster mm)
import cellmod as _cm                # noqa: E402  (cellmod does not import geom: no cycle)

CELL_OUTLINE = list(_cm.OUT)          # dense outline polygon of the plasma membrane (clockwise on screen)
CELL_D = _cm.CELL_D                   # the same as an SVG path
_xs = [p[0] for p in CELL_OUTLINE]
_ys = [p[1] for p in CELL_OUTLINE]
CELL_BOUNDS = (min(_xs), min(_ys), max(_xs), max(_ys))
CELL_BASE_Y = base_y(600)            # the base rests on the lining fluid here (it follows base_y(x))
LEAD_MEM_DENSE = _cm.segment('lead')   # the exact dense run of the outline along LEAD_MEM (bottom -> top)
RIGHT_MEM_DENSE = _cm.segment('right')  # ... along RIGHT_MEM (top -> bottom)


def inside_cell(x, y):
    from style import inside
    return inside(CELL_OUTLINE, x, y)


def _on(c, ang, dr=0.0):
    a = math.radians(ang)
    return c[0] + (c[2] + dr) * math.cos(a), c[1] + (c[2] + dr) * math.sin(a)


def _band_c(name):
    x0, y0, x1, y1 = _V.BANDS[name]
    return (x0 + x1) / 2, (y0 + y1) / 2


# --- section 2: phagocytic route
CONTACT_21 = _V.LEAD_MEM[2]                  # 2.1 contact site (middle of the leading edge; extracellular side = left)
NASCENT_23 = _V.NASCENT
EARLY_24 = _V.EARLY
LATE_25 = _V.LATE
PHAGOLYSOSOME_26 = _V.PHAGOLYSOSOME
EARLY_ENDOSOMES = [(362, 522, 9), (408, 590, 8)]
MATURATION_PATH = [NASCENT_23, EARLY_24, LATE_25, PHAGOLYSOSOME_26]
LATE_DOCK_ARC = (-100, 15)                   # upper-right arc of LATE left free for the docking lysosomes (deg, y down)

# --- section 4: fusion
FUSION_4 = _on(_V.LATE, -45) + (15,)         # docking site on the late phagosome's upper-right arc
LYSO_DOCKING = _on(_V.LATE, -45, 16) + (13,)
LYSO_DELIVER = (_V.PHAGOLYSOSOME[0] + 40, _V.PHAGOLYSOSOME[1] - 74, 13)

# --- section 3: biosynthetic route (the zone-D staircase)
NUCLEUS_C = _V.NUCLEUS[:2]
import cellmod2 as _c2               # noqa: E402
ER_SHEETS = _c2.ER_SHEETS                    # rough ER sheet centrelines leaving the envelope (top -> bottom)
ER_31 = _band_c('3.1 ER')
COPII_VESICLES = [(_V.BANDS['3.1 ER'][0] - 8, 200), (_V.BANDS['3.2 cis-Golgi'][0] - 8, 262)]
GOLGI_32 = _band_c('3.2 cis-Golgi')
TGN_33 = _band_c('3.3 TGN')
CCV_34 = [(_band_c('3.3 TGN')[0] - 30, _V.BANDS['3.3 TGN'][3] + 4), (_band_c('3.3 TGN')[0] + 30, _V.BANDS['3.3 TGN'][3] + 4)]
LATE_ENDOSOME_35 = _band_c('3.5 LE') + (21,)
LYSOSOME_36 = _band_c('3.6 Lysosome') + (21,)
CENTROSOME = _c2.CENTRO

# --- section 5: particles
SILICA_PL = _V.SILICA_PL
NLRP3_SITE = _c2.NLRP
ASB_FIBRE = _V.ASB_FIBRE
ASB_FIBRE_W = _V.ASB_FIBRE_W
CUP_UPPER_LIP = _cm.CUP_UPPER_LIP            # outer hood surface (flank -> hood tip)
CUP_POCKET = _cm.CUP_POCKET                  # inner (extracellular) surface of the open cup: roof -> back -> floor
CUP_LOWER_LIP = _cm.CUP_LOWER_LIP
CUP_UPPER_TIP = _cm.HOOD_TIP
CUP_LOWER_TIP = _cm.LAMELLA_TIP
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
