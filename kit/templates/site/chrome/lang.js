(function() {
  window.lttToggleLangDropdown = function() {
    var dd = document.getElementById('lttLangDropdown');
    var btn = document.getElementById('lttLangBtn');
    if (!dd || !btn) return;
    var isOpen = dd.classList.contains('show');
    if (isOpen) {
      dd.classList.remove('show');
      btn.classList.remove('is-active');
      btn.setAttribute('aria-expanded', 'false');
    } else {
      dd.classList.add('show');
      btn.classList.add('is-active');
      btn.setAttribute('aria-expanded', 'true');
    }
  };

  document.addEventListener('click', function(e) {
    var trigger = document.getElementById('lttLangTrigger');
    var dd = document.getElementById('lttLangDropdown');
    var btn = document.getElementById('lttLangBtn');
    if (trigger && dd && !trigger.contains(e.target)) {
      dd.classList.remove('show');
      if (btn) {
        btn.classList.remove('is-active');
        btn.setAttribute('aria-expanded', 'false');
      }
    }
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      var dd = document.getElementById('lttLangDropdown');
      var btn = document.getElementById('lttLangBtn');
      if (dd && dd.classList.contains('show')) {
        dd.classList.remove('show');
        if (btn) {
          btn.classList.remove('is-active');
          btn.setAttribute('aria-expanded', 'false');
        }
      }
    }
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
  } catch(e) {}

})();
