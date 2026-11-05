# Change log: response to review 03 (28 Oct 2026)

## Poster (generator in `src/`, master `Macrophage_poster.svg` / `.pdf`, 150 ppi raster `build/poster_150.png`)

| Review item | Change | Where |
|---|---|---|
| F01 endosomal release | "M6P released" → "acid pH: hydrolase / leaves M6PR". The phosphatase label now reads "later: phosphatase". The green carrier is labelled "M6PR recycles". | `src/m_m6p.py` |
| F02 diseases named | "silicosis: crystalline-silica lung disease" above 5.2. "asbestosis: asbestos fibrosis" under 5.3. | `src/m_patho.py` |
| F03 qualified conclusion | "Two routes converge to destroy microbes; persistent injurious particles can sustain inflammation and fibrosis." | `src/stage.py` |
| F04 no question mark | "pyroptosis?" → "possible lytic death". "re-uptake" → "possible re-uptake". Both stay dashed (dashed = possible in the legend). | `src/m_patho.py` |
| Silica is not the TLR ligand | "signal 1 · priming" → "signal 1 · priming (e.g. LPS)". No crystal is drawn at the TLR. | `src/m_patho.py` |
| Long fibre is illustrative | "> 15–20 µm" → "long fibre, e.g. >15 µm". | `src/m_patho.py` |
| SNAREs illustrative | "e.g." above syntaxin-7 / Vti1b / syntaxin-8 / VAMP7. | `src/m_vesicles.py` |
| Tissue strip | "interstitium (thickened)" added in the fibrotic septum. | `src/scene.py` |
| Provenance / scale caption | "Original illustration · …" → "Successive stages in one schematic cell · not to scale; molecular detail enlarged". | `src/stage.py` |

## Living poster (`Living_poster_v3/`)

- The scenes follow the new labels.
- The late-endosome beat now shows the hydrolase leaving M6PR at acid pH. Phosphate removal comes later as a separate step; the old animation showed the phosphate leaving as the release.
- The particles section tags lytic death as "possible · not inevitable". The fibre tag reads "a long fibre, e.g. > 15 µm". Beat "when it cannot" → "when particles persist".
- New: life under the magnifying glass (`js/life.js`, seeds in `data/life.js` from `src/export_life.py`). The cytosol jostles and streams, motors walk cargo along the microtubules, mitochondria release ATP and mRNAs leave the nucleus. Golgi carriers hop between cisternae. Protons thicken from nascent phagosome to phagolysosome, receptors drift in the membrane, red cells circle in the septal capillaries and the bacterium's flagella beat. A slow fluid field makes the drawn membranes sway, but only under the glass (`Loupe` in `js/main.js`). It backs off automatically if frames get slow.
- Performance pass, with no visual change. The lens's micro layer is now drawn directly instead of being re-cloned through `<use>`. Life particles are batched into a few paths, and attribute writes are cached. The full sheet stops painting while the opaque cover hides it. On the test machine, script and style time for a lens frame over the cytosol fell from ~80 ms to ~12–15 ms; scenes now take ~5–13 ms. Add `?fps` to the URL for a frame-rate readout.

## Living poster: motion & GPU pass (2 Nov 2026)

No labels, beats or biology changed; dashed still means possible.

- **GPU light layer.** New `js/gl.js` is a WebGL2 instanced-sprite layer between the sheet and the brass frame of the glass. It draws discs with bokeh, additive glows, rings, capsules, flares and an atlas of the poster's own sprite symbols. Without WebGL2 (or with `?nogl`) everything falls back to the old SVG drawing.
- **Life under the glass, on the GPU.** New `js/life_gl.js` draws:
  - a crowded cytosol with depth planes, depth of field, near-plane bokeh and persistent Brownian motion;
  - motors walking hand over hand, with an ATP flash on each step;
  - EB comets, mRNA leaving through the nuclear pores, ATP sparkle and silica glints.
- **The glass itself.**
  - In the gallery the live sheet is magnified and clipped directly; the old `<use>` clone was rebuilt every frame.
  - The glass opens and closes on a critically damped spring, and wheel resizing is smoothed.
  - After 7 s idle it drifts on its own over the best spots (attract mode; `?noattract` turns it off).
- **Camera and pace.**
  - Camera moves are quintic and finish on a damped post-spring, so an interrupted move never jumps.
  - Hand-held drift and shake moved to a compositor transform.
  - Shots are ~25 % shorter, catch-up on → is 6×, and section blends take 1.0–1.7 s.
- **Key moments get light:**
  - s2, s27: the lumen glows in the poster's pH-ribbon colour as it acidifies.
  - s4: SNARE zipper flash and fusion-pore bloom.
  - s27: hydrolase bite sparks, and the bacterium breaks into fragments that shrink away.
  - s5: silica lens flares, the NLRP3 snap, and the gasdermin pore spray.
  - s6: the convergence flash.
  - The opening dive has depth motes.
- **Loading.** The loading screen is new (breathing cell, progress bar). Every image, the hi-res tiles included, is decoded before it lifts, and the glass is swept over the tour spots under the curtain so the first hover does not stutter.
- **Science fixes from the independent review:**
  - s4 "c · pore": the hydrolases and H⁺ now stay in the lumen and leave only through the fusion neck.
  - s5: IL-1β leaves only through the two drawn GSDMD pores.
  - s2: the pH gauge's 6.5 → 5.5 ramp now starts at ~57 s.
- **Speed** (1600×900 and 1920×1080, DPR 2, uncapped): the glass ran at 27–41 fps before (worst frame 40–121 ms). It now runs at ~90–120 fps with p95 under 20 ms at every spot.

## Left open (not improvised)

- References are still the poster's own 13-item list. They have not been renumbered against the review's Vancouver list. The Hornung 2026 author correction is not cited yet.
- The optional GSDMD / IL-18 depth is kept. The review allows cutting it if Nora prefers.
- "reuse / recycled" products at the exporter are not itemised. The review's "nucleosides" wording was not added.
- Readability at 100 % print scale still has to be checked on a physical proof or a full-size crop of the PDF.
- Urtzi's script and rehearsal timing are outside the artwork.

## Poster: polish pass (2 Nov 2026)

Generator `src/`; master `Macrophage_poster.svg` / `.pdf` / `_150ppi.jpg`. Before/after views are in `build/poster_polish/`.

**Visual**
- Molecule labels are about 20 % larger. Every small sans label of 3.9–4.85 mm is now about 5.3–5.8 mm. This is set once in `lib.label_size()`, used by `T()`, `P()`, `text_width()` and `para_height()`. White text in pills is not scaled. Stacked lists got more line pitch: SNAREs, NOX2 subunits, COPII / GlcNAc-phosphotransferase / uncovering enzyme / clathrin, and "acid pH: hydrolase / leaves M6PR". "signal 1 · priming" was moved up so it no longer hits "ROS".
- Hierarchy is clearer: section marks are 16.5 (they were 13–14, the same size as organelle names). 2.7 Killing is 14.5.
- References: 4.1 mm (was 3.1). The three columns are sized so each reference fits on one line.
- Header: a hairline rule, a slightly larger key, and a clearer 2.7 badge. New scale lines: "Not to scale · molecular detail enlarged" and "cell ~20 µm · bacterium ~2 µm · receptor ~10 nm".
- Crowded cytosol: a new `src/cytosol.py` adds about 15k faint lit protein globules, polysomes, actin wisps and intermediate filaments. It is plate-only and kept at low contrast. Microtubules are restyled as hollow tubes; their paths are unchanged, so `export_paths` stays valid.
- Mitochondria were redrawn (`bio.mito`): a bent bean in world-aligned top-left light, inner and outer membrane, lamellar cristae and a rim highlight.
- Lighting: a soft top-left key light and a gentle warm vignette on the paper layer (`lenses.paper`).
- Fibrosis / inflammation corner (`scene.py`): a rose inflamed focus (hyperaemia / oedema) under the injured epithelium, with extra leukocytes. Collagen is sparser there. Fibrotic collagen is crisper and richer, with lit edges. The two zones now read separately.

**Scientific.** No errors were found that needed a change. All V2_brief and review-03 corrections still hold. The scale line uses textbook orders of magnitude.

**Living poster.** `build_v3_assets.py` and `export_life.py` were re-run.
- Actor ids and pivots are unchanged.
- Five cut-out bboxes grew by 1–8 mm because the labels inside them grew: `killing.nox2`, `fusion.station_b`, `m6p.er_translation`, `m6p.golgi_enzymes`, `m6p.le_interior`. Each actor image is cut to its own new bbox.
- The rest composite differs from the poster by 114 px at 100 dpi; this is covered by the 4 over-patches.
- `life.js` cytosol seeds: 2906 → 1677, because the new texture makes less cytosol "quiet". Air and tissue counts are similar.

## Poster: follow-up pass (2 Nov 2026, evening)

Master `Macrophage_poster.svg/.pdf/_150ppi.jpg` rebuilt at 20:03. The previous master (18:53) is kept in `build/master_1853/`.

| Change | Why | Where |
|---|---|---|
| The thesis V is the hero. The red phagocytic and blue enzyme ribbons are wider (56 / 50 mm), saturated, with luminous cores; a violet glow and halo mark where they converge at the phagolysosome. | Independent review: the centre read as empty and the V was too pale to see at full view. | `src/cellmod2.py` `ribbons()` |
| "signal 1 · priming (e.g. LPS)" moved off the ROS stars to the TLR → NF-κB side. New line: "NF-κB → NLRP3 + pro-IL-1β made". "ROS" relabelled beside its stars. | It read as "ROS = signal 1". Priming transcribes NLRP3 and pro-IL-1β. | `src/m_patho.py` `cascade()` |
| Caspase-1 now has cleavage arrows to pro-IL-1β/-18 and to GSDMD. New labels "pro-IL-1β / -18" and "GSDMD → GSDMD-N". | Caspase-1 had no outgoing arrow; the cytokines and the pore fragment appeared from nowhere. | `src/m_patho.py` |
| "5.1 uptake" now reads "via MARCO / SR-A". | Scavenger-receptor uptake of silica; reference 13 is about MARCO. | `src/m_patho.py` |
| "CR3" → "CR3 → RhoA". | CR3 (type II, "sinking") signals via RhoA, unlike FcγR → Cdc42/Rac. | `src/m_recognition.py` |
| Under NOX2: "burst starts at 2.3" and "iNOS: NO → ONOO⁻". | The burst begins at the nascent phagosome. Reactive nitrogen species are the macrophage-specific killing arm. | `src/m_vesicles.py` |

Still open:
- The legend's dotted lines (recycling, inflammatory) clash with "dashed = possible".
- Label collisions at the late endosome ("later: phosphatase", "acid pH…") and at "2.2 Pseudopod".
- Section 5 is cramped at the right edge.
- No static glows yet for NOX2 / the inflammasome / the GSDMD pores.

## Living poster: follow-up fixes (2 Nov 2026, evening)

- **s27, 0–13 s.** The NOX2 shots are framed wider (`scenes.js`, s27 `cam`). The whole subunit list and the new iNOS line now stay in frame. "Killing" no longer crowds the stopwatch.
- **s3, "the postcode".** The pencil envelope moved into open cytoplasm below the "3.2 cis-Golgi" name. GlcNAc-phosphotransferase and the Lys patch it explains are no longer covered.
- **Depth of field, every scene** (`main.js`). The blurred plate outside focus drops from 0.95 to 0.5 opacity and the dark veil from 0.34 to 0.24. The blurred plate carries no actors, so at full strength it ghosted moving parts and their labels: the "milky veil" the reviewer noted.
- **Loader** (`main.js`). The curtain lifts after at most 8 s, even on a slow disk or USB stick; the rest keeps decoding behind the show.
- **Checks.**
  - With WebGL: all 9 scenes at 15/50/85 %, the gallery glass at 6 spots, and autoplay — 0 console errors.
  - `?nogl` fallback and play mode (G) with a click — 0 console errors.
- **Left as is: s2 receptor shot (7–16 s).** The tall shot is already against the sheet's left edge, so some empty cytoplasm on the right is inherent at 16:9.
