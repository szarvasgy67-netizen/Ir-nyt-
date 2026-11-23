# 🧭 Bereai Mérce – Kommunikációs és Sáfársági Szimulátor

Interaktív, AI-alapú kommunikációs gyakorlótér, beszélgetéselemző és szolgálati sáfárság-kalkulátor, amely az **Apostolok cselekedetei 17:11** és az **1Korinthus 3:6–7** bibliai alapelveire épít: **nyitott meghallgatás, józan vizsgálat, kemény határhúzás és felelős magvetés.**

---

## 🎯 Teológiai és kommunikációs alapelvek

### 1. Bereai Minta (ApCsel 17:11)
*„Készséggel fogadták az igét, és naponként tudakozták az Írásokat, hogy úgy vannak-e ezek.”*
* **Nem konfliktuskerülő simulékonyság:** A bereai attitűd kerüli a mézesmázos képmutatást és az alakoskodást.
* **Egyensúly:** Egyszerre jelent tiszteletteljes, ítélkezésmentes nyitottságot a másik ember felé, és kritikus, tényeken alapuló józanságot minden állítással vagy érzelmi nyomással szemben.

### 2. Sáfárság és a növekedés szuverenitása (1Kor 3:6–7)
*„Én ültettem, Apollós öntözött, de a növekedést Isten adta.”*
* **A megtérést csak Isten tudja mérni:** Az ember feladata nem a „lelki termés” mesterséges legyártása vagy számonkérése, hanem a **tiszta, átlátható, mások kizsákmányolásától mentes magvetés**.

---

## 🛠️ Az alkalmazás 3 fő modulja

### 1. 🎲 Dinamikus Szimulátor (Élő szerepjáték)
Valós élethelyzeteken (gyülekezeti túlvállalás, lelki köntösbe bújtatott anyagi érdekek, munkahelyi világnézeti viták, családi határok, kodependencia) alapuló interaktív párbeszéd-gyakorló.
* **Rejtett motivációk:** A beszélgetés során a másik fél valódi szándéka rejtve marad, a záró kiértékelésnél azonban lehull a lepel.
* **4 pilléres bereai pontozás (1–10 skála):**
  1. **Nyitott & Tiszteletteljes Meghallgatás** (ítélkezésmentes odafordulás)
  2. **Józan Vizsgálat & Kritikai Tisztánlátás** (tények és bibliai alapok kérése a kenetteljes frázisok helyett)
  3. **Kedves, de Kemény Határhúzás** (személyeskedés nélküli, megalkuvás nélküli kiállás)
  4. **Álarc nélküli Őszinteség** (*„igen-igen, nem-nem”* – sallangmentes, egyenes beszéd)

### 2. 📋 Saját beszélgetés elemzése
Megtörtént Messenger-, e-mail- vagy élő párbeszédek utólagos kiértékelése a 4 bereai pillér alapján, természetes, hétköznapi magyar válasz-alternatívákkal.

### 3. 🌱 Missziós Sáfárság-kalkulátor (Vetés-mérő & Átkeretezés-detektor)
Szolgálati projektek, táborok és evangelizációs akciók pénzügyi, terhelési és etikai korrektségének vizsgálata.
* **Valódi összköltség és rejtett munkaérték:** Beárazza az önkéntesek befektetett munkaóráit is, hogy ne tűnjön „olcsónak” olyan projekt, amely mások ki nem fizetett munkáján nyugszik.
* **Automatikus terhelés- és kiégésbecslés:** Az egy főre jutó heti munkaórák alapján jelzi a túlhajtás kockázatát.
* **3 lépcsős érintési mérleg:** Szétválasztja a kezdeti *jóindulat-nyitást*, az *érdemi magvetést* és a *közösségi kapcsolódási potenciált* (figyelembe véve a helyi utánkövetés meglétét).
* **🔍 Átkeretezés-detektor:** Leleplezi, ha a „misszió” címke mögött valójában *vallási turizmus*, *fizetett szervezői KPI-termelés mások ingyenmunkájából*, *olcsó gyülekezeti gyerekfelügyelet* vagy *önigazolási projekt* húzódik meg.

---

## 🚀 Telepítés és indítás

### 1. Szükséges csomagok telepítése (`requirements.txt`)
```text
streamlit
google-genai
```
```bash
pip install -r requirements.txt
```

### 2. Google Gemini API kulcs beállítása
Hozz létre egy `.streamlit/secrets.toml` fájlt (vagy a Streamlit Cloudon a **Settings → Secrets** menüpontban add meg):
```toml
GEMINI_API_KEY = "AIzaSy..."
```

### 3. Alkalmazás futtatása
```bash
streamlit run app.py
```
