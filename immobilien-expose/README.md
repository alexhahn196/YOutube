# Immobilienfotos für das Exposé aufbereiten

`process_real_estate_photos.py` bearbeitet alle JPG-, JPEG- und PNG-Fotos in einem
Ordner automatisch so, wie ein Immobilienfotograf es von Hand tun würde: heller,
neutraler, gerader. Es arbeitet nur mit klassischen fotografischen Korrekturen.
Nichts wird hinzugefügt, entfernt oder retuschiert.

## Installation

Voraussetzung ist Python 3.9 oder neuer.

```bash
cd immobilien-expose
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Nutzung

```bash
python process_real_estate_photos.py ./input_photos
```

Die fertigen Bilder liegen danach in `./input_photos/output_expose/`.
Die Originale werden nie verändert.

Nützliche Optionen:

| Option | Wirkung |
|---|---|
| `-o ORDNER` | anderer Ausgabeordner |
| `--compare` | zusätzlich Vorher/Nachher-Bilder in `output_expose/_vergleich/` |
| `-j 4` | 4 Bilder parallel verarbeiten (braucht ca. 1 GB RAM je Prozess bei 12-MP-Fotos) |
| `-r` | auch Unterordner verarbeiten (Ordnerstruktur wird übernommen) |
| `-q 95` | JPEG-Qualität (Standard 92) |
| `--max-size 3000` | lange Kante auf höchstens 3000 px verkleinern (z. B. für Portale); vergrößert nie |
| `--max-crop 0.05` | Geometriekorrektur darf je Seite höchstens 5 % abschneiden (Standard 8 %) |
| `--vertical-strength 0.8` | Senkrechten nur zu 80 % begradigen (wirkt manchmal natürlicher) |
| `--focal35 13` | Kleinbild-Brennweite angeben, wenn das EXIF fehlt (z. B. Ultraweitwinkel) |
| `--no-geometry` | keine Objektiv-, Horizont- oder Senkrechtenkorrektur |
| `--no-lens`, `--no-perspective`, `--no-denoise` | einzelne Schritte abschalten |
| `--lens-k -0.05` | Objektivverzeichnung manuell vorgeben (negativ = tonnenförmig) |
| `--warmth 0` | ganz neutraler statt leicht warmer Look |
| `--strip-gps` | GPS-Position aus den EXIF-Daten entfernen |
| `--skip-existing` | schon bearbeitete Bilder nicht erneut bearbeiten |
| `-v` | alle Einzelentscheidungen im Terminal anzeigen |

Alle Optionen: `python process_real_estate_photos.py --help`

## Was das Skript macht

Die Reihenfolge ist bewusst gewählt.

1. **Laden** – EXIF-Ausrichtung anwenden, eingebettete Farbprofile (z. B. Display P3
   vom iPhone) nach sRGB umrechnen, transparente PNG-Bereiche auf Weiß legen.
2. **Rauschreduzierung** – das Rauschen wird auf strukturarmen Flächen gemessen.
   Nur wenn es sichtbar ist, wird es mit Non-Local-Means gemildert, die Stärke
   richtet sich nach dem Messwert. Feine Strukturen wie Fugen oder Risse bleiben.
3. **Geometrie** in *einem* Rechenschritt, damit das Bild nur einmal umgerechnet wird:
   - **Objektivverzeichnung**: gerade Kanten müssen gerade sein. Das Skript sucht die
     Korrektur, die möglichst viele lange Kanten am Bildrand begradigt. Nur bei
     eindeutigem Ergebnis wird korrigiert.
   - **Horizont und stürzende Linien**: senkrechte Kanten (Türzargen, Raumecken,
     Fensterrahmen, Fassaden) werden erkannt und ihr gemeinsamer Fluchtpunkt
     bestimmt. Eine virtuelle Drehung der Kamera stellt sie lotrecht und richtet den
     Horizont aus. Dachschrägen werden dabei ignoriert.
   - **Zuschnitt**: nur so weit, dass keine leeren Ränder entstehen. Das
     Seitenverhältnis bleibt, damit alle Bilder einheitlich wirken. Pro Bildseite
     gehen höchstens 8 % verloren. Würde die volle Korrektur mehr kosten, wird die
     Neigungskorrektur abgeschwächt. Decke, Boden und Lampen bleiben so im Bild.
4. **Ton und Farbe** – mit den gleichen Zielwerten für alle Bilder, daher ein
   einheitlicher Look:
   - Weißabgleich auf neutralen Flächen (Wände, Decken, Fassaden). Farbige Flächen
     wie Holz, Ziegel oder Himmel zählen nicht. Sehr starke Farbstiche werden nur
     teilweise korrigiert, sonst würde bei Mischlicht das Tageslicht blau.
   - Belichtung auf eine einheitliche Zielhelligkeit.
   - Schatten aufhellen und Lichter absenken, nur großflächig und kantenerhaltend.
     Feine Details bleiben unverändert, deshalb entsteht kein HDR-Look.
   - Schwarz- und Weißpunkt, sanfte S-Kurve für Kontrast, Dynamik (Vibrance):
     blasse Farben werden etwas kräftiger, satte Farben bleiben, wie sie sind.
5. **Schärfe** – leichte Ausgabeschärfung, nur auf der Helligkeit, mit Schwelle,
   damit Rauschen nicht mitgeschärft wird.
6. **Speichern** – JPEG mit Qualität 92, volle Farbauflösung (4:4:4), sRGB-Profil.
   EXIF (inkl. Aufnahmedatum und Kamera), XMP und Auflösung werden übernommen,
   die Ausrichtung wird auf „normal“ gesetzt. Das Bild wird nie vergrößert.

## Was das Skript bewusst nicht tut

- Keine Retusche. Wände, Fenster, Möbel, Aussicht, Schäden, Flecken und Risse
  bleiben, wie sie sind. Nichts wird weich gezeichnet, um Mängel zu verbergen.
- Kein Himmel-Austausch, keine virtuellen Möbel, keine KI-Bildgenerierung.
- Kein ästhetischer Zuschnitt. Beschnitten wird nur, was die Geometriekorrektur
  zwingend erfordert.

## Grenzen der Automatik

- **Ausgebrannte Fenster**: Was im Foto reinweiß ist, enthält keine Bildinformation
  mehr und lässt sich nicht zurückholen. Das Skript senkt nur Lichter, in denen
  noch Zeichnung steckt, und hält reinweiße Flächen sauber weiß statt grau.
  Wer Fensteraussichten zeigen will, braucht Belichtungsreihen (HDR-Modus der Kamera).
- **Objektivverzeichnung ohne Profil**: Smartphones korrigieren die Verzeichnung
  meist schon selbst. Die blinde Schätzung greift nur bei eindeutigem Befund.
  Bei bekanntem Objektiv lässt sich der Wert mit `--lens-k` vorgeben.
- **Stark geneigte Kamera**: Wurde steil nach unten oder oben fotografiert, kann das
  Skript die Senkrechten nicht vollständig begradigen, ohne viel abzuschneiden. Es
  korrigiert dann teilweise und schreibt das ins Protokoll. Für perfekte Senkrechten
  die Kamera beim Fotografieren waagrecht halten (Kamerahöhe ca. 1,20–1,50 m).
- **Mischlicht** (Glühlampe und Tageslicht): Ein globaler Weißabgleich kann nur
  einen Kompromiss finden.
- **Fehlende EXIF-Daten**: Über WhatsApp verschickte Fotos haben keine EXIF-Daten.
  Dann nimmt das Skript 24 mm Kleinbild-Brennweite an. Das beeinflusst nur leicht
  die Proportionen nach der Senkrechtenkorrektur, nicht die Geradheit.
  Am besten die Originaldateien aus der Kamera oder dem Handy verwenden.

## Protokoll und Fehler

Jeder Lauf schreibt `output_expose/verarbeitung.log`. Dort steht pro Bild, was
korrigiert wurde: Drehung, Neigung, Zuschnitt, Weißabgleich, Belichtung.
Kann ein Bild nicht gelesen werden, wird der Fehler mit Ursache protokolliert
und die übrigen Bilder werden trotzdem verarbeitet.
Rückgabewert: `0` = alles in Ordnung, `1` = mindestens ein Bild fehlgeschlagen,
`2` = Eingabe fehlt oder keine Bilder gefunden.

Dateinamen bleiben erhalten. JPEGs behalten ihren Namen exakt, PNGs werden zu
`.jpg`. Gibt es `foto.jpg` und `foto.png`, heißt das zweite `foto_png.jpg`.
Versteckte Dateien und macOS-Hilfsdateien (`._foto.jpg`) werden übersprungen,
ebenso Bilder mit weniger als 320 px an der kürzeren Kante.
