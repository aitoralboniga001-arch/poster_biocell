/**
 * devices.js — The Scientist's Desk Devices & Procedural WebAudio Sound (§2.2, §8)
 * - Loupe (★2): damped spring brass magnifier, scroll 1.8x-4.0x, live actors inside glass, click dive
 * - Microscope Turret: revolving nosepiece (4x · 10x · 40x · 100x oil · EM)
 * - Real-size Tags: museum tags on a thread ("you · 1.7 m", "≈ 20 µm", "> 15–20 µm" on desk, etc.)
 * - Stopwatch: ink pocket watch in top-right showing compressed time
 * - Calendar (★6): pencil tear-off pad flipping 1 yr … 5 yr … 10 yr … 20 yr
 * - pH Gauge (★3 & 2.7): semicircular ink dial (7.2 -> 6.5 -> 5.5 -> 4.5)
 * - WebAudio Sound (§8): breathing noise, furnace hum, glassy clicks, pen scratch (off by default, key M)
 */
(function () {
  'use strict';

  const OBJECTIVES = ['4×', '10×', '40×', '100× oil', 'EM'];

  const Devices = {
    engine: null,

    // Loupe state (★2)
    loupe: {
      enabled: true,       // Active in gallery mode or when toggled with L / scripted in Scene 1
      scripted: false,     // True during Beat 1b/1c scripted glide & dive
      x: 340,
      y: 390,
      targetX: 340,
      targetY: 390,
      vx: 0,
      vy: 0,
      power: 2.5,          // 1.8x to 4.0x
      baseRadius: 66,
      diveProgress: 0,     // 0 = normal loupe, 1 = ring expanded to frame the screen
      pointerMoved: false
    },

    // Turret state
    turret: {
      activeObj: '4×',
      wheelAngle: 0,
      targetAngle: 0
    },

    // Frame-resettable scene props (populated during render(t) by active beat)
    frameProps: {
      stopwatch: null,
      phGauge: null,
      calendar: null,
      sizeTags: []
    },

    // WebAudio procedural synthesizer (§8, off by default)
    sound: {
      enabled: false,
      ctx: null,
      breathGain: null,
      furnaceGain: null,
      lastScratchAt: 0
    },

    init(engine) {
      this.engine = engine;
      this._buildLoupeDom();
      this._buildTurretDom();
      this._buildStopwatchDom();
      this._initPointerListeners();

      // Update Loupe HUD button
      const btn = document.getElementById('btn-loupe');
      if (btn) btn.classList.toggle('active', this.loupe.enabled);
    },

    hideSceneProps() {
      this.loupe.scripted = false;
      this.loupe.diveProgress = 0;
      this.frameProps.stopwatch = null;
      this.frameProps.phGauge = null;
      this.frameProps.calendar = null;
      this.frameProps.sizeTags = [];
    },

    // ==========================================================================
    // 1. Loupe (★2) Construction & Live-Under-Glass Magnification
    // ==========================================================================
    _buildLoupeDom() {
      const E = this.engine;
      const svgProps = E.dom.layerPropsSvg;

      this.stagePropsGroup = E.createSvgEl('g', { id: 'scene-stage-props' });
      svgProps.appendChild(this.stagePropsGroup);

      this.loupeRoot = E.createSvgEl('g', { id: 'loupe-root', style: 'display:none;' });

      // Clipped inner magnified world (shows poster at 2.5x + animated live micro-actors inside the glass!)
      this.loupeClippedWorld = E.createSvgEl('g', {
        id: 'loupe-clipped-world',
        'clip-path': 'url(#loupe-clip)'
      });

      this.loupeInnerTransform = E.createSvgEl('g', { id: 'loupe-inner-transform' });
      this.loupePlateImg = E.createSvgEl('image', {
        x: '0', y: '0', width: '1100', height: '900',
        preserveAspectRatio: 'none',
        href: E.activePlateUrl || 'assets/poster_fallback.jpg'
      });
      this.loupeLiveActors = E.createSvgEl('g', { id: 'loupe-live-actors' });

      this.loupeInnerTransform.appendChild(this.loupePlateImg);
      this.loupeInnerTransform.appendChild(this.loupeLiveActors);
      this.loupeClippedWorld.appendChild(this.loupeInnerTransform);

      // Warm glass tint & subtle inner vignette inside the lens
      this.loupeGlassTint = E.createSvgEl('circle', {
        cx: '340', cy: '390', r: '66',
        fill: '#FFFDF5', opacity: '0.08', 'pointer-events': 'none'
      });
      this.loupeClippedWorld.appendChild(this.loupeGlassTint);

      // Physical Brass Ring, Wooden Handle & Specular Highlight Crescent
      this.loupeFrameGrp = E.createSvgEl('g', { id: 'loupe-frame-hardware', 'pointer-events': 'none' });

      this.loupeRoot.appendChild(this.loupeClippedWorld);
      this.loupeRoot.appendChild(this.loupeFrameGrp);
      svgProps.appendChild(this.loupeRoot);
    },

    updateLoupePlate(src) {
      if (this.loupePlateImg) {
        this.loupePlateImg.setAttribute('href', src);
      }
    },

    _initPointerListeners() {
      const stage = this.engine.dom.stage;

      stage.addEventListener('pointermove', (e) => {
        const pt = this.clientToPoster(e.clientX, e.clientY);
        this.loupe.targetX = pt.x;
        this.loupe.targetY = pt.y;
        this.loupe.pointerMoved = true;
      });

      // Scroll wheel changes loupe magnification from 1.8x to 4.0x (§2.2)
      stage.addEventListener('wheel', (e) => {
        if (!this.loupe.enabled && this.engine.mode !== 'gallery') return;
        e.preventDefault();
        const delta = e.deltaY < 0 ? 0.2 : -0.2;
        this.loupe.power = this.engine.Ease.clamp(this.loupe.power + delta, 1.8, 4.0);
        this.playGlassyClick(2100 + this.loupe.power * 250);
      }, { passive: false });
    },

    clientToPoster(clientX, clientY) {
      const svg = this.engine.dom.stage;
      const rect = svg.getBoundingClientRect();
      const [vx, vy, vw, vh] = this.engine.camera.currentBox;
      const scaleX = vw / rect.width;
      const scaleY = vh / rect.height;
      const scale = Math.max(scaleX, scaleY);
      const drawnW = vw / scale;
      const drawnH = vh / scale;
      const offX = rect.left + (rect.width - drawnW) * 0.5;
      const offY = rect.top + (rect.height - drawnH) * 0.5;
      return {
        x: vx + (clientX - offX) * scale,
        y: vy + (clientY - offY) * scale
      };
    },

    toggleLoupe() {
      this.loupe.enabled = !this.loupe.enabled;
      const btn = document.getElementById('btn-loupe');
      if (btn) btn.classList.toggle('active', this.loupe.enabled);
      this.playGlassyClick(1850);
    },

    setScriptedLoupe({ x, y, power = 2.5, dive = 0 }) {
      this.loupe.scripted = true;
      this.loupe.x = x;
      this.loupe.y = y;
      this.loupe.targetX = x;
      this.loupe.targetY = y;
      this.loupe.power = power;
      this.loupe.diveProgress = dive;
    },

    handleStageClick(e, engine) {
      // In Gallery mode with Loupe active: clicking dives through the loupe into the clicked zone! (§2.2)
      if (engine.mode === 'gallery' && this.loupe.enabled) {
        const pt = this.clientToPoster(e.clientX, e.clientY);
        this.playGlassyClick(1450);
        // Map poster coordinates (pt.x, pt.y) to corresponding speaker section
        if (pt.x < 250 && pt.y < 248) {
          engine.jumpToSection('1');
        } else if (pt.x < 360 && pt.y >= 248) {
          engine.jumpToSection('2');
        } else if (pt.x >= 550 && pt.y < 480) {
          engine.jumpToSection('3');
        } else if (pt.x >= 410 && pt.x < 575 && pt.y >= 540 && pt.y < 755) {
          engine.jumpToSection('4');
        } else if (pt.x >= 575 && pt.x < 745 && pt.y >= 540 && pt.y < 755) {
          engine.jumpToSection('2.7');
        } else if (pt.x >= 745 && pt.y >= 470) {
          engine.jumpToSection('5');
        } else if (pt.y >= 820) {
          engine.jumpToSection('6');
        } else {
          engine.jumpToSection('1');
        }
        return true;
      }
      return false;
    },

    _renderLoupe(t, engine) {
      const showLoupe = this.loupe.scripted || (this.loupe.enabled && engine.mode === 'gallery');
      if (!showLoupe) {
        this.loupeRoot.style.display = 'none';
        return;
      }
      this.loupeRoot.style.display = '';

      // If in gallery mode and pointer hasn't moved yet, glide gently in a figure-8 over the cell
      if (!this.loupe.scripted) {
        if (!this.loupe.pointerMoved) {
          this.loupe.targetX = 520 + Math.cos(t * 0.32) * 340;
          this.loupe.targetY = 440 + Math.sin(t * 0.54) * 210;
        }
        // Damped spring motion so the brass loupe feels heavy (§2.2)
        const dt = 1 / 60;
        const stiffness = 95;
        const damping = 14;
        const ax = (this.loupe.targetX - this.loupe.x) * stiffness - this.loupe.vx * damping;
        const ay = (this.loupe.targetY - this.loupe.y) * stiffness - this.loupe.vy * damping;
        this.loupe.vx += ax * dt;
        this.loupe.vy += ay * dt;
        this.loupe.x += this.loupe.vx * dt;
        this.loupe.y += this.loupe.vy * dt;
        this.loupe.diveProgress = 0;
      }

      const lx = this.loupe.x;
      const ly = this.loupe.y;
      const dive = engine.Ease.smoother(this.loupe.diveProgress);
      const r = engine.Ease.lerp(this.loupe.baseRadius, 920, dive);
      const pwr = engine.Ease.lerp(this.loupe.power, 1.0, dive);

      // Update clip circle
      const clipCirc = document.getElementById('loupe-clip-circle');
      if (clipCirc) {
        clipCirc.setAttribute('cx', lx.toFixed(2));
        clipCirc.setAttribute('cy', ly.toFixed(2));
        clipCirc.setAttribute('r', r.toFixed(2));
      }

      this.loupeGlassTint.setAttribute('cx', lx.toFixed(2));
      this.loupeGlassTint.setAttribute('cy', ly.toFixed(2));
      this.loupeGlassTint.setAttribute('r', r.toFixed(2));

      // Magnify around (lx, ly) at power pwr
      const tf = `translate(${lx.toFixed(2)} ${ly.toFixed(2)}) scale(${pwr.toFixed(3)}) translate(${(-lx).toFixed(2)} ${(-ly).toFixed(2)})`;
      this.loupeInnerTransform.setAttribute('transform', tf);

      // Populate live moving biology inside the loupe glass ("Amplify -> come alive", ★2)
      this._renderLoupeLiveBiology(t, engine);

      // Draw hand-inked brass ring, wooden handle & glass highlight crescent
      const rimW = 6.2 * (1 + dive * 1.5);
      const handleLen = 82;
      const ang = 42 * (Math.PI / 180);
      const hx0 = lx + Math.cos(ang) * (r + rimW * 0.4);
      const hy0 = ly + Math.sin(ang) * (r + rimW * 0.4);
      const hx1 = lx + Math.cos(ang) * (r + handleLen);
      const hy1 = ly + Math.sin(ang) * (r + handleLen);

      // Specular crescent arc from 205 deg to 255 deg
      const rSpec = r * 0.84;
      const sx0 = lx + Math.cos(205 * Math.PI / 180) * rSpec;
      const sy0 = ly + Math.sin(205 * Math.PI / 180) * rSpec;
      const sx1 = lx + Math.cos(255 * Math.PI / 180) * rSpec;
      const sy1 = ly + Math.sin(255 * Math.PI / 180) * rSpec;

      this.loupeFrameGrp.innerHTML = `
        <!-- Cast shadow of loupe on paper -->
        <circle cx="${(lx + 4.5).toFixed(1)}" cy="${(ly + 6.5).toFixed(1)}" r="${(r + rimW * 0.5).toFixed(1)}"
                fill="none" stroke="#2B1810" stroke-width="${(rimW + 4).toFixed(1)}" opacity="${(0.28 * (1 - dive)).toFixed(2)}"/>
        <line x1="${(hx0 + 4).toFixed(1)}" y1="${(hy0 + 6).toFixed(1)}" x2="${(hx1 + 5).toFixed(1)}" y2="${(hy1 + 8).toFixed(1)}"
              stroke="#2B1810" stroke-width="16" stroke-linecap="round" opacity="${(0.28 * (1 - dive)).toFixed(2)}"/>
        <!-- Turned wooden handle -->
        <line x1="${hx0.toFixed(1)}" y1="${hy0.toFixed(1)}" x2="${hx1.toFixed(1)}" y2="${hy1.toFixed(1)}"
              stroke="url(#wood-handle-grad)" stroke-width="13.5" stroke-linecap="round"/>
        <line x1="${hx0.toFixed(1)}" y1="${hy0.toFixed(1)}" x2="${hx1.toFixed(1)}" y2="${hy1.toFixed(1)}"
              stroke="#1E2433" stroke-width="14.5" stroke-linecap="round" fill="none" opacity="0.35"/>
        <!-- Brass ferrule collar -->
        <circle cx="${hx0.toFixed(1)}" cy="${hy0.toFixed(1)}" r="6.2" fill="url(#brass-rim-grad)" stroke="#1E2433" stroke-width="1.1"/>
        <!-- Hand-inked Brass Ring (warm watercolour wash + double ink lines) -->
        <circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="${r.toFixed(1)}"
                fill="none" stroke="url(#brass-rim-grad)" stroke-width="${rimW.toFixed(1)}"/>
        <circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="${(r + rimW * 0.5).toFixed(1)}"
                fill="none" stroke="#1E2433" stroke-width="1.35"/>
        <circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="${(r - rimW * 0.48).toFixed(1)}"
                fill="none" stroke="#1E2433" stroke-width="1.1"/>
        <!-- Glass specular highlight crescent -->
        <path d="M${sx0.toFixed(1)},${sy0.toFixed(1)} A${rSpec.toFixed(1)},${rSpec.toFixed(1)} 0 0 1 ${sx1.toFixed(1)},${sy1.toFixed(1)}"
              fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" opacity="${(0.68 * (1 - dive)).toFixed(2)}"/>
        <!-- Engraved Loupe Power tag on brass rim -->
        <text x="${(lx).toFixed(1)}" y="${(ly - r - rimW * 0.85).toFixed(1)}"
              font-family="Gabriola, 'Segoe Print', serif" font-size="11" font-weight="600"
              fill="#1E2433" text-anchor="middle" stroke="#F8F3E8" stroke-width="2.2" paint-order="stroke"
              opacity="${(1 - dive).toFixed(2)}">loupe · ${this.loupe.power.toFixed(1)}×</text>
      `;
    },

    _renderLoupeLiveBiology(t, engine) {
      // Renders active moving biological elements ONLY inside the loupe glass so that even when
      // the poster outside is completely still (e.g. Beat 1b or paused), under the glass it lives!
      const g = this.loupeLiveActors;
      g.innerHTML = '';

      // 1. Leading edge receptors flickering & actin filaments pulsing (Zone A: 60..220, 290..490)
      for (let i = 0; i < 6; i++) {
        const y = 320 + i * 26;
        const pulse = 0.5 + 0.5 * Math.sin(t * 3.8 + i * 1.1);
        g.appendChild(engine.createSvgEl('circle', {
          cx: (126 + Math.sin(t * 2.5 + i) * 2.5).toFixed(1),
          cy: y.toFixed(1),
          r: (2.2 + pulse * 1.8).toFixed(2),
          fill: i % 2 === 0 ? '#FFE066' : '#E07B39',
          opacity: (0.45 + 0.45 * pulse).toFixed(2)
        }));
      }

      // 2. Golgi & ER M6P gold stamps glinting & vesicles bobbing (Zone D: 700..940, 150..440)
      const golgiPts = [[907, 222], [855, 245], [818, 308], [770, 326], [718, 374], [757, 433]];
      golgiPts.forEach(([gx, gy], idx) => {
        const dx = Math.cos(t * 2.2 + idx) * 2.8;
        const dy = Math.sin(t * 2.7 + idx) * 2.2;
        g.appendChild(engine.createSvgEl('circle', {
          cx: (gx + dx).toFixed(1),
          cy: (gy + dy).toFixed(1),
          r: '3.4',
          fill: idx < 3 ? '#E2B33C' : '#1F58C8',
          stroke: '#FFFFFF',
          'stroke-width': '0.7',
          opacity: '0.85'
        }));
      });

      // 3. Phagolysosome H+ ions streaming & ROS stars twinkling (Zone E: 622, 665)
      for (let k = 0; k < 10; k++) {
        const a = (k * 36 + t * 48) * Math.PI / 180;
        const rad = 16 + ((k * 13 + t * 22) % 38);
        const px = 622 + Math.cos(a) * rad;
        const py = 665 + Math.sin(a) * rad;
        g.appendChild(engine.createSvgEl('use', {
          href: k % 2 === 0 ? '#sprite-hplus' : '#sprite-ros',
          transform: `translate(${px.toFixed(1)} ${py.toFixed(1)}) rotate(${(t * 90 + k * 45).toFixed(0)}) scale(1.25)`
        }));
      }

      // 4. Silica crystal rainbow glints & NLRP3 wheel rotation (Zone F: 850, 560 & 918, 655)
      const silGlints = [[862, 572], [836, 582], [1072, 220], [1028, 288]];
      silGlints.forEach(([sx, sy], idx) => {
        const s = 0.6 + 0.7 * Math.abs(Math.sin(t * 3.1 + idx * 1.4));
        g.appendChild(engine.createSvgEl('use', {
          href: '#sprite-glint',
          transform: `translate(${sx} ${sy}) rotate(${(t * 60).toFixed(0)}) scale(${s.toFixed(2)})`
        }));
      });
    },

    // ==========================================================================
    // 2. Microscope Turret (#hud-turret in bottom-right corner, §2.2)
    // ==========================================================================
    _buildTurretDom() {
      const svg = document.getElementById('hud-turret');
      if (!svg) return;
      svg.innerHTML = '';

      // Click turret to cycle zoom/sections in interactive mode
      svg.addEventListener('click', (e) => {
        e.stopPropagation();
        this.playGlassyClick(2400);
      });
    },

    onObjectiveChange(newObj) {
      this.turret.activeObj = newObj;
      this.playGlassyClick(newObj === 'EM' ? 3100 : 1950);
    },

    _renderTurret() {
      const svg = document.getElementById('hud-turret');
      if (!svg) return;
      const activeObj = this.engine.camera.objective || '4×';
      const activeIdx = Math.max(0, OBJECTIVES.indexOf(activeObj));
      const isEM = activeObj === 'EM';

      // Render hand-inked revolving nosepiece in poster style
      let barrelsHtml = '';
      OBJECTIVES.forEach((label, idx) => {
        const rel = idx - activeIdx;
        const angleDeg = rel * 28;
        const rad = angleDeg * (Math.PI / 180);
        const cx = 108 + Math.sin(rad) * 44;
        const cy = 26 + Math.cos(rad) * 34;
        const isCurrent = idx === activeIdx;
        const bandColor = idx === 0 ? '#C0392B' : idx === 1 ? '#E2B33C' : idx === 2 ? '#1F58C8' : idx === 3 ? '#FFFFFF' : '#7A3FB5';
        const op = isCurrent ? 1.0 : Math.max(0.35, 0.85 - Math.abs(rel) * 0.22);
        const scale = isCurrent ? 1.12 : 0.86;

        barrelsHtml += `
          <g transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)}) rotate(${(-angleDeg * 0.55).toFixed(1)}) scale(${scale})" opacity="${op.toFixed(2)}">
            <rect x="-9" y="-14" width="18" height="28" rx="3" fill="${isCurrent ? '#EAE2D0' : '#D5CCB8'}" stroke="#1E2433" stroke-width="${isCurrent ? '1.8' : '1.2'}"/>
            <rect x="-9" y="2" width="18" height="4.5" fill="${bandColor}" stroke="#1E2433" stroke-width="0.8"/>
            <rect x="-6" y="14" width="12" height="6" rx="1.5" fill="#2A303D" stroke="#1E2433" stroke-width="1"/>
            <text x="0" y="-2" font-family="'Segoe UI Variable Text', sans-serif" font-size="7.5" font-weight="700"
                  fill="#1E2433" text-anchor="middle">${label.replace(' oil', '')}</text>
          </g>
        `;
      });

      const captionText = isEM
        ? 'EM · beyond light, &lt; 200 nm'
        : `Objective · ${activeObj} (${this.engine.camera.mag.toFixed(1)}×)`;

      svg.innerHTML = `
        <!-- Parchment backing card -->
        <rect x="6" y="8" width="203" height="120" rx="14" fill="#F8F3E8" fill-opacity="0.93" stroke="#1E2433" stroke-width="1.8"/>
        <!-- Revolving brass/ink nosepiece disc -->
        <ellipse cx="108" cy="24" rx="58" ry="15" fill="url(#brass-rim-grad)" stroke="#1E2433" stroke-width="1.6"/>
        <ellipse cx="108" cy="21" rx="46" ry="10" fill="#3A4150" stroke="#1E2433" stroke-width="1.2"/>
        ${barrelsHtml}
        <!-- Active objective label in Gabriola -->
        <text x="108" y="102" font-family="Gabriola, 'Segoe Print', serif" font-size="18.5" font-weight="600"
              fill="${isEM ? '#7A3FB5' : '#1E2433'}" text-anchor="middle">${captionText}</text>
        <text x="108" y="118" font-family="'Sitka Text', Georgia, serif" font-size="9.5"
              fill="#5E5748" text-anchor="middle">4× · 10× · 40× · 100× oil · EM</text>
      `;
    },

    // ==========================================================================
    // 3. Stopwatch (#hud-stopwatch in top-right corner, §2.2)
    // ==========================================================================
    _buildStopwatchDom() {
      this.stopwatchSvg = document.getElementById('hud-stopwatch');
    },

    showStopwatch(mainLabel, subLabel = '', speed = 1.0) {
      this.frameProps.stopwatch = { mainLabel, subLabel, speed };
    },

    _renderStopwatch(t) {
      const svg = this.stopwatchSvg;
      if (!svg) return;
      const sw = this.frameProps.stopwatch;
      if (!sw) {
        svg.classList.remove('visible');
        return;
      }
      svg.classList.add('visible');

      const handAngle = (t * 60 * sw.speed) % 360;
      const slowAngle = (t * 8 * sw.speed) % 360;
      const rad = (handAngle - 90) * (Math.PI / 180);
      const srad = (slowAngle - 90) * (Math.PI / 180);
      const cx = 46;
      const cy = 58;
      const r = 34;

      let ticks = '';
      for (let i = 0; i < 12; i++) {
        const a = (i * 30) * (Math.PI / 180);
        const r0 = i % 3 === 0 ? r - 6 : r - 3.5;
        ticks += `<line x1="${(cx + Math.cos(a) * r0).toFixed(1)}" y1="${(cy + Math.sin(a) * r0).toFixed(1)}"
                        x2="${(cx + Math.cos(a) * (r - 1)).toFixed(1)}" y2="${(cy + Math.sin(a) * (r - 1)).toFixed(1)}"
                        stroke="#1E2433" stroke-width="${i % 3 === 0 ? '1.6' : '0.9'}"/>`;
      }

      svg.innerHTML = `
        <!-- Parchment tag behind pocket watch -->
        <rect x="4" y="14" width="182" height="94" rx="12" fill="#F8F3E8" fill-opacity="0.94" stroke="#1E2433" stroke-width="1.6"/>
        <!-- Pocket watch bow ring & crown -->
        <circle cx="${cx}" cy="13" r="7" fill="none" stroke="#1E2433" stroke-width="1.6"/>
        <rect x="${cx - 4}" y="18" width="8" height="6" rx="1.5" fill="url(#brass-rim-grad)" stroke="#1E2433" stroke-width="1.2"/>
        <!-- Watch dial -->
        <circle cx="${cx}" cy="${cy}" r="${r + 3}" fill="url(#brass-rim-grad)" stroke="#1E2433" stroke-width="1.6"/>
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="#FAF6EE" stroke="#1E2433" stroke-width="1.2"/>
        ${ticks}
        <!-- Sweeping hands -->
        <line x1="${cx}" y1="${cy}" x2="${(cx + Math.cos(srad) * 18).toFixed(1)}" y2="${(cy + Math.sin(srad) * 18).toFixed(1)}"
              stroke="#1E2433" stroke-width="2.0" stroke-linecap="round"/>
        <line x1="${cx}" y1="${cy}" x2="${(cx + Math.cos(rad) * 26).toFixed(1)}" y2="${(cy + Math.sin(rad) * 26).toFixed(1)}"
              stroke="#C0392B" stroke-width="1.4" stroke-linecap="round"/>
        <circle cx="${cx}" cy="${cy}" r="2.5" fill="#1E2433"/>
        <!-- Handwritten time scale labels -->
        <text x="134" y="56" font-family="Gabriola, 'Segoe Print', serif" font-size="22" font-weight="600"
              fill="#C0392B" text-anchor="middle">${sw.mainLabel}</text>
        <text x="134" y="76" font-family="'Sitka Text', Georgia, serif" font-size="9.5" font-style="italic"
              fill="#3A4150" text-anchor="middle">${sw.subLabel || 'biological time'}</text>
      `;
    },

    // ==========================================================================
    // 4. Real-Size Tags, pH Gauge (★3 & 2.7), and Calendar (★6) on SVG Stage
    // ==========================================================================
    showSizeTag({ text, targetX, targetY, tagX, tagY, color = '#1E2433', onDesk = false }) {
      this.frameProps.sizeTags.push({ text, targetX, targetY, tagX, tagY, color, onDesk });
    },

    showPhGauge({ x, y, ph = 7.2, scale = 1.0 }) {
      this.frameProps.phGauge = { x, y, ph, scale };
    },

    showCalendar({ x, y, years = 1, flipProgress = 0 }) {
      this.frameProps.calendar = { x, y, years, flipProgress };
    },

    _renderStageProps(t, engine) {
      this.stagePropsGroup.innerHTML = '';

      // Remove any temporary desk tags from previous frame
      const oldDeskTags = engine.dom.deskBreakout.querySelectorAll('.desk-size-tag');
      oldDeskTags.forEach((n) => n.remove());

      // A. Render Real-Size Museum Tags on a Thread (§2.2)
      for (let i = 0; i < this.frameProps.sizeTags.length; i++) {
        const tag = this.frameProps.sizeTags[i];
        const tx = tag.tagX !== undefined ? tag.tagX : tag.targetX + 26;
        const ty = tag.tagY !== undefined ? tag.tagY : tag.targetY - 24;
        const sway = Math.sin(t * 2.1 + i) * 1.4;
        const w = Math.max(46, tag.text.length * 4.5 + 14);
        const h = 16;

        // Curved thread from target (targetX, targetY) to eyelet at (tx, ty)
        const mx = (tag.targetX + tx) * 0.5;
        const my = Math.max(tag.targetY, ty) + 6;
        const grp = engine.createSvgEl('g', {
          class: tag.onDesk ? 'desk-size-tag' : 'stage-size-tag'
        });

        grp.innerHTML = `
          <!-- Ink thread & tie dot -->
          <circle cx="${tag.targetX.toFixed(1)}" cy="${tag.targetY.toFixed(1)}" r="1.6" fill="${tag.color}"/>
          <path d="M${tag.targetX.toFixed(1)},${tag.targetY.toFixed(1)} Q${mx.toFixed(1)},${my.toFixed(1)} ${tx.toFixed(1)},${ty.toFixed(1)}"
                fill="none" stroke="${tag.onDesk ? '#E8DCC8' : '#3A4150'}" stroke-width="0.65" stroke-dasharray="1.8 1.2"/>
          <!-- Museum paper tag with brass eyelet -->
          <g transform="translate(${tx.toFixed(1)} ${ty.toFixed(1)}) rotate(${sway.toFixed(2)})">
            <path d="M2,-2.5 L8,-8 L${w.toFixed(1)},-8 L${w.toFixed(1)},${(h - 8).toFixed(1)} L8,${(h - 8).toFixed(1)} L2,2.5 Z"
                  fill="#000000" opacity="0.22" transform="translate(1.4 2.0)"/>
            <path d="M0,-2.5 L6.5,-8 L${w.toFixed(1)},-8 L${w.toFixed(1)},${(h - 8).toFixed(1)} L6.5,${(h - 8).toFixed(1)} L0,2.5 Z"
                  fill="#FAF4E6" stroke="#1E2433" stroke-width="0.85" stroke-linejoin="round"/>
            <circle cx="4.2" cy="0" r="1.5" fill="none" stroke="#B4690E" stroke-width="0.8"/>
            <text x="${(w * 0.54).toFixed(1)}" y="3.2"
                  font-family="Gabriola, 'Segoe Print', serif" font-size="10.2" font-weight="600"
                  fill="${tag.color}" text-anchor="middle">${tag.text}</text>
          </g>
        `;

        if (tag.onDesk) {
          engine.dom.deskBreakout.appendChild(grp);
        } else {
          this.stagePropsGroup.appendChild(grp);
        }
      }

      // B. Render Semicircular Ink pH Gauge (★3 & Section 2.7: 7.2 -> 6.5 -> 5.5 -> 4.5)
      if (this.frameProps.phGauge) {
        const g = this.frameProps.phGauge;
        const sc = g.scale || 1.0;
        // Map pH 7.2..4.5 to angle -165 deg (left) .. -15 deg (right)
        const u = engine.Ease.clamp((7.2 - g.ph) / (7.2 - 4.5), 0, 1);
        const needleDeg = -165 + u * 150;
        const nRad = needleDeg * (Math.PI / 180);
        const nx = Math.cos(nRad) * 21;
        const ny = Math.sin(nRad) * 21;
        const phColor = g.ph > 6.8 ? '#B88428' : g.ph > 6.0 ? '#E8892D' : g.ph > 5.0 ? '#C23B2A' : '#7A3FB5';

        const phGrp = engine.createSvgEl('g', {
          transform: `translate(${g.x.toFixed(1)} ${g.y.toFixed(1)}) scale(${sc.toFixed(2)})`
        });
        phGrp.innerHTML = `
          <!-- Soft parchment backing dial -->
          <path d="M-28,4 A28,28 0 0 1 28,4 L24,14 L-24,14 Z"
                fill="#FAF5E8" stroke="#1E2433" stroke-width="0.95" opacity="0.95"/>
          <!-- Coloured pH Ribbon Arc (7.2 -> 6.5 -> 5.5 -> 4.5) -->
          <path d="M-22,0 A22,22 0 0 1 22,0"
                fill="none" stroke="url(#ph-ribbon-grad)" stroke-width="5.2" stroke-linecap="round"/>
          <!-- Scale tick labels -->
          <text x="-23" y="-5" font-family="'Segoe UI Variable Text', sans-serif" font-size="3.8" font-weight="700" fill="#8A6518" text-anchor="middle">7.2</text>
          <text x="-9" y="-23" font-family="'Segoe UI Variable Text', sans-serif" font-size="3.8" font-weight="700" fill="#E8892D" text-anchor="middle">6.5</text>
          <text x="9" y="-23" font-family="'Segoe UI Variable Text', sans-serif" font-size="3.8" font-weight="700" fill="#C23B2A" text-anchor="middle">5.5</text>
          <text x="23" y="-5" font-family="'Segoe UI Variable Text', sans-serif" font-size="3.8" font-weight="700" fill="#7A3FB5" text-anchor="middle">4.5</text>
          <!-- Pivoted Ink Needle -->
          <line x1="0" y1="0" x2="${nx.toFixed(1)}" y2="${ny.toFixed(1)}"
                stroke="#1E2433" stroke-width="1.35" stroke-linecap="round"/>
          <circle cx="0" cy="0" r="2.2" fill="${phColor}" stroke="#1E2433" stroke-width="0.7"/>
          <!-- Gabriola pH Readout -->
          <text x="0" y="11.5" font-family="Gabriola, 'Segoe Print', serif" font-size="11.5" font-weight="700"
                fill="${phColor}" text-anchor="middle">pH ${g.ph.toFixed(1)}</text>
        `;
        this.stagePropsGroup.appendChild(phGrp);
      }

      // C. Render Pencil Tear-off Calendar Pad in ★6 (1 yr … 5 yr … 10 yr … 20 yr)
      if (this.frameProps.calendar) {
        const cal = this.frameProps.calendar;
        const flip = cal.flipProgress || 0;
        const flipY = -flip * 16;
        const flipRot = -flip * 22;
        const flipOp = Math.max(0, 1 - flip * 1.25);

        const calGrp = engine.createSvgEl('g', {
          transform: `translate(${cal.x.toFixed(1)} ${cal.y.toFixed(1)})`
        });
        calGrp.innerHTML = `
          <!-- Cast shadow -->
          <rect x="-28" y="-24" width="60" height="54" rx="3" fill="#2B3040" opacity="0.18" transform="translate(2.5 3.5)"/>
          <!-- Pencil-drawn tear-off pad base -->
          <rect x="-28" y="-24" width="60" height="54" rx="3" fill="#FAF6EE" stroke="#2B3040" stroke-width="1.1"/>
          <!-- Perforated header bar & two binding rings -->
          <rect x="-28" y="-24" width="60" height="11" rx="2" fill="#D9D2C5" stroke="#2B3040" stroke-width="0.9"/>
          <line x1="-26" y1="-13" x2="30" y2="-13" stroke="#2B3040" stroke-width="0.7" stroke-dasharray="2 1.5"/>
          <circle cx="-14" cy="-18.5" r="2.0" fill="#FAF6EE" stroke="#2B3040" stroke-width="0.9"/>
          <circle cx="18" cy="-18.5" r="2.0" fill="#FAF6EE" stroke="#2B3040" stroke-width="0.9"/>
          <!-- Current Year Page -->
          <text x="2" y="10" font-family="Gabriola, 'Segoe Print', serif" font-size="22" font-weight="700"
                fill="#2B3040" text-anchor="middle">${cal.years} yr</text>
          <text x="2" y="23" font-family="'Sitka Text', Georgia, serif" font-size="6.2" font-style="italic"
                fill="#5E5748" text-anchor="middle">chronic fibrosis</text>
          <!-- Tearing/flipping sheet animation -->
          <g transform="translate(0 ${flipY.toFixed(1)}) rotate(${flipRot.toFixed(1)} -26 -13)" opacity="${flipOp.toFixed(2)}">
            <path d="M-27,-12 L31,-12 L28,26 Q2,22 -27,28 Z" fill="#FDFBF7" stroke="#2B3040" stroke-width="0.75"/>
          </g>
        `;
        this.stagePropsGroup.appendChild(calGrp);
      }

      // Reset frameProps for next deterministic render(t)
      this.frameProps.stopwatch = null;
      this.frameProps.phGauge = null;
      this.frameProps.calendar = null;
      this.frameProps.sizeTags = [];
    },

    // ==========================================================================
    // 5. Procedural WebAudio Sound Synthesizer (§8, Off by Default, Key M)
    // ==========================================================================
    toggleSound() {
      this.sound.enabled = !this.sound.enabled;
      const btn = document.getElementById('btn-sound');
      if (btn) {
        btn.textContent = `Sound: ${this.sound.enabled ? 'On' : 'Off'} [M]`;
        btn.classList.toggle('active', this.sound.enabled);
      }

      if (this.sound.enabled) {
        this._initAudioContext();
        this.playGlassyClick(2200);
      } else if (this.sound.ctx) {
        this.sound.ctx.suspend().catch(() => {});
      }
    },

    _initAudioContext() {
      if (!this.sound.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        this.sound.ctx = ctx;

        // 1. Soft filtered noise for the Breath cycle
        const bufferSize = ctx.sampleRate * 2;
        const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        let b0 = 0, b1 = 0, b2 = 0;
        for (let i = 0; i < bufferSize; i++) {
          const white = Math.random() * 2 - 1;
          b0 = 0.997 * b0 + white * 0.029;
          b1 = 0.985 * b1 + white * 0.032;
          b2 = 0.950 * b2 + white * 0.048;
          output[i] = (b0 + b1 + b2) * 0.35;
        }
        const whiteNoise = ctx.createBufferSource();
        whiteNoise.buffer = noiseBuffer;
        whiteNoise.loop = true;

        const filter = ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.value = 380;
        filter.Q.value = 1.8;

        const breathGain = ctx.createGain();
        breathGain.gain.value = 0.0;

        whiteNoise.connect(filter);
        filter.connect(breathGain);
        breathGain.connect(ctx.destination);
        whiteNoise.start(0);
        this.sound.breathGain = breathGain;
        this.sound.breathFilter = filter;

        // 2. Low resonant hum for the phagolysosome furnace (Section 2.7)
        const osc = ctx.createOscillator();
        osc.type = 'triangle';
        osc.frequency.value = 62;
        const humFilter = ctx.createBiquadFilter();
        humFilter.type = 'lowpass';
        humFilter.frequency.value = 140;
        const furnaceGain = ctx.createGain();
        furnaceGain.gain.value = 0.0;
        osc.connect(humFilter);
        humFilter.connect(furnaceGain);
        furnaceGain.connect(ctx.destination);
        osc.start(0);
        this.sound.furnaceGain = furnaceGain;
      }
      if (this.sound.ctx && this.sound.ctx.state === 'suspended') {
        this.sound.ctx.resume().catch(() => {});
      }
    },

    playGlassyClick(freq = 2200) {
      if (!this.sound.enabled || !this.sound.ctx) return;
      try {
        const ctx = this.sound.ctx;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, now);
        osc.frequency.exponentialRampToValueAtTime(freq * 1.45, now + 0.065);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.075);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.08);
      } catch (e) {}
    },

    playPenScratch() {
      if (!this.sound.enabled || !this.sound.ctx) return;
      const nowMs = performance.now();
      if (nowMs - this.sound.lastScratchAt < 90) return;
      this.sound.lastScratchAt = nowMs;
      try {
        const ctx = this.sound.ctx;
        const now = ctx.currentTime;
        const dur = 0.055;
        const buf = ctx.createBuffer(1, Math.floor(ctx.sampleRate * dur), ctx.sampleRate);
        const data = buf.getChannelData(0);
        for (let i = 0; i < data.length; i++) {
          data[i] = (Math.random() * 2 - 1) * Math.sin((Math.PI * i) / data.length);
        }
        const src = ctx.createBufferSource();
        src.buffer = buf;
        const bp = ctx.createBiquadFilter();
        bp.type = 'bandpass';
        bp.frequency.value = 1650 + Math.random() * 500;
        bp.Q.value = 3.2;
        const gain = ctx.createGain();
        gain.gain.value = 0.035;
        src.connect(bp);
        bp.connect(gain);
        gain.connect(ctx.destination);
        src.start(now);
      } catch (e) {}
    },

    _updateSoundBed(engine) {
      if (!this.sound.enabled || !this.sound.ctx) return;
      const now = this.sound.ctx.currentTime;
      if (this.sound.breathGain) {
        const bLevel = 0.012 + 0.032 * engine.breath.inhale;
        this.sound.breathGain.gain.setTargetAtTime(bLevel, now, 0.08);
        this.sound.breathFilter.frequency.setTargetAtTime(320 + engine.breath.inhale * 180 + engine.breath.shallow * 160, now, 0.08);
      }
      if (this.sound.furnaceGain) {
        // Low furnace hum is audible when zoomed into Zone E / Phagolysosome (2.7 Killing or 4 Fusion)
        const [vx, vy, vw] = engine.camera.currentBox;
        const cx = vx + vw * 0.5;
        const distToPl = Math.hypot(cx - 622, (vy + vw * 0.4) - 665);
        const furnaceLevel = (engine.camera.mag > 1.8 && distToPl < 220) ? 0.045 : 0.004;
        this.sound.furnaceGain.gain.setTargetAtTime(furnaceLevel, now, 0.15);
      }
    },

    // ==========================================================================
    // 6. Main Render Hook called at the end of Engine.render(t)
    // ==========================================================================
    render(t, engine) {
      this._renderLoupe(t, engine);
      this._renderTurret();
      this._renderStopwatch(t);
      this._renderStageProps(t, engine);
      this._updateSoundBed(engine);
    }
  };

  window.LivingDevices = Devices;
})();
