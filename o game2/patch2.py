"""Run next to app.py:  python patch2.py   (makes app.py.bak2 first)"""
import shutil

src = open("app.py", encoding="utf-8").read()
shutil.copy("app.py", "app.py.bak2")

NEW_JS = r"""let briefed=false,callT=30;
const CALLS=[`Darling... I can see you. Why are you so tense?`,`Don't run, darling. I like it when you run.`,`You look tired, detective. Come into the light... if you dare.`,`Behind you, darling. No, not that way. The other way.`,`Tick tock, darling. Ninety minutes was generous.`];
const BRIEF_SPEECH=`Detective. The city has been dark for ninety minutes. Find four proofs, then accuse the culprit. Move with W A S D. Aim your flashlight with the mouse. Press E to inspect, hide, or continue. F toggles the light. G throws a flare. Hold your light on the shadow for two seconds to burn it away. Solve the riddles for bonus time. Press Q if you are stuck. And if the phone rings... you do not have to answer. Good luck.`;
const BRIEF_HTML=`<h2>BRIEFING</h2><p>The city went dark 90 minutes ago. <b>Find 4 proofs</b>, then make the accusation at the <b>!</b> mark in the hub street.</p><p><b>WASD</b> move · <b>Shift</b> run · <b>Mouse</b> aim light · <b>E</b> inspect / hide / continue<br><b>F</b> light on/off · <b>G</b> throw flare · <b>Q</b> hint (-1 min) · <b>P</b> pause</p><p>A shadow hunts you. It <b>freezes in your light</b>; hold the beam on it for <b>2 seconds</b> to burn it away. Solve the <b>?</b> riddles for bonus time and supplies. If the phone rings... you do not have to answer.</p><button class="w" onclick="go()">I am ready</button>`;
function speak(t,p=1,r=.92){try{if(muted||!window.speechSynthesis)return;speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.pitch=p;u.rate=r;const f=speechSynthesis.getVoices().find(x=>/female|zira|samantha|hazel|google uk english female/i.test(x.name));if(f)u.voice=f;speechSynthesis.speak(u)}catch(e){}}
function phone(){ring();say('A phone is ringing somewhere close...',2500);setTimeout(()=>{if(st!='play')return;const t=CALLS[Math.random()*CALLS.length|0];say('📞 <b>Unknown caller</b><br><i>'+t+'</i>',7000);speak(t,.55,.8);flashT=.15;if(Math.random()<.5)g.black=1.5},2600)}
function askPz(it){st='key';ov(`<h2>${it.n}</h2><p>${it.pz[0]}</p><input id="cd" maxlength="24" style="font-size:1.2rem;letter-spacing:.1em" placeholder="your answer" onkeydown="if(event.key=='Enter')solvePz('${it.id}')"><button class="w" onclick="solvePz('${it.id}')">Answer</button><button class="w" onclick="ov('');st='play'">Leave it</button>`);setTimeout(()=>$('#cd').focus(),50)}
function solvePz(id){const it=items.find(x=>x.id==id);const a=($('#cd').value||'').trim().toLowerCase().replace(/^(an?|the)\s+/,'');ov('');st='play';if([].concat(it.pz[1]).includes(a)){it.done=true;g.pz=(g.pz||0)+1;g.m=Math.min(90,g.m+it.pz[2]);g.flare+=it.pz[3];g.bat=Math.min(100,g.bat+it.pz[4]);beep(660,.2,.15);beep(990,.3,.12);beep(1320,.4,.1);say('Solved! +'+it.pz[2]+' min, +'+it.pz[3]+' flare, +'+it.pz[4]+'% battery.',5000)}else{g.m-=1;shake=.5;beep(110,.4,.3,'sawtooth');say('Wrong. The dark shifts around you. -1 minute.')}}
function loop(ms){"""

NEW_ITEMS = r"""I('chart',1900,300,'F','Patient files','Eleven patient charts, all stamped <b>"survivor - do not discharge"</b>. The tunnel collapse survivors were kept quiet here. Someone paid for their silence.'),
 I('smap',2300,780,'M','Sewer map','A hand-drawn map. A red line leads from this sewer straight under the Central Grid Station. Whoever cut the power knew these tunnels.',{sc:1}),
 I('pz1',2100,150,'?','Whispering mirror','',{pz:['A cracked mirror writes in the fog: <i>"I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?"</i>',['echo'],5,0,25]}),
 I('pz2',2100,950,'?','Pipe valve lock','',{pz:['Rusty numbers are scratched on the valve: <b>2, 6, 12, 20, ?</b> Enter the next number.',['30'],3,2,30]}),
 I('pz3',600,550,'?','Chalk scrawl','',{pz:['Chalk on the wall: <i>"The more of me you take, the more you leave behind. What am I?"</i>',['footsteps','footstep','steps','step'],2,1,20]}),
 I('pz4',750,800,'?','Star lock','',{pz:['A brass lock under the telescope: <i>"I have cities but no houses, forests but no trees, and water but no fish. What am I?"</i>',['map','a map'],3,1,20]}),
 I('b4',2300,300,'+','Battery','',{bat:1}),I('b5',1900,1040,'+','Battery','',{bat:1}),
 I('f3',2250,120,'*','Flare','',{flr:1}),I('f4',2300,1000,'*','Flare','',{flr:1}),
 I('h6',1830,350,'H','Hide','',{hide:1}),I('h7',2340,1050,'H','Hide','',{hide:1}),
 I('acc',900,550,'!','Make the accusation','',{hid:1})];"""

PAINTERS = r"""hospital(x,y,w,h){g.fillStyle='#1f2e2c';g.fillRect(x,y,w,h);g.strokeStyle='rgba(255,255,255,.05)';for(let i=0;i<w;i+=50){g.beginPath();g.moveTo(x+i,y);g.lineTo(x+i,y+h);g.stroke()}[50,230,410].forEach(a=>{box(x+a,y+70,110,48,'#c9d3cf');box(x+a,y+290,110,48,'#c9d3cf');g.fillStyle='rgba(120,0,0,.45)';g.fillRect(x+a+20,y+78,40,22)});g.fillStyle='rgba(255,60,60,.5)';g.fillRect(x+w/2-4,y+170,8,40);g.fillRect(x+w/2-20,y+186,40,8)},
  sewer(x,y,w,h){g.fillStyle='#14231f';g.fillRect(x,y,w,h);g.fillStyle='rgba(40,120,95,.35)';g.fillRect(x+30,y+160,w-60,100);g.strokeStyle='#4a5b55';g.lineWidth=10;[70,330].forEach(b=>{g.beginPath();g.moveTo(x,y+b);g.lineTo(x+w,y+b);g.stroke()});g.lineWidth=1;for(let i=0;i<w;i+=60)box(x+i,y+60,8,280,'rgba(90,110,100,.25)');box(x+w/2-60,y+h-70,120,16,'#3a4a44')},
  metro(x,y,w,h){g.fillStyle='#1b2a3a';"""

EDITS = [
    # bigger world + 2 new rooms
    ("const WW=1800,WH=1100,T=16,", "const WW=2400,WH=1100,T=16,"),
    ("['CENTRAL GRID STATION',900,700,900,400,'grid','t']];",
     "['CENTRAL GRID STATION',900,700,900,400,'grid','t'],['HOSPITAL WARD',1800,0,600,400,'hospital','b'],['SEWER JUNCTION',1800,700,600,400,'sewer','t']];"),
    ("[1330,820,200,'r']);",
     "[1330,820,200,'r']);LAMPS.push([1860,60,190,'g'],[2240,340,190,'g'],[1860,780,190,'b'],[2290,1040,200,'g'],[2100,200,170,'w']);"),
    ("metro(x,y,w,h){g.fillStyle='#1b2a3a';", PAINTERS),
    ('("grid", "Central Grid Station")]',
     '("grid", "Central Grid Station"),\n         ("hospital", "Hospital Ward"), ("sewer", "Sewer Junction")]'),
    # items, riddles, score
    ("I('acc',900,550,'!','Make the accusation','',{hid:1})];", NEW_ITEMS),
    ("const nd=NEED[i];", "if(it.pz)return askPz(it);const nd=NEED[i];"),
    ("g.pages*50),rk=", "g.pages*50+(g.pz||0)*75),rk="),
    # helpers (briefing, speech, phone, puzzles)
    ("function loop(ms){", NEW_JS),
    # spoken briefing on first start
    ("function start(){initAudio();reset();st='play';ov('');say(",
     "function start(){initAudio();reset();if(!briefed){briefed=true;st='dlg';run2=0;ov(BRIEF_HTML);speak(BRIEF_SPEECH);return}go()}\n"
     "function go(){try{speechSynthesis.cancel()}catch(e){}callT=25;st='play';ov('');say("),
    # phone calls
    ("else if(r<.8){ring();say('A phone rings somewhere nearby...')}", "else if(r<.8){phone()}"),
    ("ambT-=dt;if(ambT<=0){",
     "callT-=dt;if(callT<=0){callT=40+Math.random()*35;if(!g.hid)phone()}ambT-=dt;if(ambT<=0){"),
]

for old, new in EDITS:
    assert src.count(old) == 1, f"anchor not found exactly once: {old[:60]}"
    src = src.replace(old, new)

open("app.py", "w", encoding="utf-8").write(src)
print("Patched. Run: streamlit run app.py")
