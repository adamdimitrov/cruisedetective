(function() {
    // Immediately hide and remove legacy Webflow comparison table embeds (.tcd-seo-table-container) across all Webflow articles
    function removeWebflowComparisonTables() {
        try {
            if (typeof document === "undefined") return;
            if (!document.getElementById("tcd-remove-comparison-table-style")) {
                const style = document.createElement("style");
                style.id = "tcd-remove-comparison-table-style";
                style.textContent = ".tcd-seo-table-container, .w-embed:has(.tcd-seo-table-container) { display: none !important; margin: 0 !important; padding: 0 !important; height: 0 !important; overflow: hidden !important; border: none !important; }";
                (document.head || document.documentElement).appendChild(style);
            }
            const tables = document.querySelectorAll(".tcd-seo-table-container");
            tables.forEach((table) => {
                const embedWrapper = table.closest(".w-embed");
                if (embedWrapper) {
                    embedWrapper.remove();
                } else {
                    table.remove();
                }
            });
        } catch (e) {}
    }

    removeWebflowComparisonTables();

    // ==========================================
    // Webflow Branding Badge Suppression ("Made in Webflow")
    // ==========================================
    function eliminateWebflowBadge() {
        if (typeof document === 'undefined') return;
        var badges = document.querySelectorAll('.w-webflow-badge, a.w-webflow-badge, [class*="w-webflow-badge"], a[href*="utm_campaign=brandjs"]');
        for (var i = 0; i < badges.length; i++) {
            var b = badges[i];
            if (b) {
                b.style.setProperty('display', 'none', 'important');
                b.style.setProperty('visibility', 'hidden', 'important');
                b.style.setProperty('opacity', '0', 'important');
                b.style.setProperty('pointer-events', 'none', 'important');
                try {
                    b.remove();
                } catch(e) {
                    if (b.parentNode) b.parentNode.removeChild(b);
                }
            }
        }
    }

    try {
        if (typeof document !== 'undefined') {
            var badgeStyle = document.createElement('style');
            badgeStyle.id = 'cd-suppress-webflow-badge';
            badgeStyle.textContent = '.w-webflow-badge, a.w-webflow-badge, [class*="w-webflow-badge"], a[href*="utm_campaign=brandjs"] { display: none !important; opacity: 0 !important; visibility: hidden !important; pointer-events: none !important; position: absolute !important; top: -99999px !important; left: -99999px !important; width: 0 !important; height: 0 !important; z-index: -99999 !important; }';
            if (document.head) {
                document.head.appendChild(badgeStyle);
            } else if (document.documentElement) {
                document.documentElement.appendChild(badgeStyle);
            }
        }
    } catch(e) {}

    eliminateWebflowBadge();

    if (typeof MutationObserver !== 'undefined' && typeof document !== 'undefined') {
        try {
            var badgeObs = new MutationObserver(function() {
                eliminateWebflowBadge();
            });
            var targetNode = document.documentElement || document.body;
            if (targetNode) {
                badgeObs.observe(targetNode, { childList: true, subtree: true });
            }
        } catch(e) {}
    }

    // Hosted ratings.json path:
    const RATINGS_JSON_URL = "https://raw.githubusercontent.com/adamdimitrov/cruisedetective/refs/heads/main/ratings.json";

    // ----------------------------------------------------
    // 1. Session Storage & Click ID Capture (1st Party)
    // ----------------------------------------------------
    function getQueryParam(param) {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(param);
        } catch(e) {
            return null;
        }
    }

    function setCookie(name, value, days) {
        try {
            let expires = "";
            if (days) {
                const date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                expires = "; expires=" + date.toUTCString();
            }
            document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Lax";
        } catch(e) {}
    }

    function getCookie(name) {
        try {
            const nameEQ = name + "=";
            const ca = document.cookie.split(';');
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        } catch(e) {
            return null;
        }
    }

    // Google's own conversion linker cookie: "GCL.<timestamp>.<gclid>" (90 days).
    function getGoogleLinkerGclid() {
        const raw = getCookie('_gcl_aw');
        if (!raw) return null;
        const parts = decodeURIComponent(raw).split('.');
        return parts.length >= 3 ? parts.slice(2).join('.') : null;
    }

    // Returns the ad click ID that should travel to Tiqets, persisted for 90 days so
    // a visitor who clicks an ad, leaves, and comes back later in a new tab is still
    // attributed. Lookup order: URL > our cookie > localStorage > Google's _gcl_aw.
    function getOrSetClickId() {
        let clickId = getQueryParam('gclid');
        if (clickId) {
            setCookie('_cd_gclid', clickId, 90);
            try { localStorage.setItem('_cd_gclid', clickId); } catch(e) {}
            return clickId;
        }

        let cookieGclid = getCookie('_cd_gclid');
        if (cookieGclid) return cookieGclid;

        try {
            let localGclid = localStorage.getItem('_cd_gclid');
            if (localGclid) return localGclid;
        } catch(e) {}

        return getGoogleLinkerGclid();
    }

    // ----------------------------------------------------
    // 2. Affiliate Outbound Link Decoration
    // ----------------------------------------------------
    function decorateTiqetsLinks(clickId) {
        const anchors = document.querySelectorAll('a[href*="tiqets.com"]');
        anchors.forEach(a => {
            try {
                const url = new URL(a.href);
                // Enforce verified partner ID
                url.searchParams.set('partner', 'thecruisedetective.com-176436');
                
                // Forward the click ID into tq_campaign as "<campaign>--gclid-<id>".
                // tq_campaign is the only field Tiqets returns per order, and
                // sync_tiqets_conversions.py parses the gclid out of it for Google Ads.
                if (clickId) {
                    url.searchParams.set('subid', clickId);
                    const campaign = url.searchParams.get('tq_campaign') || '';
                    if (campaign.indexOf('gclid-') === -1) {
                        url.searchParams.set('tq_campaign', (campaign || 'gads') + '--gclid-' + clickId);
                    }
                }
                a.href = url.toString();
            } catch(e) {}
        });
    }

    // ----------------------------------------------------
    // 3. Dynamic Active Navigation Link Controller
    // ----------------------------------------------------
    function ensureActiveNavStyles() {
        try {
            if (typeof document === 'undefined') return;
            if (!document.getElementById('ltt-active-nav-styles')) {
                var style = document.createElement('style');
                style.id = 'ltt-active-nav-styles';
                style.textContent = '' +
                    '.ltt-nav-link.active, .ltt-nav-link[aria-current="page"], .ltt-dropdown-btn.active {' +
                    '  color: #0f172a !important;' +
                    '  background: #f1f5f9 !important;' +
                    '  font-weight: 700 !important;' +
                    '  box-shadow: inset 0 -2px 0 #0f172a !important;' +
                    '}' +
                    '.ltt-mega-item.active, .ltt-mega-item[aria-current="page"] {' +
                    '  background: #f1f5f9 !important;' +
                    '  border-left: 3px solid #0f172a !important;' +
                    '}' +
                    '.ltt-mobile-link.active, .ltt-mobile-link[aria-current="page"] {' +
                    '  background: #0f172a !important;' +
                    '  color: #ffffff !important;' +
                    '  border-color: #0f172a !important;' +
                    '  font-weight: 700 !important;' +
                    '}' +
                    '.ltt-mobile-link.active span, .ltt-mobile-link[aria-current="page"] span {' +
                    '  color: #ffffff !important;' +
                    '}';
                (document.head || document.documentElement).appendChild(style);
            }
        } catch(e) {}
    }

    function updateActiveNavLinks() {
        try {
            if (typeof window === 'undefined' || !window.location) return;
            ensureActiveNavStyles();

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

    // Run synchronization on DOMContentLoaded and on window load
    function init() {
        const clickId = getOrSetClickId();
        decorateTiqetsLinks(clickId);
        updateActiveNavLinks();
    }

    // Immediate attempt if DOM is already present
    ensureActiveNavStyles();
    updateActiveNavLinks();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    window.addEventListener('load', init);
})();
