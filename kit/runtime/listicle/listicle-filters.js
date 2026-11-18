
(function(){
  /* Multi-select filters, Baymard-based: combinable values, live counts, no 0-result options,
     an applied-filters overview, and a sticky filter shortcut on phones. */
  var active = [];
  function catsOf(el){ return (el.getAttribute('data-cat')||'').split(/\s+/); }
  function matches(el, list){ var c=catsOf(el); return list.every(function(x){ return c.indexOf(x)!==-1; }); }
  function labelOf(b){ var t=b.cloneNode(true); var n=t.querySelector('.cd-n'); if(n) n.remove(); return t.textContent.trim(); }
  function apply(){
    var cards=[].slice.call(document.querySelectorAll('#ltt-cards-deck .bpa-card'));
    var dets=[].slice.call(document.querySelectorAll('details.bpa-details-card'));
    var shown=0;
    cards.forEach(function(card){ var s=matches(card,active); card.style.display=s?'block':'none'; if(s) shown++; });
    dets.forEach(function(d){
      var s=matches(d,active); d.style.display=s?'block':'none';
      if(d.id) document.querySelectorAll('#toc a[href="#'+d.id+'"], #hybridSheetList a[href="#'+d.id+'"]').forEach(function(lk){ lk.classList.toggle('is-filtered',!s); });
    });
    var applied=[];
    document.querySelectorAll('.cd-fbox .ltt-tab-btn').forEach(function(b){
      var c=b.getAttribute('data-cat'), on=active.indexOf(c)!==-1;
      b.classList.toggle('active',on); b.setAttribute('aria-pressed',on?'true':'false');
      var n=cards.filter(function(card){ return matches(card, on?active:active.concat([c])); }).length;
      var cn=b.querySelector('.cd-n'); if(cn) cn.textContent='('+n+')';
      var dead=!on && n===0; b.disabled=dead; b.classList.toggle('is-empty',dead);
      if(on) applied.push('<button type="button" class="cd-fchip" onclick="lttFilterSafaris(\''+c+'\')" aria-label="Remove filter '+labelOf(b)+'">'+labelOf(b)+' <span aria-hidden="true">×</span></button>');
    });
    var box=document.querySelector('.cd-fbox');
    if(box){
      box.querySelector('.cd-fcount').innerHTML='Showing <b>'+shown+'</b> of '+cards.length+' cruises';
      box.querySelector('.cd-fapplied').innerHTML=applied.join('');
      box.querySelector('.cd-fclear').hidden=!active.length;
    }
    var mn=document.querySelector('.cd-fmini-n'); if(mn){ mn.hidden=!active.length; mn.textContent=active.length; }
    var mr=document.querySelector('.cd-fmini-res'); if(mr) mr.innerHTML='<b>'+shown+'</b> of '+cards.length+' cruises';
    var sub=document.querySelector('.bpa-breakdown-sub');
    if(sub){
      if(sub._def==null) sub._def=sub.textContent;
      sub.textContent = active.length ? ('Showing '+shown+' of '+cards.length+' cruises matching your filters') : sub._def;
    }
  }
  window.lttFilterItems = window.lttFilterSafaris = window.lttFilterCruises = function(cat){
    if(!cat || cat==='all'){ active=[]; }
    else { var i=active.indexOf(cat); if(i===-1) active.push(cat); else active.splice(i,1); }
    apply();
  };
  window.cdFiltersJump = function(){
    var box=document.getElementById('cd-filters'); if(!box) return;
    var y=box.getBoundingClientRect().top+window.scrollY-(parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--cd-hdr'))||64)-8;
    window.scrollTo({top:y,behavior:'smooth'});
  };
  // header height for the sticky mini-bar
  function hdr(){
    var el=document.elementFromPoint(window.innerWidth/2,4), h=0;
    while(el && el!==document.body){ var p=getComputedStyle(el).position; if(p==='fixed'||p==='sticky'){ h=el.getBoundingClientRect().bottom; break; } el=el.parentElement; }
    document.documentElement.style.setProperty('--cd-hdr',(h>0&&h<160?h:64)+'px');
  }
  hdr(); window.addEventListener('resize',hdr);
  // show the mini-bar only once the filter box has scrolled away and while the deck is on screen
  var box=document.getElementById('cd-filters'), mini=document.querySelector('.cd-fmini');
  var deck=document.getElementById('ltt-cards-deck'), ticking=false;
  function upd(){
    ticking=false; if(!box||!mini||!deck) return;
    var top=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--cd-hdr'))||64;
    var bb=box.getBoundingClientRect(), db=deck.getBoundingClientRect();
    var on = bb.bottom < top && db.bottom > top + 160;
    if(mini.classList.contains('is-on')!==on){ mini.classList.toggle('is-on',on); mini.setAttribute('aria-hidden',on?'false':'true'); }
  }
  window.addEventListener('scroll',function(){ if(!ticking){ ticking=true; requestAnimationFrame(upd); } },{passive:true});
  window.addEventListener('resize',upd);
  upd();
  apply();
})();
