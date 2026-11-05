/**
 * s4_fusion.js — Section 4 · Phagosome–lysosome fusion: "the kiss" (Eneritz · ~70 s)
 * Beats 4a–4f:
 * - 4a (10 s): Lysosome arrives along blue route; one take from 2j resumes; membranes approach at (470, 680).
 * - 4b (12 s): Tether: Rab7-GTP and Arl8b-GTP light up; HOPS arch draws in and bridges them.
 * - 4c (14 s): Bullet time: everything else slows, paper dims, stopwatch reads "≈ milliseconds",
 *   EM flash, size tag "≈ 12 nm"; four SNARE helices (syntaxin-7 · Vti1b · syntaxin-8 + VAMP7) zip N → C.
 * - 4d (12 s): Pore: fusion pore opens like an iris, hydrolases and H⁺ pour in, lumen bleeds red → violet,
 *   normal time resumes.
 * - 4e (11 s): Recycle: NSF with α-SNAP grips cis-SNARE bundle, ATP sparks, NSF turns, SNAREs spring apart.
 * - 4f (11 s): Pull back: fused compartment flows along violet arrow into giant phagolysosome (622, 665); both routes lit.
 */
(function () {
  'use strict';

  const Scene4 = {
    id: 's4_fusion',
    order: 4,
    sectionNum: '4',
    title: '4 · Fusion ("the kiss")',
    speaker: 'Eneritz',
    color: '#7A3FB5',

    beats: [
      {
        id: '4a',
        label: 'Lysosome arrives along blue route · membranes approach',
        duration: 10,
        speakerChipText: '4 · Phagosome–lysosome fusion — Eneritz',
        camFrom: [310, 520, 380, 290],
        camTo: [350, 535, 310, 240]
      },
      {
        id: '4b',
        label: 'a · Tether: Rab7-GTP + Arl8b-GTP bridged by HOPS',
        duration: 12,
        camFrom: [350, 535, 310, 240],
        camTo: [388, 560, 210, 165]
      },
      {
        id: '4c',
        label: 'b · Bullet-time SNARE zipper (syntaxin-7 · Vti1b · syntaxin-8 + VAMP7)',
        duration: 14,
        em: true,
        bulletTime: true,
        camFrom: [388, 560, 210, 165],
        camTo: [425, 572, 165, 130]
      },
      {
        id: '4d',
        label: 'c · Fusion pore opens · hydrolases & H⁺ pour in · violet bloom',
        duration: 12,
        camFrom: [425, 572, 165, 130],
        camTo: [400, 585, 225, 175]
      },
      {
        id: '4e',
        label: 'd · Recycle: NSF + α-SNAP + ATP disassemble cis-SNAREs',
        duration: 11,
        camFrom: [400, 585, 225, 175],
        camTo: [435, 615, 210, 165]
      },
      {
        id: '4f',
        label: 'Convergence into giant phagolysosome (2.6)',
        duration: 11,
        camFrom: [435, 615, 210, 165],
        camTo: [345, 515, 420, 325]
      }
    ],

    init(engine) {
      this.engine = engine;
      this.fusionGrp = engine.createSvgEl('g', { id: 'scene4-fusion-overlays' });
      engine.dom.layerCell.appendChild(this.fusionGrp);
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      if (!this.fusionGrp) this.init(engine);
      this.fusionGrp.innerHTML = '';

      if (beat.id === '4a') {
        // Lysosome arrives from Blue Route (640, 560) -> Station A (461, 593); membranes approach at (470, 680)
        const arrU = E.smoother(E.sub(localSec, 0.4, 8.5));
        const lx = E.lerp(565, 461, arrU);
        const ly = E.lerp(548, 593, arrU);

        const lys = engine.createSvgEl('g', {
          transform: `translate(${lx.toFixed(1)} ${ly.toFixed(1)})`
        });
        lys.innerHTML = `
          <circle cx="0" cy="0" r="14" fill="#E8DAF6" stroke="#1F58C8" stroke-width="2.2" opacity="0.92"/>
          <circle cx="-4" cy="-3" r="2.3" fill="#1F58C8"/>
          <circle cx="4" cy="2" r="2.1" fill="#1F58C8"/>
          <circle cx="-1" cy="5" r="1.8" fill="#19B5E8"/>
        `;
        this.fusionGrp.appendChild(lys);

        engine.dashDraw('red_route', 0.85, 0.85);
        engine.dashDraw('blue_route', 0.85 + 0.15 * arrU, 0.9);
        engine.pulseSignal('blue_route', (globalT * 0.4) % 1, '#1F58C8', 3.4);
        engine.lightLabels(['4 Fusion', '2.5', '3.6 Lysosome'], E.smooth(E.sub(localSec, 0.5, 3.0)));

        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('t = 15 min', 'routes converge at V', 1.2);
        }
      } else if (beat.id === '4b') {
        // Tether: Rab7-GTP (465, 634) and Arl8b-GTP (462, 607) light up; HOPS arch draws in and bridges them
        const rabU = E.smooth(E.sub(localSec, 0.4, 3.2));
        const hopsU = E.smoother(E.sub(localSec, 2.2, 8.5));

        const g = engine.createSvgEl('g');
        const archLen = 42;
        const archDash = (archLen * (1 - hopsU)).toFixed(1);
        g.innerHTML = `
          <!-- Docked lysosome at Station A (461, 593) -->
          <circle cx="461" cy="593" r="14" fill="#E8DAF6" stroke="#1F58C8" stroke-width="2.2" opacity="0.92"/>
          <!-- Arl8b-GTP on lysosome membrane -->
          <circle cx="462" cy="607" r="${(4.2 * rabU).toFixed(2)}" fill="#9B6A3C" stroke="#FFFFFF" stroke-width="0.9"/>
          <!-- Rab7-GTP on late phagosome membrane -->
          <circle cx="465" cy="634" r="${(4.5 * rabU).toFixed(2)}" fill="#C0392B" stroke="#FFFFFF" stroke-width="0.9"/>
          <!-- HOPS complex tethering arch -->
          <path d="M462,607 C445,614 445,627 465,634" fill="none" stroke="#7A3FB5" stroke-width="4.4"
                stroke-linecap="round" stroke-dasharray="${archLen}" stroke-dashoffset="${archDash}"/>
          <g opacity="${hopsU.toFixed(2)}">
            <rect x="421" y="614" width="26" height="12" rx="4" fill="#7A3FB5" stroke="#FFFFFF" stroke-width="0.8"/>
            <text x="434" y="622.5" text-anchor="middle" font-family="'Segoe UI Variable Text', sans-serif"
                  font-size="6.5" font-weight="700" fill="#FFFFFF">HOPS</text>
          </g>
        `;
        this.fusionGrp.appendChild(g);

        engine.lightLabels(['4 Fusion', 'a tether', 'Rab7', 'Arl8b', 'HOPS'], E.smooth(E.sub(localSec, 0.5, 3.0)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('t = 15 min', 'HOPS tethering bridge', 1.0);
        }
      } else if (beat.id === '4c') {
        // Bullet time: paper dims, stopwatch reads "≈ milliseconds", EM flash, size tag "≈ 12 nm",
        // four SNARE helices (syntaxin-7 · Vti1b · syntaxin-8 + VAMP7) zip N -> C pulling membranes together!
        const dimU = E.smooth(E.sub(localSec, 0.2, 2.0)) * (1 - E.smooth(E.sub(localSec, 12.2, 13.8)));
        engine.dom.bulletDimmer.setAttribute('opacity', (dimU * 0.58).toFixed(3));

        const zipU = E.smoother(E.sub(localSec, 1.5, 10.8));
        engine.stateCrossFade('fusion.pore', zipU * 1.0);

        // Spotlight ring around Station B (505, 615) <-> Phagosome (491, 640)
        const g = engine.createSvgEl('g');
        let helicesHtml = `
          <circle cx="498" cy="627" r="28" fill="#FFFDF7" fill-opacity="0.22"
                  stroke="#7A3FB5" stroke-width="1.2" stroke-dasharray="3 2.5"/>
        `;

        const snareColors = ['#2E86AB', '#3FA796', '#8BAF3A', '#E07A5F'];
        snareColors.forEach((col, s) => {
          const offset = (s - 1.5) * 3.8 * (1 - 0.78 * zipU);
          const nSplay = (s - 1.5) * 9.5 * (1 - zipU);
          const x0 = 486 + nSplay;
          const y0 = 614 - Math.abs(nSplay) * 0.4;
          const xm = 494 + offset * 0.6 + Math.sin(zipU * Math.PI * 3 + s) * 1.6;
          const ym = 625 + offset * 0.4;
          const x1 = 497 + (s - 1.5) * 1.1;
          const y1 = 635 - (s - 1.5) * 0.8;
          helicesHtml += `<path d="M${x0.toFixed(1)},${y0.toFixed(1)} Q${xm.toFixed(1)},${ym.toFixed(1)} ${x1.toFixed(1)},${y1.toFixed(1)}"
                                fill="none" stroke="${col}" stroke-width="2.2" stroke-linecap="round"/>`;
        });

        // N -> C directional indicator
        const ncOp = E.smooth(E.sub(localSec, 2.5, 5.0));
        helicesHtml += `
          <g opacity="${ncOp.toFixed(2)}">
            <text x="478" y="616" font-family="ui-monospace, monospace" font-size="6.5" font-weight="800" fill="#5D2D91">N</text>
            <path d="M484,615 L492,624" fill="none" stroke="#5D2D91" stroke-width="1.3" stroke-linecap="round"/>
            <text x="493" y="630" font-family="ui-monospace, monospace" font-size="6.5" font-weight="800" fill="#5D2D91">C</text>
          </g>
        `;
        g.innerHTML = helicesHtml;
        this.fusionGrp.appendChild(g);

        engine.lightLabels(['b zipper', 'syntaxin-7', 'Vti1b', 'syntaxin-8', 'VAMP7', 'N → C'], E.smooth(E.sub(localSec, 0.5, 2.8)));

        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('≈ milliseconds', 'bullet-time SNARE zipper', 0.12);
          window.LivingDevices.showSizeTag({
            text: '≈ 12 nm',
            targetX: 498,
            targetY: 625,
            tagX: 454,
            tagY: 590,
            color: '#7A3FB5'
          });
        }
      } else if (beat.id === '4d') {
        // Pore: fusion pore opens like an iris, hydrolases and H+ pour in, lumen bleeds red -> violet, normal time resumes
        const poreU = E.smoother(E.sub(localSec, 0.4, 7.5));
        engine.stateCrossFade('fusion.pore', 1.0 + poreU * 1.0);

        // Violet watercolour bloom inside Late Phagosome (470, 680)
        engine.watercolourBloom({
          cx: 470,
          cy: 680,
          r: 44,
          color: '#7A3FB5',
          opacity: poreU * 0.65
        });

        // Streaming hydrolases (cobalt) & H+ (cyan) through Station C pore (518, 651) -> (470, 680)
        for (let i = 0; i < 12; i++) {
          const pU = ((localSec * 0.48 + i * 0.085) % 1);
          const px = E.lerp(518, 466 + Math.cos(i * 1.7) * 20, pU);
          const py = E.lerp(651, 680 + Math.sin(i * 2.3) * 20, pU);
          engine.spawnParticle(i % 2 === 0 ? 'hplus' : 'amino', px, py, 1.05, 0, Math.sin(pU * Math.PI));
        }

        engine.lightLabels(['c pore', '4 Fusion'], E.smooth(E.sub(localSec, 0.4, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('≈ seconds', 'fusion pore dilation', 1.0);
        }
      } else if (beat.id === '4e') {
        // Recycle: NSF with alpha-SNAP grips cis-SNARE bundle at (522, 687), ATP sparks, NSF turns, SNAREs spring apart
        engine.stateCrossFade('fusion.pore', 2.0);
        const recU = E.smoother(E.sub(localSec, 0.5, 8.5));
        const rotDeg = recU * 240;
        const sparkOp = Math.sin(E.sub(localSec, 2.0, 6.2) * Math.PI);
        const springU = E.membraneSpring(E.sub(localSec, 3.8, 9.0));

        const g = engine.createSvgEl('g');
        const snareColors = ['#2E86AB', '#3FA796', '#8BAF3A', '#E07A5F'];
        let html = `
          <!-- NSF hexamer wheel + alpha-SNAP collar at (538, 688) -->
          <g transform="translate(538 688) rotate(${rotDeg.toFixed(1)})">
            <circle cx="0" cy="0" r="9.2" fill="#E2E6EE" stroke="#6E7787" stroke-width="1.5"/>
            <circle cx="6.2" cy="0" r="2.4" fill="#6E7787"/>
            <circle cx="-6.2" cy="0" r="2.4" fill="#6E7787"/>
            <circle cx="3.1" cy="5.3" r="2.4" fill="#6E7787"/>
            <circle cx="-3.1" cy="5.3" r="2.4" fill="#6E7787"/>
            <circle cx="3.1" cy="-5.3" r="2.4" fill="#6E7787"/>
            <circle cx="-3.1" cy="-5.3" r="2.4" fill="#6E7787"/>
          </g>
          <!-- alpha-SNAP adaptor -->
          <ellipse cx="529" cy="688" rx="3.2" ry="6.5" fill="#A3AAB8" stroke="#475569" stroke-width="0.9"/>
          <!-- ATP spark burst -->
          <g opacity="${sparkOp.toFixed(2)}">
            <polygon points="546,676 550,670 551,675 557,673 552,679 556,683 549,681 545,686 546,679"
                     fill="#FACC15" stroke="#CA8A04" stroke-width="0.7"/>
            <text x="556" y="672" font-family="ui-monospace, monospace" font-size="6.2" font-weight="800" fill="#B45309">ATP</text>
          </g>
        `;

        snareColors.forEach((col, k) => {
          const sy = 681 + k * 4.0 + (k - 1.5) * 9.0 * springU;
          const sx0 = 516 + springU * 4;
          const sx1 = 528 + springU * 11;
          html += `<path d="M${sx0.toFixed(1)},${sy.toFixed(1)} Q${((sx0 + sx1) * 0.5).toFixed(1)},${(sy - 3 * springU).toFixed(1)} ${sx1.toFixed(1)},${(sy + (k - 1.5) * 2.8 * springU).toFixed(1)}"
                         fill="none" stroke="${col}" stroke-width="2.0" stroke-linecap="round"/>`;
        });
        g.innerHTML = html;
        this.fusionGrp.appendChild(g);

        engine.lightLabels(['d recycle', 'NSF', 'α-SNAP'], E.smooth(E.sub(localSec, 0.4, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('ATP hydrolysis', 'cis-SNARE disassembly', 1.3);
        }
      } else if (beat.id === '4f') {
        // Pull back: fused compartment flows along violet arrow into giant phagolysosome (622, 665); both routes lit
        const flowU = E.smoother(E.sub(localSec, 0.5, 8.8));
        engine.dashDraw('red_route', 1.0, 0.9);
        engine.dashDraw('blue_route', 1.0, 0.9);
        engine.pulseSignal('red_route', (globalT * 0.35) % 1, '#E0452B', 3.4);
        engine.pulseSignal('blue_route', (globalT * 0.38) % 1, '#1F58C8', 3.4);

        engine.watercolourBloom({
          cx: 470,
          cy: 680,
          r: 42,
          color: '#7A3FB5',
          opacity: 0.45
        });
        engine.watercolourBloom({
          cx: 622,
          cy: 665,
          r: 62 * flowU,
          color: '#6C2EB9',
          opacity: flowU * 0.58
        });

        const bridge = engine.createSvgEl('path', {
          d: 'M515,676 C538,674 548,670 558,668',
          fill: 'none',
          stroke: '#6C2EB9',
          'stroke-width': '4.8',
          'stroke-linecap': 'round',
          opacity: flowU.toFixed(2)
        });
        this.fusionGrp.appendChild(bridge);

        engine.lightLabels(['4 Fusion', '2.6 Phagolysosome'], E.smooth(E.sub(localSec, 0.5, 2.8)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('phagolysosome', 'both routes converged', 1.0);
        }
      }
    }
  };

  window.LivingEngine.registerScene(Scene4);
})();
