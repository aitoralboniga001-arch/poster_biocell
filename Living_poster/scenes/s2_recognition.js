/**
 * s2_recognition.js — Section 2 · Recognition → Phagocytosis → Maturation (Nerea, ★3 One Take, ~90 s)
 * Beats 2a..2j:
 *  2a: Bacterium drifts in, opsonins glint, LPS shimmers, size tag "≈ 2 µm"
 *  2b: Turret 40× -> EM flash, receptors bridge one by one with bond flashes, size tag "receptor ≈ 10 nm"
 *  2c: Branch 1: TLR4 -> MyD88 -> NF-κB pulse to nucleus glow
 *  2d: Branch 2: Src phosphorylates ITAM -> Syk docks -> PI3K -> forks into separate Cdc42->WASP and Rac->WAVE
 *  2e: Pull back to 40×: Arp2/3 nucleates 70° F-actin branches like frost on glass, pushing membrane
 *  2f: 10×: Pseudopod arms wrap bacterium (4 states) & seal with membrane kiss ripple, stopwatch "≈ 1 min"
 *  2g: ★3 One take begins: camera locks onto bacterium in nascent phagosome down red route, pH gauge 7.2
 *  2h: Early phagosome: Rab5-GTP lights up, H+ trickle in, pH gauge drops to 6.5, frame warms, stopwatch "≈ 10 min"
 *  2i: Late phagosome: Rab5 -> Rab7 conversion on the same vesicle, pH drops to 5.5, bacterium dims, stopwatch "≈ 30 min"
 *  2j: Hold: lysosome waits on blue route, "to be continued in 4"
 */
(function () {
  'use strict';

  // 70-degree dendritic F-actin branches at the leading edge (barbed ends pushing membrane)
  const ACTIN_TREES = [
    { root: [164, 345], mother: [145, 332], b1: [145, 348], b2: [143, 320] },
    { root: [162, 378], mother: [141, 366], b1: [141, 384], b2: [140, 355] },
    { root: [160, 412], mother: [140, 400], b1: [141, 418], b2: [139, 388] },
    { root: [164, 452], mother: [144, 440], b1: [145, 458], b2: [142, 428] },
    { root: [142, 285], mother: [115, 272], b1: [88, 274],  b2: [62, 284] },
    { root: [142, 505], mother: [115, 516], b1: [88, 514],  b2: [62, 502] }
  ];

  const RECEPTOR_BRIDGES = [
    { name: 'TLR4–MD-2 + CD14 → LPS', x0: 138, y0: 325, x1: 96, y1: 325, col: '#8E3B8F' },
    { name: 'MR → glycans',           x0: 139, y0: 369, x1: 96, y1: 369, col: '#8C583A' },
    { name: 'CR3 → iC3b',             x0: 138, y0: 393, x1: 96, y1: 393, col: '#13848C' },
    { name: 'FcγR → IgG',             x0: 139, y0: 418, x1: 96, y1: 418, col: '#1F4E9A' }
  ];

  const Scene2 = {
    id: 's2_recognition',
    order: 2,
    sectionNum: '2',
    title: '2 · Recognition & Maturation',
    speaker: 'Nerea',
    color: '#C0392B',

    beats: [
      {
        id: '2a',
        label: 'Bacterium Drifts In · Opsonins & LPS Shimmer',
        duration: 9,
        speakerChipText: '2 · Recognition — Nerea',
        camFrom: [8, 235, 370, 310],
        camTo: [12, 242, 345, 290]
      },
      {
        id: '2b',
        label: 'EM · Receptors Bridge & Bind Ligands (~10 nm)',
        duration: 10,
        em: true,
        camFrom: [12, 242, 345, 290],
        camTo: [38, 288, 215, 180]
      },
      {
        id: '2c',
        label: 'Branch 1 · TLR4 → MyD88 → NF-κB to Nucleus',
        duration: 9,
        em: true,
        camFrom: [38, 288, 215, 180],
        camTo: [75, 210, 420, 260]
      },
      {
        id: '2d',
        label: 'Branch 2 · Src → ITAM → Syk → PI3K → Cdc42/WASP & Rac/WAVE',
        duration: 10,
        em: true,
        camFrom: [75, 210, 420, 260],
        camTo: [68, 365, 215, 150]
      },
      {
        id: '2e',
        label: '40× · Arp2/3 Nucleates 70° F-Actin Frost Network',
        duration: 9,
        camFrom: [68, 365, 215, 150],
        camTo: [18, 250, 315, 280]
      },
      {
        id: '2f',
        label: '10× · Pseudopod Arms Wrap & Seal Cup (≈ 1 min)',
        duration: 9,
        camFrom: [18, 250, 315, 280],
        camTo: [-8, 225, 450, 365]
      },
      {
        id: '2g',
        label: '★3 One Take Begins · Nascent Phagosome (pH 7.2)',
        duration: 8,
        camFrom: [-8, 225, 450, 365],
        camTo: [140, 435, 340, 275]
      },
      {
        id: '2h',
        label: '★3 Early Phagosome · Rab5-GTP & pH 6.5 (≈ 10 min)',
        duration: 9,
        camFrom: [140, 435, 340, 275],
        camTo: [215, 510, 340, 275]
      },
      {
        id: '2i',
        label: '★3 Late Phagosome · Rab5 → Rab7 Conversion & pH 5.5 (≈ 30 min)',
        duration: 10,
        camFrom: [215, 510, 340, 275],
        camTo: [310, 540, 345, 280]
      },
      {
        id: '2j',
        label: 'Hold · Lysosome Waits ("to be continued in 4")',
        duration: 7,
        camFrom: [310, 540, 345, 280],
        camTo: [330, 530, 355, 285]
      }
    ],

    init(engine) {
      this.engine = engine;
      this.overlayGrp = engine.createSvgEl('g', { id: 's2-dynamic-overlay' });
      engine.dom.layerCell.appendChild(this.overlayGrp);
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      this.overlayGrp.innerHTML = '';

      if (beat.id === '2a') {
        // Bacterium drifts in from left air (-18 -> 0) and settles; opsonins glint; LPS shimmers
        const driftIn = 1 - E.cubicOut(E.sub(localSec, 0, 3.2));
        if (driftIn > 0.01) {
          this.overlayGrp.appendChild(engine.createSvgEl('ellipse', {
            cx: (60 - driftIn * 22).toFixed(1),
            cy: '392', rx: '34', ry: '88',
            fill: '#E2E8B8', stroke: '#8C9A3A', 'stroke-width': '2.2',
            opacity: (driftIn * 0.75).toFixed(2)
          }));
        }

        // Glinting opsonins ("eat-me" flags: IgG at y=418, iC3b at y=393, glycans at y=369) & LPS fringe
        const opsPts = [[98, 325], [96, 348], [97, 369], [98, 393], [98, 418], [96, 441]];
        opsPts.forEach(([ox, oy], idx) => {
          const s = 0.65 + 0.55 * Math.sin(globalT * 4.2 + idx * 1.3);
          engine.spawnParticle('glint', ox, oy, s, globalT * 50 + idx * 30, 0.85);
        });

        engine.lightLabels(['Bacterium', 'LPS', 'IgG', 'iC3b', 'glycans'], E.smooth(E.sub(localSec, 0.8, 3.0)));
        if (window.LivingDevices) {
          window.LivingDevices.showSizeTag({
            text: '≈ 2 µm',
            targetX: 60,
            targetY: 305,
            tagX: 78,
            tagY: 274,
            color: '#5A6420'
          });
        }
      } else if (beat.id === '2b') {
        // Turret 40× -> EM: Receptors reach across one by one, each with a bond flash
        RECEPTOR_BRIDGES.forEach((br, idx) => {
          const bridgeU = E.smoother(E.sub(localSec, 0.8 + idx * 1.8, 2.4 + idx * 1.8));
          if (bridgeU > 0.01) {
            const curX = E.lerp(br.x0, br.x1, bridgeU);
            this.overlayGrp.appendChild(engine.createSvgEl('line', {
              x1: br.x0, y1: br.y0, x2: curX.toFixed(1), y2: br.y1,
              stroke: br.col, 'stroke-width': '2.6', 'stroke-linecap': 'round'
            }));
            // Bond flash when receptor engages ligand
            if (bridgeU > 0.82) {
              const flash = Math.sin(((bridgeU - 0.82) / 0.18) * Math.PI);
              engine.spawnParticle('glint', br.x1, br.y1, 1.35 + flash * 0.8, globalT * 80, 0.95);
              engine.watercolourBloom({ cx: br.x1, cy: br.y1, r: 6.5, color: br.col, opacity: 0.55 });
            }
          }
        });

        engine.lightLabels(['TLR4–MD-2', 'CD14', 'MR', 'CR3', 'FcγR', '2.1'], E.smooth(E.sub(localSec, 0.5, 2.5)));
        if (window.LivingDevices) {
          window.LivingDevices.showSizeTag({
            text: 'receptor ≈ 10 nm',
            targetX: 138,
            targetY: 325,
            tagX: 162,
            tagY: 300,
            color: '#8E3B8F'
          });
        }
      } else if (beat.id === '2c') {
        // Branch 1: TLR4 -> MyD88 -> NF-kB pulse along dotted arrow toward nucleus; nucleus glows
        const sigU = E.sub(localSec, 0.6, 5.8);
        engine.dashDraw('nfkb_signal', sigU, 0.92);
        engine.pulseSignal('nfkb_signal', sigU, '#C81D63', 4.2);

        if (localSec > 4.2) {
          const nucGlow = Math.sin(E.sub(localSec, 4.2, 8.8) * Math.PI);
          engine.watercolourBloom({
            cx: 440,
            cy: 255,
            r: 86,
            color: '#C81D63',
            opacity: nucGlow * 0.45
          });
        }
        engine.lightLabels(['MyD88', 'NF-κB → inflammation'], E.smooth(E.sub(localSec, 0.4, 2.2)));
      } else if (beat.id === '2d') {
        // Branch 2: ITAM phosphate dots pop (Src), Syk docks, PI3K, pulse forks into separate Cdc42->WASP & Rac->WAVE
        const itamU = E.sub(localSec, 0.4, 2.4);
        const sykU = E.sub(localSec, 2.0, 4.2);
        const forkU = E.sub(localSec, 4.2, 8.5);

        // Two gold ITAM phosphate dots popping at (148, 418) and (154, 419)
        if (itamU > 0.05) {
          const pScale = E.membraneSpring(itamU);
          [[149, 418.3], [154.5, 419.0]].forEach(([px, py]) => {
            this.overlayGrp.appendChild(engine.createSvgEl('circle', {
              cx: px, cy: py, r: (2.2 * pScale).toFixed(2),
              fill: '#E2B33C', stroke: '#7A5A00', 'stroke-width': '0.5'
            }));
          });
        }

        // Src -> Syk -> PI3K path
        engine.dashDraw('src_syk_pi3k', sykU, 0.95);
        engine.pulseSignal('src_syk_pi3k', sykU, '#E2B33C', 3.4);

        // Separate parallel forks: Cdc42 -> WASP and Rac -> WAVE (§9 Science Checklist)
        engine.dashDraw('cdc42_wasp_arp', forkU, 0.95);
        engine.dashDraw('rac_wave_arp', forkU, 0.95);
        engine.pulseSignal('cdc42_wasp_arp', forkU, '#E07B39', 3.2);
        engine.pulseSignal('rac_wave_arp', forkU, '#E07B39', 3.2);

        engine.lightLabels(['Src', 'ITAM', 'Syk', 'PI3K', 'Cdc42 → WASP', 'Rac → WAVE'], E.smooth(E.sub(localSec, 0.5, 2.8)));
      } else if (beat.id === '2e') {
        // Pull back to 40×: Arp2/3 nucleates 70° F-actin branches like frost on glass; barbed ends push membrane
        const frostU = E.smoother(E.sub(localSec, 0.5, 7.2));
        ACTIN_TREES.forEach((tr, idx) => {
          const tU = E.clamp((frostU * 1.35) - idx * 0.08, 0, 1);
          if (tU > 0.01) {
            const mU = E.sub(tU, 0, 0.5);
            const dU = E.sub(tU, 0.4, 1.0);
            const mx = E.lerp(tr.root[0], tr.mother[0], mU);
            const my = E.lerp(tr.root[1], tr.mother[1], mU);
            // Mother filament
            this.overlayGrp.appendChild(engine.createSvgEl('line', {
              x1: tr.root[0], y1: tr.root[1], x2: mx.toFixed(1), y2: my.toFixed(1),
              stroke: '#E07B39', 'stroke-width': '2.1', 'stroke-linecap': 'round'
            }));
            // Arp2/3 junction node at 70°
            if (dU > 0.01) {
              this.overlayGrp.appendChild(engine.createSvgEl('circle', {
                cx: tr.mother[0], cy: tr.mother[1], r: '2.2',
                fill: '#B4561C', stroke: '#FFF0E5', 'stroke-width': '0.5'
              }));
              [tr.b1, tr.b2].forEach((bEnd) => {
                const bx = E.lerp(tr.mother[0], bEnd[0], dU);
                const by = E.lerp(tr.mother[1], bEnd[1], dU);
                this.overlayGrp.appendChild(engine.createSvgEl('line', {
                  x1: tr.mother[0], y1: tr.mother[1], x2: bx.toFixed(1), y2: by.toFixed(1),
                  stroke: '#E07B39', 'stroke-width': '1.7', 'stroke-linecap': 'round'
                }));
              });
            }
          }
        });
        // Membrane bulge outward under barbed-end force
        engine.stateCrossFade('recog.arms', frostU * 0.85);
        engine.lightLabels(['Arp2/3', 'F-actin'], E.smooth(E.sub(localSec, 0.4, 2.2)));
      } else if (beat.id === '2f') {
        // 10×: Pseudopod arms reach around the bacterium (cross-fade through 4 states 0..3) and seal with a kiss ripple
        const armState = E.smoother(E.sub(localSec, 0.4, 6.8)) * 3.0;
        engine.stateCrossFade('recog.arms', armState);

        if (armState > 2.6) {
          const kissR = 6 + E.sub(localSec, 6.2, 8.8) * 24;
          const kissOp = 1 - E.sub(localSec, 6.2, 8.8);
          this.overlayGrp.appendChild(engine.createSvgEl('circle', {
            cx: '20', cy: '392', r: kissR.toFixed(1),
            fill: 'none', stroke: '#E0452B', 'stroke-width': '2.0', opacity: kissOp.toFixed(2)
          }));
        }

        engine.lightLabels(['2.2 Pseudopod'], E.smooth(E.sub(localSec, 0.4, 2.2)));
        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('≈ 1 min', 'phagocytic cup closure', 1.2);
        }
      } else if (beat.id === '2g') {
        // ★3 One take begins: camera locks onto bacterium inside nascent phagosome, travelling to (295, 575)
        const legU = E.smoother(E.sub(localSec, 0.2, 7.2));
        const pos = engine.pointOnPolyline([[60, 392], [185, 455], [295, 575]], legU);

        this._drawTravelingPhagosome(pos.x, pos.y, 36, '#FFE3D9', '#D9472F', 1.0, engine);
        engine.dashDraw('red_route', 0.35 * legU, 0.75);
        engine.lightLabels(['2.3 Nascent phagosome'], E.smooth(E.sub(localSec, 1.0, 3.0)));

        if (window.LivingDevices) {
          window.LivingDevices.showPhGauge({ x: pos.x + 56, y: pos.y - 18, ph: 7.2, scale: 1.0 });
        }
      } else if (beat.id === '2h') {
        // ★3 Early phagosome (372, 648): Rab5-GTP dots light up, H+ trickle in, pH gauge drops 7.2 -> 6.5, frame warms
        const legU = E.smoother(E.sub(localSec, 0.0, 5.2));
        const pos = engine.pointOnPolyline([[295, 575], [372, 648]], legU);
        const phVal = E.lerp(7.2, 6.5, legU);

        // Warm frame wash
        engine.watercolourBloom({ cx: pos.x, cy: pos.y, r: 95, color: '#F7B267', opacity: 0.24 * legU });
        this._drawTravelingPhagosome(pos.x, pos.y, 40, '#FFE9CF', '#E8892D', 0.92, engine);

        // Rab5-GTP dots (#E3A21A) lighting up around the cytosolic rim
        this._drawRabDots(pos.x, pos.y, 42, '#E3A21A', E.sub(localSec, 1.5, 5.0), 0, engine);

        engine.dashDraw('red_route', 0.35 + 0.25 * legU, 0.8);
        engine.lightLabels(['2.4', 'Rab5-GTP', 'pH 6.5'], E.smooth(E.sub(localSec, 1.2, 3.5)));

        if (window.LivingDevices) {
          window.LivingDevices.showPhGauge({ x: pos.x + 60, y: pos.y - 18, ph: phVal, scale: 1.05 });
          window.LivingDevices.showStopwatch('≈ 10 min', 'early phagosome', 1.5);
        }
      } else if (beat.id === '2i') {
        // ★3 Late phagosome (470, 680): Rab5 -> Rab7 conversion ON THE SAME VESICLE!
        // pH gauge drops 6.5 -> 5.5; bacterium dims.
        const legU = E.smoother(E.sub(localSec, 0.0, 5.2));
        const convU = E.smoother(E.sub(localSec, 2.5, 7.8));
        const pos = engine.pointOnPolyline([[372, 648], [470, 680]], legU);
        const phVal = E.lerp(6.5, 5.5, convU);

        // Deeper warm crimson-amber wash
        engine.watercolourBloom({ cx: pos.x, cy: pos.y, r: 105, color: '#E05A47', opacity: 0.32 });
        this._drawTravelingPhagosome(pos.x, pos.y, 44, '#F9D5CA', '#C23B2A', E.lerp(0.9, 0.55, convU), engine);

        // Rab5 dots fade out as Rab7 dots (#C0392B) bloom on the exact same vesicle rim! (§9)
        if (convU < 0.98) {
          this._drawRabDots(pos.x, pos.y, 46, '#E3A21A', 1 - convU, 0, engine);
        }
        if (convU > 0.02) {
          this._drawRabDots(pos.x, pos.y, 46, '#C0392B', convU, 25, engine);
        }

        engine.dashDraw('red_route', 0.6 + 0.22 * legU, 0.85);
        engine.lightLabels(['2.5', 'Rab7-GTP', 'pH 5.5'], E.smooth(E.sub(localSec, 1.5, 4.0)));

        if (window.LivingDevices) {
          window.LivingDevices.showPhGauge({ x: pos.x + 64, y: pos.y - 20, ph: phVal, scale: 1.08 });
          window.LivingDevices.showStopwatch('≈ 30 min', 'real time ≈ 30 min → 40 s', 1.8);
        }
      } else if (beat.id === '2j') {
        // Hold at Late Phagosome (470, 680); a lysosome waits on the blue route; "to be continued in 4"
        this._drawRabDots(470, 680, 46, '#C0392B', 1.0, 25, engine);

        // Waiting lysosome bobbing gently at (557, 578)
        const bobY = Math.sin(globalT * 2.2) * 2.5;
        this.overlayGrp.appendChild(engine.createSvgEl('circle', {
          cx: '557', cy: (578 + bobY).toFixed(1), r: '11',
          fill: '#E4D3F3', stroke: '#6F36A8', 'stroke-width': '2.2'
        }));

        // Pencil margin note: "to be continued in 4"
        const noteOp = E.smooth(E.sub(localSec, 0.6, 2.4));
        const note = engine.createSvgEl('g', { opacity: noteOp.toFixed(2) });
        note.innerHTML = `
          <rect x="422" y="746" width="128" height="22" rx="6" fill="#FAF6EE" stroke="#2B3040" stroke-width="0.9" stroke-dasharray="2.5 1.5"/>
          <text x="486" y="761" font-family="Gabriola, 'Segoe Print', serif" font-size="13.5" fill="#2B3040" text-anchor="middle">
            to be continued in 4 …
          </text>
        `;
        this.overlayGrp.appendChild(note);

        if (window.LivingDevices) {
          window.LivingDevices.showPhGauge({ x: 534, y: 660, ph: 5.5, scale: 1.05 });
        }
      }
    },

    _drawTravelingPhagosome(cx, cy, r, lumenCol, rimCol, bactOp, engine) {
      const grp = engine.createSvgEl('g', {
        transform: `translate(${cx.toFixed(1)} ${cy.toFixed(1)})`
      });
      grp.innerHTML = `
        <circle cx="0" cy="0" r="${r}" fill="${lumenCol}" stroke="${rimCol}" stroke-width="2.8" opacity="0.88"/>
        <ellipse cx="0" cy="0" rx="${(r * 0.58).toFixed(1)}" ry="${(r * 0.26).toFixed(1)}"
                 fill="#8C9A3A" stroke="#4E5A16" stroke-width="1.2" transform="rotate(-24)" opacity="${bactOp.toFixed(2)}"/>
      `;
      this.overlayGrp.appendChild(grp);
    },

    _drawRabDots(cx, cy, r, color, opacity, angleOffset, engine) {
      const angles = [-135, -95, -55, 125, 165, 205];
      angles.forEach((deg) => {
        const a = (deg + angleOffset) * (Math.PI / 180);
        const px = cx + Math.cos(a) * (r + 3.2);
        const py = cy + Math.sin(a) * (r + 3.2);
        this.overlayGrp.appendChild(engine.createSvgEl('circle', {
          cx: px.toFixed(1), cy: py.toFixed(1), r: '2.6',
          fill: color, stroke: '#FFFFFF', 'stroke-width': '0.6',
          opacity: opacity.toFixed(2)
        }));
      });
    }
  };

  window.LivingEngine.registerScene(Scene2);
})();
