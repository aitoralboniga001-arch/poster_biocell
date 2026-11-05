/**
 * s6_particles.js — Section 5 · Indigestible particles: "glass and needles" (Nora · ★5 + ★6 · ~120 s)
 * Beats 5a–5h:
 * - 5a (13 s): Right air silica crystals sink with each breath, glinting; one is engulfed.
 * - 5b (14 s): Silica phagolysosome (850, 560) sharp corner presses membrane; membrane tears;
 *   cathepsin B leaks out; K⁺ efflux leaves cell; ROS twinkle.
 * - 5c (15 s): NLRP3 (EM): Signal 1 (TLR → NF-κB priming) + Signal 2 arrive; NLRP3 monomers
 *   swing in and lock into a wheel; ASC filaments polymerise.
 * - 5d (15 s): caspase-1 ignites; pro-IL-1β/IL-18 split into active dots; GSDMD cleaved and
 *   inserts into right membrane; pores open (tag "≈ 20 nm"); IL-1β · IL-18 stream out.
 * - 5e (13 s): Right air (ghosted/dashed with ?): dying macrophage swells/bursts (pyroptosis?);
 *   released crystal drifts along dashed curve (re-uptake) back to membrane.
 * - 5f (18 s): ★5 Asbestos: hood lip reaches along fibre, strains, and falls back three times
 *   (each attempt shorter and more tired); camera pulls out showing fibre running beyond the paper's
 *   edge onto the dark desk with cast shadow and desk size tag "> 15–20 µm"; ROS · enzymes seep onto epithelium.
 * - 5g (14 s): Wall: IL-1β · TNF-α travel dotted path into interstitium; neutrophils and monocytes
 *   squeeze out of capillaries (diapedesis); water-wash warms wall.
 * - 5h (18 s): ★6 Decades: pencil calendar flips 1 yr … 5 … 10 … 20 yr; TGF-β · PDGF reach
 *   myofibroblasts; collagen bundles hatch in and spread right → left along wall; alveoli narrow;
 *   poster's breath becomes shallow and quick; capillary RBCs slow.
 */
(function () {
  'use strict';

  const Scene6 = {
    id: 's6_particles',
    order: 6,
    sectionNum: '5',
    title: '5 · Particles ("glass and needles")',
    speaker: 'Nora',
    color: '#B4690E',

    beats: [
      {
        id: '5a',
        label: '5.1 · Crystalline silica inhaled in right air & engulfed',
        duration: 13,
        speakerChipText: '5 · Indigestible particles — Nora',
        camFrom: [740, 140, 380, 290],
        camTo: [780, 220, 340, 260]
      },
      {
        id: '5b',
        label: '5.2 · Silica phagolysosome rupture · cathepsin B leak · K⁺ efflux · ROS',
        duration: 14,
        camFrom: [780, 220, 340, 260],
        camTo: [765, 480, 280, 215]
      },
      {
        id: '5c',
        label: 'NLRP3 inflammasome wheel assembly (Signal 1 + Signal 2 → NLRP3 + ASC)',
        duration: 15,
        em: true,
        camFrom: [765, 480, 280, 215],
        camTo: [835, 545, 210, 162]
      },
      {
        id: '5d',
        label: 'caspase-1 activation · GSDMD pores (~20 nm) · IL-1β & IL-18 release',
        duration: 15,
        camFrom: [835, 545, 210, 162],
        camTo: [865, 575, 235, 180]
      },
      {
        id: '5e',
        label: 'Ghosted pyroptosis? amplification loop & crystal re-uptake',
        duration: 13,
        camFrom: [865, 575, 235, 180],
        camTo: [885, 495, 245, 190]
      },
      {
        id: '5f',
        label: '★5 · 5.3 Frustrated phagocytosis: asbestos fibre breaks out onto the desk',
        duration: 18,
        camFrom: [835, 650, 285, 220],
        camTo: [760, 580, 480, 340]
      },
      {
        id: '5g',
        label: '5.4 · Alveolar wall inflammation · IL-1β / TNF-α · leukocyte diapedesis',
        duration: 14,
        camFrom: [760, 580, 480, 340],
        camTo: [740, 680, 380, 240]
      },
      {
        id: '5h',
        label: '★6 · 5.5 Chronic fibrosis (1 yr → 20 yr) · collagen spreads R → L · shallow breath',
        duration: 18,
        camFrom: [740, 680, 380, 240],
        camTo: [260, 620, 860, 300]
      }
    ],

    init(engine) {
      this.engine = engine;
      this.partGrp = engine.createSvgEl('g', { id: 'scene6-particles-overlays' });
      engine.dom.layerCell.appendChild(this.partGrp);
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      if (!this.partGrp) this.init(engine);
      this.partGrp.innerHTML = '';

      if (beat.id === '5a') {
        // Right air: angular silica crystals sink with each breath, glinting; one is engulfed at (1028, 288) -> (850, 560)
        const breathBob = engine.breath.wallFlexY * 3.5;
        const sinkY = (localSec * 3.2) % 32;
        const crystals = [
          { x: 1072, y: 220, pts: '-7,-4 2,-8 8,-1 4,7 -5,5' },
          { x: 1043, y: 240, pts: '-6,-6 5,-5 7,3 -1,7 -7,2' },
          { x: 1082, y: 352, pts: '-8,-3 1,-9 9,-2 5,8 -6,6' }
        ];

        const g = engine.createSvgEl('g');
        let html = '';
        crystals.forEach((cr, idx) => {
          const cx = cr.x + Math.sin(globalT * 1.5 + idx) * 2.5;
          const cy = cr.y + breathBob + sinkY;
          const rot = Math.sin(globalT * 2 + idx) * 14;
          html += `
            <g transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)}) rotate(${rot.toFixed(1)})">
              <polygon points="${cr.pts}" fill="#E2E8F0" stroke="#475569" stroke-width="1.3"/>
              <polyline points="-4,-2 1,-5 4,1" fill="none" stroke="#FFFFFF" stroke-width="1.1"/>
            </g>
          `;
          engine.spawnParticle('glint', cx + 2, cy - 3, 1.15, globalT * 60 + idx * 40, 0.85);
        });

        // Engulfed crystal moving from (1028, 288) -> (1000, 325) -> (850, 560)
        const engU = E.smoother(E.sub(localSec, 1.8, 11.5));
        const ex = E.lerp(1028, 865, engU);
        const ey = E.lerp(288, 555, engU);
        html += `
          <g transform="translate(${ex.toFixed(1)} ${ey.toFixed(1)}) rotate(${(engU * 42).toFixed(1)})">
            <polygon points="-13,-7 4,-15 16,-3 8,13 -10,10" fill="#CBD5E1" stroke="#334155" stroke-width="1.6"/>
            <polyline points="-7,-3 3,-9 9,-1" fill="none" stroke="#FFFFFF" stroke-width="1.3"/>
          </g>
        `;
        g.innerHTML = html;
        this.partGrp.appendChild(g);

        engine.lightLabels(['5 Particles', '5.1 uptake'], E.smooth(E.sub(localSec, 0.4, 2.8)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('inhaled dust', 'crystalline quartz uptake', 1.0);
          window.LivingDevices.showSizeTag({
            text: 'silica ≈ 1–5 µm',
            targetX: 1043,
            targetY: 240 + sinkY,
            tagX: 965,
            tagY: 215,
            color: '#B4690E'
          });
        }
      } else if (beat.id === '5b') {
        // Silica phagolysosome (850, 560): sharp corner presses membrane; membrane tears; cathepsin B leaks out; K+ efflux; ROS twinkle
        const tearU = E.smoother(E.sub(localSec, 0.6, 8.5));
        engine.stateCrossFade('particles.silica_membrane', tearU * 2.0);

        engine.dashDraw('signal2_cathepsin', E.sub(localSec, 3.0, 11.0), 0.9);
        engine.dashDraw('signal2_kplus', E.sub(localSec, 4.0, 12.0), 0.9);
        engine.dashDraw('signal2_ros', E.sub(localSec, 3.5, 11.5), 0.9);

        // K+ efflux particles leaving cell across right membrane at (1006, 604)
        for (let i = 0; i < 6; i++) {
          const kU = ((localSec * 0.45 + i * 0.16) % 1);
          const kx = E.lerp(985, 1042, kU);
          const ky = E.lerp(604, 604 + (i - 2.5) * 5, kU);
          engine.spawnParticle('kplus', kx, ky, 1.1, 0, Math.sin(kU * Math.PI));
        }

        // ROS twinkles near ruptured membrane (892, 578)
        [[896, 562], [912, 584], [904, 600], [924, 594]].forEach(([rx, ry], idx) => {
          const sc = 0.7 + 0.5 * Math.abs(Math.sin(globalT * 5 + idx));
          engine.spawnParticle('ros', rx, ry, sc, globalT * 50, tearU);
        });

        engine.lightLabels(['5.2 Silica phagolysosome', 'cathepsin B', 'K⁺ efflux', 'ROS'], E.smooth(E.sub(localSec, 0.4, 2.8)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('membrane rupture', 'cathepsin B + K⁺ efflux', 1.3);
        }
      } else if (beat.id === '5c') {
        // NLRP3 (EM): Signal 1 (TLR -> NF-kB priming) + Signal 2 arrive; NLRP3 monomers swing in and lock into a wheel; ASC filaments polymerise
        engine.stateCrossFade('particles.silica_membrane', 2.0);
        const wheelU = E.smoother(E.sub(localSec, 1.2, 10.5));
        engine.stateCrossFade('particles.nlrp3', wheelU * 2.0);

        engine.dashDraw('signal1_priming', E.sub(localSec, 0.4, 6.0), 0.9);
        engine.dashDraw('signal2_cathepsin', 1.0, 0.85);
        engine.dashDraw('signal2_kplus', 1.0, 0.85);
        engine.dashDraw('signal2_ros', 1.0, 0.85);

        engine.pulseSignal('signal1_priming', (localSec * 0.35) % 1, '#5B4F78', 3.0);
        engine.pulseSignal('signal2_cathepsin', (localSec * 0.4) % 1, '#1F58C8', 3.0);

        engine.lightLabels(['signal 1 · priming', 'signal 2', 'NLRP3', 'ASC', 'inflammasome'], E.smooth(E.sub(localSec, 0.5, 3.0)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('oligomerisation', 'NLRP3 + ASC inflammasome', 1.0);
        }
      } else if (beat.id === '5d') {
        // caspase-1 ignites; pro-IL-1b/IL-18 split into active dots; GSDMD cleaved and inserts into right membrane; pores open (tag "≈ 20 nm")
        engine.stateCrossFade('particles.silica_membrane', 2.0);
        engine.stateCrossFade('particles.nlrp3', 2.0);

        const poreU = E.smoother(E.sub(localSec, 1.5, 9.5));
        engine.dashDraw('caspase_il1b', poreU, 0.92);

        const g = engine.createSvgEl('g');
        const sparkSc = 0.85 + 0.35 * Math.sin(globalT * 9);
        g.innerHTML = `
          <!-- Caspase-1 activation flash at (955, 662) -->
          <g transform="translate(955 662) scale(${sparkSc.toFixed(2)})">
            <circle cx="0" cy="0" r="9" fill="#C81D63" opacity="0.24"/>
            <polygon points="0,-10 2.5,-2.5 10,0 2.5,2.5 0,10 -2.5,2.5 -10,0 -2.5,-2.5" fill="#C81D63" stroke="#FFF3C4" stroke-width="0.7"/>
          </g>
          <!-- GSDMD barrel pores opening in right membrane at (1006, 646) & (1005, 668) -->
          <g opacity="${poreU.toFixed(2)}">
            <rect x="999" y="641" width="14" height="4" rx="1.5" fill="#8E1D4E" stroke="#FFFFFF" stroke-width="0.6"/>
            <rect x="999" y="649" width="14" height="4" rx="1.5" fill="#8E1D4E" stroke="#FFFFFF" stroke-width="0.6"/>
            <rect x="998" y="663" width="14" height="4" rx="1.5" fill="#8E1D4E" stroke="#FFFFFF" stroke-width="0.6"/>
            <rect x="998" y="671" width="14" height="4" rx="1.5" fill="#8E1D4E" stroke="#FFFFFF" stroke-width="0.6"/>
          </g>
        `;
        this.partGrp.appendChild(g);

        // IL-1b & IL-18 streaming out through GSDMD pores into alveolar air
        for (let i = 0; i < 10; i++) {
          const cU = ((localSec * 0.45 + i * 0.1) % 1);
          const cx = E.lerp(996, 1068, cU);
          const cy = (i % 2 === 0 ? 647 : 669) + Math.sin(cU * Math.PI * 2 + i) * 6;
          engine.spawnParticle('cytokine', cx, cy, 1.15, 0, Math.sin(cU * Math.PI));
        }

        engine.lightLabels(['caspase-1', 'GSDMD', 'GSDMD pore ~20 nm', 'IL-1β · IL-18'], E.smooth(E.sub(localSec, 0.4, 2.8)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('pore formation', 'GSDMD membrane lysis', 1.4);
          window.LivingDevices.showSizeTag({
            text: '≈ 20 nm',
            targetX: 1006,
            targetY: 646,
            tagX: 942,
            tagY: 622,
            color: '#8E1D4E'
          });
        }
      } else if (beat.id === '5e') {
        // Right air (kept ghosted / dashed with ?, §9): dying macrophage swells and bursts (pyroptosis?);
        // released crystal drifts along dashed curve (re-uptake) back to membrane
        engine.stateCrossFade('particles.silica_membrane', 2.0);
        engine.stateCrossFade('particles.nlrp3', 2.0);

        const loopU = E.smoother(E.sub(localSec, 0.5, 10.5));
        engine.dashDraw('pyroptosis_path', loopU, 0.85);

        const swellP = (localSec * 0.3) % 1;
        const ghostR = 8 + swellP * 7;
        const ghostOp = (1 - swellP * 0.65) * 0.78;
        const rePt = engine.pointOnPath('pyroptosis_path', (localSec * 0.25) % 1);

        const g = engine.createSvgEl('g');
        g.innerHTML = `
          <!-- Ghosted / dashed pyroptosis? dying cell at (1080, 622) -->
          <circle cx="1080" cy="622" r="${ghostR.toFixed(1)}" fill="#F8D7DA" fill-opacity="0.18"
                  stroke="#7A6470" stroke-width="1.3" stroke-dasharray="3 2.5" opacity="${ghostOp.toFixed(2)}"/>
          <!-- Released silica crystal drifting along dashed re-uptake curve -->
          <g transform="translate(${rePt.x.toFixed(1)} ${rePt.y.toFixed(1)}) rotate(${(localSec * 40).toFixed(0)})" opacity="0.82">
            <polygon points="-5,-3 2,-6 6,-1 3,5 -4,4" fill="#CBD5E1" stroke="#475569" stroke-width="1.1" stroke-dasharray="2 1.2"/>
          </g>
        `;
        this.partGrp.appendChild(g);

        engine.lightLabels(['pyroptosis?', 're-uptake', 'IL-1β · IL-18'], E.smooth(E.sub(localSec, 0.4, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('vicious cycle', 'release & re-uptake (?)', 1.2);
        }
      } else if (beat.id === '5f') {
        // ★5 Asbestos: hood lip reaches along fibre, strains, and falls back THREE TIMES (each attempt shorter and more tired);
        // camera pulls out showing fibre running beyond the paper's edge onto the dark desk with cast shadow and desk size tag "> 15–20 µm";
        // ROS · enzymes seep from open cup onto epithelium!
        let hoodState = 0;
        if (localSec < 5.0) {
          // Attempt 1: reaches furthest (state 2.0), falls back
          hoodState = Math.sin((localSec / 5.0) * Math.PI) * 2.0;
        } else if (localSec < 9.5) {
          // Attempt 2: shorter reach (state 1.45), falls back
          hoodState = Math.sin(((localSec - 5.0) / 4.5) * Math.PI) * 1.45;
        } else if (localSec < 13.5) {
          // Attempt 3: tired, short reach (state 0.95), falls back to exhausted state 0.7
          hoodState = 0.3 + Math.sin(((localSec - 9.5) / 4.0) * Math.PI) * 0.65;
        } else {
          hoodState = 0.75;
        }
        engine.stateCrossFade('particles.asbestos_hood', hoodState);

        // ROS & lysosomal enzymes seeping from open cup (995, 748) onto alveolar epithelium below
        for (let i = 0; i < 9; i++) {
          const sU = ((localSec * 0.38 + i * 0.11) % 1);
          const sx = E.lerp(965 + (i - 4) * 8, 1025 + (i - 4) * 10, sU);
          const sy = E.lerp(748, 782, sU);
          engine.spawnParticle(i % 2 === 0 ? 'ros' : 'hplus', sx, sy, 1.1, globalT * 40, Math.sin(sU * Math.PI));
        }

        engine.lightLabels(['5.3 Asbestos', 'open cup', '> 15–20 µm', 'ROS · enzymes'], E.smooth(E.sub(localSec, 0.4, 2.8)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('★5 frustrated cup', '3 failed engulfment attempts', 0.9);
          // Museum size tag sitting ON THE DARK DESK tied to the breakout asbestos needle at x=1165, y=751!
          window.LivingDevices.showSizeTag({
            text: '> 15–20 µm (too long to engulf)',
            targetX: 1165,
            targetY: 751,
            tagX: 1112,
            tagY: 708,
            color: '#B4690E',
            onDesk: true
          });
        }
      } else if (beat.id === '5g') {
        // Wall: IL-1b · TNF-a travel dotted path into interstitium; neutrophils and monocytes squeeze out of capillaries (diapedesis); water-wash warms wall
        const infU = E.smoother(E.sub(localSec, 0.4, 10.5));
        engine.dashDraw('wall_il1b_tnfa', infU, 0.92);
        engine.pulseSignal('wall_il1b_tnfa', (localSec * 0.35) % 1, '#C81D63', 3.2);

        // Warm inflammatory watercolour wash in right alveolar wall
        engine.watercolourBloom({
          cx: 960,
          cy: 795,
          r: 85,
          color: '#C81D63',
          opacity: infU * 0.38
        });

        // Neutrophils & monocytes squeezing out of capillaries (diapedesis) at (846, 780) -> (885, 808) & (1040, 790) -> (1010, 812)
        const leukoDefs = [
          { x0: 846, y0: 780, x1: 892, y1: 806 },
          { x0: 1045, y0: 785, x1: 1005, y1: 812 },
          { x0: 846, y0: 780, x1: 935, y1: 810 }
        ];
        const g = engine.createSvgEl('g');
        let html = '';
        leukoDefs.forEach((lk, idx) => {
          const lU = E.smoother(E.sub(localSec, 1.0 + idx * 2.2, 9.5 + idx * 1.5));
          const lx = E.lerp(lk.x0, lk.x1, lU);
          const ly = E.lerp(lk.y0, lk.y1, lU);
          const squeezeY = (lU > 0.25 && lU < 0.7) ? 0.56 : 1.0;
          html += `
            <g transform="translate(${lx.toFixed(1)} ${ly.toFixed(1)}) scale(1 ${squeezeY.toFixed(2)})">
              <circle cx="0" cy="0" r="6.2" fill="#FDE2E4" stroke="#C81D63" stroke-width="1.1"/>
              <circle cx="-1.8" cy="-1.2" r="1.7" fill="#7A0C37"/>
              <circle cx="1.8" cy="-0.8" r="1.7" fill="#7A0C37"/>
              <circle cx="0" cy="1.8" r="1.7" fill="#7A0C37"/>
            </g>
          `;
        });
        g.innerHTML = html;
        this.partGrp.appendChild(g);

        engine.lightLabels(['5.4 Inflammation', 'IL-1β · TNF-α', 'ROS · enzymes'], E.smooth(E.sub(localSec, 0.4, 2.8)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('hours → days', 'leukocyte extravasation', 1.2);
        }
      } else if (beat.id === '5h') {
        // ★6 Decades: pencil calendar flips 1 yr … 5 … 10 … 20 yr; TGF-b · PDGF reach myofibroblasts;
        // collagen bundles hatch in and spread right -> left along wall; alveoli narrow;
        // poster's breath becomes shallow and quick!
        const decU = E.smoother(E.sub(localSec, 0.5, 15.5));
        engine.dashDraw('wall_tgfb_pdgf', E.sub(localSec, 0.4, 7.0), 0.92);
        engine.pulseSignal('wall_tgfb_pdgf', (localSec * 0.35) % 1, '#B4690E', 3.2);

        // Collagen spreads right -> left (states 0..4) & alveolar lumen narrows (states 0..1)
        engine.stateCrossFade('particles.fibrosis', decU * 4.0);
        engine.stateCrossFade('alveolar.lumen', decU * 1.0);

        // Poster's breath becomes shallow and quick (5.0s -> 2.1s period)
        engine.breath.shallow = decU;

        // Calendar year steps: 1 yr -> 5 yr -> 10 yr -> 20 yr
        const yearSteps = [1, 2, 5, 10, 15, 20];
        const stepFloat = decU * (yearSteps.length - 1);
        const stepIdx = Math.min(yearSteps.length - 1, Math.floor(stepFloat));
        const flipProg = stepFloat - stepIdx;

        engine.lightLabels(['5.5 Fibrosis', 'TGF-β · PDGF', 'collagen'], E.smooth(E.sub(localSec, 0.5, 3.0)));
        if (window.LivingDevices) {
          window.LivingDevices.showCalendar({
            x: 985,
            y: 835,
            years: yearSteps[stepIdx],
            flipProgress: flipProg
          });
          window.LivingDevices.showStopwatch(`${yearSteps[stepIdx]} years`, '★6 progressive fibrosis', 2.4);
        }
      }
    }
  };

  window.LivingEngine.registerScene(Scene6);
})();
