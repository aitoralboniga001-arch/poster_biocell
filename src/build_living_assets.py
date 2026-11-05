"""Asset pipeline and exit-test verifier for The Living Poster (Phase 1 & Phase 3).

Usage:
    python src/build_living_assets.py

Generates into `Living_poster/assets/`:
  - plate_100dpi.webp, plate_blur.webp, poster_100dpi.webp
  - 300 dpi zone tiles (tile_locator, tile_zone_a..g)
  - 600 dpi EM tiles (tile_em_receptors, tile_em_snares, tile_em_nlrp3)
  - 300 dpi cropped transparent WebP actors and multi-state actor frames
  - Phase 3 new art assets (sketches, props, size tags, margin doodles, signatures, desk fibre, bloom masks, sprites)
  - manifest.json AND manifest.js (window.LIVING_MANIFEST = ... for offline file:/// compatibility)
  - build/living_contact_sheet.png (Exit Test 3 visual contact sheet)
"""
import os, sys, json, math, time, shutil, hashlib, tempfile, subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import fitz
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

import lib
import geom_v2 as V
import wallgeom
import build_poster
import anim_art
from render import CHROME

OUT_DIR = os.path.join(ROOT, 'Living_poster', 'assets')
BUILD_DIR = os.path.join(ROOT, 'build')

ZONE_TILES = {
    'tile_locator': [20, 114, 248, 148],
    'tile_zone_a':  [10, 220, 275, 355],
    'tile_zone_b':  [170, 410, 345, 310],
    'tile_zone_d':  [590, 120, 395, 450],
    'tile_zone_e':  [300, 525, 475, 245],
    'tile_zone_f':  [775, 490, 320, 220],
    'tile_zone_g':  [680, 665, 418, 175],
}

EM_TILES = {
    'tile_em_receptors': [55, 295, 175, 195],
    'tile_em_snares':    [420, 540, 140, 155],
    'tile_em_nlrp3':     [875, 535, 220, 170],
}


def safe_name(aid):
    return aid.replace('.', '_').replace(':', '_')


def svg_to_pdf(svg_str, pdf_path, w_mm=1100, h_mm=900, transparent=True):
    """Render an SVG string to a vector PDF via headless Chrome with transparent background (with MD5 cache)."""
    cache_dir = os.path.join(BUILD_DIR, 'pdf_cache')
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.md5((f'{w_mm}:{h_mm}:{transparent}:' + svg_str).encode('utf-8')).hexdigest()
    cached_pdf = os.path.join(cache_dir, f'{key}.pdf')
    if os.path.exists(cached_pdf) and os.path.getsize(cached_pdf) > 0:
        shutil.copyfile(cached_pdf, pdf_path)
        return
    if svg_str.startswith('<?xml'):
        svg_str = svg_str.split('?>', 1)[1]
    fd, html_path = tempfile.mkstemp(suffix='.html')
    bg = 'transparent' if transparent else '#F5F2EB'
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write('<!doctype html><html><head><meta charset="utf-8"><style>'
                    '@page{size:%smm %smm;margin:0}'
                    'html,body{margin:0;padding:0;width:%smm;height:%smm;overflow:hidden;background:%s}'
                    'svg{display:block;width:%smm;height:%smm;background:%s}'
                    '</style></head><body>%s</body></html>' % (
                        w_mm, h_mm, w_mm, h_mm, bg, w_mm, h_mm, bg, svg_str))
        cmd = [
            CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
            '--print-to-pdf=' + os.path.abspath(pdf_path),
            'file:///' + os.path.abspath(html_path).replace('\\', '/')
        ]
        if transparent:
            cmd.insert(3, '--default-background-color=00000000')
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            shutil.copyfile(pdf_path, cached_pdf)
    finally:
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
            except OSError:
                pass


def pdf_clip_to_pil(pdf_path, dpi, bbox_mm=None, w_mm=1100, h_mm=900, alpha=True):
    """Rasterize a PDF page (or mm bbox [x, y, w, h]) at `dpi` to a PIL Image (with straight unpremultiplied RGBA)."""
    doc = fitz.open(pdf_path)
    page = doc[0]
    rect = page.rect
    if bbox_mm is not None:
        x, y, bw, bh = bbox_mm
        sx = rect.width / float(w_mm)
        sy = rect.height / float(h_mm)
        clip = fitz.Rect(x * sx, y * sy, (x + bw) * sx, (y + bh) * sy)
        pix = page.get_pixmap(dpi=dpi, clip=clip, alpha=alpha)
    else:
        pix = page.get_pixmap(dpi=dpi, alpha=alpha)
    if alpha:
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 4).copy()
        a = arr[:, :, 3:4].astype(np.float32)
        arr[:, :, :3] = np.where(
            a > 0,
            np.clip(np.round(arr[:, :, :3].astype(np.float32) * 255.0 / np.maximum(a, 1.0)), 0, 255),
            0,
        ).astype(np.uint8)
        img = Image.fromarray(arr, 'RGBA')
    else:
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def refine_actor_bbox(pdf_path, init_bbox, w_mm=1100, h_mm=900):
    """Detect exact non-transparent bounding box of an actor PDF at 100 dpi and ensure init_bbox
    completely encloses every non-zero alpha pixel with a 2 mm safety margin."""
    img = pdf_clip_to_pil(pdf_path, dpi=100, bbox_mm=None, w_mm=w_mm, h_mm=h_mm, alpha=True)
    alpha_bb = img.getchannel('A').getbbox()
    if not alpha_bb:
        return list(init_bbox)
    px0, py0, px1, py1 = alpha_bb
    scale_x = w_mm / float(img.width)
    scale_y = h_mm / float(img.height)
    ax0 = max(0.0, math.floor(px0 * scale_x - 2.0))
    ay0 = max(0.0, math.floor(py0 * scale_y - 2.0))
    ax1 = min(float(w_mm), math.ceil(px1 * scale_x + 2.0))
    ay1 = min(float(h_mm), math.ceil(py1 * scale_y + 2.0))
    ix, iy, iw, ih = init_bbox
    nx0 = min(ix, ax0)
    ny0 = min(iy, ay0)
    nx1 = max(ix + iw, ax1)
    ny1 = max(iy + ih, ay1)
    return [round(nx0, 1), round(ny0, 1), round(nx1 - nx0, 1), round(ny1 - ny0, 1)]


def build_vector_actors(poster_doc):
    """Extract vector polylines and paths for stroke-dashoffset / particle-flow animations."""
    vectors = {}
    # 1. Branched actin network (zone A)
    if hasattr(poster_doc, '_actin_data'):
        fil, nodes = poster_doc._actin_data
        vectors['actin_branches'] = {
            'filaments': [
                {'p0': [round(a[0], 2), round(a[1], 2)],
                 'p1': [round(b[0], 2), round(b[1], 2)],
                 'scale': round(k, 3)}
                for (a, b, k) in fil
            ],
            'arp23_nodes': [
                {'pos': [round(q[0], 2), round(q[1], 2)],
                 'a1': round(a1, 3),
                 'a2': round(a2, 3),
                 'scale': round(k, 3)}
                for (q, a1, a2, k) in nodes
            ]
        }
    # 2. SNARE 4-helix bundle (zone E)
    if hasattr(poster_doc, '_snare_data'):
        vectors['snare_helices'] = [
            {'pts': [[round(p[0], 2), round(p[1], 2)] for p in pz], 'color': col}
            for (pz, col) in poster_doc._snare_data
        ]
    # 3. Painted routes (RED_ROUTE & BLUE_ROUTE)
    vectors['red_route'] = [[round(x, 2), round(y, 2)] for (x, y) in V.RED_ROUTE]
    vectors['blue_route'] = [[round(x, 2), round(y, 2)] for (x, y) in V.BLUE_ROUTE]
    # 4. Capillary centrelines for RBC flow
    vectors['capillary_centrelines'] = [
        {'cx': round(cx, 2), 'cy': round(cy, 2), 'rx': round(rx, 2), 'ry': round(ry, 2), 'healthy': bool(ok)}
        for (cx, cy, rx, ry, ok) in wallgeom.CAPS
    ]
    # 5. Circle-of-life re-uptake loop (zone F)
    vectors['circle_of_life'] = [
        [1018, 648], [1058, 636], [1080, 622], [1082, 579], [1056, 546], [1022, 524], [994, 512]
    ]
    # 6. pH gauge ribbon centreline
    vectors['ph_ribbon'] = [
        [309, 667], [311, 688], [322, 707], [343, 719], [370, 724], [398, 723.5],
        [422, 723.2], [446, 731], [474, 738.5], [506, 743], [536, 744.2]
    ]
    # 7. Play-button macrophage tendrils (centred on cell center (540, 450))
    vectors['play_tendrils'] = [
        [[540, 450], [495, 420], [450, 395], [410, 380]],
        [[540, 450], [585, 415], [635, 390], [680, 375]],
        [[540, 450], [490, 480], [445, 510], [405, 535]],
        [[540, 450], [590, 485], [640, 515], [685, 540]],
    ]
    return vectors


def run_exit_test_1(poster_svg_str):
    """Exit Test 1: Verify build_poster.py in default 'poster' mode is byte-identical to Macrophage_poster.svg."""
    orig_path = os.path.join(ROOT, 'Macrophage_poster.svg')
    with open(orig_path, 'rb') as f:
        orig_bytes = f.read()
    orig_lf = orig_bytes.replace(b'\r\n', b'\n')
    new_lf = poster_svg_str.encode('utf-8').replace(b'\r\n', b'\n')
    h_orig = hashlib.md5(orig_lf).hexdigest()
    h_new = hashlib.md5(new_lf).hexdigest()
    ok = (h_orig == h_new)
    print(f'[Exit Test 1] Byte-identical poster SVG: {ok} (MD5={h_new})')
    if not ok:
        raise AssertionError(f'Exit Test 1 FAILED: expected MD5 {h_orig}, got {h_new}')
    return {'passed': True, 'md5_lf': h_new}


def run_exit_test_2(poster_pdf, plate_pdf, actor_pdfs, actors_meta):
    """Exit Test 2: Composite plate + all rest-state cut-out actors at 100 dpi and compare to poster_100dpi.
    Assert mean diff < 1/255 and max local (16x16 block mean) < 8/255."""
    poster_img = pdf_clip_to_pil(poster_pdf, dpi=100, alpha=True)
    comp_img = pdf_clip_to_pil(plate_pdf, dpi=100, alpha=True)
    W, H = comp_img.size
    for aid, info in actors_meta.items():
        if not info.get('skip_in_plate', True):
            continue
        apdf = actor_pdfs[aid]
        # Render actor full page at 100 dpi and crop to its refined bbox so pixel grid aligns 1:1
        a_full = pdf_clip_to_pil(apdf, dpi=100, alpha=True)
        bx, by, bw, bh = info['bbox']
        x0 = max(0, int(round(bx * W / 1100.0)))
        y0 = max(0, int(round(by * H / 900.0)))
        x1 = min(W, int(round((bx + bw) * W / 1100.0)))
        y1 = min(H, int(round((by + bh) * H / 900.0)))
        crop = a_full.crop((x0, y0, x1, y1))
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        layer.paste(crop, (x0, y0))
        comp_img = Image.alpha_composite(comp_img, layer)

    arr_p = np.asarray(poster_img.convert('RGB'), dtype=np.float32)
    arr_c = np.asarray(comp_img.convert('RGB'), dtype=np.float32)
    diff = np.abs(arr_p - arr_c)
    mean_diff = float(np.mean(diff))
    # Compute 16x16 local block mean max diff (avoids single-pixel anti-aliasing jitter)
    h16, w16 = (arr_p.shape[0] // 16) * 16, (arr_p.shape[1] // 16) * 16
    blocks = diff[:h16, :w16].reshape(h16 // 16, 16, w16 // 16, 16, 3).mean(axis=(1, 3, 4))
    max_local = float(np.max(blocks))
    max_pixel = float(np.max(diff))
    print(f'[Exit Test 2] Plate + Rest Actors vs Poster: mean_diff={mean_diff:.4f}/255 '
          f'(< 1.0), max_local_16x16={max_local:.4f}/255 (< 8.0), max_px={max_pixel:.1f}/255')
    if max_local >= 4.0:
        flat_idx = np.argsort(blocks.ravel())[::-1][:8]
        for idx in flat_idx:
            br, bc = divmod(int(idx), blocks.shape[1])
            xmm = (bc * 16 + 8) * 1100.0 / W
            ymm = (br * 16 + 8) * 900.0 / H
            print(f'   -> Hotspot at poster mm ({xmm:.1f}, {ymm:.1f}): block_mean={blocks[br, bc]:.2f}/255')
    if mean_diff >= 1.0 or max_local >= 8.0:
        raise AssertionError(f'Exit Test 2 FAILED: mean_diff={mean_diff}, max_local={max_local}')
    return {'passed': True, 'mean_diff': round(mean_diff, 5), 'max_local_16x16': round(max_local, 5), 'max_pixel': round(max_pixel, 2)}


def generate_contact_sheet(assets_dir, out_png):
    """Exit Test 3: Build a comprehensive visual contact sheet of all generated WebP assets."""
    files = sorted([f for f in os.listdir(assets_dir) if f.endswith('.webp')])
    cols = 8
    cell_w, cell_h = 220, 185
    rows = math.ceil(len(files) / cols)
    sheet = Image.new('RGB', (cols * cell_w + 20, rows * cell_h + 60), (242, 239, 232))
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 16), f'THE LIVING POSTER — ASSET CONTACT SHEET ({len(files)} WebP assets)', fill=(30, 36, 51))

    for idx, fname in enumerate(files):
        r, c = divmod(idx, cols)
        x0 = 10 + c * cell_w
        y0 = 50 + r * cell_h
        # Checkerboard backing to show alpha transparency clearly
        for cy in range(y0 + 6, y0 + cell_h - 28, 12):
            for cx in range(x0 + 6, x0 + cell_w - 6, 12):
                col_c = (228, 225, 218) if ((cx // 12 + cy // 12) % 2 == 0) else (248, 246, 240)
                draw.rectangle([cx, cy, min(cx + 12, x0 + cell_w - 6), min(cy + 12, y0 + cell_h - 28)], fill=col_c)
        draw.rectangle([x0 + 5, y0 + 5, x0 + cell_w - 5, y0 + cell_h - 27], outline=(180, 172, 158), width=1)
        try:
            im = Image.open(os.path.join(assets_dir, fname)).convert('RGBA')
            iw, ih = im.size
            scale = min((cell_w - 20) / max(iw, 1), (cell_h - 42) / max(ih, 1))
            nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
            im_r = im.resize((nw, nh), Image.Resampling.LANCZOS)
            px = x0 + (cell_w - nw) // 2
            py = y0 + 6 + (cell_h - 34 - nh) // 2
            sheet.paste(im_r, (px, py), im_r)
            label = f'{fname[:26]} ({iw}x{ih})'
        except Exception as e:
            label = f'{fname[:24]} ERR'
        draw.text((x0 + 8, y0 + cell_h - 22), label, fill=(45, 50, 64))

    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    sheet.save(out_png)
    print(f'[Exit Test 3] Wrote contact sheet: {out_png} ({sheet.width}x{sheet.height} px, {len(files)} assets)')


def main():
    t_start = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(BUILD_DIR, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix='living_build_')

    try:
        # ------------------------------------------------------------------
        # 1. Build poster & plate documents + run Exit Test 1
        # ------------------------------------------------------------------
        print('1. Building poster & plate SVG documents...')
        plate_doc = build_poster.build(mode='plate')
        poster_svg = plate_doc.render_poster('Macrophages: phagocytosis, lysosomal biogenesis and vesicular trafficking')
        test1_res = run_exit_test_1(poster_svg)
        plate_svg = plate_doc.render('Macrophages — Living Poster Base Plate')
        poster_doc = plate_doc

        # Collect all PDF render jobs: (job_id, svg_str, w_mm, h_mm, transparent, pdf_path)
        pdf_jobs = []
        poster_pdf = os.path.join(tmp_dir, 'poster.pdf')
        plate_pdf = os.path.join(tmp_dir, 'plate.pdf')
        pdf_jobs.append(('poster', poster_svg, 1100, 900, False, poster_pdf))
        pdf_jobs.append(('plate', plate_svg, 1100, 900, False, plate_pdf))

        # Cut-out actors (at rest state from plate_doc)
        actor_pdfs = {}
        for aid, info in plate_doc.actors.items():
            if info.get('skip_in_plate', True):
                asvg = plate_doc.render_actor(aid)
                apdf = os.path.join(tmp_dir, f'actor_{safe_name(aid)}.pdf')
                actor_pdfs[aid] = apdf
                pdf_jobs.append((f'actor:{aid}', asvg, 1100, 900, True, apdf))

        # Multi-state region actors (skip_in_plate=False): batch into 4 fast plate builds
        # (m_m6p, m_vesicles, m_recognition are cut-out/distant and not needed for wall/outline patches)
        region_batches = [
            ('reg_b0', {'pseudopod_arms': 0, 'asbestos_hood': 0, 'fibrosis_wall': 0, 'alveolar_lumen': 1}),
            ('reg_b1', {'pseudopod_arms': 2, 'asbestos_hood': 2, 'fibrosis_wall': 1}),
            ('reg_b2', {'pseudopod_arms': 3, 'fibrosis_wall': 2}),
            ('reg_b3', {'fibrosis_wall': 4}),
        ]
        reg_pdfs = {}
        orig_live = dict(build_poster.LIVE)
        try:
            build_poster.LIVE = {'recognition': False, 'vesicles': False, 'm6p': False, 'patho': True}
            for bname, ov in region_batches:
                bdoc = build_poster.build(mode='plate', state_overrides=ov)
                bpdf = os.path.join(tmp_dir, f'{bname}.pdf')
                reg_pdfs[bname] = bpdf
                pdf_jobs.append((bname, bdoc.render(), 1100, 900, False, bpdf))

            # Multi-state cut-out actors (non-rest states): only m_vesicles and m_patho needed!
            cutout_state_batches = [
                ('cut_s0', {'fusion_pore': 0, 'bacterium_pl': 0, 'silica_membrane': 0, 'nlrp3': 0}),
                ('cut_s1', {'fusion_pore': 1, 'bacterium_pl': 1, 'silica_membrane': 2, 'nlrp3': 1}),
                ('cut_s3', {'bacterium_pl': 3}),
            ]
            cut_state_pdfs = {}
            import m_vesicles, m_patho
            for bname, ov in cutout_state_batches:
                cdoc = lib.Doc(1100, 900, mode='plate', state_overrides=ov)
                if 'fusion_pore' in ov or 'bacterium_pl' in ov:
                    m_vesicles.draw(cdoc)
                if 'silica_membrane' in ov or 'nlrp3' in ov:
                    m_patho.draw(cdoc)
                for aid, st_val in ov.items():
                    key = (aid, st_val)
                    cpdf = os.path.join(tmp_dir, f'state_{safe_name(aid)}_{st_val}.pdf')
                    cut_state_pdfs[key] = cpdf
                    pdf_jobs.append((f'state:{aid}:{st_val}', cdoc.render_actor(aid), 1100, 900, True, cpdf))
        finally:
            build_poster.LIVE = orig_live

        # Phase 3 New Art SVG documents
        new_art_specs = [
            ('opening_street', anim_art.opening_street(), 550, 450, False, 150),
            ('opening_lungs', anim_art.opening_lungs(), 550, 450, False, 150),
            ('bronchi_1', anim_art.bronchi_tunnel(0), 550, 450, False, 150),
            ('bronchi_2', anim_art.bronchi_tunnel(1), 550, 450, False, 150),
            ('bronchi_3', anim_art.bronchi_tunnel(2), 550, 450, False, 150),
            ('loupe', anim_art.prop_loupe(), 240, 240, True, 150),
            ('stopwatch', anim_art.prop_stopwatch(), 120, 140, True, 180),
            ('ph_gauge_dial', anim_art.prop_ph_gauge_dial(), 160, 110, True, 180),
            ('doodle_envelope', anim_art.doodle_envelope(), 240, 180, True, 180),
            ('doodle_sorting', anim_art.doodle_sorting(), 240, 180, True, 180),
            ('doodle_postman_home', anim_art.doodle_postman_home(), 240, 180, True, 180),
            ('desk_fibre', anim_art.desk_fibre(), 260, 140, True, 200),
            ('bloom_mask_1', anim_art.bloom_mask_1(), 1100, 900, True, 75),
            ('bloom_mask_2', anim_art.bloom_mask_2(), 1100, 900, True, 75),
            ('sprite_hplus', anim_art.sprite_hplus(), 32, 32, True, 150),
            ('sprite_ros', anim_art.sprite_ros(), 40, 40, True, 150),
            ('sprite_cytokine', anim_art.sprite_cytokine(), 32, 32, True, 150),
            ('sprite_bacterium_cursor', anim_art.sprite_bacterium_cursor(), 48, 48, True, 150),
        ]
        for s_idx in range(5):
            new_art_specs.append((f'turret_{s_idx}', anim_art.prop_turret(s_idx), 200, 120, True, 180))
            new_art_specs.append((f'calendar_{s_idx}', anim_art.prop_calendar(s_idx), 140, 160, True, 180))
        for tag_id, tag_txt, tag_col in anim_art.SIZE_TAGS_SPEC:
            new_art_specs.append((tag_id, anim_art.prop_size_tag(tag_txt, tag_col), 180, 48, True, 180))
        for sec_num, sig_name, _, _ in anim_art.SIGNATURES_SPEC:
            new_art_specs.append((f'sig_{sec_num}_{sig_name.lower()}', anim_art.signature_card(sec_num, sig_name), 160, 60, True, 180))

        art_pdfs = {}
        for name, adoc, w_mm, h_mm, transp, dpi in new_art_specs:
            svg_s = adoc.render()
            # Save .svg for props/doodles/sketches/signatures
            with open(os.path.join(OUT_DIR, f'{name}.svg'), 'w', encoding='utf-8') as f:
                f.write(svg_s)
            apdf = os.path.join(tmp_dir, f'art_{name}.pdf')
            art_pdfs[name] = (apdf, w_mm, h_mm, transp, dpi)
            pdf_jobs.append((f'art:{name}', svg_s, w_mm, h_mm, transp, apdf))
        # Also save turret.svg and calendar.svg aliases (state 0)
        shutil.copyfile(os.path.join(OUT_DIR, 'turret_0.svg'), os.path.join(OUT_DIR, 'turret.svg'))
        shutil.copyfile(os.path.join(OUT_DIR, 'calendar_0.svg'), os.path.join(OUT_DIR, 'calendar.svg'))

        # ------------------------------------------------------------------
        # 2. Render all SVGs to PDFs in parallel using Chrome headless
        # ------------------------------------------------------------------
        print(f'2. Rendering {len(pdf_jobs)} SVG documents to vector PDFs (6 parallel Chrome workers)...')
        def _run_job(job):
            jid, svg_s, w_m, h_m, tr, pdf_p = job
            svg_to_pdf(svg_s, pdf_p, w_mm=w_m, h_mm=h_m, transparent=tr)
            return jid

        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(_run_job, pdf_jobs))

        # ------------------------------------------------------------------
        # 3. Refine actor bounding boxes from alpha channel & run Exit Test 2
        # ------------------------------------------------------------------
        print('3. Verifying & refining actor bounding boxes from rendered alpha channels...')
        for aid, info in plate_doc.actors.items():
            if info.get('skip_in_plate', True):
                info['bbox'] = refine_actor_bbox(actor_pdfs[aid], info['bbox'])
                # Also check non-rest states if multi-state cut-out actor
                if info['states'] > 1:
                    for st_i in range(info['states']):
                        if st_i != info['rest_state'] and (aid, st_i) in cut_state_pdfs:
                            info['bbox'] = refine_actor_bbox(cut_state_pdfs[(aid, st_i)], info['bbox'])

        test2_res = run_exit_test_2(poster_pdf, plate_pdf, actor_pdfs, plate_doc.actors)

        # ------------------------------------------------------------------
        # 4. Extract WebP plates, 300 dpi zone tiles, 600 dpi EM tiles
        # ------------------------------------------------------------------
        print('4. Rasterizing base plates, 300 dpi zone tiles, and 600 dpi EM tiles...')
        poster_100 = pdf_clip_to_pil(poster_pdf, dpi=100, alpha=False)
        poster_100.save(os.path.join(OUT_DIR, 'poster_100dpi.webp'), 'WEBP', quality=90)

        plate_100 = pdf_clip_to_pil(plate_pdf, dpi=100, alpha=False)
        plate_100.save(os.path.join(OUT_DIR, 'plate_100dpi.webp'), 'WEBP', quality=90)

        plate_blur = plate_100.filter(ImageFilter.GaussianBlur(radius=3.5))
        plate_blur.save(os.path.join(OUT_DIR, 'plate_blur.webp'), 'WEBP', quality=86)

        tiles_manifest = {}
        for tname, tbbox in ZONE_TILES.items():
            im = pdf_clip_to_pil(poster_pdf, dpi=300, bbox_mm=tbbox, alpha=False)
            fname = f'{tname}.webp'
            im.save(os.path.join(OUT_DIR, fname), 'WEBP', quality=90)
            tiles_manifest[tname] = {'file': f'assets/{fname}', 'bbox': tbbox, 'dpi': 300, 'size': list(im.size)}

        for tname, tbbox in EM_TILES.items():
            im = pdf_clip_to_pil(poster_pdf, dpi=600, bbox_mm=tbbox, alpha=False)
            fname = f'{tname}.webp'
            im.save(os.path.join(OUT_DIR, fname), 'WEBP', quality=90)
            tiles_manifest[tname] = {'file': f'assets/{fname}', 'bbox': tbbox, 'dpi': 600, 'size': list(im.size)}

        # ------------------------------------------------------------------
        # 5. Rasterize all 300 dpi cropped actors & multi-state frames
        # ------------------------------------------------------------------
        print('5. Rasterizing 300 dpi transparent actor cut-outs & multi-state frames...')
        actors_manifest = {}
        reg_state_source = {
            ('pseudopod_arms', 0): reg_pdfs['reg_b0'],
            ('pseudopod_arms', 1): plate_pdf,
            ('pseudopod_arms', 2): reg_pdfs['reg_b1'],
            ('pseudopod_arms', 3): reg_pdfs['reg_b2'],
            ('asbestos_hood', 0):  reg_pdfs['reg_b0'],
            ('asbestos_hood', 1):  plate_pdf,
            ('asbestos_hood', 2):  reg_pdfs['reg_b1'],
            ('fibrosis_wall', 0):  reg_pdfs['reg_b0'],
            ('fibrosis_wall', 1):  reg_pdfs['reg_b1'],
            ('fibrosis_wall', 2):  reg_pdfs['reg_b2'],
            ('fibrosis_wall', 3):  plate_pdf,
            ('fibrosis_wall', 4):  reg_pdfs['reg_b3'],
            ('alveolar_lumen', 0): plate_pdf,
            ('alveolar_lumen', 1): reg_pdfs['reg_b0'],
        }

        for aid, info in plate_doc.actors.items():
            sname = safe_name(aid)
            bb = info['bbox']
            entry = {
                'id': aid,
                'pivot': list(info['pivot']),
                'bbox': list(bb),
                'zone': info['zone'],
                'states': info['states'],
                'rest_state': info['rest_state'],
                'skip_in_plate': info['skip_in_plate'],
            }
            if info['skip_in_plate']:
                im = pdf_clip_to_pil(actor_pdfs[aid], dpi=300, bbox_mm=bb, alpha=True)
                fname = f'actor_{sname}.webp'
                im.save(os.path.join(OUT_DIR, fname), 'WEBP', quality=92)
                entry['file'] = f'assets/{fname}'
                entry['size'] = list(im.size)

            if info['states'] > 1:
                state_files = []
                for st_i in range(info['states']):
                    if not info['skip_in_plate']:
                        src_pdf = reg_state_source[(aid, st_i)]
                        im_s = pdf_clip_to_pil(src_pdf, dpi=300, bbox_mm=bb, alpha=False)
                    else:
                        src_pdf = actor_pdfs[aid] if st_i == info['rest_state'] else cut_state_pdfs[(aid, st_i)]
                        im_s = pdf_clip_to_pil(src_pdf, dpi=300, bbox_mm=bb, alpha=True)
                    sfname = f'state_{sname}_{st_i}.webp'
                    im_s.save(os.path.join(OUT_DIR, sfname), 'WEBP', quality=92)
                    state_files.append(f'assets/{sfname}')
                    if st_i == info['rest_state'] and 'file' not in entry:
                        entry['file'] = f'assets/{sfname}'
                        entry['size'] = list(im_s.size)
                entry['state_files'] = state_files

            actors_manifest[aid] = entry

        # ------------------------------------------------------------------
        # 6. Rasterize Phase 3 New Art assets
        # ------------------------------------------------------------------
        print('6. Rasterizing Phase 3 New Art assets...')
        new_art_manifest = {}
        for name, (apdf, w_mm, h_mm, transp, dpi) in art_pdfs.items():
            im = pdf_clip_to_pil(apdf, dpi=dpi, bbox_mm=None, w_mm=w_mm, h_mm=h_mm, alpha=transp)
            fname = f'{name}.webp'
            im.save(os.path.join(OUT_DIR, fname), 'WEBP', quality=92)
            new_art_manifest[name] = {
                'webp': f'assets/{fname}',
                'svg': f'assets/{name}.svg',
                'w_mm': w_mm,
                'h_mm': h_mm,
                'size': list(im.size),
            }

        size_tags_json = [
            {'id': tid, 'text': ttxt.replace('&gt;', '>').replace('&amp;', '&'), 'color': tcol,
             'webp': f'assets/{tid}.webp', 'svg': f'assets/{tid}.svg'}
            for tid, ttxt, tcol in anim_art.SIZE_TAGS_SPEC
        ]
        with open(os.path.join(OUT_DIR, 'size_tags.json'), 'w', encoding='utf-8') as f:
            json.dump(size_tags_json, f, indent=2, ensure_ascii=False)

        # ------------------------------------------------------------------
        # 7. Write manifest.json AND manifest.js (for file:/// offline support)
        # ------------------------------------------------------------------
        print('7. Writing manifest.json and manifest.js...')
        manifest = {
            'canvas': {'w_mm': 1100, 'h_mm': 900, 'aspect': 1100 / 900.0},
            'plates': {
                'plate_100dpi': 'assets/plate_100dpi.webp',
                'plate_blur':   'assets/plate_blur.webp',
                'poster_100dpi': 'assets/poster_100dpi.webp',
            },
            'bloom_masks': {
                'bloom_mask_1': {'file': 'assets/bloom_mask_1.webp', 'center': [622, 665], 'radius': 115},
                'bloom_mask_2': {'file': 'assets/bloom_mask_2.webp', 'center': [890, 610], 'radius': 135},
            },
            'tiles': tiles_manifest,
            'actors': actors_manifest,
            'vectors': build_vector_actors(poster_doc),
            'labels': poster_doc.labels,
            'new_art': new_art_manifest,
            'size_tags': size_tags_json,
            'signatures': [
                {'section': sec, 'name': nm, 'x': sx, 'y': sy,
                 'webp': f'assets/sig_{sec}_{nm.lower()}.webp',
                 'svg': f'assets/sig_{sec}_{nm.lower()}.svg'}
                for sec, nm, sx, sy in anim_art.SIGNATURES_SPEC
            ],
            'exit_tests': {
                'test1_byte_identical_poster': test1_res,
                'test2_zero_seam_composite': test2_res,
            }
        }
        manifest_json_path = os.path.join(OUT_DIR, 'manifest.json')
        with open(manifest_json_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        manifest_js_path = os.path.join(OUT_DIR, 'manifest.js')
        with open(manifest_js_path, 'w', encoding='utf-8') as f:
            f.write('window.LIVING_MANIFEST = ')
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            f.write(';\n')

        # ------------------------------------------------------------------
        # 8. Exit Test 3: Generate visual contact sheet
        # ------------------------------------------------------------------
        contact_png = os.path.join(BUILD_DIR, 'living_contact_sheet.png')
        generate_contact_sheet(OUT_DIR, contact_png)

        elapsed = time.time() - t_start
        print(f'DONE in {elapsed:.1f}s! Generated {len(actors_manifest)} actors, '
              f'{len(tiles_manifest)} tiles, {len(poster_doc.labels)} labels, '
              f'and {len(new_art_manifest)} new art assets.')
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
