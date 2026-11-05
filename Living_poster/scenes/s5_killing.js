/**
 * s5_killing.js — Section 2.7 · Killing & digestion: "the furnace" (Nerea · ~70 s)
 * Beats 7a–7f:
 * - 7a (12 s): Membrane (EM): NOX2 assembles — p47 · p67 · p40phox and Rac-GTP slide from cytosol
 *   and lock onto gp91phox · p22phox at (685, 678).
 * - 7b (12 s): NADPH → NADP⁺ glows on the cytosolic side; e⁻ spark crosses the membrane;
 *   O₂ → O₂•⁻ → H₂O₂ star-bursts bloom IN THE LUMEN; stopwatch "seconds".
 * - 7c (11 s): V-ATPase spins at (671, 624) and H⁺ stream in; pH gauge returns and drops to 4.5;
 *   lumen glows like a kiln.
 * - 7d (12 s): Acid hydrolases wake (cathepsins, lipases, nucleases, lysozyme), each nibbling its target.
 * - 7e (11 s): Bacterium cracks, splits and crumbles into fragments; stopwatch "≈ minutes–hours".
 * - 7f (12 s): Circle of life: amino-acid dots leave through exporter; one hero dot floats all the
 *   way up to the ribosome on the ER (888, 168) and is built into the next enzyme!
 */
(function () {
  'use strict';

  const Scene5 = {
    id: 's5_killing',
    order: 5,
    sectionNum: '2.7',
    title: '2.7 · Killing & digestion ("the furnace")',
    speaker: 'Nerea',
    color: '#C0392B',

    beats: [
      {
        id: '7a',
        label: 'NOX2 assembly on phagolysosome membrane (gp91 · p22 + p47 · p67 · p40 + Rac-GTP)',
        duration: 12,
        em: true,
        speakerChipText: '2.7 · Killing & digestion — Nerea',
        camFrom: [470, 560, 320, 245],
        camTo: [590, 610, 195, 150]
      },
      {
        id: '7b',
        label: 'Respiratory burst: NADPH → NADP⁺ · e⁻ transfer · lumenal O₂ → O₂•⁻ → H₂O₂',
        duration: 12,
        camFrom: [590, 610, 195, 150],
        camTo: [565, 598, 225, 175]
      },
      {
        id: '7c',
        label: 'V-ATPase proton pump · pH drops to 4.5 · kiln glow',
        duration: 11,
        camFrom: [565, 598, 225, 175],
        camTo: [530, 575, 240, 185]
      },
      {
        id: '7d',
        label: 'Acid hydrolases wake (cathepsins · lipases · nucleases · lysozyme)',
        duration: 12,
        camFrom: [530, 575, 240, 185],
        camTo: [518, 575, 230, 180]
      },
      {
        id: '7e',
        label: 'Bacterium cracks, splits, and crumbles into fragments',
        duration: 11,
        camFrom: [518, 575, 230, 180],
        camTo: [515, 570, 245, 190]
      },
      {
        id: '7f',
        label: 'Circle of life: amino acids exported → hero dot floats up to ER ribosome',
        duration: 12,
        camFrom: [515, 570, 245, 190],
        camTo: [470, 120, 520, 640]
      }
    ],

    init(engine) {
      this.engine = engine;
      this.killGrp = engine.createSvgEl('g', { id: 'scene5-killing-overlays' });
      engine.dom.layerCell.appendChild(this.killGrp);
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      if (!this.killGrp) this.init(engine);
      this.killGrp.innerHTML = '';

      if (beat.id === '7a') {
        // Membrane (EM): NOX2 assembles — p47 · p67 · p40phox and Rac-GTP slide from cytosol and lock onto gp91phox · p22phox at (685, 678)
        const slideU = E.membraneSpring(E.sub(localSec, 0.6, 8.2));
        const px = E.lerp(728, 695, slideU);
        const py = E.lerp(666, 675, slideU);
        const rx = E.lerp(724, 694, slideU);
        const ry = E.lerp(696, 687, slideU);

        const g = engine.createSvgEl('g');
        g.innerHTML = `
          <!-- Membrane-embedded gp91phox · p22phox at (685, 678) -->
          <rect x="679" y="670" width="9" height="16" rx="3" fill="#B84B18" stroke="#FFFFFF" stroke-width="0.9"/>
          <rect x="682" y="684" width="7" height="9" rx="2.5" fill="#D96B27" stroke="#FFFFFF" stroke-width="0.8"/>
          <!-- Sliding cytosolic p47 · p67 · p40phox subunits -->
          <g transform="translate(${px.toFixed(1)} ${py.toFixed(1)})">
            <rect x="-9" y="-9" width="18" height="7" rx="3" fill="#E87D1E" stroke="#FFFFFF" stroke-width="0.8"/>
            <rect x="-8" y="-2" width="17" height="7" rx="3" fill="#F59E0B" stroke="#FFFFFF" stroke-width="0.8"/>
            <rect x="-7" y="5" width="15" height="6" rx="2.5" fill="#FBBF24" stroke="#FFFFFF" stroke-width="0.8"/>
          </g>
          <!-- Sliding Rac-GTP -->
          <g transform="translate(${rx.toFixed(1)} ${ry.toFixed(1)})">
            <circle cx="0" cy="0" r="5.0" fill="#DC2626" stroke="#FFFFFF" stroke-width="0.8"/>
          </g>
        `;
        this.killGrp.appendChild(g);

        engine.lightLabels(['2.7 Killing', 'NOX2', 'gp91phox · p22phox', 'p47 · p67 · p40phox', 'Rac-GTP'], E.smooth(E.sub(localSec, 0.5, 3.0)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('≈ seconds', 'NOX2 complex assembly', 1.2);
        }
      } else if (beat.id === '7b') {
        // NADPH -> NADP+ glows on cytosolic side; e- spark crosses membrane; O2 -> O2•- -> H2O2 star-bursts bloom IN THE LUMEN (§9)!
        const eProg = (localSec * 1.35) % 1;
        const ex = E.lerp(698, 662, eProg);
        const ey = E.lerp(686, 673, eProg);

        const g = engine.createSvgEl('g');
        g.innerHTML = `
          <!-- Docked NOX2 holoenzyme on membrane (685, 678) -->
          <rect x="679" y="670" width="9" height="18" rx="3" fill="#B84B18" stroke="#FFFFFF" stroke-width="0.8"/>
          <rect x="687" y="668" width="14" height="16" rx="3" fill="#F59E0B" stroke="#FFFFFF" stroke-width="0.8"/>
          <!-- Cytosolic NADPH -> NADP+ warm glow at (716, 690) -->
          <circle cx="716" cy="688" r="14" fill="url(#halo-warm-grad)" opacity="0.9"/>
          <!-- Transmembrane electron spark e- crossing into lumen -->
          <circle cx="${ex.toFixed(1)}" cy="${ey.toFixed(1)}" r="3.2" fill="#FACC15" stroke="#FFFFFF" stroke-width="0.9"/>
        `;
        this.killGrp.appendChild(g);

        // Lumenal ROS star-bursts strictly inside phagolysosome (cx=622, cy=665, r=64)
        const burstCoords = [
          [658, 672],
          [644, 660],
          [648, 682],
          [634, 670],
          [638, 652]
        ];
        burstCoords.forEach(([bx, by], idx) => {
          const phase = localSec * 3.4 - idx * 0.65;
          if (phase > 0) {
            const sc = 0.75 + 0.55 * Math.abs(Math.sin(phase));
            engine.spawnParticle('ros', bx, by, sc, globalT * 55 + idx * 35, 0.95);
          }
        });

        engine.lightLabels(['NOX2', 'NADPH → NADP⁺', 'e⁻', 'O₂ → O₂•⁻ → H₂O₂'], E.smooth(E.sub(localSec, 0.4, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('seconds', 'oxidative burst in lumen', 1.8);
        }
      } else if (beat.id === '7c') {
        // V-ATPase spins at (671, 624) and H+ stream in; pH gauge returns and drops to 4.5; lumen glows like a kiln
        const kilnU = E.smoother(E.sub(localSec, 0.5, 8.0));
        const phVal = E.lerp(5.5, 4.5, kilnU);
        const vRot = (globalT * 180) % 360;

        engine.watercolourBloom({
          cx: 622,
          cy: 665,
          r: 62,
          color: '#7A3FB5',
          opacity: 0.35 + 0.45 * kilnU
        });

        const g = engine.createSvgEl('g');
        g.innerHTML = `
          <!-- Spinning V-ATPase rotor at (671, 624) -->
          <g transform="translate(671 624) rotate(${vRot.toFixed(1)})">
            <circle cx="0" cy="0" r="7.8" fill="#E75A8B" stroke="#FFFFFF" stroke-width="1.0"/>
            <path d="M-7.5,0 H7.5 M0,-7.5 V7.5" stroke="#FFFFFF" stroke-width="1.3"/>
          </g>
        `;
        this.killGrp.appendChild(g);

        // H+ protons streaming from V-ATPase (671, 624) into phagolysosome lumen (622, 665)
        for (let i = 0; i < 8; i++) {
          const pU = ((localSec * 0.65 + i * 0.125) % 1);
          const hx = E.lerp(671, 622 + Math.cos(i * 1.9) * 26, pU);
          const hy = E.lerp(624, 665 + Math.sin(i * 2.1) * 26, pU);
          engine.spawnParticle('hplus', hx, hy, 1.1, 0, Math.sin(pU * Math.PI));
        }

        engine.lightLabels(['V-ATPase', 'H⁺', 'pH 4.5', '2.6 Phagolysosome'], E.smooth(E.sub(localSec, 0.4, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showPhGauge({ x: 545, y: 695, ph: phVal, scale: 1.15 });
          window.LivingDevices.showStopwatch('pH 4.5', 'V-ATPase acidification', 1.4);
        }
      } else if (beat.id === '7d') {
        // Acid hydrolases wake (cathepsins, lipases, nucleases, lysozyme), each nibbling its target around (618, 669)
        engine.watercolourBloom({ cx: 622, cy: 665, r: 62, color: '#7A3FB5', opacity: 0.72 });

        const nibbleU = E.smoother(E.sub(localSec, 0.5, 5.5));
        const hydroDefs = [
          { x0: 602, y0: 635, tx: 611, ty: 658, col: '#1F58C8' }, // lysozyme
          { x0: 640, y0: 619, tx: 625, ty: 658, col: '#4338CA' }, // cathepsins
          { x0: 652, y0: 696, tx: 627, ty: 676, col: '#0369A1' }, // lipases
          { x0: 601, y0: 707, tx: 610, ty: 677, col: '#6D28D9' }  // nucleases
        ];

        const g = engine.createSvgEl('g');
        let html = '';
        hydroDefs.forEach((h, idx) => {
          const osc = Math.sin(globalT * 9.5 + idx * 1.6) * 2.4 * nibbleU;
          const ax = E.lerp(h.x0, h.tx, nibbleU) + osc;
          const ay = E.lerp(h.y0, h.ty, nibbleU) - osc * 0.6;
          const ang = Math.atan2(669 - ay, 618 - ax) * (180 / Math.PI);
          html += `
            <g transform="translate(${ax.toFixed(1)} ${ay.toFixed(1)}) rotate(${ang.toFixed(1)})">
              <path d="M3,-3 A5.5,5.5 0 1 0 3,3 L0,0 Z" fill="${h.col}" stroke="#FFFFFF" stroke-width="0.8"/>
            </g>
          `;
        });
        g.innerHTML = html;
        this.killGrp.appendChild(g);

        engine.lightLabels(['cathepsins', 'lipases', 'nucleases', 'lysozyme', '2.7 Killing'], E.smooth(E.sub(localSec, 0.4, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showPhGauge({ x: 545, y: 695, ph: 4.5, scale: 1.1 });
          window.LivingDevices.showStopwatch('active at pH 4.5', 'hydrolase digestion', 1.2);
        }
      } else if (beat.id === '7e') {
        // Bacterium cracks, splits and crumbles into fragments; stopwatch "≈ minutes–hours"
        const crackU = E.smoother(E.sub(localSec, 0.5, 9.0));
        engine.stateCrossFade('killing.bacterium', crackU * 3.0);
        engine.watercolourBloom({ cx: 622, cy: 665, r: 62, color: '#7A3FB5', opacity: 0.65 });

        engine.lightLabels(['2.7 Killing', '2.6 Phagolysosome', 'pH 4.5'], E.smooth(E.sub(localSec, 0.4, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showPhGauge({ x: 545, y: 695, ph: 4.5, scale: 1.05 });
          window.LivingDevices.showStopwatch('≈ minutes–hours', 'complete bacterial lysis', 1.6);
        }
      } else if (beat.id === '7f') {
        // Circle of life: amino-acid dots leave through exporter (650, 723); one hero dot floats all the way up
        // to the ribosome on the ER (888, 168) and is built into the next enzyme!
        engine.stateCrossFade('killing.bacterium', 3.0);
        const heroU = E.smoother(E.sub(localSec, 0.6, 10.8));
        engine.dashDraw('amino_recycle', heroU, 0.92);

        // Stream of recycled amino acid particles along amino_recycle
        for (let i = 0; i < 7; i++) {
          const pU = ((localSec * 0.35 + i * 0.14) % 1);
          const pt = engine.pointOnPath('amino_recycle', pU);
          engine.spawnParticle('amino', pt.x, pt.y, 1.15, 0, Math.sin(pU * Math.PI));
        }

        // Hero amino acid with warm halo rising all the way to the ER ribosome at (888, 168)
        const hPt = engine.pointOnPath('amino_recycle', heroU);
        const heroGrp = engine.createSvgEl('g', {
          transform: `translate(${hPt.x.toFixed(1)} ${hPt.y.toFixed(1)})`
        });
        heroGrp.innerHTML = `
          <circle cx="0" cy="0" r="10" fill="url(#halo-warm-grad)" opacity="0.95"/>
          <circle cx="0" cy="0" r="3.8" fill="#1E9B6B" stroke="#FFFFFF" stroke-width="1.1"/>
        `;
        this.killGrp.appendChild(heroGrp);

        engine.lightLabels(['reuse', 'recycled', '3.1 Rough ER', 'ribosome'], E.smooth(E.sub(localSec, 0.5, 3.0)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('circle of life', 'amino acids → new enzyme', 1.2);
        }
      }
    }
  };

  window.LivingEngine.registerScene(Scene5);
})();
