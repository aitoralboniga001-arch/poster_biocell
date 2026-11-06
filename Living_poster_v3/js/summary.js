/* The "+" in the top-right corner: a small, quiet button that opens a mini summary of what is on screen right now.
   The panel follows the show live: section, speaker, and one line per beat, with the current beat marked.
   Key: I toggles it too. Pure DOM text, refreshed only when the scene or beat changes, so it costs nothing per frame. */
const Summary = {
  POSTER: [
    'One alveolar macrophage, shown as successive stages in a single schematic cell.',
    'Red route (left): bacterium → phagosome → phagolysosome.',
    'Blue route (top): ER → Golgi → lysosome, carrying the enzymes.',
    'The two routes meet at the phagolysosome (centre-bottom).',
    'Right side: silica, NLRP3 and asbestos. Below: the lung tissue.',
  ],
  SCENES: {
    open: ['The title writes itself.', 'A breath: the body at rest.', 'The dive: down the airways into one alveolus.'],
    intro: ['The opener, without words.', 'Into the poster.'],
    map: ['The whole poster.', 'The route through the sections, one per speaker.', 'Ready to start.'],
    s1: [
      'From the lung into an alveolus: the macrophage lives on the air-facing side.',
      'One cell, drawn as successive stages (not to scale).',
      'The question: the bacterium on the left, and the lung tissue below.',
    ],
    s2: [
      'A bacterium coated with opsonins (iC3b, IgG) and showing LPS.',
      'Receptors bind: TLR4-MD-2, CR3 and FcγR.',
      'TLR4 signals to NF-κB: the cell switches on its defences.',
      'Src → Syk → PI3K: the signal reaches the cytoskeleton.',
      'Arp2/3 builds branched actin and pushes the pseudopods out.',
      'The cup closes around the bacterium.',
      'Nascent phagosome: the bacterium is now inside.',
      'Early phagosome: Rab5, pH ≈ 6.5.',
      'Late phagosome: Rab7, pH ≈ 5.5.',
    ],
    s27: [
      'NOX2 subunits dock on the membrane.',
      'Oxidative burst: electrons jump and make superoxide (ROS).',
      'The V-ATPase pumps protons: the lumen drops to pH 4.5.',
      'Hydrolases wake up: cathepsins, lysozyme, nucleases, lipases.',
      'The bacterium cracks and falls apart.',
    ],
    s3: [
      'Translation: the signal sequence brings the hydrolase into the rough ER.',
      'Glucose trimming: quality control of the folded protein.',
      'COPII vesicles carry it to the Golgi.',
      'cis-Golgi: GlcNAc-phosphotransferase recognises the lysine patch.',
      'The postcode: a phosphate tag on mannose.',
      'The uncovering enzyme exposes mannose-6-phosphate (M6P).',
      'In the TGN, M6P receptors gather in a clathrin bud (AP-1 · GGA).',
      'Late endosome: the acid pH releases the hydrolase.',
      'The M6P receptor recycles back to the Golgi.',
      'Lysosome (LAMP): the enzymes are ready.',
    ],
    s4: [
      'A lysosome arrives at the late phagosome.',
      'a · Tether: Rab7, Arl8b and HOPS hold the two membranes together.',
      'b · Zipper: four SNARE helices zip N → C (milliseconds).',
      'c · Pore: the membranes fuse and the contents mix.',
      'd · Recycle: NSF and α-SNAP pull the used SNAREs apart.',
      'The phagolysosome is formed.',
      'Products reused: amino acids leave through the exporter and one rides back to the ER.',
    ],
    s5: [
      'Silica crystals are breathed in and engulfed.',
      'The phagolysosome membrane tears and cathepsin B spills out.',
      'K⁺ efflux and ROS: the NLRP3 inflammasome assembles with ASC.',
      'Caspase-1 releases IL-1β and IL-18 through gasdermin (GSDMD) pores.',
      'Possible outcomes: lytic cell death is possible, not inevitable.',
      'Asbestos: a fibre too long to engulf. Frustrated phagocytosis.',
      'Inflammation: neutrophils leave the capillaries.',
      'Decades: TGF-β and PDGF, collagen, fibrosis of the lung.',
    ],
    s6: [
      'The whole cell.',
      'The V: the red and blue routes converge on the phagolysosome.',
      'When particles persist, the same machinery causes harm.',
      'The injured lung: inflammation and fibrosis.',
    ],
    fin: ['Out of the alveolus, back through the body.', 'The team signatures.'],
  },
  PLAY: ['Feed the macrophage: S silica · X asbestos · B bacterium, then click the sheet.',
    'The bacterium is digested, silica tears the membrane, asbestos leaves the cell frustrated.'],

  open: false, key: '',
  init() {
    const b = document.createElement('button');
    b.id = 'sumBtn'; b.type = 'button'; b.tabIndex = -1; b.title = 'What is on screen (I)'; b.setAttribute('aria-label', b.title);
    b.innerHTML = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 4.5v11M4.5 10h11"/></svg>';
    const p = document.createElement('div'); p.id = 'sumPanel'; p.setAttribute('aria-live', 'polite');
    document.body.append(b, p);
    // never keep focus: Space and Enter must keep driving the talk, not re-press the button
    b.addEventListener('mousedown', e => e.preventDefault());
    b.addEventListener('click', e => { e.stopPropagation(); this.toggle(); });
    window.addEventListener('keydown', e => { if ((e.key === 'i' || e.key === 'I') && !e.ctrlKey && !e.metaKey && !e.altKey) this.toggle(); });
    p.addEventListener('mousedown', e => e.preventDefault());
    p.addEventListener('click', e => { if (e.target.closest('.x')) { e.stopPropagation(); this.toggle(); } });
    this.b = b; this.p = p;
    setInterval(() => this.open && this.update(), 250);
  },
  toggle() { this.open = !this.open; this.b.classList.toggle('on', this.open); this.p.classList.toggle('on', this.open); if (this.open) { this.key = ''; this.update(); } },
  update() {
    const s = App.si >= 0 ? SCENES[App.si] : null, mode = App.mode;
    const key = `${mode}|${s ? s.id : '-'}|${App.beat}`;
    if (key === this.key) return; this.key = key;
    const esc = t => String(t).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    let head, sub = '', lines, at = -1;
    if (mode === 'play') { head = 'Feed the macrophage'; lines = this.PLAY; }
    else if (!s) { head = 'The whole poster'; sub = 'How a macrophage destroys what it engulfs'; lines = this.POSTER; }
    else {
      head = s.num ? `${s.num} · ${s.title}` : { open: 'Prologue', intro: 'Opening', map: 'Route map', fin: 'Finale' }[s.id] || s.title;
      sub = [s.speaker, s.sub].filter(Boolean).join(' · ');
      lines = this.SCENES[s.id] || (s.beats || []).map(b => b[0]); at = App.beat;
    }
    this.p.innerHTML = `<button class="x" type="button" tabindex="-1" aria-label="Close">×</button><h4style="--c:${s && s.color ? s.color : '#1E2433'}">${esc(head)}</h4>` + (sub ? `<p class="sub">${esc(sub)}</p>` : '') +
      `<ol class="${at < 0 ? 'plain' : ''}">` + lines.map((l, i) => `<li class="${i === at ? 'now' : i < at ? 'past' : ''}">${esc(l)}</li>`).join('') + '</ol>';
  },
};
Summary.init();
