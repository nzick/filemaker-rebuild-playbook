# Playbook: FileMaker-Anwendung als Web-App neu entwickeln

Erprobt an mehreren Neuentwicklungen (u. a. eine Anwendung mit über 100 Tabellen,
300 Skripten und 270 Layouts). Ziel: **gleiches fachliches Verhalten wie in FileMaker**, moderne Architektur,
sofort lokal lauffähig, 100 % getestet, betriebsbereit (Docker, CI/CD).

Die Phasen bauen aufeinander auf. Jede Phase endet mit einem Commit und einem kurzen Bericht an den
Auftraggeber: was erledigt ist, was offen ist, was nicht geprüft werden konnte.

---

## Grundsätze (gelten in jeder Phase)

1. **Verhalten wie in FileMaker.** Texte, Formeln und Regeln 1:1 übernehmen, nichts selbst formulieren.
   Abweichungen, auch Verbesserungen, nur nach ausdrücklicher Bestätigung. Jede Entscheidung bekommt eine
   Nummer (E-1, E-2, …) in `docs/ANALYSE.md`, mit Datum und Herkunft („Ihre Entscheidung vom …“).
2. **Fehler aus FileMaker sichtbar machen statt still korrigieren.** Wirkungslose Prüfungen, unerreichbare
   Zweige und hartkodierte Konten werden als Entscheidung vorgelegt: 1:1 übernehmen, korrigieren oder weglassen.
3. **Geheimnisse nie übernehmen.** Passwörter und ODBC-Zugangsdaten aus dem DDR weder in Code, Doku noch Chat
   wiederholen, sondern nur als Sicherheitsbefund mit Rotationsempfehlung melden.
4. **Echte Daten bleiben lokal.** Exporte mit Personendaten liegen in einem git-ignorierten Ordner
   (z. B. `import-lokal/`) und werden nie committet. In Chats und Logs keine Namen oder Werte ausgeben.
   Test- und Demodaten werden pseudonymisiert.
5. **Mit Mocks sofort lauffähig.** Jedes Fremdsystem hat einen Adapter mit Mock, umschaltbar per `*_MODE`.
   Mock-Benutzer je Rolle, Passwort = Login.
6. **Rechte serverseitig.** Buttons auszublenden reicht nicht. Jede Aktion prüft das Recht im Backend, und
   Tests sichern 403/422 ab.
7. **Qualität als Pflicht, nicht als Ziel.** Lint 0/0, 100 % Testabdeckung, per Schwellenwert erzwungen,
   Produktions-Build grün. Ausnahmen nur begründet im Code.
8. **Ehrlich berichten.** Was nicht verifiziert wurde (echte Fremdsysteme, Docker, Mail-Versand), steht im
   Bericht. „Erledigt“ heißt geprüft.

---

## Phase 0 – Vorbereitung

- Extrakte besorgen: DDR (`<Datei>_fmp12.xml`) und Datenbankbericht je FileMaker-Datei, auch für Dateien,
  auf die per Dateiverweis zugegriffen wird. Dazu CSV- oder Excel-Exporte der Daten, das Logo und
  Designsystem-Vorgaben.
- Referenzprojekt festlegen: Ein bereits nach diesem Schema gebautes Projekt liefert Basisklassen
  (`core/`, `db/`, `auth/`, `shared/`), Design, Lint- und Sonar-Konfiguration sowie den Doku-Aufbau. Ab dem
  zweiten Projekt spart das die meiste Zeit.
- Projektordner und Git-Repository anlegen und `.gitignore` sofort um `import-lokal/`, `.env`,
  Datenverzeichnisse und Backups ergänzen.
- Start-Prompt aus `START-PROMPT.md` ausfüllen.

## Phase 1 – Analyse der FileMaker-Extrakte

- DDR ist UTF-16: `scripts/ddr_inventar.py` konvertiert selbst und liefert das Inventar: Basistabellen,
  Tabellenauftreten, Beziehungen, Skripte, Layouts, Wertelisten, Berechtigungssets, Konten, eigene Funktionen,
  externe Datenquellen und Sicherheitsbefunde.
- `--texte` zieht alle Textobjekte der Layouts heraus. Drucklayouts enthalten Brief-, Zahlungs-, Mahn- und
  Checklistentexte, und die werden wörtlich übernommen.
- Skripte fachlich lesen: Welche sind Anwendungsfälle, welche UI-Steuerung, welche Altlast? Das Mapping
  FM-Skript → neue Funktion kommt in `docs/ANALYSE.md`, Abschnitt „Skripte → Funktionen“.
- Bei mehreren Formelvarianten (auskommentiert/aktiv) gilt die aktive.
- Felder, die aus anderen Dateien kommen, stehen als offene Punkte mit Anforderung des fehlenden DDR in der Doku.
- Ungenutzte Objekte nur benennen, nicht nachbauen.
- **Ergebnis:** `docs/ANALYSE.md` mit Umfang, fachlichem Ablauf, Datenmodell, Skript-Mapping, Rollen,
  Altlasten, Entscheidungen, Sicherheitsbefund und offenen Punkten. Diese Entscheidungen bestätigen lassen,
  bevor die Umsetzung beginnt.

## Phase 2 – Gerüst und Architektur

- **Backend:** Node.js 22 LTS, TypeScript strict, Express 5, Zod, PostgreSQL 16. Lokal läuft das eingebettete
  PGlite hinter derselben Datenbank-Abstraktion, ganz ohne Installation. Migrationen sind SQL-Dateien mit
  Prüfsumme.
- **Frontend:** Angular (aktuelle Version), standalone, Signals, zoneless, OnPush, strictTemplates, kein `any`.
- **Webserver:** nginx (SPA + Reverse-Proxy `/api`, Security-Header, CSP ohne Inline-Skripte, Angular mit
  `inlineCritical=false`). Docker Compose mit `db`, `backend` und `web`.
- **Schichten:** controllers → services → repositories → db. Fachlogik liegt in `domain/` als Klassen ohne
  DB-Zugriff. Die Composition Root (`Application`) arbeitet mit Konstruktor-Injektion, ohne Singletons;
  die Konfiguration ist ein unveränderliches `AppConfig.fromEnv()`.
- **Patterns** gezielt einsetzen und mit Fundstelle in `docs/ARCHITEKTUR.md` dokumentieren: Abstract Factory
  (Integrationen), Adapter, Template Method (Controller, PDF), Strategy (Freigabe je Prozessart, Versand),
  Specification + Composite (Prüfregeln), Chain of Responsibility (Vorbelegungen/Lookups), Builder (SQL, XML),
  Repository, Value Objects, Fehlerklassen-Hierarchie.
- SQL immer parametrisiert, dynamische Spaltennamen nur über geprüfte Bezeichner.

## Phase 3 – Fachlichkeit umsetzen

- Jedes fachlich relevante Skript wird ein Anwendungsfall oder Endpunkt. Meldungstexte bleiben wörtlich.
- Rollen aus den Berechtigungssets ableiten und Objekt- bzw. Mandantenfilter je Benutzer umsetzen.
- Optimistic Locking (Versionsnummer), Änderungshistorie je Datensatz, Logbuch für Löschungen und Abgleiche.
- **Audit-Trail per DB-Trigger:** Er hängt sich automatisch an jede neue Fachtabelle, enthält Quelle
  (manuell, Import, System) und Vorgangs-ID und ist als CSV exportierbar.
- Belegnummern transaktionssicher vergeben und danach sperren (GoBD). DSGVO-Löschung bzw. -Anonymisierung
  mit doppelter Bestätigung.
- PDFs nach den FM-Drucklayouts, mit Texten wörtlich, Hausschrift eingebettet und Probeexemplar mit Wasserzeichen.
- Rechnungen, falls vorhanden: XRechnung 3.0 (UBL 2.1, EN 16931), XSD-Prüfung, Archiv mit SHA-256.
- **Statuswerte, die aus Kindsätzen abgeleitet sind** (z. B. „Auftrag erledigt, wenn alle Positionen
  erledigt“), auch direkt nach dem Anlegen berechnen. Sonst bleibt ein Datensatz ohne Kindsätze für immer offen.

## Phase 4 – Fremdsysteme und Importe

- Für jedes System gibt es einen Adapter mit Mock. Fällt ein System aus, laufen die anderen weiter; der Fehler
  steht im Ergebnis und im Log.
- `docs/SCHNITTSTELLEN.md`: alle Felder je System mit Bedarf (Pflicht / Druck / optional), bisherigem
  FM-Feldnamen und View-Spezifikation (Schema, Spalten, Typen, Schlüssel, NULL-Regeln, Abnahmekriterien).
- Anmeldung über AD-Gruppen → Rollen, bevorzugt per OIDC/Entra ID, LDAP nur als Alternative. Vor der
  Umsetzung klären.
- Stammdaten aus Fremdsystemen sind nur lesbar (403 im Backend). Lokal gepflegte Zusatzfelder werden als
  „lokal“ markiert, und der Abgleich überschreibt sie nicht.
- **Eingehende Lieferungen** (z. B. HR-/SAP-Vollbestand als CSV):
  - Nur echte Änderungen erkennen, also gegen die vorige Lieferung und den Bestand vergleichen.
  - Daraus *Vorschläge* (Entwürfe) erzeugen, keine direkten Änderungen.
  - Jedes Ereignis bekommt einen Status mit Empfehlung (offen, „ignorieren empfohlen“, bereits erfasst,
    freigegeben, ignoriert). Kein Ereignis bleibt „ohne Vorschlag“.
  - „Änderung ignorieren“ mit Begründung und „wieder aufnehmen“, beides im Logbuch.
  - Stabile Schlüssel je Ereignis verwenden, damit nichts doppelt kommt.
  - Felder, die aus der Lieferung stammen, im Formular sperren.
- Datenübernahme-Skript aus FM-Exporten: IDs erhalten, Sequenzen nachziehen, `--dry-run`.

## Phase 5 – Bedienung und Design

- Entweder-oder-Felder nie gleichzeitig zeigen: erst die Art wählen (Segment), dann das passende Feld.
  Ein Wechsel leert die übrigen.
- Pflichtfelder nach Zweck kennzeichnen (immer / für Freigabe / nur in bestimmten Fällen), mit Legende.
- Live-Checkliste „Was fehlt noch?“ je Workflow-Schritt.
- Editor-Muster: Tabs, Karten, Seitenleiste, Speichern/Verwerfen-Schutz, Aktionen nach Rechten.
- **Prozess-Lebenslauf sichtbar machen:** In Erfassung → In Umsetzung → Abgeschlossen, mit Filtern,
  Überfälligkeit und „liegt seit n Tagen“.
- Barrierefreiheit: Labels, Enter auf Tabellenzeilen, Escape schließt Dialoge.
- **Designsystem vollständig:**
  - Alle Farben, Abstände, Radien und Schriftgrößen als CSS-Variablen (Tokens), keine Hex-Werte oder
    px-Schriftgrößen in Komponenten.
  - Hausschrift per `@font-face` (WOFF) einbinden, mit `font-synthesis: none` und
    `button, input, select, textarea { font-family: inherit }`.
  - Die Hausschrift auch in PDFs einbetten (TTF). Zeichen, die die Schrift nicht hat, auf das Grundzeichen
    zurückführen.
  - Lizenz prüfen: Schriftdateien nur in privaten Repositories ablegen.

## Phase 6 – Erweiterungen nach Bedarf

Typische Wünsche nach dem 1:1-Nachbau. Jede Erweiterung bekommt eine E-Nummer:

- Eingabeprüfungen (E-Mail, Telefon, IBAN, Prüfziffern), auch im Backend.
- Integration weiterer FM-Dateien, die bisher eigenständig liefen.
- **E-Mail-Benachrichtigungen:**
  - Ereigniskatalog, persönliche Abos (sofort oder als Sammelmail) und Empfängerregeln im Admin-Bereich.
  - Erinnerungen vor der Frist und mehrstufige Eskalation bei Überfälligkeit.
  - Versandprotokoll mit Deduplizierung, Deep-Link zur Bearbeitung.
  - Ein Zeitplan-Job übernimmt den Versand.
- Übersicht/Dashboard mit hervorgehobener Kachel „zu bearbeiten“.

## Phase 7 – Qualität

- ESLint mit gts (Google TypeScript Style + Prettier), eslint-plugin-sonarjs und angular-eslint
  (Template-Barrierefreiheit, OnPush, Signals). Ziel: 0 Fehler, 0 Warnungen.
- Tests:
  - Unit-Tests für die Fachlogik.
  - API-Tests gegen Mocks mit In-Memory-PGlite.
  - Adapter-Tests mit simulierten Quellen.
  - Frontend-Tests mit vitest.
- **100 % Abdeckung als Schwelle** in Backend und Frontend (Statements, Branches, Functions, Lines).
- `sonar-project.properties` für SonarQube (ESLint-, lcov- und JUnit-Berichte).
- Abhängigkeiten in exakten, mindestens ca. zwei Wochen alten Versionen. `npm audit --omit=dev
  --audit-level=high` muss sauber sein.

## Phase 8 – Betrieb und CI/CD

- **Updates ohne Datenverlust:**
  - Migrationen mit Prüfsumme; geänderte, bereits gelaufene Migrationen brechen ab.
  - Vor jeder Migration automatisch sichern.
  - `scripts/update.sh`: Sicherung → neue Images → Neustart → Warten auf Health-Check.
- `docs/BETRIEB.md`: Integrationen umschalten, Datenübernahme, Produktions-Checkliste, Docker, Import-Zeitplan,
  Audit, Benachrichtigungen.
- **Pipeline** (Azure DevOps oder GitHub Actions):
  - Prüfung: Backend (Lint, Typecheck, Tests mit Abdeckung, Build), Frontend (Lint, Tests, Produktions-Build),
    Migrationen gegen echtes PostgreSQL (zweimal laufen lassen), Docker-Images und `npm audit`.
  - Optional SonarQube.
  - Optionales Deploy per SSH, nur von `main` und mit Freigabe über eine Umgebung.
- **Vor dem ersten Pipeline-Lauf `npm ci` unter Linux testen**, siehe `LESSONS-LEARNED.md` (Lockfile vom Mac).

## Phase 9 – Abnahme

Checkliste `checklisten/ABSCHLUSS.md` abarbeiten, die App im Browser je Rolle durchklicken, PDFs ansehen,
offene Punkte und nicht Verifiziertes klar berichten.

---

## Dokumentation (immer aktuell halten)

| Datei | Inhalt |
|---|---|
| `README.md` | Schnellstart (Docker / lokal), Mock-Benutzer, Installation Schritt für Schritt, Tests, CI/CD |
| `docs/ANALYSE.md` | FM → neu, Skript-Mapping, Rollen, Altlasten, **Entscheidungen E-n**, Sicherheitsbefund, offene Punkte |
| `docs/ARCHITEKTUR.md` | Schichten, Patterns mit Fundstelle, Querschnittsregeln, Fremdsysteme austauschen |
| `docs/BETRIEB.md` | Integrationen, Datenübernahme, Produktion, Updates, Import, Audit, CI/CD |
| `docs/SCHNITTSTELLEN.md` | Felder je Fremdsystem, View-Spezifikationen, Minimal-Satz für den Echtbetrieb |

Vorlagen liegen in `vorlagen/`.
