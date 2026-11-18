
(function(){
  function stepW(sl){var f=sl.firstElementChild;return (f?f.getBoundingClientRect().width+(parseFloat(getComputedStyle(sl).columnGap)||0):sl.clientWidth)||1;}
  function loadAll(sl){sl.querySelectorAll('img[data-src]').forEach(function(im){if(im.getAttribute('data-srcset')){im.srcset=im.getAttribute('data-srcset');im.removeAttribute('data-srcset');}im.src=im.getAttribute('data-src');im.removeAttribute('data-src');});}
  document.querySelectorAll('.cd-gal').forEach(function(gal){
    var slider=gal.querySelector('.bpa-slider'), strip=gal.querySelector('.cd-thumbs');
    if(!slider||!strip) return;
    var thumbs=strip.querySelectorAll('.cd-thumb');
    strip.addEventListener('click',function(e){
      var b=e.target.closest('.cd-thumb'); if(!b) return;
      if(b.hasAttribute('data-more') && !strip.classList.contains('is-open')){
        strip.classList.add('is-open');
        strip.querySelectorAll('.is-hid').forEach(function(x){x.classList.remove('is-hid');});
      }
      loadAll(slider);
      slider.scrollTo({left:(+b.getAttribute('data-i'))*stepW(slider),behavior:'smooth'});
    });
    // load the next photos before they are swiped into view, so nobody watches them load
    function preload(i,n){var kids=slider.children;for(var k=Math.max(0,i);k<Math.min(kids.length,i+(n||3)+1);k++){var im=kids[k].tagName==='IMG'?kids[k]:kids[k].querySelector('img[data-src]');if(im&&im.getAttribute('data-src')){if(im.getAttribute('data-srcset')){im.srcset=im.getAttribute('data-srcset');im.removeAttribute('data-srcset');}im.src=im.getAttribute('data-src');im.removeAttribute('data-src');}}}
    if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){if(es[0].isIntersecting){io.disconnect();preload(0,2);}},{rootMargin:'400px'});io.observe(gal);}else preload(0,2);
    ['pointerenter','touchstart','focusin'].forEach(function(ev){gal.addEventListener(ev,function(){preload(Math.round(slider.scrollLeft/stepW(slider)),4);},{passive:true,once:true});});
    slider.addEventListener('scroll',function(){
      var i=Math.round(slider.scrollLeft/stepW(slider));
      preload(i,3);
      // thumbnails follow the swipe: match by photo index, open the full strip once past the visible ones
      var on=null;
      strip.querySelectorAll('.cd-thumb[data-i]').forEach(function(x){var k=+x.getAttribute('data-i');x.classList.toggle('is-on',k===i);if(k===i)on=x;});
      if(on&&on.classList.contains('is-hid')&&!strip.classList.contains('is-open')){strip.classList.add('is-open');strip.querySelectorAll('.is-hid').forEach(function(x){x.classList.remove('is-hid');});}
      if(on&&strip.classList.contains('is-open')) strip.scrollTo({left:on.offsetLeft-strip.clientWidth/2+on.clientWidth/2,behavior:'smooth'});
    },{passive:true});
  });
  document.addEventListener('click',function(e){
    document.querySelectorAll('.cd-pdd[open]').forEach(function(d){if(!d.contains(e.target)) d.open=false;});
  });
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape') document.querySelectorAll('.cd-pdd[open]').forEach(function(d){d.open=false;});
  });
})();
