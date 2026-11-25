# Lessons Learned

Konkrete Stolpersteine aus echten Projekten, mit Ursache und Gegenmaßnahme.

## Analyse

- **Der DDR ist UTF-16**, und grep oder Editoren finden darin nichts. Immer zuerst konvertieren oder
  `scripts/ddr_inventar.py` nutzen.
- **Zugangsdaten stecken als Formel** (`<Password><Calculation>…`) unter ODBC-Quellen und Dateiverweisen. Wer
  nur den Elementtext prüft, übersieht sie.
- **Drucktexte stehen in Layout-Textobjekten**, nicht in Skripten. Wer Layouts nur strukturell liest, erfindet
  später Texte.
- **Wirkungslose FM-Prüfungen** (z. B. ein Textmuster gegen eine numerische ID): als Entscheidung vorlegen und
  standardmäßig 1:1 übernehmen, damit sich das Verhalten nicht unbemerkt ändert.
- **Hartkodierte Benutzerkonten** in Skripten nicht übernehmen; nachfragen.

## Fachlogik

- **Abgeleiteter Status ohne Kindsätze:** Gilt „keine Positionen ⇒ erledigt“, der Status wird aber nur bei
  einer Positionsänderung neu berechnet, dann bleibt ein leerer Auftrag für immer „neu“. Der Prozess wartet
  dann ewig. Status deshalb direkt nach dem Anlegen bewerten.
- **„Inaktiv“ ist nicht „ausgetreten“:** Ruhende Mitarbeiter sind im Altsystem oft inaktiv, gehören aber zum
  Bestand. Regeln für Änderungen dürfen sie nicht ausfiltern.
- **Importe ohne Vorschlag sind Arbeit ohne Ende:** Jedes Ereignis braucht eine automatische Empfehlung,
  sonst bleiben unklare Einträge liegen. „Ignorieren“ muss es geben, mit Begründung und rückgängig machbar.
- **Stabile Ereignisschlüssel** (z. B. `ART:personalnummer:stichtag`): Damit erkennt der Import, was schon
  vorgeschlagen, freigegeben oder ignoriert wurde, und nichts kommt doppelt.

## Daten und Datenschutz

- Echte Exporte nur in einem git-ignorierten Ordner. Vor jedem Push den ganzen Verlauf prüfen:
  `git log --all --name-only | grep -iE "\.csv|\.xlsx|\.env|import-lokal"`.
- Testdaten pseudonymisieren: Stammdaten (OEs, Profile) dürfen echt sein, Personen nicht.
- Im Chat oder in Logs nie Namen oder Werte aus echten Daten ausgeben, nur Anzahlen.

## Lokale Entwicklung

- **PGlite verträgt nur einen Prozess je Datenverzeichnis.** Kein zweites Backend auf dasselbe `DATA_DIR`
  starten, das kann die Datenbank beschädigen. Für Tests In-Memory-PGlite verwenden.
- Mock-Passwort = Login. Das steht in der README, damit niemand rätselt.

## Design

- Hausschrift in Komponenten erzwingen: Formularelemente erben `font-family` nicht von selbst.
- `font-synthesis: none`, sonst erzeugt der Browser falsches Fett oder Kursiv, wenn ein Schnitt fehlt.
- PDF-Bibliotheken brauchen TTF. Zeichensatz der Schrift prüfen (z. B. `ş`, `Ł`, `µ`) und fehlende Zeichen
  sauber ersetzen.
- Schriftlizenz: nur in privaten Repositories ablegen und in `docs/ARCHITEKTUR.md` vermerken.

## Build und CI

- **`npm ci` bricht unter Linux ab, obwohl es auf dem Mac läuft.** Ursache: Optionale Peer-Abhängigkeiten
  (z. B. `@emnapi/core` und `@emnapi/runtime` von `@napi-rs/wasm-runtime`) fehlen im Lockfile, das auf macOS
  erzeugt wurde. Neu Auflösen hilft nicht. Lösung: die Pakete mit fester Version als devDependencies aufnehmen.
  Test vor dem Push in einem leeren Verzeichnis:
  `cp package*.json $(mktemp -d) && cd $_ && npm ci --ignore-scripts`.
- `npm audit --omit=dev --audit-level=high` als eigener Pipeline-Job: Laufzeit-Lücken blockieren den Lauf,
  Lücken in Dev-Tools nicht.
- Migrationen in der Pipeline zweimal laufen lassen. Der zweite Lauf muss „nichts zu tun“ melden, sonst
  stimmen Prüfsummen oder Idempotenz nicht.
- Tests nach dem Zusammenführen paralleler Arbeiten (Branches, Sessions) auf dem Gesamtstand erneut laufen
  lassen, bevor gepusht wird.

## Arbeiten mit Claude Code

- Große, unabhängige Erweiterungen (z. B. Benachrichtigungen) in eigenen Sessions bauen lassen. Danach auf dem
  Gesamtstand testen.
- Zugangsdaten (Tokens, Passkeys) nicht in den Chat geben. Den Push einmal selbst im Terminal ausführen,
  danach liegt der Token im Schlüsselbund.
- Entscheidungen sofort in `docs/ANALYSE.md` festhalten. Das ist das Gedächtnis des Projekts über Sessions
  hinweg.
