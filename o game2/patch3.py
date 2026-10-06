"""Run next to app.py:  python patch3.py   (makes app.py.bak3 first)"""
import shutil

src = open("app.py", encoding="utf-8").read()
shutil.copy("app.py", "app.py.bak3")

FS_JS = r"""function toggleFS(){try{const d=document,e=d.documentElement;if(!d.fullscreenElement&&!d.webkitFullscreenElement){const f=e.requestFullscreen||e.webkitRequestFullscreen;const p=f.call(e);if(p&&p.catch)p.catch(()=>say('Fullscreen was blocked here. Try F11 in your browser.',4000))}else{(d.exitFullscreen||d.webkitExitFullscreen).call(d)}}catch(x){say('Fullscreen is not supported here. Try F11 in your browser.',4000)}}
function loop(ms){"""

CSS = r"""st.markdown("<style>.block-container{padding:.5rem 1rem !important;max-width:100% !important}</style>", unsafe_allow_html=True)
st.markdown("<h1 style='margin-bottom:0'>🔦 ZERO HOUR</h1>", unsafe_allow_html=True)"""

EDITS = [
    # fullscreen button in the HUD
    ('<button id="mb" onclick="toggleMute()">♪ Music ON</button>',
     '<button id="mb" onclick="toggleMute()">♪ Music ON</button> '
     '<button id="fsb" onclick="toggleFS()" style="pointer-events:auto;margin-top:4px;padding:3px 9px;font-size:.8rem">⛶ Fullscreen (U)</button>'),
    # fullscreen function
    ("function loop(ms){", FS_JS),
    # U key toggles fullscreen
    ("if(k=='m')toggleMute();", "if(k=='m')toggleMute();if(k=='u')toggleFS();"),
    # bigger game area by default + wide page layout
    ('height = st.slider("Game height (px)", 520, 950, 740, 10)',
     'height = st.slider("Game height (px)", 520, 1600, 900, 10)'),
    ("""st.markdown("<h1 style='margin-bottom:0'>🔦 ZERO HOUR</h1>", unsafe_allow_html=True)""", CSS),
]

for old, new in EDITS:
    assert src.count(old) == 1, f"anchor not found exactly once: {old[:60]}"
    src = src.replace(old, new)

open("app.py", "w", encoding="utf-8").write(src)
print("Patched. Run: streamlit run app.py")
