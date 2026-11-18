
(function(){
  /* Exact sunset and civil dusk (sun 6 degrees below the horizon) for Budapest on any date. */
  var LAT=47.4979, LNG=19.0402, R=Math.PI/180, DAY=864e5, J1970=2440588, J2000=2451545, OB=R*23.4397;
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
  var FMT=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Budapest',hour:'2-digit',minute:'2-digit',hour12:false});
  var DFMT=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Budapest',day:'numeric',month:'short'});
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
    if(note) note.textContent='🌇 Sunset '+SUN+': board about 20 min before ('+hm(sun-20)+') to catch it  ·  🌃 City lit up '+DARK+' to 22:00 ('+name+')';
    document.querySelectorAll('.fbm-slot').forEach(function(el){
      var tt=JSON.parse(el.getAttribute('data-tt')||'[]'), dur=+el.getAttribute('data-dur');
      var row=null; tt.forEach(function(r){ if(!row && r.from && inSeason(r,key)) row=r; });
      if(!row){ el.innerHTML='📅 <b>'+name+':</b> this date is not open for booking yet, so its sailing times are not out. It is fully dark from '+DARK+': pick a sailing after that when you book.'; el.classList.add('is-none'); return; }
      var times=row.times, lit=[],dusk=[];
      times.forEach(function(t){var a=m(t),b=a+dur; if(a>=dark-10) lit.push(t); else if(b>=dark+10&&a>=sun-45) dusk.push(t);});
      el.classList.toggle('is-none',!lit.length&&!dusk.length);
      var h;
      if(dur>=120&&times.length===1){
        var a=m(times[0]),b=a+dur,left=b-Math.max(a,dark);
        h=left>=15?('🌙 <b>'+name+':</b> dark from '+DARK+', so the last '+(left>=60?Math.floor(left/60)+' h'+(left%60?' '+left%60+' min':''):left+' min')+' of dinner ('+times[0]+' to '+hm(b)+') is under the lights.')
                :(b>sun?('🌇 <b>'+name+':</b> sunset ('+SUN+') happens during dinner; it is fully dark only after you dock ('+DARK+').')
                  :('☀️ <b>'+name+':</b> the cruise ends before sunset ('+SUN+').'));
      } else if(!lit.length&&!dusk.length){
        h='☀️ <b>'+name+':</b> the last sailing ('+times[times.length-1]+') ends before full dark ('+DARK+').';
      } else {
        var OFF=22*60, inLit=lit.filter(function(t){return m(t)<OFF;}), late=lit.length-inLit.length;
        var ev=inLit.length>3&&inLit.every(function(t,k){return !k||m(t)-m(inLit[k-1])===m(inLit[1])-m(inLit[0]);}), step=inLit.length>1?m(inLit[1])-m(inLit[0]):0;
        h='🌃 <b>City lit up on '+name+': '+DARK+' to 22:00</b> <span class="fbm-why" title="Lights are on from dusk, about 30 minutes after sunset, until the Parliament switches its floodlights off at 22:00.">ⓘ</span>';
        h+=inLit.length?'<br><span class="fbm-sub">Board for the lights: '+(ev?span(inLit[0],'lit')+' then every '+step+' min to '+span(inLit[inLit.length-1],'lit'):inLit.map(function(t){return span(t,'lit');}).join(''))+(late?' (later sailings: city lit, Parliament dark)':'')+'</span>'
                       :'<br><span class="fbm-sub">'+(late?'Its sailings start after 22:00: the city is lit, the Parliament is dark.':'No sailing starts after dark on this date.')+'</span>';
      }
      el.innerHTML=h;
    });
  }
  var inp=document.getElementById('fbm-date'); if(!inp) return;
  var t=new Date(), iso=t.getFullYear()+'-'+('0'+(t.getMonth()+1)).slice(-2)+'-'+('0'+t.getDate()).slice(-2);
  inp.value=iso; inp.min=iso; render(iso);
  inp.addEventListener('change',function(){ if(inp.value) render(inp.value); });
})();
