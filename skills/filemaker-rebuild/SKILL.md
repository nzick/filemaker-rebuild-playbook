---
name: filemaker-rebuild
description: Rebuild a FileMaker application as a modern web app (Node/TypeScript/Express/PostgreSQL + Angular) with FileMaker behaviour taken over 1:1. Use when the user wants to analyse a FileMaker DDR (Database Design Report, *_fmp12.xml) or Datenbankbericht, migrate or "neu entwickeln" a FileMaker solution, or continue such a project (ANALYSE.md with decisions E-n, mocks per external system, 100 % coverage, Docker/CI). Also use to extract layout texts or security findings from a DDR.
---

# FileMaker → Web-App neu entwickeln

Dieser Skill führt durch eine FileMaker-Neuentwicklung nach einem erprobten Schema. Die vollständige Anleitung
steht in `references/PLAYBOOK.md`. Lies sie zu Beginn eines neuen Projekts ganz, bei Folgeaufgaben den
passenden Abschnitt.

## Harte Regeln (nie brechen)

1. **Verhalten wie in FileMaker.** Texte, Formeln und Regeln wörtlich übernehmen. Jede Abweichung, auch eine
   Verbesserung, nur nach Bestätigung des Users. Dokumentiert wird sie als `E-n` in `docs/ANALYSE.md`, mit Datum.
2. **Geheimnisse aus dem DDR** (Passwörter, ODBC-Zugangsdaten) niemals übernehmen, ausgeben oder wiederholen.
   Nur den Fundort als Sicherheitsbefund melden und Rotation empfehlen.
3. **Echtdaten** (CSV-/Excel-Exporte mit Personen) bleiben in einem git-ignorierten Ordner. Nie committen, im
   Chat nur Anzahlen nennen, keine Namen oder Werte.
4. **Rechte serverseitig erzwingen**, jedes Fremdsystem mit Mock (`*_MODE`), App mit Mocks sofort lauffähig.
5. **Fertig heißt geprüft:** Lint 0/0, Tests mit 100 % Abdeckung, Builds grün, im Browser durchgeklickt.
   Nicht Verifiziertes ausdrücklich nennen.

## Ablauf

1. **Neues Projekt:** Fehlen Angaben aus `references/START-PROMPT.md` (App-Name, Zielordner,
   Referenzprojekt, Designsystem, Fremdsysteme, Ordner für Echtdaten), frage gezielt nach. Ist der Prompt
   ausgefüllt, folge ihm.
2. **Analyse:** Erzeuge das Inventar mit dem Skript (liest UTF-16 selbst):
   ```bash
   python3 -I <skill-dir>/scripts/ddr_inventar.py <DDR.xml> --texte docs/fm-layout-texte.md > docs/fm-inventar.md
   ```
   Die Layout-Texte sind die Quelle für alle Druck- und Meldungstexte. Die Sicherheitsbefunde des Skripts
   enthalten keine Werte; so bleibt es. Daraus `docs/ANALYSE.md` nach `references/vorlagen/ANALYSE.md`
   aufbauen. Entscheidungen dem User **vor** der Umsetzung vorlegen.
3. **Umsetzung** in den Phasen 2–8 des Playbooks. Bei jeder fachlichen Regel die FM-Quelle (Skript, Zeile,
   Feldformel) im Code-Kommentar oder in ANALYSE.md nennen.
4. **Vor jedem Commit oder Push:** `references/checklisten/ABSCHLUSS.md`. Insbesondere `npm ci` in einem
   leeren Verzeichnis testen; ein auf dem Mac erzeugtes Lockfile kann unter Linux scheitern.
5. **Doku laufend pflegen:** README, `docs/ANALYSE.md`, `ARCHITEKTUR.md`, `BETRIEB.md`, `SCHNITTSTELLEN.md`.
   Vorlagen dafür liegen in `references/vorlagen/`.

## Bekannte Fallen

Lies `references/LESSONS-LEARNED.md`, bevor du Importe, abgeleitete Status, Design/Schriften oder die
CI-Pipeline anfasst. Die wichtigsten Punkte:

- **Abgeleiteter Status:** Er muss auch direkt nach dem Anlegen berechnet werden. Ein Auftrag ohne Positionen
  ist sonst nie „erledigt“.
- **Importe:** Jedes Ereignis bekommt eine automatische Empfehlung, dazu „ignorieren“ mit Begründung und
  stabile Ereignisschlüssel.
- **PGlite:** nie zwei Prozesse auf dasselbe Datenverzeichnis.
- **Lizenzen:** Hausschrift und Logo nur in privaten Repositories.
