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
            const existingCampaign = url.searchParams.get('tq_campaign') || 'paris-cruise-quiz';
            
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

    function attachTrackingToButtons() {
        const ctaButtons = document.querySelectorAll('a[href*="tiqets.com"], .cta-button, .btn-secondary');
        ctaButtons.forEach(button => {
            const newBtn = button.cloneNode(true);
            button.parentNode.replaceChild(newBtn, button);

            newBtn.addEventListener('click', () => {
                const activeClickId = getClickId();
                if (activeClickId) {
                    decorateLink(newBtn, activeClickId);
                }

                if (typeof window.fbq === 'function') {
                    const priceVal = parseFloat(newBtn.dataset.checkoutValue) || 54.00;
                    const cruiseName = newBtn.dataset.cruiseName || 'Paris Seine River Cruise';
                    window.fbq('track', 'InitiateCheckout', {
                        content_name: cruiseName,
                        content_category: 'Paris River Cruises',
                        currency: 'EUR',
                        value: priceVal
                    });
                }
            });
        });
    }

    decorateAllLinks();
    attachTrackingToButtons();

    const yearEl = document.getElementById('current-year');
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }

    // -------------------------------------------------------------
    // 2. Comprehensive 9-Cruise Knowledge Base (Core + Differentiated Niches)
    // -------------------------------------------------------------
    const CRUISE_DATABASE = {
        // #1 Best Seller Sightseeing (Eiffel Tower Pier 3)
        bp_sightseeing: {
            id: '973977',
            key: 'bp_sightseeing',
            name: 'Bateaux Parisiens Sightseeing Cruise',
            badge: '🏆 #1 BEST OVERALL SIGHTSEEING CRUISE',
            matchBanner: '99% MATCH FOR YOUR PARIS SIGHTSEEING',
            matchRank: 'Official Highest-Rated Sightseeing Cruise in Paris',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/653a40c21889f4f91e8b7f7f_1-bateaux-parisiens-sighteeing-cruise%20(10)-p-800.webp',
            rating: '4.7 / 5.0',
            reviewCount: '(Over 28,400+ Verified Traveler Reviews)',
            adultPrice: 18.00,
            childPrice: 9.00,
            hasChildPrice: true,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Bateaux Parisiens Sightseeing</strong> is the undisputed #1 match. Departing directly from Pier 3 at the foot of the Eiffel Tower, its modern trimarans feature an open-air top deck, crystal clear individual multilingual audio handsets, and flexible walk-up departures all day.',
            reasons: [
                {
                    icon: '🗼',
                    title: 'Pier 3 at the Foot of the Eiffel Tower',
                    desc: 'Zero walking hassle. Step directly from the Eiffel Tower onto the boat at Port de la Bourdonnais.'
                },
                {
                    icon: '🎧',
                    title: 'Individual Handsets in 14 Languages',
                    desc: 'Listen via personal audio handset or smartphone app without crackly loudspeakers or language confusion.'
                },
                {
                    icon: '🌤️',
                    title: '360° Open-Air Rooftop Terrace',
                    desc: 'Unobstructed panoramic photo deck above, plus heated glass-enclosed salon below for cold or rainy weather.'
                },
                {
                    icon: '⚡',
                    title: 'Flexible Open Ticket (Valid All Day)',
                    desc: 'Departures every 30–45 minutes from 10:00 to 22:30. Board whenever you are ready today.'
                }
            ],
            priceAmount: '€18',
            priceSub: 'Adult €18.00 • Kids (4–11) €9.00 • Under 4 FREE',
            urgencyTitle: 'Instant Smartphone Boarding:',
            urgencyText: 'Flexible open ticket — scan directly from your phone at Pier 3 turnstiles. Free 24h cancellation.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-sightseeing-cruise-on-the-seine-p973977/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bp-sightseeing',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE →',
            ctaSubline: 'Official Tiqets Partner • Instant QR Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not Bateaux Mouches?</strong> Located 1.8km east at Pont de l\'Alma — requires an extra 25-minute metro or taxi ride if you are already visiting the Eiffel Tower. <strong>Why not Batobus?</strong> Batobus is a slow transit shuttle with flat enclosed windows and zero audio commentary.',
            compTable: [
                { feature: 'Departure Pier', winner: 'Port de la Bourdonnais (Eiffel Tower Pier 3)', other: 'Pont de l\'Alma (8th Arrondissement)' },
                { feature: 'Audio Commentary', winner: '14-Language Individual Handsets', other: 'Dual French/English Loudspeaker' },
                { feature: 'Daily Departures', winner: 'Every 30–45 Minutes', other: 'Every 45–60 Minutes' },
                { feature: 'Ticket Pricing', winner: '€18 Adult • €9 Kids (4-11)', other: '€17 Adult • €8 Kids (4-12)' }
            ],
            runnerUp: {
                title: 'Bateaux-Mouches Sightseeing Cruise',
                badge: 'RUNNER-UP SIGHTSEEING',
                desc: 'Historic operator departing from Pont de l\'Alma. Massive 360° open upper deck with classic French live commentary.',
                price: 'From €17/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-seine-cruise-by-bateaux-mouches-p982823/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bm-sightseeing',
                btnText: 'View Bateaux Mouches Sightseeing →'
            },
            testimonial: {
                quote: 'We walked straight down from the Eiffel Tower to Pier 3 and boarded within 10 minutes. The audio guide was crystal clear and the open top deck gave us the most incredible photos of Notre-Dame and the bridges. Hands down the best €18 we spent in Paris!',
                author: '— David & Emma, New York (Traveled September 2025)'
            }
        },

        // #2 Best Seller Sightseeing (360° Open Deck, Pont de l'Alma)
        bm_sightseeing: {
            id: '982823',
            key: 'bm_sightseeing',
            name: 'Bateaux-Mouches Classic Sightseeing Cruise',
            badge: '🏆 BEST 360° OPEN-AIR OBSERVATION DECK',
            matchBanner: '98% MATCH FOR OPEN-AIR ROOFTOP PHOTOS',
            matchRank: '#1 Historic Right Bank Sightseeing Operator',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/6533a18d17ca225f10bc4ca8_bateaux-mouches.webp',
            rating: '4.6 / 5.0',
            reviewCount: '(Over 18,200+ Verified Traveler Reviews)',
            adultPrice: 17.00,
            childPrice: 8.00,
            hasChildPrice: true,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Bateaux Mouches Classic Sightseeing</strong> is your ideal match. Departing from Pont de l\'Alma on the Right Bank, this iconic institution features the widest, highest 360° open-air upper observation deck on the Seine, giving photographers unobstructed angles of lit-up monuments.',
            reasons: [
                {
                    icon: '🌤️',
                    title: 'Massive 360° Open Upper Deck',
                    desc: 'The largest outdoor observation deck on the river, perfect for wide-angle photography without window reflections.'
                },
                {
                    icon: '📍',
                    title: 'Pont de l\'Alma Pier (Right Bank)',
                    desc: 'Convenient access near Champs-Élysées, Avenue Montaigne, and the 8th Arrondissement.'
                },
                {
                    icon: '🎙️',
                    title: 'Classic French Live Loudspeaker Commentary',
                    desc: 'Engaging, old-school Parisian charm broadcast over speakers as monuments pass.'
                },
                {
                    icon: '💶',
                    title: 'Slightly Lower Ticket Rate',
                    desc: 'At €17 for adults and €8 for kids, it is €1 cheaper per ticket than Bateaux Parisiens.'
                }
            ],
            priceAmount: '€17',
            priceSub: 'Adult €17.00 • Kids (4–12) €8.00 • Under 4 FREE',
            urgencyTitle: 'Immediate Boarding Availability:',
            urgencyText: 'Continuous departures every 45 minutes from Pont de l\'Alma. Instant smartphone QR ticket.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-seine-cruise-by-bateaux-mouches-p982823/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bm-sightseeing',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE (€17) →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not Bateaux Parisiens?</strong> If you want individual language headphones or are already standing at the Eiffel Tower, Bateaux Parisiens is closer. But if you want the absolute largest open-air roof deck for photos, Bateaux Mouches wins.',
            compTable: [
                { feature: 'Observation Deck', winner: 'Largest 360° Open Rooftop on the River', other: 'Standard Top Deck' },
                { feature: 'Departure Pier', winner: 'Pont de l\'Alma (Right Bank / Champs-Élysées)', other: 'Port de la Bourdonnais (Eiffel)' },
                { feature: 'Audio Style', winner: 'Loudspeaker Broadcast in EN/FR', other: 'Individual Headsets in 14 Languages' },
                { feature: 'Adult Fare', winner: '€17.00', other: '€18.00' }
            ],
            runnerUp: {
                title: 'Bateaux Parisiens Sightseeing Cruise',
                badge: 'RUNNER-UP SIGHTSEEING',
                desc: 'Leaves right from Pier 3 at the Eiffel Tower foot with individual 14-language audio handsets.',
                price: 'From €18/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-sightseeing-cruise-on-the-seine-p973977/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bp-sightseeing',
                btnText: 'View Bateaux Parisiens Sightseeing →'
            },
            testimonial: {
                quote: 'The upper deck on Bateaux Mouches is enormous! We stood right at the front as we sailed past Notre-Dame and the Louvre. The cool river breeze and evening light made it unforgettable.',
                author: '— Thomas & Sarah, Bristol (Traveled August 2025)'
            }
        },

        // #3 Romantic Flagship Dinner (Live Violin & Piano)
        bm_dinner: {
            id: '982924',
            key: 'bm_dinner',
            name: 'Bateaux-Mouches Romantic Dinner Cruise',
            badge: '🏆 #1 RATED ROMANTIC DINNER CRUISE',
            matchBanner: '99% MATCH FOR CANDLELIGHT ROMANCE',
            matchRank: '#1 Highest-Rated Dinner Cruise for Couples in Paris',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/6557d4b0f32b0baf412f95f5_Bateaux-mouches-dinner-cruise%20(7)-p-500.webp',
            rating: '4.8 / 5.0',
            reviewCount: '(Over 9,900+ Verified Couple Reviews)',
            adultPrice: 115.00,
            childPrice: 45.00,
            hasChildPrice: false,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Bateaux Mouches Dinner Cruise</strong> is your exact match. Unlike crowded sightseeing boats with microwave catering, Bateaux Mouches delivers an authentic candlelit French culinary feast prepared onboard, accompanied by an acoustic live violin and piano duo.',
            reasons: [
                {
                    icon: '🎻',
                    title: 'Live Acoustic Violin & Piano Duo',
                    desc: 'Timeless romantic French ballads played live by musicians throughout your 2-hour 15-minute dinner.'
                },
                {
                    icon: '🍷',
                    title: 'Full 4-Course French Meal + Drinks Included',
                    desc: 'Generous beverage package: 1 full bottle of wine per couple + champagne aperitif + mineral water & coffee.'
                },
                {
                    icon: '🗼',
                    title: 'Massive 360° Open-Air Rooftop Deck',
                    desc: 'Step upstairs anytime to hold hands by the rail and kiss under the sparkling Eiffel Tower at 22:00.'
                },
                {
                    icon: '✨',
                    title: 'White Tablecloths & Generous Spacing',
                    desc: 'Intimate couple tables with attentive white-glove service and candlelit elegance.'
                }
            ],
            priceAmount: '€115',
            priceSub: 'All-inclusive: 4-course dinner + wine & champagne',
            urgencyTitle: 'High Demand Date Notice:',
            urgencyText: 'Couples tables book 4 to 7 days in advance for 20:30 Prestige dinner. Free cancellation up to 24h before.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bm-dinner',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not Paris en Scène?</strong> Paris en Scène uses club armchairs facing sideways without live violin, piano, or white-tablecloth table service. <strong>Why not early 18:00 dinner cruises?</strong> They depart before dark, meaning you completely miss the Eiffel Tower\'s diamond sparkle show.',
            compTable: [
                { feature: 'Live Music', winner: 'Live Violin & Piano Duo', other: 'Live Vocalist & Lounge Band' },
                { feature: 'Drink Package', winner: 'Full Bottle of Wine + Champagne Included', other: 'Drinks depend on menu tier' },
                { feature: 'Viewing Deck', winner: 'Giant 360° Open-Air Walkout Roof Deck', other: 'Enclosed Glass Trimaran' },
                { feature: 'Romance Atmosphere', winner: 'Classic Candlelit White Tablecloths', other: 'Contemporary Architectural Chic' }
            ],
            runnerUp: {
                title: 'Bateaux Parisiens Dinner Cruise',
                badge: 'RUNNER-UP LUXURY DINNER',
                desc: 'Contemporary all-glass architectural boat departing right under the Eiffel Tower. Features live lounge singer and panoramic views.',
                price: 'From €115/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-bateaux-parisiens-dinner-cruise-p974358/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bp-dinner',
                btnText: 'View Bateaux Parisiens Dinner Option →'
            },
            testimonial: {
                quote: 'My fiancé and I celebrated our engagement here. The boat slowed right in front of the glittering Eiffel Tower while the violinist played \'La Vie en Rose\'. Pure magic. The wine kept flowing and the duck confit was superb!',
                author: '— Sarah & Marc, London (Traveled June 2025)'
            }
        },

        // #4 Modern Glass Panoramic Luxury Dinner (Eiffel Tower Pier 5)
        bp_dinner: {
            id: '974358',
            key: 'bp_dinner',
            name: 'Bateaux Parisiens Luxury Dinner Cruise',
            badge: '🏆 BEST MODERN ALL-GLASS LUXURY DINNER',
            matchBanner: '98% MATCH FOR MODERN ARCHITECTURAL LUXURY',
            matchRank: 'Top Luxury Dinner Cruise at the Eiffel Tower',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/653e675abdd0b1ea6c8c9f69_bateaux-parisiens-dinner-cruise%20(32).webp',
            rating: '4.7 / 5.0',
            reviewCount: '(Over 11,500+ Verified Reviews)',
            adultPrice: 115.00,
            childPrice: 45.00,
            hasChildPrice: false,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Bateaux Parisiens Dinner Cruise</strong> is your premier match. Boarding directly at the base of the Eiffel Tower, this 100% glass-canopied trimaran offers uninterrupted panoramic vistas from every seat, accompanied by a live singer and refined French gastronomy.',
            reasons: [
                {
                    icon: '🪟',
                    title: '100% Curved Glass Canopy Architecture',
                    desc: 'Unobstructed upward vistas of floodlit bridges and illuminated Parisian facades from every seat.'
                },
                {
                    icon: '🎤',
                    title: 'Live Vocalist & Musical Performance',
                    desc: 'Sophisticated contemporary live musical accompaniment throughout the evening.'
                },
                {
                    icon: '🗼',
                    title: 'Pier at the Foot of the Eiffel Tower',
                    desc: 'Departs from Pier 5 at Port de la Bourdonnais — unbeatable convenience after touring the tower.'
                },
                {
                    icon: '👑',
                    title: 'Service Premier VIP Privilege Option',
                    desc: 'Front bow seating with vintage champagne, fine wine pairings, and prime unobstructed angles.'
                }
            ],
            priceAmount: '€115',
            priceSub: 'Dinner packages from €115 to €215 (Service Premier)',
            urgencyTitle: 'Prime Pier Notice:',
            urgencyText: 'Eiffel Tower departures sell out fastest on weekends. Free cancellation up to 24h before.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-bateaux-parisiens-dinner-cruise-p974358/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bp-dinner',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not Bateaux Mouches?</strong> Bateaux Parisiens boards directly at the Eiffel Tower (Pier 5), saving you a transfer across town. Its 100% curved glass roof also gives superior upward visibility of lit-up monuments compared to standard boat ceilings.',
            compTable: [
                { feature: 'Roof & Windows', winner: '100% Curved Glass Canopy', other: 'Enclosed Salon + Outdoor Roof' },
                { feature: 'Boarding Pier', winner: 'Eiffel Tower (Port de la Bourdonnais)', other: 'Pont de l\'Alma (8th Arr.)' },
                { feature: 'Music Format', winner: 'Live Vocalist & Lounge Band', other: 'Live Violin & Piano Duo' },
                { feature: 'VIP Bow Option', winner: 'Service Premier Front Bow Window', other: 'Club / Window Tiering' }
            ],
            runnerUp: {
                title: 'Bateaux-Mouches Romantic Dinner Cruise',
                badge: 'RUNNER-UP LUXURY DINNER',
                desc: 'Classic French romance with live violin & piano duo and large open rooftop deck from Pont de l\'Alma.',
                price: 'From €115/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bm-dinner',
                btnText: 'View Bateaux Mouches Dinner Option →'
            },
            testimonial: {
                quote: 'Sitting under the curved glass ceiling as Notre-Dame and the Louvre drifted past felt like a movie. The live singer had an incredible voice and the Service Premier table at the bow was worth every single euro.',
                author: '— Robert & Claire, Chicago (Traveled October 2025)'
            }
        },

        // #5 [NEW NICHE] Modern Lounge Yacht + Singer & DJ Party (Beaugrenelle)
        diamant_bleu: {
            id: '1049009',
            key: 'diamant_bleu',
            name: 'Le Diamant Bleu Gourmet Dinner & DJ Party Cruise',
            badge: '🏆 BEST PARTY & ROOFTOP LOUNGE YACHT',
            matchBanner: '99% MATCH FOR ROOFTOP LOUNGE & NIGHTLIFE',
            matchRank: '#1 Luxury Party Superyacht with Live DJ on the Seine',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/6533a18de7a6dfe0f19883b0_le-diamant-bleu.webp',
            rating: '4.6 / 5.0',
            reviewCount: '(Over 1,450+ Verified Reviews)',
            adultPrice: 89.00,
            childPrice: 45.00,
            hasChildPrice: false,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Le Diamant Bleu</strong> is your ultimate match. Unlike traditional quiet boats, this sleek 70-meter modern superyacht features a breathtaking 350 m² teak rooftop lounge terrace, gourmet cuisine by an onboard chef, a live vocalist during dinner, and a live DJ dance party on the river until 23:00.',
            reasons: [
                {
                    icon: '🍸',
                    title: '350 m² Teak Rooftop Lounge Terrace',
                    desc: 'Massive open-air sky deck with chic cocktail bar, lounge seating, and 360° illuminated skyline views.'
                },
                {
                    icon: '🎧',
                    title: 'Live Singer & Onboard DJ Dance Party',
                    desc: 'Festive, stylish nightlife atmosphere on the water without stuffy violin recitals or rigid etiquette.'
                },
                {
                    icon: '🍽️',
                    title: 'Fresh 3-Course Gourmet Cuisine',
                    desc: 'Modern French seasonal dishes cooked fresh by a dedicated culinary brigade right in the ship\'s galley.'
                },
                {
                    icon: '🗼',
                    title: 'Beaugrenelle Pier Departure',
                    desc: 'Departs Port de Grenelle right beside the illuminated Statue of Liberty and Eiffel Tower.'
                }
            ],
            priceAmount: '€89',
            priceSub: 'Includes 3-course dinner + live singer + DJ dance party',
            urgencyTitle: 'Weekend Party Slots Fill Fast:',
            urgencyText: 'Rooftop cocktail tables and weekend party cruises sell out 5–7 days in advance. 24h free cancellation.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-diamond-blue-gourmet-dinner-cruise-p1049009/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-diamant-bleu',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE (€89) →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not Bateaux Mouches or Parisiens?</strong> Traditional boats feature formal quiet dining with classical violin/accordion. If you are celebrating a birthday, girls\' trip, or romantic evening and want upbeat music, cocktails, and dancing under the stars, Diamant Bleu is in a league of its own.',
            compTable: [
                { feature: 'Onboard Atmosphere', winner: 'Modern Lounge Yacht + Live DJ & Dancing', other: 'Classical Live Violin & Piano' },
                { feature: 'Rooftop Terrace', winner: '350 m² Furnished Teak Sky Lounge', other: 'Standard Observation Deck' },
                { feature: 'Evening Vibe', winner: 'Festive, Chic Celebration', other: 'Quiet Formal Date Night' },
                { feature: 'Ticket Cost', winner: 'From €89.00', other: 'From €115.00 – €135.00' }
            ],
            runnerUp: {
                title: 'Théo Trattoria Italian Dinner Cruise',
                badge: 'RUNNER-UP CASUAL DINING',
                desc: 'Fun, casual boutique barge serving fresh pasta, burrata, and Italian wine on the Seine for €69.',
                price: 'From €69/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-trattoria-dinner-cruise-p1071588/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-trattoria',
                btnText: 'View Théo Trattoria Option →'
            },
            testimonial: {
                quote: 'We celebrated my 30th birthday on Diamant Bleu and it was hands down the highlight of Paris! The rooftop deck at sunset is stunning, the food was delicious, and dancing on the boat while the Eiffel Tower sparkled was unforgettable.',
                author: '— Camille & Friends, Brussels (Traveled July 2025)'
            }
        },

        // #6 [NEW NICHE] Sunset Drinks / Apéritif & French Music (Pont d'Iéna)
        vedettes_apero: {
            id: '1003911',
            key: 'vedettes_apero',
            name: 'Vedettes de Paris Sunset Apéritif Cruise',
            badge: '🏆 BEST CASUAL SUNSET DRINKS & APÉRITIF',
            matchBanner: '98% MATCH FOR SUNSET DRINKS & CASUAL VIBES',
            matchRank: '#1 French Music & Apéritif Cruise at the Eiffel Tower',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/6568d166d4e11ba881970fcf_vedettes-de-paris.webp',
            rating: '4.6 / 5.0',
            reviewCount: '(Over 5,300+ Verified Traveler Reviews)',
            adultPrice: 22.00,
            childPrice: 14.00,
            hasChildPrice: true,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Vedettes de Paris Apéritif Cruise</strong> is your ideal match. Departing from Pont d\'Iéna right at the foot of the Eiffel Tower on intimate boutique catamarans (250 passengers), this 1-hour cruise pairs golden-hour views with an onboard bar serving Champagne, artisanal French beer, or wine with savory snacks and an authentic French indie playlist.',
            reasons: [
                {
                    icon: '🥂',
                    title: 'Chilled Drink & French Snack Included',
                    desc: 'Enjoy a glass of authentic French wine, Champagne, craft beer, or soft drink served with snacks.'
                },
                {
                    icon: '⛵',
                    title: 'Boutique Catamaran Ambiance',
                    desc: 'Intimate 250-passenger boat that avoids the overwhelming crowds of 1,000-passenger mass tourist barges.'
                },
                {
                    icon: '🎵',
                    title: 'Curated French Indie Playlist',
                    desc: 'Relaxed electro-pop and French indie tunes replacing dry multilingual museum commentary.'
                },
                {
                    icon: '🗼',
                    title: 'Pont d\'Iéna Pier at the Eiffel Tower',
                    desc: 'Boards right on the bridge between Trocadéro and the Eiffel Tower for effortless evening timing.'
                }
            ],
            priceAmount: '€22',
            priceSub: '1-hour sunset cruise + drink of choice included',
            urgencyTitle: 'Sunset Slots Sell Out Fast:',
            urgencyText: 'Golden-hour departures (19:30–21:00) have strictly limited capacity. Reserve ahead with 24h free cancellation.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-aperitif-cruise-on-the-seine-p1003911/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-vedettes-apero',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE (€22) →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not standard sightseeing (€18)?</strong> Standard sightseeing boats have no bar service, no drinks, and feel like group transit. <strong>Why not a full dinner cruise (€115+)?</strong> A full dinner takes 2.5 hours and forces you to eat on their schedule; Vedettes de Paris gives you drinks and sunset views in 1 hour, leaving your night wide open.',
            compTable: [
                { feature: 'Vessel Size', winner: 'Boutique 250-Seat Catamaran', other: '800–1,000 Passenger Giant Ships' },
                { feature: 'Drinks Included', winner: 'Wine, Champagne or Beer + Snack', other: 'None / Audio Headset Only' },
                { feature: 'Music Format', winner: 'Relaxed French Indie Playlist', other: 'Multilingual Tour Commentary' },
                { feature: 'Ticket Cost', winner: '€22.00 – €28.00', other: '€115.00+ (Sit-Down Dinner)' }
            ],
            runnerUp: {
                title: 'Bateaux Parisiens Sightseeing Cruise',
                badge: 'RUNNER-UP OPTION',
                desc: 'Classic 1-hour cruise with 14-language audio guide departing Pier 3 at the Eiffel Tower for €18.',
                price: 'From €18/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-sightseeing-cruise-on-the-seine-p973977/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bp-sightseeing',
                btnText: 'View Bateaux Parisiens Option →'
            },
            testimonial: {
                quote: 'Sipping chilled rosé on the front deck with French indie tunes playing while the sun set behind Notre-Dame was bliss. Not crowded, very romantic, and we were off by 9 PM to dinner!',
                author: '— Leo & Sophie, Amsterdam (Traveled July 2025)'
            }
        },

        // #7 [NEW NICHE] 24h Hop-On Hop-Off River Shuttle Pass (Batobus)
        batobus_shuttle: {
            id: '976735',
            key: 'batobus_shuttle',
            name: 'Batobus Paris 24h Hop-On Hop-Off River Shuttle',
            badge: '🏆 BEST RIVER TRANSPORT & MONUMENT HOPPING',
            matchBanner: '96% MATCH FOR UNLIMITED MONUMENT TRANSIT',
            matchRank: '#1 Flexible River Shuttle Pass Across 9 Paris Stops',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/65848a61b5df26ea46248b7e_Batobu-sightseeing-cruise-blog-image%20(15).webp',
            rating: '4.3 / 5.0',
            reviewCount: '(Over 8,400+ Verified Traveler Reviews)',
            adultPrice: 23.00,
            childPrice: 13.00,
            hasChildPrice: true,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, the <strong>Batobus 24-Hour River Pass</strong> gives you maximum transit freedom. Hop on and off as many times as you like across 9 central river stops connecting the Eiffel Tower, Louvre, Musée d\'Orsay, Saint-Germain, and Notre-Dame.',
            reasons: [
                {
                    icon: '📍',
                    title: '9 Central Riverfront Stations',
                    desc: 'Dock directly beside Eiffel Tower, Musée d\'Orsay, Saint-Germain, Notre-Dame, Louvre, and Concorde.'
                },
                {
                    icon: '🎫',
                    title: 'Unlimited 24-Hour Hop-On Hop-Off',
                    desc: 'Use the Seine as your scenic city highway all day long with flexible unlimited boarding.'
                },
                {
                    icon: '🌤️',
                    title: 'Avoid Underground Metro Tunnels',
                    desc: 'Travel between Paris sights in fresh open river air rather than dark crowded subway cars.'
                },
                {
                    icon: '💶',
                    title: 'Exceptional Multi-Stop Value',
                    desc: 'Just €23 for 24 full hours of boat transport across central Paris (kids under 12 only €13).'
                }
            ],
            priceAmount: '€23',
            priceSub: 'Unlimited 24-hour hop-on hop-off pass • Kids €13',
            urgencyTitle: 'All-Day Pass Activation:',
            urgencyText: 'Pass activates at first boarding and remains valid for a full 24 consecutive hours. Free 24h cancellation.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-batobus-riverboat-hop-on-hop-off-p976735/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-batobus',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE (€23) →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>⚠️ The Detective\'s Candid Trade-Off Warning:</strong> Batobus is an <em>urban water taxi</em>, not a luxury sightseeing cruise. It has single-deck flat windows, no guided audio commentary, and boats run every 25–30 minutes. If your priority is uninterrupted 360° photography and crystal-clear historical narration, choose <strong>Bateaux Parisiens (€18)</strong> instead.',
            compTable: [
                { feature: 'Ticket Freedom', winner: 'Unlimited 24h Boarding (9 Stops)', other: 'Single 60-Minute Continuous Loop' },
                { feature: 'Transit Utility', winner: 'Connects Louvre, Orsay & Eiffel', other: 'Departs & Returns to Same Pier' },
                { feature: 'Audio Guide', winner: 'None (Self-Guided Transit)', other: '14-Language Personal Handsets' },
                { feature: 'Best Used For', winner: 'Getting Around Between Sights', other: 'Pure Photography & Sightseeing' }
            ],
            runnerUp: {
                title: 'Bateaux Parisiens Sightseeing Cruise',
                badge: 'RUNNER-UP SIGHTSEEING',
                desc: 'If you want pure sightseeing with 14-language audio guide and 360° roof deck in 1 hour for €18.',
                price: 'From €18/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-sightseeing-cruise-on-the-seine-p973977/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-bp-sightseeing',
                btnText: 'View Bateaux Parisiens Sightseeing →'
            },
            testimonial: {
                quote: 'We used Batobus to travel between the Eiffel Tower, the Orsay, and Notre-Dame. So much nicer than taking the metro underground, and the kids loved being on the water all day!',
                author: '— Mark & Family, Chicago (Traveled June 2025)'
            }
        },

        // #8 Smart Value Bistro Dinner (Paris en Scène)
        pes_bistro: {
            id: '1052475',
            key: 'pes_bistro',
            name: 'Paris en Scène Bistro Dinner Cruise',
            badge: '🏆 BEST VALUE DINNER CRUISE IN PARIS',
            matchBanner: '97% MATCH FOR SMART VALUE DINING',
            matchRank: '#1 Budget-Friendly Seine Dinner Cruise',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/6533a18d6a9176ae6b373f3b_paris-en-scene.webp',
            rating: '4.6 / 5.0',
            reviewCount: '(Over 6,200+ Verified Traveler Reviews)',
            adultPrice: 55.00,
            childPrice: 45.00,
            hasChildPrice: false,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Paris en Scène</strong> is your ideal match. For roughly half the price of traditional luxury riverboats, it delivers a fresh 3-course French bistro meal, comfortable club armchairs facing floor-to-ceiling windows, and prime illuminated monument views.',
            reasons: [
                {
                    icon: '🛋️',
                    title: 'Club Armchairs Facing the River',
                    desc: 'Unique theater-style seating where every seat directly faces panoramic glass windows.'
                },
                {
                    icon: '🍽️',
                    title: 'Freshly Cooked 3-Course Bistro Menu',
                    desc: 'Starter, main dish, and dessert prepared freshly onboard during your 1h45 cruise.'
                },
                {
                    icon: '💶',
                    title: 'Unbeatable Price-to-Value Ratio',
                    desc: 'At just €55–€75 per person, it is by far the most economical full dinner cruise on the Seine.'
                },
                {
                    icon: '🗼',
                    title: 'Eiffel Tower Illumination Stop',
                    desc: 'Slows down directly in front of the illuminated Eiffel Tower for unforgettable evening photos.'
                }
            ],
            priceAmount: '€55',
            priceSub: 'Full 3-course dinner + 1h45 Seine river cruise',
            urgencyTitle: 'Limited Window Seating:',
            urgencyText: 'Club armchairs fill quickly for sunset and evening slots. Reserve ahead for best views.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-en-scene-dinner-cruise-p1052475/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-pes-bistro',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE (€55) →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not luxury boats like Bateaux Mouches (€115–€165) or Bateaux Parisiens (€115–€215)?</strong> Luxury boats cost more than double. If you want a tasty hot meal and scenic river views without paying fine-dining prices, Paris en Scène gives you 85% of the experience for half the spend.',
            compTable: [
                { feature: 'Seating Layout', winner: 'Panoramic Club Armchairs', other: 'Shared Dining Tables' },
                { feature: 'Dining Style', winner: '3-Course Fresh Bistro Cuisine', other: '4-Course Haute Gastronomy' },
                { feature: 'Atmosphere', winner: 'Relaxed, Casual Bistro Vibe', other: 'Formal Fine Dining (Dress Code)' },
                { feature: 'Price per Person', winner: 'From €55.00', other: 'From €115.00 – €165.00' }
            ],
            runnerUp: {
                title: 'Théo Trattoria Dinner Cruise',
                badge: 'RUNNER-UP CASUAL DINNER',
                desc: 'Casual, festive Italian river dinner cruise serving burrata, fresh pasta, and tiramisu on a modern boat.',
                price: 'From €69/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-trattoria-dinner-cruise-p1071588/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-trattoria',
                btnText: 'View Théo Trattoria Option →'
            },
            testimonial: {
                quote: 'We didn\'t want to spend €300 on a fancy dinner, so Paris en Scène was perfection. The club chairs face right out at the river, the 3-course meal was surprisingly delicious, and the Eiffel Tower view at night was breathtaking for only €55!',
                author: '— Chloe & Julien, Montreal (Traveled August 2025)'
            }
        },

        // #9 Casual Hip Italian River Dining (Théo Trattoria)
        theo_trattoria: {
            id: '1071588',
            key: 'theo_trattoria',
            name: 'Théo Trattoria Italian Dinner Cruise',
            badge: '🏆 BEST HIP & CASUAL ITALIAN RIVER DINING',
            matchBanner: '97% MATCH FOR CASUAL BOUTIQUE DINING',
            matchRank: '#1 Italian Culinary Cruise on the Seine',
            image: 'https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/655a4b007363595120622632_Paris-en-scene%20(8)-p-800.webp',
            rating: '4.6 / 5.0',
            reviewCount: '(Over 1,800+ Verified Traveler Reviews)',
            adultPrice: 69.00,
            childPrice: 45.00,
            hasChildPrice: false,
            defaultAdults: 2,
            defaultChildren: 0,
            hook: 'Based on your specific answers, <strong>Théo Trattoria en Seine</strong> is your ideal match. Setting sail from Port de Grenelle, this intimate 120-seat boutique barge breaks away from stuffy French banquets, serving creamy burrata, artisanal truffle pasta, and homemade tiramisu with Italian wines and panoramic monument views.',
            reasons: [
                {
                    icon: '🍝',
                    title: 'Fresh Artisanal Italian Menu',
                    desc: 'Creamy burrata pugliese, freshly made pasta, and authentic tiramisu prepared onboard.'
                },
                {
                    icon: '⛵',
                    title: 'Intimate 120-Seat Boutique Barge',
                    desc: 'Small, relaxed vessel with floor-to-ceiling windows and zero commercial tour group feel.'
                },
                {
                    icon: '🍷',
                    title: 'Italian Wines & Spritz Cocktails',
                    desc: 'Enjoy Prosecco and Aperol Spritz on the Seine with views of illuminated bridges.'
                },
                {
                    icon: '👟',
                    title: 'Smart Casual Dress Code',
                    desc: 'No jackets or ties required. Relaxed, trendy, and welcoming for young couples and friend groups.'
                }
            ],
            priceAmount: '€69',
            priceSub: 'Full 3-course Italian dinner + 2h river cruise',
            urgencyTitle: 'Small Vessel Notice:',
            urgencyText: 'With only 120 seats, tables sell out 3–5 days ahead on weekends. 24h free cancellation.',
            ctaUrl: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-trattoria-dinner-cruise-p1071588/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-trattoria',
            ctaHeadline: 'CHECK LIVE AVAILABILITY & RESERVE (€69) →',
            ctaSubline: 'Official Tiqets Partner • Instant Mobile Voucher • Free 24h Cancellation',
            whyNotText: '<strong>Why not traditional French luxury dinner?</strong> Traditional boats cost €115–€135 with formal attire. If you prefer a laid-back, trendy atmosphere with delicious Italian comfort food and great music, Théo Trattoria is a refreshing alternative.',
            compTable: [
                { feature: 'Cuisine Style', winner: 'Fresh Italian Trattoria (Burrata, Pasta)', other: 'Traditional French Haute Cuisine' },
                { feature: 'Vessel Scale', winner: 'Boutique 120-Seat Barge', other: 'Large 400–800 Seat Ships' },
                { feature: 'Dress Code', winner: 'Smart Casual (Relaxed)', other: 'Strict Smart/Formal' },
                { feature: 'Price per Person', winner: 'From €69.00', other: 'From €115.00 – €135.00' }
            ],
            runnerUp: {
                title: 'Paris en Scène Bistro Cruise',
                badge: 'RUNNER-UP VALUE DINNER',
                desc: 'Budget 3-course French bistro meal in panoramic club armchairs from €55.',
                price: 'From €55/person',
                url: 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-en-scene-dinner-cruise-p1052475/?partner=thecruisedetective.com-176436&tq_campaign=paris-cruise-quiz-pes-bistro',
                btnText: 'View Paris en Scène Option →'
            },
            testimonial: {
                quote: 'What a fun and delicious night! The truffle pasta was genuinely fantastic, the boat felt cozy and chic, and seeing the Eiffel Tower light up while having tiramisu was incredible.',
                author: '— Alessia & Tom, Milan (Traveled September 2025)'
            }
        }
    };

    // -------------------------------------------------------------
    // 3. Quiz State & Multi-Factor Scoring Machine
    // -------------------------------------------------------------
    const stepIntro = document.getElementById('step-intro');
    const stepQ1 = document.getElementById('step-q1');
    const stepQ2 = document.getElementById('step-q2');
    const stepQ3 = document.getElementById('step-q3');
    const stepQ4 = document.getElementById('step-q4');
    const stepQ5 = document.getElementById('step-q5');
    const stepLoading = document.getElementById('step-loading');
    const stepResults = document.getElementById('step-results');
    
    const progressContainer = document.getElementById('progress-container');
    const questionStepLabel = document.getElementById('question-step-label');
    const progressPercent = document.getElementById('progress-percent');
    const progressFill = document.getElementById('progress-fill');
    const btnBackStep = document.getElementById('btn-back-step');

    const btnStart = document.getElementById('btn-start-quiz');
    const btnRestart = document.getElementById('btn-restart-quiz');

    const quizSteps = [stepQ1, stepQ2, stepQ3, stepQ4, stepQ5];
    let currentStepIndex = 0;

    const quizAnswers = {
        experience: null,
        party: null,
        timing: null,
        priority: null,
        budget: null
    };

    let activeMatch = null;
    let basketState = {
        adults: 2,
        children: 0
    };

    function showStep(stepElement) {
        [stepIntro, stepQ1, stepQ2, stepQ3, stepQ4, stepQ5, stepLoading, stepResults].forEach(el => {
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

    function updateProgress(stepNum, totalSteps = 5) {
        const percent = Math.round((stepNum / totalSteps) * 100);
        if (questionStepLabel) questionStepLabel.textContent = `Question ${stepNum} of ${totalSteps}`;
        if (progressPercent) progressPercent.textContent = `${percent}% Complete`;
        if (progressFill) progressFill.style.width = `${percent}%`;

        if (btnBackStep) {
            btnBackStep.style.display = stepNum > 1 ? 'flex' : 'none';
        }
    }

    function calculateMultiFactorMatch(answers) {
        const scores = {
            bp_sightseeing: 0,
            bm_sightseeing: 0,
            bm_dinner: 0,
            bp_dinner: 0,
            diamant_bleu: 0,
            vedettes_apero: 0,
            batobus_shuttle: 0,
            pes_bistro: 0,
            theo_trattoria: 0
        };

        // Q1: Experience format
        if (answers.experience === 'sightseeing') {
            scores.bp_sightseeing += 55;
            scores.bm_sightseeing += 45;
            scores.vedettes_apero += 15;
        } else if (answers.experience === 'dinner-gourmet') {
            scores.bm_dinner += 48;
            scores.bp_dinner += 42;
            scores.diamant_bleu += 15;
        } else if (answers.experience === 'dinner-bistro') {
            scores.pes_bistro += 55;
            scores.theo_trattoria += 42;
        } else if (answers.experience === 'party-lounge') {
            scores.diamant_bleu += 65;
            scores.theo_trattoria += 25;
            scores.vedettes_apero += 15;
        } else if (answers.experience === 'champagne-aperitif') {
            scores.vedettes_apero += 65;
            scores.bp_sightseeing += 10;
        } else if (answers.experience === 'hop-on-hop-off') {
            scores.batobus_shuttle += 70;
            scores.bp_sightseeing += 10;
        } else if (answers.experience === 'lunch-daylight') {
            scores.bp_dinner += 45;
            scores.bp_sightseeing += 25;
        }

        // Q2: Party composition
        if (answers.party === 'family') {
            scores.bp_sightseeing += 30;
            scores.bm_sightseeing += 25;
            scores.batobus_shuttle += 25;
            scores.pes_bistro += 15;
            scores.bm_dinner -= 25;
            scores.diamant_bleu -= 30;
        } else if (answers.party === 'couple') {
            scores.bm_dinner += 28;
            scores.bp_dinner += 24;
            scores.vedettes_apero += 22;
            scores.diamant_bleu += 20;
            scores.theo_trattoria += 18;
        } else if (answers.party === 'friends') {
            scores.diamant_bleu += 35;
            scores.vedettes_apero += 30;
            scores.theo_trattoria += 25;
            scores.bm_sightseeing += 20;
            scores.batobus_shuttle += 15;
        } else if (answers.party === 'solo') {
            scores.bp_sightseeing += 30;
            scores.bm_sightseeing += 25;
            scores.batobus_shuttle += 25;
            scores.vedettes_apero += 20;
        }

        // Q3: Timing & Lighting
        if (answers.timing === 'night-sparkle') {
            scores.bm_dinner += 26;
            scores.bp_dinner += 24;
            scores.diamant_bleu += 28;
            scores.bp_sightseeing += 15;
            scores.bm_sightseeing += 15;
        } else if (answers.timing === 'sunset-golden') {
            scores.vedettes_apero += 32;
            scores.bm_sightseeing += 22;
            scores.diamant_bleu += 20;
            scores.pes_bistro += 15;
            scores.bp_sightseeing += 15;
        } else if (answers.timing === 'daylight') {
            scores.bp_sightseeing += 32;
            scores.bm_sightseeing += 30;
            scores.batobus_shuttle += 28;
        } else if (answers.timing === 'flexible-today') {
            scores.bp_sightseeing += 40;
            scores.bm_sightseeing += 28;
            scores.batobus_shuttle += 30;
            scores.bm_dinner -= 20;
            scores.diamant_bleu -= 20;
        }

        // Q4: Must-have feature
        if (answers.priority === 'pier-eiffel') {
            scores.bp_sightseeing += 32;
            scores.bp_dinner += 30;
            scores.vedettes_apero += 25;
            scores.bm_dinner -= 10;
            scores.bm_sightseeing -= 10;
        } else if (answers.priority === 'rooftop-deck') {
            scores.bm_sightseeing += 38;
            scores.bm_dinner += 25;
            scores.diamant_bleu += 25;
            scores.bp_sightseeing += 10;
        } else if (answers.priority === 'gourmet-music') {
            scores.bm_dinner += 35;
            scores.bp_dinner += 25;
        } else if (answers.priority === 'party-dj') {
            scores.diamant_bleu += 60;
            scores.theo_trattoria += 20;
        } else if (answers.priority === 'drinks-music') {
            scores.vedettes_apero += 55;
            scores.bp_sightseeing += 10;
        } else if (answers.priority === 'transit-shuttle') {
            scores.batobus_shuttle += 65;
        } else if (answers.priority === 'glass-canopy') {
            scores.bp_dinner += 32;
            scores.bp_sightseeing += 20;
        } else if (answers.priority === 'budget-value') {
            scores.bp_sightseeing += 28;
            scores.bm_sightseeing += 28;
            scores.pes_bistro += 28;
            scores.batobus_shuttle += 22;
            scores.bm_dinner -= 20;
        }

        // Q5: Budget Range
        if (answers.budget === 'budget-sightseeing') {
            scores.bp_sightseeing += 42;
            scores.bm_sightseeing += 42;
            scores.batobus_shuttle += 10;
            scores.bm_dinner -= 60;
            scores.bp_dinner -= 60;
            scores.diamant_bleu -= 60;
        } else if (answers.budget === 'budget-aperitif') {
            scores.vedettes_apero += 45;
            scores.batobus_shuttle += 35;
            scores.bp_sightseeing += 15;
            scores.bm_dinner -= 40;
        } else if (answers.budget === 'budget-bistro') {
            scores.pes_bistro += 45;
            scores.theo_trattoria += 35;
        } else if (answers.budget === 'budget-party') {
            scores.diamant_bleu += 50;
            scores.theo_trattoria += 38;
        } else if (answers.budget === 'budget-gourmet') {
            scores.bm_dinner += 35;
            scores.bp_dinner += 30;
            scores.diamant_bleu += 15;
        } else if (answers.budget === 'budget-vip') {
            scores.bp_dinner += 40;
            scores.bm_dinner += 28;
        }

        const rankedKeys = Object.keys(scores).sort((a, b) => scores[b] - scores[a]);
        return {
            winner: CRUISE_DATABASE[rankedKeys[0]],
            runnerUp: CRUISE_DATABASE[rankedKeys[1]],
            scores
        };
    }

    function generatePersonalizedTags(answers, match) {
        const tags = [];
        if (answers.priority === 'pier-eiffel' || match.id === '973977' || match.id === '974358' || match.id === '1003911') {
            tags.push('✓ Eiffel Tower Boarding');
        }
        if (answers.party === 'family' || match.hasChildPrice) {
            tags.push('✓ Kid-Friendly Rates');
        }
        if (answers.party === 'couple') {
            tags.push('✓ Verified Couple Ambiance');
        }
        if (match.key === 'diamant_bleu') {
            tags.push('✓ Rooftop Lounge & Live DJ');
        }
        if (match.key === 'vedettes_apero') {
            tags.push('✓ Sunset Drinks & French Music');
        }
        if (match.key === 'batobus_shuttle') {
            tags.push('✓ 9 Monument River Stops');
        }
        if (match.key === 'bm_sightseeing') {
            tags.push('✓ 360° Open-Air Rooftop Deck');
        }
        if (answers.timing === 'flexible-today' || match.key === 'bp_sightseeing') {
            tags.push('✓ All-Day Open Voucher');
        }
        if (match.key === 'bm_dinner') {
            tags.push('✓ Live Violin & Piano Duo');
        }
        if (match.key === 'pes_bistro') {
            tags.push('✓ Panoramic Club Armchairs');
        }
        return tags.slice(0, 4);
    }

    function updateBasketDisplay() {
        if (!activeMatch) return;

        const totalCost = (basketState.adults * activeMatch.adultPrice) + (basketState.children * (activeMatch.childPrice || 0));
        
        const countAdultsEl = document.getElementById('count-adults');
        const countKidsEl = document.getElementById('count-kids');
        const basketTotalEl = document.getElementById('basket-total-amount');
        const primaryCta = document.querySelector('.cta-button.primary-cta');

        if (countAdultsEl) countAdultsEl.textContent = basketState.adults;
        if (countKidsEl) countKidsEl.textContent = basketState.children;
        if (basketTotalEl) basketTotalEl.textContent = `€${totalCost.toFixed(2)}`;

        if (primaryCta) {
            primaryCta.dataset.checkoutValue = totalCost.toFixed(2);
            const headlineEl = primaryCta.querySelector('.cta-headline');
            if (headlineEl) {
                headlineEl.textContent = `CHECK LIVE AVAILABILITY & RESERVE (€${totalCost.toFixed(2)}) →`;
            }
        }
    }

    function renderResults(matchData, answers) {
        const match = matchData.winner;
        const runnerUp = matchData.runnerUp;
        activeMatch = match;

        basketState.adults = answers.party === 'solo' ? 1 : 2;
        basketState.children = (answers.party === 'family' && match.hasChildPrice) ? 2 : 0;

        const matchScoreEl = document.querySelector('.match-score');
        if (matchScoreEl) matchScoreEl.textContent = match.matchBanner;

        const matchRankEl = document.querySelector('.match-rank');
        if (matchRankEl) matchRankEl.textContent = match.matchRank;

        const tagCloud = document.querySelector('.match-tag-cloud');
        if (tagCloud) {
            const tags = generatePersonalizedTags(answers, match);
            tagCloud.innerHTML = tags.map(t => `<span class="match-tag-item">${t}</span>`).join('');
        }

        const resultImg = document.querySelector('.result-img');
        if (resultImg) {
            resultImg.src = match.image;
            resultImg.alt = match.name;
        }
        const resultTag = document.querySelector('.result-tag');
        if (resultTag) resultTag.textContent = match.badge;

        const resultTitle = document.querySelector('.result-title');
        if (resultTitle) resultTitle.textContent = match.name;

        const ratingNum = document.querySelector('.rating-num');
        if (ratingNum) ratingNum.textContent = match.rating;

        const reviewCount = document.querySelector('.review-count');
        if (reviewCount) reviewCount.textContent = match.reviewCount;

        const resultHook = document.querySelector('.result-hook');
        if (resultHook) resultHook.innerHTML = match.hook;

        const reasonsContainer = document.querySelector('.match-reasons');
        if (reasonsContainer && Array.isArray(match.reasons)) {
            reasonsContainer.innerHTML = match.reasons.map(r => `
                <div class="reason-row">
                    <span class="reason-icon">${r.icon}</span>
                    <div>
                        <strong>${r.title}</strong>
                        <p>${r.desc}</p>
                    </div>
                </div>
            `).join('');
        }

        const whyNotBody = document.querySelector('.why-not-body');
        if (whyNotBody && match.whyNotText) {
            whyNotBody.innerHTML = match.whyNotText;
        }

        const compTableContainer = document.querySelector('.comp-table-body');
        if (compTableContainer && match.compTable) {
            compTableContainer.innerHTML = match.compTable.map(row => `
                <tr>
                    <td><strong>${row.feature}</strong></td>
                    <td class="winner-cell">${row.winner}</td>
                    <td>${row.other}</td>
                </tr>
            `).join('');
        }

        const priceAmount = document.querySelector('.price-amount');
        if (priceAmount) priceAmount.innerHTML = `${match.priceAmount}<small>/person</small>`;

        const priceSub = document.querySelector('.price-sub');
        if (priceSub) priceSub.textContent = match.priceSub;

        const urgencySide = document.querySelector('.urgency-side div');
        if (urgencySide) {
            urgencySide.innerHTML = `
                <strong>${match.urgencyTitle}</strong>
                <span>${match.urgencyText}</span>
            `;
        }

        const adultPriceLabel = document.getElementById('stepper-adult-rate');
        if (adultPriceLabel) adultPriceLabel.textContent = `€${match.adultPrice.toFixed(2)} each`;

        const kidStepper = document.getElementById('stepper-item-kids');
        if (kidStepper) {
            if (match.hasChildPrice) {
                kidStepper.style.display = 'flex';
                const kidPriceLabel = document.getElementById('stepper-kid-rate');
                if (kidPriceLabel) kidPriceLabel.textContent = `€${match.childPrice.toFixed(2)} (kids)`;
            } else {
                kidStepper.style.display = 'none';
                basketState.children = 0;
            }
        }

        const primaryCta = document.querySelector('.cta-button.primary-cta');
        if (primaryCta) {
            primaryCta.href = match.ctaUrl;
            primaryCta.dataset.cruiseName = match.name;
            const ctaSubline = primaryCta.querySelector('.cta-subline');
            if (ctaSubline) ctaSubline.textContent = match.ctaSubline;
        }

        const runnerUpCard = document.querySelector('.runner-up-card');
        if (runnerUpCard && match.runnerUp) {
            const runnerTitle = runnerUpCard.querySelector('h3');
            if (runnerTitle) runnerTitle.textContent = match.runnerUp.title;

            const runnerDesc = runnerUpCard.querySelector('.runner-desc');
            if (runnerDesc) runnerDesc.textContent = match.runnerUp.desc;

            const runnerPrice = runnerUpCard.querySelector('.runner-price');
            if (runnerPrice) runnerPrice.textContent = match.runnerUp.price;

            const runnerBtn = runnerUpCard.querySelector('.btn-secondary');
            if (runnerBtn) {
                runnerBtn.href = match.runnerUp.url;
                runnerBtn.textContent = match.runnerUp.btnText;
                runnerBtn.dataset.cruiseName = match.runnerUp.title;
            }
        }

        const testimonial = document.querySelector('.couple-testimonial');
        if (testimonial && match.testimonial) {
            const quoteText = testimonial.querySelector('.quote-text');
            if (quoteText) quoteText.textContent = `"${match.testimonial.quote}"`;

            const quoteAuthor = testimonial.querySelector('.quote-author');
            if (quoteAuthor) quoteAuthor.textContent = match.testimonial.author;
        }

        updateBasketDisplay();
        decorateAllLinks();
        attachTrackingToButtons();
    }

    // -------------------------------------------------------------
    // 4. Steppers & Basket Calculator Event Listeners
    // -------------------------------------------------------------
    const btnAdultPlus = document.getElementById('btn-adult-plus');
    const btnAdultMinus = document.getElementById('btn-adult-minus');
    const btnKidPlus = document.getElementById('btn-kid-plus');
    const btnKidMinus = document.getElementById('btn-kid-minus');

    if (btnAdultPlus) {
        btnAdultPlus.addEventListener('click', () => {
            if (basketState.adults < 12) {
                basketState.adults++;
                updateBasketDisplay();
            }
        });
    }

    if (btnAdultMinus) {
        btnAdultMinus.addEventListener('click', () => {
            if (basketState.adults > 1) {
                basketState.adults--;
                updateBasketDisplay();
            }
        });
    }

    if (btnKidPlus) {
        btnKidPlus.addEventListener('click', () => {
            if (basketState.children < 10) {
                basketState.children++;
                updateBasketDisplay();
            }
        });
    }

    if (btnKidMinus) {
        btnKidMinus.addEventListener('click', () => {
            if (basketState.children > 0) {
                basketState.children--;
                updateBasketDisplay();
            }
        });
    }

    // -------------------------------------------------------------
    // 5. Step Transitions & Click Handlers
    // -------------------------------------------------------------
    if (btnStart) {
        btnStart.addEventListener('click', () => {
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStart');
            }
            if (progressContainer) progressContainer.style.display = 'block';
            currentStepIndex = 0;
            updateProgress(1, 5);
            showStep(stepQ1);
        });
    }

    if (btnBackStep) {
        btnBackStep.addEventListener('click', () => {
            if (currentStepIndex > 0) {
                currentStepIndex--;
                updateProgress(currentStepIndex + 1, 5);
                showStep(quizSteps[currentStepIndex]);
            }
        });
    }

    // Q1: Experience format
    stepQ1.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.experience = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 1, answer: quizAnswers.experience });
            }
            currentStepIndex = 1;
            updateProgress(2, 5);
            showStep(stepQ2);
        });
    });

    // Q2: Party composition
    stepQ2.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.party = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 2, answer: quizAnswers.party });
            }
            currentStepIndex = 2;
            updateProgress(3, 5);
            showStep(stepQ3);
        });
    });

    // Q3: Timing & Lighting
    stepQ3.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.timing = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 3, answer: quizAnswers.timing });
            }
            currentStepIndex = 3;
            updateProgress(4, 5);
            showStep(stepQ4);
        });
    });

    // Q4: Must-have feature
    stepQ4.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.priority = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 4, answer: quizAnswers.priority });
            }
            currentStepIndex = 4;
            updateProgress(5, 5);
            showStep(stepQ5);
        });
    });

    // Q5: Budget -> Calculation -> Results
    stepQ5.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', () => {
            quizAnswers.budget = option.dataset.answer;
            if (typeof window.fbq === 'function') {
                window.fbq('trackCustom', 'QuizStep', { step: 5, answer: quizAnswers.budget });
            }
            
            if (progressContainer) progressContainer.style.display = 'none';
            showStep(stepLoading);

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
            }, 500);

            setTimeout(() => {
                if (step2) {
                    step2.className = 'check-item done';
                    step2.querySelector('.check-icon').textContent = '✓';
                }
                if (step3) {
                    step3.className = 'check-item active';
                    step3.querySelector('.check-icon').textContent = '⏳';
                }
            }, 1000);

            setTimeout(() => {
                if (step3) {
                    step3.className = 'check-item done';
                    step3.querySelector('.check-icon').textContent = '✓';
                }
            }, 1500);

            setTimeout(() => {
                const matchResult = calculateMultiFactorMatch(quizAnswers);
                renderResults(matchResult, quizAnswers);
                showStep(stepResults);

                if (typeof window.fbq === 'function') {
                    window.fbq('trackCustom', 'QuizCompleted', {
                        match: matchResult.winner.name,
                        matchId: matchResult.winner.id,
                        experience: quizAnswers.experience,
                        party: quizAnswers.party,
                        timing: quizAnswers.timing,
                        priority: quizAnswers.priority,
                        budget: quizAnswers.budget
                    });
                }
            }, 1800);
        });
    });

    // Restart Quiz
    if (btnRestart) {
        btnRestart.addEventListener('click', () => {
            quizAnswers.experience = null;
            quizAnswers.party = null;
            quizAnswers.timing = null;
            quizAnswers.priority = null;
            quizAnswers.budget = null;
            currentStepIndex = 0;

            const step1 = document.getElementById('calc-step-1');
            const step2 = document.getElementById('calc-step-2');
            const step3 = document.getElementById('calc-step-3');
            if (step1) { step1.className = 'check-item active'; step1.querySelector('.check-icon').textContent = '⏳'; }
            if (step2) { step2.className = 'check-item'; step2.querySelector('.check-icon').textContent = '○'; }
            if (step3) { step3.className = 'check-item'; step3.querySelector('.check-icon').textContent = '○'; }

            if (progressContainer) progressContainer.style.display = 'none';
            showStep(stepIntro);
        });
    }
});
