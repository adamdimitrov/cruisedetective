// 1. Set dynamic dates
const dateElement = document.getElementById('dynamic-date');
const yearElement = document.getElementById('current-year');

const today = new Date();

// Set current year for copyright
if (yearElement) {
    yearElement.textContent = today.getFullYear();
}

// Set publish date to a recent date (e.g. today or yesterday) to keep it fresh
if (dateElement) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    dateElement.textContent = today.toLocaleDateString('en-US', options);
}

// 2. Sticky CTA Logic
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

// --- Event Bridging for Shadow DOM ---
// Since the buttons are in the Shadow DOM, the global Facebook Pixel and GTM 
// cannot automatically track clicks on them. We must manually push the events.
const ctaButtons = document.querySelectorAll('.cta-button');

ctaButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        // Push to Facebook Pixel
        if (window.fbq) {
            window.fbq('track', 'InitiateCheckout', {
                content_name: 'Tiqets Affiliate Link',
                content_category: 'Seine River Cruise',
                value: 18.00,
                currency: 'EUR'
            });
        }
        
        // Push to Google Tag Manager / GA4
        if (window.dataLayer) {
            window.dataLayer.push({
                event: 'begin_checkout',
                link_url: button.getAttribute('href')
            });
        }
    });
});
