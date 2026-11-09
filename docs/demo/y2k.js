/* PingSpace Y2K: tacky 2000s / emo-era web effects. Lightning bolts strike at random,
 * spinning NEW!/HOT!/OMG!! starbursts pop up, cringe WordArt phrases float by, emo eyes
 * blink out of the dark, broken hearts and skulls rain down, fake Windows 98 "u won"
 * popups slide in, Blingee sparkles twinkle round the pin-ups, and sparkles and
 * shooting stars fill the background. Where the side gutters have room, the pop-ups stay
 * in them so the text stays readable. Everything is click-through, pauses when the
 * window is hidden, and switches off under reduced motion. Flashes are soft and never
 * faster than one bolt every few seconds (well under the 3-per-second photosensitivity limit).
 *
 * Page config (optional), set before this script loads:
 *   window.Y2K_CONFIG = { backZ: 0, frontZ: 30, content: 860 }
 *   backZ: layer for sparkles/stars, frontZ: layer for everything else,
 *   content: width of the centred content column (the gutters are what's left either side)
 */
(function () {
  var mq = window.matchMedia;
  if (mq && mq('(prefers-reduced-motion: reduce)').matches) return;
  var cfg = window.Y2K_CONFIG || {};
  var FRONT = cfg.frontZ == null ? 30 : cfg.frontZ, CONTENT = cfg.content || 860;
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function pick(a) { return a[Math.random() * a.length | 0]; }

  var css = document.createElement('style');
  css.textContent = [
    '.y2k-layer{position:fixed;inset:0;width:100%;height:100%;pointer-events:none}',
    '.y2k-flash{position:fixed;inset:0;pointer-events:none;background:#fff;opacity:0;transition:opacity .12s}',
    '.y2k-fx{position:fixed;pointer-events:none}',
    /* starburst badges */
    '.y2k-burst{width:96px;height:96px;display:flex;align-items:center;justify-content:center;font:bold 17px Impact,"Arial Black",sans-serif;',
    'color:#d40000;text-align:center;line-height:1;letter-spacing:.5px;text-shadow:1px 1px 0 #fff;animation:y2k-pop 2.6s ease-in-out forwards}',
    '.y2k-burst::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(circle,#fffb8a,#ffe600 55%,#ff9a00);',
    'clip-path:polygon(50% 0,59% 18%,75% 7%,74% 26%,93% 25%,82% 41%,100% 50%,82% 59%,93% 75%,74% 74%,75% 93%,59% 82%,50% 100%,41% 82%,25% 93%,26% 74%,7% 75%,18% 59%,0 50%,18% 41%,7% 25%,26% 26%,25% 7%,41% 18%);',
    'animation:y2k-spin 2s linear infinite;filter:drop-shadow(0 0 6px #ff2bd6)}',
    '.y2k-burst span{display:block;transform:rotate(-12deg);animation:y2k-throb .45s ease-in-out infinite alternate}',
    '@keyframes y2k-spin{to{transform:rotate(360deg)}}',
    '@keyframes y2k-throb{to{transform:rotate(-12deg) scale(1.18)}}',
    '@keyframes y2k-pop{0%{transform:scale(0) rotate(-40deg);opacity:0}12%{transform:scale(1.2) rotate(8deg);opacity:1}',
    '20%{transform:scale(1) rotate(0)}85%{transform:scale(1);opacity:1}100%{transform:scale(0) rotate(30deg);opacity:0}}',
    /* WordArt cringe phrases */
    '.y2k-word{white-space:nowrap;font:bold 28px Impact,"Arial Black",sans-serif;letter-spacing:1px;',
    'background:linear-gradient(180deg,#ff00cc,#fff200 35%,#39ff14 55%,#00f0ff 75%,#7a00ff);-webkit-background-clip:text;background-clip:text;color:transparent;',
    'filter:drop-shadow(2px 2px 0 #000) drop-shadow(3px 3px 0 #ff2bd6) drop-shadow(0 0 6px rgba(255,255,255,.6));',
    'animation:y2k-float 3.8s ease-in-out forwards}',
    '.y2k-word.c2{background:linear-gradient(90deg,#000,#ff2bd6,#000,#ff2bd6);-webkit-background-clip:text;background-clip:text;',
    'filter:drop-shadow(1px 1px 0 #fff) drop-shadow(0 0 8px #ff2bd6);font-family:"Comic Sans MS","Comic Neue",cursive}',
    '@keyframes y2k-float{0%{transform:perspective(300px) rotateX(35deg) rotate(-8deg) scale(.2);opacity:0}',
    '15%{transform:perspective(300px) rotateX(20deg) rotate(6deg) scale(1.1);opacity:1}',
    '50%{transform:perspective(300px) rotateX(25deg) rotate(-5deg) translateY(-30px)}',
    '85%{opacity:1}100%{transform:perspective(300px) rotateX(35deg) rotate(4deg) translateY(-70px) scale(.9);opacity:0}}',
    /* emo eyes */
    '.y2k-eyes{animation:y2k-eyes 3s ease-in-out forwards}',
    '.y2k-eyes .lid{transform-origin:center;animation:y2k-blink 3s steps(1) forwards}',
    '@keyframes y2k-eyes{0%{opacity:0}15%{opacity:1}85%{opacity:1}100%{opacity:0}}',
    '@keyframes y2k-blink{0%,30%,36%,62%,68%,100%{transform:scaleY(1)}31%,35%,63%,67%{transform:scaleY(.08)}}',
    /* raining hearts, skulls, crosses and stars */
    '.y2k-rain{font:24px "Segoe UI Symbol","Apple Symbols",sans-serif;animation:y2k-fall linear forwards}',
    '@keyframes y2k-fall{to{transform:translateY(var(--fall)) rotate(var(--spin))}}',
    /* fake win98 popups */
    '.y2k-win{width:250px;background:#c0c0c0;border:2px outset #fff;box-shadow:3px 3px 0 #000;font:12px Tahoma,"MS Sans Serif",sans-serif;color:#000;',
    'animation:y2k-win 4.6s ease-in-out forwards}',
    '.y2k-win .t{background:linear-gradient(90deg,#000080,#1084d0);color:#fff;font-weight:bold;padding:3px 5px;display:flex;justify-content:space-between}',
    '.y2k-win .t i{font-style:normal;background:#c0c0c0;color:#000;border:1px outset #fff;padding:0 4px;line-height:12px}',
    '.y2k-win .b{padding:10px;line-height:1.4}',
    '.y2k-win .b b{color:#c00000;font-size:13px;animation:y2k-blinktxt .5s steps(2,start) infinite}',
    '.y2k-win .btns{display:flex;gap:8px;justify-content:center;margin-top:8px}',
    '.y2k-win .btns i{font-style:normal;border:2px outset #fff;padding:2px 12px;background:#c0c0c0}',
    '@keyframes y2k-blinktxt{to{visibility:hidden}}',
    '@keyframes y2k-win{0%{transform:translateY(40px) scale(.6);opacity:0}10%{transform:none;opacity:1}',
    '14%{transform:translateX(-6px)}18%{transform:translateX(6px)}22%{transform:translateX(-4px)}26%{transform:none}',
    '88%{opacity:1;transform:none}100%{opacity:0;transform:translateY(20px) scale(.8)}}'
  ].join('');
  document.head.appendChild(css);

  function layer(z, before) {
    var c = document.createElement('canvas'); c.className = 'y2k-layer'; c.setAttribute('aria-hidden', 'true'); c.style.zIndex = z;
    if (before) document.body.insertBefore(c, document.body.firstChild); else document.body.appendChild(c);
    return c;
  }
  var back = layer(cfg.backZ == null ? 0 : cfg.backZ, true), front = layer(FRONT, false);
  var bx = back.getContext('2d'), fx = front.getContext('2d');
  var flash = document.createElement('div'); flash.className = 'y2k-flash'; flash.style.zIndex = FRONT;
  document.body.appendChild(flash);
  var W = 0, H = 0;
  function size() {
    var d = window.devicePixelRatio || 1; W = innerWidth; H = innerHeight;
    [back, front].forEach(function (c) { c.width = W * d; c.height = H * d; });
    bx.setTransform(d, 0, 0, d, 0, 0); fx.setTransform(d, 0, 0, d, 0, 0);
  }
  size(); addEventListener('resize', size);

  // a random spot for a w x h pop-up: in a side gutter when there's room, otherwise anywhere
  function gutter() { return (W - CONTENT) / 2; }
  function spot(w, h) {
    var g = gutter(), y = rnd(0.05, 0.92) * Math.max(10, H - h);
    if (g >= w + 16) {
      var x = rnd(8, g - w - 8);
      return { x: Math.random() < 0.5 ? x : W - g + x, y: y };
    }
    return { x: rnd(0, Math.max(10, W - w)), y: y };
  }
  function fxEl(cls, w, h, html, life) {
    var el = document.createElement('div'); el.className = 'y2k-fx ' + cls; el.setAttribute('aria-hidden', 'true');
    el.style.zIndex = FRONT; el.innerHTML = html;
    var p = spot(w, h); el.style.left = p.x + 'px'; el.style.top = p.y + 'px';
    document.body.appendChild(el); setTimeout(function () { el.remove(); }, life);
    return el;
  }

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
  var BADGES = ['NEW!', 'HOT!', 'OMG!!', 'FREE!', 'LOL', 'xD', '100% LEGIT', 'WOW!', 'SALE!', '&lt;3', 'RAWR', '20ms!!'];
  function badge() { fxEl('y2k-burst', 96, 96, '<span>' + pick(BADGES) + '</span>', 2700); }

  /* ---- cringe WordArt phrases ---- */
  var CRINGE = ['rawr XD', 'rawr means i love u in dinosaur', '*glomps u*', 'its not a phase MOM', 'uR sO rAnDoM', 'brb crying',
                '~*hugz*~', 'xXx_3m0_4_LyFe_xXx', 'FIRST!!1', 'pwned', 'i &lt;3 eyeliner', 'take a pic its free', 'thx 4 the add!!',
                'pc4pc?', 'top 8 or die', 'nobody understands me', 'whatever. im over it.', 'omg BECKY', '*sparkles*', 'random!!',
                'emo kids dont dance', 'ur song is my jam', 'i luv u... as a friend', 'cake.', 'sk8er boi', '20ms bby &lt;3'];
  function word() {
    var txt = pick(CRINGE), g = gutter(), w = Math.min(380, 26 + txt.length * 15), h = 50, wrap = false;
    if (g >= 170 && w > g - 24) { w = g - 24; h = 90; wrap = true; }   // wrap to fit the gutter instead of covering the text
    var el = fxEl('y2k-word' + (Math.random() < 0.35 ? ' c2' : ''), w, h, txt, 3900);
    el.style.fontSize = (wrap || txt.length > 18 ? 21 : rnd(24, 34)) + 'px';
    if (wrap) { el.style.width = w + 'px'; el.style.whiteSpace = 'normal'; el.style.textAlign = 'center'; el.style.lineHeight = '1.05'; }
  }

  /* ---- emo eyes blinking out of the dark ---- */
  var EYE_COLS = ['#39ff14', '#00f0ff', '#ff2bd6', '#b18cff', '#ff3b3b'];
  function eyes() {
    var c = pick(EYE_COLS), one = function (x, flip) {
      return '<g transform="translate(' + x + ',0)' + (flip ? ' scale(-1,1)' : '') + '">' +
        '<path d="M-34 24 Q0 -4 34 18 L46 8 L38 24 Q0 46 -34 24Z" fill="#000"/>' +   // heavy liner with a wing
        '<g class="lid"><ellipse cx="0" cy="22" rx="27" ry="13" fill="#f6f0ff"/><circle cx="2" cy="22" r="10" fill="' + c + '"/>' +
        '<circle cx="2" cy="22" r="5" fill="#000"/><circle cx="6" cy="18" r="2.4" fill="#fff"/></g>' +
        '<path d="M-6 36 Q-10 60 -4 84" stroke="#000" stroke-width="3" fill="none" opacity=".8"/></g>';   // mascara tear
    };
    fxEl('y2k-eyes', 180, 90, '<svg width="180" height="90" viewBox="-90 -6 180 96">' + one(-46, false) + one(46, true) + '</svg>', 3100);
  }

  /* ---- raining broken hearts, skulls, crosses and stars ---- */
  var SYMS = ['♥', '♡', '☠︎', '✝', '★', '☆', '✿', '❤︎'];
  var RAIN_COLS = ['#000', '#ff2bd6', '#39ff14', '#fff', '#b18cff'];
  function rain() {
    var g = gutter(), bands = g > 70 ? [[0, g], [W - g, W]] : [[0, W]];
    for (var i = 0; i < 26; i++) {
      var band = pick(bands), s = document.createElement('span'), dur = rnd(3, 6);
      s.className = 'y2k-fx y2k-rain'; s.setAttribute('aria-hidden', 'true'); s.style.zIndex = FRONT;
      s.textContent = pick(SYMS); s.style.color = pick(RAIN_COLS);
      s.style.textShadow = '0 0 2px #fff, 0 0 6px #ff2bd6';
      s.style.left = rnd(band[0], band[1] - 24) + 'px'; s.style.top = rnd(-120, -30) + 'px';
      s.style.fontSize = rnd(16, 34) + 'px';
      s.style.setProperty('--fall', (H + 160) + 'px'); s.style.setProperty('--spin', rnd(-540, 540) + 'deg');
      s.style.animationDuration = dur + 's'; s.style.animationDelay = rnd(0, 1.2) + 's';
      document.body.appendChild(s);
      (function (s, ms) { setTimeout(function () { s.remove(); }, ms); })(s, (dur + 1.4) * 1000);
    }
  }

  /* ---- fake windows 98 "u won" popups ---- */
  var POPS = [
    ['CONGRATULATIONS!!!', 'u r the 1,000,000th visitor!!!', 'ur prize: 20ms ping 4 lyfe'],
    ['Hot Singles', 'hot singles (servers) in ur area!!', '3 sydney servers want 2 meet u'],
    ['Security Alert', 'ur computer may be infected with LAG!!', 'scan now 4 free (it wont help)'],
    ['New Friend Request', 'SydneyServer wants 2 b ur friend!!', 'and put u in their top 8'],
    ['Windows', 'ur ping is 2 high 4 this website', 'pls install more RAM']
  ];
  function popup() {
    if (gutter() < 270 && Math.random() < 0.7) return;   // keep these off the text on narrow screens, mostly
    var p = pick(POPS);
    fxEl('y2k-win', 250, 140, '<div class="t"><span>' + p[0] + '</span><i>x</i></div><div class="b"><b>' + p[1] + '</b><br>' + p[2] +
      '<div class="btns"><i>CLAIM NOW</i><i>OK</i></div></div>', 4700);
  }

  /* ---- blingee sparkles round the pin-ups ---- */
  var bling = [], pinRects = [], pinRectsAt = 0;
  function blingTick(now) {
    if (now - pinRectsAt > 1000) {
      pinRectsAt = now; pinRects = [];
      var pins = document.querySelectorAll('.pinhit');
      for (var i = 0; i < pins.length; i++) {
        var r = pins[i].getBoundingClientRect();
        if (r.width > 20 && r.bottom > 0 && r.top < H && r.right > 0 && r.left < W) pinRects.push(r);
      }
    }
    if (pinRects.length && Math.random() < 0.35) {
      var r = pick(pinRects);
      bling.push({ x: rnd(r.left, r.right), y: rnd(r.top, r.top + r.height * 0.7), t: now, c: pick(COLS), s: rnd(5, 12) });
    }
    for (var k = bling.length - 1; k >= 0; k--) {
      var b = bling[k], age = (now - b.t) / 700;
      if (age >= 1) { bling.splice(k, 1); continue; }
      star4(fx, b.x, b.y, b.s * Math.sin(age * Math.PI), 0.95, b.c);
    }
  }

  var next = {};
  function every(name, now, a, b, fn) {
    if (!next[name]) next[name] = now + rnd(a * 0.5, b * 0.6);
    if (now > next[name]) { next[name] = now + rnd(a, b); fn(now); }
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
      blingTick(now);
      every('badge', now, 2800, 6000, badge);
      every('word', now, 2200, 5000, word);
      every('eyes', now, 7000, 15000, eyes);
      every('rain', now, 14000, 26000, rain);
      every('popup', now, 18000, 34000, popup);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  window.Y2K = { strike: function () { strike(performance.now()); }, badge: badge, word: word, eyes: eyes, rain: rain, popup: popup };
})();
