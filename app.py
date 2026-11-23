import streamlit as st
import json
import random
from google import genai
from google.genai import types

st.set_page_config(page_title="Kegyelem & Igazság – Dinamikus Szimulátor", layout="wide")
st.title("🧭 Kegyelem & Igazság – Dinamikus Szituációs Szimulátor")
st.caption("Minden körben új, valós élethelyzeteken alapuló próbatétel: nyitott befogadás, bibliai iránytű és józan határok.")

# --- OLDALSÁV: API KULCS ÉS MODELL ---
st.sidebar.header("🔑 AI Settings")
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("✅ Gemini API Key loaded from Secrets")
else:
    api_key = st.sidebar.text_input("Google Gemini API Key:", type="password")

available_models = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-4-hydrogen"
]


selected_model = st.sidebar.selectbox("🤖 Gemini Modell:", available_models, index=0)

@st.cache_resource
def get_gemini_client(key):
    return genai.Client(api_key=key)

def call_gemini_json(prompt, key, preferred_model, fallback_models):
    """Új, strukturált szituáció generálása JSON formátumban."""
    models_to_try = [preferred_model] + [m for m in fallback_models if m != preferred_model]
    cfg = types.GenerateContentConfig(
        temperature=0.95,
        response_mime_type="application/json"
    )
    client = get_gemini_client(key)
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=cfg
            )
            return json.loads(response.text)
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"Nem sikerült új szituációt generálni: {last_error}")

def stream_gemini_fast(prompt, key, preferred_model, fallback_models, temp=0.5):
    models_to_try = ["gemini-3.5-flash-lite", preferred_model] + [
        m for m in fallback_models if m not in ("gemini-3.5-flash-lite", preferred_model)
    ]
    cfg = types.GenerateContentConfig(
        temperature=temp,
        thinking_config=types.ThinkingConfig(thinking_level="minimal")
    )
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
    # A leggyorsabb lite modellel indítunk a villámgyors generálásért
    models_to_try = ["gemini-3.5-flash-lite", preferred_model] + [
        m for m in fallback_models if m not in ("gemini-3.5-flash-lite", preferred_model)
    ]
    
    cfg = types.GenerateContentConfig(
        temperature=0.95,
        thinking_config=types.ThinkingConfig(thinking_level="minimal")
    )
    
    gen_prompt = f"""
    Készíts egy életszerű, feszült, valós magyar élethelyzetet (mag: {seed}) a keresztény kommunikáció (Kegyelem, Igazság, Határhúzás) tesztelésére.
    Témakör: {category}.
    
    Válaszolj PONTOSAN ebben az 5 soros formátumban, '|||' jellel elválasztva (ne írj elé és mögé semmi mást):
    CÍM ||| HELYZETKÉP (2 mondat) ||| SZEREPINSTRUKCIÓ AZ AI-NAK ||| REJTETT MOTIVÁCIÓ (1 mondat) ||| NYITÓMONDAT
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
                    "title": parts[0],
                    "context": parts[1],
                    "persona_prompt": parts[2],
                    "hidden_motivation": parts[3],
                    "opening_line": parts[4]
                }
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"Nem sikerült generálni: {last_error}")

# --- OLDALSÁV: MÓDVÁLASZTÁS ---
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
    st.caption("⚠️ *A másik fél valódi szándékát nem ismered. Figyeld a jeleket, kérdezz okosan, és tartsd meg az egyensúlyt!*")

    for msg in st.session_state["rk_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Írd le, mit mondasz vagy hogyan reagálsz..."):
        st.session_state["rk_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        history_text = "\n".join(
            [f"{'Másik fél' if m['role']=='assistant' else 'Felhasználó'}: {m['content']}" for m in st.session_state["rk_messages"]]
        )
        roleplay_prompt = f"""
        Szerepjátékot játszol. Maradj végig 100%-ban a karakteredben! Ne adj tanácsot, ne lépj ki a szerepből!
        
        HELYZET: {scen['context']}
        KARAKTERED ÉS SZABÁLYAID: {scen['persona_prompt']}
        REJTETT MOTIVÁCIÓD: {scen['hidden_motivation']}

        EDDIGI BESZÉLGETÉS:
        {history_text}

        Reagálj természetesen, életszerűen (2-4 mondatban) a Felhasználó utolsó megszólalására a karaktered személyisége és rejtett motivációja alapján:
        """

        with st.chat_message("assistant"):
            try:
                stream_gen, _ = stream_gemini_fast(roleplay_prompt, api_key, selected_model, available_models, temp=0.7)
                full_reply = st.write_stream(stream_gen)
                st.session_state["rk_messages"].append({"role": "assistant", "content": full_reply})
            except Exception as e:
                st.error(f"Hiba a válaszadáskor: {e}")

    if len(st.session_state["rk_messages"]) >= 3:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚖️ Beszélgetés lezárása és kiértékelése", type="primary"):
                transcript = "\n".join(
                    [f"{'Másik fél' if m['role']=='assistant' else 'Te'}: {m['content']}" for m in st.session_state["rk_messages"]]
                )
                eval_prompt = f"""
                Értékeld a felhasználó ('Te') teljesítményét az alábbi szituációs gyakorlatban!
                
                HELYZET: {scen['context']}
                A MÁSIK FÉL REJTETT MOTIVÁCIÓJA (amit a felhasználó nem tudott): {scen['hidden_motivation']}

                BESZÉLGETÉS:
                {transcript}

                Add meg az értékelést az alábbi bontásban (tömören, őszintén, építően):
                1. **A lepel lehull:** Hogyan reagált a felhasználó a másik fél rejtett motivációjára? Átlátott-e rajta, vagy csapdába esett?
                2. **4 pilléres pontozás (1-10 skála + 1 mondat indoklás):**
                   - Kegyelem & Emberi Méltóság
                   - Igazság & Bibliai Hűség
                   - Határhúzás & 'Kígyó-okosság'
                   - Kommunikációs Bölcsesség
                3. **Fejlesztési javaslat:** 2 konkrét mondat, amivel még bölcsebben kezelhette volna a helyzetet.
                """
                with st.spinner("Elemzés készül..."):
                    stream_gen, _ = stream_gemini_fast(eval_prompt, api_key, selected_model, available_models, temp=0.3)
                    st.session_state["rk_eval"] = "".join(list(stream_gen))

        if "rk_eval" in st.session_state:
            st.markdown("### 📊 Szimulációs Kiértékelés")
            st.markdown(st.session_state["rk_eval"])
            with st.expander("🔍 Eredeti karakterleírás és rejtett motiváció megtekintése"):
                st.write(f"**Rejtett motiváció:** {scen['hidden_motivation']}")
                st.write(f"**Karakterleírás:** {scen['persona_prompt']}")

# --- 2. MÓD: SAJÁT BESZÉLGETÉS ELEMZÉSE ---
else:
    st.subheader("📋 Valós beszélgetés kiértékelése")
    st.info("Másold be egy megtörtént beszélgetésedet (pl. Messenger, e-mail, gyülekezeti vagy családi vita), és az AI elemzi a Kegyelem, Igazság, Határhúzás és Kodependencia szempontjából.")
    user_transcript = st.text_area("Másold be ide a beszélgetés szövegét:", height=220, placeholder="Én: ...\nMásik fél: ...")

    if st.button("⚖️ Kiértékelés a 4 pillér alapján", type="primary"):
        if not api_key:
            st.error("Add meg a Gemini API kulcsot az oldalsávon!")
        elif not user_transcript.strip():
            st.warning("Írj vagy másolj be egy beszélgetést!")
        else:
            eval_prompt = f"""
            Elemezd tömören, lényegretörően az alábbi beszélgetést a 'Kegyelem & Igazság – Emberi Határhúzás' modell alapján!
            Ne feledd: az ember nem lát a másik szívébe, ezért a szeretet mellé józan határok és pszichológiai tisztánlátás is kell.

            Értékeld 1-10 skálán és 1-2 mondattal indokold ezt a 4 tengelyt:
            1. **Kegyelem & Emberi Méltóság** (ítélkezésmentes tisztelet, előítélet-mentesség)
            2. **Igazság & Bibliai Hűség** (nem relativizálja az értékrendjét, nem hódol be)
            3. **Határhúzás & 'Kígyó-okosság'** (felismeri-e a manipulációt, nem esik-e kodependens 'Megmentő' szerepbe)
            4. **Kommunikációs Bölcsesség** (kérdező, szelíd attitűd kioktatás helyett)

            Adj a végén 2-3 konkrét mondatot, hogyan lehetett volna még kiegyensúlyozottabban reagálni!

            Beszélgetés:
            {user_transcript}
            """
            try:
                stream_gen, model_used = stream_gemini_fast(eval_prompt, api_key, selected_model, available_models, temp=0.3)
                st.caption(f"⚡ Villámelemzés ezzel a modellel: `{model_used}`")
                st.write_stream(stream_gen)
            except Exception as e:
                st.error(f"Elemzési hiba: {e}")
