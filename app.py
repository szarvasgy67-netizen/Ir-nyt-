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
    st.info("„Én ültettem, Apollós öntözött, de a növekedést Isten adta.” A **vetés minőségét, a jó sáfárságot és a potenciális érintéseket** mérjük.")
    c1, c2 = st.columns(2)
    with c1:
        project_name = st.text_input("Projekt neve:", value="Negyedéves Mai Ige + kis ajándék")
        direct_cost = st.number_input("Közvetlen költség / év (Ft):", min_value=0, value=93000, step=5000)
        funding_source = st.selectbox("Finanszírozás:", ["Saját forrásból (önfinanszírozó)", "Átlátható gyülekezeti adomány", "Külső adományozók (nem látják a pontos célcsoportot)"])
        total_reach = st.number_input("Összes elért háztartás / fő (évente):", min_value=1, value=220, step=10)
        external_pct = st.slider("Valódi KÜLSŐS arány (%):", 0, 100, 95)
    with c2:
        volunteer_hours = st.number_input("Saját + önkéntes munkaórák / év:", min_value=1, value=8, step=5)
        paid_staff_involved = st.checkbox("Fizetett alkalmazott dolgoztat ingyen önkénteseket a saját KPI-jához?", value=False)
        burnout_risk = st.select_slider("Terhelés / kiégési kockázat:", options=["Alacsony", "Közepes", "Magas"], value="Alacsony")
        touch_quality = st.selectbox("Érintés minősége:", ["Kis ajándék + tartalmas üzenet (2.5x)", "Személyes meghívás / beszélgetés (3.5x)", "Egyszerű szórólap / rendezvény (1.0x)"])

    ext_reach = max(1, round(total_reach * (external_pct / 100)))
    hidden_labor = volunteer_hours * 2500
    true_cost = direct_cost + hidden_labor
    mult = 2.5 if "2.5x" in touch_quality else (3.5 if "3.5x" in touch_quality else 1.0)
    touches = min(ext_reach, round(ext_reach * 0.12 * mult))

    score = 10.0
    if "Külső" in funding_source and external_pct < 50: score -= 3.0
    elif "Átlátható" in funding_source: score -= 0.5
    if paid_staff_involved: score -= 2.5
    if burnout_risk == "Közepes": score -= 1.0
    elif burnout_risk == "Magas": score -= 2.5
    if external_pct < 30: score -= 2.0
    score = max(1.0, round(score, 1))

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sáfársági Korrektség", f"{score} / 10")
    m2.metric("Külsős elérés", f"{ext_reach} fő / ház")
    m3.metric("Költség / külsős", f"{direct_cost / ext_reach:,.0f} Ft".replace(",", " "))
    m4.metric("Érdemi érintés (potenciál)", f"~{touches} fő / év")
    st.caption(f"💡 Rejtett munkaérték: **{hidden_labor:,.0f} Ft** | Valódi összköltség: **{true_cost:,.0f} Ft** ({true_cost / ext_reach:,.0f} Ft / külsős).".replace(",", " "))

    if st.button("🧠 Bereai AI-vélemény kérése", type="primary") and api_key:
        sp = f"Értékeld 4-5 mondatban a Bereai józanság és 1Kor 3,6-7 alapján: {project_name}, pontszám: {score}/10, költség: {direct_cost} Ft, rejtett munka: {hidden_labor} Ft, finanszírozás: {funding_source}, külsős elérés: {ext_reach} ({external_pct}%), potenciális érintés: ~{touches}, fizetett szervező ingyen önkéntesekkel: {paid_staff_involved}, terhelés: {burnout_risk}."
        stream_gen, _ = stream_gemini_fast(sp, api_key, selected_model, available_models, temp=0.3)
        st.write_stream(stream_gen)
