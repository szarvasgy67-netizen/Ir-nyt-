import streamlit as st
import json
from google import genai
from google.genai import types

st.set_page_config(page_title="Radikális Kereszténység & Határhúzás Szimulátor", layout="wide")
st.title("✝️ Radikális Kereszténység: Kegyelem, Igazság & Határhúzás")
st.caption("Interaktív szituációs szimulátor és kommunikációs elemző – ahol nem látunk a másik szívébe, ezért a szeretet mellé józan határok is kellenek.")

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
    "gemini-4-argon",
    "gemini-4-hydrogen",
    "gemini-4-carbon"
]

selected_model = st.sidebar.selectbox("🤖 Gemini Modell:", available_models, index=0)

@st.cache_resource
def get_gemini_client(key):
    return genai.Client(api_key=key)

def call_gemini_with_fallback(prompt, key, preferred_model, fallback_models, temp=0.4):
    models_to_try = [preferred_model] + [m for m in fallback_models if m != preferred_model]
    cfg = types.GenerateContentConfig(
        temperature=temp,
        thinking_config=types.ThinkingConfig(thinking_level="low")
    )
    client = get_gemini_client(key)
    last_error = None
    for model_name in models_to_try:
        try:
            res = client.models.generate_content(model=model_name, contents=prompt, config=cfg)
            if res.text:
                return res.text.strip(), model_name
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"Minden Gemini modell hibát adott: {last_error}")

# --- SZITUÁCIÓK DEFINIÁLÁSA (REJTETT MOTIVÁCIÓKKAL) ---
SCENARIOS = {
    "1. Polgárpukkasztó vendég a gyülekezetben (Kereső vs. Provokátor?)": {
        "context": "Vasárnapi istentisztelet előtt egy fiatal férfi szakadt ruhában, feltűnő külsővel beül az első sorba, és hangosan megjegyzi a mellette ülőnek: 'Na, nézzük, mennyi képmutató gyűlt össze ma is.' Te vagy az egyik gyülekezeti tag/vezető, aki odalép hozzá.",
        "persona_prompt": "Te egy 23 éves fiatal férfi vagy, aki sok vallási képmutatást látott gyerekkorában, ezért védekezésből provokatív és cinikus vagy. REJTETT MOTIVÁCIÓD: Valójában mély válságban vagy és keresed, van-e bárhol őszinte ember, de ha kioktatnak vagy prédikálnak neked, azonnal támadsz és elmenekülsz. Ha viszont őszintén, emberként kérdeznek, fokozatosan megnyílsz, de nem térsz meg azonnal varázsütésre.",
        "opening_line": "Mi van, te vagy itt a biztonsági őr, aki kidob, mert nem öltönyben jöttem?"
    },
    "2. LMBTQ-aktivista ismerős éles kérdése (Kegyelem vs. Igazság)": {
        "context": "Egy régi egyetemi évfolyamtársaddal kávézol, aki nyíltan LMBTQ-aktivista. Tudja rólad, hogy komolyan veszed a Bibliát, és rákérdez, hogyan tudsz egyszerre barátkozni vele és hinni egy szerinte 'kirekesztő' könyvben.",
        "persona_prompt": "Te egy intelligens, érzékeny egyetemi oktató vagy. REJTETT MOTIVÁCIÓD: Kíváncsi vagy, hogy a beszélgetőpartnered valódi, önazonos keresztény-e, vagy csak a társadalmi nyomásnak megfelelve feladja a saját hitét, esetleg elutasítóan kioktat. Ha behódol és relativizálja a Bibliát, elveszíted iránta a tiszteletedet. Ha ítélkező, megszakítod a beszélgetést. Ha szelíd, őszinte és nem megalkuvó, tisztelettel vitázol tovább.",
        "opening_line": "Őszintén kérdezem: ha a Bibliád bűnnek tartja az életformámat, akkor ez a kávézás most csak egy udvarias térítési kísérlet, vagy te már modernizáltad a nézeteidet?"
    },
    "3. Rejtett manipulátor a közösségben (Határhúzás & 'Kígyó-okosság')": {
        "context": "Egy hónapja jár a közösségbe egy rendkívül kedves, sokat segítő új tag, aki mindenkit dicsér, de közben finoman mások ellen hangolja a tagokat, és most tőled kér pénzt valamint bizalmas információkat egy másik gyülekezeti tagról.",
        "persona_prompt": "Te egy rejtett nárcisztikus / manipulátor vagy, aki keresztény zsargont használ ('Isten vezetett hozzád', 'szeretetből kérdezem'). REJTETT MOTIVÁCIÓD: Információt és befolyást akarsz szerezni a közösségben. Ha a felhasználó naiv és 'Megmentő' szerepbe esve mindent megad, kihasználod. Ha kedvesen, de határozottan nemet mond és határokat húz, sértődötten próbálsz bűntudatot kelteni benne ('Azt hittem, itt valódi szeretet van...').",
        "opening_line": "Olyan jó, hogy végre egy igazán lelki emberrel beszélhetek! Tudod, nagyon aggódom Péterért, mesélnél róla bizalmasan, mi a gond a házasságával, hogy jobban tudjak imádkozni érte? És sajnos most megszorultam, 50 ezer forinttal ki tudnál segíteni holnapig?"
    },
    "4. Saját valós beszélgetés / konfliktus elemzése": {
        "context": "Másold be egy megtörtént beszélgetésedet (pl. Messenger, e-mail, gyülekezeti vagy családi vita), és az AI elemzi a Kegyelem, Igazság, Határhúzás és Kodependencia szempontjából.",
        "persona_prompt": None,
        "opening_line": None
    }
}

st.sidebar.divider()
selected_scenario_name = st.sidebar.selectbox("🎭 Válassz szituációt:", list(SCENARIOS.keys()))
scenario = SCENARIOS[selected_scenario_name]

if st.sidebar.button("🔄 Beszélgetés újrakezdése"):
    st.session_state.pop("rk_messages", None)
    st.session_state.pop("rk_eval", None)
    st.rerun()

# --- 4. MÓD: SAJÁT BESZÉLGETÉS ELEMZÉSE ---
if scenario["persona_prompt"] is None:
    st.subheader("📋 Valós beszélgetés kiértékelése")
    st.info(scenario["context"])
    user_transcript = st.text_area("Másold be ide a beszélgetés szövegét:", height=220, placeholder="Én: ...\nMásik fél: ...")
    
    if st.button("⚖️ Kiértékelés a 4 pillér alapján", type="primary"):
        if not api_key:
            st.error("Add meg a Gemini API kulcsot az oldalsávon!")
        elif not user_transcript.strip():
            st.warning("Írj vagy másolj be egy beszélgetést!")
        else:
            with st.spinner("Mélyelemzés folyamatban..."):
                eval_prompt = f"""
                Elemezd az alábbi beszélgetést a 'Radikális Kereszténység (Kegyelem, Igazság, Emberi Határhúzás)' modell alapján!
                Ne feledd: az ember nem lát a másik szívébe, ezért a szeretet mellé józan határok és pszichológiai tisztánlátás is kell.

                Értékeld 1-10 skálán és röviden indokold ezt a 4 tengelyt:
                1. **Kegyelem & Emberi Méltóság** (ítélkezésmentes tisztelet, előítélet-mentesség)
                2. **Igazság & Bibliai Hűség** (nem relativizálja az értékrendjét, nem hódol be)
                3. **Határhúzás & 'Kígyó-okosság'** (felismeri-e a manipulációt, nem esik-e kodependens 'Megmentő' szerepbe)
                4. **Kommunikációs Bölcsesség** (kérdező, szelíd attitűd kioktatás helyett)

                Adj a végén 2-3 konkrét mondatot, hogyan lehetett volna még kiegyensúlyozottabban reagálni!

                Beszélgetés:
                {user_transcript}
                """
                result, model_used = call_gemini_with_fallback(eval_prompt, api_key, selected_model, available_models, temp=0.3)
                st.caption(f"⚡ Elemző modell: `{model_used}`")
                st.markdown(result)

# --- 1-3. MÓD: INTERAKTÍV SZIMULÁTOR ---
else:
    st.info(f"**Helyzetkép:** {scenario['context']}")
    st.caption("⚠️ *Megjegyzés: A másik fél rejtett motivációját nem ismered – pontosan úgy, mint a valóságban.*")

    if "rk_messages" not in st.session_state or st.session_state.get("rk_current_scen") != selected_scenario_name:
        st.session_state["rk_current_scen"] = selected_scenario_name
        st.session_state["rk_messages"] = [{"role": "assistant", "content": scenario["opening_line"]}]
        st.session_state.pop("rk_eval", None)

    for msg in st.session_state["rk_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Írd be a válaszodat a szituációban...")

    if user_input:
        if not api_key:
            st.error("Add meg a Gemini API kulcsot az oldalsávon!")
        else:
            st.session_state["rk_messages"].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            history_str = "\n".join([f"{'Felhasználó' if m['role']=='user' else 'Karakter'}: {m['content']}" for m in st.session_state["rk_messages"]])
            reply_prompt = f"""
            Szerepjáték szimuláció. Maradj szigorúan a karakteredben!
            Helyzet: {scenario['context']}
            Karakter és rejtett motiváció: {scenario['persona_prompt']}
            
            Eddigi párbeszéd:
            {history_str}
            
            Válaszolj 2-4 mondatban, teljesen életszerűen a karakter stílusában (ne térj meg varázsütésre, reagálj a felhasználó hangnemére és határozottságára):
            """
            with st.chat_message("assistant"):
                with st.spinner("Reagál..."):
                    ai_reply, _ = call_gemini_with_fallback(reply_prompt, api_key, selected_model, available_models, temp=0.6)
                    st.markdown(ai_reply)
                    st.session_state["rk_messages"].append({"role": "assistant", "content": ai_reply})

    if len(st.session_state["rk_messages"]) >= 3:
        st.divider()
        if st.button("⚖️ Párbeszéd lezárása és kiértékelése (Kegyelem vs. Igazság vs. Határok)", type="primary"):
            if not api_key:
                st.error("Add meg a Gemini API kulcsot!")
            else:
                with st.spinner("A párbeszéd teológiai és pszichológiai kiértékelése..."):
                    history_str = "\n".join([f"{'Keresztény' if m['role']=='user' else 'Beszélgetőpartner'}: {m['content']}" for m in st.session_state["rk_messages"]])
                    judge_prompt = f"""
