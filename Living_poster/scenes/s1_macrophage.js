/**
 * s1_macrophage.js — Section 1 · Alveolar macrophage (Aitor, ~40 s)
 * Beat 1a: Ink glow traces the macrophage cell outline once, slowly; size tag "≈ 20 µm"
 * Beat 1b: ★2 The Loupe appears and glides over leading edge, Golgi, phagolysosome, silica crystal
 * Beat 1c: Loupe stops on the bacterium -> click dive into Section 2
 */
(function () {
  'use strict';

  const LOUPE_STOPS = [
    { x: 138, y: 392, name: 'Leading edge' },
    { x: 835, y: 275, name: 'Golgi stack' },
    { x: 622, y: 665, name: 'Phagolysosome' },
    { x: 862, y: 565, name: 'Silica crystal' }
  ];

  const Scene1 = {
    id: 's1_macrophage',
    order: 1,
    sectionNum: '1',
    title: '1 · Alveolar macrophage',
    speaker: 'Aitor',
    color: '#1E2433',

    beats: [
      {
        id: '1a',
        label: 'Macrophage Silhouette & Scale (≈ 20 µm)',
        duration: 13,
        speakerChipText: '1 · Alveolar macrophage — Aitor',
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: '1b',
        label: '★2 The Loupe Glides Over the Poster',
        duration: 16,
        camFrom: [-38, -22, 1176, 944],
        camTo: [-38, -22, 1176, 944]
      },
      {
        id: '1c',
        label: 'Loupe Stops on Bacterium → Dive into Section 2',
        duration: 11,
        camFrom: [-38, -22, 1176, 944],
        camTo: [12, 238, 360, 305]
      }
    ],

    init(engine) {
      this.engine = engine;
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      engine.dom.layerOpeningFinale.innerHTML = '';

      if (beat.id === '1a') {
        // An ink glow traces the cell outline once, slowly
        const traceU = E.smoother(E.sub(localSec, 0.5, 9.5));
        engine.dashDraw('cell_outline', traceU, 0.92);
        engine.pulseSignal('cell_outline', traceU, '#FFE066', 5.2);

        // Lit label: 1 Alveolar macrophage
        engine.lightLabels(['1 Alveolar macrophage'], E.smooth(E.sub(localSec, 0.3, 2.5)));

        // Size tag: "≈ 20 µm" on the cell dome (430, 118)
        if (window.LivingDevices) {
          window.LivingDevices.showSizeTag({
            text: '≈ 20 µm',
            targetX: 430,
            targetY: 118,
            tagX: 465,
            tagY: 88,
            color: '#1E2433'
          });
        }
      } else if (beat.id === '1b') {
        // ★2 The Loupe appears and drifts over 4 stations (~4s each):
        // leading edge -> Golgi -> phagolysosome -> silica crystal
        const segFloat = E.clamp(localSec / 4.0, 0, 3.999);
        const idx = Math.floor(segFloat);
        const frac = segFloat - idx;
        const p0 = LOUPE_STOPS[idx];
        const p1 = LOUPE_STOPS[Math.min(LOUPE_STOPS.length - 1, idx + 1)];

        // Hold on station for first 60% of 4s, then glide smoothly to next station
        const moveU = E.smoother(E.sub(frac, 0.58, 1.0));
        const lx = E.lerp(p0.x, p1.x, moveU);
        const ly = E.lerp(p0.y, p1.y, moveU);

        if (window.LivingDevices) {
          window.LivingDevices.setScriptedLoupe({
            x: lx,
            y: ly,
            power: 2.6,
            dive: 0
          });
        }
      } else if (beat.id === '1c') {
        // Loupe glides from silica crystal (862, 565) to bacterium (62, 392), holds, then dives!
        const glideU = E.smoother(E.sub(localSec, 0.0, 3.8));
        const diveU = E.smoother(E.sub(localSec, 5.2, 10.2));
        const lx = E.lerp(862, 62, glideU);
        const ly = E.lerp(565, 392, glideU);

        if (window.LivingDevices) {
          window.LivingDevices.setScriptedLoupe({
            x: lx,
            y: ly,
            power: 2.8,
            dive: diveU
          });
        }
        engine.lightLabels(['Bacterium', '2 Recognition'], E.sub(localSec, 3.5, 6.5));
      }
    }
  };

  window.LivingEngine.registerScene(Scene1);
})();
