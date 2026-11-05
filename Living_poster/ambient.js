/**
 * ambient.js — Gallery Mode: The "Circle of Life" 60s Seamless Loop (§5)
 * Also provides background capillary RBC flow and air dust drift for Talk/Film modes.
 */
(function () {
  'use strict';

  const ACIDIC_LUMENS = [
    { x: 372, y: 648, r: 28, n: 3 }, // 2.4 Early phagosome (pH 6.5)
    { x: 470, y: 680, r: 32, n: 4 }, // 2.5 Late phagosome (pH 5.5)
    { x: 718, y: 374, r: 22, n: 4 }, // 3.5 Late endosome
    { x: 757, y: 433, r: 22, n: 4 }, // 3.6 Lysosome
    { x: 622, y: 665, r: 48, n: 8 }, // 2.6 Phagolysosome (pH 4.5)
    { x: 850, y: 560, r: 34, n: 4 }  // 5.2 Silica phagolysosome
  ];

  const RIGHT_AIR_SILICA = [
    { x: 1072, y: 220, amp: 8, phase: 0.0 },
    { x: 1043, y: 240, amp: 7, phase: 1.3 },
    { x: 1028, y: 288, amp: 9, phase: 2.4 },
    { x: 1082, y: 352, amp: 8, phase: 3.7 },
    { x: 1018, y: 440, amp: 7, phase: 4.9 }
  ];

  const CAPILLARY_RUNS = [
    { x0: 42,  x1: 118, y: 775, n: 3, seed: 1 },
    { x0: 198, x1: 288, y: 773, n: 3, seed: 2 },
    { x0: 365, x1: 465, y: 770, n: 4, seed: 3 },
    { x0: 530, x1: 615, y: 772, n: 3, seed: 4 },
    { x0: 650, x1: 755, y: 778, n: 3, seed: 5 },
    { x0: 825, x1: 950, y: 784, n: 3, seed: 6 }
  ];

  const Ambient = {
    engine: null,

    init(engine) {
      this.engine = engine;
    },

    /**
     * Background life shared across Gallery, Talk, and Film modes:
     * - Inhaled dust drifting with the 5s breath cycle
     * - Red blood cells flowing through the septal capillaries (slowing when fibrotic)
     * - Subtle H+ Brownian trickle in acidic lumens
     */
    renderBackgroundLife(t, engine) {
      const inhale = engine.breath.inhale;
      const stiffSlow = 1 - 0.65 * engine.breath.shallow;

      // 1. Air dust drifting in with each inhale (top-left & right air)
      for (let i = 0; i < 14; i++) {
        const h1 = engine.Ease.hash(i * 13 + 1);
        const h2 = engine.Ease.hash(i * 29 + 7);
        const bx = i < 7 ? (250 + h1 * 180) : (1015 + h1 * 78);
        const by = i < 7 ? (95 + h2 * 75) : (155 + h2 * 310);
        const dx = Math.sin(t * 0.8 + i) * 4 + inhale * (i < 7 ? 7 : -5);
        const dy = Math.cos(t * 0.6 + i * 1.3) * 3 + inhale * 8;
        engine.spawnParticle('dust', bx + dx, by + dy, 0.8 + h1 * 0.6, 0, 0.35 + 0.3 * inhale);
      }

      // 2. Capillary RBC flow along the alveolar wall
      for (const cap of CAPILLARY_RUNS) {
        const span = cap.x1 - cap.x0;
        for (let k = 0; k < cap.n; k++) {
          const u = ((t * 0.085 * stiffSlow + k / cap.n + cap.seed * 0.17) % 1.0);
          const rx = cap.x0 + u * span;
          const ry = cap.y + Math.sin(u * Math.PI * 2 + cap.seed) * 1.4;
          const op = Math.sin(u * Math.PI) * 0.82;
          const rot = Math.cos(u * Math.PI * 2) * 12;
          engine.spawnParticle('rbc', rx, ry, 0.92, rot, op);
        }
      }

      // 3. V-ATPase H+ trickle + Brownian jitter inside every acidic compartment
      for (let cIdx = 0; cIdx < ACIDIC_LUMENS.length; cIdx++) {
        const lum = ACIDIC_LUMENS[cIdx];
        for (let k = 0; k < lum.n; k++) {
          const seed = cIdx * 31 + k * 7;
          const u = (t * 0.45 + seed * 0.19) % 1.0;
          const ang = (seed * 57 + Math.sin(t * 1.8 + k) * 18) * (Math.PI / 180);
          const rad = lum.r * (1.05 - u * 0.78);
          const hx = lum.x + Math.cos(ang) * rad + Math.sin(t * 5.2 + seed) * 1.1;
          const hy = lum.y + Math.sin(ang) * rad + Math.cos(t * 4.7 + seed) * 1.1;
          const op = Math.sin(u * Math.PI) * 0.88;
          engine.spawnParticle('hplus', hx, hy, 0.85, 0, op);
        }
      }
    },

    /**
     * Full 60-second seamless "Circle of Life" loop for Gallery Mode (§5)
     * tLoop is in [0, 60).
     */
    render(tLoop, engine) {
      this.renderBackgroundLife(tLoop, engine);

      // 1. Red Route: a bacterium dot every 12s (5 cycles in 60s) travels capture -> phagolysosome, warming in colour
      const redPeriod = 12.0;
      for (let k = 0; k < 2; k++) {
        const u = ((tLoop + k * (redPeriod * 0.5)) % redPeriod) / redPeriod;
        const pt = engine.pointOnPath('red_route', u);
        // Colour warms: olive (#8C9A3A) -> orange (#E8892D) -> crimson (#C23B2A) -> violet (#7A3FB5)
        const col = u < 0.33 ? '#D9722B' : u < 0.66 ? '#C23B2A' : '#7A3FB5';
        engine.watercolourBloom({
          cx: pt.x,
          cy: pt.y,
          r: 8.5 - u * 2.0,
          color: col,
          opacity: Math.sin(u * Math.PI) * 0.85
        });
      }

      // 2. Blue Route: an enzyme dot every 9s descends ER -> lysosome -> phagolysosome
      // (Use 10s divisor of 60s or 9s continuous with smooth fade at ends for seamless 60s export)
      const bluePeriod = 10.0; // 6 exact cycles in 60s (~9-10s)
      for (let k = 0; k < 2; k++) {
        const u = ((tLoop + k * 5.0) % bluePeriod) / bluePeriod;
        const pt = engine.pointOnPath('blue_route', u);
        engine.watercolourBloom({
          cx: pt.x,
          cy: pt.y,
          r: 6.5,
          color: '#1F58C8',
          opacity: Math.sin(u * Math.PI) * 0.88
        });
      }

      // 3. M6PR Recycling Carrier: round trip every 15s (4 exact cycles in 60s) between LE and TGN
      const m6prPeriod = 15.0;
      const m6prPhase = (tLoop % m6prPeriod) / m6prPeriod;
      const m6prU = m6prPhase < 0.5 ? (m6prPhase * 2) : (2 - m6prPhase * 2);
      const m6prPt = engine.pointOnPath('m6pr_loop', engine.Ease.sineInOut(m6prU));
      engine.spawnParticle('amino', m6prPt.x, m6prPt.y, 1.35, 0, 0.9);

      // 4. Violet Bloom at the V (622, 665) each time the routes converge
      const vPulse = Math.pow(0.5 + 0.5 * Math.sin((2 * Math.PI * tLoop) / 10.0), 3);
      if (vPulse > 0.15) {
        engine.watercolourBloom({
          cx: 622,
          cy: 665,
          r: 36 + vPulse * 28,
          color: '#7A3FB5',
          opacity: vPulse * 0.52
        });
      }

      // 5. Amino-Acid Recycling Dot rising from Phagolysosome to ER every 20s (3 exact cycles in 60s), closing the loop!
      const recyPeriod = 20.0;
      const recyU = (tLoop % recyPeriod) / recyPeriod;
      const recyPt = engine.pointOnPath('amino_recycle', engine.Ease.sineInOut(recyU));
      const recyOp = Math.sin(recyU * Math.PI);
      engine.spawnParticle('amino', recyPt.x, recyPt.y, 1.65, 0, recyOp);
      engine.watercolourBloom({
        cx: recyPt.x,
        cy: recyPt.y,
        r: 7.5,
        color: '#1E9B6B',
        opacity: recyOp * 0.55
      });

      // 6. pH Ribbon Shimmer along the maturation curve (309,667 -> 536,744)
      const shimU = (tLoop % 6.0) / 6.0;
      const shimX = engine.Ease.lerp(309, 536, shimU);
      const shimY = engine.Ease.lerp(667, 744, Math.pow(shimU, 0.7));
      engine.spawnParticle('glint', shimX, shimY, 0.9, tLoop * 40, Math.sin(shimU * Math.PI) * 0.75);

      // 7. NF-kB Signal Pulse every 15s (~14s) from TLR4/MyD88 to Nucleus
      const nfPeriod = 15.0;
      const nfSub = (tLoop % nfPeriod);
      if (nfSub < 4.5) {
        const nfU = nfSub / 4.5;
        engine.pulseSignal('nfkb_signal', nfU, '#C81D63', 3.4);
        if (nfU > 0.75) {
          // Soft warm glow on the nucleus
          engine.watercolourBloom({
            cx: 440,
            cy: 255,
            r: 68,
            color: '#B66EE8',
            opacity: Math.sin(((nfU - 0.75) / 0.25) * Math.PI) * 0.35
          });
        }
      }

      // 8. Right Air Silica Glints sinking slowly + Asbestos Cup breathing but never closing
      for (let i = 0; i < RIGHT_AIR_SILICA.length; i++) {
        const s = RIGHT_AIR_SILICA[i];
        const dy = Math.sin((2 * Math.PI * tLoop) / 5.0 + s.phase) * s.amp;
        const glintOp = 0.3 + 0.65 * Math.pow(0.5 + 0.5 * Math.sin(tLoop * 2.4 + s.phase), 2);
        engine.spawnParticle('glint', s.x, s.y + dy, 0.85, tLoop * 35 + i * 30, glintOp);
      }

      // Asbestos hood breathes gently (states 0 <-> 0.65) with the 5s breath cycle, never closing
      const hoodBreath = 0.32 + 0.32 * Math.sin((2 * Math.PI * tLoop) / 5.0);
      engine.stateCrossFade('particles.asbestos_hood', hoodBreath);
    }
  };

  window.LivingAmbient = Ambient;
})();
