/* PingSpace Y2K: tacky 2000s web effects. Lightning bolts strike at random, spinning
 * NEW!/HOT!/OMG!! starbursts pop up, sparkles twinkle and shooting stars streak across
 * the background. Click-through, pauses when the window is hidden, and switches off
 * under reduced motion. Flashes are soft and never faster than one bolt every few
 * seconds (well under the 3-per-second photosensitivity limit).
 *
 * Page config (optional), set before this script loads:
 *   window.Y2K_CONFIG = { backZ: 0, frontZ: 30 }   // layer for sparkles/stars, layer for bolts/badges
 */
(function () {
  var mq = window.matchMedia;
  if (mq && mq('(prefers-reduced-motion: reduce)').matches) return;
  var cfg = window.Y2K_CONFIG || {};
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function pick(a) { return a[Math.random() * a.length | 0]; }

  var css = document.createElement('style');
  css.textContent =
    '.y2k-layer{position:fixed;inset:0;width:100%;height:100%;pointer-events:none}' +
    '.y2k-flash{position:fixed;inset:0;pointer-events:none;background:#fff;opacity:0;transition:opacity .12s}' +
    '.y2k-burst{position:fixed;pointer-events:none;width:96px;height:96px;display:flex;align-items:center;justify-content:center;' +
      'font:bold 17px Impact,"Arial Black",sans-serif;color:#d40000;text-align:center;line-height:1;letter-spacing:.5px;' +
      'text-shadow:1px 1px 0 #fff;animation:y2k-pop 2.6s ease-in-out forwards}' +
    '.y2k-burst::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(circle,#fffb8a,#ffe600 55%,#ff9a00);' +
      'clip-path:polygon(50% 0,59% 18%,75% 7%,74% 26%,93% 25%,82% 41%,100% 50%,82% 59%,93% 75%,74% 74%,75% 93%,59% 82%,50% 100%,41% 82%,25% 93%,26% 74%,7% 75%,18% 59%,0 50%,18% 41%,7% 25%,26% 26%,25% 7%,41% 18%);' +
      'animation:y2k-spin 2s linear infinite;filter:drop-shadow(0 0 6px #ff2bd6)}' +
    '.y2k-burst span{display:block;transform:rotate(-12deg);animation:y2k-throb .45s ease-in-out infinite alternate}' +
    '@keyframes y2k-spin{to{transform:rotate(360deg)}}' +
    '@keyframes y2k-throb{to{transform:rotate(-12deg) scale(1.18)}}' +
    '@keyframes y2k-pop{0%{transform:scale(0) rotate(-40deg);opacity:0}12%{transform:scale(1.2) rotate(8deg);opacity:1}' +
      '20%{transform:scale(1) rotate(0)}85%{transform:scale(1);opacity:1}100%{transform:scale(0) rotate(30deg);opacity:0}}';
  document.head.appendChild(css);

  function layer(z, before) {
    var c = document.createElement('canvas'); c.className = 'y2k-layer'; c.setAttribute('aria-hidden', 'true'); c.style.zIndex = z;
    if (before) document.body.insertBefore(c, document.body.firstChild); else document.body.appendChild(c);
    return c;
  }
  var back = layer(cfg.backZ == null ? 0 : cfg.backZ, true), front = layer(cfg.frontZ == null ? 30 : cfg.frontZ, false);
  var bx = back.getContext('2d'), fx = front.getContext('2d');
  var flash = document.createElement('div'); flash.className = 'y2k-flash'; flash.style.zIndex = cfg.frontZ == null ? 30 : cfg.frontZ;
  document.body.appendChild(flash);
  var W = 0, H = 0;
  function size() {
    var d = window.devicePixelRatio || 1; W = innerWidth; H = innerHeight;
    [back, front].forEach(function (c) { c.width = W * d; c.height = H * d; });
    bx.setTransform(d, 0, 0, d, 0, 0); fx.setTransform(d, 0, 0, d, 0, 0);
  }
  size(); addEventListener('resize', size);

  /* ---- sparkles (twinkling 4-point stars) and shooting stars, behind everything ---- */
  var COLS = ['#ffffff', '#ff2bd6', '#00f0ff', '#fff200', '#39ff14'];
  var sparks = [];
  for (var i = 0; i < 46; i++) sparks.push({ x: Math.random(), y: Math.random(), r: rnd(3, 9), ph: rnd(0, 6.28), sp: rnd(1.2, 3.2), c: pick(COLS) });
  var shooters = [], nextShoot = 0;
  function star4(g, x, y, r, a, c) {
    g.globalAlpha = a; g.fillStyle = c; g.shadowColor = c; g.shadowBlur = r * 2;
    g.beginPath();
    g.moveTo(x, y - r); g.quadraticCurveTo(x, y, x + r, y); g.quadraticCurveTo(x, y, x, y + r);
    g.quadraticCurveTo(x, y, x - r, y); g.quadraticCurveTo(x, y, x, y - r); g.fill();
    g.shadowBlur = 0; g.globalAlpha = 1;
  }

  /* ---- lightning: jagged midpoint-displaced bolts with forks, a flicker and a soft flash ---- */
  function boltPath(x1, y1, x2, y2, rough) {
    var pts = [[x1, y1], [x2, y2]];
    for (var pass = 0; pass < 6; pass++) {
      var out = [pts[0]];
      for (var k = 1; k < pts.length; k++) {
        var a = pts[k - 1], b = pts[k], len = Math.hypot(b[0] - a[0], b[1] - a[1]);
        out.push([(a[0] + b[0]) / 2 + rnd(-1, 1) * len * rough, (a[1] + b[1]) / 2 + rnd(-0.3, 0.3) * len * rough]);
        out.push(b);
      }
      pts = out;
    }
    return pts;
  }
  var bolt = null, nextBolt = 0;
  function strike(now) {
    var x1 = rnd(0.05, 0.95) * W, y1 = -10, x2 = x1 + rnd(-0.35, 0.35) * W, y2 = rnd(0.35, 0.95) * H;
    var main = boltPath(x1, y1, x2, y2, 0.45), forks = [];
    for (var f = 1 + (Math.random() * 3 | 0); f > 0; f--) {
      var from = main[(main.length * rnd(0.2, 0.7)) | 0];
      forks.push(boltPath(from[0], from[1], from[0] + rnd(-0.25, 0.25) * W, from[1] + rnd(0.1, 0.35) * H, 0.5));
    }
    bolt = { at: now, paths: [main].concat(forks), color: pick(['#00f0ff', '#fff200', '#ff2bd6', '#b18cff']) };
    flash.style.opacity = '0.13'; setTimeout(function () { flash.style.opacity = '0'; }, 70);
  }
  function drawBolt(now) {
    if (!bolt) return;
    var t = now - bolt.at;
    if (t > 420) { bolt = null; return; }
    var on = t < 70 || (t > 120 && t < 200) || t > 240;   // flicker: on, off, on, off, glow out
    if (!on) return;
    var fade = t > 240 ? 1 - (t - 240) / 180 : 1;
    bolt.paths.forEach(function (p, idx) {
      var w = idx ? 2 : 4;
      fx.lineJoin = 'miter'; fx.lineCap = 'round';
      fx.globalAlpha = fade; fx.strokeStyle = bolt.color; fx.lineWidth = w * 3; fx.shadowColor = bolt.color; fx.shadowBlur = 24;
      fx.beginPath(); fx.moveTo(p[0][0], p[0][1]); for (var k = 1; k < p.length; k++) fx.lineTo(p[k][0], p[k][1]); fx.stroke();
      fx.shadowBlur = 0; fx.strokeStyle = '#fff'; fx.lineWidth = w; fx.stroke();
    });
    fx.globalAlpha = 1;
  }

  /* ---- spinning starburst badges ---- */
  var WORDS = ['NEW!', 'HOT!', 'OMG!!', 'FREE!', 'LOL', 'xD', '100% LEGIT', 'WOW!', 'SALE!', '&lt;3', 'RAWR', '20ms!!'];
  var nextBadge = 0;
  function badge() {
    var b = document.createElement('div'); b.className = 'y2k-burst'; b.setAttribute('aria-hidden', 'true');
    b.style.zIndex = cfg.frontZ == null ? 30 : cfg.frontZ;
    b.style.left = rnd(0.02, 0.9) * W + 'px'; b.style.top = rnd(0.05, 0.85) * H + 'px';
    b.innerHTML = '<span>' + pick(WORDS) + '</span>';
    document.body.appendChild(b); setTimeout(function () { b.remove(); }, 2700);
  }

  function frame(now) {
    if (!document.hidden) {
      bx.clearRect(0, 0, W, H); fx.clearRect(0, 0, W, H);
      sparks.forEach(function (s) {
        var a = Math.max(0, Math.sin(now / 1000 * s.sp + s.ph));
        if (a > 0.05) star4(bx, s.x * W, s.y * H, s.r * (0.6 + a * 0.6), a * 0.9, s.c);
      });
      if (now > nextShoot) {
        nextShoot = now + rnd(2000, 5500);
        var ltr = Math.random() < 0.5;
        shooters.push({ x: ltr ? -40 : W + 40, y: rnd(0.05, 0.6) * H, vx: (ltr ? 1 : -1) * rnd(9, 15), vy: rnd(2, 5), c: pick(COLS) });
      }
      for (var i = shooters.length - 1; i >= 0; i--) {
        var s = shooters[i]; s.x += s.vx; s.y += s.vy;
        if (s.x < -80 || s.x > W + 80 || s.y > H + 40) { shooters.splice(i, 1); continue; }
        var g = bx.createLinearGradient(s.x, s.y, s.x - s.vx * 9, s.y - s.vy * 9);
        g.addColorStop(0, s.c); g.addColorStop(1, 'rgba(0,0,0,0)');
        bx.strokeStyle = g; bx.lineWidth = 3; bx.beginPath(); bx.moveTo(s.x, s.y); bx.lineTo(s.x - s.vx * 9, s.y - s.vy * 9); bx.stroke();
        star4(bx, s.x, s.y, 7, 1, '#fff');
      }
      if (!nextBolt) nextBolt = now + rnd(1500, 3500);
      if (now > nextBolt) { strike(now); nextBolt = now + rnd(2600, 6500); }
      drawBolt(now);
      if (!nextBadge) nextBadge = now + rnd(1500, 3000);
      if (now > nextBadge) { badge(); nextBadge = now + rnd(2800, 6000); }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  window.Y2K = { strike: function () { strike(performance.now()); }, badge: badge };
})();
