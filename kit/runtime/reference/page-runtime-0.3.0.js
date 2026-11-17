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
    var w = slider.clientWidth;
    slider.scrollBy({ left: dir * w, behavior: 'smooth' });
  };

  window.bpaCount = function(slider) {
    loadSliderImages(slider);
    var media = slider.closest('.bpa-media');
    if (!media) return;
    var pill = media.querySelector('.bpa-pill');
    if (!pill) return;
    var w = slider.clientWidth || 1;
    var idx = Math.min(Math.round(slider.scrollLeft / w) + 1, slider.children.length);
    pill.textContent = idx + ' / ' + slider.children.length;
  };

  // 1b. Bento Filmstrip Desktop & Mobile Slider Controls
  window.lttFilmSync = function(strip) {
    if (!strip) return;
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
    document.querySelectorAll('.ltt-filmstrip').forEach(function(strip) {
      window.lttFilmSync(strip);
      if (!strip._filmBound) {
        strip._filmBound = true;
        strip.addEventListener('scroll', function() {
          window.lttFilmSync(strip);
        }, { passive: true });
      }
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

  window.lttFilterItems = function(cat, btn) {
    var buttons = Array.from(document.querySelectorAll('.ltt-tab-btn'));
    var cards = Array.from(document.querySelectorAll('#ltt-cards-deck .bpa-card'));
    var detailsCards = Array.from(document.querySelectorAll('details.bpa-details-card'));

    // Toggle: clicking the active non-all filter returns to 'all'
    if (activeCat === cat && cat !== 'all') {
      activeCat = 'all';
    } else {
      activeCat = cat || 'all';
    }

    buttons.forEach(function(b) {
      var bCat = getBtnCat(b);
      b.classList.toggle('active', bCat === activeCat);
    });

    var visibleCount = 0;
    cards.forEach(function(card, i) {
      var show = cardMatchesCat(card.getAttribute('data-cat'), activeCat);
      card.style.display = show ? 'block' : 'none';
      if (show) visibleCount++;
      if (detailsCards[i]) {
        var detCat = detailsCards[i].getAttribute('data-cat') || card.getAttribute('data-cat') || '';
        var detShow = cardMatchesCat(detCat, activeCat);
        detailsCards[i].style.display = detShow ? 'block' : 'none';
        var detId = detailsCards[i].id;
        if (detId) {
          document.querySelectorAll('#toc a[href="#' + detId + '"], #hybridSheetList a[href="#' + detId + '"]').forEach(function(lk) {
            lk.classList.toggle('is-filtered', !detShow);
          });
        }
      }
    });

    var subEl = document.querySelector('.bpa-breakdown-sub');
    if (subEl) {
      if (defaultBreakdownSub === null) {
        defaultBreakdownSub = subEl.textContent;
      }
      if (activeCat === 'all') {
        subEl.textContent = defaultBreakdownSub;
      } else {
        var activeBtn = buttons.find(function(b) { return getBtnCat(b) === activeCat; });
        var filterLabel = activeBtn ? activeBtn.textContent.trim() : activeCat;
        subEl.textContent = 'Showing ' + visibleCount + ' of ' + cards.length + ' cruises matching ' + filterLabel + ' • All reviews open by default';
      }
    }
    updateActiveTOC();
  };
  window.lttFilterSafaris = window.lttFilterItems;
  window.lttFilterCruises = window.lttFilterItems;
  window.lttFilterHelicopters = window.lttFilterItems;
  window.lttFilterHotels = window.lttFilterItems;

  // 3. Extract structured items list from Cards & Editorial Guide Sections
  function getItems() {
    return Array.from(document.querySelectorAll('.bpa-card')).map(function(card, i) {
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
        badge: '#' + (i + 1) + ' PICK',
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
      sections.push({ id: id, text: shortText, fullText: rawText });
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
      div.textContent = "Buyer's Guide & Methodology";
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
      grp.textContent = "Buyer's Guide & Methodology";
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
    var bar = document.getElementById('sticky-bar');
    if (!bar) return;
    var cards = document.querySelectorAll('.bpa-card');
    var reviews = document.querySelectorAll('.bpa-details-card');
    if (!cards.length) return;
    var itemsData = getItems();
    var vCenter = window.innerHeight * 0.45;
    var lastRev = reviews.length ? reviews[reviews.length - 1] : cards[cards.length - 1];
    var lastBottom = lastRev.getBoundingClientRect().bottom;

    var hasPassedHero = (window.scrollY > 350);
    var isPastReviews = (lastBottom < 100);
    if (!hasPassedHero || isPastReviews) {
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
      if (ctaEl) ctaEl.href = active.l;
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

  window.addEventListener('resize', function() {
    initAllFilmstrips();
  }, { passive: true });

  function initAll() {
    initHybridSheet();
    syncSidebarTOC();
    initAllFilmstrips();
    updateFloatingCTA();
    updateActiveTOC();
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