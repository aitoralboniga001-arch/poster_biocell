# Macrophage poster: V1.2 deliverables

**"How a macrophage destroys what it engulfs"**: 110 × 90 cm landscape, English, Cell Biology seminar (first-year Medicine).

| File | What it is |
|---|---|
| `Macrophage_poster.pdf` | Final print master: vector, 1 page, 1100 × 900 mm |
| `Macrophage_poster.svg` | Editable master (Inkscape / Illustrator / Affinity / Figma) |
| `Macrophage_poster_150dpi.jpg` | Full-resolution raster, 6496 × 5315 px |
| `Preview_full_poster.png` | Whole-poster preview |
| `Readable_*.png` | Crops at 100 dpi, close to reading distance, to check legibility |
| `editable_source/` | Python generator. Run `python build_poster.py --out poster.svg`, then `python render.py --svg poster.svg --pdf poster.pdf` (needs Chrome and PyMuPDF) |

## Concept: one alveolus, three scales
- **Lung tissue.** The air space is the background. A single alveolar septum runs along the bottom and changes from healthy (left) to fibrotic (right).
- **The cell.** The macrophage rests on that wall and contains every compartment, numbered in speaking order.
- **Molecular windows.** Detail views open out of the cell as frameless, feathered areas (no boxes). Each is linked to its source by a thin ring and focus lines. They cover recognition and actin, fusion, killing, lysosome biogenesis (M6P) and silica/NLRP3.

## Text rule (V1.2b)
This is a visual poster:
- The drawings carry the story. Text is limited to labels: names, numbers and section headings.
- There is one conclusion line.
- **A dashed arrow means "possible", not inevitable.** Examples are pyroptosis and re-uptake of the released crystal.
- The references are a source list at the foot of the poster.

The fully annotated V1.2 version (with captions) is kept in `../src_v12_textheavy_backup/` if you prefer it for handouts.

## Speaking order
1. Aitor
2. Nerea (2.7)
3. Urtzi
4. Eneritz
5. Nora
6. Aitor

## Print notes
- **No bleed:** the design sits on an 1100 × 900 mm page with a paper-coloured background. Ask the print shop to print at 100 % with no scaling.
- **Fonts:** Sitka and Segoe UI Variable, the Windows 11 system fonts, are embedded in the PDF, so it prints correctly anywhere. Chrome embeds them as Type 3 fonts. If a print shop's preflight check rejects them, send the 150 dpi JPG instead.
- **Colour:** the files are RGB. Expect slightly duller pinks and cyans in CMYK.
