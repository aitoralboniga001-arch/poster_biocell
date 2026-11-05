# Macrophage poster: V2 deliverables

**"How a macrophage destroys what it engulfs"**: 110 × 90 cm landscape, English, Cell Biology seminar (first-year Medicine).

| File | What it is |
|---|---|
| `Macrophage_poster.pdf` | Print master: vector plus embedded paper and wash textures, 1 page, 1100 × 900 mm, about 22 MB |
| `Macrophage_poster.svg` | Editable master |
| `Macrophage_poster_150dpi.jpg` | Full-resolution raster, 6496 × 5315 px |
| `Preview_full_poster.png` | Whole-poster preview |
| `Readable_*.png` | 100 dpi crops of each zone |
| `editable_source/` | Python generator. Run `python build_poster.py --out poster.svg`, then `python render.py --svg poster.svg --pdf poster.pdf` |

## Concept: everything happens inside one cell
There are no side panels and no windows. One giant, mixed-scale alveolar macrophage rests on a living lung septum. The septum is healthy on the left and fibrotic on the right. Molecular detail is enlarged where it happens:
- **Recognition** at the leading edge, around a captured bacterium.
- **Lysosome biogenesis** runs ER → Golgi → TGN → late endosome → lysosome, descending from the top right.
- **The phagosome chain** descends from the left.
- **The two routes meet** in a "V" at the phagolysosome: the conclusion drawn as a shape.
- **Silica / NLRP3** sits in the right bulge, with GSDMD pores in the cell's own membrane.
- **Asbestos** lies in an open cup at the right base.
- **Lung injury** is shown in the wall below.

## Typography
- **Title:** hand-lettered Sitka Banner, with *destroys* in a Gabriola swash.
- **Section and organelle names:** Gabriola.
- **Molecule labels:** a clean sans, kept for legibility.

Dashed arrows mean "possible", not inevitable.

## Print notes
- Print at 100 %, with no bleed.
- Fonts are Windows 11 system fonts, embedded by Chrome as Type 3. If the print shop's preflight check complains, send the 150 dpi JPG instead.
- The files are RGB.

## Earlier versions
- V1.2 (labels-only, side columns): `../deliverables_v12/`
- V1.2 source: `../src_v12_final_backup/`
