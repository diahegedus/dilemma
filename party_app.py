import streamlit as st
import random
import time

st.set_page_config(page_title="Részeg Dzsinn Alkuja", layout="wide")

# Extra CSS az ivós hangulathoz és animációkhoz
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
    .deal-card {
        padding: 30px; border-radius: 25px; min-height: 350px;
        text-align: center; border: 5px solid; transition: 0.3s;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .deal-a { border-color: #00f2ff; background-color: rgba(0, 242, 255, 0.1); }
    .deal-b { border-color: #ff00ff; background-color: rgba(255, 0, 255, 0.1); }
    
    .superpower { font-size: 28px; font-weight: 800; color: #ffffff; margin-bottom: 15px; }
    .curse { font-size: 22px; font-weight: bold; color: #ff4b4b; background: rgba(0,0,0,0.4); padding: 10px; border-radius: 10px; }
    
    .drinking-rule { 
        background: #ff4b4b; color: white; padding: 15px; border-radius: 50px;
        text-align: center; font-weight: bold; font-size: 20px; border: 2px solid white;
    }
    .judge-name { color: gold; font-size: 40px; font-weight: 900; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

# Bővített paklik (több ivós tartalommal)
superpowers = [
    "Minden amit megérintesz, ehető arannyá válik", "Soha nem fogsz másnaposságtól szenvedni", 
    "Bármilyen italt vízzé tudsz változtatni (és fordítva)", "Tudsz olvasni a kutyák gondolataiban",
    "Bármikor elő tudsz varázsolni egy tál meleg náchoz-t", "Ingyen utazol minden járaton örökké",
    "Te vagy a világ legjobb táncosa (még részegen is)", "Mindenki igazat mond neked"
]

curses = [
    "DE minden pohár italodba bele kell öntened egy csepp ecetet",
    "DE csak akkor beszélhetsz, ha közben fogsz egy teli poharat",
    "DE minden vicces mondatod után meg kell innod egy kortyot",
    "DE az összes létező dal szövegét csak 'Donald Kacsa' hangján tudod énekelni",
    "DE minden egyes káromkodás után egy feles a büntetésed",
    "DE csak hátrafelé tudsz közlekedni a lakásban",
    "DE mindenki más poharából kell innod (engedéllyel)",
    "DE csak akkor ülhetsz le, ha valaki más áll"
]

if 'round' not in st.session_state:
    st.session_state.round = 1
    st.session_state.players = ["Játékos 1", "Játékos 2", "Játékos 3", "Játékos 4"]
    st.session_state.current_a = (random.choice(superpowers), random.choice(curses))
    st.session_state.current_b = (random.choice(superpowers), random.choice(curses))
    st.session_state.start_time = time.time()

def refresh_deal():
    st.session_state.round += 1
    st.session_state.current_a = (random.choice(superpowers), random.choice(curses))
    st.session_state.current_b = (random.choice(superpowers), random.choice(curses))
    st.session_state.start_time = time.time()

# --- JÁTÉKMENET ---
st.markdown("<h1 style='text-align:center;'>🥂 RÉSZEG DZSINN ALKUJA 🥂</h1>", unsafe_allow_html=True)

# Bíró sáv
biro_name = st.session_state.players[(st.session_state.round - 1) % 4]
st.markdown(f"<p style='text-align:center;'>A jelenlegi Bíró:</p><p class='judge-name' style='text-align:center;'>{biro_name}</p>", unsafe_allow_html=True)

# Ivós szabály sáv
st.markdown("""
    <div class='drinking-rule'>
        SZABÁLY: Ha a Bíró nem dönt 60 másodpercen belül, MINDENKI ISZIK! ⏱️
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Kártyák megjelenítése
col1, col_vs, col2 = st.columns([4, 1, 4])

with col1:
    st.markdown(f"""<div class='deal-card deal-a'>
        <h2 style='color:#00f2ff;'>🔵 "A" SORS</h2>
        <p class='superpower'>{st.session_state.current_a[0]}</p>
        <p class='curse'>{st.session_state.current_a[1]}</p>
    </div>""", unsafe_allow_html=True)
    if st.button(f"{biro_name} választja: 'A'", use_container_width=True):
        st.balloons()
        refresh_deal()
        st.rerun()

with col_vs:
    st.markdown("<h1 style='text-align:center; margin-top:120px; color:gold;'>VAGY</h1>", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class='deal-card deal-b'>
        <h2 style='color:#ff00ff;'>🟣 "B" SORS</h2>
        <p class='superpower'>{st.session_state.current_b[0]}</p>
        <p class='curse'>{st.session_state.current_b[1]}</p>
    </div>""", unsafe_allow_html=True)
    if st.button(f"{biro_name} választja: 'B'", use_container_width=True):
        st.snow()
        refresh_deal()
        st.rerun()

# --- ALSÓ SZEKCIÓ: VÉLEMÉNYEK ---
st.divider()
st.subheader("📢 A többiek szavazata (Befolyásoljátok a bírót!):")
v_col1, v_col2 = st.columns(2)
with v_col1:
    if st.button("Szerintünk az 'A' a jobb! 👍", key="vote_a"):
        st.warning("Érveljetek! Aki nem tud meggyőző lenni, az iszik egy kortyot!")
with v_col2:
    if st.button("Szerintünk a 'B' a jobb! 👎", key="vote_b"):
        st.warning("Érveljetek! Ha a Bíró mégis az A-t választja, ti isztok!")

# Sidebar beállítások
with st.sidebar:
    st.header("👥 Barátok")
    for i in range(4):
        st.session_state.players[i] = st.text_input(f"{i+1}. Játékos", st.session_state.players[i])
    
    st.divider()
    if st.button("Buli Újratöltése (Reset)"):
        st.session_state.round = 1
        st.rerun()

    st.markdown("""
    **EXTRA IVÓS SZABÁLYOK:**
    - Ha valaki nevet egy átkon, iszik.
    - Ha a Bíró 30 másodpercig nem szólal meg, iszik.
    - Ha valaki kimegy a mosdóba, ivás a büntetése, amikor visszatér.
    """)
