
(function(){
  /* UI strings: English defaults; a language page overrides them with <script type="application/json" id="listicle-ui"> (written by listicle.py build-lang) */
  var UI=(function(){try{var e=document.getElementById('listicle-ui');return e?JSON.parse(e.textContent):{};}catch(x){return {};}})();
  function tr(k,d,o){var s=UI[k]!=null?UI[k]:d;return o?s.replace(/\{(\w+)\}/g,function(m,n){return o[n]!=null?o[n]:m;}):s;}
  /* Exact sunset and civil dusk (sun 6 degrees below the horizon) on any date, for the place the
     .fbm-mrow names: data-lat, data-lng, data-tz, data-lit-end ("22:00", or empty = no end time),
     data-lit-what (e.g. "the Eiffel Tower"). No attributes = Budapest, lights until the Parliament
     goes dark at 22:00. data-lit-what without data-lit-end = no end time. */
  var ROW=document.querySelector('.fbm-mrow');
  function at(n){return ROW&&ROW.hasAttribute(n)?ROW.getAttribute(n).trim():null;}
  function num(n,d){var v=parseFloat(at(n));return isFinite(v)?v:d;}
  var LAT=num('data-lat',47.4979), LNG=num('data-lng',19.0402), TZ=at('data-tz')||'Europe/Budapest';
  var WHAT=at('data-lit-what'), END=at('data-lit-end');
  if(END==null) END=WHAT==null?'22:00':'';
  if(END&&!/^\d{1,2}:\d{2}$/.test(END)) END='';
  /* the original Budapest strings (and their translations) unless the page names its own landmark or end time */
  var LEGACY=WHAT==null&&END==='22:00'; if(WHAT==null) WHAT='the Parliament';
  var R=Math.PI/180, DAY=864e5, J1970=2440588, J2000=2451545, OB=R*23.4397;
  function tj(d){return d.valueOf()/DAY-0.5+J1970;}
  function fj(j){return new Date((j+0.5-J1970)*DAY);}
  function sunAt(date,h){
    var lw=R*-LNG, phi=R*LAT, d=tj(date)-J2000, n=Math.round(d-0.0009-lw/(2*Math.PI));
    var ds=0.0009+lw/(2*Math.PI)+n, M=R*(357.5291+0.98560028*ds);
    var C=R*(1.9148*Math.sin(M)+0.02*Math.sin(2*M)+0.0003*Math.sin(3*M)), L=M+C+R*102.9372+Math.PI;
    var dec=Math.asin(Math.sin(OB)*Math.sin(L));
    var w=Math.acos((Math.sin(h*R)-Math.sin(phi)*Math.sin(dec))/(Math.cos(phi)*Math.cos(dec)));
    var a=0.0009+(w+lw)/(2*Math.PI)+n;
    return fj(J2000+a+0.0053*Math.sin(M)-0.0069*Math.sin(2*L));
  }
  var LOC=tr('locale','en-GB');
  var FMT=new Intl.DateTimeFormat(LOC,{timeZone:TZ,hour:'2-digit',minute:'2-digit',hour12:false});
  var DFMT=new Intl.DateTimeFormat(LOC,{timeZone:TZ,day:'numeric',month:'short'});
  function loc(d){return FMT.format(d);}
  function m(t){var p=t.split(':');return +p[0]*60+(+p[1]);}
  function hm(x){return ('0'+Math.floor(x/60)).slice(-2)+':'+('0'+(x%60)).slice(-2);}
  function span(t,c){return '<span class="t '+c+'">'+t+'</span>';}
  function md(iso){return iso.slice(5);}
  function inSeason(r,k){ if(!r.from) return true; return r.from<=r.to ? (k>=r.from&&k<=r.to) : (k>=r.from||k<=r.to); }
  function render(iso){
    var noon=new Date(iso+'T11:00:00Z');
    var SUN=loc(sunAt(noon,-0.833)), DARK=loc(sunAt(noon,-6)), sun=m(SUN), dark=m(DARK), name=DFMT.format(noon), key=md(iso);
    var note=document.getElementById('fbm-mnote');
    var nv={sun:SUN,board:hm(sun-20),dark:DARK,date:name,end:END};
    if(note) note.textContent=LEGACY?tr('sun_note','🌇 Sunset {sun}: board about 20 min before ({board}) to catch it  ·  🌃 City lit up {dark} to 22:00 ({date})',nv)
      :END?tr('sun_note_end','🌇 Sunset {sun}: board about 20 min before ({board}) to catch it  ·  🌃 City lit up {dark} to {end} ({date})',nv)
      :tr('sun_note_open','🌇 Sunset {sun}: board about 20 min before ({board}) to catch it  ·  🌃 City lit up from {dark} ({date})',nv);
    document.querySelectorAll('.fbm-slot').forEach(function(el){
      var tt=JSON.parse(el.getAttribute('data-tt')||'[]'), dur=+el.getAttribute('data-dur');
      var row=null; tt.forEach(function(r){ if(!row && r.from && inSeason(r,key)) row=r; });
      if(!row){ el.innerHTML=tr('slot_closed','📅 <b>{date}:</b> this date is not open for booking yet, so its sailing times are not out. It is fully dark from {dark}: pick a sailing after that when you book.',{date:name,dark:DARK}); el.classList.add('is-none'); return; }
      var times=row.times, lit=[],dusk=[];
      times.forEach(function(t){var a=m(t),b=a+dur; if(a>=dark-10) lit.push(t); else if(b>=dark+10&&a>=sun-45) dusk.push(t);});
      el.classList.toggle('is-none',!lit.length&&!dusk.length);
      var h;
      if(dur>=120&&times.length===1){
        var a=m(times[0]),b=a+dur,left=b-Math.max(a,dark);
        var dl=left>=60?(left%60?tr('dur_hm','{h} h {m} min',{h:Math.floor(left/60),m:left%60}):tr('dur_h','{h} h',{h:Math.floor(left/60)})):tr('dur_m','{m} min',{m:left});
        h=left>=15?tr('dinner_lit','🌙 <b>{date}:</b> dark from {dark}, so the last {left} of dinner ({start} to {end}) is under the lights.',{date:name,dark:DARK,left:dl,start:times[0],end:hm(b)})
                :(b>sun?tr('dinner_sunset','🌇 <b>{date}:</b> sunset ({sun}) happens during dinner; it is fully dark only after you dock ({dark}).',{date:name,sun:SUN,dark:DARK})
                  :tr('dinner_day','☀️ <b>{date}:</b> the cruise ends before sunset ({sun}).',{date:name,sun:SUN}));
      } else if(!lit.length&&!dusk.length){
        h=tr('slot_day','☀️ <b>{date}:</b> the last sailing ({last}) ends before full dark ({dark}).',{date:name,last:times[times.length-1],dark:DARK});
      } else {
        var OFF=END?m(END):Infinity, lv={date:name,dark:DARK,end:END,what:WHAT}, inLit=lit.filter(function(t){return m(t)<OFF;}), late=lit.length-inLit.length;
        var ev=inLit.length>3&&inLit.every(function(t,k){return !k||m(t)-m(inLit[k-1])===m(inLit[1])-m(inLit[0]);}), step=inLit.length>1?m(inLit[1])-m(inLit[0]):0;
        h=(LEGACY?tr('lit_head','🌃 <b>City lit up on {date}: {dark} to 22:00</b>',lv):END?tr('lit_head_end','🌃 <b>City lit up on {date}: {dark} to {end}</b>',lv):tr('lit_head_open','🌃 <b>City lit up on {date}: from {dark}</b>',lv))
          +' <span class="fbm-why" title="'+(LEGACY?tr('lit_why','Lights are on from dusk, about 30 minutes after sunset, until the Parliament switches its floodlights off at 22:00.')
            :END?tr('lit_why_end','Lights are on from dusk, about 30 minutes after sunset, until {what} goes dark at {end}.',lv)
            :tr('lit_why_open','Lights are on from dusk, about 30 minutes after sunset, when the city and {what} light up.',lv))+'">ⓘ</span>';
        h+=inLit.length?'<br><span class="fbm-sub">'+tr('lit_board','Board for the lights:')+' '+(ev?tr('lit_every','{first} then every {step} min to {last}',{first:span(inLit[0],'lit'),step:step,last:span(inLit[inLit.length-1],'lit')}):inLit.map(function(t){return span(t,'lit');}).join(''))+(late?' '+(LEGACY?tr('lit_late','(later sailings: city lit, Parliament dark)'):tr('lit_late_end','(later sailings: city lit, {what} dark)',lv)):'')+'</span>'
                       :'<br><span class="fbm-sub">'+(late?(LEGACY?tr('lit_after22','Its sailings start after 22:00: the city is lit, the Parliament is dark.'):tr('lit_after_end','Its sailings start after {end}: the city is lit, {what} is dark.',lv)):tr('lit_none','No sailing starts after dark on this date.'))+'</span>';
      }
      el.innerHTML=h;
    });
  }
  var inp=document.getElementById('fbm-date'); if(!inp) return;
  var t=new Date(), iso=t.getFullYear()+'-'+('0'+(t.getMonth()+1)).slice(-2)+'-'+('0'+t.getDate()).slice(-2);
  inp.value=iso; inp.min=iso; render(iso);
  inp.addEventListener('change',function(){ if(inp.value) render(inp.value); });
})();
