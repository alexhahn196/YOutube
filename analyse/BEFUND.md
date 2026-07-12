# BEFUND — Geschäftsmodell-Test der 33 Kanäle

Stand: Juli 2026. Nur Zahlen/Befunde, keine Empfehlungen. Datenbasis: eigene, gedrosselte
Scrapes (bash+curl+Python), Roh-Responses in `raw/` (33 Kanäle) und `raw_d/` (Welle).
Grundsatz: nicht sauber extrahierbare Werte = NULL + Vermerk (siehe Datenqualität).

## 0. Prämissen-Korrektur (wichtigster Befund)
Die Annahme „alle 33 sind Shorts-Kanäle" ist **falsch**. Nach exakter Dauer-Auswertung
(Video-Overlays):
- **28 von 33 = LONG-FORM** (Median-Videolänge 5 Min bis 2,4 Std; reguläre Videos).
- **5 von 33 = SHORTS** (keine Dauer-Overlays / ≤180s): MovidTV1, thedramatalesx,
  LOVERSINUSA, CheathanMust, AaluTamatarTales.
Der Shorts-YPP-Test (10 Mio. Shorts-Views/90 T.) gilt daher nur für diese 5 Kanäle.

## 1. YPP-Werbe-Eligibility (Check B) — nackte Zahl: **2 von 33**
Nur Shorts-Kanäle können den Shorts-Werbe-Pfad erfüllen. Ergebnis (subs≥1000 UND
Shorts-Views_90d≥10 Mio., Shorts-Views = exakte Gesamt-Views bei reinen Shorts-Kanälen):

| Shorts-Kanal | subs | shorts_views_90d (exakt) | ≥10M |
|---|---|---|---|
| MovidTV1 | 92.200 | 132.246.317 | JA |
| thedramatalesx | 46.700 | 14.189.050 | JA |
| LOVERSINUSA | 93.000 | 7.452.214 | nein |
| CheathanMust | 12.400 | 6.603.655 | nein |
| AaluTamatarTales | 4.820 | (Shorts-Anteil, Summe niedrig) | nein |

→ **ypp_ad_eligible (Shorts-Pfad) = 2** (MovidTV1, thedramatalesx). Harte Untergrenze:
Wer <10 Mio. Shorts-Views hat, KANN keine Shorts-Werbeeinnahmen haben.
→ Fan-Funding-Stufe (≥500 subs + ≥3 Mio. Shorts-Views): 4 der 5 Shorts-Kanäle.

**Long-Form-Kanäle (28):** Gate ist 1.000 subs + 4.000 öffentliche Watch-Stunden/12 Mon.
Watch-Stunden werden von YouTube extern nicht exponiert → **nicht bestimmbar** (keine
Schätzung). Ausgewiesen ist stattdessen `watch_hours_upperbound` (Σ exakte Views × exakte
Dauer = 100%-Retention-Maximum) und die dafür nötige Mindest-Retention pro Kanal
(`retention_needed_for_4000h`) in `kanaele_full.csv`. subs≥1000: siehe CSV.

## 2. Median statt Maximum (Check A): **12 SYSTEM · 4 LOTTERIE · 17 UNKLAR**
Regel: median<10.000 UND hit_ratio<5% = LOTTERIE; median≥100.000 = SYSTEM; sonst UNKLAR.
- **SYSTEM (konstant, 12):** u.a. FuntooBabaTV (median 1.123.568), MehramSheikh (387.000,
  hit_ratio 0,48), Sasuraldramastory (394.387, 0,42), AALUFAMILYTV (283.000), Bingebox
  (258.793).
- **LOTTERIE (4):** HappyEndingTales (median 8.900), Aiduniya377 (1.869), VEGHINDISTORYTV
  (972), AaluTamatarTales (440) — je 1 viraler Hit, Rest flach.
- Weitere sehr niedrige Mediane trotz Viral-Hit (UNKLAR wegen Grenzwert): ToonyPitara 497,
  LittleDramaWorld 482, MASTICARTOON 119, VeggieStory 777.
- median_to_max und alle Perzentile: `kanaele_full.csv`.

## 3. Ist das Fenster offen? (Check C) — **OFFEN**
- (a) Spätestes join_date mit ≥480k-Hit: **25.06.2026** (TrioHistory111, Hit 6.100.000).
- (b) Kanäle gestartet NACH 01.06.2026 mit Viral-Hit: **14** (u.a. Bestorytales 20.06. →
  12M, SabjiyoKiDuniya 20.06. → 6,3M, AALUBIGTV 09.06. → 7,7M).
- Kohorten (alle 33 auf Hit selektiert, daher 100% Trefferquote — unverzerrte Rate = Check D):
  Apr 6 Kanäle / Median-Top 2,05M · Mai 13 / 811k · Jun 14 / 2,30M.

## 4. Basisrate der Welle (Check D) — Trefferquote **2,4 %**, Kohorten-Median **129 Views**
Aus 260 Klon-Wellen-Handles gefiltert auf neu(<90 T., Start ab Apr 2026)+klein(<200k Abos):
- **N = 84** neue Kleinkanäle.
- **M = 2** mit ≥480k-Hit (im Scrape-Fenster bestätigt): thedramatalesx (11,0M), VEGHINDISTORYTV
  (1,06M) — beide zugleich in der 33er-Gewinnerliste.
- **Trefferquote = M/N = 2,4 %** (harte Untergrenze; ältere Hits außerhalb Scrape-Fenster nicht
  erfasst; 2 Kanäle mit unbestimmbarem Hit, da total≥480k aber kein Einzelvideo≥480k im Fenster).
- **Median Top-Video über die GESAMTE Kohorte (n=84) = 129 Views.** D.h. der mittlere neue
  Kleinkanal der Welle bringt es auf ein bestes Video von 129 Aufrufen.
- Trefferquote je Welle: Gemüse-Veg 8,3 % (1/12), Drama/Karma 6,2 % (1/16), Gemüse-Sabzi 0 %
  (0/15), GiantFood 0 % (0/15), Gemüse-Aalu 0 % (0/7), Tales/Story 0 % (0/5), sonstige 0 %.
- Befund: Die 33er-„Gewinner"-Liste ist massiver Survivorship-Bias — die unverzerrte Basisrate
  eines Neueinsteigers in diesen Wellen liegt bei ~2–3 % für einen Viral-Hit, Kohorten-Median 129.
  Tabelle in `kohorten.csv` (WELLE:*-Zeilen).

## 5. Netzwerk-Cluster (Check E) — schwache Signale, kein starker Farm-Beweis
- **Identische Beschreibungs-Boilerplate (Hash):** keine unter den 33.
- **Geteilte externe Domain:** MovidTV1 + thedramatalesx → beide facebook.com (zugleich die
  2 englischen Shorts-Kanäle mit ≥10M — möglicher selber Operator, aber Boilerplate ≠).
  Radhakrishnadub + SabjiyoKiDuniya → beide instagram.com (generisch, schwach).
- **Upload-Stunde (UTC):** Häufung 12–13 UTC (14 Kanäle) — konsistent mit indischer
  Tageszeit, kein Operator-Beweis.
- **Handle-Namensmuster (Wellen):** aalu(3), tales(4), story(3), drama(4), veg(2) — belegt
  Klon-Wellen (gleiche Nische/Namenskonvention), nicht zwingend gleicher Betreiber.

## 6. Datenqualität — was NICHT ermittelbar war und warum
- **Reale Watch-Stunden (Long-Form-Gate):** von YouTube extern nicht exponiert → NULL für
  28 Kanäle; nur Obergrenze (Views×Dauer) berechenbar.
- **All-Time-Top-Video außerhalb Scrape-Fenster:** Scrape erfasst neueste ~30–46 Uploads +
  RSS-15. Wo der virale Hit älter ist, spiegelt `max_views` (Check A) nur jüngste Videos,
  nicht den historischen Hit — betrifft u.a. thedramatalesx (max_scraped 96k vs. verifizierter
  11M-Hit), LOVERSINUSA. 16 Kanäle tragen `data_quality`-Vermerke. Der verifizierte ≥480k-Hit
  (Check C) stammt aus der Erst-Recherche (`_verified33.json`), nicht aus diesem Scrape.
- **Subs:** About-Seite liefert nur gerundete Abo-Zahl (z.B. „23.8K") → exakte Abos nicht
  verfügbar; für die 1.000/500-Schwellen ausreichend.
- **exakte Views:** aus RSS `media:statistics` (letzte 15 Uploads) exakt; ältere Uploads nur
  gerundet („1.2M") aus der Listenansicht — in `views_source` pro Video markiert.
- **4 Kanäle im alten HTML-Format** (richItemRenderer statt lockupViewModel): separat geparst.
