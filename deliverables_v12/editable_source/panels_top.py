"""Header band: title, speaker route, how-to-read legend."""
from lib import *
from bio import *
from panels_common import *

GOLD = '#F2C94C'


def legend(doc, x, y, w, h):
    rect(doc, x, y, w, h, fill='#FFFFFF', r=5)
    T(doc, x + 8, y + 9.5, 'HOW TO READ THE ARROWS', size=4.2, weight=700, fill=NAVY, spacing=1.0)
    items = [
        ('transport', PHAG, 'Phagocytic pathway'),
        ('transport', BIO, 'Biosynthetic pathway'),
        ('fusion', CONV, 'Membrane fusion'),
        ('recycle', RECY, 'Recycling / reuse'),
        ('modify', INK, 'Maturation, signalling'),
        ('path', PATH, 'Pathological consequence'),
        ('signal', INFL, 'Inflammatory signal'),
        ('transport', '#13848C', 'Antigen route (optional)'),
    ]
    cw = (w - 12) / 2
    for k, (kind, col, t) in enumerate(items):
        cx = x + 8 + (k // 4) * cw
        cy = y + 22 + (k % 4) * 15.5
        ww = 1.5 if kind != 'path' else 1.4
        arrow(doc, [(cx, cy), (cx + 20, cy)], col, kind, w=ww, head=(5.5 if kind != 'path' else 6), smooth=False)
        T(doc, cx + 25, cy + 1.6, t, size=4.4, weight=600, fill=INK)


def header(doc):
    rect(doc, 0, 0, 1100, 98, fill=NAVY)
    # decorative thin lines
    path(doc, 'M0,98 L1100,98', stroke=GOLD, w=1.2)
    T(doc, 30, 20, 'CELL BIOLOGY SEMINAR  ·  FIRST-YEAR MEDICINE', size=4.8, weight=700, fill=GOLD, spacing=1.8)
    T(doc, 30, 55, 'How a macrophage destroys what it engulfs', size=29, weight=700, fill='#FFFFFF', family=SERIF, kind='serif')
    T(doc, 30, 71, 'Phagocytosis, lysosomal biogenesis and vesicular trafficking — and what happens when the cargo cannot be cleared', size=7.4, fill='#CFD8E4')
    # speaker route
    route = [('1', 'Aitor', 'Introduction'), ('2', 'Nerea', 'Phagocytosis'), ('3', 'Urtzi', 'Lysosomal biogenesis'),
             ('4', 'Eneritz', 'Integration'), ('5', 'Nora', 'Pathology'), ('6', 'Aitor', 'Conclusion')]
    x = 30
    y = 80
    for n, who, what in route:
        circ(doc, x + 5.2, y + 5.2, 5.2, fill=GOLD)
        T(doc, x + 5.2, y + 8.4, n, size=6.4, weight=700, fill=NAVY, anchor='middle')
        label = '%s · %s' % (who, what)
        T(doc, x + 13, y + 7.6, label, size=4.8, weight=600, fill='#E8EEF5')
        x += 13 + text_width(label, 4.8, 600) + 9
        if n != '6':
            path(doc, 'M%s,%s l3,0 l-1.8,-1.8 M%s,%s l1.8,1.8' % (x - 7.5, y + 5.2, x - 4.5, y + 5.2), stroke='#6F7F95', w=0.7)
    legend(doc, 770, 9, 305, 80)
