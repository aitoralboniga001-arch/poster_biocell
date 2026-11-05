"""Alveolar-wall profile (poster mm).  Shared by geom, scene and the cell outline (cellmod) without import cycles.

wall_top(x)    epithelial (air-side) surface of the septum the macrophage sits on
surface(x)     the drawn apical surface: wall_top plus a shallow dip under the macrophage base (lining-fluid space)
base_y(x)      where the macrophage's ventral membrane rests (on the lining fluid)
wall_bottom(x) V2b: the organic lower (air-side) edge of that septum: a thin healthy septum whose underside bulges
               over each capillary (left), thickening into a fibrotic mass that runs off the bottom (right)
SEPT_CAPS      the healthy capillaries (cx, rx, ry) that shape the underside; SEPT_GAPS the wider interstitial gaps
"""
import math, random
from lib import cr_sample

WALL_Y = (748, 845)
# V2b: the left end lifts a little toward the page edge, like the rim of the alveolus (x < 140 only)
WALL_TOP_PTS = [(-10, 738), (22, 752.5), (62, 764.5), (104, 769.2), (140, 767.5), (220, 771), (290, 764), (345, 760.8),
                (420, 760.4), (560, 760.5), (700, 760.4), (790, 760.2), (850, 759.2), (920, 757.4), (1005, 755.2),
                (1060, 752.5), (1110, 750)]
WALL_BOT_PTS = [(-10, 822), (80, 826.5), (180, 821), (300, 825.5), (420, 823), (540, 827), (650, 831), (760, 835),
                (860, 839), (960, 842.5), (1040, 844), (1110, 843)]          # legacy (V1 band); see wall_bottom()
HEALTHY_X = 520                     # wall is healthy left of this ...
FIBROTIC_X = 760                    # ... and fully fibrotic right of this (continuous blend between)

_TOP = cr_sample(WALL_TOP_PTS, closed=False, per=24)


def _interp(poly, x):
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * ((x - x0) / ((x1 - x0) or 1e-9))
    return poly[0][1] if x < poly[0][0] else poly[-1][1]


def wall_top(x):
    """y of the epithelial (air-side) surface of the wall at poster x."""
    return _interp(_TOP, x)


def fibrosis(x):
    """0 = healthy, 1 = fibrotic; smooth blend between HEALTHY_X and FIBROTIC_X."""
    t = min(1.0, max(0.0, (x - HEALTHY_X) / (FIBROTIC_X - HEALTHY_X)))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------------------- the cell's footprint on the wall
CELL_FOOT = (212, 978)     # x range where the macrophage base (incl. the cup's lamella) rests on the lining fluid
CELL_BASE_DIP = 1.9        # the drawn epithelium sits this much below wall_top under the cell (thin lining space)
LIN = 1.2                  # lining-fluid thickness


def _smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def dip(x):
    x0, x1 = CELL_FOOT
    return CELL_BASE_DIP * _smooth((x - x0 + 6) / 34) * (1 - _smooth((x - x1 + 4) / 30))


def surface(x):
    return wall_top(x) + dip(x)


def base_y(x):
    """The macrophage's ventral membrane (centre line) rests here, on top of the lining fluid."""
    return surface(x) - LIN - 0.9


# ------------------------------------------------------------------------------- the septum's organic underside
BM_D = 2.7                 # depth of the basement membrane below the apical surface
SEPT_END = 640             # healthy capillary row ends here; the fibrotic mass takes over
FIB0, FIB1 = 540, 828      # thickening ramp: thin septum -> merged fibrotic mass


def _gen_caps():
    """A single row of capillaries just under the basement membrane, each bulging the septum's underside."""
    rnd = random.Random(23)
    caps, gaps = [], []
    x = -26.0
    while True:
        h = _smooth((x - 470) / 170)
        rx = rnd.choice((7.5, 9, 10.5, 12, 13.5, 15.5, 17)) * (1 - 0.3 * h)
        ry = rnd.uniform(4.4, 6.2) * (1 - 0.2 * h)
        cx = x + rx
        if cx > SEPT_END:
            break
        caps.append((round(cx, 2), round(rx, 2), round(ry, 2)))
        gap = rnd.choice((2.2, 3.0, 4.0, 5.5, 8.0, 11.0, 14.0))
        if gap >= 8:
            gaps.append(round(cx + rx + gap / 2, 2))
        x = cx + rx + gap
    return caps, gaps


SEPT_CAPS, SEPT_GAPS = _gen_caps()


def _cap_depth(x):
    """Depth (below surface) of the septum underside imposed by the capillaries, with soft fillets at the sides."""
    best = 0.0
    for cx, rx, ry in SEPT_CAPS:
        R = rx + 1.9
        dx = abs(x - cx)
        if dx > R + 5:
            continue
        cy = BM_D + 0.25 + ry
        if dx <= R:
            d = cy + (ry + 1.9) * math.sqrt(max(0.0, 1 - (dx / R) ** 2))
        else:
            d = cy * (1 - (dx - R) / 5) ** 2
        best = max(best, d)
    return best


def _thin(x):
    """Thin interstitium between capillaries: a little under the two epithelia, gently varying."""
    return 6.4 + 0.9 * math.sin(x / 31.0 + 0.4) + 0.5 * math.sin(x / 12.7 + 2.1)


def _fib_bottom(x):
    return 868 + 3.0 * math.sin(x / 17.0 + 1.0) + 2.0 * math.sin(x / 6.3)


def _depth(x):
    a, b = _thin(x), _cap_depth(x)
    p = 6.0
    th = (a ** p + b ** p) ** (1 / p)            # smooth max: rounded junctions between capillary bulges
    g = _smooth((x - FIB0) / (FIB1 - FIB0)) ** 1.8
    tf = _fib_bottom(x) - surface(x)
    lump = 7.0 * math.sin(x / 10.5 + 0.7) * 4 * g * (1 - g) + 3.0 * math.sin(x / 4.9) * 4 * g * (1 - g)
    return th + (tf - th) * g + lump


_XS0, _DX = -30.0, 0.5
_DEPTH = [_depth(_XS0 + i * _DX) for i in range(int((1140 - _XS0) / _DX) + 1)]


def depth(x):
    """Septum thickness (surface -> lower air-side edge)."""
    f = (x - _XS0) / _DX
    i = int(max(0, min(len(_DEPTH) - 2, math.floor(f))))
    t = min(1.0, max(0.0, f - i))
    return _DEPTH[i] * (1 - t) + _DEPTH[i + 1] * t


def wall_bottom(x):
    """y of the septum's lower (air-side) edge at poster x."""
    return surface(x) + depth(x)
