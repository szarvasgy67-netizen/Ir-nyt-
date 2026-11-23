# -*- coding: utf-8 -*-
import streamlit as st
import random
import time
from google import genai
from google.genai import types

st.set_page_config(page_title="Bereai Merce - Szimulator", layout="wide")
st.markdown("""<style>
html, body, [class*="css"], [data-testid="stChatMessageContent"] p { font-size: 14px !important; line-height: 1.5 !important; }
h1 { font-size: 1.7rem !important; } h2, h3 { font-size: 1.25rem !important; }
</style>""", unsafe_allow_html=True)

st.title("🧭 Bereai Mérce – Kommunikációs és Sáfársági Szimulátor")
st.caption("ApCsel 17:11 & 1Kor 3:6: nyitott meghallgatás, józan vizsgálat, kemény határhúzás és felelős magvetés.")

st.sidebar.header("🔑 AI Settings")
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Google Gemini API Key:", type="password")
if "GEMINI_API_KEY" in st.secrets:
    st.sidebar.success("✅ API Key loaded")

available_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-4-hydrogen"]
selected_model = st.sidebar.selectbox("🤖 Gemini Modell:", available_models, index=0)

@st.cache_resource
def get_gemini_client(key):
    return genai.Client(api_key=key)

def stream_gemini_fast(prompt, key, preferred_model, fallback_models, temp=0.5):
    models_to_try = [preferred_model] + [m for m in fallback_models if m != preferred_model]
    cfg = types.GenerateContentConfig(temperature=temp)
    client = get_gemini_client(key)
    last_error = None
    for model_name in models_to_try:
        for _ in range(2):
            try:
                it = iter(client.models.generate_content_stream(model=model_name, contents=prompt, config=cfg))
                first = next(it)
                def gen(f=first, i=it):
                    if f and f.text: yield f.text
                    for c in i:
                        if c.text: yield c.text
                return gen(), model_name
            except Exception as e:
                last_error = e
                time.sleep(0.5)
    raise RuntimeError(f"Minden modell foglalt: {last_error}")

def generate_new_scenario(category, key, preferred_model, fallback_models):
    seed = random.randint(1000, 99999)
    models_to_try = ["gemini-3.5-flash-lite", preferred_model] + [m for m in fallback_models if m not in ("gemini-3.5-flash-lite", preferred_model)]
    gen_prompt = f"""Készíts egy életszerű, valós magyar élethelyzetet (mag: {seed}) a bereai kommunikáció (nyitott meghallgatás, józan vizsgálat, kemény határhúzás) tesztelésére. Témakör: {category}.
    SZEREPOSZTÁS: A Felhasználó MINDIG saját maga (ne adj neki kitalált nevet). Az AI MINDIG a másik fél.
    Válaszolj PONTOSAN ebben az 5 elemű formátumban, '|||' jellel elválasztva, sortörések nélkül:
    CÍM ||| HELYZETKÉP (2 mondat) ||| AI KARAKTERE ||| AI REJTETT MOTIVÁCIÓJA (1 mondat) ||| AI NYITÓMONDATA"""
    client = get_gemini_client(key)
    last_error = None
    for model_name in models_to_try:
        for _ in range(2):
            try:
                resp = client.models.generate_content(model=model_name, contents=gen_prompt, config=types.GenerateContentConfig(temperature=0.95))
                parts = [p.strip().strip('"') for p in resp.text.split("|||")]
                if len(parts) >= 5:
                    return dict(zip(("title", "context", "persona_prompt", "hidden_motivation", "opening_line"), parts))
            except Exception as e:
                last_error = e
                time.sleep(0.5)
    raise RuntimeError(f"Hiba: {last_error}")
BEREA_EVAL_CRITERIA = """BEREAI MINTA (ApCsel 17:11): 1. Nyitott, tiszteletteljes meghallgatás. 2. Kritikus, józan vizsgálat (nem dől be kenetteljes/zsaroló frázisoknak). 3. Kedves, de kőkemény határhúzás alakoskodás nélkül ('igen-igen, nem-nem')."""

st.sidebar.divider()
mode = st.sidebar.radio("🎯 Mód:", ["🎲 Dinamikus Szimulátor", "📋 Saját beszélgetés elemzése", "🌱 Missziós Sáfárság-kalkulátor"])

if mode == "🎲 Dinamikus Szimulátor":
    category = st.sidebar.selectbox("🌍 Témakör:", [
        "Teljesen véletlenszerű valós élethelyzet", "Gyülekezeti konfliktusok és manipuláció",
        "Lelki köntösbe bújtatott szervezeti / anyagi érdekek", "Munkahelyi / egyetemi világnézeti viták",
        "Családi határok, érzelmi zsarolás", "Pénzügyi segítségkérés és kodependencia"
    ])
    if st.sidebar.button("✨ Új szituáció", type="primary") and api_key:
        with st.spinner("Generálás..."):
            new_scen = generate_new_scenario(category, api_key, selected_model, available_models)
            st.session_state["dyn_scenario"] = new_scen
            st.session_state["rk_messages"] = [{"role": "assistant", "content": new_scen["opening_line"]}]
            st.session_state.pop("rk_eval", None)
            st.session_state.pop("trigger_eval", None)
            st.rerun()
    if len(st.session_state.get("rk_messages", [])) >= 2 and "dyn_scenario" in st.session_state:
        if st.sidebar.button("⚖️ Kiértékelés MOST"):
            st.session_state["trigger_eval"] = True

if mode == "🎲 Dinamikus Szimulátor":
    if not api_key:
        st.warning("👈 Add meg az API kulcsodat az oldalsávon!")
        st.stop()
    if "dyn_scenario" not in st.session_state:
        new_scen = generate_new_scenario(category, api_key, selected_model, available_models)
        st.session_state["dyn_scenario"] = new_scen
        st.session_state["rk_messages"] = [{"role": "assistant", "content": new_scen["opening_line"]}]

    scen = st.session_state["dyn_scenario"]
    st.subheader(f"🎭 {scen['title']}")
    st.info(f"**Helyzetkép:** {scen['context']}")
    for msg in st.session_state["rk_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.get("trigger_eval"):
        st.divider()
        st.markdown("### 📊 Bereai Kiértékelés")
        transcript = "\n".join([f"{'Másik fél' if m['role']=='assistant' else 'Te'}: {m['content']}" for m in st.session_state["rk_messages"]])
        eval_prompt = f"""Értékeld 'Te' teljesítményét a BEREAI MINTA alapján! {BEREA_EVAL_CRITERIA}
        HELYZET: {scen['context']} | REJTETT MOTIVÁCIÓ: {scen['hidden_motivation']} | BESZÉLGETÉS:\n{transcript}
        Bontás (sallangmentesen): 1. **Bereai mérleg (A lepel lehull)** 2. **4 pillér pontozása (1-10 + 1 mondat):** Nyitott Meghallgatás, Józan Vizsgálat, Kedves de Kemény Határhúzás, Álarc nélküli Őszinteség. 3. **2 egyenes magyar válasz-alternatíva** (tilos a vallásos zsargon!)."""
        stream_gen, _ = stream_gemini_fast(eval_prompt, api_key, selected_model, available_models, temp=0.3)
        st.session_state["rk_eval"] = st.write_stream(stream_gen)
        st.session_state["trigger_eval"] = False
    elif "rk_eval" in st.session_state:
        st.divider()
        st.markdown("### 📊 Bereai Kiértékelés")
        st.markdown(st.session_state["rk_eval"])

    if "rk_eval" in st.session_state:
        with st.expander("🔍 Eredeti karakterleírás és rejtett motiváció"):
            st.write(f"**Rejtett motiváció:** {scen['hidden_motivation']}\n\n**Karakter:** {scen['persona_prompt']}")

    if user_input := st.chat_input("Írd le, hogyan reagálsz..."):
        st.session_state["rk_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        history_text = "\n".join([f"{'Másik fél' if m['role']=='assistant' else 'Felhasználó'}: {m['content']}" for m in st.session_state["rk_messages"]])
        roleplay_prompt = f"Szerepjáték. Csak a másik fél nevében beszélj! HELYZET: {scen['context']} | KARAKTERED: {scen['persona_prompt']} | REJTETT CÉLOD: {scen['hidden_motivation']}\nBESZÉLGETÉS:\n{history_text}\nReagálj 2-3 mondatban:"
        with st.chat_message("assistant"):
            stream_gen, _ = stream_gemini_fast(roleplay_prompt, api_key, selected_model, available_models, temp=0.7)
            st.session_state["rk_messages"].append({"role": "assistant", "content": st.write_stream(stream_gen)})
elif mode == "📋 Saját beszélgetés elemzése":
    st.subheader("📋 Valós beszélgetés bereai kiértékelése")
    user_transcript = st.text_area("Másold be a beszélgetést:", height=200, placeholder="Én: ...\nMásik fél: ...")
    if st.button("⚖️ Kiértékelés", type="primary") and api_key and user_transcript.strip():
        eval_prompt = f"""Elemezd a beszélgetést a BEREAI MINTA alapján! {BEREA_EVAL_CRITERIA}
        Pontozd 1-10-ig: 1. Nyitott Meghallgatás 2. Józan Vizsgálat 3. Kedves de Kemény Határhúzás 4. Álarc nélküli Őszinteség. Adj 2 egyenes magyar mondat-alternatívát (tilos a vallásos zsargon!).\nBeszélgetés:\n{user_transcript}"""
        stream_gen, _ = stream_gemini_fast(eval_prompt, api_key, selected_model, available_models, temp=0.3)
        st.write_stream(stream_gen)

else:
    st.subheader("🌱 Missziós Sáfárság-kalkulátor (1Kor 3,6–7)")
    st.info("„Én ültettem, Apollós öntözött, de a növekedést Isten adta.” A **vetés minőségét, a jó sáfárságot és a terhek arányosságát** mérjük.")

    preset = st.selectbox("⚡ Gyors sablon betöltése (vagy írd át szabadon):", [
        "1. Egyéni magvetés (pl. Mai Ige + kis ajándék)",
        "2. Nagy költségű 1 hetes tábor (pl. külföldi csapattal)",
        "3. Helyi éves gyülekezeti / ifjúsági program"
    ])

    if "1." in preset:
        d_name, d_cost, d_fund, d_reach, d_ext, d_hours, d_vol, d_weeks, d_paid, d_touch = (
            "Negyedéves Mai Ige + kis ajándék", 93000, 0, 220, 95, 8, 1, 52, False, 0
        )
    elif "2." in preset:
        d_name, d_cost, d_fund, d_reach, d_ext, d_hours, d_vol, d_weeks, d_paid, d_touch = (
            "1 hetes angol tábor külföldi csapattal", 8000000, 2, 30, 15, 1000, 20, 1, True, 2
        )
    else:
        d_name, d_cost, d_fund, d_reach, d_ext, d_hours, d_vol, d_weeks, d_paid, d_touch = (
            "Helyi közösségi est / klub", 250000, 1, 80, 45, 200, 5, 40, False, 1
        )

    c1, c2 = st.columns(2)
    with c1:
        project_name = st.text_input("Projekt neve:", value=d_name)
        direct_cost = st.number_input("Közvetlen költség / év (Ft):", min_value=0, value=d_cost, step=10000)
        funding_source = st.selectbox("Finanszírozás:", [
            "Saját forrásból (önfinanszírozó)",
            "Átlátható gyülekezeti adomány",
            "Külső adományozók (nem látják a pontos célcsoportot)"
        ], index=d_fund)
        total_reach = st.number_input("Összes elért háztartás / fő:", min_value=1, value=d_reach, step=10)
        external_pct = st.slider("Valódi KÜLSŐS arány (%):", 0, 100, d_ext)

    with c2:
        volunteer_hours = st.number_input("Összes önkéntes munkaóra:", min_value=1, value=d_hours, step=10)
        col_sub1, col_sub2 = st.columns(2)
        volunteers_count = col_sub1.number_input("Önkéntesek száma (fő):", min_value=1, value=d_vol, step=1)
        duration_weeks = col_sub2.number_input("Időtartam (hét):", min_value=1, value=d_weeks, step=1)
        
        hrs_per_person_week = volunteer_hours / (volunteers_count * duration_weeks)
        auto_burnout = "Alacsony" if hrs_per_person_week < 5 else ("Közepes" if hrs_per_person_week <= 20 else "Magas")
        
        burnout_risk = st.select_slider(
            f"Terhelés ({hrs_per_person_week:.1f} óra/fő/hét → ajánlott: {auto_burnout}):",
            options=["Alacsony", "Közepes", "Magas"],
            value=auto_burnout
        )
        paid_staff_involved = st.checkbox("Fizetett alkalmazott dolgoztat ingyen önkénteseket a saját KPI-jához?", value=d_paid)
        touch_quality = st.selectbox("Érintés minősége:", [
            "Kis ajándék + tartalmas üzenet (2.5x)",
            "Személyes meghívás / beszélgetés (3.5x)",
            "Egyszerű szórólap / rendezvény (1.0x)"
        ], index=d_touch)

    ext_reach = max(1, round(total_reach * (external_pct / 100)))
    hidden_labor = volunteer_hours * 2500
    true_cost = direct_cost + hidden_labor
    true_unit_cost = true_cost / ext_reach
    mult = 2.5 if "2.5x" in touch_quality else (3.5 if "3.5x" in touch_quality else 1.0)
    touches = min(ext_reach, round(ext_reach * 0.12 * mult))

    score = 10.0
    if "Külső" in funding_source and external_pct < 50: score -= 3.0
    elif "Külső" in funding_source: score -= 1.0
    elif "Átlátható" in funding_source: score -= 0.5
    if paid_staff_involved: score -= 2.5
    if burnout_risk == "Közepes": score -= 1.0
    elif burnout_risk == "Magas": score -= 2.5
    if external_pct < 30: score -= 2.0
    if true_unit_cost > 100000: score -= 2.5
    elif true_unit_cost > 25000: score -= 1.0
    score = max(1.0, round(score, 1))

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sáfársági Korrektség", f"{score} / 10")
    m2.metric("Külsős elérés", f"{ext_reach} fő / ház")
    m3.metric("Költség / külsős", f"{direct_cost / ext_reach:,.0f} Ft".replace(",", " "))
    m4.metric("Érdemi érintés (potenciál)", f"~{touches} fő / év")
    st.caption(f"💡 Terhelés: **{hrs_per_person_week:.1f} óra / fő / hét** | Rejtett munkaérték: **{hidden_labor:,.0f} Ft** | Valódi összköltség: **{true_cost:,.0f} Ft** ({true_unit_cost:,.0f} Ft / külsős).".replace(",", " "))

    if st.button("🧠 Bereai AI-vélemény kérése", type="primary") and api_key:
        sp = f"Értékeld 4-5 mondatban a Bereai józanság és 1Kor 3,6-7 alapján: {project_name}, pontszám: {score}/10, költség: {direct_cost} Ft, rejtett munka: {hidden_labor} Ft ({hrs_per_person_week:.1f} óra/fő/hét terhelés), finanszírozás: {funding_source}, külsős elérés: {ext_reach} ({external_pct}%), potenciális érintés: ~{touches}, fizetett szervező ingyen önkéntesekkel: {paid_staff_involved}."
        stream_gen, _ = stream_gemini_fast(sp, api_key, selected_model, available_models, temp=0.3)
        st.write_stream(stream_gen)
