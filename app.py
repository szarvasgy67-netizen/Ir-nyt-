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
                try:
                    stream_gen, _ = stream_gemini_fast(reply_prompt, api_key, selected_model, available_models, temp=0.6)
                    ai_reply = st.write_stream(stream_gen)
                    st.session_state["rk_messages"].append({"role": "assistant", "content": ai_reply})
                except Exception as e:
                    st.error(f"Hiba a válaszadásnál: {e}")

    if len(st.session_state["rk_messages"]) >= 3:
        st.divider()
        if st.button("⚖️ Párbeszéd lezárása és kiértékelése (Kegyelem vs. Igazság vs. Határok)", type="primary"):
            if not api_key:
                st.error("Add meg a Gemini API kulcsot!")
            else:
                history_str = "\n".join([f"{'Keresztény' if m['role']=='user' else 'Beszélgetőpartner'}: {m['content']}" for m in st.session_state["rk_messages"]])
                judge_prompt = f"""
                Értékeld ki tömören, lényegretörően a 'Keresztény' szereplő kommunikációját az alábbi szimulációban!
                A szituáció rejtett háttere (amit ő nem tudott előre): {scenario['persona_prompt']}

                Értékeld 1-10 ponttal és 1-2 mondatos indoklással a 4 pillért:
                1. **Kegyelem & Méltóság** (emberi tisztelet, nyitottság)
                2. **Igazság & Bibliai Hűség** (nem adta-e fel a bibliai értékrendet)
                3. **Határhúzás & 'Kígyó-okosság'** (átlátott-e a manipuláción, elkerülte-e a kodependens megmentő-szerepet)
                4. **Alázat & Bölcsesség** (elfogadta-e, hogy nem lát a másik szívébe, kérdezett-e kioktatás helyett)

                Fedd fel 2 mondatban a másik fél rejtett motivációját, és adj 2 konkrét mondatjavaslatot!

                Párbeszéd:
                {history_str}
                """
                try:
                    st.subheader("📊 Kiértékelés: Kegyelem, Igazság & Emberi Határok")
                    stream_gen, model_used = stream_gemini_fast(judge_prompt, api_key, selected_model, available_models, temp=0.3)
                    st.caption(f"⚡ Villámelemzés ezzel a modellel: `{model_used}`")
                    full_eval = st.write_stream(stream_gen)
                    st.session_state["rk_eval"] = (full_eval, model_used)
                except Exception as e:
                    st.error(f"Kiértékelési hiba: {e}")

    if "rk_eval" in st.session_state:
        eval_res, model_used = st.session_state["rk_eval"]
        st.subheader("📊 Kiértékelés: Kegyelem, Igazság & Emberi Határok")
        st.caption(f"⚡ Bírói modell: `{model_used}`")
        st.markdown(eval_res)
