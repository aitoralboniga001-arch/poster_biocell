/**
 * engine.js — The Living Poster Deterministic Animation Engine
 * Pure function of time render(t), camera controller, 2.5D parallax,
 * zoom objective thresholds (4x · 10x · 40x · 100x oil · EM), focus pull,
 * actor state cross-fader, vector path drawer, label lighter, and pooled particles.
 * Zero external libraries. Works offline on file:///.
 */
(function () {
  'use strict';

  const SVG_NS = 'http://www.w3.org/2000/svg';

  // ============================================================================
  // 1. Easing & Math Utilities (Organic cinemagraph eases, nothing faster than 0.25s)
  // ============================================================================
  const Ease = {
    clamp(v, a = 0, b = 1) {
      return Math.max(a, Math.min(b, v));
    },
    remap(v, in0, in1, out0 = 0, out1 = 1) {
      if (Math.abs(in1 - in0) < 1e-9) return out1;
      const u = Math.max(0, Math.min(1, (v - in0) / (in1 - in0)));
      return out0 + (out1 - out0) * u;
    },
    sub(t, t0, t1) {
      if (t1 <= t0) return t >= t1 ? 1 : 0;
      return Math.max(0, Math.min(1, (t - t0) / (t1 - t0)));
    },
    smooth(t) {
      const u = Math.max(0, Math.min(1, t));
      return u * u * (3 - 2 * u);
    },
    smoother(t) {
      const u = Math.max(0, Math.min(1, t));
      return u * u * u * (u * (u * 6 - 15) + 10);
    },
    sineInOut(t) {
      const u = Math.max(0, Math.min(1, t));
      return 0.5 * (1 - Math.cos(Math.PI * u));
    },
    cubicOut(t) {
      const u = Math.max(0, Math.min(1, t));
      return 1 - Math.pow(1 - u, 3);
    },
    cubicInOut(t) {
      const u = Math.max(0, Math.min(1, t));
      return u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
    },
    membraneSpring(t) {
      // Slight organic overshoot only for membrane spring-back (§2.3)
      const u = Math.max(0, Math.min(1, t));
      const c1 = 1.15;
      const c3 = c1 + 1;
      return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2);
    },
    bell(t) {
      const u = Math.max(0, Math.min(1, t));
      return Math.sin(Math.PI * u);
    },
    lerp(a, b, t) {
      return a + (b - a) * t;
    },
    lerpBox(b0, b1, t) {
      const e = Ease.smoother(t);
      return [
        b0[0] + (b1[0] - b0[0]) * e,
        b0[1] + (b1[1] - b0[1]) * e,
        b0[2] + (b1[2] - b0[2]) * e,
        b0[3] + (b1[3] - b0[3]) * e
      ];
    },
    hash(n) {
      const x = Math.sin(n * 127.1 + 311.7) * 43758.5453123;
      return x - Math.floor(x);
    }
  };

  // ============================================================================
  // 2. Default Manifest (Exact V2 Poster Geometry in mm, 1100 x 900)
  // ============================================================================
  const DEFAULT_MANIFEST = {
    posterSize: [1100, 900],
    deskViewBox: [-80, -55, 1260, 1010],
    overviewViewBox: [-38, -22, 1176, 944],
    plate: 'assets/plate_100dpi.webp',
    fallbackPlates: [
      'assets/plate_100dpi.webp',
      'assets/plate.webp',
      'assets/Preview_full_poster.png',
      'assets/poster_fallback.jpg',
      '../deliverables_v2/Macrophage_poster_150dpi.jpg',
      '../animated/poster_bg.jpg'
    ],
    zones: {
      locator:   { rect: [22, 108, 193, 132], dpi300: 'assets/zone_locator_300.webp' },
      zoneA:     { rect: [22, 250, 313, 280], dpi300: 'assets/zone_A_300.webp', fallback: 'assets/Readable_recognition.png', em600: 'assets/em_receptors_600.webp' },
      zoneB:     { rect: [220, 510, 310, 230], dpi300: 'assets/zone_B_300.webp' },
      zoneC:     { rect: [315, 150, 250, 210], dpi300: 'assets/zone_C_300.webp' },
      zoneD:     { rect: [560, 130, 430, 340], dpi300: 'assets/zone_D_300.webp', fallback: 'assets/Readable_enzyme_route.png' },
      zoneE:     { rect: [420, 550, 300, 210], dpi300: 'assets/zone_E_300.webp', fallback: 'assets/Readable_fusion_killing.png', em600: 'assets/em_snares_600.webp' },
      zoneF:     { rect: [760, 478, 255, 240], dpi300: 'assets/zone_F_300.webp', fallback: 'assets/Readable_particles.png', em600: 'assets/em_nlrp3_600.webp' },
      zoneG:     { rect: [880, 700, 235, 90],  dpi300: 'assets/zone_G_300.webp' },
      wall:      { rect: [0, 735, 1100, 130],  dpi300: 'assets/zone_wall_300.webp', fallback: 'assets/Readable_lung_wall.png' }
    },
    paths: {
      cell_outline: [
        [318,236],[340,178],[376,141],[430,113],[490,114],[558,140],[624,159],[684,155],
        [742,132],[818,114],[890,116],[956,131],[997,166],[999,212],[977,258],[958,326],
        [938,388],[909,456],[941,502],[990,517],[1003,540],[1007,590],[1006,640],[1001,690],
        [994,731],[1007,739.3],[952,741],[893,743],[891,750.6],[948,752.9],[973,754.6],
        [900,757],[750,759],[560,760],[380,760],[232,769],[184,755],[174,716],[202,664],
        [218,604],[178,556],[142,532],[90,524],[48,505],[31,482],[38,484],[72,499],
        [114,509],[145.5,503],[150,494],[142,454],[138,392],[142,330],[150,290],[135,278],
        [92,279],[54,292],[31,302],[48,279],[90,260],[142,252],[166,258],[224,264],
        [280,274],[312,256],[318,236]
      ],
      red_route: [
        [60, 392], [120, 392], [230, 470], [295, 575], [372, 648], [470, 680], [622, 665]
      ],
      blue_route: [
        [885, 172], [842, 236], [795, 304], [718, 374], [757, 433], [656, 495], [640, 560], [622, 665]
      ],
      copii_hop: [
        [914, 205], [907, 222], [890, 238]
      ],
      clathrin_path: [
        [812, 306], [770, 326], [732, 352]
      ],
      m6pr_loop: [
        [744, 362], [775, 355], [803, 352], [828, 344], [849, 336]
      ],
      amino_recycle: [
        [652, 722], [685, 650], [720, 540], [785, 395], [845, 260], [888, 168]
      ],
      nfkb_signal: [
        [152, 325], [176, 319], [235, 298], [305, 275], [355, 260]
      ],
      src_syk_pi3k: [
        [152, 411], [158, 418], [166, 426], [154, 436]
      ],
      cdc42_wasp_arp: [
        [154, 436], [148, 449], [159, 449.5], [168, 468]
      ],
      rac_wave_arp: [
        [154, 436], [148, 460], [159, 460.5], [168, 468]
      ],
      signal1_priming: [
        [996, 560], [975, 564], [966, 590], [946, 608]
      ],
      signal2_cathepsin: [
        [892, 578], [912, 595], [938, 614]
      ],
      signal2_kplus: [
        [1005, 604], [976, 606], [950, 614]
      ],
      signal2_ros: [
        [906, 550], [925, 580], [940, 610]
      ],
      caspase_il1b: [
        [918, 655], [955, 662], [991, 650], [1032, 658]
      ],
      pyroptosis_path: [
        [1045, 650], [1080, 622], [1082, 579], [1052, 544], [994, 512]
      ],
      wall_il1b_tnfa: [
        [1050, 676], [1078, 694], [1089, 722], [1090, 748], [1088, 770]
      ],
      wall_tgfb_pdgf: [
        [852, 722], [864, 760], [870, 796]
      ],
      capillary_1: [[65, 776], [95, 776], [125, 776]],
      capillary_2: [[235, 773], [265, 773], [295, 773]],
      capillary_3: [[410, 769], [442, 769], [472, 769]],
      capillary_4: [[652, 776], [668, 776], [684, 776]],
      capillary_5: [[828, 780], [846, 780], [864, 780]],
      lead_mem: [[150, 290], [142, 330], [138, 392], [142, 454], [150, 494]]
    },
    labels: {
      // Section 1
      '1 Alveolar macrophage': { x: 95, y: 120, w: 135, h: 18, color: '#1E2433' },
      'this scene':            { x: 193, y: 212, w: 58, h: 14, color: '#C0392B' },
      // Section 2
      '2 Recognition':         { x: 75, y: 246, w: 96, h: 18, color: '#C0392B' },
      'Bacterium':             { x: 49, y: 350, w: 58, h: 14, color: '#5A6420' },
      'LPS':                   { x: 66, y: 325, w: 26, h: 10, color: '#8E3B8F' },
      'glycans':               { x: 62, y: 370, w: 38, h: 10, color: '#3E9B57' },
      'iC3b':                  { x: 64, y: 390, w: 28, h: 10, color: '#13848C' },
      'IgG':                   { x: 66, y: 419, w: 26, h: 10, color: '#1F4E9A' },
      'peptidoglycan':         { x: 48, y: 441, w: 62, h: 10, color: '#5A6420' },
      'TLR4–MD-2':             { x: 128, y: 305, w: 54, h: 10, color: '#8E3B8F' },
      'CD14':                  { x: 190, y: 349, w: 30, h: 10, color: '#8E3B8F' },
      'MR':                    { x: 188, y: 369, w: 24, h: 10, color: '#8C583A' },
      'CR3':                   { x: 188, y: 393, w: 26, h: 10, color: '#13848C' },
      'FcγR':                  { x: 120, y: 430, w: 28, h: 10, color: '#1F4E9A' },
      '2.1':                   { x: 128, y: 382, w: 22, h: 10, color: '#C0392B' },
      'MyD88':                 { x: 162, y: 332, w: 34, h: 10, color: '#8E3B8F' },
      'NF-κB → inflammation':  { x: 245, y: 294, w: 92, h: 12, color: '#C81D63' },
      'Src':                   { x: 188, y: 412, w: 24, h: 10, color: '#3B4350' },
      'ITAM':                  { x: 168, y: 420, w: 28, h: 10, color: '#1F4E9A' },
      'Syk':                   { x: 188, y: 427, w: 24, h: 10, color: '#3B4350' },
      'PI3K':                  { x: 188, y: 437, w: 28, h: 10, color: '#3B4350' },
      'Cdc42 → WASP':          { x: 204, y: 450, w: 62, h: 10, color: '#3B4350' },
      'Rac → WAVE':            { x: 200, y: 461, w: 56, h: 10, color: '#3B4350' },
      'Arp2/3':                { x: 192, y: 472, w: 36, h: 10, color: '#B4561C' },
      'F-actin':               { x: 192, y: 482, w: 36, h: 10, color: '#E07B39' },
      '2.2 Pseudopod':         { x: 96, y: 536, w: 78, h: 14, color: '#C0392B' },
      '2.3 Nascent phagosome': { x: 242, y: 625, w: 105, h: 14, color: '#C0392B' },
      '2.4':                   { x: 330, y: 696, w: 26, h: 12, color: '#E8892D' },
      'Rab5-GTP':              { x: 356, y: 602, w: 48, h: 10, color: '#E3A21A' },
      'pH 6.5':                { x: 408, y: 722, w: 36, h: 11, color: '#E8892D' },
      '2.5':                   { x: 435, y: 730, w: 26, h: 12, color: '#C23B2A' },
      'Rab7-GTP':              { x: 450, y: 635, w: 48, h: 10, color: '#C0392B' },
      'pH 5.5':                { x: 485, y: 738, w: 36, h: 11, color: '#C23B2A' },
      // Section 3
      '3 Lysosome biogenesis': { x: 665, y: 129, w: 138, h: 18, color: '#1F58C8' },
      'glycan key':            { x: 675, y: 143, w: 140, h: 10, color: '#1F58C8' },
      '3.1 Rough ER':          { x: 910, y: 144, w: 78, h: 14, color: '#1F4E9A' },
      'mRNA':                  { x: 812, y: 138, w: 30, h: 10, color: '#6A3C7A' },
      'ribosome':              { x: 865, y: 136, w: 44, h: 10, color: '#2E3B66' },
      'Sec61':                 { x: 832, y: 154, w: 30, h: 10, color: '#4A5566' },
      'BiP':                   { x: 874, y: 185, w: 24, h: 10, color: '#4A5566' },
      'acid hydrolase':        { x: 922, y: 182, w: 62, h: 10, color: '#1F58C8' },
      'glucose trimming':      { x: 942, y: 179, w: 68, h: 10, color: '#4A5566' },
      'COPII vesicle':         { x: 882, y: 222, w: 58, h: 12, color: '#D98E00' },
      '3.2 cis-Golgi':         { x: 735, y: 228, w: 72, h: 14, color: '#1F5A7E' },
      'Lys patch':             { x: 816, y: 238, w: 44, h: 10, color: '#1F58C8' },
      'GlcNAc-phosphotransferase': { x: 805, y: 215, w: 95, h: 14, color: '#4A5566' },
      'GlcNAc-P':              { x: 864, y: 246, w: 44, h: 10, color: '#E2B33C' },
      '3.3 TGN':               { x: 912, y: 336, w: 54, h: 14, color: '#1F5A7E' },
      'uncovering enzyme':     { x: 895, y: 282, w: 68, h: 14, color: '#4A5566' },
      'M6P':                   { x: 855, y: 304, w: 28, h: 10, color: '#E2B33C' },
      'M6PR':                  { x: 818, y: 312, w: 32, h: 10, color: '#1E8A5A' },
      'clathrin':              { x: 775, y: 300, w: 42, h: 10, color: '#6B7C93' },
      'AP-1 · GGA':            { x: 772, y: 308, w: 48, h: 10, color: '#6B7C93' },
      '3.4 Clathrin bud':      { x: 760, y: 320, w: 82, h: 14, color: '#1F5A7E' },
      '3.5 Late endosome':     { x: 642, y: 378, w: 88, h: 14, color: '#8A2F5A' },
      'V-ATPase':              { x: 672, y: 386, w: 46, h: 10, color: '#E75A8B' },
      'M6P released':          { x: 762, y: 368, w: 58, h: 10, color: '#E2B33C' },
      'phosphatase':           { x: 722, y: 392, w: 54, h: 10, color: '#4A5566' },
      'recycling':             { x: 803, y: 352, w: 52, h: 12, color: '#1E9B6B' },
      '3.6 Lysosome':          { x: 825, y: 440, w: 74, h: 14, color: '#5A2A8C' },
      'LAMP':                  { x: 750, y: 406, w: 32, h: 10, color: '#8E7BB0' },
      'active hydrolase':      { x: 762, y: 448, w: 68, h: 10, color: '#1F58C8' },
      // Section 4
      '4 Fusion':              { x: 515, y: 565, w: 64, h: 16, color: '#7A3FB5' },
      'a tether':              { x: 455, y: 576, w: 44, h: 11, color: '#7A3FB5' },
      'Arl8b':                 { x: 440, y: 611, w: 32, h: 10, color: '#9B6A3C' },
      'HOPS':                  { x: 438, y: 625, w: 30, h: 10, color: '#7A3FB5' },
      'Rab7':                  { x: 436, y: 636, w: 30, h: 10, color: '#C0392B' },
      'b zipper':              { x: 495, y: 588, w: 44, h: 11, color: '#7A3FB5' },
      'syntaxin-7':            { x: 536, y: 598, w: 48, h: 9,  color: '#2E86AB' },
      'Vti1b':                 { x: 530, y: 604, w: 32, h: 9,  color: '#3FA796' },
      'syntaxin-8':            { x: 536, y: 610, w: 48, h: 9,  color: '#8BAF3A' },
      'VAMP7':                 { x: 532, y: 615, w: 36, h: 9,  color: '#E07A5F' },
      'N → C':                 { x: 530, y: 621, w: 32, h: 9,  color: '#5E5648' },
      'c pore':                { x: 548, y: 648, w: 36, h: 11, color: '#7A3FB5' },
      'd recycle':             { x: 552, y: 702, w: 46, h: 11, color: '#7A3FB5' },
      'NSF':                   { x: 550, y: 686, w: 28, h: 10, color: '#6E7787' },
      'α-SNAP':                { x: 554, y: 694, w: 38, h: 10, color: '#6E7787' },
      '2.6 Phagolysosome':     { x: 618, y: 590, w: 98, h: 15, color: '#5A2A8C' },
      '2.6':                   { x: 618, y: 590, w: 98, h: 15, color: '#5A2A8C' },
      // Section 2.7
      '2.7 Killing':           { x: 725, y: 642, w: 74, h: 16, color: '#C0392B' },
      'NOX2':                  { x: 725, y: 667, w: 34, h: 10, color: '#C81D63' },
      'gp91phox · p22phox':    { x: 752, y: 673, w: 84, h: 10, color: '#C81D63' },
      'p47 · p67 · p40phox':   { x: 752, y: 679, w: 84, h: 10, color: '#C81D63' },
      'Rac-GTP':               { x: 732, y: 684, w: 42, h: 10, color: '#8A4F6A' },
      'NADPH → NADP⁺':         { x: 748, y: 690, w: 68, h: 10, color: '#7A0C37' },
      'e⁻':                    { x: 690, y: 684, w: 18, h: 10, color: '#7A0C37' },
      'O₂ → O₂•⁻ → H₂O₂':      { x: 648, y: 690, w: 76, h: 10, color: '#7A0C37' },
      'H⁺':                    { x: 654, y: 626, w: 22, h: 10, color: '#0A6E92' },
      'pH 4.5':                { x: 552, y: 746, w: 38, h: 12, color: '#5A2A8C' },
      'lysozyme':              { x: 586, y: 643, w: 44, h: 10, color: '#1F58C8' },
      'cathepsins':            { x: 625, y: 614, w: 48, h: 10, color: '#1F58C8' },
      'lipases':               { x: 638, y: 715, w: 36, h: 10, color: '#1F58C8' },
      'nucleases':             { x: 598, y: 716, w: 44, h: 10, color: '#1F58C8' },
      'reuse':                 { x: 692, y: 726, w: 32, h: 10, color: '#1E9B6B' },
      'recycled':              { x: 688, y: 744, w: 42, h: 10, color: '#1E9B6B' },
      // Section 5
      '5 Particles':           { x: 1052, y: 132, w: 76, h: 16, color: '#B4690E' },
      '5.1 uptake':            { x: 1058, y: 324, w: 62, h: 13, color: '#B4690E' },
      '5.2 Silica phagolysosome': { x: 840, y: 502, w: 125, h: 15, color: '#5A2A8C' },
      'cathepsin B':           { x: 906, y: 617, w: 52, h: 10, color: '#1F58C8' },
      'K⁺ efflux':             { x: 1048, y: 605, w: 46, h: 10, color: '#3F4C68' },
      'ROS':                   { x: 936, y: 551, w: 26, h: 10, color: '#C81D63' },
      'signal 1 · priming':    { x: 958, y: 548, w: 72, h: 10, color: '#5B4F78' },
      'signal 2':              { x: 978, y: 599, w: 40, h: 10, color: '#6F5E66' },
      'NLRP3':                 { x: 968, y: 621, w: 34, h: 10, color: '#C81D63' },
      'ASC':                   { x: 918, y: 676, w: 48, h: 10, color: '#C81D63' },
      'inflammasome':          { x: 918, y: 682, w: 62, h: 10, color: '#C81D63' },
      'caspase-1':             { x: 955, y: 675, w: 46, h: 10, color: '#8E1D4E' },
      'IL-1β · IL-18':         { x: 1072, y: 666, w: 56, h: 10, color: '#C81D63' },
      'GSDMD':                 { x: 972, y: 693, w: 36, h: 10, color: '#6A5D7B' },
      'GSDMD pore ~20 nm':     { x: 1038, y: 692, w: 64, h: 14, color: '#4E445E' },
      'pyroptosis?':           { x: 1072, y: 644, w: 54, h: 10, color: '#5E4A56' },
      're-uptake':             { x: 1064, y: 523, w: 46, h: 10, color: '#B4690E' },
      '5.3 Asbestos':          { x: 936, y: 716, w: 72, h: 13, color: '#B4690E' },
      'open cup':              { x: 948, y: 732, w: 44, h: 10, color: '#B4690E' },
      '> 15–20 µm':            { x: 1046, y: 735, w: 54, h: 10, color: '#B4690E' },
      'ROS · enzymes':         { x: 1045, y: 767, w: 62, h: 10, color: '#B4690E' },
      'IL-1β · TNF-α':         { x: 1052, y: 711, w: 58, h: 10, color: '#C81D63' },
      '5.4 Inflammation':      { x: 1066, y: 814, w: 82, h: 13, color: '#C81D63' },
      'TGF-β · PDGF':          { x: 902, y: 783, w: 58, h: 10, color: '#B4690E' },
      '5.5 Fibrosis':          { x: 916, y: 816, w: 68, h: 13, color: '#B4690E' },
      'collagen':              { x: 822, y: 816, w: 42, h: 10, color: '#7C5F56' },
      '5.x':                   { x: 950, y: 660, w: 160, h: 140, color: '#B4690E' },
      // Section 6
      'routes':                { x: 555, y: 580, w: 160, h: 80, color: '#7A3FB5' },
      'conclusion':            { x: 420, y: 854, w: 650, h: 20, color: '#1E9B6B' },
      'title':                 { x: 380, y: 68, w: 540, h: 65, color: '#C0392B' }
    }
  };

  // Merge user/builder LIVING_MANIFEST with DEFAULT_MANIFEST
  function mergeManifest(custom) {
    if (!custom || typeof custom !== 'object') return DEFAULT_MANIFEST;
    const out = Object.assign({}, DEFAULT_MANIFEST, custom);
    out.zones = Object.assign({}, DEFAULT_MANIFEST.zones, custom.zones || {});
    out.paths = Object.assign({}, DEFAULT_MANIFEST.paths, custom.paths || {});
    out.labels = Object.assign({}, DEFAULT_MANIFEST.labels, custom.labels || {});
    out.actors = Object.assign({}, custom.actors || {});
    return out;
  }

  const MANIFEST = mergeManifest(window.LIVING_MANIFEST);
  window.LIVING_MANIFEST = MANIFEST;

  // ============================================================================
  // 3. SVG Path & Geometry Helpers
  // ============================================================================
  function pointsToPathD(pts, closed = false) {
    if (!pts || !pts.length) return '';
    let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
    for (let i = 1; i < pts.length; i++) {
      d += ` L${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)}`;
    }
    if (closed) d += ' Z';
    return d;
  }

  function catmullRomToPathD(pts, closed = false, tension = 0.5) {
    if (!pts || pts.length < 2) return '';
    if (pts.length === 2) return pointsToPathD(pts, closed);
    const n = pts.length;
    let d = `M${pts[0][0].toFixed(2)},${pts[0][1].toFixed(2)}`;
    const count = closed ? n : n - 1;
    for (let i = 0; i < count; i++) {
      const p0 = pts[(i - 1 + n) % n] && (closed || i > 0) ? pts[(i - 1 + n) % n] : pts[0];
      const p1 = pts[i];
      const p2 = pts[(i + 1) % n];
      const p3 = (closed || i + 2 < n) ? pts[(i + 2) % n] : pts[n - 1];
      const c1x = p1[0] + (p2[0] - p0[0]) * tension / 3;
      const c1y = p1[1] + (p2[1] - p0[1]) * tension / 3;
      const c2x = p2[0] - (p3[0] - p1[0]) * tension / 3;
      const c2y = p2[1] - (p3[1] - p1[1]) * tension / 3;
      d += ` C${c1x.toFixed(2)},${c1y.toFixed(2)} ${c2x.toFixed(2)},${c2y.toFixed(2)} ${p2[0].toFixed(2)},${p2[1].toFixed(2)}`;
    }
    if (closed) d += ' Z';
    return d;
  }

  function pointOnPolyline(pts, progress) {
    if (!pts || !pts.length) return { x: 0, y: 0, angle: 0 };
    if (pts.length === 1) return { x: pts[0][0], y: pts[0][1], angle: 0 };
    const u = Ease.clamp(progress, 0, 1);
    let total = 0;
    const segs = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const dx = pts[i + 1][0] - pts[i][0];
      const dy = pts[i + 1][1] - pts[i][1];
      const len = Math.hypot(dx, dy);
      segs.push({ x0: pts[i][0], y0: pts[i][1], dx, dy, len });
      total += len;
    }
    if (total < 1e-6) return { x: pts[0][0], y: pts[0][1], angle: 0 };
    const target = total * u;
    let acc = 0;
    for (let i = 0; i < segs.length; i++) {
      const s = segs[i];
      if (acc + s.len >= target || i === segs.length - 1) {
        const f = s.len > 1e-6 ? (target - acc) / s.len : 0;
        return {
          x: s.x0 + s.dx * f,
          y: s.y0 + s.dy * f,
          angle: Math.atan2(s.dy, s.dx) * (180 / Math.PI)
        };
      }
      acc += s.len;
    }
    return { x: pts[pts.length - 1][0], y: pts[pts.length - 1][1], angle: 0 };
  }

  function createSvgEl(tag, attrs = {}) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v !== undefined && v !== null) el.setAttribute(k, String(v));
    }
    return el;
  }

  // ============================================================================
  // 4. Engine Core State & DOM References
  // ============================================================================
  const Engine = {
    Ease,
    MANIFEST,
    SVG_NS,
    createSvgEl,
    pointsToPathD,
    catmullRomToPathD,
    pointOnPolyline,

    mode: 'gallery', // 'gallery' | 'talk' | 'film' | 'play'
    paused: false,
    time: 0,         // Current deterministic time t (in seconds)
    lastRaf: 0,
    scenes: [],      // Registered storyboard scenes in speaking order
    beats: [],       // Flattened list of all storyboard beats with global [t0, t1]
    currentBeatIdx: 0,
    beatLocalTime: 0,
    filmDuration: 580,

    // Camera state: viewBox [x, y, w, h]
    camera: {
      currentBox: [-38, -22, 1176, 944],
      targetBox: [-38, -22, 1176, 944],
      mag: 1.0,
      objective: '4×',
      lastObjective: '4×',
      focusPullUntil: -1,
      emFlashUntil: -1,
      lastSpeakerSec: null,
      speakerChipUntil: -1
    },

    // Breath state (5s period normal; 2.1s shallow in ★6)
    breath: {
      period: 5.0,
      shallow: 0.0, // 0 = normal deep breath, 1 = stiff fibrotic shallow breath
      phase: 0,
      inhale: 0
    },

    // Actor & Path registries
    actorNodes: {},
    pathNodes: {},
    particlePool: [],
    MAX_PARTICLES: 280,

    // Register a scene module (called by scenes/s0_opening.js .. s7_conclusion_finale.js)
    registerScene(sceneDef) {
      this.scenes.push(sceneDef);
      this.scenes.sort((a, b) => (a.order || 0) - (b.order || 0));
      this._rebuildTimeline();
    },

    _rebuildTimeline() {
      this.beats = [];
      let cursor = 0;
      for (const sc of this.scenes) {
        sc.tStart = cursor;
        for (let i = 0; i < (sc.beats || []).length; i++) {
          const b = sc.beats[i];
          const dur = b.duration || 10;
          const beatEntry = Object.assign({}, b, {
            sceneId: sc.id,
            sceneTitle: sc.title,
            speaker: sc.speaker,
            sectionNum: sc.sectionNum,
            color: sc.color || '#1E2433',
            t0: cursor,
            t1: cursor + dur,
            duration: dur,
            indexInScene: i
          });
          this.beats.push(beatEntry);
          cursor += dur;
        }
        sc.tEnd = cursor;
      }
      this.filmDuration = Math.max(60, cursor);
    },

    // ==========================================================================
    // 5. Stage Initialization (Plates, Routes, Actors, Particle Pool, Desk)
    // ==========================================================================
    init() {
      this.dom = {
        stage: document.getElementById('stage'),
        defs: document.getElementById('stage-defs'),
        plateBase: document.getElementById('plate-base'),
        layerTiles: document.getElementById('layer-tiles'),
        layerWall: document.getElementById('layer-wall'),
        layerRoutes: document.getElementById('layer-routes'),
        layerCell: document.getElementById('layer-cell'),
        layerAir: document.getElementById('layer-air'),
        layerDoodles: document.getElementById('layer-doodles'),
        layerLabels: document.getElementById('layer-labels'),
        particlePoolGroup: document.getElementById('particle-pool'),
        layerPlay: document.getElementById('layer-play'),
        layerOpeningFinale: document.getElementById('layer-opening-finale'),
        deskBreakout: document.getElementById('desk-breakout-layer'),
        layerPropsSvg: document.getElementById('layer-props-svg'),
        playCursor: document.getElementById('play-cursor'),
        bulletDimmer: document.getElementById('bullet-dimmer'),
        paperLightSweep: document.getElementById('paper-light-sweep'),
        statusText: document.getElementById('status-text'),
        modeDot: document.getElementById('mode-dot'),
        speakerChip: document.getElementById('speaker-chip'),
        progressThread: document.getElementById('progress-thread'),
        helpDialog: document.getElementById('help-dialog')
      };

      this._initPlateFallbackChain();
      this._initWatercolourNoiseMask();
      this._initRoutesAndPaths();
      this._initActors();
      this._initDeskBreakoutFibre();
      this._initParticlePool();
      this._initControls();

      if (window.LivingDevices) window.LivingDevices.init(this);
      if (window.LivingAmbient) window.LivingAmbient.init(this);
      if (window.LivingPlay) window.LivingPlay.init(this);
      for (const sc of this.scenes) {
        if (typeof sc.init === 'function') sc.init(this);
      }

      // Parse URL query params (?mode=film&t=12.5) for headless video exporter
      const params = new URLSearchParams(window.location.search);
      if (params.get('mode')) {
        this.setMode(params.get('mode'));
      }
      if (params.get('t') !== null) {
        const tVal = parseFloat(params.get('t'));
        if (!isNaN(tVal)) {
          this.seek(tVal);
          return;
        }
      }

      // Start requestAnimationFrame loop
      this.lastRaf = performance.now();
      const tick = (now) => {
        const dt = Math.min(0.1, (now - this.lastRaf) / 1000);
        this.lastRaf = now;
        if (!this.paused) {
          this._advanceTime(dt);
        }
        this.render(this.time);
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    },

    _initPlateFallbackChain() {
      const candidates = MANIFEST.fallbackPlates || [];
      let idx = 0;
      const tryNext = () => {
        if (idx >= candidates.length) return;
        const src = candidates[idx++];
        const img = new Image();
        img.onload = () => {
          this.dom.plateBase.setAttribute('href', src);
          this.activePlateUrl = src;
          if (window.LivingDevices && window.LivingDevices.updateLoupePlate) {
            window.LivingDevices.updateLoupePlate(src);
          }
        };
        img.onerror = tryNext;
        img.src = src;
      };
      tryNext();
    },

    _initWatercolourNoiseMask() {
      // Generate a procedural wet-paint noise mask on an offscreen canvas once at startup (§7.3)
      try {
        const c = document.createElement('canvas');
        c.width = 128;
        c.height = 128;
        const ctx = c.getContext('2d');
        const img = ctx.createImageData(128, 128);
        for (let y = 0; y < 128; y++) {
          for (let x = 0; x < 128; x++) {
            const dx = (x - 64) / 64;
            const dy = (y - 64) / 64;
            const r = Math.hypot(dx, dy);
            const n = Math.sin(x * 0.23) * Math.cos(y * 0.29) * 0.14 +
                      Math.sin(x * 0.61 + y * 0.53) * 0.08;
            const edge = Ease.clamp(1 - (r + n - 0.55) / 0.38, 0, 1);
            const val = Math.round(edge * 255);
            const idx = (y * 128 + x) * 4;
            img.data[idx] = val;
            img.data[idx + 1] = val;
            img.data[idx + 2] = val;
            img.data[idx + 3] = 255;
          }
        }
        ctx.putImageData(img, 0, 0);
        this.watercolourMaskUri = c.toDataURL('image/png');
      } catch (e) {
        this.watercolourMaskUri = null;
      }
    },

    _initRoutesAndPaths() {
      const g = this.dom.layerRoutes;
      g.innerHTML = '';
      const pathStyles = {
        cell_outline:       { stroke: '#C07A66', w: 3.4, glow: '#FFE2B8' },
        red_route:          { stroke: '#E0452B', w: 5.5, glow: '#FF8A75' },
        blue_route:         { stroke: '#1F58C8', w: 5.5, glow: '#75A8FF' },
        copii_hop:          { stroke: '#D98E00', w: 2.2, dash: '2.5 1.8' },
        clathrin_path:      { stroke: '#1F58C8', w: 2.2 },
        m6pr_loop:          { stroke: '#1E9B6B', w: 2.4, dash: '3.2 2.2' },
        amino_recycle:      { stroke: '#1E9B6B', w: 2.5, dash: '3.4 2.4' },
        nfkb_signal:        { stroke: '#C81D63', w: 2.2, dash: '1.2 2.2' },
        src_syk_pi3k:       { stroke: '#E2B33C', w: 2.0 },
        cdc42_wasp_arp:     { stroke: '#E07B39', w: 2.0 },
        rac_wave_arp:       { stroke: '#E07B39', w: 2.0 },
        signal1_priming:    { stroke: '#5B4F78', w: 2.2 },
        signal2_cathepsin:  { stroke: '#1F58C8', w: 2.0 },
        signal2_kplus:      { stroke: '#5F73A3', w: 2.0 },
        signal2_ros:        { stroke: '#C81D63', w: 2.0 },
        caspase_il1b:       { stroke: '#C81D63', w: 2.4 },
        pyroptosis_path:    { stroke: '#7A6470', w: 2.0, dash: '3.5 2.5' },
        wall_il1b_tnfa:     { stroke: '#C81D63', w: 2.4, dash: '1.4 2.2' },
        wall_tgfb_pdgf:     { stroke: '#B4690E', w: 2.6 }
      };

      for (const [id, pts] of Object.entries(MANIFEST.paths)) {
        const st = pathStyles[id] || { stroke: '#7A3FB5', w: 2.0 };
        const closed = id === 'cell_outline';
        const d = catmullRomToPathD(pts, closed);
        const grp = createSvgEl('g', { id: `path-grp-${id}`, opacity: '0' });

        // Soft under-glow path
        const glowPath = createSvgEl('path', {
          d,
          fill: 'none',
          stroke: st.glow || st.stroke,
          'stroke-width': st.w * 2.8,
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round',
          opacity: '0.38'
        });

        // Main stroke path
        const mainPath = createSvgEl('path', {
          id: `path-${id}`,
          d,
          fill: 'none',
          stroke: st.stroke,
          'stroke-width': st.w,
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round'
        });
        if (st.dash) mainPath.setAttribute('stroke-dasharray', st.dash);

        grp.appendChild(glowPath);
        grp.appendChild(mainPath);
        g.appendChild(grp);

        let len = 500;
        try { len = mainPath.getTotalLength(); } catch (e) {}
        this.pathNodes[id] = { grp, mainPath, glowPath, pts, length: len, dash: st.dash };
      }

      // Signal pulse comet group
      this.signalCometGroup = createSvgEl('g', { id: 'signal-comets' });
      g.appendChild(this.signalCometGroup);

      // Watercolour bloom group
      this.bloomGroup = createSvgEl('g', { id: 'watercolour-blooms' });
      g.appendChild(this.bloomGroup);
    },

    // ==========================================================================
    // 6. Actor System (Multi-State Vector + Raster Hybrid Actors)
    // ==========================================================================
    _initActors() {
      // Build dynamic actor groups in #layer-cell, #layer-wall, #layer-air
      this.dom.layerCell.innerHTML = '';
      this.dom.layerWall.innerHTML = '';
      this.dom.layerAir.innerHTML = '';

      // 1. Air Breath Wash & Sinking Silica Crystals in #layer-air
      this.airWashRect = createSvgEl('rect', {
        x: '0', y: '90', width: '1100', height: '670',
        fill: 'url(#breath-air-grad)', opacity: '0.25', 'pointer-events': 'none'
      });
      this.dom.layerAir.appendChild(this.airWashRect);

      // 2. Build Multi-State Actors required by §7.1 Table:
      // - recog.bacterium (4 states: whole -> cracked -> split -> crumbled)
      // - recog.arms (4 states: open -> reaching -> wrapping -> sealed)
      // - recog.receptors (4 bridges: TLR4, MR, CR3, FcγR)
      // - recog.actin (70° dendritic Arp2/3 branches growing like frost)
      // - matur.vesicle (traveling phagosome on red route + Rab5 -> Rab7 conversion)
      // - biogen.hero (hero enzyme travelling ER -> cis-Golgi -> TGN -> LE -> Lysosome)
      // - fusion.pore (3 states: tethered -> zippered -> open iris pore)
      // - killing.furnace (NOX2 assembly, V-ATPase spin, hydrolases waking, bacterium crumbling)
      // - particles.silica_pl (3 states: intact -> pressing -> torn membrane + cathepsin B leak)
      // - particles.nlrp3 (3 states: scattered monomers -> swinging -> locked clockwork wheel + ASC)
      // - particles.gsdmd (GSDMD pores opening like irises in right membrane)
      // - particles.asbestos_hood (3 states: rest / reach / max strain along fibre)
      // - particles.fibrosis (5 states: collagen spreading right -> left along wall)
      // - alveolar.lumen (2 states: open / narrowed alveoli)
      this.actorsRoot = createSvgEl('g', { id: 'actors-root' });
      this.dom.layerCell.appendChild(this.actorsRoot);

      this.wallActorsRoot = createSvgEl('g', { id: 'wall-actors-root' });
      this.dom.layerWall.appendChild(this.wallActorsRoot);

      this._buildProceduralStateActors();
    },

    _buildProceduralStateActors() {
      // A. Pseudopod arms (4 states: 0=open printed, 1=reaching, 2=wrapping, 3=sealed kiss)
      const armsGrp = this._createActorGroup('recog.arms', 95, 392, 4);
      const armAngles = [0, 0.35, 0.72, 1.0];
      armAngles.forEach((f, idx) => {
        const st = armsGrp.states[idx];
        const tipX = 31 - f * 12;
        const upperY = 302 + f * 88;
        const lowerY = 482 - f * 88;
        const dUp = `M150,290 Q${95 - f * 15},${262 + f * 18} ${tipX},${upperY} Q${65 - f * 10},${305 + f * 55} 142,330 Z`;
        const dLo = `M150,494 Q${95 - f * 15},${522 - f * 18} ${tipX},${lowerY} Q${65 - f * 10},${479 - f * 55} 142,454 Z`;
        st.appendChild(createSvgEl('path', {
          d: `${dUp} ${dLo}`,
          fill: '#FAD8C5',
          stroke: '#C07A66',
          'stroke-width': '2.6',
          'stroke-linejoin': 'round',
          opacity: idx === 0 ? '0' : '0.94'
        }));
        if (idx === 3) {
          // Soft membrane "kiss" ripple at seal point (19, 392)
          st.appendChild(createSvgEl('circle', {
            cx: String(tipX), cy: '392', r: '11',
            fill: 'none', stroke: '#E07B39', 'stroke-width': '1.6', opacity: '0.85'
          }));
        }
      });

      // B. Fusion pore (3 states: 0=approaching/tether, 1=SNARE tight contact, 2=open fusion pore + violet bleed)
      const poreGrp = this._createActorGroup('fusion.pore', 508, 660, 3);
      [0, 1, 2].forEach((idx) => {
        const st = poreGrp.states[idx];
        if (idx === 1) {
          st.appendChild(createSvgEl('circle', {
            cx: '508', cy: '656', r: '15',
            fill: '#E4D3F3', stroke: '#7A3FB5', 'stroke-width': '3.2', opacity: '0.9'
          }));
        } else if (idx === 2) {
          // Open fusion neck & violet inflow stream
          st.appendChild(createSvgEl('path', {
            d: 'M482,665 Q502,650 518,654 Q504,672 484,682 Z',
            fill: '#C694E8', stroke: '#6F36A8', 'stroke-width': '2.8', opacity: '0.92'
          }));
        }
      });

      // C. Silica membrane (3 states: 0=intact, 1=crystal pressing & bulging rim, 2=torn rim + cathepsin B leak)
      const silMemGrp = this._createActorGroup('particles.silica_membrane', 850, 560, 3);
      [0, 1, 2].forEach((idx) => {
        const st = silMemGrp.states[idx];
        if (idx === 1) {
          st.appendChild(createSvgEl('path', {
            d: 'M892,570 L904,584 L886,588 Z',
            fill: '#D8ECF8', stroke: '#4F6874', 'stroke-width': '1.4'
          }));
        } else if (idx === 2) {
          // Jagged membrane tear + leaking blue cathepsin B & ROS
          st.appendChild(createSvgEl('path', {
            d: 'M890,566 L902,562 M894,586 L906,594',
            fill: 'none', stroke: '#C81D63', 'stroke-width': '2.4', 'stroke-linecap': 'round'
          }));
          [[902, 588], [912, 594], [919, 589], [924, 600]].forEach(([cx, cy]) => {
            st.appendChild(createSvgEl('circle', {
              cx, cy, r: '2.6', fill: '#1F58C8', stroke: '#0D2E70', 'stroke-width': '0.5'
            }));
          });
        }
      });

      // D. NLRP3 Inflammasome (3 states: 0=scattered monomers, 1=swinging in, 2=locked 7-spoke clockwork wheel + ASC)
      const nlrp3Grp = this._createActorGroup('particles.nlrp3', 918, 655, 3);
      [0, 1, 2].forEach((idx) => {
        const st = nlrp3Grp.states[idx];
        const radius = idx === 0 ? 18 : idx === 1 ? 11 : 6.5;
        const rotOffset = idx * 25;
        if (idx > 0) {
          for (let k = 0; k < 7; k++) {
            const a = ((k * 360 / 7) + rotOffset) * Math.PI / 180;
            const x = 918 + Math.cos(a) * radius;
            const y = 655 + Math.sin(a) * radius;
            st.appendChild(createSvgEl('ellipse', {
              cx: x.toFixed(1), cy: y.toFixed(1), rx: '4.2', ry: '2.2',
              fill: '#E58AAE', stroke: '#7A0C37', 'stroke-width': '0.6',
              transform: `rotate(${(k * 360 / 7 + rotOffset).toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)})`
            }));
          }
        }
        if (idx === 2) {
          st.appendChild(createSvgEl('circle', {
            cx: '918', cy: '655', r: '4.2', fill: '#FFE066', stroke: '#7A0C37', 'stroke-width': '0.8'
          }));
        }
      });

      // E. Bacterium in Phagolysosome (4 states: 0=intact rod, 1=cracked envelope, 2=split halves, 3=crumbled fragments)
      const bactKillGrp = this._createActorGroup('killing.bacterium', 618, 669, 4);
      [0, 1, 2, 3].forEach((idx) => {
        const st = bactKillGrp.states[idx];
        if (idx === 1) {
          st.appendChild(createSvgEl('path', {
            d: 'M612,656 L620,666 L615,674 L624,682',
            fill: 'none', stroke: '#FFE066', 'stroke-width': '2.2', 'stroke-linecap': 'round'
          }));
        } else if (idx === 2) {
          st.appendChild(createSvgEl('ellipse', {
            cx: '604', cy: '662', rx: '14', ry: '7',
            fill: '#8C9A3A', stroke: '#4E5A16', 'stroke-width': '1.2', transform: 'rotate(-28 604 662)'
          }));
          st.appendChild(createSvgEl('ellipse', {
            cx: '632', cy: '676', rx: '14', ry: '7',
            fill: '#8C9A3A', stroke: '#4E5A16', 'stroke-width': '1.2', transform: 'rotate(-10 632 676)'
          }));
        } else if (idx === 3) {
          [[-16, -8], [-6, 6], [8, -4], [18, 10], [2, 14], [-12, 12]].forEach(([dx, dy]) => {
            st.appendChild(createSvgEl('circle', {
              cx: String(618 + dx), cy: String(669 + dy), r: '2.8',
              fill: '#A2B048', stroke: '#4E5A16', 'stroke-width': '0.6', opacity: '0.85'
            }));
          });
        }
      });

      // F. Asbestos Hood (3 states: 0=rest, 1=reaching along fibre, 2=max strain & trembling)
      const hoodGrp = this._createActorGroup('particles.asbestos_hood', 995, 738, 3);
      [0, 1, 2].forEach((idx) => {
        const st = hoodGrp.states[idx];
        if (idx > 0) {
          const ext = idx * 18;
          const d = `M991,722 Q${1005 + ext},732 ${1007 + ext},740.5 Q${985 + ext * 0.6},742 952,741 Z`;
          st.appendChild(createSvgEl('path', {
            d,
            fill: '#F7C9B0',
            stroke: idx === 2 ? '#C81D63' : '#C07A66',
            'stroke-width': '2.6',
            opacity: '0.92'
          }));
        }
      });

      // G. Fibrosis extent along the wall (5 states: spreading right -> left x=950 down to x=360)
      const fibGrp = this._createActorGroup('particles.fibrosis', 650, 795, 5, this.wallActorsRoot);
      const xReach = [900, 760, 620, 480, 340];
      xReach.forEach((xLeft, idx) => {
        const st = fibGrp.states[idx];
        if (idx > 0) {
          for (let k = 0; k < idx * 9; k++) {
            const bx = xLeft + ((k * 47) % (1060 - xLeft));
            const by = 768 + ((k * 23) % 58);
            const d = `M${bx - 16},${by} Q${bx - 8},${by - 3.5} ${bx},${by} T${bx + 16},${by}`;
            st.appendChild(createSvgEl('path', {
              d,
              fill: 'none',
              stroke: '#C7A170',
              'stroke-width': '1.65',
              'stroke-linecap': 'round',
              opacity: String(0.35 + idx * 0.12)
            }));
          }
        }
      });

      // H. Alveolar lumen narrowing in ★6 (2 states: 0=open, 1=narrowed/compressed alveoli below septum)
      const alvGrp = this._createActorGroup('alveolar.lumen', 550, 815, 2, this.wallActorsRoot);
      alvGrp.states[1].appendChild(createSvgEl('rect', {
        x: '200', y: '758', width: '890', height: '95',
        fill: '#E6CDAE', opacity: '0.36', rx: '12'
      }));
    },

    _createActorGroup(actorId, pivotX, pivotY, numStates = 1, parent = this.actorsRoot) {
      const grp = createSvgEl('g', {
        id: `actor-${actorId.replace(/\./g, '-')}`,
        'data-actor': actorId,
        'data-pivot': `${pivotX},${pivotY}`
      });
      const states = [];
      const manifestActor = MANIFEST.actors && MANIFEST.actors[actorId];

      for (let i = 0; i < numStates; i++) {
        const sg = createSvgEl('g', {
          class: `actor-state state-${i}`,
          opacity: i === 0 ? '1' : '0'
        });
        // If manifest provides raster WebP for this state, attach <image>
        if (manifestActor && manifestActor.states && manifestActor.states[i] && manifestActor.bbox) {
          const [bx, by, bw, bh] = manifestActor.bbox;
          sg.appendChild(createSvgEl('image', {
            x: bx, y: by, width: bw, height: bh,
            href: manifestActor.states[i],
            preserveAspectRatio: 'none'
          }));
        }
        grp.appendChild(sg);
        states.push(sg);
      }

      parent.appendChild(grp);
      this.actorNodes[actorId] = { grp, states, pivotX, pivotY, numStates };
      return this.actorNodes[actorId];
    },

    // ==========================================================================
    // 7. ★5 Fourth-Wall Breakout Asbestos Fibre on the Dark Scientist's Desk
    // ==========================================================================
    _initDeskBreakoutFibre() {
      const g = this.dom.deskBreakout;
      g.innerHTML = '';
      // The asbestos fibre starts in the open cup at (905, 746), crosses the paper edge at x=1100,
      // and continues out onto the dark scientist's desk to x=1215, casting a realistic shadow!
      const shadow = createSvgEl('line', {
        id: 'desk-fibre-shadow',
        x1: '1099', y1: '753.5', x2: '1218', y2: '758.5',
        stroke: '#000000', 'stroke-width': '9.5', 'stroke-linecap': 'round', opacity: '0.58'
      });
      const fibreCore = createSvgEl('line', {
        id: 'desk-fibre-body',
        x1: '1098', y1: '749.7', x2: '1215', y2: '752.2',
        stroke: '#D6B676', 'stroke-width': '4.6', 'stroke-linecap': 'butt'
      });
      const fibreHi = createSvgEl('line', {
        id: 'desk-fibre-hi',
        x1: '1098', y1: '748.4', x2: '1215', y2: '750.9',
        stroke: '#F5E4B8', 'stroke-width': '1.3', 'stroke-linecap': 'butt', opacity: '0.85'
      });
      // Frayed needle splinters at the far desk tip (1215, 752.2)
      const frays = createSvgEl('path', {
        id: 'desk-fibre-frays',
        d: 'M1214,750.5 L1224,748.8 M1215,752.0 L1227,752.4 M1214,753.6 L1223,755.5',
        fill: 'none', stroke: '#DFC48C', 'stroke-width': '1.1', 'stroke-linecap': 'round'
      });

      g.appendChild(shadow);
      g.appendChild(fibreCore);
      g.appendChild(fibreHi);
      g.appendChild(frays);
    },

    // ==========================================================================
    // 8. Pooled Particle System (<= 300 live SVG nodes, deterministic from t)
    // ==========================================================================
    _initParticlePool() {
      const g = this.dom.particlePoolGroup;
      g.innerHTML = '';
      this.particlePool = [];
      for (let i = 0; i < this.MAX_PARTICLES; i++) {
        const useEl = createSvgEl('use', {
          href: '#sprite-hplus',
          x: '0', y: '0',
          style: 'display:none'
        });
        g.appendChild(useEl);
        this.particlePool.push({ el: useEl, active: false });
      }
      this.particleCursor = 0;
    },

    resetParticlesForFrame() {
      for (let i = 0; i < this.particleCursor; i++) {
        this.particlePool[i].el.style.display = 'none';
      }
      this.particleCursor = 0;
      if (this.signalCometGroup) this.signalCometGroup.innerHTML = '';
      if (this.bloomGroup) this.bloomGroup.innerHTML = '';
    },

    spawnParticle(kind, x, y, scale = 1, rot = 0, opacity = 1) {
      if (this.particleCursor >= this.MAX_PARTICLES) return;
      const p = this.particlePool[this.particleCursor++];
      const spriteMap = {
        hplus: '#sprite-hplus',
        kplus: '#sprite-kplus',
        ros: '#sprite-ros',
        cytokine: '#sprite-cytokine',
        amino: '#sprite-amino',
        glint: '#sprite-glint',
        rbc: '#sprite-rbc',
        dust: '#sprite-dust'
      };
      p.el.setAttribute('href', spriteMap[kind] || '#sprite-hplus');
      p.el.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rot.toFixed(1)}) scale(${scale.toFixed(2)})`);
      p.el.setAttribute('opacity', opacity.toFixed(2));
      p.el.style.display = '';
    },

    // ==========================================================================
    // 9. Public Choreography Helpers for Scenes (stateCrossFade, dashDraw, etc.)
    // ==========================================================================
    resetSceneOverlays() {
      // Reset all paths, actor transforms, label halos before evaluating pure render(t)
      for (const pn of Object.values(this.pathNodes)) {
        pn.grp.setAttribute('opacity', '0');
        pn.mainPath.removeAttribute('stroke-dashoffset');
      }
      for (const an of Object.values(this.actorNodes)) {
        an.grp.setAttribute('transform', '');
        an.grp.setAttribute('opacity', '1');
        an.states.forEach((st, i) => st.setAttribute('opacity', i === 0 ? '1' : '0'));
      }
      this.dom.layerLabels.innerHTML = '';
      this.dom.bulletDimmer.setAttribute('opacity', '0');
    },

    stateCrossFade(actorId, stateFloat) {
      const an = this.actorNodes[actorId];
      if (!an) return;
      const s = Ease.clamp(stateFloat, 0, an.numStates - 1);
      const i0 = Math.floor(s);
      const i1 = Math.min(an.numStates - 1, i0 + 1);
      const frac = s - i0;
      an.states.forEach((st, idx) => {
        let op = 0;
        if (idx === i0 && idx === i1) op = 1;
        else if (idx === i0) op = 1 - frac;
        else if (idx === i1) op = frac;
        st.setAttribute('opacity', op.toFixed(3));
      });
    },

    transformActor(actorId, { dx = 0, dy = 0, rot = 0, scale = 1, opacity = 1 } = {}) {
      const an = this.actorNodes[actorId];
      if (!an) return;
      const px = an.pivotX;
      const py = an.pivotY;
      const tf = `translate(${dx.toFixed(2)} ${dy.toFixed(2)}) translate(${px} ${py}) rotate(${rot.toFixed(2)}) scale(${scale.toFixed(3)}) translate(${-px} ${-py})`;
      an.grp.setAttribute('transform', tf);
      an.grp.setAttribute('opacity', opacity.toFixed(3));
    },

    dashDraw(pathId, progress, opacity = 1) {
      const pn = this.pathNodes[pathId];
      if (!pn) return;
      const u = Ease.clamp(progress, 0, 1);
      if (u <= 0.001) {
        pn.grp.setAttribute('opacity', '0');
        return;
      }
      pn.grp.setAttribute('opacity', opacity.toFixed(3));
      const len = pn.length || 400;
      if (!pn.dash) {
        pn.mainPath.setAttribute('stroke-dasharray', `${len}`);
        pn.mainPath.setAttribute('stroke-dashoffset', `${(len * (1 - u)).toFixed(1)}`);
      }
      pn.glowPath.setAttribute('stroke-dasharray', `${len}`);
      pn.glowPath.setAttribute('stroke-dashoffset', `${(len * (1 - u)).toFixed(1)}`);
    },

    pointOnPath(pathId, progress) {
      const pn = this.pathNodes[pathId];
      if (!pn) return { x: 550, y: 450, angle: 0 };
      return pointOnPolyline(pn.pts, progress);
    },

    pulseSignal(pathId, progress, color = '#FFE066', radius = 3.6) {
      const u = Ease.clamp(progress, 0, 1);
      if (u <= 0 || u >= 1) return;
      const pt = this.pointOnPath(pathId, u);
      // Draw fading comet trail + bright head
      for (let k = 3; k >= 0; k--) {
        const trailU = Math.max(0, u - k * 0.045);
        const tp = this.pointOnPath(pathId, trailU);
        const r = radius * (1 - k * 0.18);
        const op = (1 - k * 0.22) * Math.sin(Math.PI * u);
        this.signalCometGroup.appendChild(createSvgEl('circle', {
          cx: tp.x.toFixed(1),
          cy: tp.y.toFixed(1),
          r: r.toFixed(2),
          fill: k === 0 ? '#FFFFFF' : color,
          stroke: color,
          'stroke-width': k === 0 ? '1.2' : '0',
          opacity: op.toFixed(2)
        }));
      }
    },

    watercolourBloom({ cx, cy, r, color = '#7A3FB5', opacity = 0.55 }) {
      if (opacity <= 0.01) return;
      this.bloomGroup.appendChild(createSvgEl('circle', {
        cx: cx.toFixed(1),
        cy: cy.toFixed(1),
        r: r.toFixed(1),
        fill: color,
        opacity: (opacity * 0.55).toFixed(3)
      }));
      this.bloomGroup.appendChild(createSvgEl('circle', {
        cx: (cx - r * 0.08).toFixed(1),
        cy: (cy - r * 0.06).toFixed(1),
        r: (r * 0.78).toFixed(1),
        fill: color,
        opacity: (opacity * 0.35).toFixed(3)
      }));
    },

    /**
     * Lights poster labels by name with a soft warm halo behind them plus a 15% lift (§7.1.6).
     * Enforces the glow budget (§2.3: at most two strong glows on screen at once).
     */
    lightLabels(names = [], intensity = 1.0) {
      if (!names || !names.length || intensity <= 0.01) return;
      const g = this.dom.layerLabels;
      let strongGlowCount = 0;

      for (const name of names) {
        const info = MANIFEST.labels[name];
        if (!info) continue;
        const isStrong = strongGlowCount < 2;
        if (isStrong) strongGlowCount++;

        const liftScale = 1 + 0.15 * Ease.clamp(intensity, 0, 1);
        const rx = Math.max(16, info.w * 0.72);
        const ry = Math.max(9, info.h * 0.95);

        const itemGrp = createSvgEl('g', {
          transform: `translate(${info.x.toFixed(1)} ${info.y.toFixed(1)}) scale(${liftScale.toFixed(3)}) translate(${-info.x.toFixed(1)} ${-info.y.toFixed(1)})`,
          opacity: Ease.clamp(intensity, 0, 1).toFixed(3)
        });

        // Soft warm watercolour halo behind the label
        itemGrp.appendChild(createSvgEl('ellipse', {
          cx: info.x.toFixed(1),
          cy: (info.y - info.h * 0.28).toFixed(1),
          rx: rx.toFixed(1),
          ry: ry.toFixed(1),
          fill: isStrong ? 'url(#halo-warm-grad)' : '#FFF8DC',
          opacity: isStrong ? '0.92' : '0.62'
        }));

        // Crisp lifted label text in the poster's own words & colour
        const isDisplay = info.h >= 13 || /^[1-6]/.test(name);
        const txt = createSvgEl('text', {
          x: info.x.toFixed(1),
          y: info.y.toFixed(1),
          'font-family': isDisplay ? "Gabriola, 'Segoe Print', serif" : "'Segoe UI Variable Text', 'Segoe UI', sans-serif",
          'font-size': isDisplay ? '11.5' : '5.1',
          'font-weight': isDisplay ? '600' : '700',
          fill: info.color || '#1E2433',
          'text-anchor': 'middle',
          stroke: '#F8F3E8',
          'stroke-width': '1.3',
          'paint-order': 'stroke'
        });
        txt.textContent = name;
        itemGrp.appendChild(txt);
        g.appendChild(itemGrp);
      }
    },

    // ==========================================================================
    // 10. Camera & 2.5D Parallax & Objective Thresholds
    // ==========================================================================
    setCameraBox(box, forceEM = false) {
      this.camera.currentBox = box;
      const [vx, vy, vw, vh] = box;
      this.dom.stage.setAttribute('viewBox', `${vx.toFixed(2)} ${vy.toFixed(2)} ${vw.toFixed(2)} ${vh.toFixed(2)}`);

      // Compute magnification relative to 1100 mm poster width
      const mag = 1100 / Math.max(40, vw);
      this.camera.mag = mag;

      // Determine Microscope Objective from zoom thresholds (§7.3: 1.4x, 2.5x, 3.5x, EM)
      let obj = '4×';
      if (forceEM || mag >= 4.4) obj = 'EM';
      else if (mag >= 3.5) obj = '100× oil';
      else if (mag >= 2.5) obj = '40×';
      else if (mag >= 1.4) obj = '10×';

      if (obj !== this.camera.objective) {
        this.camera.lastObjective = this.camera.objective;
        this.camera.objective = obj;
        this.camera.focusPullUntil = this.time + 0.6;
        if (obj === 'EM') {
          this.camera.emFlashUntil = this.time + 0.4;
        }
        if (window.LivingDevices) {
          window.LivingDevices.onObjectiveChange(obj, this.time);
        }
      }

      // Focus pull & EM flash CSS classes (deterministic from time window)
      const inFocusPull = this.time < this.camera.focusPullUntil && this.time >= this.camera.focusPullUntil - 0.6;
      const inEmFlash = this.time < this.camera.emFlashUntil && this.time >= this.camera.emFlashUntil - 0.4;
      this.dom.stage.classList.toggle('focus-pull-active', inFocusPull);
      this.dom.stage.classList.toggle('em-flash-active', inEmFlash);

      // 1-2% 2.5D Parallax between Air Dust (+1.6%), Cell (0%), and Alveolar Wall (-1.0%) (§2.3)
      const cx = vx + vw * 0.5;
      const cy = vy + vh * 0.5;
      const dx = cx - 550;
      const dy = cy - 450;
      const zoomFactor = Ease.clamp((mag - 1.0) / 2.5, 0, 1);

      const airDx = -dx * 0.016 * zoomFactor;
      const airDy = -dy * 0.016 * zoomFactor;
      const wallDx = dx * 0.010 * zoomFactor;
      const wallDy = dy * 0.010 * zoomFactor + this.breath.wallFlexY;

      this.dom.layerAir.setAttribute('transform', `translate(${airDx.toFixed(2)} ${airDy.toFixed(2)})`);
      this.dom.layerWall.setAttribute('transform', `translate(${wallDx.toFixed(2)} ${wallDy.toFixed(2)})`);

      // Lazy High-Res Tile Activation based on zoom & viewBox overlap (§7.1.7)
      this._updateLazyTiles(box, mag, obj === 'EM');
    },

    _updateLazyTiles(box, mag, isEM) {
      if (mag < 1.35) {
        this.dom.layerTiles.style.display = 'none';
        return;
      }
      this.dom.layerTiles.style.display = '';
      const [vx, vy, vw, vh] = box;
      for (const [zid, zinfo] of Object.entries(MANIFEST.zones)) {
        const [zx, zy, zw, zh] = zinfo.rect;
        const overlaps = !(vx + vw < zx || vx > zx + zw || vy + vh < zy || vy > zy + zh);
        let tileEl = document.getElementById(`lazy-tile-${zid}`);
        if (overlaps && (zinfo.dpi300 || zinfo.em600)) {
          if (!tileEl) {
            tileEl = createSvgEl('image', {
              id: `lazy-tile-${zid}`,
              x: zx, y: zy, width: zw, height: zh,
              preserveAspectRatio: 'none',
              opacity: '0'
            });
            // Probe tile URL softly so missing tiles never show broken image icons
            const targetSrc = (isEM && zinfo.em600) ? zinfo.em600 : zinfo.dpi300;
            const probe = new Image();
            probe.onload = () => {
              tileEl.setAttribute('href', targetSrc);
              tileEl.setAttribute('opacity', '1');
            };
            probe.src = targetSrc;
            this.dom.layerTiles.appendChild(tileEl);
          }
        }
      }
    },

    // ==========================================================================
    // 11. Pure Deterministic Render Function render(t) & window.seek(t)
    // ==========================================================================
    _advanceTime(dt) {
      if (this.mode === 'gallery' || this.mode === 'play' || this.mode === 'film') {
        this.time += dt;
        if (this.mode === 'film' && this.time >= this.filmDuration) {
          this.setMode('gallery');
        }
      } else if (this.mode === 'talk') {
        // In talk mode, advance within current beat and gently loop hold window until presenter presses ->
        const beat = this.beats[this.currentBeatIdx] || this.beats[0];
        if (beat) {
          this.beatLocalTime += dt;
          const holdStart = beat.duration * 0.72;
          const holdSpan = Math.max(1.5, beat.duration * 0.28);
          let effectiveLocal = this.beatLocalTime;
          if (effectiveLocal > beat.duration) {
            effectiveLocal = holdStart + ((effectiveLocal - holdStart) % holdSpan);
          }
          this.time = beat.t0 + effectiveLocal;
        }
      }
    },

    render(t) {
      this.time = t;
      this.resetParticlesForFrame();
      this.resetSceneOverlays();

      // 1. Always-on Breath Cycle (5s period normal; 2.1s shallow in ★6 after t=490s in film)
      const period = Ease.lerp(5.0, 2.1, this.breath.shallow);
      const amp = Ease.lerp(1.0, 0.42, this.breath.shallow);
      const bWave = Math.sin((2 * Math.PI * t) / period);
      this.breath.phase = (t % period) / period;
      this.breath.inhale = 0.5 + 0.5 * bWave;
      this.breath.wallFlexY = bWave * 1.45 * amp;

      // Update air space brightness with breath
      if (this.airWashRect) {
        const airOp = 0.14 + 0.22 * this.breath.inhale * amp;
        this.airWashRect.setAttribute('opacity', airOp.toFixed(3));
      }

      // 2. Always-on Paper Life: slow 20s light sweep across the paper grain (§2.2, §5)
      if (this.dom.paperLightSweep) {
        const sweepU = (t % 20.0) / 20.0;
        const sweepX = Ease.lerp(-950, 1450, sweepU);
        this.dom.paperLightSweep.setAttribute('x', sweepX.toFixed(1));
      }

      // 3. Evaluate Active Mode
      if (this.mode === 'gallery') {
        this.breath.shallow = 0;
        this.setCameraBox(MANIFEST.overviewViewBox, false);
        if (window.LivingAmbient) {
          window.LivingAmbient.render(t % 60.0, this);
        }
      } else if (this.mode === 'play') {
        this.breath.shallow = 0;
        this.setCameraBox([-25, 160, 620, 480], false);
        if (window.LivingAmbient) {
          window.LivingAmbient.render(t % 60.0, this);
        }
        if (window.LivingPlay) {
          window.LivingPlay.render(t, this);
        }
      } else {
        // 'talk' or 'film' mode: find beat containing t
        const beat = this._findBeatAtTime(t);
        if (beat) {
          this.currentBeatIdx = this.beats.indexOf(beat);
          const localU = Ease.sub(t, beat.t0, beat.t1);
          const localSec = t - beat.t0;

          // Update progress thread & speaker chip on section change
          this._updateProgressAndSpeaker(beat, localSec);

          // Camera interpolation for this beat
          const fromCam = beat.camFrom || beat.cam || MANIFEST.overviewViewBox;
          const toCam = beat.camTo || beat.cam || fromCam;
          const camEaseU = Ease.clamp(localSec / Math.min(3.2, beat.duration * 0.45), 0, 1);
          const box = Ease.lerpBox(fromCam, toCam, camEaseU);
          this.setCameraBox(box, Boolean(beat.em));

          // Ambient background micro-life (breathing dust + capillary RBCs) unless bullet-time
          const bulletSlow = beat.bulletTime ? 0.08 : 1.0;
          if (window.LivingAmbient) {
            window.LivingAmbient.renderBackgroundLife(t * bulletSlow, this);
          }

          // Call Scene's deterministic beat renderer
          const scene = this.scenes.find((s) => s.id === beat.sceneId);
          if (scene && typeof scene.renderBeat === 'function') {
            scene.renderBeat(beat, localU, localSec, t, this);
          }
        }
      }

      // 4. Render Scientist's Desk Devices (Loupe, Turret, Stopwatch, pH Gauge, Size Tags, Calendar)
      if (window.LivingDevices) {
        window.LivingDevices.render(t, this);
      }
    },

    _findBeatAtTime(t) {
      if (!this.beats.length) return null;
      const clamped = Ease.clamp(t, 0, this.filmDuration - 0.001);
      for (let i = 0; i < this.beats.length; i++) {
        const b = this.beats[i];
        if (clamped >= b.t0 && clamped < b.t1) return b;
      }
      return this.beats[this.beats.length - 1];
    },

    _updateProgressAndSpeaker(beat, localSec) {
      const secKey = String(beat.sectionNum);
      if (this.dom.statusText) {
        const modeLabel = this.mode === 'film' ? 'Film' : 'Talk';
        this.dom.statusText.textContent = `${modeLabel} · ${beat.id}: ${beat.label || beat.sceneTitle}`;
      }

      // Highlight bottom progress thread dot
      const dots = this.dom.progressThread.querySelectorAll('.prog-dot');
      dots.forEach((d) => {
        d.classList.toggle('current', d.getAttribute('data-sec') === secKey);
      });

      // Speaker Chip at the start of each section (fades after 4s, §3)
      if (beat.indexInScene === 0 && localSec < 4.0 && beat.speakerChipText) {
        const chip = this.dom.speakerChip;
        chip.textContent = beat.speakerChipText;
        chip.style.borderColor = beat.color;
        chip.style.color = beat.color;
        chip.classList.add('visible');
        if (localSec < 0.7) chip.classList.add('stamp-ring');
        else chip.classList.remove('stamp-ring');
      } else {
        this.dom.speakerChip.classList.remove('visible', 'stamp-ring');
      }
    },

    // ==========================================================================
    // 12. Mode Switching, Navigation & Keyboard Controls (§3)
    // ==========================================================================
    setMode(newMode) {
      this.mode = newMode;
      this.paused = false;

      const isPlay = newMode === 'play';
      document.getElementById('play-hud').classList.toggle('visible', isPlay);
      document.getElementById('btn-play').classList.toggle('active', isPlay);
      document.getElementById('btn-auto').classList.toggle('active', newMode === 'film');
      this.dom.stage.classList.toggle('play-cursor-hidden', isPlay);
      this.dom.playCursor.style.display = isPlay ? '' : 'none';

      if (newMode === 'gallery') {
        this.dom.statusText.textContent = 'Gallery · Circle of Life';
        this.dom.modeDot.style.background = '#1E9B6B';
        this.dom.speakerChip.classList.remove('visible');
        if (window.LivingDevices) window.LivingDevices.hideSceneProps();
      } else if (newMode === 'play') {
        this.dom.statusText.textContent = 'Play · Feed the Macrophage';
        this.dom.modeDot.style.background = '#E07B39';
        if (window.LivingDevices) window.LivingDevices.hideSceneProps();
      } else if (newMode === 'film') {
        this.dom.modeDot.style.background = '#C0392B';
        if (this.time >= this.filmDuration - 1) this.time = 0;
      } else if (newMode === 'talk') {
        this.dom.modeDot.style.background = '#1F58C8';
      }
    },

    jumpToBeat(idx) {
      if (!this.beats.length) return;
      this.currentBeatIdx = Ease.clamp(idx, 0, this.beats.length - 1);
      const b = this.beats[this.currentBeatIdx];
      this.beatLocalTime = 0;
      this.time = b.t0;
      if (this.mode !== 'talk' && this.mode !== 'film') {
        this.setMode('talk');
      }
      this.dom.progressThread.classList.add('active-poke');
      clearTimeout(this._pokeTimer);
      this._pokeTimer = setTimeout(() => this.dom.progressThread.classList.remove('active-poke'), 2500);
    },

    jumpToSection(secKey) {
      const idx = this.beats.findIndex((b) => String(b.sectionNum) === String(secKey));
      if (idx >= 0) {
        this.setMode('talk');
        this.jumpToBeat(idx);
      }
    },

    nextBeat() {
      if (this.mode === 'gallery') {
        this.setMode('talk');
        this.jumpToBeat(0);
        return;
      }
      if (this.currentBeatIdx < this.beats.length - 1) {
        this.jumpToBeat(this.currentBeatIdx + 1);
      } else {
        this.setMode('gallery');
      }
    },

    prevBeat() {
      if (this.mode === 'gallery') {
        this.setMode('talk');
        this.jumpToBeat(this.beats.length - 1);
        return;
      }
      this.jumpToBeat(Math.max(0, this.currentBeatIdx - 1));
    },

    seek(t) {
      this.paused = true;
      if (this.mode === 'talk' || (this.mode !== 'gallery' && this.mode !== 'play')) {
        this.mode = 'film';
      }
      this.render(t);
    },

    _initControls() {
      // Modern <dialog closedby="any"> fallback from modern-web-guidance: light-dismiss-a-dialog
      const dialog = this.dom.helpDialog;
      if (dialog && !('closedBy' in HTMLDialogElement.prototype)) {
        dialog.addEventListener('click', (event) => {
          if (event.target !== dialog) return;
          const rect = dialog.getBoundingClientRect();
          const isDialogContent = (
            rect.top <= event.clientY &&
            event.clientY <= rect.top + rect.height &&
            rect.left <= event.clientX &&
            event.clientX <= rect.left + rect.width
          );
          if (isDialogContent) return;
          dialog.close();
        });
      }

      const toggleHelp = () => {
        if (!dialog) return;
        if (dialog.open) {
          dialog.close();
        } else {
          dialog.showModal();
          clearTimeout(this._helpAutoClose);
          this._helpAutoClose = setTimeout(() => {
            if (dialog.open) dialog.close();
          }, 5000);
        }
      };

      // HUD buttons
      document.getElementById('btn-loupe').addEventListener('click', (e) => {
        e.stopPropagation();
        if (window.LivingDevices) window.LivingDevices.toggleLoupe();
      });
      document.getElementById('btn-auto').addEventListener('click', (e) => {
        e.stopPropagation();
        this.setMode(this.mode === 'film' ? 'talk' : 'film');
      });
      document.getElementById('btn-play').addEventListener('click', (e) => {
        e.stopPropagation();
        this.setMode(this.mode === 'play' ? 'gallery' : 'play');
      });
      document.getElementById('btn-sound').addEventListener('click', (e) => {
        e.stopPropagation();
        if (window.LivingDevices) window.LivingDevices.toggleSound();
      });
      document.getElementById('btn-help').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleHelp();
      });

      // Progress dots click
      this.dom.progressThread.querySelectorAll('.prog-dot').forEach((dot) => {
        dot.addEventListener('click', (e) => {
          e.stopPropagation();
          this.jumpToSection(dot.getAttribute('data-sec'));
        });
      });

      // Stage click advances beat in Talk mode (unless Loupe dive or Play mode handles it)
      this.dom.stage.addEventListener('click', (e) => {
        if (this.mode === 'play') return;
        if (window.LivingDevices && window.LivingDevices.handleStageClick(e, this)) return;
        if (this.mode === 'talk') {
          this.nextBeat();
        }
      });

      // Keyboard Shortcuts (§3 Table)
      window.addEventListener('keydown', (e) => {
        if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
        const k = e.key;

        if (k === 'ArrowRight' || k === ' ') {
          e.preventDefault();
          this.nextBeat();
        } else if (k === 'ArrowLeft') {
          e.preventDefault();
          this.prevBeat();
        } else if (k === 'Escape' || k === '0') {
          if (dialog && dialog.open) return;
          this.setMode('gallery');
        } else if (k >= '1' && k <= '6') {
          this.jumpToSection(k);
        } else if (k === '7') {
          this.jumpToSection('2.7');
        } else if (k === 'o' || k === 'O') {
          this.jumpToSection('0');
        } else if (k === 'e' || k === 'E') {
          this.jumpToSection('finale');
        } else if (k === 'l' || k === 'L') {
          if (window.LivingDevices) window.LivingDevices.toggleLoupe();
        } else if (k === 'a' || k === 'A') {
          this.setMode(this.mode === 'film' ? 'talk' : 'film');
        } else if (k === 'p' || k === 'P') {
          this.paused = !this.paused;
          if (this.paused) {
            this.dom.statusText.textContent += ' [PAUSED]';
          }
        } else if (k === 'g' || k === 'G') {
          this.setMode(this.mode === 'play' ? 'gallery' : 'play');
        } else if (k === 'f' || k === 'F') {
          if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {});
          } else {
            document.exitFullscreen().catch(() => {});
          }
        } else if (k === 'h' || k === 'H' || k === '?') {
          toggleHelp();
        } else if (k === 'm' || k === 'M') {
          if (window.LivingDevices) window.LivingDevices.toggleSound();
        } else if (this.mode === 'play' && window.LivingPlay) {
          window.LivingPlay.handleKey(k);
        }
      });
    }
  };

  // Expose globally for scenes, devices, play mode, and CDP video exporter
  window.LivingEngine = Engine;
  window.seek = (t) => Engine.seek(t);
  window.setMode = (m) => Engine.setMode(m);

  window.addEventListener('DOMContentLoaded', () => {
    Engine.init();
  });
})();
