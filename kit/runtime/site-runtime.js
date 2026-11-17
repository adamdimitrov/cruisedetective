/* site-runtime.js — shared front-end runtime for every site (github.com/adamdimitrov/site-kit).
 * Do not edit the copy in a site's /js/: change runtime/site-runtime.js in site-kit and run
 * python3 kit/update.py. Loaded where the inline page runtime used to be, synchronously, so
 * execution order is unchanged. Reads window.LTT_PAGE_CONFIG set by the page just before it.
 * Parts: 1) page runtime (sliders, filters, TOC, sticky bar), 2) slider lazy-load fallbacks.
 * Page options (window.LTT_PAGE_CONFIG): deckId, tocDeckLabel, tocBreakdownLabel, tocGuideLabel,
 * shortTitles, tocSubHeadings (list h2[id] inside a section too), filterSummary ('{visible} of
 * {total} for {filter}'), pickBadge ('#{n} PICK'), pickLabel, pickBadgeFromTag, alsoLabel,
 * stickyUntil ('reviews'|'footer'), btnText, stickyCtaRewrite, stickyCtaFromCard, preloadSliders.
 */

/* ---- 1. page runtime ---- */
/* ==========================================================================
   LUXURY EDITORIAL SYSTEM — UNIFIED PAGE RUNTIME
   Handles: Sliders, Filter Tabs, Accordion Controls, Desktop TOC Scrollspy,
   Hybrid Sticky Bottom Bar, Mobile Bottom Sheet TOC, & Dynamic Smooth Scroll
   ========================================================================== */
(function() {
  var cfg = window.LTT_PAGE_CONFIG || {};
  var deckId = cfg.deckId || 'dubai-safari-deck';
  var tocDeckLabel = cfg.tocDeckLabel || 'Top 10 Comparison';
  var tocBreakdownLabel = cfg.tocBreakdownLabel || 'Detailed Breakdown';
  var shortTitles = cfg.shortTitles || [];

  // 0. Purge a leftover Webflow badge (sites were exported from Webflow)
  function purgeWebflowBadge() {
    var badges = document.querySelectorAll('.w-webflow-badge, [class*="webflow-badge"], a[href*="webflow.com?utm_campaign=brandjs"]');
    badges.forEach(function(el) { el.remove(); });
  }
  purgeWebflowBadge();
  document.addEventListener('DOMContentLoaded', purgeWebflowBadge);
  window.addEventListener('load', purgeWebflowBadge);
  if (window.MutationObserver) {
    new MutationObserver(purgeWebflowBadge).observe(document.documentElement, { childList: true, subtree: true });
  }

  // 1. Slider controls with Progressive Lazy-Loading
  function loadSliderImages(slider) {
    if (!slider || slider._loaded) return;
    slider._loaded = true;
    var lazyImgs = slider.querySelectorAll('img[data-src]');
    for (var i = 0; i < lazyImgs.length; i++) {
      var img = lazyImgs[i];
      if (img.getAttribute('data-srcset')) {
        img.setAttribute('srcset', img.getAttribute('data-srcset'));
        img.removeAttribute('data-srcset');
      }
      img.src = img.getAttribute('data-src');
      img.removeAttribute('data-src');
    }
  }

  window.bpaSlide = function(btn, dir) {
    var media = btn.closest('.bpa-media');
    if (!media) return;
    var slider = media.querySelector('.bpa-slider');
    if (!slider) return;
    loadSliderImages(slider);
    var first = slider.firstElementChild;
    var w = first ? first.getBoundingClientRect().width + (parseFloat(getComputedStyle(slider).columnGap) || 0) : slider.clientWidth;
    // right-to-left pages (Hebrew) scroll towards negative scrollLeft, so "next" goes left
    var rtl = getComputedStyle(slider).direction === 'rtl' ? -1 : 1;
    slider.scrollBy({ left: dir * w * rtl, behavior: 'smooth' });
  };

  window.bpaCount = function(slider, pillOnly) {
    if (!pillOnly) loadSliderImages(slider);
    var media = slider.closest('.bpa-media');
    if (!media) return;
    // older guide pages (airport, parliament, things to do, statistics) name it .bpa-counter-pill
    var pill = media.querySelector('.bpa-pill, .bpa-counter-pill');
    if (!pill) return;
    var first = slider.firstElementChild;
    var w = (first ? first.getBoundingClientRect().width + (parseFloat(getComputedStyle(slider).columnGap) || 0) : slider.clientWidth) || 1;
    var slides = slider.children;
    var photos = slider.querySelectorAll('img').length;
    var i = Math.min(Math.round(Math.abs(slider.scrollLeft) / w), slides.length - 1);
    pill.textContent = Math.min(i + 1, photos) + ' / ' + photos;
    var cap = media.querySelector('.bpa-cap');
    if (cap) cap.textContent = (slides[i] && slides[i].getAttribute('data-cap')) || '';
  };

  // set every pill once on load without fetching lazy photos (they load on first swipe/tap)
  // (single-photo carousels are skipped: their .bpa-pill can be a text label, not a counter)
  document.querySelectorAll('.bpa-card .bpa-slider').forEach(function(sl) { if (sl.children.length > 1) window.bpaCount(sl, true); });

  // 1b. Bento Filmstrip Desktop & Mobile Slider Controls
  window.lttFilmSync = function(strip) {
    if (!strip) return;
    requestAnimationFrame(function() {
      var wrap = strip.closest('.ltt-filmstrip-wrap');
      if (!wrap) return;
      var prevBtn = wrap.querySelector('.ltt-film-prev');
      var nextBtn = wrap.querySelector('.ltt-film-next');
      var maxScroll = strip.scrollWidth - strip.clientWidth;
      if (prevBtn) {
        prevBtn.classList.toggle('is-disabled', maxScroll <= 6 || strip.scrollLeft <= 6);
      }
      if (nextBtn) {
        nextBtn.classList.toggle('is-disabled', maxScroll <= 6 || strip.scrollLeft >= maxScroll - 6);
      }
    });
  };

  window.lttFilmSlide = function(btn, dir) {
    var wrap = btn.closest('.ltt-filmstrip-wrap');
    if (!wrap) return;
    var strip = wrap.querySelector('.ltt-filmstrip');
    if (!strip) return;
    var slide = strip.querySelector('.ltt-strip-slide');
    var step = slide ? (slide.offsetWidth + 12) : Math.round(strip.clientWidth * 0.75);
    strip.scrollBy({ left: dir * step, behavior: 'smooth' });
    setTimeout(function() { window.lttFilmSync(strip); }, 260);
  };

  function initAllFilmstrips() {
    requestAnimationFrame(function() {
      document.querySelectorAll('.ltt-filmstrip').forEach(function(strip) {
        window.lttFilmSync(strip);
        if (!strip._filmBound) {
          strip._filmBound = true;
          strip.addEventListener('scroll', function() {
            window.lttFilmSync(strip);
          }, { passive: true });
        }
      });
    });
  }

  // 2. Filter tabs (Single-select buyer intent + Detailed Breakdown sync)
  var activeCat = 'all';
  var defaultBreakdownSub = null;

  function getBtnCat(b) {
    var dc = b.getAttribute('data-cat');
    if (dc) return dc;
    var oc = b.getAttribute('onclick') || '';
    var m = oc.match(/['"]([^'"]+)['"]/);
    return m ? m[1] : '';
  }

  function cardMatchesCat(cardCatStr, cat) {
    if (!cat || cat === 'all') return true;
    var tokens = (cardCatStr || '').split(/\s+/);
    return tokens.indexOf(cat) !== -1;
  }

  // Two modes. Grouped: when any pill carries data-group, pills combine across groups (one
  // choice per group) and each pill shows its live count. Single: the classic one-at-a-time
  // filter. A page with no data-group never enters grouped mode, so ungrouped pills can never
  // all render active (the Nov 2026 bug). check_filters.py enforces data-group on grouped pages.
  var activeSel = {};
  function btnGroup(b) { return b ? (b.getAttribute('data-group') || '') : ''; }
  function groupOf(cat) {
    var b = document.querySelector('.ltt-tab-btn[data-cat="' + cat + '"]');
    return btnGroup(b) || 'fit';
  }
  function matchesSel(catStr, sel) {
    return Object.keys(sel).every(function(g) { return cardMatchesCat(catStr, sel[g]); });
  }
  function selIsAll(sel) {
    return Object.keys(sel).every(function(g) { return sel[g] === 'all'; });
  }

  window.lttFilterItems = function(cat, btn) {
    var buttons = Array.from(document.querySelectorAll('.ltt-tab-btn'));
    var cards = Array.from(document.querySelectorAll('#ltt-cards-deck .bpa-card'));
    var detailsCards = Array.from(document.querySelectorAll('details.bpa-details-card'));
    var groups = [];
    buttons.forEach(function(b) { var g = btnGroup(b); if (g && groups.indexOf(g) === -1) groups.push(g); });
    var grouped = groups.length > 0;
    var sel;

    if (grouped) {
      groups.forEach(function(g) { if (!activeSel[g]) activeSel[g] = 'all'; });
      if (!cat || cat === 'all') {
        groups.forEach(function(g) { activeSel[g] = 'all'; });
      } else {
        var g0 = btnGroup(btn) || groupOf(cat);
        activeSel[g0] = (activeSel[g0] === cat) ? 'all' : cat;
      }
      activeCat = selIsAll(activeSel) ? 'all' : groups.map(function(g) { return activeSel[g]; }).join('|');
      sel = activeSel;
    } else {
      // Toggle: clicking the active non-all filter returns to 'all'
      if (activeCat === cat && cat !== 'all') {
        activeCat = 'all';
      } else {
        activeCat = cat || 'all';
      }
      sel = { fit: activeCat };
    }

    buttons.forEach(function(b) {
      var bCat = getBtnCat(b);
      if (!grouped) {
        b.classList.toggle('active', bCat === activeCat);
        return;
      }
      var g = btnGroup(b);
      var isActive = g ? activeSel[g] === bCat : activeCat === 'all';
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      var cnt = b.querySelector('.ltt-cnt');
      if (cnt) {
        var trial = {};
        groups.forEach(function(x) { trial[x] = g ? activeSel[x] : 'all'; });
        if (g) trial[g] = bCat;
        var n = cards.filter(function(c) { return matchesSel(c.getAttribute('data-cat'), trial); }).length;
        cnt.textContent = '(' + n + ')';
        b.classList.toggle('is-empty', n === 0 && !isActive);
        b.disabled = (n === 0 && !isActive);
      }
    });

    var visibleCount = 0;
    cards.forEach(function(card, i) {
      var show = matchesSel(card.getAttribute('data-cat'), sel);
      card.style.display = show ? 'block' : 'none';
      if (show) visibleCount++;
      if (detailsCards[i]) {
        var detCat = detailsCards[i].getAttribute('data-cat') || card.getAttribute('data-cat') || '';
        var detShow = matchesSel(detCat, sel);
        detailsCards[i].style.display = detShow ? 'block' : 'none';
        var detId = detailsCards[i].id;
        if (detId) {
          document.querySelectorAll('#toc a[href="#' + detId + '"], #hybridSheetList a[href="#' + detId + '"]').forEach(function(lk) {
            lk.classList.toggle('is-filtered', !detShow);
          });
        }
      }
    });

    // hide the "Also sailing" headings when nothing under them is visible
    ['also-sailing', 'also-sailing-details'].forEach(function(id) {
      var h = document.getElementById(id);
      if (!h) return;
      var any = false, el = h.nextElementSibling;
      while (el) {
        if (el.matches && el.matches('.bpa-card, details.bpa-details-card') && el.style.display !== 'none') { any = true; break; }
        el = el.nextElementSibling;
      }
      h.style.display = any ? '' : 'none';
      var sub = h.nextElementSibling;
      if (sub && sub.classList.contains('xmas-also-sub')) sub.style.display = any ? '' : 'none';
    });

    var subEl = document.querySelector('.bpa-breakdown-sub');
    if (subEl) {
      if (defaultBreakdownSub === null) {
        defaultBreakdownSub = subEl.textContent;
      }
      if (activeCat === 'all') {
        subEl.textContent = defaultBreakdownSub;
      } else {
        var filterLabel;
        if (grouped) {
          filterLabel = groups.filter(function(g) { return activeSel[g] !== 'all'; }).map(function(g) {
            var b = buttons.find(function(x) { return getBtnCat(x) === activeSel[g]; });
            return b ? b.getAttribute('data-label') : activeSel[g];
          }).join(' + ');
        } else {
          var activeBtn = buttons.find(function(b) { return getBtnCat(b) === activeCat; });
          filterLabel = activeBtn ? activeBtn.textContent.trim() : activeCat;
        }
        subEl.textContent = cfg.filterSummary
          ? cfg.filterSummary.replace('{visible}', visibleCount).replace('{total}', cards.length).replace('{filter}', filterLabel)
          : (grouped
            ? 'Showing ' + visibleCount + ' of ' + cards.length + ' tours: ' + filterLabel + ' • All reviews open by default'
            : 'Showing ' + visibleCount + ' of ' + cards.length + ' cruises matching ' + filterLabel + ' • All reviews open by default');
      }
    }
    updateActiveTOC();
  };
  window.lttFilterSafaris = window.lttFilterItems;
  window.lttFilterCruises = window.lttFilterItems;
  window.lttFilterHelicopters = window.lttFilterItems;
  window.lttFilterHotels = window.lttFilterItems;
  (function initFilterCounts() {
    var run = function() {
      if (!document.querySelector('.ltt-tab-btn[data-group]')) return;
      try { window.lttFilterItems('all'); } catch (e) {}
    };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
    else setTimeout(run, 0);
  })();

  // 3. Extract structured items list from Cards & Editorial Guide Sections
  function getItems() {
    return Array.from(document.querySelectorAll('.bpa-card:not(.bpa-mkt)')).map(function(card, i) {
      var sub = card.querySelector('.bpa-sublink');
      var id = sub ? sub.getAttribute('href').replace('#', '') : '';
      var kicker = card.querySelector('.bpa-kicker');
      var head = card.querySelector('.bpa-title');
      var btn = card.querySelector('.bpa-btn');
      var tag = card.querySelector('.bpa-rank-tag');
      var p = card.querySelector('.bpa-price');
      var psub = card.querySelector('.bpa-psub');
      var kp = kicker ? kicker.textContent.split('•') : [];
      var rawTag = tag ? tag.textContent.trim() : '';
      var cleanLabel = rawTag.replace(/^[^\w#]+/, '').replace(/^#\d+\s*/, '').trim();
      return {
        id: id,
        r: String(i + 1),
        badge: cfg.pickBadgeFromTag
          ? (/#\d/.test(rawTag) ? rawTag.match(/#\d+/)[0] + ' ' + (cfg.pickLabel || 'PICK') : (cfg.alsoLabel || 'ALSO SAILING'))
          : cfg.pickBadge ? cfg.pickBadge.replace('{n}', i + 1) : '#' + (i + 1) + ' ' + (cfg.pickLabel || 'PICK'),
        bt: btn ? btn.textContent.trim() : '',
        tag: rawTag,
        label: cleanLabel,
        name: shortTitles[i] || (kp[0] ? kp[0].trim() : ''),
        p: p ? p.textContent.trim() : '',
        d: (kp[1] ? kp[1].trim() : '') + (psub ? ' • ' + psub.textContent.trim() : ''),
        l: btn ? btn.href : (head ? head.href : ''),
        t: (i + 1) + '. ' + (head ? head.textContent.trim() : '')
      };
    });
  }

  function getEditorialSections() {
    var sections = [];
    document.querySelectorAll('.ltt-editorial-wrapper section[id]').forEach(function(sec) {
      var id = sec.id;
      var h2 = sec.querySelector('h2');
      if (!id || !h2) return;
      var rawText = h2.textContent.replace(/\s+/g, ' ').trim();
      var shortText = rawText.indexOf(':') !== -1 ? rawText.split(':')[1].trim() : rawText;
      if (shortText.length > 42) shortText = rawText.split(':')[0].trim();
      sections.push({ id: id, text: sec.getAttribute('data-toc') || shortText, fullText: rawText });
      if (cfg.tocSubHeadings) sec.querySelectorAll('h2[id]').forEach(function(h) {
        if (h === h2) return;
        var t = h.textContent.replace(/\s+/g, ' ').trim();
        sections.push({ id: h.id, text: h.getAttribute('data-toc') || t, fullText: t });
      });
    });
    return sections;
  }

  // 4. Details Toggle Controls
  window.toggleAllDetails = function(openAll) {
    document.querySelectorAll('.bpa-details-card').forEach(function(d) {
      d.open = openAll;
    });
    setTimeout(initAllFilmstrips, 60);
    setTimeout(updateActiveTOC, 80);
  };

  // 5. Sync Bottom Sheet TOC
  function syncHybridSheetTOC(itemsList, guideList) {
    var list = document.getElementById('hybridSheetList');
    if (!list) return;
    list.innerHTML = '';

    itemsList.forEach(function(item) {
      var a = document.createElement('a');
      a.className = 'hybrid-toc-link';
      a.href = '#' + item.id;
      var suffix = item.label ? ' (' + item.label + ')' : '';
      a.innerHTML = '<span><strong>#' + item.r + '</strong> · ' + item.name + suffix + '</span><span class="toc-price">' + item.p + '</span>';
      list.appendChild(a);
    });

    if (guideList && guideList.length) {
      var div = document.createElement('div');
      div.className = 'hybrid-toc-divider';
      div.textContent = cfg.tocGuideLabel || "Buyer's Guide & Methodology";
      list.appendChild(div);
      guideList.forEach(function(g) {
        var a = document.createElement('a');
        a.className = 'hybrid-toc-link';
        a.href = '#' + g.id;
        a.innerHTML = '<span>📖 ' + g.text + '</span><span class="toc-price">Guide</span>';
        list.appendChild(a);
      });
    }

    list.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        closeHybridSheet();
      });
    });
  }

  function openHybridSheet() {
    var backdrop = document.getElementById('hybridBackdrop');
    if (backdrop) backdrop.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    updateActiveTOC();
    var activeLink = document.querySelector('#hybridSheetList .hybrid-toc-link.is-active');
    if (activeLink && activeLink.scrollIntoView) {
      setTimeout(function() {
        activeLink.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }, 60);
    }
  }

  function closeHybridSheet() {
    var backdrop = document.getElementById('hybridBackdrop');
    if (backdrop) backdrop.classList.remove('is-open');
    document.body.style.overflow = '';
  }
  window.openHybridSheet = openHybridSheet;
  window.closeHybridSheet = closeHybridSheet;

  function initHybridSheet() {
    var btn = document.getElementById('hybridTocBtn');
    var closeBtn = document.getElementById('hybridCloseBtn');
    var backdrop = document.getElementById('hybridBackdrop');
    if (btn && !btn._bound) {
      btn._bound = true;
      btn.addEventListener('click', openHybridSheet);
    }
    if (closeBtn && !closeBtn._bound) {
      closeBtn._bound = true;
      closeBtn.addEventListener('click', closeHybridSheet);
    }
    if (backdrop && !backdrop._bound) {
      backdrop._bound = true;
      backdrop.addEventListener('click', function(e) {
        if (e.target === backdrop) closeHybridSheet();
      });
    }
  }

  // 6. Sync Desktop Sidebar TOC & Deterministic Real-Time ScrollSpy
  var _tocTargetIds = [];
  var _lastActiveTocId = null;

  function syncSidebarTOC() {
    var toc = document.querySelector('#toc');
    if (!toc || toc.getAttribute('data-synced') === 'true') return;
    var itemsData = getItems();
    if (!itemsData.length) return;
    var guideSections = getEditorialSections();

    var items = [
      { id: deckId, text: tocDeckLabel },
      { id: 'breakdown-header', text: tocBreakdownLabel }
    ];
    itemsData.forEach(function(s) {
      items.push({ id: s.id, text: s.r + '. ' + s.name });
    });

    toc.innerHTML = '';
    var frag = document.createDocumentFragment();
    items.forEach(function(it) {
      var a = document.createElement('a');
      a.className = 'tocitem';
      a.href = '#' + it.id;
      a.textContent = it.text;
      frag.appendChild(a);
    });

    if (guideSections.length) {
      var grp = document.createElement('div');
      grp.className = 'toc-group-label';
      grp.textContent = cfg.tocGuideLabel || "Buyer's Guide & Methodology";
      frag.appendChild(grp);
      guideSections.forEach(function(g) {
        var a = document.createElement('a');
        a.className = 'tocitem';
        a.href = '#' + g.id;
        a.textContent = g.text;
        frag.appendChild(a);
        items.push({ id: g.id, text: g.text });
      });
    }

    toc.appendChild(frag);
    toc.setAttribute('data-synced', 'true');
    _tocTargetIds = items.map(function(it) { return it.id; });
    syncHybridSheetTOC(itemsData, guideSections);

    var leftCol = toc.closest('.content-left');
    if (leftCol) leftCol.style.display = 'block';
    updateActiveTOC();
  }

  function updateActiveTOC() {
    var toc = document.getElementById('toc');
    if (!toc || !_tocTargetIds.length) return;
    var probeY = 165;
    var activeId = _tocTargetIds[0];

    for (var i = 0; i < _tocTargetIds.length; i++) {
      var id = _tocTargetIds[i];
      var el = document.getElementById(id);
      if (!el || el.style.display === 'none') continue;
      var r = el.getBoundingClientRect();
      if (r.top <= probeY) {
        activeId = id;
      }
    }

    // If user is between the comparison deck and the detailed breakdown (intro paragraphs), highlight Top 10 Comparison
    var brk = document.getElementById('breakdown-header');
    if (brk && brk.getBoundingClientRect().top > probeY) {
      activeId = deckId;
    }

    if (activeId !== _lastActiveTocId) {
      _lastActiveTocId = activeId;
      toc.querySelectorAll('.tocitem').forEach(function(a) {
        var isMatch = (a.getAttribute('href') === '#' + activeId);
        a.classList.toggle('active', isMatch);
        if (isMatch && toc.scrollHeight > toc.clientHeight) {
          var aTop = a.offsetTop;
          var aBot = aTop + a.offsetHeight;
          if (aTop < toc.scrollTop + 20) {
            toc.scrollTo({ top: Math.max(0, aTop - 24), behavior: 'smooth' });
          } else if (aBot > toc.scrollTop + toc.clientHeight - 20) {
            toc.scrollTo({ top: aBot - toc.clientHeight + 24, behavior: 'smooth' });
          }
        }
      });
      var sheetList = document.getElementById('hybridSheetList');
      if (sheetList) {
        sheetList.querySelectorAll('.hybrid-toc-link').forEach(function(a) {
          a.classList.toggle('is-active', a.getAttribute('href') === '#' + activeId);
        });
      }
    }
  }

  // 7. Update Floating Sticky Bottom Bar
  function updateFloatingCTA() {
    var bar = document.getElementById('sticky-bar') || document.querySelector('.hybrid-sticky-bar');
    if (!bar) return;
    if (document.body.classList.contains('ltt-drawer-open')) {
      bar.classList.remove('visible', 'is-visible');
      return;
    }
    var cards = document.querySelectorAll('.bpa-card:not(.bpa-mkt)');
    var reviews = document.querySelectorAll('.bpa-details-card');
    if (!cards.length) return;
    var itemsData = getItems();
    var vCenter = window.innerHeight * 0.45;
    // stickyUntil: 'reviews' (default, hide after the last review) or 'footer' (stay until the footer)
    var hasPassedHero, hideNow;
    if (cfg.stickyUntil === 'footer') {
      var footer = document.querySelector('footer');
      hasPassedHero = (window.scrollY > 300);
      hideNow = footer ? (footer.getBoundingClientRect().top < (window.innerHeight - 20)) : false;
    } else {
      var lastRev = reviews.length ? reviews[reviews.length - 1] : cards[cards.length - 1];
      hasPassedHero = (window.scrollY > 350);
      hideNow = (lastRev.getBoundingClientRect().bottom < 100);
    }
    if (!hasPassedHero || hideNow) {
      bar.classList.remove('visible', 'is-visible');
      return;
    }

    var activeIdx = 0, minDistance = Infinity, foundContaining = false;
    cards.forEach(function(card, i) {
      if (card.style.display === 'none') return;
      var r = card.getBoundingClientRect();
      if (r.top <= vCenter && r.bottom >= vCenter) {
        activeIdx = i;
        foundContaining = true;
      } else if (!foundContaining) {
        var dist = Math.abs(r.top + r.height / 2 - vCenter);
        if (dist < minDistance) {
          minDistance = dist;
          activeIdx = i;
        }
      }
    });

    reviews.forEach(function(rev, i) {
      if (rev.style.display === 'none') return;
      var r = rev.getBoundingClientRect();
      if (r.top <= vCenter && r.bottom >= vCenter) {
        activeIdx = i;
        foundContaining = true;
      } else if (!foundContaining) {
        var dist = Math.abs(r.top + r.height / 2 - vCenter);
        if (dist < minDistance) {
          minDistance = dist;
          activeIdx = i;
        }
      }
    });

    var active = itemsData[activeIdx];
    if (active) {
      var rankEl = document.getElementById('sticky-rank');
      if (rankEl) rankEl.textContent = active.badge;
      var nameEl = document.getElementById('sticky-name');
      if (nameEl) nameEl.textContent = active.name;
      var priceEl = document.getElementById('sticky-price');
      if (priceEl) priceEl.textContent = active.p;
      var ctaEl = document.getElementById('sticky-cta-btn');
      if (ctaEl) {
        ctaEl.href = cfg.stickyCtaRewrite ? active.l.replace('-card-button-', '-sticky-cta-') : active.l;
        if (cfg.btnText) ctaEl.textContent = cfg.btnText;
        if (cfg.stickyCtaFromCard && active.bt) ctaEl.textContent = active.bt;
      }
      bar.classList.add('visible', 'is-visible');
    }
  }

  // Allow clicking links inside summary without toggling details
  document.addEventListener('click', function(e) {
    var a = e.target.closest('summary a');
    if (a) e.stopPropagation();
  }, true);

  // 8. Dynamic Scroll Tracker (Tracks lazy-loading layout shifts in real time)
  var _activeScrollId = null;
  function smoothScrollToElement(target, offset) {
    if (!target) return;
    offset = (typeof offset === 'number') ? offset : 85;

    // If user clicked a cruise that was hidden by a category filter, reset filter to 'all'
    if (target.style.display === 'none' && activeCat !== 'all') {
      window.lttFilterItems('all');
    }

    var details = target.closest('details');
    if (details) details.open = true;
    if (target.tagName === 'DETAILS') target.open = true;

    if (_activeScrollId) {
      cancelAnimationFrame(_activeScrollId);
      _activeScrollId = null;
    }

    function stopScroll() {
      if (_activeScrollId) {
        cancelAnimationFrame(_activeScrollId);
        _activeScrollId = null;
      }
      cleanup();
    }
    function cleanup() {
      window.removeEventListener('wheel', stopScroll, { passive: true });
      window.removeEventListener('touchmove', stopScroll, { passive: true });
      window.removeEventListener('keydown', stopScroll, { passive: true });
    }
    window.addEventListener('wheel', stopScroll, { passive: true });
    window.addEventListener('touchmove', stopScroll, { passive: true });
    window.addEventListener('keydown', stopScroll, { passive: true });

    var lastScrollY = -1;
    var stuckFrames = 0;
    var settlingFrames = 0;

    function frame() {
      var rect = target.getBoundingClientRect();
      var diff = rect.top - offset;

      if (Math.abs(diff) <= 2) {
        window.scrollBy(0, diff);
        settlingFrames++;
        if (settlingFrames > 8) {
          _activeScrollId = null;
          cleanup();
          return;
        }
        _activeScrollId = requestAnimationFrame(frame);
        return;
      }

      settlingFrames = 0;
      var absDiff = Math.abs(diff);
      var speed;
      if (absDiff > 25000) {
        speed = Math.min(absDiff * 0.35, 4000);
      } else if (absDiff > 5000) {
        speed = Math.min(absDiff * 0.3, 2200);
      } else if (absDiff > 1000) {
        speed = Math.min(absDiff * 0.25, 900);
      } else {
        speed = Math.max(14, Math.min(absDiff * 0.2, 180));
      }

      var move = Math.sign(diff) * Math.min(absDiff, speed);
      window.scrollBy(0, move);

      if (window.scrollY === lastScrollY) {
        stuckFrames++;
        if (stuckFrames > 15) {
          _activeScrollId = null;
          cleanup();
          return;
        }
      } else {
        stuckFrames = 0;
        lastScrollY = window.scrollY;
      }

      _activeScrollId = requestAnimationFrame(frame);
    }

    _activeScrollId = requestAnimationFrame(frame);
  }

  // 9. Smooth Click Handler
  document.addEventListener('click', function(e) {
    var drawer = document.getElementById('lttMobileDrawer');
    var toggle = document.getElementById('lttNavToggle');
    if (drawer && drawer.classList.contains('is-open')) {
      if (e.target.closest('#lttMobileDrawer a')) {
        drawer.classList.remove('is-open');
        if (toggle) {
          toggle.classList.remove('is-active');
          toggle.setAttribute('aria-expanded', 'false');
        }
        drawer.setAttribute('aria-hidden', 'true');
        drawer.setAttribute('inert', '');
        document.body.classList.remove('ltt-drawer-open');
      }
    }
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var hash = a.getAttribute('href');
    if (!hash || hash === '#') return;
    var targetId = hash.substring(1);
    var target = document.getElementById(targetId);
    if (!target && (targetId === 'desert-safaris-breakdown' || targetId === 'breakdown-header')) {
      target = document.getElementById('breakdown-header');
    }
    if (target) {
      e.preventDefault();
      e.stopPropagation();
      smoothScrollToElement(target, 85);
      history.pushState(null, '', hash);
    }
  }, true);

  window.addEventListener('scroll', function() {
    if (!window._flTicking) {
      window._flTicking = true;
      requestAnimationFrame(function() {
        updateFloatingCTA();
        updateActiveTOC();
        window._flTicking = false;
      });
    }
  }, { passive: true });

  var _layoutScheduled = false;
  function scheduleLayoutSync() {
    if (_layoutScheduled) return;
    _layoutScheduled = true;
    requestAnimationFrame(function() {
      _layoutScheduled = false;
      initAllFilmstrips();
      updateFloatingCTA();
      updateActiveTOC();
    });
  }

  window.addEventListener('resize', function() {
    scheduleLayoutSync();
  }, { passive: true });

  function initLazySliders() {
    document.querySelectorAll('.bpa-slider').forEach(function(slider) {
      if (slider._lazyBound) return;
      slider._lazyBound = true;
      var media = slider.closest('.bpa-media');
      if (media) {
        media.addEventListener('mouseenter', function() { loadSliderImages(slider); }, { once: true, passive: true });
        media.addEventListener('touchstart', function() { loadSliderImages(slider); }, { once: true, passive: true });
      }
      slider.addEventListener('scroll', function() { loadSliderImages(slider); }, { once: true, passive: true });
    });
  }

  function initAll() {
    initLazySliders();
    initHybridSheet();
    syncSidebarTOC();
    scheduleLayoutSync();
    if (window.location.hash) {
      var h = window.location.hash.substring(1);
      var el = document.getElementById(h) || (h === 'desert-safaris-breakdown' ? document.getElementById('breakdown-header') : null);
      if (el) {
        setTimeout(function() {
          smoothScrollToElement(el, 85);
        }, 150);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
  window.addEventListener('load', initAll);
  setTimeout(initAll, 200);
  setTimeout(initAll, 800);
})();

/* ---- 2. slider lazy-load fallbacks ---- */
(function() {
  function loadSliderImages(slider) {
    if (!slider || slider._loaded) return;
    slider._loaded = true;
    var lazyImgs = slider.querySelectorAll('img[data-src]');
    for (var i = 0; i < lazyImgs.length; i++) {
      var img = lazyImgs[i];
      if (img.getAttribute('data-srcset')) {
        img.setAttribute('srcset', img.getAttribute('data-srcset'));
        img.removeAttribute('data-srcset');
      }
      img.src = img.getAttribute('data-src');
      img.removeAttribute('data-src');
    }
  }
  window._loadSliderImages = loadSliderImages;

  // Optional (page config preloadSliders): fetch a carousel's photos 400px before it reaches
  // the viewport and the first two carousels right away, so photos are ready before a swipe.
  if ((window.LTT_PAGE_CONFIG || {}).preloadSliders) {
    if ('IntersectionObserver' in window) {
      var bpaObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            var el = entry.target;
            var slider = el.classList.contains('bpa-slider') ? el : el.querySelector('.bpa-slider');
            if (slider) {
              loadSliderImages(slider);
              observer.unobserve(el);
            }
          }
        });
      }, { rootMargin: '400px 0px 400px 0px' });
      document.querySelectorAll('.bpa-media, .bpa-slider').forEach(function(el) {
        bpaObserver.observe(el);
      });
    } else {
      document.querySelectorAll('.bpa-slider').forEach(loadSliderImages);
    }
    var initFirstSliders = function() {
      var sliders = document.querySelectorAll('.bpa-slider');
      for (var i = 0; i < Math.min(2, sliders.length); i++) {
        loadSliderImages(sliders[i]);
      }
    };
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initFirstSliders);
    } else {
      initFirstSliders();
    }
  }

  document.addEventListener('click', function(e) {
    var btn = e.target && e.target.closest && e.target.closest('.bpa-arrow, .bpa-prev, .bpa-next, [onclick*="bpaSlide"]');
    if (btn) {
      var media = (btn.closest && btn.closest('.bpa-media, .bpa-slider-wrap, .bpa-gallery')) || btn.parentElement;
      var slider = media ? media.querySelector('.bpa-slider') : null;
      if (slider) loadSliderImages(slider);
    }
  }, true);

  document.addEventListener('pointerenter', function(e) {
    var target = e.target;
    if (target && target.closest) {
      var media = target.closest('.bpa-media, .bpa-slider');
      if (media) {
        var slider = media.classList.contains('bpa-slider') ? media : media.querySelector('.bpa-slider');
        if (slider) loadSliderImages(slider);
      }
    }
  }, true);

  document.addEventListener('touchstart', function(e) {
    var target = e.target;
    if (target && target.closest) {
      var media = target.closest('.bpa-media, .bpa-slider');
      if (media) {
        var slider = media.classList.contains('bpa-slider') ? media : media.querySelector('.bpa-slider');
        if (slider) loadSliderImages(slider);
      }
    }
  }, { passive: true, capture: true });

  document.addEventListener('scroll', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('bpa-slider')) {
      loadSliderImages(e.target);
    }
  }, { passive: true, capture: true });
  document.addEventListener('wheel', function(e) {
    if (e.target && e.target.closest) {
      var slider = e.target.closest('.bpa-slider');
      if (slider) loadSliderImages(slider);
    }
  }, { passive: true, capture: true });
})();
