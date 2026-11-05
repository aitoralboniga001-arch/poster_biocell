"""Assets for The Living Poster v3: the poster cut into a still plate + moving actors, all from the generator.

python src/build_v3_assets.py            -> Living_poster_v3/assets/*, Living_poster_v3/data/manifest.js

  plate.jpg            plate (poster minus the cut-out actors) at 100 dpi, the overview layer
  plate_blur.jpg       the same, blurred (depth of field outside the focus)
  tile_r_c_ij.webp     plate tiles at 250 dpi, 4 x 4 grid split 2 x 2 (loaded only when the camera is close)
  lo/, mid/            1/4 and 1/2 size copies of the actor/region/state images (level of detail)
  actor_<id>.webp      each cut-out actor alone, transparent, 300 dpi, cropped to its bbox
  state_<id>_<k>.webp  alternative states of multi-state actors (cut-outs: transparent; regions: opaque crops)
  check_*.png          rest-state composite vs poster diff (debug)
Rendering goes SVG -> vector PDF (Chrome, cached by content hash) -> raster (PyMuPDF), as the print master does.
"""
import os, sys, json, time, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image, ImageFilter
import lib
import build_poster
from build_living_assets import svg_to_pdf, pdf_clip_to_pil, refine_actor_bbox, safe_name

OUT = os.path.join(ROOT, 'Living_poster_v3', 'assets')
DATA = os.path.join(ROOT, 'Living_poster_v3', 'data')
TILE_DPI, ACTOR_DPI, REGION_DPI = 250, 300, 250
GRID = 4

# region actors (skip_in_plate=False) are whole-poster rebuilds in another state, cropped to the region
REGION_STATES = {
    'pseudopod_arms': [0, 2, 3],      # rest 1
    'asbestos_hood': [0, 2],          # rest 1
    'fibrosis_wall': [0, 1, 2, 4],    # rest 3
    'alveolar_lumen': [1],            # rest 0
}
# multi-state cut-outs: (module that draws them, states other than rest)
CUTOUT_STATES = {
    'fusion_pore': ('m_vesicles', [0, 1]),
    'bacterium_pl': ('m_vesicles', [0, 1, 3]),
    'silica_membrane': ('m_patho', [0, 2]),
    'nlrp3': ('m_patho', [0, 1]),
}


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='lp3_')
    jobs = []

    print('1. plate document')
    doc = build_poster.build(mode='plate')
    poster_svg, plate_svg = doc.render_poster(), doc.render('plate')
    poster_pdf, plate_pdf = os.path.join(tmp, 'poster.pdf'), os.path.join(tmp, 'plate.pdf')
    jobs += [(poster_svg, False, poster_pdf), (plate_svg, False, plate_pdf)]

    actor_pdfs = {}
    for aid, info in doc.actors.items():
        if info.get('skip_in_plate', True):
            p = os.path.join(tmp, 'a_%s.pdf' % safe_name(aid))
            actor_pdfs[aid] = p
            jobs.append((doc.render_actor(aid), True, p))

    print('2. state documents')
    region_pdfs = {}
    for aid, states in REGION_STATES.items():
        for st in states:
            d = build_poster.build(mode='plate', state_overrides={aid: st})
            p = os.path.join(tmp, 'r_%s_%d.pdf' % (aid, st))
            region_pdfs[(aid, st)] = p
            jobs.append((d.render('region'), False, p))
    import importlib
    cut_pdfs = {}
    for aid, (modname, states) in CUTOUT_STATES.items():
        mod = importlib.import_module(modname)
        for st in states:
            d = lib.Doc(1100, 900, mode='plate', state_overrides={aid: st})
            mod.draw(d)
            p = os.path.join(tmp, 'c_%s_%d.pdf' % (safe_name(aid), st))
            cut_pdfs[(aid, st)] = p
            jobs.append((d.render_actor(aid), True, p))

    print('3. rendering %d documents' % len(jobs))
    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(lambda j: svg_to_pdf(j[0], j[2], transparent=j[1]), jobs))

    print('4. plate, blur, tiles')
    plate = pdf_clip_to_pil(plate_pdf, dpi=100, alpha=False)
    plate.save(os.path.join(OUT, 'plate.jpg'), quality=90)
    # blurred plate: only ever shown soft, so a small file (keeps the GPU decode cache free for the sharp layers)
    pb = plate.filter(ImageFilter.GaussianBlur(4))
    pb.resize((round(pb.width / 4), round(pb.height / 4)), Image.LANCZOS).save(os.path.join(OUT, 'plate_blur.jpg'), quality=82)
    poster100 = pdf_clip_to_pil(poster_pdf, dpi=100, alpha=False)
    poster100.save(os.path.join(OUT, 'poster.jpg'), quality=90)
    tiles = []
    tw, th = 1100 / GRID, 900 / GRID
    for r in range(GRID):
        for c in range(GRID):
            bb = [round(c * tw, 3), round(r * th, 3), round(tw, 3), round(th, 3)]
            im = pdf_clip_to_pil(plate_pdf, dpi=TILE_DPI, bbox_mm=bb, alpha=False)
            # split each cell 2 x 2: small tiles decode fast and only the visible ones are attached
            hw, hh = im.width // 2, im.height // 2
            for rr in range(2):
                for cc in range(2):
                    sub = im.crop((cc * hw, rr * hh, im.width if cc else hw, im.height if rr else hh))
                    f = 'tile_%d_%d_%d%d.webp' % (r, c, rr, cc)
                    sub.save(os.path.join(OUT, f), quality=88)
                    tiles.append({'file': 'assets/' + f, 'bbox': [round(bb[0] + cc * bb[2] / 2, 3), round(bb[1] + rr * bb[3] / 2, 3),
                                                                  round(bb[2] / 2, 3), round(bb[3] / 2, 3)]})

    print('5. actors')
    actors = {}
    for aid, info in doc.actors.items():
        sname = safe_name(aid)
        e = {'pivot': info['pivot'], 'zone': info['zone'], 'rest_state': info['rest_state'], 'cut': info['skip_in_plate']}
        if info['skip_in_plate']:
            bb = refine_actor_bbox(actor_pdfs[aid], info['bbox'])
            sts = CUTOUT_STATES.get(aid, (None, []))[1]
            for st in sts:
                bb = refine_actor_bbox(cut_pdfs[(aid, st)], bb)
            e['bbox'] = bb
            im = pdf_clip_to_pil(actor_pdfs[aid], dpi=ACTOR_DPI, bbox_mm=bb, alpha=True)
            f = 'actor_%s.webp' % sname
            im.save(os.path.join(OUT, f), quality=90)
            if sts:
                files = []
                for st in range(info['states']):
                    src = actor_pdfs[aid] if st == info['rest_state'] else cut_pdfs[(aid, st)]
                    ims = pdf_clip_to_pil(src, dpi=ACTOR_DPI, bbox_mm=bb, alpha=True)
                    fs = 'state_%s_%d.webp' % (sname, st)
                    ims.save(os.path.join(OUT, fs), quality=90)
                    files.append({'file': 'assets/' + fs})
                e['states'] = files
            else:
                e['file'] = 'assets/' + f
        else:
            bb = info['bbox']
            e['bbox'] = bb
            files = []
            for st in range(info['states']):
                if st == info['rest_state']:
                    files.append(None)        # the plate itself
                    continue
                ims = pdf_clip_to_pil(region_pdfs[(aid, st)], dpi=REGION_DPI, bbox_mm=bb, alpha=False)
                fs = 'region_%s_%d.webp' % (sname, st)
                ims.save(os.path.join(OUT, fs), quality=88)
                files.append('assets/' + fs)
            e['region'] = files
        actors[aid] = e

    print('6. rest composite check')
    W, H = poster100.size
    comp = pdf_clip_to_pil(plate_pdf, dpi=100, alpha=True)
    for aid, e in actors.items():
        if not e['cut']:
            continue
        a = pdf_clip_to_pil(actor_pdfs[aid], dpi=100, alpha=True)
        comp = Image.alpha_composite(comp, a)
    diff = np.abs(np.asarray(comp.convert('RGB'), np.float32) - np.asarray(poster100, np.float32)).max(axis=2)
    mask = (diff > 24).astype(np.uint8) * 255
    Image.fromarray(mask).save(os.path.join(ROOT, 'build', 'check_v3_diff.png'))
    ys, xs = np.nonzero(mask)
    print('   differing px > 24/255:', len(xs))
    # "over" patch: wherever the rest composite differs (poster marks painted above an actor), paste the poster's
    # pixels on top, so the rest state is exact; scenes fade it out while that actor moves.
    over = np.zeros((H, W, 4), np.uint8)
    m = np.asarray(Image.fromarray(mask).filter(ImageFilter.MaxFilter(5))) > 0
    over[..., :3] = np.asarray(poster100)
    over[..., 3] = np.where(m, 255, 0)
    oy, ox = np.nonzero(m)
    overs = []
    if len(ox):
        # split into connected blobs (coarse grid clustering)
        lab = np.zeros(m.shape, np.int32)
        from scipy import ndimage
        lab, n = ndimage.label(np.asarray(Image.fromarray(m.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(15))) > 0)
        for k, sl in enumerate(ndimage.find_objects(lab)):
            y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
            crop = over[y0:y1, x0:x1].copy()
            crop[..., 3] = np.where(lab[y0:y1, x0:x1] == k + 1, crop[..., 3], 0)
            if crop[..., 3].max() == 0:
                continue
            f = 'over_%d.png' % k
            Image.fromarray(crop, 'RGBA').save(os.path.join(OUT, f))
            mm = 1100.0 / W
            overs.append({'file': 'assets/' + f, 'bbox': [round(x0 * mm, 2), round(y0 * mm, 2), round((x1 - x0) * mm, 2), round((y1 - y0) * mm, 2)]})
    print('   over patches:', len(overs))

    print('7. LOD copies (lo = 1/4, mid = 1/2) of every actor / region / state image')
    import re, shutil
    for sub, k in (('lo', 4), ('mid', 2)):
        d = os.path.join(OUT, sub)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        for f in sorted(os.listdir(OUT)):
            if re.match(r'^(actor|region|state)_.+\.webp$', f):
                im = Image.open(os.path.join(OUT, f))
                im.resize((max(1, round(im.width / k)), max(1, round(im.height / k))), Image.LANCZOS).save(os.path.join(d, f), quality=88)

    man = {'tiles': tiles, 'actors': actors, 'labels': doc.labels, 'overs': overs}
    with open(os.path.join(DATA, 'manifest.js'), 'w', encoding='utf-8') as f:
        f.write('window.MANIFEST = ' + json.dumps(man, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print('done in %.0fs: %d actors, %d labels' % (time.time() - t0, len(actors), len(doc.labels)))


if __name__ == '__main__':
    main()
