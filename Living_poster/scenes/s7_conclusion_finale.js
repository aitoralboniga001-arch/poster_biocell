/**
 * s7_conclusion_finale.js — Section 6 · Conclusion (Aitor · ~45 s) & ★ Finale (20 s)
 * Beats 6a–6d + fin_a–fin_c:
 * - 6a (11 s): Full poster at shallow breath; everything dims slightly.
 * - 6b (12 s): The red route and the blue route light up one after the other and meet in a violet bloom at the V.
 * - 6c (11 s): The pathology branch glows amber from right air down into the scarred wall.
 * - 6d (11 s): Conclusion line inks in; the word *destroys* gets its last brush sweep.
 * - fin_a (8 s): Reverse of the opening dive: poster → locator → bronchiole → construction worker,
 *   who coughs once gently; breath returns to normal only for the healthy left half of the lungs.
 * - fin_b (8 s): Back to full poster; five ink signatures write themselves along the bottom margin
 *   in speaking order (Aitor · Nerea · Urtzi · Eneritz · Nora), each in the colour of its section.
 * - fin_c (4 s): Settle into gallery mode with the loupe waiting on the paper.
 */
(function () {
  'use strict';

  const SceneConclusion = {
    id: 's7_conclusion',
    order: 7,
    sectionNum: '6',
    title: '6 · Conclusion',
    speaker: 'Aitor',
    color: '#1E2433',

    beats: [
      {
        id: '6a',
        label: 'Full poster overview at shallow fibrotic breath · slight dim',
        duration: 11,
        speakerChipText: '6 · Conclusion — Aitor',
        camFrom: [260, 620, 860, 300],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: '6b',
        label: 'Red route + Blue route converge in a violet bloom at the V',
        duration: 12,
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: '6c',
        label: 'Pathology branch glows amber from right air into scarred wall',
        duration: 11,
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: '6d',
        label: 'Conclusion line inks in · "destroys" gets its crimson brush sweep',
        duration: 11,
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      }
    ],

    init(engine) {
      this.engine = engine;
      this.concGrp = engine.createSvgEl('g', { id: 'scene7-conclusion-overlays' });
      engine.dom.layerCell.appendChild(this.concGrp);
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      if (!this.concGrp) this.init(engine);
      this.concGrp.innerHTML = '';

      // Maintain scarred right wall & shallow breath through Section 6
      engine.stateCrossFade('particles.fibrosis', 4.0);
      engine.stateCrossFade('alveolar.lumen', 0.85);
      engine.breath.shallow = 0.85;

      if (beat.id === '6a') {
        // Full poster at shallow breath; everything dims slightly
        const dimU = E.smooth(E.sub(localSec, 1.0, 5.0));
        engine.dom.bulletDimmer.setAttribute('opacity', (dimU * 0.22).toFixed(3));
        engine.lightLabels(['1 Alveolar macrophage', 'conclusion'], E.smooth(E.sub(localSec, 0.5, 3.0)));
      } else if (beat.id === '6b') {
        // Red route and blue route light up one after the other and meet in a violet bloom at the V
        engine.dom.bulletDimmer.setAttribute('opacity', '0.18');
        const redU = E.smoother(E.sub(localSec, 0.4, 4.5));
        const blueU = E.smoother(E.sub(localSec, 3.2, 7.5));
        const bloomU = E.smoother(E.sub(localSec, 6.5, 10.5));

        engine.dashDraw('red_route', redU, 0.95);
        engine.dashDraw('blue_route', blueU, 0.95);
        engine.pulseSignal('red_route', (globalT * 0.35) % 1, '#E0452B', 4.0);
        engine.pulseSignal('blue_route', (globalT * 0.38) % 1, '#1F58C8', 4.0);

        engine.watercolourBloom({ cx: 470, cy: 680, r: 54, color: '#7A3FB5', opacity: bloomU * 0.65 });
        engine.watercolourBloom({ cx: 622, cy: 665, r: 72, color: '#6C2EB9', opacity: bloomU * 0.72 });

        engine.lightLabels(['2 Recognition', '3 Lysosome biogenesis', '4 Fusion', '2.6 Phagolysosome'], E.smooth(E.sub(localSec, 0.5, 3.0)));
      } else if (beat.id === '6c') {
        // Pathology branch glows amber from right air down into the scarred wall
        engine.dom.bulletDimmer.setAttribute('opacity', '0.18');
        engine.dashDraw('red_route', 1.0, 0.65);
        engine.dashDraw('blue_route', 1.0, 0.65);

        const ambU = E.smoother(E.sub(localSec, 0.4, 7.5));
        engine.dashDraw('signal2_cathepsin', ambU, 0.95);
        engine.dashDraw('caspase_il1b', ambU, 0.95);
        engine.dashDraw('wall_il1b_tnfa', ambU, 0.95);
        engine.dashDraw('wall_tgfb_pdgf', ambU, 0.95);

        engine.watercolourBloom({ cx: 850, cy: 560, r: 58, color: '#D4621A', opacity: ambU * 0.52 });
        engine.watercolourBloom({ cx: 950, cy: 760, r: 95, color: '#B4690E', opacity: ambU * 0.58 });

        engine.lightLabels(['5 Particles', '5.2 Silica phagolysosome', '5.3 Asbestos', '5.5 Fibrosis'], E.smooth(E.sub(localSec, 0.5, 3.0)));
      } else if (beat.id === '6d') {
        // Conclusion line inks in; the word *destroys* gets its last brush sweep
        const inkU = E.smoother(E.sub(localSec, 0.4, 4.0));
        const brushU = E.smoother(E.sub(localSec, 4.2, 8.5));
        const brushLen = 110;
        const brushOff = (brushLen * (1 - brushU)).toFixed(1);

        const g = engine.createSvgEl('g', { opacity: inkU.toFixed(2) });
        g.innerHTML = `
          <rect x="135" y="842" width="830" height="36" rx="8" fill="#FAF6EE" fill-opacity="0.96"
                stroke="#1E2433" stroke-width="1.5"/>
          <text x="550" y="864" text-anchor="middle" font-family="'Sitka Text', Georgia, serif"
                font-size="13.5" font-weight="700" fill="#1E2433">
            The same lysosomal machinery that <tspan fill="#1F58C8">defends</tspan> the lung against microbes
            <tspan fill="#C0392B" font-style="italic">destroys</tspan> it when faced with biopersistent mineral particles.
          </text>
          <!-- Crimson brush sweep under "destroys" -->
          <path d="M585,871 C612,876 645,875 676,870" fill="none" stroke="#C0392B" stroke-width="3.6"
                stroke-linecap="round" stroke-dasharray="${brushLen}" stroke-dashoffset="${brushOff}"/>
        `;
        this.concGrp.appendChild(g);
        engine.lightLabels(['conclusion', 'title'], inkU);
      }
    }
  };

  const SceneFinale = {
    id: 's7_finale',
    order: 8,
    sectionNum: 'finale',
    title: '★ Finale · Human Scale & Signatures',
    speaker: 'Aitor · Nerea · Urtzi · Eneritz · Nora',
    color: '#7A3FB5',

    beats: [
      {
        id: 'fin_a',
        label: 'Reverse Powers of Ten: poster → locator → worker gentle cough (healthy left vs fibrotic right lung)',
        duration: 8,
        speakerChipText: '★ Finale — Aitor · Nerea · Urtzi · Eneritz · Nora',
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: 'fin_b',
        label: 'Five ink signatures write themselves in speaking order (Aitor · Nerea · Urtzi · Eneritz · Nora)',
        duration: 8,
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: 'fin_c',
        label: 'Settle into Gallery mode with the Loupe waiting on the paper',
        duration: 4,
        camFrom: [-38, -22, 1176, 944],
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

      if (beat.id === 'fin_a') {
        // 0–8 s: Reverse of the opening dive: poster -> locator -> bronchiole -> construction worker,
        // who coughs once gently; breath returns to normal ONLY for the healthy left half of the lungs!
        const revU = E.smoother(E.sub(localSec, 0.3, 2.5)) * (1 - E.smoother(E.sub(localSec, 6.5, 7.9)));
        const coughActive = localSec >= 3.2 && localSec <= 5.4;
        const coughShake = coughActive ? Math.sin((localSec - 3.2) * 24) * 2.2 : 0;

        // Healthy left lung (viewer's left) breathes deeply at 5s period; scarred right lung stays stiff
        const healthyScale = 1 + 0.085 * Math.sin(((globalT % 5.0) / 5.0) * Math.PI * 2);
        const scarredScale = 1 + 0.015 * Math.sin(((globalT % 2.1) / 2.1) * Math.PI * 2);
        engine.breath.shallow = 0.25;

        const card = engine.createSvgEl('g', { opacity: revU.toFixed(3) });
        card.innerHTML = `
          <!-- Warm parchment Powers-of-Ten reverse overlay -->
          <rect x="330" y="180" width="440" height="360" rx="14" fill="#FAF6EE" fill-opacity="0.96"
                stroke="#1E2433" stroke-width="2.0"/>
          <g transform="translate(0 ${coughShake.toFixed(1)})">
            <!-- Construction worker head & hard hat -->
            <circle cx="550" cy="260" r="24" fill="none" stroke="#1E2433" stroke-width="2.2"/>
            <path d="M520,255 C520,230 580,230 580,255 Z" fill="#E2B33C" stroke="#1E2433" stroke-width="1.8"/>
            <!-- Torso -->
            <path d="M475,440 C480,340 510,300 550,300 C590,300 620,340 625,440"
                  fill="#F3EDE0" stroke="#1E2433" stroke-width="2.2"/>
            <!-- Healthy Left Half of Lungs (deep normal breath) -->
            <g transform="translate(522 365) scale(${healthyScale.toFixed(3)}) translate(-522 -365)">
              <path d="M542,322 C505,322 492,358 498,405 C502,422 532,420 544,398 Z"
                    fill="#D4ECF7" stroke="#1F58C8" stroke-width="2.0"/>
            </g>
            <!-- Scarred Fibrotic Right Half of Lungs (stiff shallow breath) -->
            <g transform="translate(578 365) scale(${scarredScale.toFixed(3)}) translate(-578 -365)">
              <path d="M558,322 C592,326 604,358 598,396 C594,412 568,410 556,392 Z"
                    fill="#EED6BE" stroke="#B4690E" stroke-width="2.2" stroke-dasharray="4 2.5"/>
            </g>
            <!-- Gentle cough puff -->
            <g opacity="${coughActive ? '0.92' : '0'}">
              <circle cx="592" cy="268" r="7" fill="none" stroke="#5E5748" stroke-width="1.3" stroke-dasharray="2.5 2"/>
              <circle cx="610" cy="262" r="11" fill="none" stroke="#5E5748" stroke-width="1.1" stroke-dasharray="2.5 2"/>
              <text x="632" y="266" font-family="Gabriola, 'Segoe Print', serif" font-size="16" font-style="italic" fill="#3A4150">*gentle cough*</text>
            </g>
          </g>
          <text x="550" y="485" text-anchor="middle" font-family="Gabriola, 'Segoe Print', serif" font-size="22" font-weight="600" fill="#1E2433">
            human scale · healthy lobe vs. scarred fibrotic lobe
          </text>
          <text x="550" y="512" text-anchor="middle" font-family="'Sitka Text', Georgia, serif" font-size="11" fill="#5E5748">
            1.7 m → 1 mm bronchiole → 200 µm alveolus → 21 µm macrophage
          </text>
        `;
        g.appendChild(card);
      } else if (beat.id === 'fin_b' || beat.id === 'fin_c') {
        // 8–16 s (and holding through 16–20 s): Back to full poster; five ink signatures write themselves
        // along the bottom margin in speaking order (Aitor · Nerea · Urtzi · Eneritz · Nora), each in the colour of its section!
        engine.breath.shallow = 0;

        const sigDefs = [
          { name: 'Aitor',   role: '1 · Macrophage & 6 · Conclusion', col: '#1E2433', x: 190 },
          { name: 'Nerea',   role: '2 · Phagocytosis & 2.7 · Killing', col: '#C0392B', x: 370 },
          { name: 'Urtzi',   role: '3 · Lysosome Biogenesis (M6P)',    col: '#1F58C8', x: 550 },
          { name: 'Eneritz', role: '4 · SNARE & HOPS Fusion',          col: '#7A3FB5', x: 730 },
          { name: 'Nora',    role: '5 · Silica, Asbestos & Fibrosis',  col: '#B4690E', x: 910 }
        ];

        const sigContainer = engine.createSvgEl('g', { id: 'finale-signatures' });
        sigDefs.forEach((sd, idx) => {
          const writeU = beat.id === 'fin_c'
            ? 1.0
            : E.smoother(E.sub(localSec, 0.3 + idx * 1.35, 1.6 + idx * 1.35));

          if (writeU > 0.01) {
            const flourishLen = 90;
            const dashOff = (flourishLen * (1 - writeU)).toFixed(1);
            const item = engine.createSvgEl('g', { opacity: writeU.toFixed(2) });
            item.innerHTML = `
              <rect x="${sd.x - 74}" y="858" width="148" height="34" rx="7" fill="#FAF6EE" fill-opacity="0.96"
                    stroke="${sd.col}" stroke-width="1.4"/>
              <text x="${sd.x}" y="876" text-anchor="middle" font-family="Gabriola, 'Segoe Print', serif"
                    font-size="18.5" font-weight="700" fill="${sd.col}">${sd.name}</text>
              <text x="${sd.x}" y="887" text-anchor="middle" font-family="'Segoe UI Variable Text', sans-serif"
                    font-size="6.0" font-weight="700" fill="#4A5566">${sd.role}</text>
              <path d="M${sd.x - 38},879 C${sd.x - 12},874 ${sd.x + 14},874 ${sd.x + 38},879"
                    fill="none" stroke="${sd.col}" stroke-width="1.3" stroke-linecap="round"
                    stroke-dasharray="${flourishLen}" stroke-dashoffset="${dashOff}"/>
            `;
            sigContainer.appendChild(item);
          }
        });
        g.appendChild(sigContainer);

        // In fin_c (16–20 s), bring out the Loupe waiting on the paper
        if (beat.id === 'fin_c' && window.LivingDevices) {
          window.LivingDevices.loupe.enabled = true;
          window.LivingDevices.loupe.scripted = false;
        }
      }
    }
  };

  window.LivingEngine.registerScene(SceneConclusion);
  window.LivingEngine.registerScene(SceneFinale);
})();
