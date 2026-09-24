# Immobilienfotos für das Exposé aufbereiten

`process_real_estate_photos.py` bearbeitet alle JPG-, JPEG- und PNG-Fotos in einem
Ordner automatisch so, wie ein Immobilienfotograf es von Hand tun würde: heller,
neutraler, gerader. Es arbeitet nur mit klassischen fotografischen Korrekturen.
Nichts wird hinzugefügt, entfernt oder retuschiert.

## Installation

Voraussetzung ist Python 3.9 oder neuer ([python.org](https://www.python.org/downloads/);
unter Windows beim Installieren „Add python.exe to PATH“ anhaken).

**macOS / Linux** (Terminal):

```bash
cd immobilien-expose
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows** (Eingabeaufforderung `cmd`):

```bat
cd immobilien-expose
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

In der PowerShell heißt die Aktivierung `.venv\Scripts\Activate.ps1`. Blockiert
Windows das Skript, vorher einmal `Set-ExecutionPolicy -Scope Process Bypass` ausführen.

## Nutzung

1. Fotos in einen Ordner legen. Eine ZIP-Datei vorher entpacken
   (Windows: Rechtsklick → „Alle extrahieren“).
2. Skript mit dem Ordner aufrufen:

```bash
python process_real_estate_photos.py ./input_photos
```

Pfade mit Leerzeichen gehören in Anführungszeichen:

```bat
python process_real_estate_photos.py "C:\Users\Anna\Downloads\Fotos Wohnung"
```

Die fertigen Bilder liegen danach im Unterordner `output_expose` des Fotoordners,
im Beispiel also in `./input_photos/output_expose/`. Die Originale werden nie verändert.

Nützliche Optionen:

| Option | Wirkung |
|---|---|
| `-o ORDNER` | anderer Ausgabeordner |
| `--compare` | zusätzlich Vorher/Nachher-Bilder in `output_expose/_vergleich/` |
| `-r` | auch Unterordner verarbeiten (die Ordnerstruktur wird übernommen) |
| `-j 4` | 4 Bilder parallel verarbeiten; braucht je Prozess ca. 1–1,5 GB RAM bei 12-MP-Fotos, gut 2 GB bei 24 MP |
| `-q 95` | JPEG-Qualität (Standard 92) |
| `--max-size 3000` | lange Kante auf höchstens 3000 px verkleinern (z. B. für Portale); vergrößert nie |
| `--max-crop 0.05` | Geometriekorrektur darf je Bildseite höchstens 5 % abschneiden. Ausdrücklich gesetzt, gilt das auch für das Ausrichten des Horizonts. |
| `--vertical-strength 0.8` | Senkrechten nur zu 80 % begradigen (wirkt manchmal natürlicher) |
| `--focal35 13` | Kleinbild-Brennweite angeben, wenn das EXIF fehlt (z. B. Ultraweitwinkel) |
| `--no-geometry` | keine Objektiv-, Horizont- oder Senkrechtenkorrektur |
| `--no-lens`, `--no-perspective`, `--no-denoise` | einzelne Schritte abschalten |
| `--lens-k -0.05` | Objektivverzeichnung manuell vorgeben (negativ = tonnenförmig) |
| `--warmth 0` | ganz neutraler statt leicht warmer Look |
| `--strip-gps` | GPS-Position aus EXIF und XMP entfernen |
| `--skip-existing` | Fotos überspringen, die schon bearbeitet wurden und seitdem unverändert sind |
| `-v` | alle Einzelentscheidungen im Terminal anzeigen |

Alle Optionen: `python process_real_estate_photos.py --help`
(unter macOS/Linux ggf. `python3` statt `python`).

## Was das Skript macht

Die Reihenfolge ist bewusst gewählt.

1. **Laden** – EXIF-Ausrichtung anwenden, eingebettete Farbprofile (z. B. Display P3
   vom iPhone, Adobe RGB) nach sRGB umrechnen, transparente PNG-Bereiche auf Weiß legen.
2. **Rauschreduzierung** – das Rauschen wird auf strukturarmen Flächen gemessen.
   Farbrauschen wird sanft geglättet. Helligkeitsrauschen wird nur bei deutlich
   verrauschten Bildern und nur teilweise reduziert, damit feine Risse, Fugen und
   Flecken sichtbar bleiben.
3. **Geometrie** in *einem* Rechenschritt, damit das Bild nur einmal umgerechnet wird:
   - **Objektivverzeichnung**: Gerade Kanten müssen gerade sein. Das Skript sucht die
     Korrektur, die möglichst viele lange Kanten am Bildrand begradigt. Korrigiert wird
     nur eindeutige, tonnenförmige Verzeichnung (typisch für Weitwinkel).
   - **Horizont und stürzende Linien**: Senkrechte Kanten (Türzargen, Raumecken,
     Fensterrahmen, Fassaden) werden erkannt und ihr gemeinsamer Fluchtpunkt bestimmt.
     Eine virtuelle Drehung der Kamera stellt sie lotrecht und richtet den Horizont aus.
     Konvergierende Dachsparren werden in einem zweiten Durchgang aussortiert. Hängt
     das Ergebnis an einzelnen Linien (z. B. einer schrägen Dachkante), wird lieber
     nicht korrigiert als falsch.
   - **Zuschnitt**: nur so weit, dass keine leeren Ränder entstehen. Das Seitenverhältnis
     bleibt, damit alle Bilder einheitlich wirken. Für das Begradigen der Senkrechten
     gehen an jeder Stelle jeder Bildkante höchstens 8 % verloren. Würde die volle
     Korrektur mehr kosten, wird sie abgeschwächt; das Protokoll nennt dann den
     gemessenen Wert und den korrigierten Anteil. Einen schiefen Horizont auszurichten
     kostet zwangsläufig die Bildecken; bei starker Schräglage (über ca. 3°) kann das
     etwas mehr als 8 % sein. Mindestens 72 % des Bildinhalts bleiben immer erhalten.
4. **Ton und Farbe** – mit den gleichen Zielwerten für alle Bilder, daher ein
   einheitlicher Look:
   - Weißabgleich auf den neutralsten Flächen (Wände, Decken, Fugen). Beige Fliesen,
     Holz, Ziegel oder Himmel zählen nicht. Bei Mischlicht (Lampe und Fenster) werden
     Tageslicht-Flächen nicht ins Blaue geschoben. Ein gleichmäßiger, starker
     Kunstlichtstich wird kräftiger korrigiert.
   - Belichtung auf eine einheitliche Zielhelligkeit. Helle Räume werden nicht abgedunkelt.
   - Schatten aufhellen und echte Lichter absenken, nur großflächig und kantenerhaltend.
     Feine Details bleiben unverändert, deshalb entsteht kein HDR-Look. Große helle
     Flächen wie der Himmel werden so geschützt, dass kein Farbkanal ausbrennt.
   - Schwarz- und Weißpunkt, sanfte S-Kurve für Kontrast, Dynamik (Vibrance):
     blasse Farben werden etwas kräftiger, satte Farben bleiben, wie sie sind. Die
     Buntheit darf gegenüber dem Original nur maßvoll steigen.
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
- **Stark geneigte Kamera**: Wurde steil nach unten oder oben fotografiert, lassen
  sich die Senkrechten nicht vollständig begradigen, ohne viel abzuschneiden. Das
  Skript korrigiert dann teilweise und schreibt das ins Protokoll. Für perfekte
  Senkrechten die Kamera beim Fotografieren waagrecht halten (Kamerahöhe ca. 1,20–1,50 m)
  und lieber etwas weiter fotografieren.
- **Objektivverzeichnung ohne Profil**: Smartphones korrigieren die Verzeichnung meist
  schon selbst. Die blinde Schätzung greift nur bei eindeutigem Befund. Bei bekanntem
  Objektiv lässt sich der Wert mit `--lens-k` vorgeben.
- **Mischlicht** (Glühlampe und Tageslicht): Ein Weißabgleich für das ganze Bild kann
  nur einen Kompromiss finden. Das Skript korrigiert einen Kunstlichtstich deshalb
  bewusst nur teilweise; ein Rest Wärme bleibt.
- **Fehlende EXIF-Daten**: Über WhatsApp verschickte Fotos haben keine EXIF-Daten und
  sind stark komprimiert. Dann nimmt das Skript 24 mm Kleinbild-Brennweite an. Das
  ändert nur leicht die Proportionen nach der Senkrechtenkorrektur, nicht die
  Geradheit. Am besten die Originaldateien aus Kamera oder Handy verwenden.

## Protokoll und Fehler

Jeder Lauf schreibt `output_expose/verarbeitung.log`. Dort steht pro Bild, was
korrigiert wurde: Rauschen, Drehung, Neigung, Zuschnitt, Weißabgleich, Belichtung.
Kann ein Bild nicht gelesen werden, wird der Fehler mit Ursache protokolliert
und die übrigen Bilder werden trotzdem verarbeitet. Das gilt auch, wenn bei `-j`
ein Prozess abstürzt: Die betroffenen Bilder werden dann einzeln wiederholt.
Rückgabewert: `0` = alles in Ordnung, `1` = mindestens ein Bild fehlgeschlagen,
`2` = Eingabe fehlt, ungültige Option oder keine Bilder gefunden, `130` = mit Strg+C abgebrochen.

Dateinamen bleiben erhalten. JPEGs behalten ihren Namen exakt, PNGs werden zu
`.jpg`. Gibt es `foto.jpg` und `foto.png`, heißt das zweite `foto_png.jpg`.
Übersprungen werden versteckte Dateien, macOS-Hilfsdateien (`._foto.jpg`),
NAS-Vorschauordner (`@eaDir`), Ausgabeordner früherer Läufe und Bilder mit weniger
als 320 px an der kürzeren Kante.

## Tests

```bash
pip install pytest
python -m pytest -q
```
