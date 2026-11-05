/**
 * s3_biogenesis.js — Section 3 · Lysosome Biogenesis: "The Enzyme Gets Its Postcode" (Urtzi, ★4, ~100 s)
 * Beats 3a..3j:
 *  3a: Rough ER (EM flash): mRNA slides through ribosome, nascent chain threads through Sec61, folds with BiP
 *  3b: N-glycan tree grows onto enzyme; three glucose dots pop off one by one (glucose trimming)
 *  3c: ER -> cis-Golgi: COPII coat gathers, buds, hops the gap (907, 222), uncoats and fuses
 *  3d: cis-Golgi: GlcNAc-phosphotransferase docks on Lys patch, adds GlcNAc-P (yellow-gold glint)
 *  3e: ★4 Margin doodle: pencil sketch of envelope addressed "→ lysosome" with M6P stamp pressed on it; smudges away
 *  3f: TGN: uncovering enzyme clips GlcNAc; M6P is exposed (glows gold like the stamp)
 *  3g: TGN bud: pencil doodle "sorting office" (2s); M6PR grabs M6P IN THE LUMEN; clathrin + AP-1/GGA gather on cytosolic face; bud pinches off
 *  3h: Late endosome: V-ATPase rotor spins, H+ pour in, violet watercolour bloom; M6P releases from M6PR; phosphatase cancels stamp
 *  3i: Empty M6PR rides green dashed carrier back to TGN ("the postman goes home")
 *  3j: Lysosome: LAMP glints, active hydrolase brightens, two lysosomes set off down blue route; stopwatch "≈ 1 h"
 */
(function () {
  'use strict';

  const Scene3 = {
    id: 's3_biogenesis',
    order: 3,
    sectionNum: '3',
    title: '3 · Lysosome biogenesis',
    speaker: 'Urtzi',
    color: '#1F58C8',

    beats: [
      {
        id: '3a',
        label: 'Rough ER · Ribosome, Sec61 Translocation & BiP Folding',
        duration: 10,
        em: true,
        speakerChipText: '3 · Lysosome biogenesis — Urtzi',
        camFrom: [560, 120, 440, 350],
        camTo: [740, 118, 250, 115]
      },
      {
        id: '3b',
        label: 'Rough ER · N-Glycan Addition & Three-Glucose Trimming',
        duration: 10,
        camFrom: [740, 118, 250, 115],
        camTo: [730, 118, 265, 122]
      },
      {
        id: '3c',
        label: 'ER → cis-Golgi · COPII Vesicle Buds, Hops Gap & Uncoats',
        duration: 10,
        camFrom: [730, 118, 265, 122],
        camTo: [765, 155, 220, 135]
      },
      {
        id: '3d',
        label: 'cis-Golgi · Lys Patch Recognition & GlcNAc-P Addition',
        duration: 10,
        camFrom: [765, 155, 220, 135],
        camTo: [715, 185, 250, 135]
      },
      {
        id: '3e',
        label: '★4 Margin Doodle · "The Enzyme Gets Its M6P Postcode"',
        duration: 10,
        camFrom: [715, 185, 250, 135],
        camTo: [700, 190, 270, 155]
      },
      {
        id: '3f',
        label: 'TGN · Uncovering Enzyme Clips GlcNAc → M6P Exposed',
        duration: 10,
        camFrom: [700, 190, 270, 155],
        camTo: [725, 232, 245, 135]
      },
      {
        id: '3g',
        label: '★4 Sorting Office · Luminal M6PR + Cytosolic Clathrin Bud',
        duration: 10,
        camFrom: [725, 232, 245, 135],
        camTo: [695, 248, 245, 138]
      },
      {
        id: '3h',
        label: 'Late Endosome · V-ATPase Acidification, M6P Release & Phosphatase',
        duration: 10,
        camFrom: [695, 248, 245, 138],
        camTo: [615, 315, 245, 135]
      },
      {
        id: '3i',
        label: 'M6PR Recycling · "The Postman Goes Home" to TGN',
        duration: 10,
        camFrom: [615, 315, 245, 135],
        camTo: [645, 295, 255, 145]
      },
      {
        id: '3j',
        label: 'Lysosome · LAMP Glycocalyx & Blue Route Departure (≈ 1 h)',
        duration: 10,
        camFrom: [645, 295, 255, 145],
        camTo: [555, 375, 330, 230]
      }
    ],

    init(engine) {
      this.engine = engine;
      this.bioGrp = engine.createSvgEl('g', { id: 's3-biogenesis-overlay' });
      engine.dom.layerCell.appendChild(this.bioGrp);
    },

    renderBeat(beat, u, localSec, globalT, engine) {
      const E = engine.Ease;
      this.bioGrp.innerHTML = '';
      engine.dom.layerDoodles.innerHTML = '';

      if (beat.id === '3a') {
        // Rough ER: mRNA slides through ribosome (880, 148), chain threads through Sec61 into ER lumen and folds with BiP
        const slideU = E.smoother(E.sub(localSec, 0.3, 6.5));
        const foldU = E.membraneSpring(E.sub(localSec, 3.2, 8.2));
        const mrnaShift = E.lerp(-14, 10, slideU);

        const g = engine.createSvgEl('g');
        g.innerHTML = `
          <!-- Sliding purple mRNA strand above ribosome -->
          <path d="M${(855 + mrnaShift).toFixed(1)},141 Q${(875 + mrnaShift).toFixed(1)},137 ${(898 + mrnaShift).toFixed(1)},141"
                fill="none" stroke="#7A4C8A" stroke-width="1.4" stroke-dasharray="3 1.5"/>
          <!-- Nascent cobalt polypeptide threading through Sec61 channel into ER lumen -->
          <path d="M880,148 Q882,162 895,169 Q906,174 916,174"
                fill="none" stroke="#1F58C8" stroke-width="1.6" stroke-dasharray="40" stroke-dashoffset="${(40 * (1 - slideU)).toFixed(1)}"/>
          <!-- Folding cobalt hydrolase inside ER lumen (never in cytosol!) -->
          <circle cx="918" cy="174" r="${(7.2 * foldU).toFixed(2)}" fill="#1F58C8" stroke="#0D2E70" stroke-width="1.0" opacity="0.9"/>
          <!-- BiP chaperone beside folding enzyme -->
          <ellipse cx="915" cy="184" rx="6.2" ry="3.0" fill="#9A8F80" stroke="#4A433B" stroke-width="0.7" opacity="${E.smooth(slideU).toFixed(2)}"/>
        `;
        this.bioGrp.appendChild(g);

        engine.lightLabels(['mRNA', 'ribosome', 'Sec61', 'BiP', '3.1 Rough ER'], E.smooth(E.sub(localSec, 0.5, 2.5)));
      } else if (beat.id === '3b') {
        // N-glycan tree grows onto enzyme; three white glucose dots pop off one by one
        const growU = E.smoother(E.sub(localSec, 0.4, 3.8));
        const pop1 = E.sub(localSec, 4.0, 5.8);
        const pop2 = E.sub(localSec, 5.4, 7.2);
        const pop3 = E.sub(localSec, 6.8, 8.6);

        const g = engine.createSvgEl('g');
        // Branched N-glycan tree at (925, 172)
        if (growU > 0.01) {
          g.innerHTML = `
            <g transform="translate(925 172) scale(${growU.toFixed(2)})">
              <line x1="0" y1="0" x2="14" y2="-4" stroke="#1E3B6E" stroke-width="0.9"/>
              <line x1="6" y1="-2" x2="13" y2="4" stroke="#1E3B6E" stroke-width="0.9"/>
              <rect x="2" y="-2" width="2.6" height="2.6" fill="#22407E"/>
              <circle cx="9" cy="-3" r="1.4" fill="#9DC0F2" stroke="#1E3B6E" stroke-width="0.35"/>
              <circle cx="13" cy="-4.5" r="1.4" fill="#9DC0F2" stroke="#1E3B6E" stroke-width="0.35"/>
              <circle cx="12" cy="3.5" r="1.4" fill="#9DC0F2" stroke="#1E3B6E" stroke-width="0.35"/>
            </g>
          `;
        }
        // Three glucose dots popping off one by one
        [
          { u: pop1, x0: 940, y0: 166, dx: 7, dy: -6 },
          { u: pop2, x0: 943, y0: 165, dx: 11, dy: -2 },
          { u: pop3, x0: 946, y0: 164, dx: 14, dy: -7 }
        ].forEach((glc) => {
          const gx = glc.x0 + glc.dx * E.cubicOut(glc.u);
          const gy = glc.y0 + glc.dy * E.cubicOut(glc.u);
          const op = 1 - glc.u * 0.75;
          g.appendChild(engine.createSvgEl('circle', {
            cx: gx.toFixed(1), cy: gy.toFixed(1), r: '1.6',
            fill: '#F4F1EA', stroke: '#6E6A60', 'stroke-width': '0.45', opacity: op.toFixed(2)
          }));
        });
        this.bioGrp.appendChild(g);

        engine.lightLabels(['glucose trimming', 'glycan key', 'acid hydrolase'], E.smooth(E.sub(localSec, 0.5, 2.5)));
      } else if (beat.id === '3c') {
        // ER -> cis-Golgi: COPII coat gathers, buds, hops the gap along copii_hop (914,205 -> 907,222 -> 890,238), uncoats
        const hopU = E.smoother(E.sub(localSec, 1.2, 7.8));
        const coatOp = Math.sin(E.clamp(hopU * 1.15, 0, 1) * Math.PI);
        const pt = engine.pointOnPath('copii_hop', hopU);

        engine.dashDraw('copii_hop', hopU, 0.85);
        const vGrp = engine.createSvgEl('g', {
          transform: `translate(${pt.x.toFixed(1)} ${pt.y.toFixed(1)})`
        });
        vGrp.innerHTML = `
          <!-- Enclosed vesicle membrane (hydrolase stays strictly inside the lumen!) -->
          <circle cx="0" cy="0" r="6.4" fill="#D3E3F8" stroke="#3D6AAE" stroke-width="1.6"/>
          <!-- Cobalt hydrolase cargo inside lumen -->
          <circle cx="-0.8" cy="0.5" r="2.6" fill="#1F58C8" stroke="#0D2E70" stroke-width="0.5"/>
          <!-- Amber COPII coat cages on cytosolic face (gathers on bud, sheds before fusion) -->
          <circle cx="0" cy="0" r="8.4" fill="none" stroke="#D98E00" stroke-width="2.0"
                  stroke-dasharray="2.4 1.6" opacity="${coatOp.toFixed(2)}"/>
        `;
        this.bioGrp.appendChild(vGrp);

        engine.lightLabels(['COPII vesicle'], E.smooth(E.sub(localSec, 0.5, 2.5)));
      } else if (beat.id === '3d') {
        // cis-Golgi: GlcNAc-phosphotransferase docks on Lys patch (+), adds GlcNAc-P (yellow-gold glint)
        const dockU = E.smoother(E.sub(localSec, 0.6, 4.0));
        const glintU = E.sub(localSec, 3.8, 8.8);

        const g = engine.createSvgEl('g');
        // Phosphotransferase docking bridge & Lys patch (+) glow at (838, 236)
        g.innerHTML = `
          <circle cx="838" cy="236" r="${(8 * dockU).toFixed(1)}" fill="url(#halo-warm-grad)" opacity="0.85"/>
          <circle cx="852" cy="242" r="${(3.2 * E.membraneSpring(glintU)).toFixed(2)}" fill="#E2B33C" stroke="#7A5A00" stroke-width="0.6"/>
          <rect x="855" y="240" width="3.4" height="3.4" fill="#22407E" stroke="#0F2350" stroke-width="0.4" opacity="${E.smooth(glintU).toFixed(2)}"/>
        `;
        this.bioGrp.appendChild(g);

        if (glintU > 0.1) {
          engine.spawnParticle('glint', 852, 242, 1.45, globalT * 70, 0.95);
        }
        engine.lightLabels(['3.2 cis-Golgi', 'Lys patch', 'GlcNAc-phosphotransferase', 'GlcNAc-P'], E.smooth(E.sub(localSec, 0.5, 2.5)));
      } else if (beat.id === '3e') {
        // ★4 Margin Doodle: Pencil sketch over the Golgi stack of an envelope addressed "→ lysosome"
        // with a stamp pressed on it labelled M6P. Holds 3s, then dissolves like graphite smudged away!
        const drawIn = E.smooth(E.sub(localSec, 0.3, 2.5));
        const stampPress = E.membraneSpring(E.sub(localSec, 2.2, 3.8));
        const smudgeOut = 1 - E.smoother(E.sub(localSec, 7.0, 9.6));
        const op = drawIn * smudgeOut;

        if (drawIn > 0.05 && localSec < 3.5 && window.LivingDevices) {
          window.LivingDevices.playPenScratch();
        }

        if (op > 0.01) {
          const smudgeBlur = (1 - smudgeOut) * 6;
          const doodle = engine.createSvgEl('g', {
            opacity: op.toFixed(3),
            transform: `translate(${(1 - smudgeOut) * 8} 0)`
          });
          if (smudgeBlur > 0.2) doodle.style.filter = `blur(${smudgeBlur.toFixed(1)}px)`;

          doodle.innerHTML = `
            <!-- Sketchy graphite card inside Golgi lumen area (enclosed!) -->
            <rect x="758" y="224" width="128" height="72" rx="4" fill="#FAF6EE" fill-opacity="0.93"
                  stroke="#2B3040" stroke-width="1.2" stroke-dasharray="3.5 1.5"/>
            <!-- Envelope flap & diagonal seams -->
            <path d="M758,224 L822,262 L886,224 M758,296 L798,256 M886,296 L846,256"
                  fill="none" stroke="#2B3040" stroke-width="0.95" opacity="0.75"/>
            <!-- Handwritten address: "→ lysosome" -->
            <text x="808" y="280" font-family="Gabriola, 'Segoe Print', serif" font-size="16" font-weight="600"
                  fill="#2B3040" text-anchor="middle">→ lysosome</text>
            <!-- M6P Postcode Stamp pressed in top-right corner of envelope -->
            <g transform="translate(864 242) scale(${stampPress.toFixed(3)})">
              <rect x="-15" y="-11" width="30" height="22" rx="1.5" fill="#FFF3C4" stroke="#B8860B" stroke-width="1.2" stroke-dasharray="2 1"/>
              <circle cx="0" cy="0" r="7.5" fill="#E2B33C" stroke="#7A5A00" stroke-width="0.8"/>
              <text x="0" y="3.2" font-family="'Segoe UI Variable Text', sans-serif" font-size="7.5" font-weight="700"
                    fill="#3B2D00" text-anchor="middle">M6P</text>
              <!-- Wavy postmark cancellation lines -->
              <path d="M-24,-3 Q-19,-6 -14,-3 M-24,3 Q-19,0 -14,3" fill="none" stroke="#2B3040" stroke-width="0.7"/>
            </g>
            <text x="822" y="218" font-family="Gabriola, 'Segoe Print', serif" font-size="11.5"
                  fill="#2B3040" text-anchor="middle" stroke="#FAF6EE" stroke-width="2" paint-order="stroke">
              pencil doodle · the enzyme gets its postcode
            </text>
          `;
          engine.dom.layerDoodles.appendChild(doodle);
        }
      } else if (beat.id === '3f') {
        // TGN: uncovering enzyme clips GlcNAc; M6P is exposed and glows the exact same yellow-gold as in the doodle!
        const clipU = E.smoother(E.sub(localSec, 0.8, 5.2));
        const m6pGlow = E.sub(localSec, 2.0, 9.0);

        // Clipped blue GlcNAc square drifting away in TGN lumen (872, 294)
        const sqX = 864 + clipU * 14;
        const sqY = 292 + clipU * 8;
        const g = engine.createSvgEl('g');
        g.innerHTML = `
          <!-- Exposed M6P gold stamp glowing on the hydrolase at (855, 296) -->
          <circle cx="855" cy="296" r="${(10 * E.smooth(m6pGlow)).toFixed(1)}" fill="url(#halo-warm-grad)" opacity="0.95"/>
          <circle cx="855" cy="296" r="3.4" fill="#E2B33C" stroke="#7A5A00" stroke-width="0.7"/>
          <text x="855" y="297.8" font-family="'Segoe UI Variable Text', sans-serif" font-size="4.2" font-weight="700"
                fill="#3B2D00" text-anchor="middle">P</text>
          <!-- Clipped GlcNAc square drifting off -->
          <rect x="${sqX.toFixed(1)}" y="${sqY.toFixed(1)}" width="3.2" height="3.2"
                fill="#22407E" stroke="#0F2350" stroke-width="0.4" opacity="${(1 - clipU * 0.6).toFixed(2)}"/>
        `;
        this.bioGrp.appendChild(g);
        engine.spawnParticle('glint', 855, 296, 1.4, globalT * 60, 0.9);
        engine.lightLabels(['uncovering enzyme', 'M6P', '3.3 TGN'], E.smooth(E.sub(localSec, 0.5, 2.5)));
      } else if (beat.id === '3g') {
        // TGN bud: Doodle comes back for 2s ("sorting office" / "postman" / "mail bag");
        // M6PR grabs M6P IN THE LUMEN; Clathrin triskelia + AP-1/GGA gather on CYTOSOLIC face; bud pinches off!
        const doodleOp = Math.sin(E.sub(localSec, 0.2, 3.2) * Math.PI);
        if (doodleOp > 0.02) {
          const dGrp = engine.createSvgEl('g', { opacity: doodleOp.toFixed(2) });
          dGrp.innerHTML = `
            <rect x="782" y="262" width="76" height="16" rx="4" fill="#FAF6EE" stroke="#2B3040" stroke-width="0.8" stroke-dasharray="2 1"/>
            <text x="820" y="273.5" font-family="Gabriola, 'Segoe Print', serif" font-size="11.5" fill="#2B3040" text-anchor="middle">sorting office (TGN)</text>
            <text x="836" y="318" font-family="Gabriola, 'Segoe Print', serif" font-size="10.5" fill="#1E8A5A" stroke="#FAF6EE" stroke-width="1.8" paint-order="stroke">postman (M6PR)</text>
            <text x="768" y="292" font-family="Gabriola, 'Segoe Print', serif" font-size="10.5" fill="#4A5566" text-anchor="end" stroke="#FAF6EE" stroke-width="1.8" paint-order="stroke">mail bag (clathrin)</text>
          `;
          engine.dom.layerDoodles.appendChild(dGrp);
        }

        // Clathrin triskelia net closing on cytosolic face & vesicle pinching along clathrin_path
        const gatherU = E.smoother(E.sub(localSec, 1.8, 5.5));
        const pinchU = E.smoother(E.sub(localSec, 5.0, 9.2));
        const budPt = engine.pointOnPath('clathrin_path', pinchU);

        const bGrp = engine.createSvgEl('g', {
          transform: `translate(${budPt.x.toFixed(1)} ${budPt.y.toFixed(1)})`
        });
        bGrp.innerHTML = `
          <!-- Enclosed TGN bud/vesicle membrane -->
          <circle cx="0" cy="0" r="6.8" fill="#BEDDEE" stroke="#1F5A7E" stroke-width="1.6"/>
          <!-- Luminal M6PR (green Y) holding M6P-hydrolase (blue+gold) STRICTLY INSIDE LUMEN (§9) -->
          <path d="M2.5,4.5 L0.8,1.5 M0.8,1.5 L-1.2,1.2 M0.8,1.5 L1.2,-0.8" fill="none" stroke="#1E8A5A" stroke-width="1.2" stroke-linecap="round"/>
          <circle cx="-1.2" cy="-1.0" r="2.6" fill="#1F58C8" stroke="#0D2E70" stroke-width="0.5"/>
          <circle cx="0.6" cy="0.4" r="1.2" fill="#E2B33C"/>
          <!-- Cytosolic AP-1/GGA adaptors & Clathrin lattice coat OUTSIDE membrane -->
          <circle cx="0" cy="0" r="9.2" fill="none" stroke="#6B7C93" stroke-width="2.1"
                  stroke-dasharray="${(3.2 * gatherU).toFixed(1)} ${(2.4 - gatherU * 1.1).toFixed(1)}" opacity="${gatherU.toFixed(2)}"/>
        `;
        this.bioGrp.appendChild(bGrp);
        engine.dashDraw('clathrin_path', pinchU, 0.85);
        engine.lightLabels(['M6PR', 'clathrin', 'AP-1 · GGA', '3.4 Clathrin bud'], E.smooth(E.sub(localSec, 0.8, 3.0)));
      } else if (beat.id === '3h') {
        // Late endosome (718, 374): V-ATPase rotor spins, H+ pour in, violet watercolour bloom;
        // M6P lets go of M6PR; phosphatase strips the phosphate (stamp cancelled!)
        const acidU = E.smoother(E.sub(localSec, 0.4, 5.0));
        const relU = E.smoother(E.sub(localSec, 3.5, 8.5));

        // Violet watercolour bloom inside Late Endosome lumen (718, 374)
        engine.watercolourBloom({
          cx: 718,
          cy: 374,
          r: 28,
          color: '#A8406E',
          opacity: acidU * 0.48
        });

        // V-ATPase mechanical rotor spin at (692, 362) & H+ pouring in
        const spinDeg = (globalT * 180) % 360;
        const g = engine.createSvgEl('g');
        g.innerHTML = `
          <!-- Spinning V-ATPase rotor indicator -->
          <g transform="translate(690 362) rotate(${spinDeg.toFixed(1)})">
            <circle cx="0" cy="0" r="4.2" fill="#E75A8B" stroke="#7A1842" stroke-width="0.7"/>
            <path d="M-4.2,0 H4.2 M0,-4.2 V4.2" stroke="#FFFFFF" stroke-width="0.9"/>
          </g>
          <!-- Released hydrolase drifting away from luminal M6PR; Pi cleaved by phosphatase -->
          <circle cx="${(724 - relU * 5).toFixed(1)}" cy="${(366 + relU * 10).toFixed(1)}" r="4.2"
                  fill="#1F58C8" stroke="#0D2E70" stroke-width="0.7"/>
          <circle cx="${(728 + relU * 8).toFixed(1)}" cy="${(372 + relU * 12).toFixed(1)}" r="1.8"
                  fill="#E2B33C" stroke="#7A5A00" stroke-width="0.4" opacity="${(1 - relU * 0.5).toFixed(2)}"/>
        `;
        this.bioGrp.appendChild(g);

        engine.lightLabels(['3.5 Late endosome', 'V-ATPase', 'M6P released', 'phosphatase'], E.smooth(E.sub(localSec, 0.5, 2.5)));
      } else if (beat.id === '3i') {
        // Empty M6PR rides the green dashed recycling carrier back to the TGN ("the postman goes home")
        const recU = E.smoother(E.sub(localSec, 0.5, 8.2));
        const pt = engine.pointOnPath('m6pr_loop', recU);

        engine.dashDraw('m6pr_loop', recU, 0.92);
        const cGrp = engine.createSvgEl('g', {
          transform: `translate(${pt.x.toFixed(1)} ${pt.y.toFixed(1)})`
        });
        cGrp.innerHTML = `
          <circle cx="0" cy="0" r="5.5" fill="#DDEFE5" stroke="#1E8A5A" stroke-width="1.5"/>
          <!-- Empty Y-shaped M6PR receptors facing lumen -->
          <path d="M-2,0 L0,2 L2,0 M0,2 L0,4.2" fill="none" stroke="#1E8A5A" stroke-width="1.2" stroke-linecap="round"/>
        `;
        this.bioGrp.appendChild(cGrp);

        // Subtle pencil caption "the postman goes home"
        const noteOp = Math.sin(E.sub(localSec, 1.2, 7.8) * Math.PI);
        if (noteOp > 0.05) {
          const note = engine.createSvgEl('text', {
            x: '803', y: '372',
            'font-family': "Gabriola, 'Segoe Print', serif",
            'font-size': '11.5',
            fill: '#1E8A5A',
            'text-anchor': 'middle',
            stroke: '#FAF6EE',
            'stroke-width': '2',
            'paint-order': 'stroke',
            opacity: noteOp.toFixed(2)
          });
          note.textContent = 'empty M6PR recycles → TGN';
          engine.dom.layerDoodles.appendChild(note);
        }

        engine.lightLabels(['recycling', 'M6PR'], E.smooth(E.sub(localSec, 0.5, 2.5)));
      } else if (beat.id === '3j') {
        // Lysosome (757, 433): LAMP glints along inner membrane; active hydrolase brightens;
        // two lysosomes set off down the blue route (656,484 -> 640,560); Stopwatch "≈ 1 h"
        const lampPts = [[735, 422], [748, 416], [764, 417], [778, 424], [772, 444], [744, 446]];
        lampPts.forEach(([lx, ly], idx) => {
          const s = 0.7 + 0.6 * Math.sin(globalT * 4.5 + idx);
          engine.spawnParticle('glint', lx, ly, s, globalT * 50, 0.9);
        });

        // Active hydrolase glow at (762, 434)
        engine.watercolourBloom({ cx: 762, cy: 434, r: 16, color: '#1F58C8', opacity: 0.65 });

        // Two lysosomes travelling down the lower blue route toward Zone E
        const travelU = E.smoother(E.sub(localSec, 1.5, 8.8));
        const p1 = engine.pointOnPolyline([[725, 448], [662, 492], [646, 535]], travelU);
        const p2 = engine.pointOnPolyline([[662, 492], [646, 535], [635, 565]], travelU);

        [p1, p2].forEach((p) => {
          this.bioGrp.appendChild(engine.createSvgEl('circle', {
            cx: p.x.toFixed(1), cy: p.y.toFixed(1), r: '7.5',
            fill: '#E8DAF6', stroke: '#6F36A8', 'stroke-width': '1.8'
          }));
          this.bioGrp.appendChild(engine.createSvgEl('circle', {
            cx: p.x.toFixed(1), cy: p.y.toFixed(1), r: '2.4',
            fill: '#1F58C8'
          }));
        });

        engine.dashDraw('blue_route', 0.65 + 0.35 * travelU, 0.85);
        engine.lightLabels(['3.6 Lysosome', 'LAMP', 'active hydrolase'], E.smooth(E.sub(localSec, 0.5, 2.5)));

        if (window.LivingDevices) {
          window.LivingDevices.showStopwatch('≈ 1 h', 'ER → lysosome biogenesis', 1.4);
          window.LivingDevices.showSizeTag({
            text: 'lysosome ≈ 0.5 µm',
            targetX: 757,
            targetY: 433,
            tagX: 798,
            tagY: 405,
            color: '#5A2A8C'
          });
        }
      }
    }
  };

  window.LivingEngine.registerScene(Scene3);
})();
