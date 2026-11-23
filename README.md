# 🧭 Bereai Iránytű – Dinamikus Kommunikációs és Határhúzó Szimulátor

Interaktív, AI-alapú szituációs gyakorlótér és beszélgetéselemző, amely az **Apostolok cselekedetei 17:11** szerinti bereai közösség attitűdjére épít: **nyitott, tiszteletteljes meghallgatás, józan kritikai vizsgálat és kedves, de kőkemény határhúzás.**

---

## 🎯 Mi a Bereai Minta alapelve?

A bereai hívők két tulajdonságukról voltak híresek: *„készséggel fogadták az igét, és naponként tudakozták az Írásokat, hogy úgy vannak-e ezek”* (ApCsel 17:11). 

A szimulátorban ez a stílus **nem a konfliktuskerülő, mézesmázos simulékonyságot** jelenti, hanem a **nyitott emberség** és a **józan, megalkuvás nélküli igazságkeresés** egyensúlyát. Az alkalmazás minden körben vadonatúj, valós élethelyzeteken (munkahely, gyülekezet, család, pénzügyek) alapuló szituációkat generál rejtett motivációkkal, majd a párbeszéd végén fedi fel a másik fél valódi szándékát.

---

## 📊 A 4 értékelési pillér és a pontozás kritériumai (1–10 skála)

### 1. Nyitott & Tiszteletteljes Meghallgatás *(Kegyelem)*
* **Mit vizsgál:** Képes-e a felhasználó előítéletek, cinizmus és azonnali lecsapás nélkül meghallgatni a másik felet, teret hagyva neki, hogy kifejtse az álláspontját?
* **1–3 pont:** Azonnali elutasítás, lekezelő vagy támadó hangnem, a másik fél szavába vágás.
* **4–7 pont:** Meghallgatja ugyan a helyzetet, de hamar védekezővé vagy türelmetlenné válik, és átveszi az irányítást, mielőtt a másik kiterítené a kártyáit.
* **8–10 pont:** Nyugodt, tiszteletteljes odafordulás; jó kérdésekkel hagyja beszélni a másikat, miközben végig megőrzi a méltóságát.

### 2. Józan Vizsgálat & Kritikai Tisztánlátás *(Igazság-próba)*
* **Mit vizsgál:** Mennyire dől be a felhasználó a tekintélyelvű, kenetteljes vagy érzelmi zsaroló frázisoknak? Képes-e a tények, a logika és a Szentírás mérlegére tenni a hallottakat?
* **1–3 pont:** Naiv hiszékenység, kodependens „Megmentő” szerepbe esés, a manipuláció teljes figyelmen kívül hagyása.
* **4–7 pont:** Megérzi, hogy valami nem stimmel, de bizonytalanul reagál, vagy hagyja magát érzelmi terelésekkel elbizonytalanítani.
* **8–10 pont:** Tűpontos valóságérzékelés; átlát a „lelki” vagy érzelmi ködösítésen, tényekre, előzményekre és bibliai alapokra kérdez rá.

### 3. Kedves, de Kemény Határhúzás *(„Kígyó-okosság & galamb-szelídség”)*
* **Mit vizsgál:** Tud-e a felhasználó egyszerre higgadt, nem személyeskedő, ugyanakkor kőkemény, megalkuvás nélküli határt húzni ott, ahol a másik visszaélne a jóindulatával?
* **1–3 pont:** Teljes behódolás és bűntudatból fakadó engedékenység, VAGY durva, dühös, személyeskedő támadás.
* **4–7 pont:** Meghúzza ugyan a határt és nemet mond, de a stílusa rideggé, számonkérővé vagy védekezővé válik.
* **8–10 pont:** Szelíd, nyugodt szilárdság; személyeskedés és harag nélkül, egyetlen tárgyilagos mondatban zárja le a manipulációs kísérletet.

### 4. Álarc nélküli Őszinteség *(Képmutatás-ellenesség)*
* **Mit vizsgál:** Mennyire mentes a kommunikáció a művi udvariaskodástól, a konfliktuskerülő alakoskodástól és az üres vallásos zsargontól (*„igen-igen, nem-nem”*)?
* **1–3 pont:** Mézesmázos alakoskodás, hamis együttérzés színlelése, miközben mást gondol, vagy üres „lelki” klisék puffogtatása.
* **4–7 pont:** Alapvetően egyenes beszéd, de néhol még diplomáciai köntösbe csomagolja a valódi álláspontját, hogy elkerülje a feszültséget.
* **8–10 pont:** Teljesen hiteles, álarc nélküli, természetes emberi beszéd; kimondja a valóságot úgy, ahogy van, szeretetből, de mellébeszélés nélkül.

---

## 🛠️ Főbb funkciók

* **🎲 Dinamikus Szimulátor (Élő szerepjáték):** Minden indításkor új, valós élethelyzetet generál titkos motivációval és karakterleírással.
* **⚖️ Azonnali Bereai Kiértékelés:** A beszélgetés bármely pontján lekérhető elemzés, amely felfedi a másik fél rejtett szándékát, pontozza a 4 pillért, és kenetteljes zsargontól mentes válasz-alternatívákat ad.
* **📋 Saját beszélgetés elemzése:** Megtörtént Messenger-, e-mail- vagy élő párbeszédek utólagos kiértékelése a Bereai Minta alapján.
* **⚡ Hibatűrő modellváltás:** Automatikus tartalékmodell-kezelés (`gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-4-hydrogen`) a gyors és megszakításmentes működésért.

---

## 🚀 Telepítés és indítás

### 1. Szükséges csomagok telepítése
```bash
pip install streamlit google-genai
```

### 2. Google Gemini API kulcs beállítása
Hozz létre egy `.streamlit/secrets.toml` fájlt a projekt gyökerében, és add meg az API kulcsodat (vagy add meg futás közben az oldalsávon):
```toml
GEMINI_API_KEY = "AIzaSy..."
```

### 3. Alkalmazás indítása
```bash
streamlit run app.py
```
*(A `app.py` helyére írd a saját Python-fájlod nevét.)*
# Ir-nyt-
Keresztény iránytű
