# The Living Poster: plan for the animated V2

> **One sentence.** We dive from a person taking a breath into the paper poster. A brass magnifying loupe shows that every printed drawing is secretly alive. Each speaker "dives through the loupe" into their part, where the mechanism plays out in ink and watercolour. At the end, years pass in seconds, the lung stiffens, and the five of us sign the poster.

Status: **plan only, nothing built yet.** Every choice below can be changed. Section 11 lists the ones to confirm.

---

## 0. The idea
The printed V2 poster is a still frame from a film that already exists. The animated version shows the rest of that film without ever stopping looking like the poster:
- same paper, same ink, same watercolour washes, same hand lettering;
- nothing appears that isn't on the poster, except a few pencil "margin doodles" and the instruments of a scientist's desk: a loupe, a microscope turret, a stopwatch.

**Amplify → come alive.** Zooming is never a plain digital zoom. It is always a physical act:
1. **the loupe** shows life under the glass;
2. **the microscope turret** clicks to a stronger objective, with a focus pull;
3. **the dive** through the loupe, where the lens ring grows until it becomes the screen.

---

## 1. The six surprise moments
These are the moments built to make the teacher sit up. Everything else supports them.

| # | Moment | Where | Why it lands |
|---|---|---|---|
| ★1 | **Powers of Ten opening.** A pen-sketched person in a dusty street takes a breath. The camera dives through the airway, bronchi and bronchiole, into one alveolus, which turns out to be the poster's own locator sketch. Then it dives into the poster. | Opening, 25 s | Starts at human scale and lands in the cell. Places the whole seminar in the body in one shot. |
| ★2 | **The loupe.** A hand-inked brass magnifier glides over the still poster. Under the glass, everything moves: receptors flicker, H⁺ stream, actin grows. Outside the glass, the paper stays still. | Overview, between speakers, Q&A | A clear "the drawing is alive" reveal. The teacher can drag it anywhere. |
| ★3 | **The bacterium's last journey, as one take.** The camera rides with the bacterium from capture to phagolysosome. As the pH falls, the whole frame warms, and a pH gauge drawn in ink drops 7.2 → 6.5 → 5.5 → 4.5. | Section 2 → 2.7 | A point-of-view shot of maturation that makes acidification something you can feel. |
| ★4 | **The enzyme gets its postcode.** A pencil doodle of an envelope briefly appears over the Golgi: M6P is the postcode, the TGN is the sorting office, M6PR is the postman, the clathrin coat is the mail bag. It dissolves back into the real molecules, which then do exactly that. | Section 3 | Turns the hardest concept in the seminar into a picture you can remember, then shows it is literally true. |
| ★5 | **The fibre breaks out of the poster.** In the asbestos scene the fibre keeps going past the paper's edge onto the dark "desk" around the poster, casting a shadow. The cell tries to close around it three times and can't. | Section 5 | Breaks the fourth wall to make "> 15–20 µm, too long to engulf" impossible to forget. |
| ★6 | **Decades in seconds.** A pen-drawn calendar flips 1 yr … 10 yr … 20 yr. Fibrosis creeps right to left along the wall, the alveoli narrow, and the poster's breathing, which has been gently running the whole time, becomes shallow and quick. Then the conclusion. Then the five of us sign the poster in ink, one signature per speaker, in speaking order. | 5 → 6 → Finale | Emotional and clinical: the audience feels the lung get stiff. The signatures turn a school poster into an artwork. |

Bonus for Q&A: **Feed the macrophage** (§6). The cursor becomes a tiny bacterium, and the poster's pseudopods reach for it.

---

## 2. Visual language: how motion stays a poster

### 2.1 Rules
1. **The poster is the stage.** Every moving thing is a printed part that starts to move. When a scene ends, everything settles back exactly into its printed place.
2. **Cinemagraph.** Mostly still, with chosen life. Periods are 4–20 s, eases are organic, nothing moves faster than 0.25 s, and nothing bounces.
3. **No new prose.** The only words are the poster's own labels. They light up as each molecule acts. The few additions are hand-lettered: speaker chips, the size tags, the stopwatch and the calendar.
4. **Dashed means possible**, here too. Pyroptosis and re-uptake play as ghosted, translucent, dashed animations with a "?".
5. **Science first.** Directions and order follow §9. Any metaphor is a pencil doodle (graphite grey, sketchy) that always dissolves into the real molecules.

### 2.2 Devices
These are the recurring "scientist's desk" props. They are all drawn with the poster's own `marks.ink()` hand and Gabriola lettering.

| Device | Look | Behaviour |
|---|---|---|
| **Loupe** | Brass ring (ink outline + warm watercolour wash), a short wooden handle, a soft glass highlight crescent | Follows the pointer with a lagging, damped motion (it feels heavy). Inside: the 300 dpi tile at 2.5× plus that zone's live actors. Scroll changes the power from 1.8× to 4×. A click dives: the ring grows to fill the screen and becomes the edge of the scene. |
| **Microscope turret** | Small ink drawing in the bottom-right corner: a revolving nosepiece with objectives **4× · 10× · 40× · 100× oil · EM** | Rotates and clicks to the objective that matches the camera magnification. Each change brings a **focus pull** (brief blur → sharp, 0.6 s). At the last stop the lettering reads *"EM · beyond light, < 200 nm"*. This marks the moment we go below the resolution of light: the scene flashes to a cool grey "electron micrograph" for 0.4 s, then colour returns. |
| **Real-size tag** | A handwritten tag on a thread, like a museum label | The poster is mixed-scale, so instead of a false scale bar each hero object gets an honest real size: macrophage ≈ 20 µm, bacterium ≈ 2 µm, alveolus ≈ 200 µm, lysosome ≈ 0.5 µm, receptor ≈ 10 nm, SNARE bundle ≈ 12 nm, GSDMD pore ≈ 20 nm, asbestos > 15–20 µm. |
| **Stopwatch** | Ink pocket watch in the top-right of a scene | Shows how compressed time is: "real time ≈ 30 min → 40 s". The ROS burst is "seconds", the SNARE zipper "≈ milliseconds", fibrosis "decades". The teacher sees that we know the time scales. |
| **Calendar** | Tear-off pad drawn in pencil | Only in ★6. The pages flip faster and faster. |
| **pH gauge** | Semicircular ink dial, coloured with the poster's pH ribbon | Rides along in ★3 and 2.7. |
| **Ink-in** | Labels and lines write themselves with a feathered wipe following the writing direction. The section badges *stamp* (scale 1.15 → 1, ink-spread ring). | Every reveal |
| **Watercolour bloom** | A wet-paint edge, from a pre-rendered noise mask | Transitions and lumen colour changes. The phagosome lumen bleeds from red to violet like wet paint. |
| **Breath** | The whole air space brightens and darkens; dust drifts in with each inhale; the alveolar wall flexes 1–2 mm | Always on (period 5 s). Becomes shallow and quick in ★6. The poster's heartbeat. |
| **Paper life** | Paper grain lit by a light that sweeps very slowly; a faint drop shadow under the sheet | Always on. Feels like a physical object. |

### 2.3 Motion palette
- Biology (membranes, organelles, vesicles): sine and cubic ease, slight overshoot only for membrane spring-back.
- Molecular machines (V-ATPase rotor, NSF): a steady mechanical spin, eased on start and stop.
- Signals: a bright pulse travelling along the poster's own arrows, about 120 mm/s, leaving a fading trail.
- Particles: Brownian jitter plus drift. H⁺ are quick and tiny, ROS twinkle (star sprites), cytokines tumble slowly.
- Glow budget: at most two strong glows on screen at once.
- Depth: a 1–2 % parallax between air dust, cell and wall during camera moves, for a quiet 2.5D.

---

## 3. Modes and controls

| Mode | Use | How it behaves |
|---|---|---|
| **Gallery** (layer A) | Before the talk, between speakers, after | The living poster. Loupe available. The "circle of life" ambient loop (§5). |
| **Talk** | The 12–15 min seminar | Sections in speaking order. Each beat holds and gently loops until → is pressed, so no one is ever rushed. |
| **Film** | Backup MP4 and to send the teacher | The whole talk auto-timed, about 6 min, plus the opening and finale. |
| **Play** | Q&A, or the teacher alone | Feed the macrophage (§6). |

| Key | Action |
|---|---|
| → / Space / click | next beat → next section |
| ← | previous beat / section |
| 1–6, 7 | jump to section (7 = 2.7 Killing) |
| Esc / 0 | back to the gallery |
| L | loupe on/off (also: just move the mouse in the gallery) |
| A | autoplay (film timing) |
| P | pause, freezing everything as the printed poster |
| G | play mode |
| F | fullscreen |
| H | show the key hints for 5 s |

The **speaker chip** ink-stamps in at the start of each section: "2 · Recognition — Nerea", in Gabriola, in the section colour. It fades after 4 s. A thin progress thread of six ink dots runs along the bottom edge and fades when idle.

---

## 4. Storyboard
Times are for film mode. In talk mode every beat loops until →.

Columns:
- **Picture**: what is on screen.
- **Comes alive**: the motion.
- **Lit**: the poster labels that glow.
- **Device**: the prop used.

### ★ Opening: Powers of Ten (Aitor, 25 s)
| t | Picture | Comes alive | Device |
|---|---|---|---|
| 0–3 s | Blank warm paper. The title inks itself in letter by letter; *destroys* is painted last, red, with the swash. | Ink-in | — |
| 3–7 s | The title floats up and shrinks into its poster place, which is not visible yet. A **pen sketch of a person** appears in a street with a building site behind: a dusty haze, sparkles of silica and a few long fibres. | Dust drifts, the person's chest rises | Size tag: "you · 1.7 m" |
| 7–12 s | The person breathes in. The camera dives toward the chest; the sketch's lungs appear in watercolour behind the ribs. | Air dots stream into the trachea | — |
| 12–18 s | Continuous dive down the bronchial tree, three branch levels. Each level is a new sketch that grows out of the previous one. It ends at the poster's **locator sketch**: lung → bronchiole → alveolar sac. | Air flows; branches flex | Turret clicks 4× → 10× |
| 18–22 s | The "this scene" circle in the locator glows. The camera passes **through** it, and the circle grows until it becomes the frame of the full poster. | Focus pull | Size tag "alveolus ≈ 200 µm" |
| 22–25 s | We are in the alveolus: the whole poster, alive. The breath continues from the person's breath, at the same rhythm. | Routes start to flow | Speaker chip "1 · Alveolar macrophage — Aitor" |

### 1 · Alveolar macrophage (Aitor; full poster; about 40 s)
| Beat | Picture | Comes alive | Lit | Device |
|---|---|---|---|---|
| 1a | Full poster | An ink glow traces the cell outline once, slowly | 1 Alveolar macrophage | Size tag "≈ 20 µm" on the cell |
| 1b | Full poster | The **loupe appears** and drifts over the poster, revealing life under the glass at the leading edge, the Golgi, the phagolysosome and the silica crystal (about 3 s each) | — | Loupe |
| 1c | Loupe stops on the bacterium | Click: **dive** into section 2 | — | Loupe dive |

### 2 · Recognition → phagocytosis → maturation (Nerea; ★3 one take; about 90 s)
Zone A first, at about 2.8×, then the red route.

| Beat | Picture | Comes alive | Lit | Device |
|---|---|---|---|---|
| 2a | Zone A | The bacterium drifts in from the left air and settles into its place. Opsonins glint like little "eat-me" flags. The LPS fringe shimmers. | Bacterium, LPS, IgG, iC3b, glycans | Size tag "≈ 2 µm" |
| 2b | Turret 40× → **EM** | Receptors reach across one by one, each with a bond flash: TLR4–MD-2 + CD14 → LPS; MR → glycans; CR3 → iC3b; FcγR → IgG. | TLR4–MD-2, CD14, MR, CR3, FcγR, 2.1 | EM flash, size tag "receptor ≈ 10 nm" |
| 2c | Same | Branch 1: TLR4 → MyD88; a pulse runs along the dotted arrow toward the nucleus. The nucleus gives one soft glow. | MyD88, NF-κB → inflammation | — |
| 2d | Same | Branch 2: ITAM phosphate dots pop (Src). Syk docks. PI3K. The pulse forks into **Cdc42 → WASP** and **Rac → WAVE**. | Src, ITAM, Syk, PI3K, Cdc42 → WASP, Rac → WAVE | — |
| 2e | Pull back to 40× | Arp2/3 nucleates. **Actin branches grow at 70°**, drawing in branch by branch like frost on glass. Their barbed ends push the membrane, which bulges outward. | Arp2/3, F-actin | — |
| 2f | 10× | The **pseudopod arms reach around the bacterium** (cross-fade through 4 rendered arm states). The tips meet and the cup seals with a soft membrane "kiss" ripple. | 2.2 Pseudopod | Stopwatch "≈ 1 min" |
| 2g | **One take begins** | The camera locks onto the bacterium, now inside the nascent phagosome, and travels down the red route. The pH gauge rides beside it. | 2.3 Nascent phagosome | pH gauge 7.2 |
| 2h | Early phagosome | Rab5-GTP dots light up. H⁺ trickle in. The gauge drops to **6.5**. The whole frame warms by one step. | 2.4, Rab5-GTP, pH 6.5 | Stopwatch "≈ 10 min" |
| 2i | Late phagosome | **Rab conversion on the same vesicle:** Rab5 dots fade as Rab7 dots bloom. The gauge drops to **5.5**. The bacterium dims. | 2.5, Rab7-GTP, pH 5.5 | Stopwatch "≈ 30 min" |
| 2j | Hold | A lysosome waits on the blue route. The take pauses: "to be continued in 4". | — | — |

### 3 · Lysosome biogenesis: "the enzyme gets its postcode" (Urtzi; ★4; about 100 s)
Zone D at about 2.4×. The camera follows **one hero enzyme**, the blue glyph.

| Beat | Picture | Comes alive | Lit | Device |
|---|---|---|---|---|
| 3a | Rough ER | mRNA slides through the ribosome. The chain threads through Sec61 into the lumen and folds (it scales in, with BiP alongside). | mRNA, ribosome, Sec61, BiP, 3.1 Rough ER | EM flash |
| 3b | Same | The N-glycan tree grows onto the enzyme. Three glucose dots pop off one by one. | glucose trimming, glycan key | — |
| 3c | ER → cis-Golgi | A COPII coat gathers, buds and hops the gap (a small arc), then uncoats and fuses. | COPII vesicle | — |
| 3d | cis-Golgi | The phosphotransferase docks on the Lys patch. GlcNAc-P is added: a yellow glint. | 3.2 cis-Golgi, Lys patch, GlcNAc-phosphotransferase, GlcNAc-P | — |
| 3e | **Margin doodle** | A pencil sketch appears over the stack: an envelope addressed "→ lysosome", and a stamp being pressed on it, labelled **M6P**. The camera holds 3 s, then the doodle dissolves like graphite smudged away. | — | Doodle |
| 3f | TGN | The uncovering enzyme clips GlcNAc. **M6P is exposed** (the "stamp" glows the same yellow as in the doodle). | uncovering enzyme, M6P, 3.3 TGN | — |
| 3g | TGN bud | The doodle comes back for 2 s: "sorting office". M6PR (the "postman") grabs M6P **in the lumen**. Clathrin triskelia gather on the cytosolic face like a net closing (AP-1/GGA). The bud pinches off. | M6PR, clathrin, AP-1 · GGA, 3.4 Clathrin bud | — |
| 3h | Late endosome | The V-ATPase rotor spins. H⁺ pour in, and the lumen deepens violet (watercolour bloom). **M6P lets go of M6PR.** The phosphatase strips the phosphate: the stamp is cancelled. | 3.5 Late endosome, V-ATPase, M6P released, phosphatase | — |
| 3i | Same | The empty M6PR rides the green dashed carrier back to the TGN ("the postman goes home"). | recycling | — |
| 3j | Lysosome | LAMP glints. The enzyme brightens to "active hydrolase". Two lysosomes set off down the blue route. | 3.6 Lysosome, LAMP, active hydrolase | Stopwatch "≈ 1 h" |

### 4 · Fusion: "the kiss" (Eneritz; bullet time; about 70 s)
Zone E around the late phagosome, about 3×, then EM.

| Beat | Picture | Comes alive | Lit | Device |
|---|---|---|---|---|
| 4a | The lysosome arrives; the one take from 2j resumes. | The two membranes approach | — | — |
| 4b | **Tether** | Rab7-GTP and Arl8b-GTP light up. HOPS reaches out and bridges them (the arch draws in). | a tether, Rab7, Arl8b, HOPS | — |
| 4c | **Bullet time** | Everything else in the cell slows to near-stillness and the paper dims. The stopwatch reads "≈ milliseconds". Four SNARE helices (syntaxin-7 · Vti1b · syntaxin-8 + VAMP7) **zip N → C**, the strokes drawing from the N-terminus toward the membranes, pulling them together. | b zipper, syntaxin-7, Vti1b, syntaxin-8, VAMP7, N → C | EM flash, size tag "≈ 12 nm" |
| 4d | **Pore** | The fusion pore opens like an iris. Hydrolases and H⁺ pour in. The lumen bleeds red → violet (watercolour bloom). Normal time resumes. | c pore | — |
| 4e | **Recycle** | NSF with α-SNAP grips the cis-SNARE bundle. ATP sparks, NSF turns, and the SNAREs spring apart and drift away, ready for reuse. | d recycle, NSF, α-SNAP | — |
| 4f | Pull back | The fused compartment flows along the violet arrow into the giant phagolysosome. **Both routes are now drawn as lit.** | 2.6 Phagolysosome | — |

### 2.7 · Killing: "the furnace" (Nerea; about 70 s)
Phagolysosome at about 3.2×.

| Beat | Picture | Comes alive | Lit | Device |
|---|---|---|---|---|
| 7a | Membrane | **NOX2 assembles:** p47 · p67 · p40phox and Rac-GTP slide from the cytosol and lock onto gp91phox · p22phox. | NOX2, gp91phox · p22phox, p47 · p67 · p40phox, Rac-GTP | EM flash |
| 7b | Same | NADPH → NADP⁺ glows on the cytosolic side. An e⁻ spark crosses. O₂ → O₂•⁻ → H₂O₂ star-bursts bloom **in the lumen**. | NADPH → NADP⁺, e⁻, O₂ → O₂•⁻ → H₂O₂ | Stopwatch "seconds" |
| 7c | Same | The V-ATPase spins and H⁺ stream in. The pH gauge returns and drops to **4.5**. The lumen glows like a kiln. | V-ATPase, H⁺, pH 4.5 | pH gauge |
| 7d | Lumen | The acid hydrolases wake as the pH falls (dim → bright): cathepsins, lipases, nucleases, lysozyme, each nibbling its own target. | cathepsins, lipases, nucleases, lysozyme | — |
| 7e | Same | The bacterium cracks, splits and crumbles into fragments. | — | Stopwatch "≈ minutes–hours" |
| 7f | **Circle of life** | Fragments leave through the transporter as amino-acid dots. **One dot floats all the way up to the ribosome on the ER and is built into the next enzyme.** The two routes become one loop. | reuse, recycled | — |

### 5 · Particles: "glass and needles" (Nora; ★5 + ★6; about 120 s)
Zones F/G and the wall.

| Beat | Picture | Comes alive | Lit | Device |
|---|---|---|---|---|
| 5a | Right air | Silica crystals sink through the air with each breath, glinting like glass (rainbow refraction sprites). One is engulfed. | 5 Particles, 5.1 uptake | Size tag "silica ≈ 1–5 µm" |
| 5b | Silica phagolysosome | The crystal presses on the membrane. **The membrane tears** (the tear grows along the rim). Cathepsin B leaks out. K⁺ dots leave the cell. ROS twinkle. | 5.2 Silica phagolysosome, cathepsin B, K⁺ efflux, ROS | — |
| 5c | NLRP3 | Signal 1 pulses TLR → NF-κB ("priming"). Signal 2 arrives. **NLRP3 monomers swing in and lock into a wheel, like clockwork.** ASC filaments polymerise out from the wheel. | signal 1 · priming, signal 2, NLRP3, ASC, inflammasome | EM flash |
| 5d | Same | Caspase-1 ignites. Pro-IL-1β/IL-18 diamonds split. GSDMD is cleaved and inserts; **pores open in the cell's own membrane** like irises. IL-1β/IL-18 stream into the air. | caspase-1, IL-1β · IL-18, GSDMD pore ~20 nm | Size tag "≈ 20 nm" |
| 5e | Right air, ghosted | **Possible** outcomes, translucent and dashed with a "?": a cell swells and bursts (pyroptosis?); the crystal is released and drifts toward a dashed "re-uptake" curve. | pyroptosis?, re-uptake | — |
| 5f | ★5 Asbestos | The camera pans to the base. The hood lip reaches along the fibre, strains, and falls back, **three times**, each attempt shorter and more tired. The camera pulls out: the fibre runs **beyond the paper's edge** onto the dark desk, with a cast shadow. ROS · enzymes seep from the open cup onto the epithelium. | 5.3 Asbestos, open cup, > 15–20 µm, ROS · enzymes | Size tag "> 15–20 µm" (on the desk, outside the poster) |
| 5g | Wall | IL-1β · TNF-α travel the dotted path. Neutrophils and monocytes squeeze out of the capillaries. Inflammatory cells pulse. | IL-1β · TNF-α, 5.4 Inflammation | — |
| 5h | ★6 **Decades** | The calendar appears and flips: 1 yr … 5 … 10 … 20 yr. TGF-β · PDGF reach the myofibroblasts. **Collagen spreads right → left along the wall** (cross-fade through 5 rendered fibrosis states). The alveoli narrow. **The breath becomes shallow and quick.** Red cells in the capillaries slow. | TGF-β · PDGF, 5.5 Fibrosis, collagen | Calendar |

### 6 · Conclusion: the V (Aitor; about 45 s)
| Beat | Picture | Comes alive | Lit |
|---|---|---|---|
| 6a | Full poster, still at the shallow breath | The poster dims a little | — |
| 6b | Same | The **red route** lights from the bacterium down to the phagolysosome, and the **blue route** from the ER down to the same point. They meet in a **bloom at the V**, like two rivers joining. | routes, 2.6 |
| 6c | Same | The pathology branch glows amber: silica, asbestos, the wall. | 5.x |
| 6d | Same | The conclusion line inks itself in. *destroys* gets its last brush sweep. | conclusion, title |

### ★ Finale (20 s)
| t | Picture |
|---|---|
| 0–8 s | Reverse dive: poster → locator → bronchiole → the person, who coughs once, gently. The breath returns to normal only for the healthy left half of the lungs: an honest ending. |
| 8–16 s | Back to the full poster. **Five ink signatures** write themselves along the bottom margin in speaking order (Aitor · Nerea · Urtzi · Eneritz · Nora), each in the colour of its section. |
| 16–20 s | Settle into gallery mode. The loupe waits on the paper for the teacher. |

---

## 5. Gallery mode: the "circle of life" loop
A seamless 60 s loop that tells the whole story at once, very quietly:
- **Red route:** a soft dot (a bacterium) every 12 s travels capture → phagolysosome, warming in colour on the way.
- **Blue route:** an enzyme dot every 9 s descends ER → lysosome. The M6PR recycling carrier makes a round trip every 15 s.
- **The two routes meet:** each time they meet at the V, a small violet bloom.
- **Recycling:** an amino-acid dot rises from the phagolysosome to the ER every 20 s, closing the loop.
- **Lumens:** V-ATPase H⁺ trickle into every acidic compartment; the pH ribbon shimmers.
- **Signals:** NF-κB pulses every 14 s.
- **Air:** silica glints sink slowly in the right-hand air; the asbestos cup breathes but never closes.
- **Wall:** red cells flow in the capillaries.
- **Breath:** 5 s period.
- **Light:** a slow light sweep across the paper every 20 s.

---

## 6. Play mode: "Feed the macrophage" (Q&A)
1. Press G. The cursor becomes a tiny ink bacterium with a wiggling flagellum.
2. Bring it near the leading edge: vector **pseudopod tendrils reach toward the cursor**, following it with a lag.
3. Click: the tendrils close, and the cursor-bacterium is engulfed and rides the red route as a dot to the phagolysosome. A counter in the corner shows "eaten: 3".
4. Press **S** to switch the cursor to a silica crystal: on engulfment the membrane tears and the NLRP3 wheel spins.
5. Press **X** for an asbestos fibre: the tendrils try and fail, and the counter says "frustrated: 1".

It is a playful way to re-ask the three outcomes, and the teacher will want to try it.

---

## 7. Technical architecture

### 7.1 Cut-out compositing driven by our generator
The poster is generated by Python, so we render the poster **without** the moving parts (the *plate*) and render each moving part **alone** (an *actor*) in identical coordinates. At rest, plate + actors = the printed poster.

**1. Actor tagging.** In the zone modules, `with actor(doc, 'recog.bacterium', pivot=(x, y)):` wraps the code that draws each moving part. A normal build is byte-identical.

**2. Build modes** in `lib.Doc`:
- `poster` (today's output);
- `plate` (actors skipped);
- `actor:<id>` (only that actor, plus `defs`).

**3. Rendered states.** Each changes a parameter on existing functions; the default is the printed state.

| Element | States |
|---|---|
| Pseudopod arms | 4: open → closed |
| Fusion pore | 3 |
| Silica membrane | 3: intact → torn |
| NLRP3 | 3: scattered → wheel |
| Bacterium | 4: whole → crumbled |
| Fibrosis extent along the wall | 5 |
| Alveolar lumen | 2: open / narrowed |
| Asbestos hood | 3: rest / reach / max |

**4. Vector actors** are exported as SVG path data:
- actin, the SNARE helices, routes, signal arrows, the M6PR loop, the conclusion line and the signatures, all drawn live with dash-offset;
- the play-mode tendrils, from the LEAD_MEM geometry.

**5. Raster actors** are transparent WebP at 300 dpi, cropped to their bounding box.

**6. Label registry.** `T()` and `marks.hand()` record each label's text, bbox, colour and zone. Scenes light labels by name with a soft halo behind them plus a 15 % lift, using the poster's real words.

**7. Plates and tiles.**
- Overview plate at 100 dpi.
- Zone tiles at 300 dpi, which allow about a 4× zoom crisp on 1080p.
- An extra 600 dpi tile only for the three EM shots (receptors, SNAREs, NLRP3).
- Tiles load lazily per section.

**8. `manifest.json`** holds actors (file, bbox mm, pivot, states, zone), paths (routes, COPII hop, clathrin path, M6PR loop, cytokine path, capillary centrelines, the play-mode reach area), labels and zone rects.

### 7.2 New artwork (drawn in Python with the same `marks` hand, so it matches)
| Group | Items |
|---|---|
| Opening and finale | The person in a dusty street; three bronchial-tree zoom sketches that nest into the existing locator |
| Props | Loupe; microscope turret (5 objective states); stopwatch; calendar pad (pages); pH gauge; size tags |
| Doodles | Three pencil margin doodles: the envelope with its M6P stamp, the sorting office, the postman |
| Finale and desk | Five signatures; the desk surround with the off-paper asbestos fibre and its shadow |

### 7.3 Engine (no libraries, works offline)
- **Files:** `index.html`, `engine.js`, `devices.js` (loupe, turret, stopwatch, gauge, calendar, chips), `ambient.js`, `scenes/s0_opening.js … s7_finale.js`, `play.js`, `assets/`.
- **Stage:** one SVG stage in poster mm (`viewBox 0 0 1100 900`), extended by a desk margin so the fibre and props can live off the paper.
- **Timeline:** deterministic; `render(t)` is a pure function of time.
  - Tweens: translate, rotate about a pivot, scale, opacity, path-follow, dash-draw, state cross-fade.
  - This enables scrubbing, held beats and frame-exact video export.
- **Camera:** eased `viewBox` interpolation. The turret, focus pull and EM flash are triggered by the zoom thresholds 1.4× / 2.5× / 3.5×.
- **Loupe:** an SVG `clipPath` circle follows the pointer through a damped spring. Inside it sits a second group showing the tile and actors at the loupe's power.
- **Watercolour bloom and focus pull:** pre-rendered noise masks and a pre-blurred plate, cross-faded. No live SVG filters on large layers.
- **Particles:** pooled, at most 300 live nodes; glows are pre-rendered sprites.
- **Performance target:** 60 fps at 1080p on a normal laptop, never below 30, measured via Chrome CDP.

### 7.4 Outputs
| File | Content |
|---|---|
| `Living_poster/index.html` + `assets/` | Opens offline by double-click in Chrome or Edge. About 50–70 MB, also zipped. |
| `Living_poster_film_1080p.mp4` | Film mode, about 8 min |
| `Living_poster_film_4k.mp4` | The same in 4K |
| `Living_poster_gallery_loop.mp4` | 60 s seamless loop for a screen beside the printed poster |
| Presenter cheat sheet (1 page) | Keys, plus the beat list for each speaker |

The exporter, `export_video.mjs`, uses Node 22's built-in WebSocket to drive headless Chrome over CDP. For each frame it calls `seek(t)` and captures a screenshot, then pipes the frames to ffmpeg (H.264, CRF 18, 30 fps). No npm packages.

---

## 8. Sound (optional, off by default)
A soft WebAudio bed, generated with no audio files:
- breathing noise that follows the breath cycle;
- a low hum in the furnace;
- glassy clicks for silica and the turret;
- the scratch of a pen for the signatures.

Off unless you press M, and baked into a second version of the film MP4.

---

## 9. Science checklist and the numbers we show
**Recognition**
- Opsonins sit on the bacterium, and each receptor engages its own ligand.
- TLR4 → MyD88 → NF-κB is signalling and inflammation, not engulfment by itself.
- Src phosphorylates the ITAM, then Syk docks.
- Cdc42 → WASP and Rac → WAVE are separate branches.
- Arp2/3 branches at 70°, and the barbed ends push the membrane.

**Maturation**
- Nascent → early (Rab5, ≈ 6.5) → late (Rab7, ≈ 5.5) → phagolysosome (≈ 4.5).
- Rab5 → Rab7 conversion happens on the same vesicle.

**Biogenesis**
- Sec61 translocation; N-glycan and glucose trimming in the ER.
- GlcNAc-phosphotransferase (Lys patch) in the cis-Golgi; the uncovering enzyme exposes M6P in the TGN.
- M6PR binds M6P in the lumen; clathrin, AP-1 and GGA are on the cytosolic face.
- Low pH releases M6P, then the phosphatase acts, and M6PR recycles.
- No hydrolase is ever in the cytosol. The doodle never shows the enzyme outside a membrane.

**Fusion**
- Rab7/HOPS (+ Arl8b) tether comes before the N → C SNARE zipper, then the pore.
- NSF + α-SNAP + ATP disassemble the cis-SNAREs.

**Killing**
- NOX2 cytosolic subunits + Rac assemble on the membrane.
- NADPH is cytosolic; superoxide forms in the lumen.
- The V-ATPase pumps H⁺ *in*; hydrolases are active at low pH.
- Amino acids are recycled to protein synthesis (the circle-of-life dot).

**Silica**
- Signal 1 (priming) + signal 2 (lysosomal damage → cathepsin B, K⁺ efflux, ROS).
- NLRP3 + ASC (filaments) → caspase-1 → IL-1β/IL-18 + GSDMD → pores.
- Pyroptosis and re-uptake are *possible*.

**Asbestos**
- Fibres longer than 15–20 µm are too long to engulf: the cup never closes and the fibre never pierces an intact membrane.
- ROS and enzymes leak onto the epithelium.
- IL-1β/TNF-α → inflammation; TGF-β/PDGF → myofibroblasts and collagen, narrowed alveoli, impaired gas exchange; this takes decades.

**Sizes and times on screen.** These are approximate on purpose; each carries "≈".

| Shown | Value |
|---|---|
| Macrophage | 20 µm |
| Bacterium | 2 µm |
| Alveolus | 200 µm |
| Lysosome | 0.5 µm |
| Receptor | 10 nm |
| SNARE bundle | 12 nm |
| GSDMD pore | 20 nm |
| Respirable silica | 1–5 µm |
| Light resolution limit | ≈ 200 nm |
| Phagosome maturation | ≈ 30 min |
| ER → lysosome | ≈ 1 h |
| Fusion | ms |
| ROS burst | seconds |
| Fibrosis | decades |

A fresh-context verifier checks every number against a textbook source before the export.

---

## 10. Build phases
| Phase | Who | Output | Exit test |
|---|---|---|---|
| P1 Pipeline | executor A | `actor()` tagging, build modes, the ~30 actors and states, plates, tiles, manifest, label registry | plate + actors at rest matches the printed poster: mean diff < 1/255, max local < 8/255; normal poster build unchanged |
| P2 Engine and devices | executor B, in parallel with P1 against a mock manifest | engine, camera, loupe, turret, focus pull, bloom, stopwatch, gauge, calendar, chips, controls, exporter | 60 fps gallery; loupe follows smoothly; 10 s test MP4 |
| P3 New art | executor C | person, bronchial-tree zooms, props, doodles, signatures, desk | contact sheet looks hand-made and matches the poster |
| P4 Scenes | four in parallel (opening + 1 + 6 + finale · 2 + 2.7 · 3 · 4 + 5) | the beats in §4; play mode | one-frame-per-beat contact sheet per scene; §9 passes |
| P5 Integration | me | timing pass, film timing, gallery loop | full run-through in the browser |
| P6 Verification | verifier (fresh) | science, numbers, alignment, performance, controls | CONFIRMED |
| P7 Export | me | HTML package, three MP4s, cheat sheet | everything opened and watched |

---

## 11. Decisions to confirm (defaults chosen)
1. **Who's in the opening sketch.** Default: an anonymous construction worker, which is relevant to silica and asbestos. Alternative: a student, i.e. "you".
2. **Signatures:** first names only, in speaking order.
3. **Play mode:** included, hidden behind G.
4. **Sound:** off by default.
5. **Talk pacing:** every beat waits for →.
6. **Screen:** 1920×1080 projector, scaling to 4K.
7. **QR code on the printed poster** linking to the living version. This would need the poster re-exported and the animation hosted somewhere. Default: no.

## 12. Risks and fallbacks
| Risk | Fallback |
|---|---|
| Some parts are drawn interleaved with others (e.g. actin inside the arm outline) | Redraw that part as a vector actor from the same geometry, with an underlay patch from the plate |
| Arm and fibrosis morphs | Cross-fade through rendered states, at enough states that it reads as motion |
| GPU memory | Lazy tiles, WebP, a 4096 px cap; 200 dpi on low-memory machines |
| School PC lacks Gabriola | All lettering is baked into the rasters; the chips fall back to Segoe Print |
| Browser or laptop failure in class | The 1080p film MP4 on a USB stick |
| Scope / time | Must-haves: ★1–★3, ★5, sections 1–6, gallery. Nice-to-haves, in order: ★6 calendar, signatures, ★4 doodles, play mode, sound, 4K. |
