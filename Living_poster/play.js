/**
 * play.js — Play Mode · "Feed the Macrophage" (§6 · Key G)
 * - Cursor (#play-cursor) becomes a tiny ink bacterium with a wiggling flagellum (B),
 *   a sharp silica crystal (S), or a long asbestos needle (X).
 * - Bringing the cursor near the macrophage's leading membrane causes vector pseudopod
 *   tendrils in #layer-play to reach toward the cursor with a damped spring lag.
 * - Clicking closes the tendrils and triggers the corresponding biological fate:
 *   - Bacterium (B): engulfed -> rides red_route -> digested in phagolysosome ("eaten: N")
 *   - Silica (S): engulfed -> tears phagolysosome membrane -> spins NLRP3 wheel ("eaten: N · lysed: M")
 *   - Asbestos (X): tendrils strain and fail to close -> frustrated phagocytosis ("frustrated: K")
 */
(function () {
  'use strict';

  const LivingPlay = {
    engine: null,
    cargo: 'bacterium', // 'bacterium' | 'silica' | 'asbestos'
    cursor: { x: 95, y: 392, tx: 95, ty: 392 },
    tendrilTip: { x: 145, y: 392, vx: 0, vy: 0 },
    counts: {
      eaten: 0,
      lysed: 0,
      frustrated: 0
    },
    activeEvents: [],

    init(engine) {
      this.engine = engine;
      const E = engine;
      const playLayer = E.dom.layerPlay;
      const cursorGrp = E.dom.playCursor;
      if (!playLayer || !cursorGrp) return;

      playLayer.innerHTML = '';
      cursorGrp.innerHTML = '';

      // Reactive pseudopod tendrils reaching from leading membrane toward cursor
      this.tendrilUpper = E.createSvgEl('path', {
        fill: '#FAD8C5',
        'fill-opacity': '0.68',
        stroke: '#C07A66',
        'stroke-width': '2.8',
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round'
      });
      this.tendrilLower = E.createSvgEl('path', {
        fill: '#FAD8C5',
        'fill-opacity': '0.68',
        stroke: '#C07A66',
        'stroke-width': '2.8',
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round'
      });
      this.targetRing = E.createSvgEl('circle', {
        r: '16',
        fill: 'none',
        stroke: '#E07B39',
        'stroke-width': '1.2',
        'stroke-dasharray': '3 2.5',
        opacity: '0.65'
      });
      this.eventsGroup = E.createSvgEl('g', { id: 'play-events-group' });

      playLayer.appendChild(this.tendrilUpper);
      playLayer.appendChild(this.tendrilLower);
      playLayer.appendChild(this.targetRing);
      playLayer.appendChild(this.eventsGroup);

      // Build custom cursor graphic inside #play-cursor
      this.cursorFlagellum = E.createSvgEl('path', {
        fill: 'none',
        stroke: '#4E5A16',
        'stroke-width': '1.4',
        'stroke-linecap': 'round'
      });
      this.cursorBody = E.createSvgEl('g');
      cursorGrp.appendChild(this.cursorFlagellum);
      cursorGrp.appendChild(this.cursorBody);

      this.scoreEl = document.getElementById('play-score');
      this.kbdEls = document.querySelectorAll('#play-hud kbd[data-cargo]');

      this.kbdEls.forEach((kbd) => {
        kbd.style.cursor = 'pointer';
        kbd.addEventListener('click', (ev) => {
          ev.stopPropagation();
          this.setCargo(kbd.getAttribute('data-cargo'));
        });
      });

      this._updateCursorGraphic();

      // Pointer tracking & click-to-feed on #stage
      const stage = E.dom.stage;
      stage.addEventListener('pointermove', (ev) => {
        if (E.mode !== 'play') return;
        const pt = this._clientToPoster(ev.clientX, ev.clientY);
        this.cursor.tx = pt.x;
        this.cursor.ty = pt.y;
      });

      stage.addEventListener('click', (ev) => {
        if (E.mode !== 'play') return;
        if (ev.target && ev.target.closest && ev.target.closest('#hud')) return;
        const pt = this._clientToPoster(ev.clientX, ev.clientY);
        this.cursor.tx = pt.x;
        this.cursor.ty = pt.y;
        this.triggerFeed(pt.x, pt.y);
      });
    },

    _clientToPoster(clientX, clientY) {
      const stage = this.engine && this.engine.dom.stage;
      if (!stage) return { x: 95, y: 392 };
      const rect = stage.getBoundingClientRect();
      const [vx, vy, vw, vh] = this.engine.camera.currentBox || [-25, 160, 620, 480];
      const x = vx + ((clientX - rect.left) / Math.max(1, rect.width)) * vw;
      const y = vy + ((clientY - rect.top) / Math.max(1, rect.height)) * vh;
      return { x, y };
    },

    handleKey(key) {
      const k = String(key).toLowerCase();
      if (k === 'b') this.setCargo('bacterium');
      else if (k === 's') this.setCargo('silica');
      else if (k === 'x') this.setCargo('asbestos');
    },

    setCargo(type) {
      this.cargo = type;
      if (this.kbdEls) {
        this.kbdEls.forEach((kbd) => {
          kbd.classList.toggle('active-food', kbd.getAttribute('data-cargo') === type);
        });
      }
      this._updateCursorGraphic();
    },

    setPayload(type) {
      this.setCargo(type);
    },

    _updateCursorGraphic() {
      if (!this.cursorBody) return;
      if (this.cargo === 'bacterium') {
        this.cursorBody.innerHTML = `
          <g transform="rotate(-14)">
            <ellipse cx="0" cy="0" rx="11" ry="5.2" fill="#8C9A3A" stroke="#4E5A16" stroke-width="1.3"/>
            <ellipse cx="-3" cy="-1.4" rx="4.5" ry="1.6" fill="#B5C45C" opacity="0.75"/>
          </g>
        `;
        this.cursorFlagellum.setAttribute('opacity', '1');
      } else if (this.cargo === 'silica') {
        this.cursorBody.innerHTML = `
          <polygon points="-11,-6 3,-12 13,-2 7,11 -9,8" fill="#D8ECF8" stroke="#3B5360" stroke-width="1.5"/>
          <polyline points="-6,-3 2,-7 8,-1" fill="none" stroke="#FFFFFF" stroke-width="1.3"/>
        `;
        this.cursorFlagellum.setAttribute('opacity', '0');
      } else if (this.cargo === 'asbestos') {
        this.cursorBody.innerHTML = `
          <g transform="rotate(-5)">
            <line x1="-38" y1="0" x2="38" y2="0" stroke="#B88E44" stroke-width="3.8" stroke-linecap="round"/>
            <line x1="-38" y1="-0.9" x2="38" y2="-0.9" stroke="#F5E4B8" stroke-width="1.1"/>
            <rect x="-22" y="-3.2" width="6" height="6.4" rx="1" fill="#7A5618"/>
            <rect x="12" y="-3.2" width="6" height="6.4" rx="1" fill="#7A5618"/>
          </g>
        `;
        this.cursorFlagellum.setAttribute('opacity', '0');
      }
    },

    _updateScoreText() {
      if (!this.scoreEl) return;
      const parts = [`eaten: ${this.counts.eaten}`];
      if (this.counts.lysed > 0) parts.push(`lysed: ${this.counts.lysed}`);
      if (this.counts.frustrated > 0) parts.push(`frustrated: ${this.counts.frustrated}`);
      this.scoreEl.textContent = parts.join(' · ');
    },

    triggerFeed(x, y) {
      if (!this.engine || !this.eventsGroup) return;
      const E = this.engine;
      const t0 = E.time;

      if (this.cargo === 'bacterium') {
        this.counts.eaten++;
        this._updateScoreText();
        if (window.LivingDevices) window.LivingDevices.playGlassyClick(1850);

        const el = E.createSvgEl('g');
        el.innerHTML = `
          <circle cx="0" cy="0" r="14" fill="#FAD8C5" fill-opacity="0.45" stroke="#C0392B" stroke-width="1.8"/>
          <ellipse cx="0" cy="0" rx="9" ry="4.2" fill="#8C9A3A" stroke="#4E5A16" stroke-width="1.1" transform="rotate(-18)"/>
        `;
        this.eventsGroup.appendChild(el);
        this.activeEvents.push({ type: 'bacterium', t0, duration: 4.0, x0: x, y0: y, el });
      } else if (this.cargo === 'silica') {
        this.counts.lysed++;
        this._updateScoreText();
        if (window.LivingDevices) window.LivingDevices.playGlassyClick(2650);

        const el = E.createSvgEl('g');
        el.innerHTML = `
          <circle cx="0" cy="0" r="15" fill="#E4D3F3" fill-opacity="0.45" stroke="#7A3FB5" stroke-width="1.8" stroke-dasharray="4 2"/>
          <polygon points="-9,-5 2,-10 11,-2 6,9 -7,7" fill="#D8ECF8" stroke="#3B5360" stroke-width="1.3"/>
        `;
        this.eventsGroup.appendChild(el);
        this.activeEvents.push({ type: 'silica', t0, duration: 4.2, x0: x, y0: y, el });
      } else if (this.cargo === 'asbestos') {
        this.counts.frustrated++;
        this._updateScoreText();
        if (window.LivingDevices) window.LivingDevices.playGlassyClick(1250);

        const el = E.createSvgEl('g');
        el.innerHTML = `
          <line x1="-36" y1="0" x2="36" y2="0" stroke="#B88E44" stroke-width="3.6" stroke-linecap="round"/>
          <path d="M-18,-10 C-6,-3 6,-3 18,-10" fill="none" stroke="#C81D63" stroke-width="2.8" stroke-linecap="round"/>
        `;
        this.eventsGroup.appendChild(el);
        this.activeEvents.push({ type: 'asbestos', t0, duration: 4.2, x0: x, y0: y, el });
      }
    },

    render(t, engine) {
      if (!this.tendrilUpper) this.init(engine);
      if (!this.tendrilUpper) return;
      const E = engine.Ease;

      // 1. Smoothly damp cursor position & wiggle bacterium flagellum
      this.cursor.x += (this.cursor.tx - this.cursor.x) * 0.32;
      this.cursor.y += (this.cursor.ty - this.cursor.y) * 0.32;
      engine.dom.playCursor.setAttribute(
        'transform',
        `translate(${this.cursor.x.toFixed(1)} ${this.cursor.y.toFixed(1)})`
      );

      if (this.cargo === 'bacterium') {
        const w1 = Math.sin(t * 18) * 4.5;
        const w2 = Math.cos(t * 18) * 4.5;
        this.cursorFlagellum.setAttribute(
          'd',
          `M-11,2 Q-19,${(2 + w1).toFixed(1)} -26,2 T-36,${(2 + w2).toFixed(1)}`
        );
      }

      // 2. Pseudopod tendrils on leading membrane (x ~ 142, y ~ 290..494) reaching toward cursor with damped lag
      const anchorX = 142;
      const anchorY = E.clamp(this.cursor.y, 300, 485);
      const dist = Math.hypot(this.cursor.x - anchorX, this.cursor.y - anchorY);
      const reachFactor = E.clamp(1 - dist / 240, 0.18, 0.92);
      const goalX = E.lerp(anchorX, this.cursor.x, reachFactor);
      const goalY = E.lerp(anchorY, this.cursor.y, reachFactor);

      this.tendrilTip.vx = (this.tendrilTip.vx + (goalX - this.tendrilTip.x) * 0.2) * 0.72;
      this.tendrilTip.vy = (this.tendrilTip.vy + (goalY - this.tendrilTip.y) * 0.2) * 0.72;
      this.tendrilTip.x += this.tendrilTip.vx;
      this.tendrilTip.y += this.tendrilTip.vy;

      const cupSpread = 12 + (1 - reachFactor) * 14;
      const ux = this.tendrilTip.x;
      const uy = this.tendrilTip.y - cupSpread;
      const lx = this.tendrilTip.x;
      const ly = this.tendrilTip.y + cupSpread;

      this.tendrilUpper.setAttribute(
        'd',
        `M${anchorX},${anchorY - 28} Q${((anchorX + ux) * 0.5 - 10).toFixed(1)},${(uy - 12).toFixed(1)} ${ux.toFixed(1)},${uy.toFixed(1)} Q${((anchorX + ux) * 0.5).toFixed(1)},${(uy + 6).toFixed(1)} ${anchorX},${anchorY - 8} Z`
      );
      this.tendrilLower.setAttribute(
        'd',
        `M${anchorX},${anchorY + 28} Q${((anchorX + lx) * 0.5 - 10).toFixed(1)},${(ly + 12).toFixed(1)} ${lx.toFixed(1)},${ly.toFixed(1)} Q${((anchorX + lx) * 0.5).toFixed(1)},${(ly - 6).toFixed(1)} ${anchorX},${anchorY + 8} Z`
      );
      this.targetRing.setAttribute('cx', this.tendrilTip.x.toFixed(1));
      this.targetRing.setAttribute('cy', this.tendrilTip.y.toFixed(1));

      // 3. Step active feed events
      for (let i = this.activeEvents.length - 1; i >= 0; i--) {
        const ev = this.activeEvents[i];
        const u = (t - ev.t0) / ev.duration;
        if (u >= 1 || u < 0) {
          if (ev.el && ev.el.parentNode) ev.el.parentNode.removeChild(ev.el);
          this.activeEvents.splice(i, 1);
          continue;
        }

        if (ev.type === 'bacterium') {
          // Ride red_route to phagolysosome (622, 665) and crumble
          const pt = engine.pointOnPath('red_route', u);
          const bx = u < 0.2 ? E.lerp(ev.x0, pt.x, u / 0.2) : pt.x;
          const by = u < 0.2 ? E.lerp(ev.y0, pt.y, u / 0.2) : pt.y;
          const sc = u > 0.75 ? Math.max(0.1, 1 - (u - 0.75) * 3.5) : 1.0;
          ev.el.setAttribute('transform', `translate(${bx.toFixed(1)} ${by.toFixed(1)}) scale(${sc.toFixed(2)})`);
          engine.dashDraw('red_route', u, 0.85);
          if (u > 0.65) {
            engine.watercolourBloom({ cx: 622, cy: 665, r: 58, color: '#7A3FB5', opacity: 0.6 });
            engine.stateCrossFade('killing.bacterium', ((u - 0.65) / 0.35) * 3.0);
          }
        } else if (ev.type === 'silica') {
          // Engulfed to (320, 480) -> tears membrane & spins NLRP3 wheel
          const moveU = E.smoother(E.clamp(u / 0.5, 0, 1));
          const sx = E.lerp(ev.x0, 320, moveU);
          const sy = E.lerp(ev.y0, 460, moveU);
          ev.el.setAttribute('transform', `translate(${sx.toFixed(1)} ${sy.toFixed(1)}) rotate(${(u * 140).toFixed(0)})`);
          if (u > 0.45) {
            const tearU = E.clamp((u - 0.45) / 0.45, 0, 1);
            engine.stateCrossFade('particles.silica_membrane', tearU * 2.0);
            engine.stateCrossFade('particles.nlrp3', tearU * 2.0);
            engine.spawnParticle('ros', sx + 14, sy - 8, 1.2, t * 60, 0.9);
            engine.spawnParticle('kplus', sx - 12, sy + 10, 1.2, 0, 0.9);
          }
        } else if (ev.type === 'asbestos') {
          // Tendrils strain 3 times and fail to close; ROS leak out
          const strain = Math.sin(u * Math.PI * 3) * 5;
          ev.el.setAttribute('transform', `translate(${ev.x0.toFixed(1)} ${(ev.y0 + strain).toFixed(1)})`);
          engine.stateCrossFade('particles.asbestos_hood', Math.abs(Math.sin(u * Math.PI * 3)) * 2.0);
          engine.spawnParticle('ros', ev.x0 - 8, ev.y0 + 12, 1.15, t * 50, 0.9);
          engine.spawnParticle('hplus', ev.x0 + 10, ev.y0 + 14, 1.15, 0, 0.9);
        }
      }
    }
  };

  window.LivingPlay = LivingPlay;
  window.PlayMode = LivingPlay;
})();
