
(function(){
  var N={en:'English',fr:'French',es:'Spanish',de:'German',it:'Italian',pt:'Portuguese',nl:'Dutch',pl:'Polish',ru:'Russian',ar:'Arabic',hi:'Hindi',zh:'Chinese',ja:'Japanese',ko:'Korean'};
  function init(){
    var langs=[];
    try{langs=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'']);}catch(e){}
    var code=String(langs[0]||'').slice(0,2).toLowerCase();
    var boxes=document.querySelectorAll('.bpa-lang');
    if(!boxes.length) return;
    document.documentElement.classList.add('bpa-lang-on');

    var pop=document.createElement('div');
    pop.id='bpa-lang-float';
    pop.setAttribute('role','tooltip');
    document.body.appendChild(pop);
    var current=null, pinned=false, hideTimer=null;
    var canHover=window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    function place(d){
      var s=d.querySelector('summary').getBoundingClientRect();
      var vw=document.documentElement.clientWidth, vh=window.innerHeight;
      var w=Math.min(290, vw-16);
      pop.style.width=w+'px';
      var left=Math.max(8, Math.min(s.left, vw-w-8));
      var h=pop.offsetHeight;
      var above=(s.bottom+10+h>vh) && (s.top-10-h>0);
      var top=above ? (s.top-10-h) : (s.bottom+10);
      pop.classList.toggle('is-above', above);
      pop.style.left=(left+window.scrollX)+'px';
      pop.style.top=(top+window.scrollY)+'px';
      pop.style.setProperty('--ax', Math.max(14, Math.min(w-14, s.left+Math.min(s.width,40)/2-left))+'px');
    }
    function show(d, pin){
      clearTimeout(hideTimer);
      if(current && current!==d) current.classList.remove('is-open');
      current=d; pinned=!!pin;
      pop.innerHTML=d.querySelector('.bpa-lang-pop').innerHTML;
      d.classList.add('is-open');
      d.querySelector('summary').setAttribute('aria-expanded','true');
      place(d);
      pop.classList.add('is-visible');
    }
    function hide(){
      clearTimeout(hideTimer);
      if(current){ current.classList.remove('is-open'); current.querySelector('summary').setAttribute('aria-expanded','false'); }
      current=null; pinned=false;
      pop.classList.remove('is-visible');
    }
    function softHide(e){
      if(pinned) return;
      var to=e && e.relatedTarget;
      if(to && to.closest && (to.closest('#bpa-lang-float') || (current && current.contains(to)))) return;
      hide();
    }

    boxes.forEach(function(d){
      var sum=d.querySelector('summary');
      sum.setAttribute('aria-expanded','false');
      sum.addEventListener('click',function(e){
        e.preventDefault();
        if(current===d && pinned){ hide(); return; }
        show(d,true);
      });
      if(canHover){
        sum.addEventListener('mouseenter',function(){ if(!pinned||current!==d) show(d,false); });
        sum.addEventListener('mouseleave',softHide);
      }
      if(!code||code==='en'||!N[code]) return;
      var list=(d.getAttribute('data-langs')||'').split(',');
      if(list.indexOf(code)===-1) return;
      var label=d.querySelector('.bpa-lang-label');
      if(label) label.textContent='Audio in '+N[code]+' \u2713';
      d.classList.add('is-match');
      var names=d.querySelector('.bpa-lang-names');
      if(names) names.innerHTML=names.textContent.split(', ').map(function(n){return n===N[code]?'<b>'+n+'</b>':n;}).join(', ');
    });
    pop.addEventListener('mouseenter',function(){ clearTimeout(hideTimer); });
    pop.addEventListener('mouseleave',softHide);
    document.addEventListener('click',function(e){
      if(!current) return;
      if(e.target.closest && (e.target.closest('.bpa-lang') || e.target.closest('#bpa-lang-float'))) return;
      hide();
    });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') hide(); });
    window.addEventListener('resize',function(){ if(current) place(current); });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
