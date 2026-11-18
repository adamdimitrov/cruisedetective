
(function(){
  var box=document.getElementById('cd-filters'); if(!box) return;
  var btn=box.querySelector('.cd-fmore'), rows=[].slice.call(box.querySelectorAll('.cd-frow-more'));
  function hiddenCount(){ return rows.filter(function(r){ return !r.classList.contains('has-on'); }).reduce(function(n,r){ return n+r.querySelectorAll('.ltt-tab-btn').length; },0); }
  function sync(){
    rows.forEach(function(r){ r.classList.toggle('has-on', !!r.querySelector('.ltt-tab-btn[aria-pressed="true"]')); });
    var n=hiddenCount(), open=!box.classList.contains('is-collapsed');
    btn.hidden=n===0; btn.setAttribute('aria-expanded', open?'true':'false');
    btn.firstChild.nodeValue=open?'Fewer filters ':'More filters ';
    btn.querySelector('.cd-fmore-n').textContent=open?'':'('+n+')';
  }
  box.classList.add('is-collapsed');
  btn.addEventListener('click',function(){ box.classList.toggle('is-collapsed'); sync(); });
  box.addEventListener('click',function(e){ if(e.target.closest('.ltt-tab-btn, .cd-fclear, .cd-fchip')) setTimeout(sync,40); });
  sync();
})();
