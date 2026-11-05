# Macrophage poster V2: "Everything happens inside one cell"

## Why we are rebuilding
The client's verdict on V1.2 (labels-only, side columns of molecular windows):
- it does not feel like a poster;
- the typography should feel hand-made;
- the central cell looks like a square;
- the views outside the cell feel like attachments and do not belong to the same story;
- the drawings could be more beautiful.

They want imagination, and they want to impress the teacher.

## The concept
There are no side panels, no windows, no lenses and no cards. **One giant, mixed-scale macrophage fills the scene**, resting on the alveolar wall. Molecular detail is drawn inside the cell, at the exact place where it happens. Think David Goodsell or a high-end semi-schematic textbook spread.

**Recognition.** The leading edge of the cell is drawn at molecular scale. Receptors bridge to a big bacterium caught between two pseudopod arms.

**Lysosome biogenesis.** This route is a staircase of enlarged organelle sacs: ER → cis-Golgi → TGN with clathrin bud → late endosome → lysosome. It descends from the top right toward the bottom centre.

**Phagocytic route.** The phagosome chain descends from the leading edge toward the bottom centre.

**The meeting point.** The two routes meet in a **V** at the giant phagolysosome, the point of the V. This is the poster's thesis drawn as a shape: *two routes converge to destroy*.

**Silica.** The NLRP3 cascade happens in the cytosol next to the silica phagolysosome. The GSDMD pores sit in the cell's own right-hand membrane.

**Asbestos.** The fibre lies on the wall in an open cup at the cell's right base and runs off the page.

**The alveolus.** The cell sits in an alveolus:
- the air space is above;
- the septum along the bottom changes from healthy (left) to fibrotic (right);
- the locator sketch of lung → alveolus sits in the air at the top left;
- the title is hand-lettered above the cell.

The geometry contract is `src/geom_v2.py`: zones, membrane segments, vesicle centres, the asbestos fibre and air strips.

## Art direction (everyone)
- **Beautiful first.** Illustrative and painterly. Soft light from the top left; gradients are fine. Use rich but harmonious colour: warm peach cytoplasm, cool blue enzyme route, plum/violet lysosomal compartments, amber pathology.
- **Nothing that looks like a box, window, card, strip or frame.** Molecular areas live in the cytoplasm. A very soft local tint pool (feathered, no edge) behind a molecular area is allowed.
- **Smooth scale changes.** Where molecular scale meets organelle scale, membranes thicken or taper smoothly. There are no hard seams.
- **Organic forms.** Wobbly-but-controlled lines, rounded sacs, no ruler-straight edges on biological structures.
- **No new prose.** Labels only: names, numbers, short qualifiers. Dashed arrows mean "possible".
- **Keep every scientific correction from V1.2:**
  - TLR4 is a single-pass receptor that signals through MyD88 to NF-κB;
  - Cdc42 → WASP and Rac → WAVE are separate;
  - Arp2/3 builds a 70° branched network;
  - M6PR faces the lumen;
  - no loose hydrolases in the cytosol;
  - HOPS/Rab7 tethering is distinct from the SNARE zipper;
  - NSF/α-SNAP recycle the SNAREs;
  - NOX2 → ROS; V-ATPase → H⁺;
  - the pH falls 6.5 → 5.5 → 4.5;
  - silica: priming (signal 1, TLR → NF-κB) plus cathepsin B leak / K⁺ efflux (signal 2) → NLRP3 + ASC → caspase-1 → IL-1β / IL-18 + GSDMD pore (~20 nm);
  - pyroptosis and re-uptake are possible (dashed), not inevitable;
  - the asbestos fibre is longer than 15–20 µm; the cup stays open and the fibre never pierces an intact membrane;
  - ROS and enzymes leak onto the epithelium; IL-1β / TNF-α drive inflammation; TGF-β / PDGF drive fibrosis.

## Typography
- **Title:** hand-lettered feel. "How a macrophage" and "what it engulfs" in Sitka Banner. *destroys* is in Gabriola with swash (`font-feature-settings:'ss07'`), in red.
- **Section marks:** `marks.section()`, a number in a hand-inked circle plus the name in Gabriola.
- **Organelle names:** Gabriola. Larger than the molecule labels, and in the organelle's colour.
- **Molecule labels:** a clean humanist sans (current `T()` / Segoe UI Variable), 4.4–4.8 mm, so they stay legible.
- Speaking order: 1 Aitor, 2 Nerea · 2.7, 3 Urtzi, 4 Eneritz, 5 Nora, 6 Aitor.

## Working method (every agent)
1. Copy `src/` to `build/work_<yourname>/src/` and work only there.
2. Edit **only the files you own**. New files are fine if you create them; list them in your report.
3. Build: `python build_poster.py --out ../build/work_<yourname>.svg`
4. Render: `python render.py --svg ../build/work_<yourname>.svg --pdf ../build/work_<yourname>.pdf --out ../build/work_<yourname>.png --dpi 45`
5. Look at the full view and at 100–150 dpi crops of your zone (`--crop x y w h --dpi 120`, in mm). Iterate until it is genuinely beautiful and legible, with no collisions.
6. The console is cp1252. Write any Unicode output to UTF-8 files instead of printing it.
7. Report back:
   - the files you changed or created;
   - a 6–10 line summary;
   - any contract number you had to bend, and why;
   - the path of your final full-view PNG.
