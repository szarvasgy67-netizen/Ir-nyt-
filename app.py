import streamlit as st
import random
from google import genai
from google.genai import types

st.set_page_config(page_title="Bereai Iránytű – Kommunikációs és Határhúzó Szimulátor", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 14px !important;
    }
    [data-testid="stChatMessageContent"] p {
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    h1 {
        font-size: 1.7rem !important;
    }
    h2, h3 {
        font-size: 1.25rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧭 Bereai Iránytű – Dinamikus Szituációs Szimulátor")
st.caption("ApCsel 17:11 mintájára: nyitott, tiszteletteljes meghallgatás, józan vizsgálat és kedves, de kemény határhúzás.")

# --- OLDALSÁV: API KULCS ÉS MODELL ---
st.sidebar.header("🔑 AI Settings")
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("✅ Gemini API Key loaded from Secrets")
else:
    api_key = st.sidebar.text_input("Google Gemini API Key:", type="password")

available_models = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-4-hydrogen"
]


selected_model = st.sidebar.selectbox("🤖 Gemini Modell:", available_models, index=0)

@st.cache_resource
def get_gemini_client(key):
    return genai.Client(api_key=key)

def stream_gemini_fast(prompt, key, preferred_model, fallback_models, temp=0.5):
    models_to_try = [preferred_model, "gemini-3.5-flash-lite"] + [
        m for m in fallback_models if m not in (preferred_model, "gemini-3.5-flash-lite")
    ]
    cfg = types.GenerateContentConfig(temperature=temp)
    client = get_gemini_client(key)
    last_error = None
    for model_name in models_to_try:
        try:
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=prompt,
                config=cfg
            )
            iterator = iter(response_stream)
            first_chunk = next(iterator)

            def text_generator(first=first_chunk, it=iterator):
                if first and first.text:
                    yield first.text
                for chunk in it:
                    if chunk.text:
                        yield chunk.text

            return text_generator(), model_name
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"Minden Gemini modell hibát adott: {last_error}")

def generate_new_scenario(category, key, preferred_model, fallback_models):
    seed = random.randint(1000, 99999)
    models_to_try = ["gemini-3.5-flash-lite", preferred_model] + [
        m for m in fallback_models if m not in ("gemini-3.5-flash-lite", preferred_model)
    ]
    cfg = types.GenerateContentConfig(temperature=0.95)
    
    gen_prompt = f"""
    Készíts egy életszerű, valós magyar élethelyzetet (mag: {seed}) a bereai típusú keresztény kommunikáció (nyitott meghallgatás, józan vizsgálat, kedves de kemény határhúzás) tesztelésére.
    Témakör: {category}.
    
    SZIGORÚ SZEREPOSZTÁS:
    - A Felhasználó MINDIG saját maga (egy józan keresztény hívő). NE adj neki kitalált nevet!
    - Az AI MINDIG a másik fél (pl. kolléga, rokon, gyülekezeti tag, vezető, ismerős), aki megszólítja a Felhasználót.
    
    Válaszolj PONTOSAN ebben az 5 elemű formátumban, '|||' jellel elválasztva, sortörések nélkül:
    CÍM ||| HELYZETKÉP (2 mondat arról, hol vagy és ki szólít meg téged) ||| AI KARAKTERE (pl. Te Péter vagy, az ifjúsági vezető. Így viselkedsz...) ||| AI REJTETT MOTIVÁCIÓJA (1 mondat) ||| AI NYITÓMONDATA (amivel megszólítja a Felhasználót)
    """
    
    client = get_gemini_client(key)
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=gen_prompt,
                config=cfg
            )
            parts = [p.strip() for p in response.text.split("|||")]
            if len(parts) >= 5:
                return {
                    "title": parts,
                    "context": parts,
                    "persona_prompt": parts,
                    "hidden_motivation": parts,
                    "opening_line": parts.strip('"')
                }
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"Nem sikerült generálni: {last_error}")
BEREA_EVAL_CRITERIA = """
MI A BEREAI GYÜLEKEZETI MINTA ALAPELVE (ApCsel 17:11)?
1. **Készséges, nyitott meghallgatás:** Nem előítéletes, nem támad azonnal, tisztelettel és emberi méltósággal hallgatja meg a másikat.
2. **Kritikus, józan vizsgálat:** Nem hisz el mindent vakon, nem hatódik meg a kenetteljes, tekintélyelvű vagy érzelmi zsaroló frázisoktól, hanem józan ésszel és a Szentírás mérlegén vizsgál meg minden állítást.
3. **Kedves, de kőkemény határhúzás:** Kerüli a mézesmázos képmutatást és alakoskodást. Nem személyeskedik, de szelíd, egyenes, megalkuvás nélküli határokat húz ('igen-igen, nem-nem').
"""

def run_evaluation(scen, messages, key, pref_model, fallbacks):
    transcript = "\n".join(
        [f"{'Másik fél' if m['role']=='assistant' else 'Te'}: {m['content']}" for m in messages]
    )
    eval_prompt = f"""
    Értékeld a felhasználó ('Te') teljesítményét az alábbi szituációs gyakorlatban a **BEREAI GYÜLEKEZETI MINTA** alapján!
    {BEREA_EVAL_CRITERIA}

    HELYZET: {scen['context']}
    A MÁSIK FÉL REJTETT MOTIVÁCIÓJA (amit a felhasználó nem tudott): {scen['hidden_motivation']}

    BESZÉLGETÉS:
    {transcript}

    Add meg az értékelést az alábbi bontásban (tömören, őszintén, mindenféle vallásos maszlag és alakoskodás nélkül):
    1. **Bereai mérleg (A lepel lehull):** Mennyire sikerült egyszerre nyitottnak maradni, ugyanakkor józanul megvizsgálni a másik fél szándékát és átlátni a manipuláción?
    2. **4 bereai pillér pontozása (1-10 skála + 1 mondat indoklás):**
       - **Nyitott & Tiszteletteljes Meghallgatás** (ítélkezésmentes, emberi odafordulás)
       - **Józan Vizsgálat & Kritikai Tisztánlátás** (nem dől be érzelmi/lelki nyomásnak, tényeket és bibliai alapot kér)
       - **Kedves, de Kemény Határhúzás** (határozott, megalkuvás nélküli kiállás személyeskedés nélkül)
       - **Álarc nélküli Őszinteség** (képmutatás-mentes, egyenes beszéd a művi udvariaskodás helyett)
    3. **Bereai válasz-alternatíva:** 2 konkrét, természetes, egyenes magyar mondat (TILOS a kenetteljes zsargon!), amivel még higgadtabban és szilárdabban lehetett volna meghúzni a határt.
    """
    stream_gen, _ = stream_gemini_fast(eval_prompt, key, pref_model, fallbacks, temp=0.3)
    return "".join(list(stream_gen))

# --- OLDALSÁV: MÓDVÁLASZTÁS ÉS VEZÉRLŐGOMBOK ---
st.sidebar.divider()
mode = st.sidebar.radio(
    "🎯 Mód kiválasztása:",
    ["🎲 Dinamikus Szimulátor (Élő szerepjáték)", "📋 Saját beszélgetés elemzése"]
)

if mode == "🎲 Dinamikus Szimulátor (Élő szerepjáték)":
    category = st.sidebar.selectbox(
        "🌍 Élethelyzet témaköre:",
        [
            "Teljesen véletlenszerű valós élethelyzet",
            "Gyülekezeti / közösségi konfliktusok és manipuláció",
            "Munkahelyi / egyetemi világnézeti viták",
            "Családi és baráti határok, érzelmi zsarolás",
            "Pénzügyi segítségkérés és kodependencia csapdái"
        ]
    )

    if st.sidebar.button("✨ Új véletlen szituáció generálása", type="primary"):
        if not api_key:
            st.sidebar.error("Előbb add meg az API kulcsot!")
        else:
            with st.spinner("Új valós élethelyzet felépítése..."):
                try:
                    new_scen = generate_new_scenario(category, api_key, selected_model, available_models)
                    st.session_state["dyn_scenario"] = new_scen
                    st.session_state["rk_messages"] = [{"role": "assistant", "content": new_scen["opening_line"]}]
                    st.session_state.pop("rk_eval", None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Hiba a generáláskor: {e}")

    if len(st.session_state.get("rk_messages", [])) >= 2 and "dyn_scenario" in st.session_state:
        if st.sidebar.button("⚖️ Beszélgetés kiértékelése MOST"):
            with st.spinner("Bereai elemzés készül..."):
                try:
                    st.session_state["rk_eval"] = run_evaluation(
                        st.session_state["dyn_scenario"],
                        st.session_state["rk_messages"],
                        api_key,
                        selected_model,
                        available_models
                    )
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Hiba az értékeléskor: {e}")

# --- 1. MÓD: DINAMIKUS SZIMULÁTOR ---
if mode == "🎲 Dinamikus Szimulátor (Élő szerepjáték)":
    if not api_key:
        st.warning("👈 Add meg a Google Gemini API kulcsodat az oldalsávon az indításhoz!")
        st.stop()

    if "dyn_scenario" not in st.session_state:
        with st.spinner("Első élő szituáció generálása..."):
            try:
                new_scen = generate_new_scenario(category, api_key, selected_model, available_models)
                st.session_state["dyn_scenario"] = new_scen
                st.session_state["rk_messages"] = [{"role": "assistant", "content": new_scen["opening_line"]}]
            except Exception as e:
                st.error(f"Hiba: {e}")
                st.stop()

    scen = st.session_state["dyn_scenario"]

    st.subheader(f"🎭 {scen['title']}")
    st.info(f"**Helyzetkép:** {scen['context']}")
    st.caption("⚠️ *A másik fél valódi szándékát nem ismered. Hallgasd meg nyitottan, vizsgáld meg józanul, és húzz tiszta határokat!*")

    for msg in st.session_state["rk_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if "rk_eval" in st.session_state:
        st.divider()
        st.markdown("### 📊 Bereai Kiértékelés")
        st.markdown(st.session_state["rk_eval"])
        with st.expander("🔍 Eredeti karakterleírás és rejtett motiváció megtekintése"):
            st.write(f"**Rejtett motiváció:** {scen['hidden_motivation']}")
            st.write(f"**Karakterleírás:** {scen['persona_prompt']}")

    if user_input := st.chat_input("Írd le, mit mondasz vagy hogyan reagálsz..."):
        st.session_state["rk_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        history_text = "\n".join(
            [f"{'Másik fél' if m['role']=='assistant' else 'Felhasználó'}: {m['content']}" for m in st.session_state["rk_messages"]]
        )
        roleplay_prompt = f"""
        Szerepjátékot játszol. Te KIZÁRÓLAG a másik fél szerepét játszod, SOHA nem beszélhetsz a Felhasználó nevében és nem írhatsz választ helyette!
        
        HELYZET: {scen['context']}
        A TE KARAKTERED (AI): {scen['persona_prompt']}
        A TE REJTETT MOTIVÁCIÓD: {scen['hidden_motivation']}

        EDDIGI BESZÉLGETÉS:
        {history_text}

        Írd meg KIZÁRÓLAG a te karaktered következő 2-3 mondatos reakcióját a Felhasználó utolsó mondatára:
        """

        with st.chat_message("assistant"):
            try:
                stream_gen, _ = stream_gemini_fast(roleplay_prompt, api_key, selected_model, available_models, temp=0.7)
                full_reply = st.write_stream(stream_gen)
                st.session_state["rk_messages"].append({"role": "assistant", "content": full_reply})
                st.rerun()
            except Exception as e:
                st.error(f"Hiba a válaszadáskor: {e}")

# --- 2. MÓD: SAJÁT BESZÉLGETÉS ELEMZÉSE ---
else:
    st.subheader("📋 Valós beszélgetés bereai kiértékelése")
    st.info("Másold be egy megtörtént beszélgetésedet (pl. Messenger, e-mail, gyülekezeti vagy családi vita), és az AI elemzi a Bereai Minta (nyitott meghallgatás, józan vizsgálat, kedves de kemény határhúzás) alapján.")
    user_transcript = st.text_area("Másold be ide a beszélgetés szövegét:", height=220, placeholder="Én: ...\nMásik fél: ...")

    if st.button("⚖️ Kiértékelés a Bereai Minta alapján", type="primary"):
        if not api_key:
            st.error("Add meg a Gemini API kulcsot az oldalsávon!")
        elif not user_transcript.strip():
            st.warning("Írj vagy másolj be egy beszélgetést!")
        else:
            eval_prompt = f"""
            Elemezd tömören, lényegretörően az alábbi beszélgetést a **BEREAI GYÜLEKEZETI MINTA** alapján!
            {BEREA_EVAL_CRITERIA}

            Értékeld 1-10 skálán és 1-2 mondattal indokold ezt a 4 bereai pillért:
            1. **Nyitott & Tiszteletteljes Meghallgatás** (ítélkezésmentes, emberi odafordulás)
            2. **Józan Vizsgálat & Kritikai Tisztánlátás** (nem dől be érzelmi/lelki nyomásnak, tényeket és bibliai alapot kér)
            3. **Kedves, de Kemény Határhúzás** (határozott, megalkuvás nélküli kiállás személyeskedés nélkül)
            4. **Álarc nélküli Őszinteség** (képmutatás-mentes, egyenes beszéd a művi udvariaskodás helyett)

            Adj a végén 2-3 konkrét, természetes, egyenes magyar mondatot (TILOS a kenetteljes zsargon!), hogyan lehetett volna még higgadtabban és szilárdabban meghúzni a határt!

            Beszélgetés:
            {user_transcript}
            """
            try:
                stream_gen, model_used = stream_gemini_fast(eval_prompt, api_key, selected_model, available_models, temp=0.3)
                st.caption(f"⚡ Bereai villámelemzés ezzel a modellel: `{model_used}`")
                st.write_stream(stream_gen)
            except Exception as e:
                st.error(f"Elemzési hiba: {e}")
