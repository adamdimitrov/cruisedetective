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

        return null;
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
                
                // If we captured an active click ID, forward it into subid / tq_campaign
                if (clickId) {
                    url.searchParams.set('subid', clickId);
                    if (!url.searchParams.has('tq_campaign')) {
                        url.searchParams.set('tq_campaign', 'gads_' + clickId);
                    }
                }
                a.href = url.toString();
            } catch(e) {}
        });
    }

    // Run synchronization on DOMContentLoaded and on window load
    function init() {
        const clickId = getOrSetClickId();
        decorateTiqetsLinks(clickId);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    window.addEventListener('load', init);
})();
