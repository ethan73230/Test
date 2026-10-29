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
    if (e.key === 'Escape' && n.classList.contains('open')) { n.classList.remove('open'); b.setAttribute('aria-expanded', false); b.focus(); }
  });
})();

// Visionneuse de photos
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.gallery a'));
  if (!links.length) return;
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Photo agrandie');
  lb.innerHTML = '<img alt=""><button class="close" aria-label="Fermer">×</button>' +
    '<button class="prev" aria-label="Photo précédente">‹</button><button class="next" aria-label="Photo suivante">›</button>' +
    '<p class="count" aria-live="polite"></p>';
  document.body.appendChild(lb);
  var img = lb.querySelector('img'), count = lb.querySelector('.count'), i = 0, last = null;
  function show(k) {
    i = (k + links.length) % links.length;
    img.src = links[i].href;
    img.alt = links[i].querySelector('img').alt;
    count.textContent = 'Photo ' + (i + 1) + ' sur ' + links.length;
  }
  function open(k) { last = document.activeElement; show(k); lb.classList.add('open'); lb.querySelector('.close').focus(); document.body.style.overflow = 'hidden'; }
  function close() { lb.classList.remove('open'); img.src = ''; document.body.style.overflow = ''; if (last) last.focus(); }
  links.forEach(function (a, k) { a.addEventListener('click', function (e) { e.preventDefault(); open(k); }); });
  lb.querySelector('.close').addEventListener('click', close);
  lb.querySelector('.prev').addEventListener('click', function () { show(i - 1); });
  lb.querySelector('.next').addEventListener('click', function () { show(i + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
    if (e.key === 'Tab') { // garder le focus dans la visionneuse
      var f = lb.querySelectorAll('button'), first = f[0], lastB = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); lastB.focus(); }
      else if (!e.shiftKey && document.activeElement === lastB) { e.preventDefault(); first.focus(); }
    }
  });
})();

// Statut de la bourse (heure de Paris)
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
