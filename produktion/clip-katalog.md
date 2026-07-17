# 🎞️ Clip-Katalog (Reuse-Pool) — SINGLE SOURCE OF TRUTH für Wiederverwendung

> **Regel (CLAUDE.md Prozess-Regel 6):** Pool-Reuse NUR über diesen Katalog. Vor jeder Wiederverwendung:
> Status prüfen → `ungescannt`? Dann erst `produktion/pipeline/qc_textscan.py` laufen lassen und Befund hier eintragen.
> **Kein Clip ohne ✅ in den Schnitt.** Neue Clips nach jeder Folgen-Produktion hier ergänzen.
>
> Status: ✅ clean · ⚠️ bedingt (Auflage beachten) · ⛔ gesperrt (Fake-Text) · ❔ ungescannt
> Scan-Stand: 17.07.2026 (F2+F3-Pools komplett, F4 via Master-QC 16./17.07.)

## ⛔ Gesperrte Clips (NIE wieder ungefixt verwenden)
| ID | Motiv | Problem | Ersatz |
|---|---|---|---|
| NV05 | Wow!-Printout 1977, rot umkreist | **„ERR 404"** + Falschdatum **„OCT 26, '77"** (Wow! war 15.08.77!) + $-Zeichen | **NY01** (echter 6EQUJ5-Printout, diegetisch korrekt) |
| NX09 | JPL-Nacht, Silhouetten vor Konsolen | Screens: **„DATA STREAM CORRUPTED"** + Kauderwelsch **„BJERAM"** | **NZ01** (sauberer Forensik-Raum) |
| C20 | Interstellar-Relikt vor Milchstraße | Fake-Schild **„NASA JWST DEEP TIME RELIC"** unten mittig | **C20 gecroppt** (Base-Crop 82 % oben-verankert; Rezept in `folge-02/build_fix.sh`-Historie / F4 `work4k/base_C20.mp4`) |

## Herkunft F1 (C- & NV-Serie, `folge-01-v4/clips/`)
| ID | Motiv | Status | Verwendet in |
|---|---|---|---|
| C17 | Radioteleskop-Dish + Cyan-Beam zum Stern | ✅ | F1, F2, F3, F4 |
| C19 | Komet/Objekt mit Schweif vor Sonne | ✅ (textloses dunkles Emblem u. r. — akzeptiert) | F1, F2, F3, F4 |
| C20 | Interstellar-Relikt vor Milchstraße | ⛔ → nur Crop | F1, F2*, F3*, F4 (Crop) |
| C21 | Observatoriumskuppel bei Nacht | ✅ | F1, F2-Pool |
| C01–C16 | F1-Erstbestand (div. Kosmos-Shots) | ❔ (nur F1; vor Reuse scannen!) | F1 |
| NV01 | Chile-Survey-Kuppel, First Light | ✅ | F1, F2 |
| NV02 | Himmel voller ankommender Besucher | ❔ (nur F1) | F1 |
| NV03 | Einsamer Forscher vor Sternenfeld-Projektion | ✅ | F1, F2, F3, F4 |
| NV04 | 22 Anomalie-Marker, einer pulsiert | ❔ (nur F1) | F1 |
| NV05 | Wow!-Printout (Fake) | ⛔ | F1, F2*, F3* |
| NV06 | Big Ear 1977 bei Nacht | ❔ (nur F1) | F1 |
| NV07 | Herd-/General-Key-Diagramm | ❔ (nur F1) | F1 |
| NV08 | Ermittler vor Monitor-Wand | ✅ | F1, F2, F3, F4 |
| NV09 | Kohoutek historischer Anti-Tail | ❔ (nur F1) | F1 |
| NV10 | Green-Bank-Dish bei Nacht | ✅ | F1, F2, F3, F4 |
| NV11 | Berkeley-Studentin nachts an Konsolen | ✅ | F1, F2, F3, F4 |
| NV13 | Komet zieht auf Linie weiter (never turned) | ✅ | F1, F2, F4 |
| NV14 | Würfel/Wahrscheinlichkeit (look-elsewhere) | ✅ | F1, F2, F3, F4 |
| NV15 | Tabloid-Headline-Wand (ALIEN…) | ⚠️ absichtliche Text-Requisite, teils KI-Kauderwelsch — nur beiläufig/kurz, nie Standbild-Fokus | F1, F2, F3, F4 |

## Herkunft F2 (NW-Serie, `folge-02/clips/`)
| ID | Motiv | Status | Verwendet in |
|---|---|---|---|
| NW01 | K2-18b Hycean-Ozeanwelt (Letterbox-Balken eingebrannt) | ✅ | F2 |
| NW02 | Erdozean, leuchtendes Plankton | ✅ | F2 |
| NW03 | JWST schwenkt (echtes NASA-Logo — diegetisch ok) | ✅ | F2 |
| NW04 | Roter Zwerg + Transit | ✅ | F2 |
| NW05 | Wackelnde Spektrum-Linie auf Screens | ✅ | F2, F3, F4 |
| NW06 | DMS-Molekül über Ozean | ✅ | F2 |
| NW07 | Titan-artiger Dunstmond (Letterbox) | ✅ | F2 |
| NW08 | Toter Komet 67P | ✅ | F2 |
| NW09 | Laser-Spektroskopie-Labor | ✅ | F2 |
| NW10 | Triptychon Ozean/Gasball/Magma | ✅ | F2 |
| NW11 | Magma-Welt nah | ✅ | F2 |
| NW12 | Blitzsturm überm Meer | ✅ | F2 |
| NW13 | Konturloser Mini-Neptun | ✅ | F2 |

## Herkunft F3 (NX-Serie, `folge-03/clips/`)
| ID | Motiv | Status | Verwendet in |
|---|---|---|---|
| NX01 | HERO: Voyager winzig vor Heliopausen-Grenze | ✅ | F3 |
| NX02 | 1977 Titan-Centaur-Start (Archiv-Look) | ✅ | F3 |
| NX03 | Golden Record Makro (echte Gravuren — diegetisch) | ✅ | F3 |
| NX04 | Pale Blue Dot (Letterbox) | ✅ | F3 |
| NX05 | Heliopausen-Plasmavorhang | ✅ | F3 |
| NX06 | Magnetfeld-Linien um Heliosphäre | ✅ | F3 |
| NX07 | Oszilloskop „Hum"-Wellenform | ⚠️ Readout „0.04 Hz" physikalisch fragwürdig — bei KÜNFTIGER Nutzung croppen/ersetzen (in F3/F4 bereits verschifft) | F3, F4 |
| NX08 | 70er-Speicherplatine (historisch korrekt „INTEL 1702A") | ✅ | F3 |
| NX09 | JPL-Nacht Garble-Screen | ⛔ | F3* |
| NX10 | Thruster-Puff an der Sonde | ✅ | F3 |
| NX12 | Roter Zwerg fern, Sonde driftet (40.000 J.) | ✅ | F3 |
| NX13 | Heizleitungen dimmen (Big Bang Seg 8) | ✅ | F3 |

## Herkunft F4 (NY/NZ-Serie, `folge-04/clips/`)
| ID | Motiv | Status | Verwendet in |
|---|---|---|---|
| NY01 | HERO 4K: 6EQUJ5-Fanfold-Printout (diegetischer Ehman-Text ERLAUBT) | ✅ | F4, F2 (Fix-Outro) |
| NY02 | Big Ear 1977 Kraus-Typ (kein Dish!) | ✅ | F4 |
| NY03 | Nadeldrucker im Dunkel | ✅ | F4 |
| NY04 | Sagittarius-Sternfeld, 2 Beam-Glows | ✅ | F4 |
| NY05 | Wasserstoff-Linie abstrakt | ✅ | F4 |
| NY06 | Kalte dunkle H-Wolke | ✅ | F4 |
| NY07 | Magnetar-Flare | ✅ | F4 |
| NY08 | H-Wolke leuchtet auf (Natur-Laser) | ✅ | F4 |
| NY09 | Arecibo majestätisch | ✅ | F4 |
| NY10 | Arecibo-Ruine | ✅ | F4 |
| NY11 | Golfplatz im Morgennebel (Big-Ear-Killer-Beat) | ✅ | F4 |
| NY12 | Archivraum Endlospapier (40.000 Blips) | ✅ | F4 |
| NZ01 | Forensik-Kontrollraum 2 Analysten (NX09-Ersatz) | ✅ | F4 |

\* = in dieser Folge ursprünglich verschifft; F2 per QC-Fix 17.07. bereinigt, **F3-Fix offen** (NX09→NZ01, NV05→NY01, C20→Crop), F1 Bestandsschutz.
