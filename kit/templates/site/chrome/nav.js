(function() {
  var toggle = document.getElementById('lttNavToggle');
  var drawer = document.getElementById('lttMobileDrawer');

  if (toggle && drawer && !toggle._lttBound) {
    toggle._lttBound = true;
    toggle.addEventListener('click', function(e) {
      e.stopPropagation();
      var isOpen = drawer.classList.contains('is-open');
      if (isOpen) {
        drawer.classList.remove('is-open');
        toggle.classList.remove('is-active');
        toggle.setAttribute('aria-expanded', 'false');
        drawer.setAttribute('aria-hidden', 'true');
        drawer.setAttribute('inert', '');
        drawer.setAttribute('inert', '');
        document.body.classList.remove('ltt-drawer-open');
      } else {
        drawer.classList.add('is-open');
        toggle.classList.add('is-active');
        toggle.setAttribute('aria-expanded', 'true');
        drawer.setAttribute('aria-hidden', 'false');
        drawer.removeAttribute('inert');
        drawer.removeAttribute('inert');
        document.body.classList.add('ltt-drawer-open');
      }
    });

    drawer.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        drawer.classList.remove('is-open');
        toggle.classList.remove('is-active');
        toggle.setAttribute('aria-expanded', 'false');
        drawer.setAttribute('aria-hidden', 'true');
        drawer.setAttribute('inert', '');
        drawer.setAttribute('inert', '');
        document.body.classList.remove('ltt-drawer-open');
      });
    });
  }

  var drops = Array.prototype.slice.call(document.querySelectorAll('.ltt-nav-dropdown'));
  function setOpen(d, on) {
    d.classList.toggle('is-open', on);
    var b = d.querySelector('.ltt-dropdown-btn');
    if (b) b.setAttribute('aria-expanded', on ? 'true' : 'false');
  }
  drops.forEach(function(d) {
    if (d._bound) return;
    d._bound = true;
    var t = null;
    var btn = d.querySelector('.ltt-dropdown-btn');
    d.addEventListener('mouseenter', function() {
      if (t) { clearTimeout(t); t = null; }
      drops.forEach(function(o) { if (o !== d) setOpen(o, false); });
      setOpen(d, true);
    });
    d.addEventListener('mouseleave', function() { t = setTimeout(function() { setOpen(d, false); }, 120); });
    if (btn) btn.addEventListener('click', function(e) {
      e.preventDefault();
      var on = !d.classList.contains('is-open');
      drops.forEach(function(o) { setOpen(o, false); });
      setOpen(d, on);
    });
  });
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.ltt-nav-dropdown')) drops.forEach(function(o) { setOpen(o, false); });
  });
  // menu thumbnails load only once a menu is first opened
  var thumbsLoaded = false;
  function loadThumbs() {
    if (thumbsLoaded) return;
    thumbsLoaded = true;
    document.querySelectorAll('img.ltt-thumb[data-src]').forEach(function(im) { im.src = im.getAttribute('data-src'); });
  }
  drops.forEach(function(d) { d.addEventListener('mouseenter', loadThumbs); d.addEventListener('focusin', loadThumbs); d.addEventListener('touchstart', loadThumbs, {passive: true}); });
  if (toggle) toggle.addEventListener('click', loadThumbs);

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') drops.forEach(function(o) { setOpen(o, false); });
  });

  // CANONICAL ACTIVE PAGE HIGHLIGHTER
  try {
    var rawPath = (window.location.pathname || '/').replace(/\/$/, '') || '/';
    var normPath = rawPath.replace(/\.html$/, '');
    
    var isRiver = (normPath.indexOf('river-cruise') !== -1 || normPath.indexOf('setahajozas-a-dunan-budapest') !== -1 || normPath.indexOf('bootsfahrten-dunau') !== -1 || normPath.indexOf('croisieres-danube') !== -1 || normPath.indexOf('riecne-plavby') !== -1 || normPath.indexOf('rejsy-dunaju') !== -1 || normPath.indexOf('rechnyye-kruizy') !== -1) && normPath.indexOf('dinner') === -1 && normPath.indexOf('vacsoraval') === -1 && normPath.indexOf('abendessen') === -1;
    var isDinner = normPath.indexOf('dinner-cruise') !== -1 || normPath.indexOf('vacsoraval') !== -1 || normPath.indexOf('candlelit') !== -1 || normPath.indexOf('abendessen') !== -1 || normPath.indexOf('diner-croisiere') !== -1 || normPath.indexOf('cena-danubio') !== -1 || normPath.indexOf('kolacja') !== -1 || normPath.indexOf('vecera-plavby') !== -1;
    var isCard = normPath.indexOf('budapest-card') !== -1;
    var isAbout = normPath.indexOf('/about') !== -1 || normPath.indexOf('/rolunk') !== -1 || normPath.indexOf('/körülbelül') !== -1;
    var isContact = normPath.indexOf('/contact') !== -1 || normPath.indexOf('/kapcsolat') !== -1 || normPath.indexOf('/érintkezés') !== -1;

    var navLinks = document.querySelectorAll('.ltt-nav-links .ltt-nav-link:not(.ltt-dropdown-btn), .ltt-mobile-drawer .ltt-mobile-link');
    navLinks.forEach(function(el) {
      var href = el.getAttribute('href');
      if (!href) return;
      var hClean = href.replace(/\/$/, '').replace(/\.html$/, '') || '/';
      
      var match = false;
      if (normPath === hClean) {
        match = true;
      } else if (isRiver && (hClean.indexOf('river-cruise') !== -1 || hClean.indexOf('setahajozas-a-dunan-budapest') !== -1 || hClean.indexOf('bootsfahrten-dunau') !== -1)) {
        match = true;
      } else if (isDinner && (hClean.indexOf('dinner-cruise') !== -1 || hClean.indexOf('setahajozas-a-dunan-vacsoraval') !== -1 || hClean.indexOf('bootsfahrten-mit-abendessen') !== -1)) {
        match = true;
      } else if (isCard && hClean.indexOf('budapest-card') !== -1) {
        match = true;
      } else if (isAbout && (hClean.indexOf('/about') !== -1 || hClean.indexOf('/rolunk') !== -1)) {
        match = true;
      } else if (isContact && (hClean.indexOf('/contact') !== -1 || hClean.indexOf('/kapcsolat') !== -1)) {
        match = true;
      }
      
      if (match) {
        el.classList.add('active');
        el.setAttribute('aria-current', 'page');
      } else if (hClean !== '/' && !hClean.match(/^\/[a-z]{2}$/)) {
        el.classList.remove('active');
        el.removeAttribute('aria-current');
      }
    });
    var cur = document.querySelector('.ltt-mobile-acc .ltt-mobile-link.active');
    if (cur) cur.closest('.ltt-mobile-acc').open = true;
  } catch(e) {}

})();
