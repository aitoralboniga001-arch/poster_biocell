"""V2 layout contract (poster mm, 1100 x 900, y down).  ONE giant mixed-scale macrophage fills the scene; there are
no side panels and no windows.  Molecular detail is drawn IN the cell, at the spot where it happens, by the zone owners.
Every owner must respect these numbers; change them only through the integrator."""

# ------------------------------------------------------------------------------------------------ page furniture
TITLE_BOX = (30, 18, 780, 100)           # hand-lettered title
HEADER_RIGHT = (790, 18, 1078, 100)      # course line, speaking order, arrow key
LOCATOR = (22, 108, 215, 240)            # 1  lung -> alveolus -> "this scene" sketch, in the air (top-left notch)
CONCL_Y = 857                            # 6  conclusion baseline
REFS = (25, 866, 1075, 897)              # references block

# ------------------------------------------------------------------------------------------------ the cell
# Silhouette (drawn by the skeleton owner): an amoeboid dome, NOT a rounded rectangle.
#   leftmost pseudopod tips ~x 40, body left edge ~x 140-200; dome peak ~ (430, 120) over the nucleus; shallow saddle
#   ~ (640, 150); right lobe ~ (860, 128); round right shoulder; right flank ~x 1000-1008; base sits on wall_top(x)
#   from ~x 210 to ~x 990; open frustrated-phagocytosis cup at the right base around the asbestos fibre.
#   Air must stay visible: left strip x < ~60 (outside the bacterium), right strip x > ~1010, and the top-left notch.
CELL_RIGHT_X = 1006                      # nominal right flank
CELL_TOP_Y = 118                         # dome peak

# Membrane segments that are drawn at MOLECULAR scale by a zone owner.  The skeleton outline must pass exactly along
# these polylines (cytosol on the stated side); the zone owner over-draws a thicker bilayer here with tapered ends.
LEAD_MEM = [(150, 290), (142, 330), (138, 392), (142, 454), (150, 494)]       # cytosol to the RIGHT (zone A)
RIGHT_MEM = [(1003, 540), (1007, 590), (1006, 640), (1001, 690)]              # cytosol to the LEFT  (zone F)

# ------------------------------------------------------------------------------------------------ zones
# Zone A  2 Recognition (owner: recognition).  Bacterium caught at the leading edge; receptors bridge the gap to
# LEAD_MEM; signalling + Arp2/3 actin inside; two thin pseudopod arms wrap the bacterium's ends (tips ~x 40).
ZONE_A = (22, 250, 335, 530)
BACT = (60, 392, 36, 92)                 # rod: centre x, centre y, radius, half-length (vertical axis, x 24-96)

# Zone B  phagosome maturation chain (owner: skeleton) - organelle scale, red route.
NASCENT = (295, 575, 38)                 # 2.3  (cx, cy, r)
EARLY = (372, 648, 42)                   # 2.4  pH 6.5, Rab5
LATE = (470, 680, 45)                    # 2.5  pH 5.5, Rab7

# Zone C  nucleus (owner: skeleton)
NUCLEUS = (440, 255, 112, 92)            # cx, cy, rx, ry

# Zone D  3 Lysosome biogenesis (owner: enzyme route).  A descending staircase of ENLARGED organelle segments, each a
# closed, rounded sac (not an open strip): top-right -> down-left, so the enzyme route falls toward the phagolysosome.
BANDS = {                                # x0, y0, x1, y1
    '3.1 ER':        (750, 150, 970, 192),
    '3.2 cis-Golgi': (705, 212, 925, 254),
    '3.3 TGN':       (660, 274, 880, 334),      # includes the clathrin bud (3.4) hanging below the band
    '3.5 LE':        (615, 354, 835, 396),
    '3.6 Lysosome':  (570, 416, 790, 458),
}
ZONE_D = (560, 130, 990, 470)

# Zone E  4 Fusion + 2.7 Killing (owner: fusion/killing).  Lysosomes dock on LATE (upper-right arc) showing tether ->
# zipper -> pore -> recycle around it; the giant phagolysosome is where both routes meet (the V's point).
PHAGOLYSOSOME = (600, 668, 68)           # 2.6
ZONE_E = (420, 560, 700, 752)

# Zone F  5 Silica / NLRP3 (owner: particles).  Silica phagolysosome, cathepsin B leak, NLRP3 inflammasome,
# caspase-1, IL-1b/IL-18, GSDMD pores IN RIGHT_MEM, K+ efflux to the right air.
SILICA_PL = (850, 560, 48)
ZONE_F = (760, 478, 1008, 715)

# Zone G  asbestos (owner: particles).  Fibre lies on the epithelium; its near end sits in the open cup at the cell's
# right base; it runs off the right edge (too long to engulf).  Lips never meet.
ASB_FIBRE = ((905.0, 746.0), (1112.0, 750.0))
ASB_FIBRE_W = 4.4

# Air strips (owner: particles for the right one): inhaled particles, possible outcomes (dashed), released IL-1b.
AIR_RIGHT = (1010, 104, 1098, 742)

# Route ribbons (owner: skeleton): soft painted bands under the cytoplasm content.
RED_ROUTE = [(120, 392), (230, 470), (295, 575), (372, 648), (470, 680), (600, 668)]
BLUE_ROUTE = [(860, 171), (815, 233), (770, 304), (725, 375), (680, 437), (640, 560), (600, 668)]

# Section marks: hand-lettered number + name, placed by each zone owner near (ideally in the air beside) its zone,
# with marks.section(doc, x, y, num, name, color).
