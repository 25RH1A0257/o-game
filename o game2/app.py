"""
ZERO HOUR - Streamlit edition
Run:  pip install streamlit pillow
      streamlit run app.py
"""
import base64
import io
import json

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="ZERO HOUR", page_icon="🔦", layout="wide")

SLOTS = [("title", "Title screen"), ("street", "Hub street"), ("metro", "Abandoned Metro"),
         ("tower", "North Tower"), ("police", "Old Police Station"),
         ("obs", "City Observatory"), ("grid", "Central Grid Station")]


def img_uri(f, maxw=1280):
    data, mime = f.getvalue(), f.type or "image/jpeg"
    try:  # shrink big photos so the page stays fast
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((maxw, maxw))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=80)
        data, mime = b.getvalue(), "image/jpeg"
    except Exception:
        pass
    return f"data:{mime};base64," + base64.b64encode(data).decode()


with st.sidebar:
    st.header("🔦 ZERO HOUR")
    vol = st.slider("Music volume", 0, 100, 60)
    height = st.slider("Game height (px)", 520, 950, 740, 10)
    with st.expander("🎵 Your own music (optional)"):
        mf = st.file_uploader("Upload mp3 / wav / ogg", type=["mp3", "wav", "ogg"])
        murl = st.text_input("...or paste a direct audio link")
    with st.expander("🖼️ Background photos (optional)"):
        st.caption("Upload a photo (or paste a link) for any area. Empty = built-in painted scenes.")
        bg = {}
        for key, label in SLOTS:
            up = st.file_uploader(label, type=["jpg", "jpeg", "png", "webp"], key="u_" + key)
            url = st.text_input(label + " link", key="l_" + key, label_visibility="collapsed",
                                placeholder=label + " image link")
            if up:
                bg[key] = img_uri(up)
            elif url.strip():
                bg[key] = url.strip()

music = None
if mf:
    music = f"data:{mf.type or 'audio/mpeg'};base64," + base64.b64encode(mf.getvalue()).decode()
elif murl.strip():
    music = murl.strip()

cfg = json.dumps({"bg": bg, "music": music, "vol": vol / 100}).replace("</", "<\\/")

GAME = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZERO HOUR</title>
<link href="https://fonts.googleapis.com/css2?family=Creepster&family=Special+Elite&display=swap" rel="stylesheet">
<style>
:root{--bg:#07060d;--fg:#f6f2ff;--ac:#ff8a3d;--red:#ff4f8b;--pan:rgba(22,6,26,.95);color-scheme:dark}
html,body{height:100%;margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 "Special Elite","Courier New",monospace;overflow:hidden;user-select:none}
canvas{position:fixed;inset:0;width:100%;height:100%}#sc{z-index:50;pointer-events:none}
#hud{position:fixed;left:12px;right:12px;top:8px;display:flex;justify-content:space-between;align-items:flex-start;pointer-events:none;text-shadow:0 2px 4px #000}
#clock{font:2.2rem Creepster,Impact,fantasy;color:var(--red);letter-spacing:.06em}.bar{width:120px;height:7px;background:#1a1530;border-radius:4px;overflow:hidden;margin-top:3px}.bar i{display:block;height:100%}
#pf span{display:inline-block;padding:2px 7px;margin:0 3px;border:1px solid #463c64;border-radius:6px;color:#6e6490;font-size:.8rem}#pf .on{color:#ffd23f;border-color:#ffd23f;background:#3c2d0a}
#loc{color:#c0b9e6;font-size:.8rem}#pr{position:fixed;left:50%;transform:translateX(-50%);bottom:30px;color:#ffd23f;font-size:1.1rem;text-shadow:0 2px 6px #000;pointer-events:none;white-space:nowrap}
#msg{position:fixed;left:50%;transform:translateX(-50%);bottom:72px;width:min(560px,92vw);background:var(--pan);border:1px solid var(--ac);border-left:5px solid var(--ac);border-radius:6px;padding:8px 12px;display:none;pointer-events:none}
.ov{position:fixed;inset:0;z-index:10;background:rgba(3,3,12,.7);display:none;align-items:center;justify-content:center;padding:12px;overflow:auto}
.p{background:var(--pan);border:1px solid var(--ac);box-shadow:0 0 30px -8px var(--ac);border-radius:12px;padding:18px;max-width:540px;text-align:center}
h1,h2{font:400 3.4rem/1 Creepster,Impact,fantasy;letter-spacing:.08em;margin:0 0 8px;text-shadow:0 0 18px var(--ac)}h2{font-size:2.2rem}p{margin:8px 0;text-align:left}.m{color:#c0b9e6;font-size:.85rem}
button,input{font:inherit;color:var(--fg);background:linear-gradient(135deg,#4a1633,#25124d);border:1px solid var(--ac);border-radius:10px;padding:9px 14px;cursor:pointer}
button:hover{box-shadow:0 0 14px var(--ac)}button.w{width:100%;margin-top:8px}button.sel{background:#7a3a10}input{width:100%;text-align:center;font-size:1.6rem;letter-spacing:.3em;cursor:text;box-sizing:border-box}
#mb{pointer-events:auto;margin-top:4px;padding:3px 9px;font-size:.8rem}
#tb{position:fixed;right:14px;bottom:16px;display:none;gap:10px;z-index:5}#tb button{width:60px;height:60px;border-radius:50%;padding:0;font-size:1.2rem}
</style></head><body>
<canvas id="c"></canvas><canvas id="sc"></canvas>
<div id="hud"><div><div id="clock">90:00</div><div class="bar"><i id="bt" style="background:#ff8a3d;width:100%"></i></div><div class="bar"><i id="sm" style="background:#6dffb0;width:100%"></i></div><div id="loc"></div></div><div id="pf"></div><div class="m" style="text-align:right">F light · G flare · Shift run · M music<br><button id="mb" onclick="toggleMute()">♪ Music ON</button></div></div>
<div id="msg"></div><div id="pr"></div><div id="tb"><button id="bR">RUN</button><button id="bL">💡</button><button id="bG">🔥</button><button id="bA">E</button></div>
<div id="ov" class="ov"></div>
<script>
const CFG=__CONFIG__;
const $=s=>document.querySelector(s),cv=$('#c'),cx=cv.getContext('2d'),sc=$('#sc'),sx=sc.getContext('2d'),dk=document.createElement('canvas'),dx=dk.getContext('2d');
let VW,VH,Z=1;function rs(){VW=cv.width=sc.width=dk.width=innerWidth;VH=cv.height=sc.height=dk.height=innerHeight;Z=VW<700?.8:1}addEventListener('resize',rs);rs();
const WW=1800,WH=1100,T=16,DR=110,HALF=.52,CONE=380,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const RM=[['ABANDONED METRO',0,0,600,400,'metro','b'],['NORTH TOWER',600,0,600,400,'tower','b'],['OLD POLICE STATION',1200,0,600,400,'police','b'],['CITY OBSERVATORY',0,700,900,400,'obs','t'],['CENTRAL GRID STATION',900,700,900,400,'grid','t']];
const walls=[[0,400,T,300],[WW-T,400,T,300]];
RM.forEach(([n,x,y,w,h,k,d])=>{const a=x+w/2-DR/2;walls.push([x,y,T,h],[x+w-T,y,T,h]);d=='b'?walls.push([x,y,w,T],[x,y+h-T,a-x,T],[a+DR,y+h-T,x+w-a-DR,T]):walls.push([x,y+h-T,w,T],[x,y,a-x,T],[a+DR,y,x+w-a-DR,T])});
const blocked=(x,y,r=11)=>walls.some(([a,b,w,h])=>x+r>a&&x-r<a+w&&y+r>b&&y-r<b+h);
/* ---------- permanent lights (candles, street lamps, neon) ---------- */
const LC={w:'255,190,110',b:'110,150,255',r:'255,70,60',g:'110,255,170'};
const LAMPS=[];for(let x=150;x<WW;x+=360)LAMPS.push([x+3,430,230,'w']);
LAMPS.push([300,640,170,'g'],[1000,640,170,'r'],[1600,640,170,'b'],
 [60,60,190,'w'],[520,330,190,'w'],[300,200,150,'b'],
 [700,60,190,'w'],[1130,340,190,'w'],[900,200,170,'w'],
 [1260,60,190,'w'],[1740,340,190,'w'],[1480,150,150,'b'],
 [60,780,190,'b'],[840,1040,190,'b'],[450,900,260,'b'],
 [960,780,190,'r'],[1740,1040,190,'r'],[1330,820,200,'r']);
/* ---------- painted backgrounds (+ optional photos) ---------- */
const PH={};for(const k in CFG.bg){const im=new Image();im.onload=()=>{PH[k]=im;paintBG()};im.src=CFG.bg[k]}
const bg=document.createElement('canvas');bg.width=WW;bg.height=WH;
function cover(g,im,x,y,w,h,a){const s=Math.max(w/im.width,h/im.height),iw=w/s,ih=h/s;g.save();g.beginPath();g.rect(x,y,w,h);g.clip();g.globalAlpha=a;g.drawImage(im,(im.width-iw)/2,(im.height-ih)/2,iw,ih,x,y,w,h);g.restore()}
function paintBG(){const g=bg.getContext('2d');let s=7;const r=()=>(s=s*16807%2147483647)/2147483647;
 const speck=(x,y,w,h,n,c)=>{g.fillStyle=c;for(let i=0;i<n;i++)g.fillRect(x+r()*w,y+r()*h,1+r()*2,1+r()*2)};
 const stain=(x,y,rad,c)=>{const q=g.createRadialGradient(x,y,0,x,y,rad);q.addColorStop(0,c);q.addColorStop(1,'transparent');g.fillStyle=q;g.fillRect(x-rad,y-rad,rad*2,rad*2)};
 const crack=(x,y)=>{g.strokeStyle='rgba(0,0,0,.55)';g.lineWidth=1.5;g.beginPath();g.moveTo(x,y);for(let i=0;i<7;i++){x+=r()*40-12;y+=r()*30-10;g.lineTo(x,y)}g.stroke()};
 const beam=(x,y,w,h)=>{const q=g.createLinearGradient(x,y,x,y+h);q.addColorStop(0,'rgba(150,180,255,.25)');q.addColorStop(1,'transparent');g.fillStyle=q;g.beginPath();g.moveTo(x,y);g.lineTo(x+w,y);g.lineTo(x+w+90,y+h);g.lineTo(x+60,y+h);g.fill()};
 const box=(x,y,w,h,c,l)=>{g.fillStyle=c;g.fillRect(x,y,w,h);g.fillStyle=l||'rgba(255,255,255,.1)';g.fillRect(x,y,w,2)};
 g.fillStyle='#14121a';g.fillRect(0,0,WW,WH);
 g.fillStyle='#17141f';g.fillRect(0,400,WW,300);speck(0,400,WW,300,2500,'rgba(255,255,255,.05)');
 g.fillStyle='rgba(255,230,120,.3)';for(let x=40;x<WW;x+=120)g.fillRect(x,548,60,5);
 for(let i=0;i<9;i++){const x=80+r()*1640,y=430+r()*240,q=g.createRadialGradient(x,y,0,x,y,60);q.addColorStop(0,'rgba(120,150,220,.25)');q.addColorStop(1,'transparent');g.fillStyle=q;g.beginPath();g.ellipse(x,y,70,18,0,0,7);g.fill()}
 for(let x=150;x<WW;x+=360){box(x,420,6,40,'#3a3a46');g.fillStyle='#2a2a32';g.fillRect(x-8,418,22,6);g.fillStyle='#ffd88a';g.beginPath();g.arc(x+3,424,5,0,7);g.fill()}
 // neon signs on the street
 g.font='34px Creepster,Impact,fantasy';[['OPEN',280,640,'#6dffb0'],['MOTEL',900,650,'#ff4f8b'],['BAR',1520,640,'#78aaff']].forEach(([t,x,y,c])=>{g.shadowColor=c;g.shadowBlur=22;g.fillStyle=c;g.fillText(t,x,y);g.shadowBlur=0});
 for(let i=0;i<4;i++)crack(100+r()*1600,430+r()*230);
 if(PH.street){cover(g,PH.street,0,400,WW,300,.8);g.fillStyle='rgba(5,4,14,.35)';g.fillRect(0,400,WW,300)}
 const TH={
  metro(x,y,w,h){g.fillStyle='#1b2a3a';g.fillRect(x,y,w,h);g.strokeStyle='rgba(255,255,255,.06)';for(let i=0;i<w;i+=40){g.beginPath();g.moveTo(x+i,y);g.lineTo(x+i,y+h);g.stroke()}for(let j=0;j<h;j+=40){g.beginPath();g.moveTo(x,y+j);g.lineTo(x+w,y+j);g.stroke()}
   g.fillStyle='rgba(255,200,0,.4)';for(let i=0;i<w;i+=30)g.fillRect(x+i,y+h-80,18,5);box(x+30,y+36,240,80,'#2b3d52');g.fillStyle='rgba(200,214,160,.3)';for(let i=0;i<5;i++)g.fillRect(x+45+i*45,y+50,30,28);
   [330,440,520].forEach(b=>box(x+b,y+200,60,16,'#4a3526'));for(let i=0;i<4;i++){g.fillStyle=['#7a2020','#20507a','#7a6a20','#3a7a3a'][i];g.fillRect(x+300+i*70,y+22,44,60)}},
  tower(x,y,w,h){g.fillStyle='#2b2638';g.fillRect(x,y,w,h);g.fillStyle='rgba(255,255,255,.045)';for(let i=0;i<w;i+=60)for(let j=0;j<h;j+=60)if((i+j)/60%2==0)g.fillRect(x+i,y+j,60,60);
   [[90,130],[500,130],[90,300],[500,300]].forEach(([a,b])=>{const q=g.createRadialGradient(x+a-5,y+b-5,2,x+a,y+b,22);q.addColorStop(0,'#7a6e96');q.addColorStop(1,'#2e2640');g.fillStyle=q;g.beginPath();g.arc(x+a,y+b,22,0,7);g.fill()});
   box(x+200,y+170,200,44,'#3b2f2a');beam(x+120,y+16,70,300);beam(x+400,y+16,70,300)},
  police(x,y,w,h){g.fillStyle='#2e2522';g.fillRect(x,y,w,h);g.strokeStyle='rgba(0,0,0,.35)';for(let j=0;j<h;j+=22){g.beginPath();g.moveTo(x,y+j);g.lineTo(x+w,y+j);g.stroke()}
   [[60,100],[220,100],[60,260],[220,260]].forEach(([a,b])=>{box(x+a,y+b,110,46,'#4a3526');g.fillStyle='rgba(240,240,220,.6)';g.fillRect(x+a+12,y+b+8,26,18)});
   g.strokeStyle='#6a6a74';g.lineWidth=3;for(let i=0;i<9;i++){g.beginPath();g.moveTo(x+420+i*18,y+20);g.lineTo(x+420+i*18,y+140);g.stroke()}g.lineWidth=1;box(x+400,y+150,180,6,'#6a6a74')},
  obs(x,y,w,h){g.fillStyle='#1d2040';g.fillRect(x,y,w,h);const cx0=x+w/2,cy0=y+h/2;for(let rr=50;rr<230;rr+=36){g.strokeStyle='rgba(120,140,255,.14)';g.beginPath();g.arc(cx0,cy0,rr,0,7);g.stroke()}
   const q=g.createRadialGradient(cx0,cy0,0,cx0,cy0,150);q.addColorStop(0,'rgba(140,170,255,.3)');q.addColorStop(1,'transparent');g.fillStyle=q;g.fillRect(cx0-150,cy0-150,300,300);
   g.fillStyle='#2a2d5e';g.beginPath();g.arc(cx0,cy0,34,0,7);g.fill();g.save();g.translate(cx0,cy0);g.rotate(-.6);g.fillStyle='#3a3f86';g.fillRect(0,-12,150,24);g.restore();speck(x,y,w,h,200,'rgba(200,210,255,.35)')},
  grid(x,y,w,h){g.fillStyle='#301e1e';g.fillRect(x,y,w,h);g.strokeStyle='rgba(0,0,0,.35)';for(let i=0;i<w;i+=20){g.beginPath();g.moveTo(x+i,y);g.lineTo(x+i,y+h);g.stroke()}for(let j=0;j<h;j+=20){g.beginPath();g.moveTo(x,y+j);g.lineTo(x+w,y+j);g.stroke()}
   box(x+30,y+h-60,w-60,16,'#7a2b2b','rgba(255,150,150,.25)');for(let i=0;i<w;i+=44){g.fillStyle=(i/44)%2?'rgba(255,200,0,.5)':'rgba(0,0,0,.5)';g.fillRect(x+i,y+h-140,22,6)}
   [100,330,560,780].forEach(a=>{box(x+a,y+90,90,110,'#3a3a44');g.fillStyle='#f33';g.fillRect(x+a+10,y+100,6,6);g.fillStyle='#3f3';g.fillRect(x+a+24,y+100,6,6)})}};
 RM.forEach(([n,x,y,w,h,k])=>{TH[k](x,y,w,h);speck(x,y,w,h,900,'rgba(255,255,255,.04)');
  if(PH[k]){cover(g,PH[k],x,y,w,h,.85);g.fillStyle='rgba(5,4,14,.3)';g.fillRect(x,y,w,h)}
  for(let i=0;i<3;i++)stain(x+60+r()*(w-120),y+60+r()*(h-120),34+r()*30,'rgba(70,6,6,.55)');for(let i=0;i<3;i++)crack(x+40+r()*(w-120),y+40+r()*(h-100));
  const v=g.createRadialGradient(x+w/2,y+h/2,h*.3,x+w/2,y+h/2,w*.7);v.addColorStop(0,'transparent');v.addColorStop(1,'rgba(0,0,0,.55)');g.fillStyle=v;g.fillRect(x,y,w,h);
  g.font='22px Creepster,Impact,fantasy';g.fillStyle='rgba(255,255,255,.16)';g.fillText(n,x+30,y+h/2+(y<400?-30:40))});
 walls.forEach(([a,b,w,h])=>{g.fillStyle='#473a5c';g.fillRect(a,b,w,h);g.strokeStyle='rgba(0,0,0,.4)';g.lineWidth=1;for(let i=b;i<b+h;i+=12){g.beginPath();g.moveTo(a,i);g.lineTo(a+w,i);g.stroke()}g.fillStyle='rgba(255,255,255,.14)';g.fillRect(a,b,w,2)});
 // lamp fixtures
 LAMPS.forEach(([x,y,R,c])=>{g.fillStyle=`rgb(${LC[c]})`;g.shadowColor=`rgb(${LC[c]})`;g.shadowBlur=14;g.beginPath();g.arc(x,y,4,0,7);g.fill();g.shadowBlur=0})}
const fog=document.createElement('canvas');fog.width=fog.height=256;{const f=fog.getContext('2d'),q=f.createRadialGradient(128,128,0,128,128,128);q.addColorStop(0,'rgba(200,210,255,.2)');q.addColorStop(1,'transparent');f.fillStyle=q;f.fillRect(0,0,256,256)}
const grain=document.createElement('canvas');grain.width=grain.height=128;{const f=grain.getContext('2d'),d=f.createImageData(128,128);for(let i=0;i<d.data.length;i+=4){const v=Math.random()*255;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=22}f.putImageData(d,0,0)}
/* ---------- audio: generative music + synthesised sfx ---------- */
let AC=null,MG,MUS,NB,SEND,rainG,tenG,muted=false,au=null,mt=0,chordI=0;
const mf=n=>440*Math.pow(2,(n-69)/12),CH=[[45,57,60,64],[41,53,57,60],[48,55,60,64],[40,52,56,59]],SCL=[57,60,62,64,67,69,72,76];
function noise(d,v,f,ty){if(!AC||muted)return;const s=AC.createBufferSource();s.buffer=NB;const fl=AC.createBiquadFilter();fl.type=ty;fl.frequency.value=f;const g=AC.createGain(),t=AC.currentTime;g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.001,t+d);s.connect(fl);fl.connect(g);g.connect(MG);s.start();s.stop(t+d)}
function beep(f,d,v,ty='sine',to){if(!AC||muted)return;const o=AC.createOscillator(),g=AC.createGain(),t=AC.currentTime;o.type=ty;o.frequency.setValueAtTime(f,t);if(to)o.frequency.exponentialRampToValueAtTime(to,t+d);g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.001,t+d);o.connect(g);g.connect(MG);o.start(t);o.stop(t+d)}
function pad(ch){const t=AC.currentTime;ch.forEach((n,i)=>[-7,7].forEach(det=>{const o=AC.createOscillator(),f=AC.createBiquadFilter(),g=AC.createGain();o.type=i?'triangle':'sawtooth';o.frequency.value=mf(n);o.detune.value=det;f.type='lowpass';f.frequency.value=i?1000:360;g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(i?.05:.085,t+2.6);g.gain.linearRampToValueAtTime(0,t+9.6);o.connect(f);f.connect(g);g.connect(MUS);o.start(t);o.stop(t+10)}))}
function pluck(){const t=AC.currentTime,n=SCL[Math.random()*SCL.length|0],o=AC.createOscillator(),g=AC.createGain();o.type='triangle';o.frequency.value=mf(n);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.16,t+.01);g.gain.exponentialRampToValueAtTime(.001,t+2.2);o.connect(g);g.connect(MUS);o.start(t);o.stop(t+2.3)}
function musicTick(){if(!AC||muted||CFG.music||st=='menu'&&mt%2)return;if(mt%8==0)pad(CH[chordI++%4]);if(Math.random()<.45)pluck();mt++}
function initAudio(){if(AC){AC.resume();return}try{AC=new(window.AudioContext||window.webkitAudioContext)()}catch(e){return}
 MG=AC.createGain();MG.gain.value=.9;MG.connect(AC.destination);MUS=AC.createGain();MUS.gain.value=CFG.vol*1.2;MUS.connect(MG);
 NB=AC.createBuffer(1,AC.sampleRate*2,AC.sampleRate);const d=NB.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;
 const len=AC.sampleRate*2.6,ir=AC.createBuffer(2,len,AC.sampleRate);for(let c=0;c<2;c++){const a=ir.getChannelData(c);for(let i=0;i<len;i++)a[i]=(Math.random()*2-1)*Math.pow(1-i/len,2.6)}
 const cvb=AC.createConvolver();cvb.buffer=ir;SEND=AC.createGain();SEND.connect(cvb);cvb.connect(MG);const mw=AC.createGain();mw.gain.value=.55;MUS.connect(mw);mw.connect(SEND);
 [43,43.7,86.5].forEach((f,i)=>{const o=AC.createOscillator(),g=AC.createGain(),l=AC.createBiquadFilter();o.type=i<2?'sawtooth':'sine';o.frequency.value=f;l.type='lowpass';l.frequency.value=140;g.gain.value=i<2?.04:.06;o.connect(l);l.connect(g);g.connect(MG);o.start()});
 // tension layer: tritone with tremolo, fades in when danger is close
 tenG=AC.createGain();tenG.gain.value=0;tenG.connect(MUS);[110,155.6,311].forEach(f=>{const o=AC.createOscillator();o.type='sine';o.frequency.value=f;o.connect(tenG);o.start()});
 const tl=AC.createOscillator(),tg=AC.createGain();tl.frequency.value=5.5;tg.gain.value=.03;tl.connect(tg);tg.connect(tenG.gain);tl.start();
 const loop=(f,ty,q)=>{const s=AC.createBufferSource();s.buffer=NB;s.loop=true;const b=AC.createBiquadFilter();b.type=ty;b.frequency.value=f;if(q)b.Q.value=q;const g=AC.createGain();s.connect(b);b.connect(g);g.connect(MG);s.start();return g};
 const wg=loop(380,'bandpass',.8);wg.gain.value=.05;rainG=loop(2500,'highpass');rainG.gain.value=0;cryLoop();
 if(CFG.music){au=new Audio(CFG.music);au.loop=true;au.volume=CFG.vol;au.play().catch(()=>{})}else pad(CH[0]),chordI=1}
setInterval(musicTick,1000);
function toggleMute(){muted=!muted;if(MG)MG.gain.value=muted?0:.9;if(au)muted?au.pause():au.play().catch(()=>{});$('#mb').textContent=muted?'♪ Music OFF':'♪ Music ON'}
function cry(vol,pan,pitch=1){if(!AC||muted)return;const t=AC.currentTime,dur=1.8+Math.random()*1.4,b=(300+Math.random()*100)*pitch;
 const o=AC.createOscillator();o.type='sawtooth';o.frequency.setValueAtTime(b*.8,t);o.frequency.linearRampToValueAtTime(b*1.55,t+dur*.3);o.frequency.exponentialRampToValueAtTime(b*.55,t+dur);
 const v=AC.createOscillator(),vg=AC.createGain();v.frequency.value=5.5;vg.gain.value=b*.04;v.connect(vg);vg.connect(o.frequency);
 const am=AC.createGain();am.gain.value=.5;const t2=AC.createOscillator(),tg=AC.createGain();t2.frequency.value=6+Math.random()*2;tg.gain.value=.45;t2.connect(tg);tg.connect(am.gain);
 const env=AC.createGain();env.gain.setValueAtTime(0,t);env.gain.linearRampToValueAtTime(vol,t+.25);env.gain.linearRampToValueAtTime(vol*.8,t+dur*.7);env.gain.linearRampToValueAtTime(0,t+dur);
 const p=AC.createStereoPanner?AC.createStereoPanner():AC.createGain();if(p.pan)p.pan.value=pan;
 [[700,5],[1250,7]].forEach(([f,q])=>{const bp=AC.createBiquadFilter();bp.type='bandpass';bp.frequency.value=f;bp.Q.value=q;o.connect(bp);bp.connect(am)});
 am.connect(env);env.connect(p);p.connect(MG);const s=AC.createGain();s.gain.value=.9;p.connect(s);s.connect(SEND);[o,v,t2].forEach(x=>{x.start(t);x.stop(t+dur+.1)})}
function cryLoop(){const near=st=='play'?Math.max(0,1-ghDist()/700):0;cry(.3+.5*near,Math.random()*1.6-.8,Math.random()<.3?1.6:1);setTimeout(cryLoop,5000+Math.random()*8000)}
function scream(){if(!AC||muted)return;const t=AC.currentTime,ws=AC.createWaveShaper(),c=new Float32Array(256);for(let i=0;i<256;i++)c[i]=Math.tanh((i/128-1)*6);ws.curve=c;
 const g=AC.createGain();g.gain.setValueAtTime(.5,t);g.gain.exponentialRampToValueAtTime(.001,t+1);[['sawtooth',1100],['square',1480]].forEach(([ty,f])=>{const o=AC.createOscillator();o.type=ty;o.frequency.setValueAtTime(f,t);o.frequency.exponentialRampToValueAtTime(170,t+.9);o.connect(ws);o.start(t);o.stop(t+1)});ws.connect(g);g.connect(MG);g.connect(SEND);noise(.7,.6,3500,'highpass');beep(50,.5,.8)}
const beat=()=>{beep(55,.18,.7);setTimeout(()=>beep(48,.2,.55),170)},thunder=()=>noise(2.6,.7,220,'lowpass'),zap=()=>{noise(.4,.5,5000,'highpass');beep(900,.3,.2,'sawtooth',120)},whoosh=()=>noise(.35,.25,900,'bandpass'),ring=()=>{for(let i=0;i<4;i++)setTimeout(()=>{beep(1400,.12,.12,'square');beep(1000,.12,.1,'square')},i*220)};
/* ---------- jump scare face ---------- */
function face(g,W,H,k){g.save();g.translate(W/2+(Math.random()-.5)*40*k,H/2+(Math.random()-.5)*40*k);const s=Math.min(W,H)/400*(1+(1-k)*.5);g.scale(s,s);g.rotate((Math.random()-.5)*.08*k);
 g.strokeStyle='#050505';g.lineWidth=4;for(let i=0;i<46;i++){g.beginPath();g.moveTo(-100+i*4.4,-130);g.bezierCurveTo(-140+i*5,-60,-170+i*6,40,-150+i*5+Math.random()*30,230);g.stroke()}
 g.fillStyle='#e8e8dc';g.beginPath();g.ellipse(0,0,115,165,0,0,7);g.fill();g.fillStyle='rgba(0,0,0,.22)';g.beginPath();g.ellipse(0,60,70,90,0,0,7);g.fill();
 g.fillStyle='#000';[-45,45].forEach(x=>{g.beginPath();g.ellipse(x,-35,27,44,0,0,7);g.fill()});g.shadowColor='#f00';g.shadowBlur=24;g.fillStyle='#f22';[-45,45].forEach(x=>{g.beginPath();g.arc(x,-28,6,0,7);g.fill()});g.shadowBlur=0;
 g.fillStyle='#000';g.beginPath();g.moveTo(-62,72);for(let i=0;i<=8;i++)g.lineTo(-62+i*15.5,72+(i%2?8:-6));g.bezierCurveTo(60,190,-60,190,-62,72);g.fill();g.fillStyle='#eee';for(let i=0;i<7;i++){g.beginPath();g.moveTo(-55+i*18,76);g.lineTo(-47+i*18,100);g.lineTo(-39+i*18,76);g.fill()}g.restore()}
/* ---------- game data ---------- */
const NEED={trace:['drive','The tracer needs a signal key. Check the police evidence locker.'],console:['code','Locked. It wants the 4-digit time of the first failure. Check the metro control panel.']};
const I=(id,x,y,sy,n,t,o={})=>({id,x,y,sy,n,t,...o});
const ITEMS=[I('panel',150,200,'P','Control panel','A maintenance card stamped <b>23:41</b>. The line was shut down by hand. That is the minute everything first failed.',{fl:'code'}),
 I('ticket',450,300,'T','Torn ticket','A ticket marked <b>M.R.</b> A photo says Mara Reed did it, but its shadows point two ways. Someone is framing her.'),
 I('logs',700,110,'L','Security desk','Access log: an executive badge entered at <b>23:47</b>. Name: <b>E. Voss</b>. PROOF 1: the badge log.',{pr:'logs'}),
 I('files',900,200,'F','Records cabinet','PROJECT BLACKOUT-0: a cancelled city kill-switch drill. Its access codes were never deleted.'),
 I('server',1090,290,'S','Server rack','The network cable was cut cleanly. PROOF 2: this was deliberate. Something tall stands at the end of the aisle...',{pr:'cable',sc:1}),
 I('board',1300,110,'B','Case board','Three suspects held grid clearance: Mara Reed, Elias Voss, Dr. Sen. A clipping: TUNNEL COLLAPSE, 11 DEAD. Report closed by E. Voss.'),
 I('radio',1710,150,'R','Old radio','Static, then: "The backup is in the observatory." A whisper: "I can hear you breathing."',{sc:1}),
 I('evid',1500,290,'E','Evidence locker','A sealed drive: a GPS log under the Central Grid Station and the signal key for the transmitter.',{fl:'drive'}),
 I('trans',150,880,'X','Transmitter','It sent one burst at midnight. Destination: the central grid.'),
 I('trace',760,1000,'Z','Signal tracer','The signal was an automated script scheduled months ago with the old BLACKOUT-0 login. PROOF 3: the signal trace.',{pr:'trace',sc:1}),
 I('console',1500,900,'C','Grid console',''),
 ...[['Diary page 1','"Voss told us the tunnel supports were fine. They were not. I signed anyway."',480,150],['Diary page 2','"Eleven names on a list nobody reads. Mara kept a copy."',1130,130],['Diary page 3','"BLACKOUT-0 was never a drill. It was a way to bury the vault."',1650,330],['Diary page 4','"Dr. Sen refused to sign. Two days later the lab was closed."',250,1040],['Diary page 5','"If you are reading this: hold the light on it. The light is the only thing it fears."',1250,820]].map((p,i)=>I('pg'+i,p[2],p[3],'¶',p[0],p[1],{pg:1})),
 ...[[300,540],[1500,560],[1000,330],[1150,950]].map((p,i)=>I('b'+i,p[0],p[1],'+','Battery','',{bat:1})),
 ...[[450,650],[1250,470],[600,1020]].map((p,i)=>I('f'+i,p[0],p[1],'*','Flare','',{flr:1})),
 ...[[60,350],[1140,70],[1260,350],[60,760],[860,1050],[1750,740]].map((p,i)=>I('h'+i,p[0],p[1],'H','Hide','',{hide:1})),
 I('acc',900,550,'!','Make the accusation','',{hid:1})];
const SUSP=['Mara Reed, station engineer','Elias Voss, executive','Dr. Sen, scientist'],SPM=[5,4,3],WHISP=['You hear someone sobbing behind the wall.','A phone rings somewhere. Nobody answers.','Something drags across the floor above you.','"Detective..." the dark whispers.'];
const TAUNT=['"One down. Do you even know what you are looking for?"','"Careful, detective. The dark has teeth."','"Three. I almost admire you. Almost."'];
let st='menu',diff=1,g,keys={},mouse=null,joy=null,shake=0,scareT=0,scareMax=1,flashT=0,lt=15,ambT=45,rainI=0,msgT,lastClock='',run2=false,best=0,items,rain=[],camx=0,camy=0,T1=0,beatT=0;
try{best=+localStorage.getItem('zh_best')||0}catch(e){}
for(let i=0;i<130;i++)rain.push([Math.random(),Math.random(),.6+Math.random()]);
const ghDist=()=>g?Math.min(...g.gh.map(h=>Math.hypot(h.x-g.x,h.y-g.y))):9e3;
function say(t,d=4500){const m=$('#msg');m.innerHTML=t;m.style.display='block';clearTimeout(msgT);msgT=setTimeout(()=>m.style.display='none',d)}
function ov(h){const o=$('#ov');o.innerHTML=h?`<div class="p">${h}</div>`:'';o.style.display=h?'flex':'none'}
function reset(){g={m:90,bat:100,light:true,x:900,y:550,ang:-1.57,stam:100,hid:false,hidt:0,pf:new Set,fl:new Set,wr:0,near:null,walk:0,black:0,flare:1,pages:0,fls:[],gh:[{x:1500,y:200,d:6,lt:0}]};if(diff==2)g.gh.push({x:300,y:900,d:14,lt:0});items=ITEMS.map(i=>({...i,done:false}))}
function menu(){st='menu';ov(`<h1>ZERO HOUR</h1><p class="m" style="text-align:center">Case 001 · Veridia City · 90 minutes to live</p><p>Find <b>4 proofs</b>, then accuse the culprit. A faceless thing hunts you: it <b>freezes in your light</b>, and <b>2 seconds of beam burns it away</b>. Throw <b>flares</b> (G) to make safe zones. Collect <b>diary pages</b> for bonus time and score. Hide in lockers when it gets close.</p><p class="m">⚠ Loud sounds, flashing images and jump scares. Headphones recommended.</p><div style="display:flex;gap:6px">${['Easy','Normal','Hard'].map((n,i)=>`<button class="w ${i==diff?'sel':''}" onclick="diff=${i};menu()">${n}</button>`).join('')}</div><button class="w" onclick="start()">▶ Begin case</button><p class="m" style="text-align:center">Best score: ${best}</p>`)}
function start(){initAudio();reset();st='play';ov('');say('Follow the glowing marks. Candles and lamps are safe light.',6500);ambT=40;lt=15}
function dlg(t,h,sc){st='dlg';run2=sc;ov(`<h2>${t}</h2><p>${h}</p><button class="w" onclick="closeDlg()">Continue [E]</button>`)}
function closeDlg(){if(st!='dlg')return;ov('');st='play';if(run2)setTimeout(()=>{if(st=='play')scare(1)},1100)}
function scare(big){if(scareT>0)return;scareMax=scareT=big?.8:.45;shake=1;flashT=.2;scream();try{navigator.vibrate&&navigator.vibrate([120,50,120])}catch(e){}}
function lose(w){st='end';ov(`<h2 style="color:var(--red)">TIME EXPIRED</h2><p>${w}</p><button class="w" onclick="start()">Retry</button><button class="w" onclick="menu()">Menu</button>`)}
function win(){st='end';const sc=Math.round(g.m*10+(2-g.wr)*100+g.pages*50),rk=g.m>=30?'S':g.m>=12?'A':'B';if(sc>best){best=sc;try{localStorage.setItem('zh_best',sc)}catch(e){}}
 ov(`<h2 style="color:#6dffb0">CASE CLOSED</h2><p>Elias Voss sealed every safety report after the tunnel collapse killed 11 people. He blacked out the city to wipe the vault that proved it. Your proofs put him away.</p><p><b>${Math.floor(g.m)} min left · Pages ${g.pages}/5 · Rank ${rk} · Score ${sc}</b></p><button class="w" onclick="start()">Play again</button><button class="w" onclick="menu()">Menu</button>`)}
function throwFlare(){if(st!='play'||g.flare<=0||g.hid)return;g.flare--;let x=g.x,y=g.y;for(let i=0;i<14;i++){const nx=x+Math.cos(g.ang)*10,ny=y+Math.sin(g.ang)*10;if(blocked(nx,ny,6))break;x=nx;y=ny}g.fls.push({x,y,t:14});whoosh();say('Flare lit. It cannot cross this light.',2500)}
function use(it){const i=it.id;
 if(it.hide){g.hid=true;g.hidt=0;beep(300,.1,.1);say('You hide. Stay quiet...');return}
 if(it.bat){it.done=true;g.bat=Math.min(100,g.bat+45);beep(900,.15,.15);say('Battery +45%');return}
 if(it.flr){it.done=true;g.flare++;beep(700,.15,.15);say('Flare +1  (press G)');return}
 if(i=='acc'){st='acc';ov(`<h2>WHO DID IT?</h2><p class="m">Two wrong accusations lose.</p>${SUSP.map((n,k)=>`<button class="w" onclick="accuse(${k})">${n}</button>`).join('')}<button class="w" onclick="ov('');st='play'">Not yet</button>`);return}
 const nd=NEED[i];if(nd&&!g.fl.has(nd[0])){say(nd[1]);beep(120,.3,.2,'sawtooth');return}
 if(i=='console'){st='key';ov(`<h2>GRID CONSOLE</h2><p class="m" style="text-align:center">Time of the first failure (4 digits)</p><input id="cd" inputmode="numeric" maxlength="4" placeholder="----" onkeydown="if(event.key=='Enter')code()"><button class="w" onclick="code()">Unlock</button><button class="w" onclick="ov('');st='play'">Cancel</button>`);setTimeout(()=>$('#cd').focus(),50);return}
 it.done=true;if(it.fl)g.fl.add(it.fl);let t=it.t;
 if(it.pg){g.pages++;g.m=Math.min(90,g.m+3);t+=` <i>(+3 minutes · ${g.pages}/5 pages)</i>`;beep(660,.2,.15);beep(990,.3,.12)}
 else if(it.pr){g.pf.add(it.pr);t+=' <i>'+TAUNT[Math.min(g.pf.size,3)-1]+'</i>';beep(880,.2,.2);beep(1320,.3,.15)}else beep(520,.15,.15,'triangle');dlg(it.n,t,it.sc)}
function code(){if($('#cd').value=='2341'){const c=items.find(x=>x.id=='console');c.done=true;g.pf.add('cred');beep(880,.2,.2);dlg('Grid console','ARCHIVE WIPE SCHEDULED. Authorised by the credential of <b>Elias Voss</b>. PROOF 4: the credential. The phone rings: <i>"You found me. But who gave me the codes?"</i>',1)}else{g.m-=2;shake=.6;beep(110,.4,.3,'sawtooth');ov('');st='play';say('Wrong code. -2 minutes.')}}
function accuse(k){if(k==1&&g.pf.size>=4)return win();g.wr++;g.m-=10;ov('');st='play';beep(110,.4,.3,'sawtooth');say(k==1?'Not enough proof yet. -10 minutes.':'That does not match the proof. -10 minutes.');if(g.wr>=2)lose('Two wrong accusations. The culprit slipped into the dark.')}
function lit(h){if(!(g.light&&g.bat>0)||g.hid||g.black>0||Math.hypot(h.x-g.x,h.y-g.y)>CONE-20)return false;return Math.abs(((Math.atan2(h.y-g.y,h.x-g.x)-g.ang+Math.PI*3)%(Math.PI*2))-Math.PI)<HALF+.08}
function farRoom(){return RM.map(r=>[r[1]+r[3]/2,r[2]+r[4]/2]).sort((a,b)=>Math.hypot(b[0]-g.x,b[1]-g.y)-Math.hypot(a[0]-g.x,a[1]-g.y))[0]}
/* ---------- input ---------- */
addEventListener('keydown',e=>{const k=e.key.toLowerCase();if(!AC&&st!='menu')initAudio();keys[k]=1;if(st=='key')return;if(k=='e'||k==' '||k=='enter'){if(st=='dlg')closeDlg();else if(st=='play'){if(g.hid)g.hid=false;else if(g.near)use(g.near)}}
 if(st=='play'){if(k=='f')g.light=!g.light;if(k=='g')throwFlare();if(k=='p'||k=='escape'){st='pause';ov('<h2>PAUSED</h2><button class="w" onclick="ov(\'\');st=\'play\'">Resume</button><button class="w" onclick="menu()">Menu</button>')}}else if(st=='pause'&&(k=='p'||k=='escape')){ov('');st='play'}
 if(k=='m')toggleMute();if(e.key.startsWith('Arrow')||e.key==' ')e.preventDefault()});
addEventListener('keyup',e=>keys[e.key.toLowerCase()]=0);
if(!('ontouchstart'in window))addEventListener('mousemove',e=>mouse=[e.clientX,e.clientY]);
addEventListener('mousedown',e=>{window.focus();if(e.target.closest('.ov,#tb,#hud'))return;if(e.button==2&&st=='play')g.light=!g.light});addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('touchstart',e=>{const t=e.changedTouches[0];if(!joy)joy={id:t.identifier,x:t.clientX,y:t.clientY,dx:0,dy:0}},{passive:true});
cv.addEventListener('touchmove',e=>{for(const t of e.changedTouches)if(joy&&t.identifier==joy.id){joy.dx=t.clientX-joy.x;joy.dy=t.clientY-joy.y}},{passive:true});
cv.addEventListener('touchend',()=>joy=null);
if('ontouchstart'in window){$('#tb').style.display='flex';$('#bA').onclick=()=>keydown('e');$('#bG').onclick=()=>throwFlare();$('#bL').onclick=()=>st=='play'&&(g.light=!g.light);$('#bR').ontouchstart=()=>keys.shift=1;$('#bR').ontouchend=()=>keys.shift=0}
function keydown(k){dispatchEvent(new KeyboardEvent('keydown',{key:k}))}
/* ---------- update ---------- */
function update(dt){shake=Math.max(0,shake-dt);flashT=Math.max(0,flashT-dt);lt-=dt;if(lt<0){lt=18+Math.random()*25;flashT=.3;setTimeout(thunder,350+Math.random()*700)}
 if(st!='play'){if(tenG)tenG.gain.setTargetAtTime(0,AC.currentTime,.5);return}
 let vx=(keys.d||keys.arrowright?1:0)-(keys.a||keys.arrowleft?1:0),vy=(keys.s||keys.arrowdown?1:0)-(keys.w||keys.arrowup?1:0);
 if(joy&&Math.hypot(joy.dx,joy.dy)>10){vx=joy.dx;vy=joy.dy}const L=Math.hypot(vx,vy);
 if(g.hid){if(L)g.hid=false;else{g.hidt+=dt;if(g.hidt>6){g.hid=false;const f=farRoom();g.gh.forEach(h=>{h.x=f[0];h.y=f[1];h.d=8});say('It lingered, then drifted away.')}}}
 const run=keys.shift&&g.stam>0&&L>0&&!g.hid;g.stam=run?Math.max(0,g.stam-32*dt):Math.min(100,g.stam+14*dt);
 if(L&&!g.hid){const s=(run?235:150)*dt;vx=vx/L*s;vy=vy/L*s;g.walk+=dt*10;if(!blocked(g.x+vx,g.y))g.x+=vx;if(!blocked(g.x,g.y+vy))g.y+=vy;if(!mouse||joy)g.ang=Math.atan2(vy,vx);if(Math.sin(g.walk)>.97)noise(.06,.05,500,'lowpass')}
 if(mouse&&!joy)g.ang=Math.atan2(mouse[1]-(g.y-camy)*Z,mouse[0]-(g.x-camx)*Z);
 g.m-=dt/SPM[diff];if(g.light&&g.bat>0&&!g.hid)g.bat=Math.max(0,g.bat-dt*1.3);g.black=Math.max(0,g.black-dt);
 g.fls.forEach(f=>f.t-=dt);g.fls=g.fls.filter(f=>f.t>0);
 if(g.m<=0){g.m=0;return lose('The batteries died. The hospitals went dark and the city is still offline.')}
 let dm=9e3;for(const h of g.gh){h.d-=dt;const d=Math.hypot(g.x-h.x,g.y-h.y);dm=Math.min(dm,d);const LT=lit(h);
  if(LT&&d<320){h.lt+=dt;if(h.lt>2){h.lt=0;h.x+=(h.x-g.x)/(d||1)*230;h.y+=(h.y-g.y)/(d||1)*230;h.d=4;zap();shake=.5;say('The light burns it away!',2200)}}else h.lt=Math.max(0,h.lt-dt*2);
  const fr=g.fls.find(f=>Math.hypot(f.x-h.x,f.y-h.y)<210);
  if(fr){const k=Math.hypot(h.x-fr.x,h.y-fr.y)||1;h.x+=(h.x-fr.x)/k*90*dt;h.y+=(h.y-fr.y)/k*90*dt}
  else if(h.d<=0&&!LT){const sp=(50+diff*12+(1-g.m/90)*40)*dt*((g.light&&g.bat>0)?1:1.5)*(run&&d<420?1.3:1);h.x+=(g.x-h.x)/(d||1)*sp;h.y+=(g.y-h.y)/(d||1)*sp;
  if(d<22&&!g.hid){g.m-=8;scare(1);say('It touched you. -8 minutes. Keep it in the light!');const f=farRoom();h.x=f[0];h.y=f[1];h.d=4}}}
 const tens=Math.max(0,1-dm/650)*.8+(g.m<20?.2:0);if(tenG)tenG.gain.setTargetAtTime(tens*.14,AC.currentTime,.4);
 beatT-=dt;if(dm<260&&beatT<=0){beat();beatT=Math.max(.45,dm/260*1.1)}
 ambT-=dt;if(ambT<=0){ambT=35+Math.random()*40;if(!g.hid){const r=Math.random();if(r<.3)scare(0);else if(r<.6){g.black=2.5;say(WHISP[Math.random()*4|0]);cry(.7,0,1.3)}else if(r<.8){ring();say('A phone rings somewhere nearby...')}else{shake=.7;noise(.5,.8,150,'lowpass');say('A door slams in the dark.')}}}
 if(Math.random()<dt*.03)say(WHISP[Math.random()*4|0]);
 g.near=null;let b=62;for(const it of items){if(it.done||(it.hid&&g.pf.size<4))continue;const d=Math.hypot(it.x-g.x,it.y-g.y);if((it.bat||it.flr)&&d<30){use(it);continue}if(d<b){b=d;g.near=it}}
 const inSt=g.y>400&&g.y<700;rainI+=((inSt?1:0)-rainI)*dt*2;if(rainG)rainG.gain.value=rainI*.05;
 const mm=Math.floor(g.m),ss=Math.floor(g.m%1*60),ck=String(mm).padStart(2,'0')+':'+String(ss).padStart(2,'0');if(ck!=lastClock){lastClock=ck;$('#clock').textContent=ck}
 $('#bt').style.width=g.bat+'%';$('#sm').style.width=g.stam+'%';$('#loc').textContent=(RM.find(r=>g.x>r[1]&&g.x<r[1]+r[3]&&g.y>r[2]&&g.y<r[2]+r[4])||['HUB STREET'])[0]+` · flares ${g.flare} · pages ${g.pages}/5`;
 $('#pf').innerHTML=[['logs','LOG'],['cable','CABLE'],['trace','TRACE'],['cred','CRED']].map(([k,l])=>`<span class="${g.pf.has(k)?'on':''}">${l}</span>`).join('');
 $('#pr').textContent=g.hid?'HIDING... [E] leave':g.near?`[E] ${g.near.hide?'Hide':g.near.n}`:''}
/* ---------- draw ---------- */
function ghost(h,t){const sh=h.lt>0?(Math.random()-.5)*h.lt*5:0,x=h.x+sh,y=h.y,w=Math.sin(t*3+x)*3;cx.save();cx.fillStyle='#000';cx.beginPath();cx.moveTo(x-18,y+34);cx.bezierCurveTo(x-24+w,y-10,x-16,y-34,x,y-40);cx.bezierCurveTo(x+16,y-34,x+24-w,y-10,x+18,y+34);for(let i=0;i<4;i++)cx.lineTo(x+18-i*9+(i%2?4:-4),y+34+(i%2?10:2)+w);cx.fill();
 cx.fillStyle='rgba(220,220,210,.5)';cx.beginPath();cx.ellipse(x,y-26,8,11,0,0,7);cx.fill();cx.shadowColor='#f00';cx.shadowBlur=12;cx.fillStyle='#f22';cx.fillRect(x-6,y-30,4,4);cx.fillRect(x+2,y-30,4,4);cx.restore()}
function drawTitle(t){cx.setTransform(1,0,0,1,0,0);const q=cx.createLinearGradient(0,0,0,VH);q.addColorStop(0,'#05040c');q.addColorStop(1,'#2a1038');cx.fillStyle=q;cx.fillRect(0,0,VW,VH);
 if(PH.title){cover(cx,PH.title,0,0,VW,VH,.85);cx.fillStyle='rgba(5,4,14,.45)';cx.fillRect(0,0,VW,VH)}else{
 const mx=VW*.76,my=VH*.24,mr=Math.min(VW,VH)*.1,m=cx.createRadialGradient(mx,my,mr*.3,mx,my,mr*3);m.addColorStop(0,'rgba(255,240,210,.5)');m.addColorStop(1,'transparent');cx.fillStyle=m;cx.fillRect(0,0,VW,VH);cx.fillStyle='#f3ead0';cx.beginPath();cx.arc(mx,my,mr,0,7);cx.fill();cx.fillStyle='rgba(120,110,90,.3)';cx.beginPath();cx.arc(mx-mr*.3,my-mr*.2,mr*.18,0,7);cx.arc(mx+mr*.25,my+mr*.3,mr*.12,0,7);cx.fill();
 let s=3;const r=()=>(s=s*16807%2147483647)/2147483647;cx.fillStyle='#07050e';for(let x=0;x<VW;x+=VW/18){const bw=VW/18+4,bh=VH*(.22+r()*.35);cx.fillRect(x,VH-bh,bw,bh);for(let j=0;j<8;j++)if(r()<.14&&Math.sin(t*3+x+j)>-.6){cx.fillStyle='rgba(255,210,100,.6)';cx.fillRect(x+6+r()*(bw-14),VH-bh+10+j*18,6,8);cx.fillStyle='#07050e'}}}
 ghost({x:VW*.45,y:VH*.82,lt:0},t);for(let i=0;i<4;i++){cx.globalAlpha=.5;cx.drawImage(fog,((i*430+t*14*(i%2?1:-1))%(VW+500)+VW+500)%(VW+500)-250,VH*(.55+i*.1),520,300)}cx.globalAlpha=1;
 cx.strokeStyle='rgba(170,190,255,.25)';cx.beginPath();for(const d of rain){d[1]=(d[1]+.016*d[2]*1.6)%1;const x=d[0]*VW,y=d[1]*VH;cx.moveTo(x,y);cx.lineTo(x-3,y+16)}cx.stroke()}
function draw(t,dt){
 if(st=='menu'){drawTitle(t);post(t);return}
 camx=clamp(g.x-VW/(2*Z),0,Math.max(0,WW-VW/Z));camy=clamp(g.y-VH/(2*Z),0,Math.max(0,WH-VH/Z));const ox=shake>0?(Math.random()-.5)*14:0,oy=shake>0?(Math.random()-.5)*14:0;
 cx.setTransform(1,0,0,1,0,0);cx.fillStyle='#07060d';cx.fillRect(0,0,VW,VH);cx.setTransform(Z,0,0,Z,-camx*Z+ox,-camy*Z+oy);cx.drawImage(bg,0,0);
 for(let i=0;i<6;i++){cx.globalAlpha=.5;cx.drawImage(fog,((i*420+t*10*(i%2?1:-1))%WW+WW)%WW-150,(i*190)%WH,600,420)}cx.globalAlpha=1;
 cx.textAlign='center';cx.font='bold 16px monospace';
 for(const it of items){if(it.done||(it.hid&&g.pf.size<4))continue;if(it.hide){cx.fillStyle='#24304a';cx.fillRect(it.x-14,it.y-24,28,48);cx.strokeStyle='#5a6e96';cx.strokeRect(it.x-14,it.y-24,28,48);cx.fillStyle='#5a6e96';cx.fillRect(it.x-8,it.y-14,16,3);cx.fillRect(it.x-8,it.y-8,16,3);continue}
  const c=it.bat?'#6dffb0':it.flr?'#ff9d3d':it.pg?'#e8b6ff':it.pr?'#ffd23f':'#78aaff',p=1+Math.sin(t*4)*.12;cx.save();cx.translate(it.x,it.y);cx.scale(p,p);cx.shadowColor=c;cx.shadowBlur=14;cx.fillStyle='#14091e';cx.strokeStyle=c;cx.lineWidth=2;cx.beginPath();cx.arc(0,0,14,0,7);cx.fill();cx.stroke();cx.shadowBlur=0;cx.fillStyle=c;cx.fillText(it.sy,0,5);cx.restore()}
 for(const f of g.fls){cx.fillStyle='#fff3c0';cx.shadowColor='#ff9d3d';cx.shadowBlur=24;cx.beginPath();cx.arc(f.x,f.y,5+Math.random()*2,0,7);cx.fill();cx.shadowBlur=0}
 g.gh.forEach(h=>ghost(h,t));
 if(!g.hid){const y=g.y+Math.sin(g.walk)*1.5;cx.fillStyle='rgba(0,0,0,.5)';cx.beginPath();cx.ellipse(g.x,y+10,12,5,0,0,7);cx.fill();cx.fillStyle='#2e5c6e';cx.beginPath();cx.arc(g.x,y,12,0,7);cx.fill();cx.fillStyle='#1c1c28';cx.beginPath();cx.ellipse(g.x,y-5,14,6,0,0,7);cx.fill();cx.fillStyle='#ffd23f';cx.beginPath();cx.arc(g.x+Math.cos(g.ang)*11,y+Math.sin(g.ang)*11,3,0,7);cx.fill()}
 // darkness with flashlight cone, lamps and flares cut out of it
 cx.setTransform(1,0,0,1,0,0);const sx0=(g.x-camx)*Z+ox,sy0=(g.y-camy)*Z+oy,fl=(Math.random()<.02||g.black>0&&Math.random()<.5)?.8:1;
 const lamps=LAMPS.concat(g.fls.map(f=>[f.x,f.y,240*Math.min(1,f.t/2),'w']));const vis=[];
 for(const Lm of lamps){const lx=(Lm[0]-camx)*Z+ox,ly=(Lm[1]-camy)*Z+oy,R=Lm[2]*Z;if(lx<-R||lx>VW+R||ly<-R||ly>VH+R)continue;vis.push([lx,ly,R,Lm[3],.85+.15*Math.sin(t*7+Lm[0]*.1)*Math.sin(t*2.3+Lm[1])])}
 dx.globalCompositeOperation='source-over';dx.clearRect(0,0,VW,VH);dx.fillStyle=`rgba(2,1,8,${.9*fl})`;dx.fillRect(0,0,VW,VH);dx.globalCompositeOperation='destination-out';
 let q=dx.createRadialGradient(sx0,sy0,8*Z,sx0,sy0,130*Z);q.addColorStop(0,'rgba(0,0,0,1)');q.addColorStop(1,'rgba(0,0,0,0)');dx.fillStyle=q;dx.beginPath();dx.arc(sx0,sy0,130*Z,0,7);dx.fill();
 for(const [lx,ly,R,c,fk] of vis){q=dx.createRadialGradient(lx,ly,4,lx,ly,R);q.addColorStop(0,`rgba(0,0,0,${.85*fk})`);q.addColorStop(1,'rgba(0,0,0,0)');dx.fillStyle=q;dx.beginPath();dx.arc(lx,ly,R,0,7);dx.fill()}
 const beamOn=g.light&&g.bat>0&&!g.hid&&g.black<=0&&!(g.bat<15&&Math.random()<.25);
 if(beamOn){q=dx.createRadialGradient(sx0,sy0,20*Z,sx0,sy0,CONE*Z);q.addColorStop(0,'rgba(0,0,0,1)');q.addColorStop(1,'rgba(0,0,0,0)');dx.fillStyle=q;dx.beginPath();dx.moveTo(sx0,sy0);dx.arc(sx0,sy0,CONE*Z,g.ang-HALF,g.ang+HALF);dx.closePath();dx.fill()}
 cx.drawImage(dk,0,0);
 // coloured light glow on top (warm candles, blue observatory, red grid, flashlight beam)
 cx.globalCompositeOperation='lighter';
 for(const [lx,ly,R,c,fk] of vis){q=cx.createRadialGradient(lx,ly,2,lx,ly,R);q.addColorStop(0,`rgba(${LC[c]},${.26*fk})`);q.addColorStop(1,`rgba(${LC[c]},0)`);cx.fillStyle=q;cx.beginPath();cx.arc(lx,ly,R,0,7);cx.fill()}
 if(beamOn){q=cx.createRadialGradient(sx0,sy0,10,sx0,sy0,CONE*Z);q.addColorStop(0,'rgba(255,240,200,.2)');q.addColorStop(1,'rgba(255,240,200,0)');cx.fillStyle=q;cx.beginPath();cx.moveTo(sx0,sy0);cx.arc(sx0,sy0,CONE*Z,g.ang-HALF,g.ang+HALF);cx.closePath();cx.fill()}
 cx.globalCompositeOperation='source-over';
 for(const it of items){if(it.done||it.hide||(it.hid&&g.pf.size<4))continue;if(Math.hypot(it.x-g.x,it.y-g.y)<520){cx.fillStyle=`rgba(255,210,63,${.4+.3*Math.sin(t*4)})`;cx.beginPath();cx.arc((it.x-camx)*Z+ox,(it.y-camy)*Z+oy,3,0,7);cx.fill()}}
 if(rainI>.02){cx.strokeStyle=`rgba(170,190,255,${.35*rainI})`;cx.lineWidth=1;cx.beginPath();for(const d of rain){d[1]=(d[1]+dt*d[2]*1.6)%1;const x=d[0]*VW,y=d[1]*VH;cx.moveTo(x,y);cx.lineTo(x-3,y+16)}cx.stroke()}
 if(joy){cx.strokeStyle='rgba(255,255,255,.25)';cx.beginPath();cx.arc(joy.x,joy.y,40,0,7);cx.stroke();cx.fillStyle='rgba(255,255,255,.2)';cx.beginPath();cx.arc(joy.x+clamp(joy.dx,-40,40),joy.y+clamp(joy.dy,-40,40),18,0,7);cx.fill()}
 if(g.m<20){cx.fillStyle=`rgba(120,0,10,${.1+.06*Math.sin(t*4)})`;cx.fillRect(0,0,VW,VH)}post(t)}
function post(t){cx.setTransform(1,0,0,1,0,0);cx.globalAlpha=1;cx.drawImage(grain,Math.random()*-128,Math.random()*-128,VW+128,VH+128);const v=cx.createRadialGradient(VW/2,VH/2,Math.min(VW,VH)*.35,VW/2,VH/2,Math.max(VW,VH)*.75);v.addColorStop(0,'transparent');v.addColorStop(1,'rgba(0,0,0,.6)');cx.fillStyle=v;cx.fillRect(0,0,VW,VH);
 if(flashT>0){cx.fillStyle=`rgba(210,220,255,${flashT*1.6})`;cx.fillRect(0,0,VW,VH)}}
function loop(ms){const t=ms/1000,dt=Math.min(.05,t-T1||0);T1=t;if(scareT>0){scareT-=dt;const k=Math.max(0,scareT/scareMax);sx.clearRect(0,0,VW,VH);if(scareT>0){sx.fillStyle=`rgba(${70+Math.random()*100|0},0,0,${.55+.4*k})`;sx.fillRect(0,0,VW,VH);face(sx,VW,VH,k)}else sx.clearRect(0,0,VW,VH)}
 update(dt);draw(t,dt);requestAnimationFrame(loop)}
paintBG();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(paintBG);
reset();menu();requestAnimationFrame(loop);
addEventListener('click',()=>{if(AC)AC.resume()});
</script></body></html>"""

st.markdown("<h1 style='margin-bottom:0'>🔦 ZERO HOUR</h1>", unsafe_allow_html=True)
st.caption("Click inside the game once so the keyboard works. Use headphones. Photos & music: sidebar.")
components.html(GAME.replace("__CONFIG__", cfg), height=height, scrolling=False)

with st.expander("How to play"):
    st.markdown("""
- **Move** WASD / arrows · **Run** Shift · **Aim light** mouse · **Light on/off** F or right-click
- **Interact / hide / continue** E or Space · **Throw flare** G · **Music** M · **Pause** P
- Find **4 proofs** (LOG, CABLE, TRACE, CRED) then accuse at the `!` mark in the hub street. Two wrong accusations lose.
- The shadow thing **freezes while your light is on it**. Hold the beam on it for **2 seconds** and it gets burned away.
- **Flares** make a safe light zone it cannot enter. Candles and lamps give permanent light.
- **Diary pages** (5 hidden) give +3 minutes and +50 score each. Batteries recharge the flashlight.
- Hide in lockers (`H`) when it gets close. Running makes it chase faster.
""")
