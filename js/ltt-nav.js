/* ==========================================================================
   THE CRUISE DETECTIVE — INTERACTIVE CLIENT RUNTIME CONTROLLER
   Zero-dependency, semantic, responsive, WCAG-compliant (Desktop & Mobile)
   Features:
   1. Modern Navigation Header & Mobile Drawer
   2. Media Slider Carousel & Dynamic Counter
   3. Category Filter Tabs (Deck Cards & Detailed Reviews)
   4. Floating Hybrid Sticky Bar (appears after scrolling past hero/deck)
   5. Interactive Bottom-Sheet / Modal Table of Contents
   6. Safe DOM-ID Smooth Scrolling (Unicode/Emoji/Digit resilient)
   ========================================================================== */

(function() {
  'use strict';

  // 1. Photo Slider Controller
  window.bpaSlide = function(btn, dir) {
    var media = btn.closest('.bpa-media');
    if (!media) return;
    var slider = media.querySelector('.bpa-slider');
    if (!slider) return;
    var w = slider.clientWidth;
    slider.scrollBy({ left: dir * w, behavior: 'smooth' });
  };

  window.bpaCount = function(slider) {
    var media = slider.closest('.bpa-media');
    if (!media) return;
    var pill = media.querySelector('.bpa-pill');
    if (!pill) return;
    var w = slider.clientWidth || 1;
    var idx = Math.min(Math.round(slider.scrollLeft / w) + 1, slider.children.length);
    pill.textContent = idx + ' / ' + slider.children.length;
  };

  // 2. Category Filter Tabs Controller
  window.lttFilterItems = function(cat, btn) {
    var buttons = document.querySelectorAll('.ltt-tab-btn');
    var activeCat = cat || 'all';

    // If currently active and clicked again (except 'all'), toggle back to 'all'
    if (btn && btn.classList.contains('active') && cat !== 'all') {
      activeCat = 'all';
    }

    buttons.forEach(function(b) {
      var bCat = b.getAttribute('data-cat') || 'all';
      if (bCat === activeCat) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });

    var cards = document.querySelectorAll('.ltt-deck-container .bpa-card, #ltt-cards-deck .bpa-card, .bpa-card');
    var detailsCards = document.querySelectorAll('details.bpa-details-card');

    cards.forEach(function(card, idx) {
      var cardCat = card.getAttribute('data-cat') || '';
      var show = (activeCat === 'all' || cardCat.indexOf(activeCat) !== -1);
      card.style.display = show ? '' : 'none';
      if (detailsCards[idx]) {
        detailsCards[idx].style.display = show ? '' : 'none';
      }
    });
  };

  // Aliases to guarantee 100% template compatibility
  window.lttFilterSafaris = window.lttFilterItems;
  window.lttFilterCruises = window.lttFilterItems;
  window.lttFilterCards = window.lttFilterItems;

  // 3. Navigation Header & Mobile Drawer
  function initNav() {
    var toggle = document.getElementById('lttNavToggle');
    var drawer = document.getElementById('lttMobileDrawer');
    var dropdown = document.getElementById('lttExploreDropdown');
    var dropBtn = dropdown ? dropdown.querySelector('.ltt-dropdown-btn') : null;

    if (toggle && drawer && !toggle._hasNavListener) {
      toggle._hasNavListener = true;
      toggle.addEventListener('click', function(e) {
        e.stopPropagation();
        var isOpen = drawer.classList.contains('is-open');
        if (isOpen) {
          drawer.classList.remove('is-open');
          toggle.classList.remove('is-active');
          toggle.setAttribute('aria-expanded', 'false');
          drawer.setAttribute('aria-hidden', 'true');
        } else {
          drawer.classList.add('is-open');
          toggle.classList.add('is-active');
          toggle.setAttribute('aria-expanded', 'true');
          drawer.setAttribute('aria-hidden', 'false');
        }
      });

      drawer.querySelectorAll('a').forEach(function(link) {
        link.addEventListener('click', function() {
          drawer.classList.remove('is-open');
          toggle.classList.remove('is-active');
          toggle.setAttribute('aria-expanded', 'false');
          drawer.setAttribute('aria-hidden', 'true');
        });
      });
    }

    if (dropBtn && dropdown) {
      dropBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        var open = dropdown.classList.toggle('is-open');
        dropBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }

    document.addEventListener('click', function(e) {
      if (drawer && drawer.classList.contains('is-open') && !drawer.contains(e.target) && (!toggle || !toggle.contains(e.target))) {
        drawer.classList.remove('is-open');
        if (toggle) {
          toggle.classList.remove('is-active');
          toggle.setAttribute('aria-expanded', 'false');
        }
        drawer.setAttribute('aria-hidden', 'true');
      }
      if (dropdown && dropdown.classList.contains('is-open') && !dropdown.contains(e.target)) {
        dropdown.classList.remove('is-open');
        if (dropBtn) dropBtn.setAttribute('aria-expanded', 'false');
      }
    });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        if (drawer && drawer.classList.contains('is-open')) {
          drawer.classList.remove('is-open');
          if (toggle) {
            toggle.classList.remove('is-active');
            toggle.setAttribute('aria-expanded', 'false');
          }
          drawer.setAttribute('aria-hidden', 'true');
        }
        if (dropdown && dropdown.classList.contains('is-open')) {
          dropdown.classList.remove('is-open');
          if (dropBtn) dropBtn.setAttribute('aria-expanded', 'false');
        }
        closeTocSheet();
      }
    });

    // Update active nav links based on current URL
    updateActiveNavLinks();
  }

  function updateActiveNavLinks() {
    try {
      if (typeof window === 'undefined' || !window.location) return;
      var rawPath = (window.location.pathname || '/').toLowerCase();
      var normPath = rawPath.replace(/\/index\.html$/, '').replace(/\/$/, '') || '/';

      var navLinks = document.querySelectorAll('.ltt-nav-link:not(.ltt-dropdown-btn), .ltt-mobile-link, .ltt-mega-item');
      var isDropdownChildActive = false;

      navLinks.forEach(function(el) {
        var rawHref = (el.getAttribute('href') || '').toLowerCase();
        if (!rawHref) return;
        var normHref = rawHref.split('?')[0].split('#')[0].replace(/\/index\.html$/, '').replace(/\/$/, '') || '/';

        var isMatch = false;
        if (normHref !== '/' && (normPath === normHref || normPath.indexOf(normHref + '/') === 0)) {
          isMatch = true;
        } else if (normHref === '/' && normPath === '/') {
          isMatch = true;
        }

        if (isMatch) {
          el.classList.add('active');
          el.setAttribute('aria-current', 'page');
          if (el.closest('.ltt-mega-menu')) {
            isDropdownChildActive = true;
          }
        } else {
          if (normHref !== '/') {
            el.classList.remove('active');
            el.removeAttribute('aria-current');
          }
        }
      });

      // Handle Destinations dropdown button (only active if child is active AND not already represented by a top-level link)
      var hasDirectTopLink = false;
      var topLinks = document.querySelectorAll('.ltt-nav-links > .ltt-nav-link:not(.ltt-dropdown-btn)');
      topLinks.forEach(function(tl) {
        if (tl.classList.contains('active')) {
          hasDirectTopLink = true;
        }
      });

      var dropBtn = document.querySelector('.ltt-dropdown-btn');
      if (dropBtn) {
        if (isDropdownChildActive && !hasDirectTopLink) {
          dropBtn.classList.add('active');
          dropBtn.setAttribute('aria-current', 'true');
        } else {
          dropBtn.classList.remove('active');
          dropBtn.removeAttribute('aria-current');
        }
      }
    } catch(e) {}
  }

  // 4. Hybrid Sticky Bar & Bottom Sheet TOC
  function initStickyBarAndToc() {
    var stickyBar = document.getElementById('sticky-bar') || document.querySelector('.hybrid-sticky-bar');
    var tocBtn = document.getElementById('hybridTocBtn');
    var backdrop = document.getElementById('hybridBackdrop');
    var closeBtn = document.getElementById('hybridCloseBtn');
    var tocList = document.getElementById('hybridSheetList');

    if (!stickyBar) return;

    // Populate Mobile Bottom Sheet TOC from Cards or Details
    if (tocList && tocList.children.length === 0) {
      var cards = document.querySelectorAll('.ltt-deck-container .bpa-card, #ltt-cards-deck .bpa-card, .bpa-card');
      cards.forEach(function(card) {
        var titleElem = card.querySelector('.bpa-title');
        var sublink = card.querySelector('.bpa-sublink');
        var priceElem = card.querySelector('.bpa-price');
        var targetId = sublink ? sublink.getAttribute('href') : '';
        if (titleElem && targetId) {
          var a = document.createElement('a');
          a.className = 'hybrid-toc-item';
          a.href = targetId;
          a.innerHTML = '<span>' + titleElem.textContent.trim() + '</span>' +
            (priceElem ? '<span class="hybrid-toc-price">' + priceElem.textContent.trim() + '</span>' : '');
          a.addEventListener('click', function() {
            closeTocSheet();
          });
          tocList.appendChild(a);
        }
      });
    }

    // Populate Desktop Sticky TOC (#toc)
    var desktopToc = document.getElementById('toc');
    if (desktopToc && desktopToc.children.length === 0) {
      var cfg = window.LTT_PAGE_CONFIG || {};
      var deckJumpText = cfg.tocDeckLabel || '⚡ Comparison Deck';
      var bdJumpText = cfg.tocBreakdownLabel || '📋 Detailed Breakdown';

      var deckElem = document.getElementById('ltt-cards-deck') || document.querySelector('.ltt-deck-container') || document.querySelector('.comparison-table');
      if (deckElem) {
        var deckJump = document.createElement('a');
        deckJump.className = 'tocitem';
        deckJump.href = '#' + (deckElem.id || 'ltt-cards-deck');
        deckJump.textContent = deckJumpText;
        desktopToc.appendChild(deckJump);
      }

      var detailsCards = document.querySelectorAll('details.bpa-details-card');
      if (detailsCards.length > 0) {
        var bdHeader = document.getElementById('breakdown-header');
        if (bdHeader) {
          var bdJump = document.createElement('a');
          bdJump.className = 'tocitem';
          bdJump.href = '#breakdown-header';
          bdJump.textContent = bdJumpText;
          desktopToc.appendChild(bdJump);
        }

        detailsCards.forEach(function(card) {
          var titleEl = card.querySelector('.bpa-details-title');
          var id = card.getAttribute('id');
          if (titleEl && id) {
            var item = document.createElement('a');
            item.className = 'tocitem';
            item.href = '#' + id;
            item.textContent = titleEl.textContent.trim();
            desktopToc.appendChild(item);
          }
        });
      }

      var buyingGuide = document.getElementById('buying-guide') || document.querySelector('.ltt-post-guide') || document.getElementById('faq-section');
      if (buyingGuide) {
        var bgJump = document.createElement('a');
        bgJump.className = 'tocitem';
        bgJump.href = '#' + (buyingGuide.id || 'buying-guide');
        bgJump.textContent = cfg.tocGuideLabel || '💡 Field Advice & FAQs';
        desktopToc.appendChild(bgJump);
      }
    }

    // Safe Scrollspy for Desktop TOC items (ID lookup without CSS selector crash)
    if (desktopToc) {
      var tocItems = desktopToc.querySelectorAll('.tocitem');
      window.addEventListener('scroll', function() {
        var fromTop = window.scrollY + 140;
        var cur = null;
        tocItems.forEach(function(item) {
          var hash = item.getAttribute('href');
          if (hash && hash.startsWith('#')) {
            var targetId = hash.slice(1);
            var target = document.getElementById(targetId);
            if (target && target.offsetTop <= fromTop) {
              cur = item;
            }
          }
        });
        tocItems.forEach(function(item) {
          if (item === cur) {
            item.classList.add('active');
          } else {
            item.classList.remove('active');
          }
        });
      }, { passive: true });
    }

    // Show/hide sticky bar based on scroll position
    var thresholdElem = document.getElementById('ltt-cards-deck') || 
                        document.querySelector('.ltt-deck-container') || 
                        document.querySelector('.ltt-duel-grid') || 
                        document.querySelector('.comparison-table') || 
                        document.querySelector('.ltt-hero-wrap');
    function onScroll() {
      var scrollY = window.pageYOffset || document.documentElement.scrollTop;
      var triggerPoint = thresholdElem ? Math.max(250, thresholdElem.offsetTop) : 350;
      if (scrollY > triggerPoint) {
        stickyBar.classList.add('is-visible');
      } else {
        stickyBar.classList.remove('is-visible');
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // Open TOC sheet
    if (tocBtn && backdrop) {
      tocBtn.addEventListener('click', function(e) {
        e.preventDefault();
        backdrop.classList.add('is-open');
        document.body.style.overflow = 'hidden';
      });
    }

    // Close TOC sheet
    function closeTocSheet() {
      if (backdrop) {
        backdrop.classList.remove('is-open');
        document.body.style.overflow = '';
      }
    }

    if (closeBtn) closeBtn.addEventListener('click', closeTocSheet);
    if (backdrop) {
      backdrop.addEventListener('click', function(e) {
        if (e.target === backdrop) closeTocSheet();
      });
    }
  }

  // Safe Smooth Scroll Handler for all in-page hash links
  document.addEventListener('click', function(e) {
    var anchor = e.target.closest('a[href^="#"]');
    if (!anchor) return;
    var href = anchor.getAttribute('href');
    if (href && href.length > 1) {
      var targetId = href.slice(1);
      var targetElem = document.getElementById(targetId);
      if (targetElem) {
        e.preventDefault();
        var topOffset = 80;
        var elemPos = targetElem.getBoundingClientRect().top + window.pageYOffset - topOffset;
        window.scrollTo({ top: elemPos, behavior: 'smooth' });
        if (history.pushState) {
          history.pushState(null, '', href);
        }
      }
    }
  });

  // Global Expand / Collapse All Detailed Reviews controller
  window.toggleAllDetails = function(open) {
    var cards = document.querySelectorAll('details.bpa-details-card');
    cards.forEach(function(c) {
      if (open) {
        c.setAttribute('open', '');
      } else {
        c.removeAttribute('open');
      }
    });
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initNav();
      initStickyBarAndToc();
    });
  } else {
    initNav();
    initStickyBarAndToc();
  }
})();
