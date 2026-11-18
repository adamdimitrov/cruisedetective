
(function(){
  /* UI strings: English defaults; a language page overrides them with <script type="application/json" id="listicle-ui"> (written by listicle.py build-lang) */
  var UI=(function(){try{var e=document.getElementById('listicle-ui');return e?JSON.parse(e.textContent):{};}catch(x){return {};}})();
  function tr(k,d,o){var s=UI[k]!=null?UI[k]:d;return o?s.replace(/\{(\w+)\}/g,function(m,n){return o[n]!=null?o[n]:m;}):s;}
  var inp=document.getElementById('fbm-date'); if(!inp) return;
  var chips=Array.prototype.slice.call(document.querySelectorAll('.fbm-day'));
  function iso(d){ return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2); }
  function dayFor(k){ var d=new Date(); if(k==='sat'){ var add=(6-d.getDay()+7)%7; d.setDate(d.getDate()+(add===0?7:add)); } else { d.setDate(d.getDate()+(+k)); } return iso(d); }
  function mark(v){
    var hit=false;
    chips.forEach(function(c){ var k=c.getAttribute('data-day'); var on=k!==null && dayFor(k)===v && !hit; if(on) hit=true; c.classList.toggle('is-on',on); if(k!==null) c.setAttribute('aria-pressed',on?'true':'false'); });
    var other=document.querySelector('.fbm-other'); if(other){ other.classList.toggle('is-on',!hit); var sp=other.querySelector('span'); if(sp) sp.textContent=hit?tr('other_date','Other date'):new Date(v+'T12:00:00').toLocaleDateString(tr('locale','en-GB'),{day:'numeric',month:'short'}); }
  }
  chips.forEach(function(c){ var k=c.getAttribute('data-day'); if(k===null) return;
    c.addEventListener('click',function(){ inp.value=dayFor(k); inp.dispatchEvent(new Event('change',{bubbles:true})); mark(inp.value); }); });
  inp.addEventListener('change',function(){ if(inp.value) mark(inp.value); });
  var other=document.querySelector('.fbm-other'); if(other) other.addEventListener('click',function(){ try{ inp.showPicker(); }catch(e){} });
  var DF=new Intl.DateTimeFormat(tr('locale','en-GB'),{day:'numeric',month:'short'});
  chips.forEach(function(c){ var k=c.getAttribute('data-day'); if(k===null) return; c.textContent=c.textContent.split(' \u00b7 ')[0]+' \u00b7 '+DF.format(new Date(dayFor(k)+'T12:00:00')); });
  mark(inp.value||dayFor(0));
})();
