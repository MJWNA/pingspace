/* PingSpace goo: a blob hangs off the sausage cursor's tip, swells when the pointer
 * slows, drops, and splats on whatever is underneath, including the pin-ups of
 * Ronnie (it follows their exact outline and sticks to them as they move).
 * Purely visual: the canvas is click-through, splats fade, desktop only, and it
 * switches off under reduced motion. Shared by the app (ui/) and the install guide.
 *
 * Page config (optional), set before this script loads:
 *   window.GOO_CONFIG = { surfaces: 'css selector of things it can land on', z: 40 }
 * Pin-ups opt in by being a `.pinhit` element holding the <img> and three empty
 * <i> corner markers (top-left, top-right, bottom-left), so transforms can be traced.
 */
(function () {
  var mq = window.matchMedia;
  if (!mq || !mq('(pointer: fine)').matches || mq('(prefers-reduced-motion: reduce)').matches) return;
  var cfg = window.GOO_CONFIG || {};
  var SURF = cfg.surfaces || 'p,li,img,button,h1,h2,label,ol,ul,footer';
  var COLOR = '#ecebe1', GLOSS = '#ffffff';
  var TIP_X = 6, TIP_Y = 8;   // where the drip leaves the sausage cursor, relative to its click point

  // canvas + the goo filter (blur then sharpen the alpha = blobs that merge like slime)
  var NS = 'http://www.w3.org/2000/svg';
  var svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', '0'); svg.setAttribute('height', '0'); svg.setAttribute('aria-hidden', 'true');
  svg.style.position = 'absolute';
  svg.innerHTML = '<filter id="goofx"><feGaussianBlur in="SourceGraphic" stdDeviation="4"/>' +
    '<feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10"/></filter>';
  var cv = document.createElement('canvas');
  cv.setAttribute('aria-hidden', 'true');
  cv.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:' + (cfg.z || 40) +
    ';filter:url(#goofx) drop-shadow(0 1px 1px rgba(0,0,0,.45)) drop-shadow(0 0 2px rgba(60,40,70,.35))';
  document.body.appendChild(svg); document.body.appendChild(cv);
  var ctx = cv.getContext('2d');

  var mx = -999, my = -999, speed = 0, lastMove = 0, running = false;
  var hang = { x: 0, y: 0, vx: 0, vy: 0, m: 0.1 };
  var drops = [], puddles = [];
  window.__goo = { drops: drops, puddles: puddles, spurts: 0 };
  // rhythm: bursts of 2-4 spurts a beat apart, each weaker than the last, then a few seconds of dripping
  var nextBurst = 0, burstLeft = 0, nextSpurt = 0, power = 1;
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function size() {
    var d = window.devicePixelRatio || 1;
    cv.width = innerWidth * d; cv.height = innerHeight * d; ctx.setTransform(d, 0, 0, d, 0, 0);
  }
  size(); addEventListener('resize', size);

  /* ---- pin-ups: alpha masks + tracing each one's current transform ---- */
  var MASKS = {};
  function mask(img) {
    var key = img.currentSrc || img.src;
    if (key in MASKS) return MASKS[key];
    MASKS[key] = null;
    var im = new Image();
    im.onload = function () {
      try {
        var c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight;
        var x = c.getContext('2d'); x.drawImage(im, 0, 0);
        MASKS[key] = { w: c.width, h: c.height, a: x.getImageData(0, 0, c.width, c.height).data };
      } catch (e) { MASKS[key] = null; }   // e.g. file:// pages can't read pixels; pin-ups just won't catch drops
    };
    im.src = key;
    return null;
  }
  // learn the outlines up front so the very first drop doesn't fall straight through him
  setTimeout(function () { Array.prototype.forEach.call(document.querySelectorAll('.pinhit img'), mask); }, 300);
  // affine map from the pin-up's own box (u, v) to the screen, via its three corner markers
  function frameOf(pic) {
    var m = pic.__marks || (pic.__marks = pic.querySelectorAll(':scope > i'));
    if (m.length < 3) return null;
    var a = m[0].getBoundingClientRect(), b = m[1].getBoundingClientRect(), c = m[2].getBoundingClientRect();
    var w = pic.offsetWidth, h = pic.offsetHeight;
    if (!w || !h) return null;
    return { ox: a.left, oy: a.top, ux: (b.left - a.left) / w, uy: (b.top - a.top) / w,
             vx: (c.left - a.left) / h, vy: (c.top - a.top) / h, w: w, h: h };
  }
  function toLocal(F, x, y) {
    var dx = x - F.ox, dy = y - F.oy, det = F.ux * F.vy - F.vx * F.uy;
    if (Math.abs(det) < 1e-6) return null;
    return { u: (dx * F.vy - dy * F.vx) / det, v: (F.ux * dy - F.uy * dx) / det };
  }
  function toScreen(F, u, v) { return { x: F.ox + u * F.ux + v * F.vx, y: F.oy + u * F.uy + v * F.vy }; }
  function visible(pic, x, y) {
    if (!pic.isConnected) return false;
    var off = pic.closest('.bum'); if (off && !off.classList.contains('on')) return false;
    var clip = pic.closest('.lurk');   // lurkers are mostly hidden behind their box
    if (clip) { var r = clip.getBoundingClientRect(); if (x < r.left || x > r.right || y < r.top || y > r.bottom) return false; }
    return true;
  }
  function solid(pic, F, x, y) {
    var img = pic.querySelector('img'); if (!img) return null;
    var M = mask(img); if (!M) return null;
    var L = toLocal(F, x, y); if (!L || L.u < 0 || L.v < 0 || L.u >= F.w || L.v >= F.h) return null;
    var px = (L.u / F.w * M.w) | 0, py = (L.v / F.h * M.h) | 0;
    return M.a[(py * M.w + px) * 4 + 3] > 110 ? L : null;
  }
  // is there a bit of ronnie at (x, y)? returns where on him it is, nudged up to his top edge
  function pinupAt(x, y) {
    var pics = document.querySelectorAll('.pinhit');
    for (var i = pics.length - 1; i >= 0; i--) {
      var pic = pics[i];
      if (!visible(pic, x, y)) continue;
      var F = frameOf(pic); if (!F) continue;
      var L = solid(pic, F, x, y); if (!L) continue;
      for (var k = 1; k < 18 && solid(pic, F, x, y - k); k++) L = toLocal(F, x, y - k);
      return { pic: pic, u: L.u, v: L.v };
    }
    return null;
  }

  /* ---- landing on ordinary page stuff ---- */
  function blockAt(x, y) {
    var el = document.elementFromPoint(x, y);
    if (!el || el === document.body || el === document.documentElement) return null;
    if (el.closest('.pinhit')) return null;   // pin-ups catch drops by their outline (pinupAt), not their box
    return el.closest(SURF);
  }
  function landingY(x, y) {
    var start = blockAt(x, y), floor = innerHeight - 3;
    for (var yy = y + 8; yy < floor; yy += 5) {
      var b = blockAt(x, yy);
      if (b && b !== start && !b.contains(start)) return Math.max(y + 8, b.getBoundingClientRect().top);
    }
    return floor;
  }
  function drop(x, y, r, vx, vy) {   // viewport coords in; drops live in page coords
    drops.push({ x: x, y: y + scrollY, r: r, vx: vx, vy: vy, land: vy < 0 ? null : landingY(x, y) + scrollY });
    if (drops.length > 70) drops.shift();
  }
  // a spurt: one big glob plus a few droplets fired up and out of the sausage tip, weaker each time (p)
  function spurt(x, y, p) {
    var ang = -2.2 + rnd(-0.45, 0.45), sp = rnd(9, 13) * p;
    drop(x, y, rnd(5, 7.5) * (0.6 + 0.4 * p), Math.cos(ang) * sp, Math.sin(ang) * sp);
    for (var i = 2 + (Math.random() * 3 | 0); i > 0; i--) {
      var a2 = ang + rnd(-0.35, 0.35), s2 = sp * rnd(0.55, 0.9);
      drop(x, y, rnd(1.8, 3.6), Math.cos(a2) * s2, Math.sin(a2) * s2);
    }
    window.__goo.spurts++;
  }
  function drips(r) {
    var out = [], n = Math.random() < 0.75 ? 1 + (Math.random() * 2 | 0) : 0;
    for (var i = 0; i < n; i++) out.push({ dx: rnd(-r * 1.4, r * 1.4), len: 0, max: rnd(10, 38), sp: rnd(0.08, 0.22) });
    return out;
  }
  function splat(d, on) {
    var p = { x: d.x, y: d.land, r: d.r, t: 0, life: rnd(4000, 8000), drips: drips(d.r) };
    if (on) { p.pic = on.pic; p.u = on.u; p.v = on.v; p.life += 2500; }   // stuck to ronnie, sticks around longer
    puddles.push(p);
    if (puddles.length > 70) puddles.shift();
  }
  function blob(x, y, r) { if (r > 0.3) { ctx.beginPath(); ctx.arc(x, y, r, 0, 6.2832); ctx.fill(); } }
  function glossy(x, y, r) {
    blob(x, y, r);
    if (r > 3) { ctx.fillStyle = GLOSS; blob(x - r * 0.35, y - r * 0.35, r * 0.3); ctx.fillStyle = COLOR; }
  }

  addEventListener('mousemove', function (e) {
    var dx = e.clientX - mx, dy = e.clientY - my;
    if (mx < -900) { hang.x = e.clientX + TIP_X; hang.y = e.clientY + TIP_Y + 6; dx = dy = 0; }
    mx = e.clientX; my = e.clientY; lastMove = performance.now();
    speed = speed * 0.7 + Math.min(80, Math.hypot(dx, dy)) * 0.3;
    if (speed > 22 && Math.random() < 0.3) drop(mx - dx * 0.4, my - dy * 0.4 + 6, rnd(2, 3.6), dx * 0.06, dy * 0.06);
    start();
  }, { passive: true });
  document.addEventListener('mouseleave', function () { mx = my = -999; });

  var last = 0;
  function frame(now) {
    var dt = Math.min(48, now - (last || now)) / 16.7; last = now;
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    ctx.fillStyle = COLOR;
    var sy = scrollY;

    // the blob hanging off the sausage
    if (mx > -900) {
      speed *= Math.pow(0.9, dt);
      var slow = speed < 3;
      hang.m = Math.min(1, hang.m + (slow ? 0.022 : 0.007) * dt);
      var ox = mx + TIP_X, oy = my + TIP_Y;
      if (now - lastMove < 6000) {
        if (!nextBurst) nextBurst = now + rnd(1500, 3500);
        if (!burstLeft && now >= nextBurst) { burstLeft = 2 + (Math.random() * 3 | 0); power = 1; nextSpurt = now; }
        if (burstLeft && now >= nextSpurt) {
          spurt(ox, oy, power); burstLeft--; power *= rnd(0.62, 0.8);
          hang.m = 0.05; hang.y = oy + 4;                    // spent, starts dripping again from empty
          nextSpurt = now + rnd(170, 340);
          if (!burstLeft) nextBurst = now + rnd(2800, 6500);
        }
      }
      var tx = ox, ty = oy + 6 + hang.m * 30;
      hang.vx = (hang.vx + (tx - hang.x) * 0.12 * dt) * Math.pow(0.8, dt);
      hang.vy = (hang.vy + ((ty - hang.y) * 0.12 + 0.35) * dt) * Math.pow(0.8, dt);
      hang.x += hang.vx * dt; hang.y += hang.vy * dt;
      var R = 3.2 + hang.m * 8.5;
      if (hang.m >= 1 || (hang.m > 0.55 && slow && Math.random() < 0.02 * dt)) {
        drop(hang.x, hang.y, R, hang.vx * 0.4, Math.max(0, hang.vy * 0.4));
        hang.m = 0.08; hang.y = oy + 6;
      }
      blob(ox, oy, 3.6);
      for (var i = 1; i <= 9; i++) {
        var t = i / 9;
        blob(ox + (hang.x - ox) * t, oy + (hang.y - oy) * t, 1.6 + (R - 1.6) * t * t);
      }
      glossy(hang.x, hang.y, R);
    }

    // falling drops: land on ronnie if they hit him on the way down, else on whatever is below
    for (var k = drops.length - 1; k >= 0; k--) {
      var d = drops[k];
      d.vy += 0.5 * dt; d.vx *= Math.pow(0.985, dt); d.x += d.vx * dt; d.y += d.vy * dt;
      var y0 = d.y - sy;
      if (d.x < -60 || d.x > innerWidth + 60 || y0 > innerHeight + 200) { drops.splice(k, 1); continue; }
      // spurts only work out where they'll land once they start coming down
      if (d.land == null && d.vy >= 0) d.land = landingY(d.x, Math.max(2, Math.min(innerHeight - 4, y0))) + sy;
      var hit = d.vy > 0 && y0 > 0 && y0 < innerHeight ? pinupAt(d.x, y0 + d.r * 0.5) : null;
      if (hit) { splat(d, hit); drops.splice(k, 1); continue; }
      if (d.land != null && d.y + d.r * 0.4 >= d.land) { d.y = d.land; splat(d); drops.splice(k, 1); continue; }
      glossy(d.x, y0, d.r);
      blob(d.x - d.vx * 0.6, y0 - Math.min(d.vy, 14) * 0.7, d.r * 0.7);
      blob(d.x - d.vx * 1.1, y0 - Math.min(d.vy, 14) * 1.3, d.r * 0.4);
    }

    // splats with drips running down, then fading. the ones on ronnie move with him
    for (var p = puddles.length - 1; p >= 0; p--) {
      var q = puddles[p]; q.t += 16.7 * dt;
      var f = q.t < 120 ? q.t / 120 : (q.t > q.life ? 1 - (q.t - q.life) / 1500 : 1);
      if (f <= 0) { puddles.splice(p, 1); continue; }
      var x, yy;
      if (q.pic) {
        if (!q.pic.isConnected) { puddles.splice(p, 1); continue; }
        var F = frameOf(q.pic); if (!F) continue;
        var s = toScreen(F, q.u, q.v); x = s.x; yy = s.y;
        if (!visible(q.pic, x, yy)) continue;
      } else {
        x = q.x; yy = q.y - sy;
      }
      if (yy < -60 || yy > innerHeight + 60) continue;
      var r = q.r * f;
      blob(x - r * 1.35, yy - r * 0.15, r * 0.65);
      blob(x + r * 1.25, yy - r * 0.15, r * 0.6);
      glossy(x, yy - r * 0.3, r * 1.05);
      for (var j = 0; j < q.drips.length; j++) {
        var dr = q.drips[j];
        dr.len = Math.min(dr.max, dr.len + dr.sp * dt);
        for (var z = 0; z <= dr.len; z += 3) blob(x + dr.dx, yy + z, Math.max(1.5, r * 0.38 * (1 - z / (dr.max + 8))) * f);
        glossy(x + dr.dx, yy + dr.len, r * 0.5);
      }
    }

    var idle = now - lastMove > 6000;
    if (idle && !drops.length && !puddles.length) { running = false; ctx.clearRect(0, 0, innerWidth, innerHeight); return; }
    requestAnimationFrame(frame);
  }
  function start() { if (!running) { running = true; last = 0; requestAnimationFrame(frame); } }
  window.Goo = { drop: drop, pinupAt: pinupAt, start: start };
})();
