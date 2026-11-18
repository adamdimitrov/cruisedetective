
(function(){
  /* UI strings: English defaults; a language page overrides them with <script type="application/json" id="listicle-ui"> (written by listicle.py build-lang) */
  var UI=(function(){try{var e=document.getElementById('listicle-ui');return e?JSON.parse(e.textContent):{};}catch(x){return {};}})();
  function tr(k,d,o){var s=UI[k]!=null?UI[k]:d;return o?s.replace(/\{(\w+)\}/g,function(m,n){return o[n]!=null?o[n]:m;}):s;}
  var box=document.getElementById('cd-filters'); if(!box) return;
  var btn=box.querySelector('.cd-fmore'), rows=[].slice.call(box.querySelectorAll('.cd-frow-more'));
  function hiddenCount(){ return rows.filter(function(r){ return !r.classList.contains('has-on'); }).reduce(function(n,r){ return n+r.querySelectorAll('.ltt-tab-btn').length; },0); }
  function sync(){
    rows.forEach(function(r){ r.classList.toggle('has-on', !!r.querySelector('.ltt-tab-btn[aria-pressed="true"]')); });
    var n=hiddenCount(), open=!box.classList.contains('is-collapsed');
    btn.hidden=n===0; btn.setAttribute('aria-expanded', open?'true':'false');
    btn.firstChild.nodeValue=open?tr('fewer_filters','Fewer filters')+' ':tr('more_filters','More filters')+' ';
    btn.querySelector('.cd-fmore-n').textContent=open?'':'('+n+')';
  }
  box.classList.add('is-collapsed');
  btn.addEventListener('click',function(){ box.classList.toggle('is-collapsed'); sync(); });
  box.addEventListener('click',function(e){ if(e.target.closest('.ltt-tab-btn, .cd-fclear, .cd-fchip')) setTimeout(sync,40); });
  sync();
})();
