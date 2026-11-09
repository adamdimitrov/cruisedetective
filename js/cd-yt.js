/*
 * Cruise Detective — lightweight YouTube facade.
 *
 * Markup (rendered server-side, works without JS as a plain link to YouTube):
 *   <a class="cd-yt" href="https://www.youtube.com/watch?v=ID&t=161s"
 *      data-yt="ID" data-start="161" data-title="…"> <img …> <span class="cd-yt-play">…</span> </a>
 *
 * On click the anchor is swapped for a youtube-nocookie iframe (autoplay), so no
 * YouTube JS, cookies or third-party requests load until the visitor asks for the video.
 */
(function () {
  'use strict';

  var EMBED = 'https://www.youtube-nocookie.com/embed/';
  var warmed = false;

  function warm() {
    if (warmed) return;
    warmed = true;
    ['https://www.youtube-nocookie.com', 'https://www.google.com', 'https://i.ytimg.com'].forEach(function (href) {
      var l = document.createElement('link');
      l.rel = 'preconnect';
      l.href = href;
      l.crossOrigin = '';
      document.head.appendChild(l);
    });
  }

  function track(id, start) {
    try {
      var payload = { video_id: id, video_start: start || 0, page_path: location.pathname };
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'video_play', payload);
      } else {
        (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: 'video_play' }, payload));
      }
    } catch (e) { /* analytics must never break playback */ }
  }

  function play(el) {
    var id = el.getAttribute('data-yt');
    if (!id) return;
    var start = parseInt(el.getAttribute('data-start') || '0', 10) || 0;
    var params = 'autoplay=1&rel=0&playsinline=1&modestbranding=1' + (start ? '&start=' + start : '');
    var lang = (document.documentElement.lang || '').slice(0, 2);
    if (lang && lang !== 'en') params += '&hl=' + lang + '&cc_lang_pref=' + lang;

    var iframe = document.createElement('iframe');
    iframe.src = EMBED + encodeURIComponent(id) + '?' + params;
    iframe.title = el.getAttribute('data-title') || 'YouTube video player';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.allowFullscreen = true;
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    iframe.setAttribute('frameborder', '0');
    iframe.style.cssText = el.style.cssText || 'position:absolute;inset:0;width:100%;height:100%;';
    iframe.style.border = '0';

    el.parentNode.replaceChild(iframe, el);
    iframe.focus();
    track(id, start);
  }

  document.addEventListener('pointerover', function (e) {
    if (e.target.closest && e.target.closest('.cd-yt')) warm();
  }, { passive: true });

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var el = e.target.closest && e.target.closest('.cd-yt');
    if (!el) return;
    e.preventDefault();
    play(el);
  });

  var css = document.createElement('style');
  css.textContent =
    '.cd-yt{cursor:pointer;background:#000;overflow:hidden}' +
    '.cd-yt img{transition:transform .35s ease,filter .35s ease}' +
    '.cd-yt:hover img,.cd-yt:focus-visible img{transform:scale(1.03);filter:brightness(.85)}' +
    '.cd-yt:hover .cd-yt-play path:first-child,.cd-yt:focus-visible .cd-yt-play path:first-child{fill:#f00;fill-opacity:1}' +
    '.cd-yt:focus-visible{outline:3px solid #c9a227;outline-offset:2px}' +
    '.cd-shorts{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 2px 10px;-webkit-overflow-scrolling:touch}' +
    '.cd-shorts>figure{flex:0 0 200px;margin:0;scroll-snap-align:start}' +
    '.cd-shorts figcaption{font-size:13px;line-height:1.35;margin-top:6px;color:inherit;opacity:.8}';
  document.head.appendChild(css);
})();
