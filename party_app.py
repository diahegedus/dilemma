import streamlit as st
from groq import Groq
import json
import time

# --- OLDAL BEÁLLÍTÁSA ---
st.set_page_config(page_title="Dzsinntelen Kívánságok", layout="wide", initial_sidebar_state="collapsed")

# --- CSS (Design a image_1.png alapján) ---
st.markdown("""
    <style>
    /* Alap beállítások elrejtése */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Háttér: Sötétkék-lila, füstös hangulat */
    .stApp {
        background: radial-gradient(circle at center, #2b1a4e 0%, #1a1233 50%, #0c091f 100%);
        color: white;
        font-family: 'Comic Sans MS', 'Arial', sans-serif; /* Rajzfilmesebb betűtípus */
    }

    /* Cím stílusa (Dzsinntelen Kívánságok logó) */
    .title-text {
        font-size: 60px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to right, #00d4ff, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5), 0 0 20px rgba(255, 0, 255, 0.5);
        margin-bottom: 30px;
    }

    /* Kártyák stílusa: Sötét doboz, neon keret */
    .game-card {
        background: rgba(20, 20, 60, 0.85); /* Sötétkék, áttetsző */
        border-radius: 25px;
        padding: 35px;
        border: 4px solid;
        min-height: 480px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start; /* Balra igazított szöveg, mint a képen */
        text-align: left;
        box-shadow: 0 0 30px rgba(0,0,0,0.7), inset 0 0 50px rgba(0,0,0,0.5);
        transition: transform 0.3s;
    }
    /* "A" kártya kék neon */
    .card-a { border-color: #00d4ff; box-shadow: 0 0 30px rgba(0, 212, 255, 0.4); }
    /* "B" kártya pink neon */
    .card-b { border-color: #ff00ff; box-shadow: 0 0 30px rgba(255, 0, 255, 0.4); }
    
    /* Címkék (Kívánság, Dzsinn) */
    .label {
        font-size: 28px;
        font-weight: bold;
        color: gold; /* Arany színű címkék */
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    /* Szövegek */
    .superpower { font-size: 24px !important; font-weight: normal; margin-bottom: 30px; line-height: 1.4; color: #fff; }
    .curse { font-size: 24px !important; font-weight: normal; color: #fff; line-height: 1.4; }
    
    /* Gombok stílusa */
    .stButton>button {
        border-radius: 50px; font-size: 20px !important; font-weight: bold; width: 100%;
        padding: 15px; background: linear-gradient(to right, #1e1e2e, #2a2a4a); color: white;
        border: 3px solid;
    }
    .stButton>button:hover { filter: brightness(1.2); }
    /* Gomb színek kártyához igazítva */
    .btn-a>button { border-color: #00d4ff; }
    .btn-b>button { border-color: #ff00ff; }
    
    /* VS szöveg */
    .vs-text {
        font-size: 60px; font-weight: 900; color: gold; text-align: center;
        margin-top: 200px; text-shadow: 0 0 20px gold;
    }
    
    /* Sidebar stílus */
    [data-testid="stSidebar"] { background-color: #161625; border-right: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE ---
if 'api_key' not in st.session_state: st.session_state.api_key = None
if 'game_started' not in st.session_state: st.session_state.game_started = False
if 'round' not in st.session_state: st.session_state.round = 1
if 'cards' not in st.session_state: st.session_state.cards = None
if 'mode' not in st.session_state: st.session_state.mode = "Party / Vicces 🤪"

# --- MÓDOK DEFINIÁLÁSA ---
MODES = {
    "Party / Vicces 🤪": {
        "role": "Te egy szarkasztikus, de vicces Dzsinn vagy. A cél a nevetés.",
        "instruct": "Legyenek az opciók abszurdak, viccesek, szilveszteri hangulatúak. Könnyed témák."
    },
    "Mélyvíz / Filozófikus 🤔": {
        "role": "Te egy bölcs, elgondolkodtató Dzsinn vagy. A cél, hogy a játékosok elgondolkodjanak.",
        "instruct": "Az opciók legyenek komolyak. A 'Super' rész legyen egy nagy társadalmi vagy személyes haszon, a 'Curse' pedig egy nehéz morális ár, amit fizetni kell érte. Ne legyen vicces."
    },
    "Kínos / Bevállalós 😳": {
        "role": "Te egy szemtelen, provokátor Dzsinn vagy.",
        "instruct": "Az opciók legyenek társaságban kínosak, titkokat feszegetőek vagy szociálisan nehéz helyzetek. 'Cringe' faktor legyen magas."
    },
    "Sötét Humor 💀": {
        "role": "Te a morbid humorú, gonosz Dzsinn vagy.",
        "instruct": "Az opciók legyenek fekete humorúak, kicsit polgárpukkasztóak, de ne lépjék át a jó ízlés végső határát."
    }
}

# --- GROQ AI GENERÁTOR ---
def get_ai_cards(api_key, mode_key):
    try:
        client = Groq(api_key=api_key)
        selected_mode = MODES[mode_key]
        system_prompt = f"""
        {selected_mode['role']}
        A feladatod a "Would You Rather" játékhoz kártyákat generálni MAGYARUL.
        KIMENET: Szigorúan csak ez a JSON:
        {{ "a_super": "...", "a_curse": "...", "b_super": "...", "b_curse": "..." }}
        """
        user_prompt = f"""
        Generálj 2 választási lehetőséget.
        UTASÍTÁS: {selected_mode['instruct']}
        Fontos: A "super" legyen az előny/képesség, a "curse" a következmény/feltétel.
        """
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.9, max_tokens=300, response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e: return None

# --- 1. LOGIN SCREEN (Marad a régi, de a háttér már új) ---
if not st.session_state.game_started:
    st.markdown("<h1 class='title-text'>🧞‍♂️ DZSINNTELEN KÍVÁNSÁGOK</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box' style='background: rgba(20, 20, 60, 0.85); border: 2px solid #00d4ff;'>", unsafe_allow_html=True)
        key_input = st.text_input("Add meg a Dzsinn kulcsát (Groq API Key):", type="password")
        if st.button("JÁTÉK INDÍTÁSA 🚀", key="login_btn"):
            if key_input.startswith("gsk_"):
                st.session_state.api_key = key_input
                st.session_state.cards = get_ai_cards(key_input, st.session_state.mode)
                if st.session_state.cards:
                    st.session_state.game_started = True
                    st.rerun()
                else: st.error("A Dzsinn nem válaszol. Ellenőrizd a kulcsot!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. GAME SCREEN (Új design) ---
else:
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Dzsinn Beállításai")
        st.write("Milyen kedvében legyen a Dzsinn?")
        new_mode = st.radio("Hangulat", list(MODES.keys()))
        if new_mode != st.session_state.mode:
            st.session_state.mode = new_mode
            st.success(f"Dzsinn hangulata: {new_mode}")
        st.divider()
        if st.button("Kijelentkezés"):
            st.session_state.game_started = False
            st.rerun()

    # Főcím és Dzsinn kép
    col_title, col_img = st.columns([3, 1])
    with col_title:
        st.markdown("<h1 class='title-text'>🧞‍♂️ DZSINNTELEN KÍVÁNSÁGOK</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; opacity: 0.8; color: gold;'>{st.session_state.mode}</h3>", unsafe_allow_html=True)
    with col_img:
        # Egy placeholder kép a Dzsinnről (cserélhető sajátra)
        st.image("https://img.freepik.com/free-vector/genie-lamp-cartoon-character_1308-104635.jpg?w=740&t=st=1703600000~exp=1703600600~hmac=e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0", width=150)

    current = st.session_state.cards
    col1, col_vs, col2 = st.columns([5, 1, 5])
    
    with col1:
        st.markdown(f"""
        <div class='game-card card-a'>
            <div class='label'>Kívánság:</div>
            <div class='superpower'>{current.get('a_super', '...')}</div>
            <div class='label'>Dzsinn:</div>
            <div class='curse'>...de {current.get('a_curse', '...')}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="btn-a">', unsafe_allow_html=True)
        if st.button("EZT A KÍVÁNSÁGOT KÉREM (A)", use_container_width=True):
            st.balloons() if "Vicces" in st.session_state.mode else None
            with st.spinner(f"A Dzsinn gondolkodik ({st.session_state.mode})..."):
                st.session_state.cards = get_ai_cards(st.session_state.api_key, st.session_state.mode)
                st.session_state.round += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_vs:
        st.markdown("<div class='vs-text'>VAGY</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='game-card card-b'>
            <div class='label'>Kívánság:</div>
            <div class='superpower'>{current.get('b_super', '...')}</div>
            <div class='label'>Dzsinn:</div>
            <div class='curse'>...de {current.get('b_curse', '...')}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="btn-b">', unsafe_allow_html=True)
        if st.button("INKÁBB EZT KÉREM (B)", use_container_width=True):
            st.snow() if "Vicces" in st.session_state.mode else None
            with st.spinner(f"A Dzsinn gondolkodik ({st.session_state.mode})..."):
                st.session_state.cards = get_ai_cards(st.session_state.api_key, st.session_state.mode)
                st.session_state.round += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center; color: #888; margin-top: 50px;'>Kör: {st.session_state.round}</p>", unsafe_allow_html=True)
