document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // 1. Click ID Persistence & Tiqets Link Decoration Engine (CAPI)
    // -------------------------------------------------------------
    const STORAGE_KEY = 'cd_gclid';
    const EXPIRATION_KEY = 'cd_gclid_exp';
    const EXPIRATION_MS = 90 * 24 * 60 * 60 * 1000; // 90 days in ms
    const COOKIE_MAX_AGE = 90 * 24 * 60 * 60; // 90 days in seconds

    function saveClickId(type, value) {
        if (!value || typeof value !== 'string') return;
        const cleanValue = value.trim();
        if (!cleanValue) return;

        const payload = `${type}:${cleanValue}`;
        const expTime = Date.now() + EXPIRATION_MS;

        try {
            if (typeof localStorage !== 'undefined') {
                localStorage.setItem(STORAGE_KEY, payload);
                localStorage.setItem(EXPIRATION_KEY, expTime.toString());
            }
        } catch (e) {}

        try {
            if (typeof document !== 'undefined') {
                document.cookie = `${STORAGE_KEY}=${encodeURIComponent(payload)}; max-age=${COOKIE_MAX_AGE}; path=/; SameSite=Lax`;
            }
        } catch (e) {}
    }

    function parseStoredId(storedVal) {
        if (!storedVal) return null;
        if (storedVal.startsWith('fbclid:')) return { type: 'fbclid', value: storedVal.substring(7) };
        if (storedVal.startsWith('gclid:')) return { type: 'gclid', value: storedVal.substring(6) };
        if (storedVal.startsWith('wbraid:')) return { type: 'wbraid', value: storedVal.substring(7) };
        if (storedVal.startsWith('gbraid:')) return { type: 'gbraid', value: storedVal.substring(7) };
        return { type: 'fbclid', value: storedVal };
    }

    function getClickId() {
        // Hierarchy 1: URL query parameter
        try {
            if (typeof window !== 'undefined' && window.location && window.location.search) {
                const urlParams = new URLSearchParams(window.location.search);
                for (const type of ['fbclid', 'gclid', 'wbraid', 'gbraid']) {
                    const val = urlParams.get(type);
                    if (val && val.trim()) {
                        const cleanVal = val.trim();
                        saveClickId(type, cleanVal);
                        return { type, value: cleanVal };
                    }
                }
            }
        } catch (e) {}

        // Hierarchy 2: localStorage
        try {
            if (typeof localStorage !== 'undefined') {
                const localVal = localStorage.getItem(STORAGE_KEY);
                const exp = localStorage.getItem(EXPIRATION_KEY);
                if (localVal) {
                    if (exp) {
                        const expTime = parseInt(exp, 10);
                        if (!isNaN(expTime) && Date.now() < expTime) {
                            return parseStoredId(localVal);
                        }
                    } else {
                        return parseStoredId(localVal);
                    }
                }
            }
        } catch (e) {}

        // Hierarchy 3: Cookie
        try {
            if (typeof document !== 'undefined' && document.cookie) {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.startsWith(`${STORAGE_KEY}=`)) {
                        const cookieVal = decodeURIComponent(cookie.substring(STORAGE_KEY.length + 1));
                        if (cookieVal) {
                            const parsed = parseStoredId(cookieVal);
                            saveClickId(parsed.type, parsed.value);
                            return parsed;
                        }
                    }
                }
            }
        } catch (e) {}

        return null;
    }

    function decorateLink(link, clickIdObj) {
        if (!link || !clickIdObj || !clickIdObj.value) return;
        const { type, value } = clickIdObj;
        try {
            const rawHref = link.getAttribute('href');
            if (!rawHref || !rawHref.includes('tiqets.com')) return;

            const url = new URL(rawHref, window.location.href);
            const existingCampaign = url.searchParams.get('tq_campaign') || 'dinner-paris-advertorial-bm';
            
            // Format composite campaign tag
            let newCampaign = existingCampaign;
            const match = existingCampaign.match(/--(fbclid|gclid|wbraid|gbraid)-/);
            if (match) {
                const baseTag = existingCampaign.substring(0, match.index);
                newCampaign = baseTag ? `${baseTag}--${type}-${value}` : `${type}-${value}`;
            } else {
                newCampaign = `${existingCampaign}--${type}-${value}`;
            }

            url.searchParams.set('tq_campaign', newCampaign);
            url.searchParams.set(type, value);
            url.searchParams.set('click_id', value);
            url.searchParams.set('subid', `${type}:${value}`);

            link.href = url.toString();
        } catch (e) {
            console.warn('Failed to decorate Tiqets link:', e);
        }
    }

    function scanAndDecorateLinks() {
        const activeClickId = getClickId();
        if (!activeClickId) return;

        const links = document.querySelectorAll('a[href*="tiqets.com"]');
        links.forEach(link => decorateLink(link, activeClickId));
    }

    function attachTrackingToButtons() {
        const ctaButtons = document.querySelectorAll('a[href*="tiqets.com"], .cta-button');
        ctaButtons.forEach(button => {
            button.addEventListener('click', () => {
                const activeClickId = getClickId();
                if (activeClickId) {
                    decorateLink(button, activeClickId);
                }

                if (typeof window.fbq === 'function') {
                    window.fbq('track', 'InitiateCheckout', {
                        content_name: 'Bateaux-Mouches Romantic Dinner Cruise (Advertorial)',
                        content_category: 'Paris Dinner Cruise',
                        currency: 'EUR',
                        value: 230.00
                    });
                }
            });
        });
    }

    // Run link decoration & event tracking
    scanAndDecorateLinks();
    attachTrackingToButtons();

    // -------------------------------------------------------------
    // 2. Set dynamic dates
    // -------------------------------------------------------------
    const dateElement = document.getElementById('dynamic-date');
    const yearElement = document.getElementById('current-year');
    const today = new Date();
    
    // Set current year for copyright
    if (yearElement) {
        yearElement.textContent = today.getFullYear();
    }
    
    // Set publish date
    if (dateElement) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = today.toLocaleDateString('en-US', options);
    }

    // -------------------------------------------------------------
    // 3. Sticky CTA Logic
    // -------------------------------------------------------------
    const stickyCta = document.getElementById('sticky-cta');
    const mainHeader = document.querySelector('.main-header');
    
    window.addEventListener('scroll', () => {
        if (!stickyCta || !mainHeader) return;
        
        const scrollPosition = window.scrollY;
        // Show sticky CTA after scrolling 500px down
        if (scrollPosition > 500) {
            stickyCta.style.display = 'block';
        } else {
            stickyCta.style.display = 'none';
        }
    });
});
