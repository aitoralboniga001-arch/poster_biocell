# Macrophage poster V1.2: art direction and science brief

This is the shared spec for everyone building V1.2. V1.1 is the current `src/` (v6 renders in `build/v6_*.png`). Backups are in `src_v4_backup/`, and `build/v4_*` holds the original.

## The client's critique (summary)
The central macrophage works. Everything outside it still reads as **separate mini-diagrams or slides arranged around the cell**, and the composition is fragmented. The client wants the surroundings to become an **organic extension of the main illustration**, so the whole poster reads as one exceptional scientific illustration.

The illustrations should **explain mechanisms**, not decorate labels, and they should do it with publication-grade molecular drawing. In particular, recognition and the fusion sequence must stop looking like isolated educational icons.

Mandatory: a 110 x 90 cm landscape poster in English (first-year Medicine, Cell Biology seminar). It has one main macrophage with its cytoplasmic compartments and interactions, and it supports a 12–15 minute talk by 5 speakers.

## Chosen concept: "One alveolus, three scales"
I explored three options: a molecular "orbit" ribbon around the cell, this concept, and a left-to-right scale descent. The orbit becomes a decorative ring (a border) and the descent falls back into columns of cards. This concept turns the surroundings into **the macrophage's real environment**:

- **Tissue scale:** the whole sheet is the inside of one alveolus. The background is the alveolar air space.
  - An **alveolar wall** runs along the bottom of the poster: epithelium, basement membrane, thin interstitium and capillaries with RBCs.
  - The macrophage **rests on it**: the cell base is gently flattened where it adheres.
  - The wall changes continuously from **healthy (left)** to **fibrotic (right)**. Thin septum with type I and type II pneumocytes on the left. Thickened interstitium with collagen bundles, fibroblasts becoming α-SMA myofibroblasts, and recruited neutrophils/monocytes leaving capillaries on the right.
  - This gradient **replaces** the normal and fibrotic lung circles and the inflammation lens. Pathology becomes place, not panel.
- **Cell scale:** the macrophage stays the dominant focus at organelle scale.
- **Molecular scale:** only where a mechanism happens below organelle resolution. Each magnification is anchored to its exact site in the cell by a small hairline source ring and two fine focus lines. Each view is drawn so its membrane is **oriented like the real membrane at that site** (the recognition window's bilayer is vertical, like the left cell edge). Sequences are drawn as **one continuous strip** (membranes progress across the strip) instead of separate icon circles. No rims, no boxes, no drop shadows: content fades into the paper with a feathered mask, as in v6.

Reading path (= speaking order):
1. Top-left: intro and scale cue.
2. Left: recognition and actin window at the bacterium contact, then the phagocytic route (2.x) down the cell's left half.
3. Biosynthetic route (3.x) in the cell's upper right, plus the hydrolase-journey strip in the right column.
4. The fusion strip (lower left), magnified from site 4.
5. Back to section 2: the maturation and killing strip (lower left), magnified from 2.3–2.6.
6. Section 5, pathology: right column, the cell's lower-right edge with the asbestos fibre, and the wall's fibrotic right half.
7. Section 6, the conclusion: one sentence closing the poster under the wall.

## Composition grid (mm, sheet 1100 x 900; adjust ±15 mm if the drawing needs it)
| Zone | Box | Content |
|---|---|---|
| Header | y 0–84 | Title (keep "How a macrophage *destroys* what it engulfs"), with a shorter subtitle at left. Right side: "Cell Biology seminar · First-year Medicine", **speaking order** `1 Aitor · 2 Nerea · 3 Urtzi · 4 Eneritz · 5 Nora · 6 Aitor`, and a compact 2-row arrow key (phagocytic, enzyme route, fusion, recycling, pathological effect, inflammatory signal). **No institutional placeholder**: delete "[Faculty · University…]". Don't invent affiliations. |
| Left column | x 25–262, y 92–745 | **1** intro (y≈96–232): 2–3 short lines plus a small line-drawn **scale cue**: bronchiole → alveolar sac, one alveolus highlighted, "this scene". **2** recognition and actin window (y≈240–480). **4** fusion strip (y≈495–610). **2.7** maturation and killing strip (y≈625–745). |
| Cell | x≈265–860, y≈92–770 | Main macrophage, base resting on the wall. |
| Right column | x 872–1078, y 92–750 | **3** hydrolase-journey strip (y≈96–335). **5** particles (y≈345–750): exposure glyphs, fate note, 5.2 and 5.3 text, silica / NLRP3 window. |
| Alveolar wall | full width, y≈755–845 | Undulating band. Healthy (x<~520) blends into fibrotic (x>~760), thicker on the right. 5.4 and 5.5 labels sit on and above it at the right; healthy anatomy labels at the left. |
| Conclusion **6** | y≈848–862 | One serif sentence centred under the wall with a small "6" marker. Not a box, not a mini-slide. |
| References | y≈867–897 | 3 columns, small but readable (≥3.0 mm), numbered, journal format, quiet grey. |

Speaker names appear **only** in the header speaking order. Section headings keep the numbered badge but drop the name tags.

## Visual language (all modules)
- Fonts: unchanged. Sitka serif for the story and headings; Segoe UI Variable for figure labels.
- Sizes: body 6.2, labels ≥4.6, the smallest in-figure annotation **≥4.2 mm**, references ≥3.0.
- Palette (from `lib.py`): PHAG #E0452B, BIO #1F58C8, CONV #7A3FB5, RECY #1E9B6B, PATH #B4690E, INFL #C81D63, HPLUS #19B5E8, BACT #8C9A3A.
- **One colour per molecule identity across the whole poster**. Each identity must look identical in the cell, in the windows and in the key.

| Molecule | Colour |
|---|---|
| IgG / FcγR | navy-slate #3E5C86 |
| iC3b / CR3 | teal #1F8F8A |
| Mannose receptor | brown #8F5A2A |
| TLR4 / MD-2 / LPS | magenta #C2185B |
| MARCO scavenger receptor | ochre (PATH) |
| F-actin and Arp2/3 | orange #E07B39 |
| Rab5 | amber #E3A21A |
| Rab7 | red #C0392B |
| HOPS | violet (CONV) |
| SNAREs: Qa syntaxin-7 / Qb Vti1b / Qc syntaxin-8 / R VAMP7 | four distinct but harmonious hues |
| V-ATPase | rose |
| H+ | HPLUS |
| NOX2 complex | crimson (INFL) |
| M6P phosphate | gold #E2B33C |
| M6PR | green #1E8A5A |
| Clathrin | grey-blue |
| Hydrolase | cobalt (BIO) |

- Membranes are toned bilayers (two leaflets, pale core), drawn the same way as the v6 plasma membrane, at a larger scale in windows. Proteins are simple volumetric shapes lit from the top-left (`style.shade` / `spec`), sized plausibly relative to the bilayer (~5 nm).
- Magnifications use the v6 feathered `lens_open`/`lens_close` mask idea, but they are **not necessarily circles**. Strips can be wide ellipses or capsule shapes with feathered ends. Focus links are hairlines (0.25 mm) from a small hairline source ring at the exact site.
- Arrows use `lib.arrow` with the existing kinds and meanings. Annotation leaders are hairline curves.
- No boxes, cards, rules or borders anywhere outside the cell. Group things with whitespace and alignment.
- Avoid repetition: the cell shows **where** and **in what order**. Windows and strips show **how, at molecular scale**. Captions don't restate what the drawing already labels.

## Science: required content and corrections

### Recognition and engulfment (section 2, window at site 2.1)
- Show a Gram-negative envelope: outer membrane with LPS, a thin peptidoglycan layer and surface mannans. The surface carries IgG (Fab bound to antigen, Fc toward the cell) and covalently bound iC3b.
- Receptors in the macrophage bilayer:
  - FcγR, which binds IgG Fc. Its ITAM is phosphorylated by Src-family kinases, which recruits **Syk**.
  - **CR3** (CD11b/CD18 integrin, two subunits), which binds iC3b.
  - **Mannose receptor (CD206)**, which binds mannose-rich glycans.
  - **TLR4–MD-2 (with CD14)**, which binds LPS.
- Cytosolic side: Syk → PI3K → Rac/Cdc42 → WASP → **Arp2/3 branched F-actin (~70° branches)**. Barbed ends push the membrane outward into a pseudopod.
- **TLR4 wording (correction):** TLR4 is primarily an **LPS-sensing receptor that drives inflammatory signalling (MyD88 → NF-κB → cytokines)**. It can also influence phagocytosis and phagosome maturation. **Never write "only signals".**
- Remove the stray "CR1 binds C3b/C4b" sentence.
- This window **merges** the old receptor lens and the "engulfment zipper" chip chain. The signalling chain is drawn as molecules, not as text pills.

### Phagosome maturation (in the cell: 2.3 → 2.6)
- Rab5 is on the early phagosome. Rab conversion to Rab7 happens via the Mon1–Ccz1 GEF.
- V-ATPase accumulates as the phagosome matures, and the lumen acidifies: early ≈6.1–6.5, late ≈5.5–6, phagolysosome ≈4.5–5. Add a subtle pH tint along this path in the cell.
- NOX2 assembles on the nascent phagosome: gp91phox/p22phox in the membrane, plus cytosolic p47phox, p67phox, p40phox and Rac-GTP. This is the early oxidative burst.

### Fusion (section 4, strip magnified from site 4)
One continuous strip shows the late phagosome membrane and the lysosome membrane approaching each other.
- (a) **Tethering:** Rab7-GTP (and Arl8b on the lysosome) recruit the **HOPS** complex, which bridges the two membranes at a distance.
- (b) **Trans-SNARE zippering:** Qa syntaxin-7, Qb Vti1b and Qc syntaxin-8 pair with R VAMP7. **HOPS also chaperones SNARE assembly**: this is the explicit link between tethering and fusion. Zippering proceeds N→C and pulls the bilayers together.
- (c) **Hemifusion → fusion pore**, and the contents mix.
- (d) **NSF + α-SNAP** disassemble the cis-SNARE complex (ATP), so the SNAREs are recycled.

Tethering and SNARE fusion must read as **distinct but connected** steps.

### Maturation and killing (section 2.7, strip magnified from 2.3–2.6)
Show the phagosomal membrane at molecular scale over time:
- **Early:** NOX2 transfers electrons from cytosolic NADPH (→ NADP⁺) across the membrane to O₂ in the lumen → O₂•⁻ → H₂O₂ (via dismutation).
- **Late / phagolysosome:** V-ATPase uses ATP to pump H⁺ into the lumen. Acid hydrolases (cathepsins, lysozyme on peptidoglycan, lipases, nucleases, glycosidases) dismantle the bacterium. Transporters export amino acids, sugars and nucleotides to the cytosol for reuse.

ROS and acid hydrolases are **two distinct antimicrobial mechanisms**. Peptides may be presented on MHC II; keep that short and qualified ("can").

### Lysosomal biogenesis (section 3; organelles in the cell plus the hydrolase-journey strip)
The order and locations must be exact:
1. Rough ER: co-translational import, folding, N-linked glycosylation (Glc₃Man₉GlcNAc₂ precursor, then trimming).
2. COPII vesicles to the cis-Golgi.
3. cis-Golgi: **GlcNAc-1-phosphotransferase** recognises the hydrolase's lysine-based signal patch and adds GlcNAc-1-P to mannose.
4. TGN: the **uncovering enzyme** removes GlcNAc, exposing **M6P**, which binds the **M6P receptor** (near-neutral pH).
5. Clathrin / AP-1 / GGA vesicles carry it to the endosome.
6. Early/late endosome (pH ≈6 or below): the hydrolase is released from M6PR, the M6PR returns to the TGN (retromer), and the phosphate is removed.
7. The hydrolase arrives in the lysosome, which carries heavily glycosylated LAMP-1/2 in its membrane.

### Particles (section 5)
- **Particle persistence:** don't imply every particle has the same fate or is fully phagocytosed.
  - Particles that reach the alveoli are **often** taken up, notably via scavenger receptors such as **MARCO**.
  - Inorganic material **cannot be digested**.
  - The fate depends on size, shape and surface reactivity. Some particles stay extracellular, some are cleared up the airway, some reach the interstitium.
- **Asbestos (5.2), redrawn:**
  - A long fibre (>~15–20 µm) lies on the epithelium, outside the cell.
  - The macrophage spreads actin-driven pseudopods along it, but the cup **cannot close around it**. The fibre must **not** pierce an intact plasma membrane.
  - The open cup releases **ROS (plasma-membrane NOX2)** and **lysosomal enzymes** into the extracellular gap. This damages the epithelium below (wall right half) and sustains inflammation.
  - Short fibres can be engulfed but may persist.
- **Silica (5.3):**
  - A crystal in a phagolysosome **can destabilise** its membrane, so cathepsin B leaks into the cytosol.
  - Together with K⁺ efflux and ROS, this **can activate** the NLRP3 inflammasome (NLRP3 + ASC + pro-caspase-1 → caspase-1), which turns pro-IL-1β into IL-1β (and pro-IL-18 into IL-18).
  - **Possible outcomes, not a fixed sequence:** the macrophage may die (e.g. pyroptosis via gasdermin D), releasing the crystal, which may then be taken up again.
- **Inflammation (5.4), on the wall:** IL-1β, TNF-α and chemokines recruit neutrophils and monocytes from the capillaries. Their ROS and proteases can injure the epithelium. Biopersistent particles keep the stimulus going.
- **Fibrosis (5.5), on the wall:** macrophage TGF-β and PDGF drive fibroblast → myofibroblast (α-SMA) transition and collagen deposition. The septa thicken and stiffen, and **gas exchange is impaired** (never "fails").

### Conclusion (6)
One sentence, qualified. For example: *"Clearing a microbe needs two routes to converge: the maturing phagosome and the delivery of lysosomal enzymes. When the cargo cannot be degraded, the same machinery can sustain inflammation and drive fibrosis."*

## Engineering rules
- Build with `python build_poster.py [--out PATH]`. Render with `python render.py --svg S --pdf P --out PNG [--crop x y w h --dpi N]`. The temp HTML must be unique per PDF, so parallel renders don't collide.
- Phase-2 workers work in their own copy, `build/work_<name>/src`, and render there. They edit **only the files they own**: the integrator copies exactly those files back.
- Region constants live in `src/geom.py` (read-only in phase 2). Each module exposes `draw(doc)` and is called from `build_poster.py`.
- After every meaningful change, look at the renders (30 dpi full view, 100 dpi crops). Check for overlaps, clipping, illegible labels and arrows that point at nothing.

---
## V1.2b TEXT DIET (overrides everything above about captions and notes)
The owner's direction: **"This is a visual poster, there shouldn't be almost any text."** The speakers explain; the poster shows.
The current version has ~700 visible words outside the references. The target is **≤ ~150 words outside the references**.

**Keep, and only as short labels:**
- the title (no subtitle);
- the header speaking order;
- the arrow key (1–2 words each);
- section headings: badge plus a 1–3 word name, e.g. "2 Recognition", "4 Fusion", "2.7 Killing", "5 Particles";
- molecule and structure NAMES on the drawings, 1–3 words each (e.g. "FcγR", "HOPS", "V-ATPase", "M6P receptor", "NLRP3");
- essential numbers as data (pH values, "10 nm", "~20 µm");
- the references, which remain mandatory and stay small.

**Remove:**
- every caption and paragraph;
- every explanatory note under a label, e.g. "hydrolases are imported co-translationally…";
- the "Possible outcomes" sentences;
- the asbestos note;
- the 5.4 and 5.5 notes;
- the scale-key descriptions;
- most wall anatomy labels. Keep only ~3–4: type I and type II pneumocyte, capillary, and collagen or myofibroblast on the fibrotic side.

**Say it visually instead:**
- Possible or uncertain outcomes become **dashed arrows**, with at most one word, e.g. "possible".
- Sequences are carried by arrows and step letters or numbers.
- Contrasts (early vs late, healthy vs fibrotic) are carried by colour or tint plus a single word.

**Conclusion (6):** one short line, ≤ 15 words. For example: *"Two routes converge to destroy; when the cargo persists, the same machinery injures the lung."*

**Freed space:** don't leave holes. Let the drawings grow into it: larger windows and strips, more air, a calmer layout. The scientific content of the DRAWINGS must stay; only the words go.

**Science qualifiers still matter.** Express them graphically: dashed means possible. One word ("may", "possible") is allowed where a picture can't say it. The drawings must never imply an absolute.
