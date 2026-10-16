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
        // Hierarchy 1: URL parameter
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
            const existingCampaign = url.searchParams.get('tq_campaign') || 'romantic-quiz-bm';
            
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

    function decorateAllLinks() {
        const activeClickId = getClickId();
        if (!activeClickId) return;

        const links = document.querySelectorAll('a[href*="tiqets.com"]');
        links.forEach(link => decorateLink(link, activeClickId));
    }

    // Attach Meta Pixel InitiateCheckout event to Tiqets CTA buttons
    function attachTrackingToButtons() {
        const ctaButtons = document.querySelectorAll('a[href*="tiqets.com"], .cta-button, .btn-secondary');
        ctaButtons.forEach(button => {
            button.addEventListener('click', () => {
                const activeClickId = getClickId();
                if (activeClickId) {
                    decorateLink(button, activeClickId);
                }

                if (typeof window.fbq === 'function') {
                    window.fbq('track', 'InitiateCheckout', {
                        content_name: 'Paris Romantic Dinner Cruise',
                        content_category: 'Dinner Cruise',
                        currency: 'EUR',
                        value: 230.00
                    });
                }
            });
        });
    }

    // Initial link decoration
    decorateAllLinks();
    attachTrackingToButtons();

    // Set Copyright Year
    const yearEl = document.getElementById('current-year');
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }

    // -------------------------------------------------------------
    // 2. Interactive Quiz State Machine
    // -------------------------------------------------------------
    const stepIntro = document.getElementById('step-intro');
    const stepQ1 = document.getElementById('step-q1');
    const stepQ2 = document.getElementById('step-q2');
    const stepQ3 = document.getElementById('step-q3');
    const stepQ4 = document.getElementById('step-q4');
    const stepLoading = document.getElementById('step-loading');
    const stepResults = document.getElementById('step-results');
    
    const progressContainer = document.getElementById('progress-container');
    const questionStepLabel = document.getElementById('question-step-label');
    const progressPercent = document.getElementById('progress-percent');
    const progressFill = document.getElementById('progress-fill');

    const btnStart = document.getElementById('btn-start-quiz');
    const btnRestart = document.getElementById('btn-restart-quiz');

    const quizAnswers = {
        occasion: null,
        vibe: null,
        priority: null,
        budget: null
    };

    function showStep(stepElement) {
        [stepIntro, stepQ1, stepQ2, stepQ3, stepQ4, stepLoading, stepResults].forEach(el => {
            if (el) {
                el.style.display = 'none';
                el.classList.remove('active');
            }
        });

        if (stepElement) {
            stepElement.style.display = 'block';
            stepElement.classList.add('active');
            window.scrollTo({ top: 100, behavior: 'smooth' });
        }
    }

    function updateProgress(stepIndex, totalSteps) {
        const percent = Math.round((stepIndex / totalSteps) * 100);
        if (questionStepLabel) questionStepLabel.textContent = `Question ${stepIndex} of ${totalSteps}`;
        if (progressPercent) progressPercent.textContent = `${percent}% Complete`;
        if (progressFill) progressFill.style.width = `${percent}%`;
    }

    // Start Quiz
    if (btnStart) {
        btnStart.addEventListener('click', () => {
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStart');
            }
            if (progressContainer) progressContainer.style.display = 'block';
            updateProgress(1, 4);
            showStep(stepQ1);
        });
    }

    // Handle Question 1 Selection
    stepQ1.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.occasion = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 1, answer: quizAnswers.occasion });
            }
            updateProgress(2, 4);
            showStep(stepQ2);
        });
    });

    // Handle Question 2 Selection
    stepQ2.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.vibe = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 2, answer: quizAnswers.vibe });
            }
            updateProgress(3, 4);
            showStep(stepQ3);
        });
    });

    // Handle Question 3 Selection
    stepQ3.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.priority = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 3, answer: quizAnswers.priority });
            }
            updateProgress(4, 4);
            showStep(stepQ4);
        });
    });

    // Handle Question 4 Selection -> Trigger Loading & Results
    stepQ4.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.budget = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 4, answer: quizAnswers.budget });
            }
            
            if (progressContainer) progressContainer.style.display = 'none';
            showStep(stepLoading);

            // Animate calculation checklist
            const step1 = document.getElementById('calc-step-1');
            const step2 = document.getElementById('calc-step-2');
            const step3 = document.getElementById('calc-step-3');

            setTimeout(() => {
                if (step1) {
                    step1.className = 'check-item done';
                    step1.querySelector('.check-icon').textContent = '✓';
                }
                if (step2) {
                    step2.className = 'check-item active';
                    step2.querySelector('.check-icon').textContent = '⏳';
                }
            }, 800);

            setTimeout(() => {
                if (step2) {
                    step2.className = 'check-item done';
                    step2.querySelector('.check-icon').textContent = '✓';
                }
                if (step3) {
                    step3.className = 'check-item active';
                    step3.querySelector('.check-icon').textContent = '⏳';
                }
            }, 1600);

            setTimeout(() => {
                if (step3) {
                    step3.className = 'check-item done';
                    step3.querySelector('.check-icon').textContent = '✓';
                }
            }, 2400);

            // Reveal Results
            setTimeout(() => {
                showStep(stepResults);
                decorateAllLinks();
                attachTrackingToButtons();

                if (typeof window.fbq === 'function') {
                    window.fbq('trackCustom', 'QuizCompleted', {
                        match: 'Bateaux-Mouches',
                        occasion: quizAnswers.occasion,
                        vibe: quizAnswers.vibe,
                        budget: quizAnswers.budget
                    });
                }
            }, 2800);
        });
    });

    // Restart Quiz
    if (btnRestart) {
        btnRestart.addEventListener('click', () => {
            quizAnswers.occasion = null;
            quizAnswers.vibe = null;
            quizAnswers.priority = null;
            quizAnswers.budget = null;

            if (progressContainer) progressContainer.style.display = 'none';
            showStep(stepIntro);
        });
    }
});
