import streamlit as st
import google.generativeai as genai
import json
import time

# --- OLDAL BEÁLLÍTÁSA ---
st.set_page_config(page_title="Szilveszteri Party AI", layout="wide", initial_sidebar_state="collapsed")

# --- CSS A MEGJELENÉSHEZ ---
st.markdown("""
    <style>
    /* Alap beállítások elrejtése */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Háttér és színek */
    .stApp {
        background: radial-gradient(circle, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: white;
    }

    /* Bejelentkezési doboz stílusa */
    .login-box {
        background: rgba(0, 0, 0, 0.6);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #00d4ff;
        text-align: center;
        max-width: 600px;
        margin: 100px auto;
        box-shadow: 0 0 50px rgba(0, 212, 255, 0.2);
    }

    /* Kártyák stílusa */
    .game-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 30px;
        padding: 30px;
        border: 4px solid;
        min-height: 450px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 0 30px rgba(0,0,0,0.7);
        transition: transform 0.3s;
    }
    .card-a { border-color: #00f2ff; }
    .card-b { border-color: #ff00ff; }
    
    .superpower { font-size: 32px !important; font-weight: 800; margin-bottom: 25px; line-height: 1.2; color: #fff; }
    .curse { font-size: 24px !important; color: #ff6b6b; font-style: italic; border-top: 2px solid rgba(255,255,255,0.1); padding-top: 20px; }
    
    /* Gombok */
    .stButton>button {
        border-radius: 50px;
        font-size: 20px !important;
        font-weight: bold;
        width: 100%;
        padding: 15px;
        background-color: #1e1e2e;
        color: white;
        border: 2px solid #555;
    }
    .stButton>button:hover { border-color: white; color: gold; }
    
    /* Input mező */
    .stTextInput>div>div>input {
        text-align: center;
        font-size: 20px;
        background-color: #1e1e2e;
        color: white;
        border-radius: 10px;
    }
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

# --- AI FÜGGVÉNY ---
def get_ai_cards(api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Készíts egy vicces "Melyiket választanád?" party játékhoz 2 opciót.
    Az opciók legyenek abszurdak, viccesek és szilveszteri hangulatúak.
    
    Formátum (csak ezt a JSON-t add vissza):
    {"a_super": "Pozitív dolog A", "a_curse": "Negatív következmény A", "b_super": "Pozitív dolog B", "b_curse": "Negatív következmény B"}
    
    Példa stílus: "Tudsz repülni" DE "Csak hátrafelé". Legyen magyar nyelvű.
    """
    
    try:
        response = model.generate_content(prompt)
        # JSON tisztítása (ha az AI véletlenül markdownba tenné)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        return None

# --- 1. KÉPERNYŐ: BEJELENTKEZÉS (KULCS MEGADÁSA) ---
if not st.session_state.game_started:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🔐 PARTY LOCKDOWN</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.write("A játék indításához add meg a Dzsinn (Gemini) kulcsát!")
        
        # Jelszó mező a kulcsnak
        key_input = st.text_input("Illeszd ide az API kulcsot:", type="password")
        
        if st.button("🚀 MEHET A BULI"):
            if key_input and len(key_input) > 20:
                # Teszteljük a kulcsot egy gyors generálással
                st.info("Kapcsolódás a műholdhoz... 📡")
                cards = get_ai_cards(key_input)
                
                if cards:
                    st.session_state.api_key = key_input
                    st.session_state.cards = cards
                    st.session_state.game_started = True
                    st.rerun()
                else:
                    st.error("Hoppá! Ez a kulcs nem nyitja a kaput. Próbáld újra!")
            else:
                st.warning("Kérlek adj meg egy érvényes kulcsot!")
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. KÉPERNYŐ: A JÁTÉK ---
else:
    st.markdown("<h1 style='text-align: center; font-size: 50px; text-shadow: 0 0 10px #fff;'>🎉 SZILVESZTERI DILEMMA 🎉</h1>", unsafe_allow_html=True)
    
    # Kártyák megjelenítése
    col1, col_vs, col2 = st.columns([5, 1, 5])
    
    current_cards = st.session_state.cards
    
    with col1:
        st.markdown(f"""
        <div class='game-card card-a'>
            <h2 style='color: #00f2ff;'>'A' LEHETŐSÉG</h2>
            <div class='superpower'>{current_cards['a_super']}</div>
            <div class='curse'>{current_cards['a_curse']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("EZT VÁLASZTOM (A)", use_container_width=True):
            st.balloons()
            with st.spinner("A következő kör betöltése..."):
                st.session_state.cards = get_ai_cards(st.session_state.api_key)
                st.session_state.round += 1
            st.rerun()

    with col_vs:
        st.markdown("<div style='font-size: 60px; font-weight: 900; color: gold; text-align: center; margin-top: 180px;'>VS</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='game-card card-b'>
            <h2 style='color: #ff00ff;'>'B' LEHETŐSÉG</h2>
            <div class='superpower'>{current_cards['b_super']}</div>
            <div class='curse'>{current_cards['b_curse']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("INKÁBB EZ (B)", use_container_width=True):
            st.snow()
            with st.spinner("A következő kör betöltése..."):
                st.session_state.cards = get_ai_cards(st.session_state.api_key)
                st.session_state.round += 1
            st.rerun()

    # Footer infó
    st.markdown(f"<p style='text-align: center; color: #666; margin-top: 50px;'>Kör: {st.session_state.round} | AI Powered Party</p>", unsafe_allow_html=True)
    
    # Kilépés gomb (ha újra meg akarod adni a kulcsot)
    if st.sidebar.button("Kulcs törlése és Kilépés"):
        st.session_state.game_started = False
        st.session_state.api_key = None
        st.rerun()
