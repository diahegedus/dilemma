import streamlit as st
from groq import Groq
import json
import time

# --- OLDAL BEÁLLÍTÁSA ---
st.set_page_config(page_title="Szilveszteri Party AI (Groq)", layout="wide", initial_sidebar_state="collapsed")

# --- CSS A MEGJELENÉSHEZ (Profi Neon Design) ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {
        background: radial-gradient(circle, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: white;
    }
    .login-box {
        background: rgba(0, 0, 0, 0.6); padding: 40px; border-radius: 20px;
        border: 2px solid #00d4ff; text-align: center; max-width: 600px;
        margin: 100px auto; box-shadow: 0 0 50px rgba(0, 212, 255, 0.2);
    }
    .game-card {
        background: rgba(255, 255, 255, 0.05); border-radius: 30px; padding: 30px;
        border: 4px solid; min-height: 450px; display: flex; flex-direction: column;
        justify-content: center; align-items: center; text-align: center;
        box-shadow: 0 0 30px rgba(0,0,0,0.7); transition: transform 0.3s;
    }
    .card-a { border-color: #00f2ff; }
    .card-b { border-color: #ff00ff; }
    .superpower { font-size: 32px !important; font-weight: 800; margin-bottom: 25px; line-height: 1.2; color: #fff; }
    .curse { font-size: 24px !important; color: #ff6b6b; font-style: italic; border-top: 2px solid rgba(255,255,255,0.1); padding-top: 20px; }
    .stButton>button {
        border-radius: 50px; font-size: 20px !important; font-weight: bold; width: 100%;
        padding: 15px; background-color: #1e1e2e; color: white; border: 2px solid #555;
    }
    .stButton>button:hover { border-color: white; color: gold; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px; background-color: #1e1e2e; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE KEZELÉS ---
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'cards' not in st.session_state:
    st.session_state.cards = None

# --- GROQ AI FÜGGVÉNY ---
def get_ai_cards(api_key):
    try:
        client = Groq(api_key=api_key)
        
        # Rendszer prompt: Itt állítjuk be, hogy JSON-t adjon és magyarul beszéljen
        system_prompt = """
        Te egy szarkasztikus és vicces party játékmester vagy. A feladatod a "Would You Rather" (Melyiket választanád) játékhoz kártyákat generálni.
        Mindig MAGYARUL válaszolj.
        A kimenetnek szigorúan JSON formátumúnak kell lennie ebben a szerkezetben:
        {
            "a_super": "...",
            "a_curse": "...",
            "b_super": "...",
            "b_curse": "..."
        }
        """

        user_prompt = """
        Generálj két új opciót a játékhoz.
        Szabályok:
        1. Az "A" és "B" opció is tartalmazzon egy szupererőt/jó dolgot (super) és egy idegesítő/vicces átkot (curse).
        2. Legyenek abszurdak, kreatívak és illjenek egy szilveszteri bulihoz.
        3. Ne ismételd a korábbiakat.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Vagy "llama3-70b-8192"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=300,
            response_format={"type": "json_object"} # Ez kényszeríti a JSON-t
        )

        response_content = completion.choices[0].message.content
        return json.loads(response_content)

    except Exception as e:
        # Ha hibás a kulcs vagy a Groq
        return None

# --- 1. KÉPERNYŐ: LOGIN ---
if not st.session_state.game_started:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>⚡ GROQ PARTY LOGIN</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.write("A villámgyors játékhoz add meg a Groq API kulcsot!")
        
        key_input = st.text_input("Groq API Key (gsk_...)", type="password")
        
        if st.button("🚀 INDÍTÁS"):
            if key_input and key_input.startswith("gsk_"):
                st.info("Kapcsolódás a Groq LPU-hoz... ⚡")
                cards = get_ai_cards(key_input)
                
                if cards:
                    st.session_state.api_key = key_input
                    st.session_state.cards = cards
                    st.session_state.game_started = True
                    st.rerun()
                else:
                    st.error("Hiba! A kulcs nem jó, vagy a Groq épp pihen.")
            else:
                st.warning("A Groq kulcsok 'gsk_'-vel kezdődnek!")
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. KÉPERNYŐ: JÁTÉK ---
else:
    st.markdown("<h1 style='text-align: center; font-size: 50px; text-shadow: 0 0 10px #fff;'>🎉 SZILVESZTERI DILEMMA 🎉</h1>", unsafe_allow_html=True)
    
    current_cards = st.session_state.cards
    col1, col_vs, col2 = st.columns([5, 1, 5])
    
    with col1:
        st.markdown(f"""
        <div class='game-card card-a'>
            <h2 style='color: #00f2ff;'>'A' LEHETŐSÉG</h2>
            <div class='superpower'>{current_cards.get('a_super', 'Hiba')}</div>
            <div class='curse'>{current_cards.get('a_curse', 'Hiba')}</div>
        </div>""", unsafe_allow_html=True)
        
        if st.button("EZT VÁLASZTOM (A)", use_container_width=True):
            st.balloons()
            with st.spinner("Generálás..."):
                st.session_state.cards = get_ai_cards(st.session_state.api_key)
                st.session_state.round += 1
            st.rerun()

    with col_vs:
        st.markdown("<div style='font-size: 60px; font-weight: 900; color: gold; text-align: center; margin-top: 180px;'>VS</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='game-card card-b'>
            <h2 style='color: #ff00ff;'>'B' LEHETŐSÉG</h2>
            <div class='superpower'>{current_cards.get('b_super', 'Hiba')}</div>
            <div class='curse'>{current_cards.get('b_curse', 'Hiba')}</div>
        </div>""", unsafe_allow_html=True)
        
        if st.button("INKÁBB EZ (B)", use_container_width=True):
            st.snow()
            with st.spinner("Generálás..."):
                st.session_state.cards = get_ai_cards(st.session_state.api_key)
                st.session_state.round += 1
            st.rerun()

    st.markdown(f"<p style='text-align: center; color: #666; margin-top: 50px;'>Kör: {st.session_state.round} | Powered by Groq LPU</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("Kijelentkezés"):
        st.session_state.game_started = False
        st.session_state.api_key = None
        st.rerun()
