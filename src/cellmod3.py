"""V2 skeleton: cortex details drawn over the interior (actin in the hood / lamella / arms / protrusions, route flow
marks) and finally the plasma-membrane line.  The V1 vignettes (silica, asbestos, short fibre, contact receptors,
pathway arrows) moved to the zone owners."""
import math, random
from lib import *
from bio import *
from cellmod import *
from cellmod2 import *


def _interp_y(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if min(x0, x1) <= x <= max(x0, x1):
            return y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1e-9)
    return pts[-1][1]


def cup_actin(doc):
    """Frustrated phagocytosis: a thick Arp2/3 actin hood over the fibre, a thin cortical lamella under it."""
    hood = run_between((993, 715), (906, 740.6))           # hood surface -> tip -> roof
    floor = run_between((893, 749), (972, 754.4))           # pocket floor -> lamella tip
    actin_network(doc, hood, depth=12.0, step=2.0, seed=12, w=0.42, op=0.85, wash=0.10)
    cortex_mesh(doc, floor, depth=2.6, step=1.1, seed=13, w=0.3, op=0.7)


def arm_actin(doc):
    """Quiet cortex in both pseudopod arms (zone A draws the dense Arp2/3 network at the leading edge itself)."""
    lower = run_between((178, 556), (147, 501))
    upper = run_between((150, 283), (170, 247))
    cortex_mesh(doc, lower, depth=4.5, seed=17, op=0.55)
    cortex_mesh(doc, upper, depth=4.5, seed=18, op=0.55)


def draw_extras(doc):
    cup_actin(doc)
    arm_actin(doc)
    protrusion_actin(doc)
    membrane_line(doc)
