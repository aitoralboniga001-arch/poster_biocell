"""Lung parenchyma beneath the septum (V2b wall owner): the next alveoli seen in depth.

A Voronoi foam of air spaces, each shrunk by half the septal thickness and rounded (Chaikin), gives the lacy
alveolar septa.  Toward the fibrotic right the septa thicken and the spaces collapse into slits and vanish.
Pure geometry here; scene.py paints it."""
import math, random
import numpy as np
from scipy.spatial import Voronoi


def _smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def _clip_half(poly, a, n, d):
    """Keep the part of poly where dot(p - a, n) >= d (Sutherland-Hodgman against one half-plane)."""
    out = []
    m = len(poly)
    for i in range(m):
        p, q = poly[i], poly[(i + 1) % m]
        fp = (p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1] - d
        fq = (q[0] - a[0]) * n[0] + (q[1] - a[1]) * n[1] - d
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def inset(poly, d):
    """Shrink a convex polygon by distance d (offset every edge inward)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = list(poly)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ex, ey) or 1e-9
        n = (-ey / L, ex / L)
        if (cx - a[0]) * n[0] + (cy - a[1]) * n[1] < 0:
            n = (-n[0], -n[1])
        out = _clip_half(out, a, n, d)
        if len(out) < 3:
            return []
    return out


def chaikin(poly, it=3, r=0.25):
    for _ in range(it):
        out = []
        m = len(poly)
        for i in range(m):
            p, q = poly[i], poly[(i + 1) % m]
            out.append((p[0] + (q[0] - p[0]) * r, p[1] + (q[1] - p[1]) * r))
            out.append((p[0] + (q[0] - p[0]) * (1 - r), p[1] + (q[1] - p[1]) * (1 - r)))
        poly = out
    return poly


def area(poly):
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                         for i in range(len(poly))))


def seeds(x0, x1, y0, y1, sp_fn, rowh, rnd, jit=0.3):
    pts = []
    y, row = y0, 0
    while y <= y1:
        x = x0 + (rnd.uniform(0, 0.5) if row % 2 else 0.5) * sp_fn(x0)
        while x <= x1:
            s = sp_fn(x)
            pts.append((x + rnd.uniform(-jit, jit) * s, y + rnd.uniform(-jit, jit) * rowh))
            x += s * rnd.uniform(0.85, 1.15)
        y += rowh
        row += 1
    return pts


def foam(pts, half_wall_fn, collapse_fn, keep_fn, rnd, wobble=0.6):
    """-> (holes, ridges).  holes: rounded air-space polygons; ridges: (mid, angle, length, x) of the shared walls."""
    P = np.array(pts)
    xmin, ymin = P.min(0) - 400
    xmax, ymax = P.max(0) + 400
    dummy = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), ((xmin + xmax) / 2, ymin), ((xmin + xmax) / 2, ymax),
             (xmin, (ymin + ymax) / 2), (xmax, (ymin + ymax) / 2)]
    vor = Voronoi(np.vstack([P, np.array(dummy)]))
    V = vor.vertices
    holes = []
    for i, (sx, sy) in enumerate(pts):
        reg = vor.regions[vor.point_region[i]]
        if not reg or -1 in reg:
            continue
        poly = [tuple(V[k]) for k in reg]
        if not keep_fn(sx, sy):
            continue
        hw = half_wall_fn(sx, sy)
        poly = inset(poly, hw)
        if len(poly) < 3:
            continue
        c = collapse_fn(sx, sy)                    # 0 open .. 1 gone
        if c >= 0.97:
            continue
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        k = 1 - 0.78 * c
        ky = k * (1 - 0.55 * c)                    # collapsing spaces flatten into slits
        poly = [(cx + (x - cx) * k, cy + (y - cy) * ky) for x, y in poly]
        poly = [(x + rnd.uniform(-wobble, wobble), y + rnd.uniform(-wobble, wobble)) for x, y in poly]
        poly = chaikin(poly, 3, 0.25)
        if area(poly) < 6:
            continue
        holes.append(dict(poly=poly, c=(cx, cy), collapse=c, seed=i))
    ridges = []
    for (i, j), rv in zip(vor.ridge_points, vor.ridge_vertices):
        if i >= len(pts) or j >= len(pts) or -1 in rv:
            continue
        a, b = V[rv[0]], V[rv[1]]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 4:
            continue
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ridges.append(((mx, my), math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), L, a, b))
    return holes, ridges
