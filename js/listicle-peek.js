
/* Show that pills open: when the #1 card scrolls into view, its first pill opens for 1.5 s and closes. Once per load; skipped if the visitor already opened a pill. */
(function(){
  function run(){
    var card=document.getElementById('card-1'), sm=card&&card.querySelector('.bpa-specs-row .bpa-lang>summary'); if(!sm||!('IntersectionObserver' in window)) return;
    var touched=false; document.addEventListener('click',function(e){ if(e.isTrusted&&e.target.closest('.bpa-lang')) touched=true; },true);
    var io=new IntersectionObserver(function(es){ if(!es[0].isIntersecting) return; io.disconnect();
      setTimeout(function(){ if(touched) return; sm.click(); setTimeout(function(){ if(sm.parentNode.classList.contains('is-open')||sm.parentNode.open) sm.click(); },1500); },600); },{threshold:.6});
    io.observe(card);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',run); else run();
})();
