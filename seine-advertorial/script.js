document.addEventListener('DOMContentLoaded', () => {
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
    
    // Check if we are on a mobile device (sticky CTA is most effective here)
    // But we can enable it for all sizes, usually it's hidden or styled differently for desktop.
    // We will show it if scrolled past the header.
    
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
