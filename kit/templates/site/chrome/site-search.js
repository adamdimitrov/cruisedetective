/* Site search overlay (shared by The Cruise Detective, Budapest Adventures, Luxury Travel Tester).
   Opened by any [data-ltt-search] button in the header, Ctrl/Cmd+K or "/".
   Searches /search/<lang>.json (built by scripts/sync_layout.py): page titles,
   descriptions and section headings, and links straight to the matching section.
   Bump the ?v= on the <script> tag in the masters after changing this file. */
(function () {
  'use strict';
  if (window.__lttSearch) return;
  window.__lttSearch = true;

  var LANG = ((document.documentElement.lang || 'en').split('-')[0] || 'en').toLowerCase();
  // [placeholder, no results, popular, close, open, move]. A data-placeholder
  // attribute on the search button overrides the placeholder.
  var T = {
    en: ['Search guides, tours and tips', 'No results for', 'Popular guides', 'Close', 'to open', 'to move'],
    hu: ['Keresés a cikkekben és túrákban', 'Nincs találat erre:', 'Népszerű cikkek', 'Bezárás', 'megnyitás', 'mozgás'],
    fr: ['Rechercher guides, visites et conseils', 'Aucun résultat pour', 'Guides populaires', 'Fermer', 'pour ouvrir', 'pour naviguer'],
    de: ['Guides, Touren und Tipps suchen', 'Keine Ergebnisse für', 'Beliebte Guides', 'Schließen', 'öffnen', 'navigieren'],
    es: ['Buscar guías, tours y consejos', 'Sin resultados para', 'Guías populares', 'Cerrar', 'para abrir', 'para moverse'],
    it: ['Cerca guide, tour e consigli', 'Nessun risultato per', 'Guide popolari', 'Chiudi', 'per aprire', 'per spostarti'],
    nl: ['Zoek gidsen, tours en tips', 'Geen resultaten voor', 'Populaire gidsen', 'Sluiten', 'om te openen', 'om te bewegen'],
    pl: ['Szukaj przewodników, wycieczek i porad', 'Brak wyników dla', 'Popularne przewodniki', 'Zamknij', 'aby otworzyć', 'aby przejść'],
    ro: ['Caută ghiduri, tururi și sfaturi', 'Niciun rezultat pentru', 'Ghiduri populare', 'Închide', 'pentru a deschide', 'pentru a naviga'],
    cs: ['Hledat průvodce, výlety a tipy', 'Žádné výsledky pro', 'Oblíbení průvodci', 'Zavřít', 'otevřít', 'pohyb'],
    sk: ['Hľadať sprievodcov, výlety a tipy', 'Žiadne výsledky pre', 'Obľúbení sprievodcovia', 'Zavrieť', 'otvoriť', 'pohyb'],
    pt: ['Pesquisar guias, passeios e dicas', 'Sem resultados para', 'Guias populares', 'Fechar', 'para abrir', 'para mover'],
    ru: ['Поиск гидов, экскурсий и советов', 'Нет результатов для', 'Популярные гиды', 'Закрыть', 'открыть', 'перейти'],
    hr: ['Pretraži vodiče, ture i savjete', 'Nema rezultata za', 'Popularni vodiči', 'Zatvori', 'za otvaranje', 'za kretanje'],
    sr: ['Pretraži vodiče, ture i savete', 'Nema rezultata za', 'Popularni vodiči', 'Zatvori', 'za otvaranje', 'za kretanje'],
    bg: ['Търсене на пътеводители, турове и съвети', 'Няма резултати за', 'Популярни пътеводители', 'Затвори', 'отваряне', 'придвижване'],
    el: ['Αναζήτηση οδηγών, εκδρομών και συμβουλών', 'Κανένα αποτέλεσμα για', 'Δημοφιλείς οδηγοί', 'Κλείσιμο', 'άνοιγμα', 'μετακίνηση'],
    tr: ['Rehber, tur ve ipucu ara', 'Sonuç bulunamadı:', 'Popüler rehberler', 'Kapat', 'açmak için', 'gezinmek için'],
    uk: ['Пошук путівників, екскурсій і порад', 'Немає результатів для', 'Популярні путівники', 'Закрити', 'відкрити', 'перейти'],
    he: ['חיפוש מדריכים, סיורים וטיפים', 'אין תוצאות עבור', 'מדריכים פופולריים', 'סגירה', 'לפתיחה', 'למעבר'],
    ja: ['ガイド・ツアー・ヒントを検索', '該当する結果はありません：', '人気のガイド', '閉じる', '開く', '移動'],
    ko: ['가이드, 투어, 팁 검색', '검색 결과 없음:', '인기 가이드', '닫기', '열기', '이동']
  }[LANG];
  if (!T) {
    LANG = 'en';
    T = ['Search guides, tours and tips', 'No results for', 'Popular guides', 'Close', 'to open', 'to move'];
  }
  var btnPh = document.querySelector('[data-ltt-search][data-placeholder]');
  if (btnPh) T = [btnPh.getAttribute('data-placeholder')].concat(T.slice(1));

  var CSS = [
    '.ltt-search-overlay{position:fixed;inset:0;z-index:2147483000;display:none;background:rgba(15,23,42,.55);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);font-family:"Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,sans-serif}',
    '.ltt-search-overlay.is-open{display:block}',
    '.ltt-search-panel{position:relative;max-width:640px;margin:9vh auto 0;background:#fff;border-radius:16px;box-shadow:0 24px 60px rgba(15,23,42,.35);overflow:hidden;display:flex;flex-direction:column;max-height:78vh}',
    '.ltt-search-field{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid #e2e8f0}',
    '.ltt-search-field svg{flex-shrink:0;color:#9f6e0d}',
    '.ltt-search-input{flex:1;min-width:0;border:0;outline:0;font:500 17px/1.4 inherit;font-family:inherit;color:#0f172a;background:transparent;padding:4px 0}',
    '.ltt-search-input::placeholder{color:#94a3b8}',
    '.ltt-search-close{flex-shrink:0;border:1px solid #cbd5e1;background:#f8fafc;color:#475569;border-radius:8px;font:700 11px/1 inherit;font-family:inherit;padding:6px 8px;cursor:pointer}',
    '.ltt-search-close:hover{border-color:#dfa732;color:#0f172a}',
    '.ltt-search-results{overflow-y:auto;padding:8px;margin:0;list-style:none}',
    '.ltt-search-label{padding:8px 10px 4px;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#94a3b8}',
    '.ltt-search-item a{display:block;padding:10px 12px;border-radius:10px;text-decoration:none!important;color:#0f172a;border-left:3px solid transparent}',
    '.ltt-search-item.is-active a,.ltt-search-item a:hover{background:#fdfaf2;border-left-color:#dfa732}',
    '.ltt-search-title{display:block;font-size:15px;font-weight:700;line-height:1.35}',
    '.ltt-search-sub{display:block;margin-top:3px;font-size:13px;line-height:1.45;color:#64748b;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}',
    '.ltt-search-sub.is-section{color:#9f6e0d;font-weight:600}',
    '.ltt-search-item mark{background:#fdf0cf;color:inherit;border-radius:3px;padding:0 1px}',
    '.ltt-search-empty{padding:22px 14px;color:#64748b;font-size:14px;text-align:center}',
    '.ltt-search-hint{display:flex;gap:16px;justify-content:flex-end;padding:9px 16px;border-top:1px solid #e2e8f0;font-size:11px;color:#94a3b8}',
    '.ltt-search-hint kbd{font-family:inherit;font-weight:700;border:1px solid #e2e8f0;border-radius:4px;padding:1px 5px;margin-right:4px;color:#475569;background:#f8fafc}',
    '@media (max-width:767px){.ltt-search-panel{margin:0;border-radius:0 0 16px 16px;max-height:88vh}.ltt-search-hint{display:none}.ltt-search-input{font-size:16px}}'
  ].join('');

  var overlay, input, list, data = null, loading = null, items = [], active = -1, lastFocus = null;

  function norm(s) {
    return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function highlight(text, tokens) {
    var n = norm(text), marks = [];
    tokens.forEach(function (t) {
      var i = n.indexOf(t);
      while (t && i > -1) { marks.push([i, i + t.length]); i = n.indexOf(t, i + t.length); }
    });
    if (!marks.length) return esc(text);
    marks.sort(function (a, b) { return a[0] - b[0]; });
    var out = '', pos = 0;
    marks.forEach(function (m) {
      if (m[0] < pos) return;
      out += esc(text.slice(pos, m[0])) + '<mark>' + esc(text.slice(m[0], m[1])) + '</mark>';
      pos = m[1];
    });
    return out + esc(text.slice(pos));
  }
  function sectionUrl(url, h) {
    if (h[1]) return url + '#' + encodeURIComponent(h[1]);
    return url + '#:~:text=' + encodeURIComponent(h[0]).replace(/-/g, '%2D');
  }

  function load() {
    if (data || loading) return loading;
    var v = (document.querySelector('script[src*="site-search.js"]') || {}).src || '';
    v = (v.split('?v=')[1] || '1');
    loading = fetch('/search/' + LANG + '.json?v=' + v)
      .then(function (r) { return r.ok ? r.json() : []; })
      .catch(function () { return []; })
      .then(function (d) {
        data = d.map(function (p) {
          var slug = p.u;
          try { slug = decodeURI(p.u); } catch (e) {}
          return { u: p.u, t: p.t, d: p.d, h: p.h, nt: norm(p.t), nd: norm(p.d), ns: norm(slug.replace(/[-\/]/g, ' ')),
            nh: p.h.map(function (h) { return norm(h[0]); }) };
        });
        render();
      });
    return loading;
  }

  function search(q) {
    var tokens = norm(q).split(/\s+/).filter(Boolean);
    if (!tokens.length || !data) return { tokens: tokens, hits: [] };
    var hits = [];
    data.forEach(function (p) {
      var score = 0, best = -1, bestScore = 0;
      for (var k = 0; k < tokens.length; k++) {
        var t = tokens[k], s = 0;
        if (p.nt.indexOf(t) > -1) s += 10;
        if (p.nd.indexOf(t) > -1) s += 3;
        if (p.ns.indexOf(t) > -1) s += 6;
        var inHead = false;
        for (var i = 0; i < p.nh.length; i++) if (p.nh[i].indexOf(t) > -1) { inHead = true; break; }
        if (inHead) s += 4;
        if (!s) return;
        score += s;
      }
      p.nh.forEach(function (nh, i) {
        var c = 0;
        tokens.forEach(function (t) { if (nh.indexOf(t) > -1) c++; });
        if (c > bestScore) { bestScore = c; best = i; }
      });
      var titleAll = tokens.every(function (t) { return p.nt.indexOf(t) > -1; });
      hits.push({ p: p, score: score + (titleAll ? 8 : 0), head: titleAll ? -1 : best });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    return { tokens: tokens, hits: hits.slice(0, 8) };
  }

  function suggestions() {
    var seen = {}, out = [];
    document.querySelectorAll('.ltt-mega-item[href]').forEach(function (a) {
      var href = a.getAttribute('href');
      if (seen[href] || out.length >= 6) return;
      seen[href] = 1;
      var strong = a.querySelector('strong'), p = a.querySelector('p');
      out.push({ url: href, title: (strong ? strong.textContent : a.textContent).trim(), sub: p ? p.textContent.trim() : '' });
    });
    return out;
  }

  function render() {
    if (!list) return;
    var q = input.value.trim();
    var html = '';
    items = [];
    if (!q) {
      var sug = suggestions();
      if (sug.length) html += '<li class="ltt-search-label" role="presentation">' + esc(T[2]) + '</li>';
      sug.forEach(function (s) {
        items.push(s.url);
        html += '<li class="ltt-search-item" role="option"><a href="' + esc(s.url) + '"><span class="ltt-search-title">' + esc(s.title) +
          '</span>' + (s.sub ? '<span class="ltt-search-sub">' + esc(s.sub) + '</span>' : '') + '</a></li>';
      });
    } else if (data) {
      var r = search(q);
      if (!r.hits.length) {
        html = '<li class="ltt-search-empty">' + esc(T[1]) + ' “' + esc(q) + '”</li>';
      }
      r.hits.forEach(function (hit) {
        var p = hit.p, url = p.u, sub;
        if (hit.head > -1) {
          url = sectionUrl(p.u, p.h[hit.head]);
          sub = '<span class="ltt-search-sub is-section">§ ' + highlight(p.h[hit.head][0], r.tokens) + '</span>';
        } else {
          sub = p.d ? '<span class="ltt-search-sub">' + highlight(p.d, r.tokens) + '</span>' : '';
        }
        items.push(url);
        html += '<li class="ltt-search-item" role="option"><a href="' + esc(url) + '"><span class="ltt-search-title">' +
          highlight(p.t, r.tokens) + '</span>' + sub + '</a></li>';
      });
    }
    list.innerHTML = html;
    setActive(items.length ? 0 : -1);
  }

  function setActive(i) {
    var lis = list.querySelectorAll('.ltt-search-item');
    lis.forEach(function (li) { li.classList.remove('is-active'); li.removeAttribute('aria-selected'); });
    active = i;
    if (i > -1 && lis[i]) {
      lis[i].classList.add('is-active');
      lis[i].setAttribute('aria-selected', 'true');
      lis[i].scrollIntoView({ block: 'nearest' });
    }
  }

  function build() {
    var style = document.createElement('style');
    style.id = 'ltt-search-overlay-styles';
    style.textContent = CSS;
    document.head.appendChild(style);
    overlay = document.createElement('div');
    overlay.className = 'ltt-search-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', T[0]);
    overlay.innerHTML =
      '<div class="ltt-search-panel">' +
      '<div class="ltt-search-field"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>' +
      '<input class="ltt-search-input" type="search" autocomplete="off" spellcheck="false" enterkeyhint="go" placeholder="' + esc(T[0]) + '" aria-label="' + esc(T[0]) + '"/>' +
      '<button type="button" class="ltt-search-close" aria-label="' + esc(T[3]) + '">Esc</button></div>' +
      '<ul class="ltt-search-results" role="listbox"></ul>' +
      '<div class="ltt-search-hint"><span><kbd>↑</kbd><kbd>↓</kbd>' + esc(T[5]) + '</span><span><kbd>↵</kbd>' + esc(T[4]) + '</span></div>' +
      '</div>';
    document.body.appendChild(overlay);
    input = overlay.querySelector('.ltt-search-input');
    list = overlay.querySelector('.ltt-search-results');
    overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });
    overlay.querySelector('.ltt-search-close').addEventListener('click', close);
    input.addEventListener('input', function () { load(); render(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (items.length) setActive((active + 1) % items.length); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); if (items.length) setActive((active - 1 + items.length) % items.length); }
      else if (e.key === 'Enter' && active > -1) { e.preventDefault(); go(items[active]); }
    });
    list.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (a) { e.preventDefault(); go(a.getAttribute('href')); }
    });
  }

  function go(url) {
    var here = location.pathname.replace(/\/$/, '') || '/';
    var path = url.split('#')[0];
    close();
    if (decodeURI(path) === decodeURI(here) && url.indexOf('#') > -1) {
      var hash = url.slice(url.indexOf('#'));
      if (hash.indexOf('#:~:') === 0) { location.href = url; return; }
      var el = document.getElementById(decodeURIComponent(hash.slice(1)));
      if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); history.replaceState(null, '', hash); return; }
    }
    location.href = url;
  }

  function open() {
    if (!overlay) build();
    lastFocus = document.activeElement;
    var drawer = document.getElementById('lttMobileDrawer');
    var toggle = document.getElementById('lttNavToggle');
    if (drawer && drawer.classList.contains('is-open') && toggle) toggle.click();
    overlay.classList.add('is-open');
    document.documentElement.style.overflow = 'hidden';
    input.focus();
    render();
    load();
  }

  function close() {
    if (!overlay || !overlay.classList.contains('is-open')) return;
    overlay.classList.remove('is-open');
    document.documentElement.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-ltt-search]');
    if (b) { e.preventDefault(); open(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') return close();
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || '')) || e.target.isContentEditable;
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) { e.preventDefault(); open(); }
    else if (e.key === '/' && !typing) { e.preventDefault(); open(); }
  });
  // Warm the index when the user shows intent, so results appear instantly.
  document.addEventListener('pointerover', function (e) {
    if (e.target.closest && e.target.closest('[data-ltt-search]')) load();
  }, { passive: true });
})();
