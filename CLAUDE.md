# Montageprotokoll-Agent

Der Nutzer diktiert nach jeder Montage (auf Deutsch, oft per Sprache, also mit Tippfehlern) was gemacht wurde. Deine Aufgabe: Protokoll ausfüllen, als PDF erzeugen, zustellen.

## Speicherort / Sicherung
- Alles liegt im Git-Repo `markusunger1990/montageprotokolle` (lokal /home/user/montageprotokolle, Symlink /home/user/montage).
- Zu Beginn einer Montage-Anfrage: falls der Ordner fehlt oder leer ist (Container wurde zurückgesetzt) → Repo per add_repo anhängen und klonen; sonst `git pull` (still).
- Am Ende jeder Montage: `git add -A && git commit -m "Montage <Datum> <Kunde>" && git push -u origin main`.

## Ablauf pro Montage
1. `gedaechtnis.md` lesen (Stammdaten: Monteure, Kunden, Gewohnheiten). NICHT alte Protokolle lesen, außer der Nutzer bezieht sich darauf.
2. Diktat in JSON übertragen → `daten/<JJJJ-MM-TT>_<Kunde-kurz>.json` (Felder siehe Kopf von `fill.py`).
   - Fehlendes aus dem Gedächtnis ergänzen (z. B. Standard-Monteur, Unterschrift-Name/Funktion, Adresse bekannter Kunden).
   - Montagedatum/Unterschriftsdatum: Standard = heute, Format TT.MM.JJJJ. Uhrzeiten "07:30 Uhr".
   - `arbeiten`: sauber formulierte Sätze im Protokollstil, Inhalt nicht erfinden.
   - Wichtige Pflichtangaben (Kunde, Ort, Arbeiten) fehlen und nicht ableitbar → EINE kurze Rückfrage, sonst nicht fragen.
   - Unterschrift-Feld bleibt leer (handschriftlich).
3. `python3 fill.py daten/<datei>.json` → `protokolle/<datei>.pdf`.
4. Versand: `python3 send.py protokolle/<datei>.pdf "Montageprotokoll – <Kunde> – <Datum>" "<2-3 Zeilen Zusammenfassung>"`
   (AgentMail-API, Absender markus-flynn@agentmail.to → markusunger1990@icloud.com; API-Key injiziert der Proxy, nie selbst setzen).
   NICHT den AgentMail-MCP-Connector mit Base64 nutzen – das bläht den Kontext auf. Zusätzlich PDF mit SendUserFile (display: attach) schicken.
5. Kurze Zusammenfassung (2–3 Zeilen) im Chat – nicht das ganze Protokoll wiederholen.
6. Neues/Geändertes Wissen in `gedaechtnis.md` nachtragen (neuer Kunde, neue Adresse, neuer Kollege, Vorlieben/Korrekturen des Nutzers). Eine Zeile in die Montage-Liste.

## Kontext sparsam halten
- Keine PDFs rendern/anschauen, außer der Nutzer meldet ein Layoutproblem.
- `fill.py` nicht lesen, außer zum Ändern.
- Das Gedächtnis kompakt halten (Stichpunkte); Montage-Liste nur eine Zeile pro Montage.

## Vorlage
- `vorlage.pdf` = Vorlage ohne Linien (Wunsch des Nutzers). `vorlage_original.pdf` = unveränderte Originalvorlage mit Linien.
