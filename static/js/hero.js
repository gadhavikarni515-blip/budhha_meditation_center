(function() {
    const updateHeroForViewport = () => {
        const gif = document.querySelector('.nb-hero-gif');
        const poster = document.querySelector('.nb-hero-poster');

        if (!gif) return;

        // Always show the GIF on all devices for better user experience
        // The CSS will handle responsive sizing
        try {
            gif.style.display = 'block';
            gif.setAttribute('aria-hidden', 'false');
            if (poster) {
                poster.style.display = 'none';
                poster.setAttribute('aria-hidden', 'true');
            }
        } catch (err) {
            // ignore errors when toggling display
        }
    };

    // Run at load and on resize (debounced)
    document.addEventListener('DOMContentLoaded', updateHeroForViewport);
    let _heroResizeTimer = null;
    window.addEventListener('resize', () => {
        if (_heroResizeTimer) clearTimeout(_heroResizeTimer);
        _heroResizeTimer = setTimeout(updateHeroForViewport, 150);
    });
    window.addEventListener('orientationchange', () => setTimeout(updateHeroForViewport, 200));
})();