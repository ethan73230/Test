// ------------------------------------------------------------
// Si une miniature (wsrv.nl) ne charge pas, on affiche la photo d'origine.
document.addEventListener('error', function (e) {
  var im = e.target;
  if (im && im.tagName === 'IMG' && im.dataset.orig && im.src !== im.dataset.orig) {
    im.removeAttribute('srcset');
    im.src = im.dataset.orig;
  }
}, true);

// ------------------------------------------------------------
// Menu mobile
(function () {
  var b = document.querySelector('.burger'), n = document.getElementById('nav');
  if (!b || !n) return;
  b.addEventListener('click', function () {
    var open = n.classList.toggle('open');
    b.setAttribute('aria-expanded', open);
    b.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && n.classList.contains('open')) {
      n.classList.remove('open'); b.setAttribute('aria-expanded', false); b.focus();
    }
  });
})();

// ------------------------------------------------------------
// Prochain rendez-vous (heure de Paris). Pour la saison suivante,
// il suffit de modifier cette liste.
(function () {
  var box = document.getElementById('next');
  if (!box) return;
  var p = box.getAttribute('data-prefix') || '';
  var T = function (s) { return new Date(s).getTime(); };
  var events = [
    { end: T('2026-10-30T20:00:00+01:00'), tag: 'Bourse aux skis', what: 'Dépôt vendredi 30 octobre, 9h00 – 20h00', where: 'Gymnase Vivet', href: 'bourse-aux-skis-2026.html' },
    { end: T('2026-10-31T11:30:00+01:00'), tag: 'Bourse aux skis', what: 'Dépôt samedi 31 octobre, 8h00 – 11h30', where: 'vente dès 14h00', href: 'bourse-aux-skis-2026.html' },
    { end: T('2026-10-31T19:30:00+01:00'), tag: 'Bourse aux skis', what: 'Vente samedi 31 octobre, 14h00 – 19h30', where: 'Gymnase Vivet', href: 'bourse-aux-skis-2026.html' },
    { end: T('2026-11-01T16:30:00+01:00'), tag: 'Bourse aux skis', what: 'Vente dimanche 1er novembre, 9h00 – 16h30', where: 'Gymnase Vivet', href: 'bourse-aux-skis-2026.html' },
    { end: T('2026-11-01T19:15:00+01:00'), tag: 'Bourse aux skis', what: 'Restitution dimanche, 18h30 – 19h15', where: 'reçu de dépôt obligatoire', href: 'bourse-aux-skis-2026.html' }
  ];
  var sorties = [
    ['2027-01-09', 'Saint-François-Longchamp'], ['2027-01-16', 'Saint-François-Longchamp'],
    ['2027-01-23', 'Saint-François-Longchamp'], ['2027-01-30', 'Saint-François-Longchamp'],
    ['2027-02-06', 'Saint-François-Longchamp'], ['2027-02-27', 'Les Karellis'],
    ['2027-03-06', 'Les Karellis'], ['2027-03-13', 'Les Karellis'],
    ['2027-03-20', 'Les Karellis, passage des tests'], ['2027-03-27', 'Les Karellis']
  ];
  var JOURS = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
  var MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
  sorties.forEach(function (s, i) {
    var d = new Date(s[0] + 'T12:00:00+01:00');
    events.push({ end: T(s[0] + 'T18:45:00+01:00'), tag: 'Sortie ' + (i + 1) + ' sur 10', blue: true,
      what: 'Samedi ' + d.getDate() + (d.getDate() === 1 ? 'er' : '') + ' ' + MOIS[d.getMonth()] + ', rendez-vous 11h00 au collège',
      where: s[1], href: 'les-sorties.html' });
  });
  var now = Date.now(), ev = null;
  for (var i = 0; i < events.length; i++) { if (now < events[i].end) { ev = events[i]; break; } }
  if (!ev) return;
  // Pas de bandeau sur la page de l'événement lui-même (l'info y est déjà en haut)
  if (location.pathname.split('/').pop() === ev.href && ev.href === 'bourse-aux-skis-2026.html') return;
  var wrap = document.createElement('div');
  wrap.className = 'wrap';
  wrap.innerHTML = '<a href="' + p + ev.href + '"><span class="tag' + (ev.blue ? ' b' : '') + '">' + ev.tag + '</span>' +
    '<span class="what">' + ev.what + ' <em>(' + ev.where + ')</em></span><span class="go">Voir les détails</span></a>';
  box.appendChild(wrap);
  box.hidden = false;
})();

// ------------------------------------------------------------
// Visionneuse de photos : clavier, glisser du doigt, téléchargement
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.gallery a'));
  if (!links.length) return;
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Photo agrandie');
  lb.innerHTML = '<img alt="">' +
    '<button class="close" type="button" aria-label="Fermer">×</button>' +
    '<button class="prev" type="button" aria-label="Photo précédente">‹</button>' +
    '<button class="next" type="button" aria-label="Photo suivante">›</button>' +
    '<p class="count" aria-live="polite"></p>' +
    '<a class="dl" download target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>Télécharger</a>';
  document.body.appendChild(lb);
  var img = lb.querySelector('img'), count = lb.querySelector('.count'), dl = lb.querySelector('.dl');
  var i = 0, last = null, cache = {};
  function big(a) { return a.getAttribute('data-big') || a.href; }
  function preload(k) {
    var a = links[(k + links.length) % links.length], u = big(a);
    if (!cache[u]) { cache[u] = new Image(); cache[u].src = u; }
  }
  function show(k) {
    i = (k + links.length) % links.length;
    var a = links[i], u = big(a);
    img.classList.add('loading');
    img.onload = function () { img.classList.remove('loading'); };
    img.onerror = function () { if (img.src !== a.href) img.src = a.href; };
    img.src = u;
    img.alt = (a.querySelector('img') || {}).alt || '';
    dl.href = a.href;
    count.textContent = 'Photo ' + (i + 1) + ' sur ' + links.length;
    preload(i + 1); preload(i - 1);
  }
  function open(k) {
    last = document.activeElement; show(k); lb.classList.add('open');
    lb.querySelector('.close').focus(); document.body.style.overflow = 'hidden';
  }
  function close() {
    lb.classList.remove('open'); img.removeAttribute('src'); document.body.style.overflow = '';
    if (last) last.focus();
  }
  links.forEach(function (a, k) { a.addEventListener('click', function (e) { e.preventDefault(); open(k); }); });
  lb.querySelector('.close').addEventListener('click', close);
  lb.querySelector('.prev').addEventListener('click', function () { show(i - 1); });
  lb.querySelector('.next').addEventListener('click', function () { show(i + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  // Glisser du doigt (uniquement dans la visionneuse)
  var x0 = null, y0 = null;
  lb.addEventListener('touchstart', function (e) { if (e.touches.length === 1) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; } }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) show(dx < 0 ? i + 1 : i - 1);
    else if (dy > 90 && Math.abs(dy) > Math.abs(dx) * 1.5) close();
    x0 = y0 = null;
  });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
    if (e.key === 'Tab') {
      var f = lb.querySelectorAll('button, a.dl'), first = f[0], lastB = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastB.focus(); }
      else if (!e.shiftKey && document.activeElement === lastB) { e.preventDefault(); first.focus(); }
    }
  });
})();

// ------------------------------------------------------------
// Bouton « Imprimer la liste »
document.querySelectorAll('[data-print]').forEach(function (b) {
  b.addEventListener('click', function () { window.print(); });
});

// ------------------------------------------------------------
// Statut de la bourse (page Bourse)
(function () {
  var el = document.getElementById('bourse-status');
  if (!el) return;
  var t = function (s) { return new Date(s).getTime(); };
  var phases = [
    [t('2026-10-30T09:00:00+01:00'), 'Dépôt ouvert vendredi à 9h00'],
    [t('2026-10-30T20:00:00+01:00'), 'Dépôt ouvert jusqu’à 20h00'],
    [t('2026-10-31T08:00:00+01:00'), 'Dépôt samedi de 8h00 à 11h30'],
    [t('2026-10-31T11:30:00+01:00'), 'Dépôt ouvert jusqu’à 11h30'],
    [t('2026-10-31T14:00:00+01:00'), 'Vente samedi à partir de 14h00'],
    [t('2026-10-31T19:30:00+01:00'), 'Vente ouverte jusqu’à 19h30'],
    [t('2026-11-01T09:00:00+01:00'), 'Vente dimanche à partir de 9h00'],
    [t('2026-11-01T16:30:00+01:00'), 'Vente ouverte jusqu’à 16h30'],
    [t('2026-11-01T18:30:00+01:00'), 'Restitution dimanche à 18h30'],
    [t('2026-11-01T19:15:00+01:00'), 'Restitution en cours jusqu’à 19h15']
  ];
  var now = Date.now(), msg = 'La bourse 2026 est terminée. Merci à tous !';
  for (var k = 0; k < phases.length; k++) { if (now < phases[k][0]) { msg = phases[k][1]; break; } }
  el.textContent = msg;
})();

// ------------------------------------------------------------
// Parcours de la saison : centrer la sortie affichée (mobile)
(function () {
  var cur = document.querySelector('.track a[aria-current="page"]');
  var t = document.querySelector('.track');
  if (cur && t && t.scrollWidth > t.clientWidth) {
    t.scrollLeft = cur.offsetLeft - t.clientWidth / 2 + cur.offsetWidth / 2;
  }
})();
