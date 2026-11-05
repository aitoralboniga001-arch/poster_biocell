"""Render pipeline: SVG -> PDF (Chrome headless, vector) -> JPEG / preview PNG (PyMuPDF).
usage: python render.py [--final] [--crop x y w h --dpi N --out file.png]
"""
import os, subprocess, sys, argparse
import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'build')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


def svg_to_pdf(svg_path, pdf_path):
    svg = open(svg_path, encoding='utf-8').read()
    if svg.startswith('<?xml'):
        svg = svg.split('?>', 1)[1]
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>@page{size:1100mm 900mm;margin:0}'
            'html,body{margin:0;padding:0;background:#fff}svg{display:block}</style></head><body>%s</body></html>' % svg)
    hp = os.path.join(BUILD, '_poster.html')
    open(hp, 'w', encoding='utf-8').write(html)
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
           '--print-to-pdf=%s' % pdf_path, 'file:///' + hp.replace('\\', '/')]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=300)


def raster(pdf_path, out, dpi=30, crop=None, jpg=False):
    d = fitz.open(pdf_path)
    pg = d[0]
    clip = None
    if crop:
        k = 72 / 25.4 * (pg.rect.width / (1100 / 25.4 * 72))  # mm -> pt
        x, y, w, h = crop
        clip = fitz.Rect(x * k, y * k, (x + w) * k, (y + h) * k)
    pix = pg.get_pixmap(dpi=dpi, clip=clip, alpha=False)
    if jpg:
        pix.save(out, jpg_quality=95)
    else:
        pix.save(out)
    return pix.width, pix.height


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--svg', default=os.path.join(ROOT, 'Macrophage_poster.svg'))
    ap.add_argument('--pdf', default=os.path.join(ROOT, 'Macrophage_poster.pdf'))
    ap.add_argument('--crop', nargs=4, type=float)
    ap.add_argument('--dpi', type=int, default=30)
    ap.add_argument('--out')
    ap.add_argument('--nopdf', action='store_true')
    a = ap.parse_args()
    if not a.nopdf:
        svg_to_pdf(a.svg, a.pdf)
    if a.out:
        print(raster(a.pdf, a.out, a.dpi, a.crop, jpg=a.out.lower().endswith('.jpg')))
