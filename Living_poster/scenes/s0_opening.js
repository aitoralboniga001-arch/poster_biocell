/**
 * s0_opening.js — ★1 Opening: Powers of Ten (Aitor, 25 s)
 * Blank warm paper -> Title ink-in (destroys painted last in red swash) ->
 * Pen sketch of construction worker in dusty street ("you · 1.7 m") ->
 * Dive into chest & watercolour lungs -> 3 bronchial branch zoom levels ->
 * Locator sketch ("alveolus ≈ 200 µm") -> Pass through "this scene" circle into full poster.
 */
(function () {
  'use strict';

  const Scene0 = {
    id: 's0_opening',
    order: 0,
    sectionNum: '0',
    title: 'Opening · Powers of Ten',
    speaker: 'Aitor',
    color: '#1E2433',

    beats: [
      {
        id: '0a',
        label: 'Powers of Ten · Title & Dusty Street (0–12 s)',
        duration: 12,
        speakerChipText: '★1 · Opening: Powers of Ten — Aitor',
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: '0b',
        label: 'Bronchial Tree Dive → Locator → Alveolus (12–25 s)',
        duration: 13,
        camFrom: [0, 0, 1100, 900],
        camTo: [-38, -22, 1176, 944]
      }
    ],

    init(engine) {
      this.engine = engine;
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      const g = engine.dom.layerOpeningFinale;
      g.innerHTML = '';

      // Compute continuous opening time tOpen in [0, 25]
      const tOpen = beat.id === '0a' ? localSec : (12 + localSec);

      // ----------------------------------------------------------------------
      // Phase 1 (0–22 s): Warm paper cover over the poster that opens through
      // the locator's "this scene" circle at t = 18..22 s!
      // ----------------------------------------------------------------------
      const diveThroughU = E.sub(tOpen, 18.0, 22.0);
      const paperOp = 1 - E.smoother(E.sub(tOpen, 20.2, 22.4));

      if (paperOp > 0.01) {
        const openGrp = engine.createSvgEl('g', {
          id: 'opening-sequence-layer',
          opacity: paperOp.toFixed(3)
        });

        // Warm blank paper sheet
        openGrp.appendChild(engine.createSvgEl('rect', {
          x: '-120', y: '-100', width: '1340', height: '1100',
          fill: '#F7F3EA'
        }));

        // ====================================================================
        // Beat 0..7 s: Title inks in letter by letter, then floats to TITLE_BOX
        // ====================================================================
        const titleInkU = E.sub(tOpen, 0.2, 2.8);
        const destroysU = E.sub(tOpen, 1.8, 3.0);
        const floatUpU = E.smoother(E.sub(tOpen, 3.0, 6.8));

        // Interpolate title transform from centre stage (550, 430, scale 1.45) to poster TITLE_BOX (30, 18, scale 1.0)
        const tx = E.lerp(185, 0, floatUpU);
        const ty = E.lerp(350, 0, floatUpU);
        const tScale = E.lerp(1.38, 1.0, floatUpU);

        const howText = 'How a macrophage';
        const whatText = 'what it engulfs';
        const howChars = Math.floor(E.sub(titleInkU, 0, 0.55) * howText.length);
        const whatChars = Math.floor(E.sub(titleInkU, 0.45, 0.9) * whatText.length);

        if (titleInkU > 0.05 && titleInkU < 0.98 && window.LivingDevices) {
          window.LivingDevices.playPenScratch();
        }

        const titleGrp = engine.createSvgEl('g', {
          transform: `translate(${tx.toFixed(1)} ${ty.toFixed(1)}) scale(${tScale.toFixed(3)})`
        });

        // Line 1: "How a macrophage" in Sitka Banner
        const t1 = engine.createSvgEl('text', {
          x: '128', y: '53',
          'font-family': "'Sitka Banner', 'Sitka Display', Georgia, serif",
          'font-size': '43',
          fill: '#1E2433',
          'letter-spacing': '-0.6'
        });
        t1.textContent = howText.slice(0, howChars);
        titleGrp.appendChild(t1);

        // Line 2b: "what it engulfs"
        const t2 = engine.createSvgEl('text', {
          x: '298', y: '94',
          'font-family': "'Sitka Banner', 'Sitka Display', Georgia, serif",
          'font-size': '43',
          fill: '#1E2433',
          'letter-spacing': '-0.6'
        });
        t2.textContent = whatText.slice(0, whatChars);
        titleGrp.appendChild(t2);

        // Line 2a: "destroys" painted last in red Gabriola swash + watercolour wash
        if (destroysU > 0.01) {
          const swashScale = E.membraneSpring(destroysU);
          const dGrp = engine.createSvgEl('g', {
            opacity: E.smooth(destroysU).toFixed(2),
            transform: `translate(190 82) scale(${swashScale.toFixed(3)}) translate(-190 -82)`
          });
          dGrp.appendChild(engine.createSvgEl('ellipse', {
            cx: '196', cy: '81', rx: String(98 * destroysU), ry: '16',
            fill: '#F2B4A6', opacity: '0.58', transform: 'rotate(-3 196 81)'
          }));
          const dTxt = engine.createSvgEl('text', {
            x: '94', y: '94',
            'font-family': "Gabriola, 'Segoe Print', serif",
            'font-size': '77',
            fill: '#C0392B',
            stroke: '#C0392B',
            'stroke-width': '0.5',
            style: "font-feature-settings:'ss07';"
          });
          dTxt.textContent = 'destroys';
          dGrp.appendChild(dTxt);
          titleGrp.appendChild(dGrp);
        }
        openGrp.appendChild(titleGrp);

        // ====================================================================
        // Beat 3..12 s: Pen sketch of person (construction worker) in dusty street
        // Diving into chest & watercolour lungs (7..12 s)
        // ====================================================================
        const personInU = E.smooth(E.sub(tOpen, 3.0, 6.2));
        const chestDiveU = E.smoother(E.sub(tOpen, 7.0, 12.2));
        const personFadeOut = 1 - E.smooth(E.sub(tOpen, 12.0, 14.5));

        if (personInU > 0.01 && personFadeOut > 0.01) {
          const pScale = E.lerp(1.0, 3.4, chestDiveU);
          const pCx = 550;
          const pCy = 440;
          const chestRise = Math.sin(E.sub(tOpen, 4.5, 11.5) * Math.PI) * 5.5;

          const personGrp = engine.createSvgEl('g', {
            opacity: (personInU * personFadeOut).toFixed(3),
            transform: `translate(${pCx} ${pCy}) scale(${pScale.toFixed(3)}) translate(${-pCx} ${-(pCy - chestDiveU * 45)})`
          });

          // Building site scaffolding & dusty street horizon in pencil grey (#2B3040)
          personGrp.innerHTML = `
            <!-- Dusty construction site haze -->
            <ellipse cx="550" cy="460" rx="340" ry="180" fill="#E9E0CE" opacity="0.65"/>
            <!-- Scaffolding & crane sketch on left/right -->
            <g stroke="#5A5E6B" stroke-width="1.1" fill="none" opacity="${(0.55 * (1 - chestDiveU * 0.7)).toFixed(2)}">
              <path d="M240,590 L240,280 L360,280 L360,590 M240,360 L360,360 M240,450 L360,450 M240,280 L360,360 M360,280 L240,360"/>
              <path d="M740,590 L740,310 L870,310 L870,590 M740,390 L870,390 M740,480 L870,480"/>
              <path d="M180,590 Q550,582 920,592" stroke-width="1.8"/>
            </g>

            <!-- Watercolour Lungs appearing behind ribs during 7..12 s -->
            <g opacity="${E.smooth(E.sub(tOpen, 6.6, 9.8)).toFixed(2)}" transform="translate(0 ${(-chestRise * 0.6).toFixed(1)})">
              <!-- Left & Right Lung Watercolour Washes -->
              <path d="M538,375 C512,372 486,398 480,445 C476,482 482,508 505,508 C528,508 538,488 540,440 Z"
                    fill="#E9A9A0" stroke="#2B3040" stroke-width="1.3" opacity="0.88"/>
              <path d="M562,375 C588,372 614,398 620,445 C624,482 618,508 595,508 C572,508 562,488 560,440 Z"
                    fill="#E9A9A0" stroke="#2B3040" stroke-width="1.3" opacity="0.88"/>
              <!-- Trachea & Primary Bronchi -->
              <path d="M546,315 L546,382 M554,315 L554,382 M546,382 L515,418 M554,382 L585,418"
                    stroke="#2B3040" stroke-width="1.6" fill="none" stroke-linecap="round"/>
              <!-- Subtle rib cage arcs -->
              <g stroke="#2B3040" stroke-width="0.9" fill="none" opacity="0.38">
                <path d="M492,395 Q520,405 540,396 M608,395 Q580,405 560,396"/>
                <path d="M484,422 Q518,432 540,422 M616,422 Q582,432 560,422"/>
                <path d="M482,450 Q518,460 540,448 M618,450 Q582,460 560,448"/>
                <path d="M486,478 Q518,486 538,475 M614,478 Q582,486 562,475"/>
              </g>
            </g>

            <!-- Pen Sketch of Person (Hardhat + Torso + Breathing Chest) -->
            <g stroke="#1E2433" fill="none" stroke-linecap="round" stroke-linejoin="round">
              <!-- Hardhat -->
              <path d="M512,248 C512,216 588,216 588,248 L602,252 L498,252 Z" fill="#F2D894" fill-opacity="0.45" stroke-width="2.1"/>
              <!-- Head & Profile -->
              <path d="M522,252 C520,282 530,305 550,308 C570,305 580,282 578,252" stroke-width="1.9"/>
              <!-- Neck & Shoulders (rising with breath) -->
              <g transform="translate(0 ${(-chestRise).toFixed(1)})">
                <path d="M536,306 L534,332 L462,358 L446,575 M564,306 L566,332 L638,358 L654,575" stroke-width="2.2"/>
                <path d="M482,352 L486,575 M618,352 L614,575" stroke-width="1.6"/>
                <!-- Safety vest stripes -->
                <path d="M505,345 L512,520 M595,345 L588,520 M486,465 L614,465" stroke="#B4690E" stroke-width="1.4" opacity="0.65"/>
              </g>
            </g>
          `;

          // Air dots, silica sparkles & long asbestos fibres drifting into nose/mouth -> trachea (4..12 s)
          for (let k = 0; k < 18; k++) {
            const uAir = ((tOpen * 0.42 + k * 0.09) % 1.0);
            const ax = E.lerp(380 + (k % 5) * 75, 550 + Math.sin(k) * 4, E.smooth(uAir));
            const ay = E.lerp(240 + (k % 4) * 32, 395 + uAir * 55, E.smooth(uAir));
            const col = k % 3 === 0 ? '#70D6FF' : k % 3 === 1 ? '#D6B676' : '#8C9A3A';
            personGrp.appendChild(engine.createSvgEl('circle', {
              cx: ax.toFixed(1), cy: ay.toFixed(1),
              r: k % 3 === 0 ? '2.4' : '1.8',
              fill: col, opacity: (Math.sin(uAir * Math.PI) * 0.85).toFixed(2)
            }));
          }

          openGrp.appendChild(personGrp);
        }

        // Size tag: "you · 1.7 m" during 3.2..9.5 s
        if (tOpen >= 3.2 && tOpen <= 9.5 && window.LivingDevices) {
          window.LivingDevices.showSizeTag({
            text: 'you · 1.7 m',
            targetX: 625,
            targetY: 365,
            tagX: 675,
            tagY: 335,
            color: '#1E2433'
          });
        }

        // ====================================================================
        // Beat 12..18 s: Continuous Dive Down 3 Bronchial Branch Levels
        // Nesting into the Poster's Locator Sketch (lung -> bronchiole -> sac)
        // ====================================================================
        const branchPhase = E.sub(tOpen, 11.5, 18.2);
        if (branchPhase > 0.01) {
          // Force turret objective 4x -> 10x at t=14.5s (§4 Opening Table)
          if (tOpen > 14.5 && window.LivingDevices) {
            engine.camera.objective = '10×';
          }

          const bFadeOut = 1 - E.smooth(E.sub(tOpen, 18.2, 20.8));
          // Drift center from (550, 450) to Locator (135, 185) as we land in the poster's locator sketch
          const toLocU = E.smoother(E.sub(tOpen, 15.2, 19.0));
          const bx = E.lerp(550, 145, toLocU);
          const by = E.lerp(450, 185, toLocU);
          const bScale = E.lerp(1.35, 0.42, toLocU);

          const treeGrp = engine.createSvgEl('g', {
            opacity: (E.smooth(branchPhase * 3) * bFadeOut).toFixed(3),
            transform: `translate(${bx.toFixed(1)} ${by.toFixed(1)}) scale(${bScale.toFixed(3)}) translate(-550 -450)`
          });

          // Level 1 (12..14s): Primary & Lobar Bronchi
          // Level 2 (14..16s): Segmental Bronchioles
          // Level 3 (16..18s): Terminal Bronchiole & Alveolar Sac (grape cluster)
          const l1Op = E.sub(tOpen, 11.5, 13.2);
          const l2Op = E.sub(tOpen, 13.2, 15.2);
          const l3Op = E.sub(tOpen, 15.0, 17.5);
          const flex = Math.sin(tOpen * 2.4) * 3.5;

          treeGrp.innerHTML = `
            <!-- Level 1: Primary & Lobar Bronchial Tree with Cartilage Rings -->
            <g opacity="${l1Op.toFixed(2)}" stroke="#2B3040" fill="none" stroke-linecap="round">
              <path d="M535,180 L535,320 Q535,360 440,${(430 + flex).toFixed(1)} M565,180 L565,320 Q565,360 660,${(430 + flex).toFixed(1)}" stroke-width="3.2"/>
              <path d="M550,345 L465,${(450 + flex).toFixed(1)} M550,345 L635,${(450 + flex).toFixed(1)}" stroke-width="2.6"/>
              <path d="M537,210 Q550,216 563,210 M537,240 Q550,246 563,240 M537,270 Q550,276 563,270 M537,300 Q550,306 563,300" stroke-width="1.4" opacity="0.65"/>
            </g>

            <!-- Level 2: Dichotomous Bronchioles -->
            <g opacity="${l2Op.toFixed(2)}" stroke="#2B3040" fill="none" stroke-linecap="round">
              <path d="M440,${(430 + flex).toFixed(1)} L370,510 M452,${(442 + flex).toFixed(1)} L495,525" stroke-width="2.2"/>
              <path d="M648,${(435 + flex).toFixed(1)} L595,520 M660,${(430 + flex).toFixed(1)} L725,515" stroke-width="2.2"/>
              <text x="355" y="485" font-family="Gabriola, 'Segoe Print', serif" font-size="26" fill="#4B4F5C" stroke="none">bronchiole</text>
            </g>

            <!-- Level 3: Terminal Bronchiole & Alveolar Sac Cluster -->
            <g opacity="${l3Op.toFixed(2)}">
              <ellipse cx="620" cy="575" rx="95" ry="72" fill="#E9A9A0" opacity="0.45"/>
              <circle cx="585" cy="555" r="26" fill="#D7E6EE" stroke="#2B3040" stroke-width="1.8"/>
              <circle cx="630" cy="542" r="28" fill="#D7E6EE" stroke="#2B3040" stroke-width="1.8"/>
              <circle cx="668" cy="568" r="25" fill="#D7E6EE" stroke="#2B3040" stroke-width="1.8"/>
              <circle cx="645" cy="605" r="27" fill="#D7E6EE" stroke="#2B3040" stroke-width="1.8"/>
              <circle cx="595" cy="598" r="24" fill="#D7E6EE" stroke="#2B3040" stroke-width="1.8"/>
              <!-- Red zoom circle around the chosen alveolus -->
              <circle cx="668" cy="568" r="31" fill="none" stroke="#C0392B" stroke-width="2.4" stroke-dasharray="6 4"/>
              <text x="625" y="662" font-family="Gabriola, 'Segoe Print', serif" font-size="28" fill="#4B4F5C" text-anchor="middle">alveolar sac · ≈ 200 µm</text>
            </g>
          `;
          openGrp.appendChild(treeGrp);
        }

        // ====================================================================
        // Beat 18..22 s: "this scene" circle in Locator glows & expands to
        // become the frame of the full poster!
        // ====================================================================
        if (tOpen >= 17.2) {
          const ringR = E.lerp(21.5, 980, E.smoother(diveThroughU));
          const ringCx = E.lerp(193, 550, E.smoother(diveThroughU));
          const ringCy = E.lerp(188, 450, E.smoother(diveThroughU));

          openGrp.appendChild(engine.createSvgEl('circle', {
            cx: ringCx.toFixed(1),
            cy: ringCy.toFixed(1),
            r: ringR.toFixed(1),
            fill: 'none',
            stroke: '#C0392B',
            'stroke-width': (2.4 + diveThroughU * 6).toFixed(1),
            opacity: (1 - diveThroughU * 0.6).toFixed(2)
          }));

          if (tOpen <= 21.5 && window.LivingDevices) {
            window.LivingDevices.showSizeTag({
              text: 'alveolus ≈ 200 µm',
              targetX: 193,
              targetY: 188,
              tagX: 235,
              tagY: 162,
              color: '#C0392B'
            });
          }
        }

        g.appendChild(openGrp);
      }

      // ======================================================================
      // Phase 2 (22–25 s): Full Living Poster Revealed, Routes Start to Flow,
      // Speaker Chip "1 · Alveolar macrophage — Aitor" stamps in!
      // ======================================================================
      if (tOpen >= 21.0) {
        const routeU = E.sub(tOpen, 21.5, 24.8);
        engine.dashDraw('red_route', routeU, 0.78);
        engine.dashDraw('blue_route', routeU, 0.78);
        engine.lightLabels(['1 Alveolar macrophage', 'this scene'], routeU);

        if (tOpen >= 22.0 && engine.dom.speakerChip) {
          const chip = engine.dom.speakerChip;
          chip.textContent = '1 · Alveolar macrophage — Aitor';
          chip.style.borderColor = '#1E2433';
          chip.style.color = '#1E2433';
          chip.classList.add('visible', 'stamp-ring');
        }
      }
    }
  };

  window.LivingEngine.registerScene(Scene0);
})();
