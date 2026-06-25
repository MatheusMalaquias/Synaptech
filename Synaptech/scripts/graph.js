// ── OBSIDIAN-STYLE GRAPH ANIMATION ──
// Shared renderer used by mind-canvas (Home) and page-hero-canvas (Solutions/Contact)

(function initGraph() {
  const ACCENT = { r: 159, g: 103, b: 255 };
  const CYAN   = { r:   6, g: 182, b: 212 };
  const GREY   = { r: 100, g: 120, b: 160 };

  function rnd(a, b) { return a + Math.random() * (b - a); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  function buildGraph(W, H, hubCount, satCount) {
    // Hub nodes — larger, slower, become graph "centers"
    const hubs = Array.from({ length: hubCount }, (_, i) => ({
      x: W * 0.12 + Math.random() * W * 0.76,
      y: H * 0.12 + Math.random() * H * 0.76,
      vx: (Math.random() - 0.5) * 0.18,
      vy: (Math.random() - 0.5) * 0.18,
      r: rnd(6, 13),
      pulse: Math.random() * Math.PI * 2,
      ps: rnd(0.015, 0.028),
      col: i % 3 === 0 ? CYAN : ACCENT,
      hub: true,
    }));

    // Satellite nodes — small, faster
    const sats = Array.from({ length: satCount }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.55,
      vy: (Math.random() - 0.5) * 0.55,
      r: rnd(1.8, 4),
      pulse: Math.random() * Math.PI * 2,
      ps: rnd(0.025, 0.05),
      col: Math.random() < 0.5 ? ACCENT : GREY,
      hub: false,
    }));

    return { nodes: [...hubs, ...sats], pulses: [], frame: 0, cc: 0, sc: 0, nc: 0, ct: 0, st: 0, nt: 0 };
  }

  function drawGraph(canvas, state, counterEls, opts) {
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const { hubDist = 220, satDist = 90, dimmed = false } = opts || {};
    const alpha_scale = dimmed ? 0.45 : 1;

    ctx.clearRect(0, 0, W, H);
    const { nodes, pulses } = state;
    const hubs = nodes.filter(n => n.hub);
    const sats = nodes.filter(n => !n.hub);
    let cons = 0;

    // Hub ↔ hub edges
    for (let i = 0; i < hubs.length; i++) {
      for (let j = i + 1; j < hubs.length; j++) {
        const dx = hubs[i].x - hubs[j].x, dy = hubs[i].y - hubs[j].y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < hubDist) {
          cons++;
          const a = (1 - d / hubDist) * 0.55 * alpha_scale;
          const c = hubs[i].col;
          ctx.beginPath();
          ctx.strokeStyle = `rgba(${c.r},${c.g},${c.b},${a})`;
          ctx.lineWidth = 1.1;
          ctx.moveTo(hubs[i].x, hubs[i].y);
          ctx.lineTo(hubs[j].x, hubs[j].y);
          ctx.stroke();
          if (Math.random() < 0.003) state.pulses.push({ from: hubs[i], to: hubs[j], t: 0, sp: rnd(0.006, 0.013) });
        }
      }
    }

    // Sat ↔ hub edges
    for (const s of sats) {
      for (const h of hubs) {
        const dx = s.x - h.x, dy = s.y - h.y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < satDist) {
          cons++;
          const a = (1 - d / satDist) * 0.22 * alpha_scale;
          const c = h.col;
          ctx.beginPath();
          ctx.strokeStyle = `rgba(${c.r},${c.g},${c.b},${a})`;
          ctx.lineWidth = 0.5;
          ctx.moveTo(s.x, s.y);
          ctx.lineTo(h.x, h.y);
          ctx.stroke();
        }
      }
    }

    // Pulses
    const alive = [];
    for (const pu of pulses) {
      pu.t += pu.sp;
      if (pu.t >= 1) continue;
      alive.push(pu);
      const px = lerp(pu.from.x, pu.to.x, pu.t);
      const py = lerp(pu.from.y, pu.to.y, pu.t);
      const c = pu.from.col;
      const g = ctx.createRadialGradient(px, py, 0, px, py, 5);
      g.addColorStop(0, `rgba(${c.r},${c.g},${c.b},${0.9 * alpha_scale})`);
      g.addColorStop(1, `rgba(${c.r},${c.g},${c.b},0)`);
      ctx.beginPath(); ctx.arc(px, py, 5, 0, Math.PI * 2);
      ctx.fillStyle = g; ctx.fill();
    }
    state.pulses = alive;

    // Draw all nodes
    for (const n of nodes) {
      n.pulse += n.ps;
      const gw = (Math.sin(n.pulse) + 1) / 2;
      const c = n.col;

      if (n.hub) {
        const outerR = n.r * (1.7 + gw * 0.5);
        // Glow
        const g = ctx.createRadialGradient(n.x, n.y, n.r * 0.4, n.x, n.y, outerR * 1.9);
        g.addColorStop(0, `rgba(${c.r},${c.g},${c.b},${(0.16 + gw * 0.1) * alpha_scale})`);
        g.addColorStop(1, `rgba(${c.r},${c.g},${c.b},0)`);
        ctx.beginPath(); ctx.arc(n.x, n.y, outerR * 1.9, 0, Math.PI * 2);
        ctx.fillStyle = g; ctx.fill();
        // Ring
        ctx.beginPath(); ctx.arc(n.x, n.y, outerR, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(${c.r},${c.g},${c.b},${(0.22 + gw * 0.15) * alpha_scale})`;
        ctx.lineWidth = 0.8; ctx.stroke();
        // Core
        const core = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r);
        core.addColorStop(0, `rgba(255,255,255,${(0.9 + gw * 0.1) * alpha_scale})`);
        core.addColorStop(0.45, `rgba(${c.r},${c.g},${c.b},${0.9 * alpha_scale})`);
        core.addColorStop(1, `rgba(${c.r},${c.g},${c.b},${0.6 * alpha_scale})`);
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = core; ctx.fill();
      } else {
        // Satellite
        const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 3);
        g.addColorStop(0, `rgba(${c.r},${c.g},${c.b},${(0.5 + gw * 0.3) * alpha_scale})`);
        g.addColorStop(1, `rgba(${c.r},${c.g},${c.b},0)`);
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r * 3, 0, Math.PI * 2);
        ctx.fillStyle = g; ctx.fill();
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${c.r},${c.g},${c.b},${(0.65 + gw * 0.3) * alpha_scale})`;
        ctx.fill();
      }

      // Move & bounce
      n.x += n.vx; n.y += n.vy;
      const pad = n.r * 2;
      if (n.x < pad || n.x > W - pad) n.vx *= -1;
      if (n.y < pad || n.y > H - pad) n.vy *= -1;
    }

    // Counters
    state.frame++;
    if (state.frame % 45 === 0) {
      state.ct = cons;
      state.st = Math.floor(rnd(10, 42));
      state.nt = nodes.length;
    }
    state.cc = Math.round(lerp(state.cc, state.ct, 0.1));
    state.sc = Math.round(lerp(state.sc, state.st, 0.07));
    state.nc = Math.round(lerp(state.nc, state.nt, 0.1));
    if (counterEls) {
      if (counterEls[0]) counterEls[0].textContent = state.cc;
      if (counterEls[1]) counterEls[1].textContent = state.sc;
      if (counterEls[2]) counterEls[2].textContent = state.nc;
    }
  }

  function mountCanvas(canvasId, opts) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const parent = canvas.parentElement;
    let state, animId;

    function resize() {
      canvas.width  = parent.offsetWidth  || 600;
      canvas.height = parent.offsetHeight || 380;
      state = buildGraph(canvas.width, canvas.height, opts.hubs || 5, opts.sats || 28);
    }

    const counterEls = (opts.counters || []).map(id => document.getElementById(id));

    let running = false;
    function loop() {
      drawGraph(canvas, state, counterEls, opts);
      animId = requestAnimationFrame(loop);
    }

    // Only run when visible
    const target = canvas.closest('[data-graph-section]') || canvas.parentElement;
    const io = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !running) {
        running = true; loop();
      } else if (!entries[0].isIntersecting && running) {
        running = false;
        cancelAnimationFrame(animId); animId = null;
      }
    }, { threshold: 0.05 });
    io.observe(target);

    window.addEventListener('resize', () => { resize(); });
    resize();
  }

  // ── Mount: Second Mind (Home) ──
  mountCanvas('mind-canvas', {
    hubs: 6, sats: 32,
    hubDist: 230, satDist: 95,
    counters: ['mind-connections', 'mind-signals', 'mind-nodes'],
    dimmed: false,
  });

  // ── Mount: Page hero canvas (Solutions / Contact) ──
  mountCanvas('page-hero-canvas', {
    hubs: 5, sats: 24,
    hubDist: 260, satDist: 110,
    dimmed: true,
  });

})();