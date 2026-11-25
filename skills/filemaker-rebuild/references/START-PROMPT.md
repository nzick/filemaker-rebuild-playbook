# Start-Prompt (Vorlage)

Platzhalter in `<…>` ersetzen, nicht zutreffende Abschnitte streichen und die Extrakte anhängen.

---

Ich möchte die FileMaker-Anwendung "<APP_NAME>" neu entwickeln. Angehängt sind die FileMaker-Extrakte
(DDR "<APP_NAME>_fmp12.xml" und "Datenbankbericht-<APP_NAME>.xml") sowie unser Logo.
Arbeite im Projektordner <ZIELORDNER>. Antworte auf <SPRACHE>.

Referenz: Die Anwendung "<REFERENZPROJEKT>" unter <PFAD_REFERENZ> ist nach genau diesem Schema gebaut.
Übernimm von dort Architektur, Basisklassen (core/, db/, auth/, shared/), Design (frontend/src/styles.scss,
Logo, Komponentenmuster), Lint-/Sonar-Konfiguration und Doku-Aufbau.
(Ohne Referenzprojekt: diesen Absatz streichen, das Gerüst entsteht nach Abschnitt 2.)

## 1. Analyse der FileMaker-Extrakte
- DDR ist UTF-16: vor der Analyse nach UTF-8 konvertieren (z. B. mit `scripts/ddr_inventar.py`).
- Vollständig auswerten:
  - Basistabellen, Tabellenauftreten, Beziehungen
  - Felder, inkl. Formel- und globaler Felder
  - Skripte, Layouts, Wertelisten
  - Konten/Berechtigungssets
  - externe Datenquellen (Dateiverweise, ODBC)
- Layouts NICHT nur strukturell lesen: Textobjekte (<Data>) in Drucklayouts enthalten Brief-, Zahlungs- und
  Mahntexte. Alle Texte, Formeln und Regeln 1:1 aus FileMaker übernehmen, nichts selbst formulieren.
  Bei mehreren Varianten (auskommentiert/aktiv) gilt die aktive Formel.
- Grundsatz: Verhalten wie in FileMaker. Abweichungen (auch Verbesserungen) nur nach meiner ausdrücklichen
  Bestätigung. Jede Entscheidung in docs/ANALYSE.md festhalten (E-1, E-2, …).
- Ungenutzte Objekte und Altlasten benennen, aber nicht nachbauen.
- Geheimnisse aus dem DDR (Passwörter, ODBC-Zugangsdaten) niemals übernehmen oder wiederholen, nur als
  Sicherheitsbefund melden (Rotation empfehlen).
- Felder, die im DDR fehlen bzw. aus anderen Dateien kommen, als offene Punkte auflisten und die DDRs der
  referenzierten Dateien anfordern.
- Echte Datenexporte liegen in <ORDNER_ECHTDATEN> (git-ignoriert): nie committen, keine Namen oder Werte im
  Chat ausgeben.

## 2. Zielarchitektur
- Backend:
  - Node.js 22, TypeScript (strict), Express 5, Zod, PostgreSQL 16.
  - Lokal ohne Installation über eingebettetes PGlite (gleiche Datenbank-Abstraktion).
  - SQL-Migrationen als Dateien mit Prüfsumme.
- Frontend: Angular (aktuelle Version), Standalone-Komponenten, Signals, zoneless, OnPush überall, typisierte
  Modelle (kein `any`), strictTemplates.
- Webserver: nginx (SPA + Reverse-Proxy /api, Security-Header, CSP ohne Inline-Skripte; Angular-Build daher mit
  inlineCritical=false). Betrieb per Docker Compose (db, backend, web).
- Strikt objektorientiert:
  - Schichten controllers → services → repositories → db.
  - Fachlogik in domain/ als Klassen ohne DB-Zugriff.
  - Composition Root (Application-Klasse) mit Konstruktor-Injektion, keine globalen Singletons.
  - Konfiguration als unveränderliche AppConfig.fromEnv().
- Design Patterns gezielt einsetzen und in docs/ARCHITEKTUR.md mit Fundstelle dokumentieren:
  - Abstract Factory (Integrationen), Factory Method, Adapter
  - Template Method (Controller-Basisklasse, PDF-Aufbau)
  - Strategy (Sprachen, Versandkanäle, Freigaben je Prozessart)
  - Specification + Composite (Prüfregeln), Chain of Responsibility (automatische Übernahmen/Lookups)
  - Builder (XML, SQL), Repository, Value Objects, Fehlerklassen-Hierarchie
- SQL immer parametrisiert; dynamische Spaltennamen nur über geprüfte Bezeichner.

## 3. Fachliche Anforderungen (aus FileMaker abgeleitet)
- Alle fachlich relevanten Skripte als Anwendungsfälle/Endpunkte; Mapping FM-Skript → neu in docs/ANALYSE.md.
- Rollen aus den FM-Berechtigungssets ableiten. Rechte serverseitig erzwingen (nicht nur Buttons ausblenden).
  Objekt- und Mandantenfilter je Benutzer wie in FileMaker.
- Datensätze mit Optimistic Locking (Versionsnummer).
- Protokollierung:
  - Änderungshistorie je Datensatz.
  - Audit-Trail per DB-Trigger (Quelle manuell/Import/System).
  - Logbuch für Löschungen und Abgleiche.
- Belegnummern (falls vorhanden):
  - transaktionssicher vergeben, danach den Datensatz sperren (GoBD);
  - kein Löschen nummerierter Belege;
  - DSGVO-Löschung nach Aufbewahrungsfrist mit doppelter Bestätigung.
- PDF-Ausgaben nach den FM-Drucklayouts (Texte wörtlich, Sprachvarianten, Hausschrift eingebettet),
  Probeexemplar mit Wasserzeichen.
- Falls Rechnungen erzeugt werden: XRechnung 3.0 (UBL 2.1, EN 16931) mit Pflichtfeldprüfung, XML-Download,
  Versand per E-Mail/Peppol, Archivierung mit SHA-256; XML gegen das UBL-XSD prüfen.
- Datenübernahme-Skript aus FM-CSV-Exporten (IDs erhalten, Sequenzen nachziehen, --dry-run).

## 4. Fremdsysteme
- Für JEDES externe System ein Adapter mit Mock-Implementierung, umschaltbar über *_MODE in .env.
  Systeme: <LISTE, z. B. FileMaker Data API, SQL-Server-Views (technischer Leserbenutzer, TLS, ReadOnly),
  Anmeldung, SMTP (Mock schreibt .eml), HR-/SAP-Lieferung>.
- Die App muss mit Mocks sofort lokal lauffähig sein (Demo-Daten, Mock-Benutzer je Rolle, Passwort = Login).
- Fällt ein Fremdsystem beim Abgleich aus, laufen die übrigen weiter; Fehler im Ergebnis und Log melden.
- docs/SCHNITTSTELLEN.md: alle Felder je Fremdsystem mit Bedarf, bisherigem FM-Feldnamen und Verwendung;
  View-Spezifikationen mit Abnahmekriterien.
- Eingehende Lieferungen: nur echte Änderungen erkennen, daraus Vorschläge erzeugen. Jedes Ereignis bekommt
  einen Status mit Empfehlung, „Änderung ignorieren“ mit Begründung.
- Anmeldung über AD-Gruppen → Rollen. Bevorzugt Entra ID / OIDC; LDAP-Bind nur als Alternative. Vor der
  Umsetzung mit mir klären.

## 5. Stammdaten
- Stammdaten aus Fremdsystemen sind in der App nur lesbar; Anlegen nur bei rein lokalen Stammdaten.
- Felder, die die App zusätzlich pflegt, sind auch bei externen Datensätzen änderbar, als „lokal“
  gekennzeichnet und werden vom Abgleich nicht überschrieben.
- Im Backend erzwingen (403) und mit Tests absichern. Die Liste zeigt die Quelle je Datensatz.

## 6. Bedienung (UX)
- Entweder-oder-Felder nie gleichzeitig anzeigen: erst die Art wählen (Segment), dann nur das passende Feld;
  ein Wechsel leert die anderen Angaben.
- Pflichtfelder sichtbar kennzeichnen und nach Zweck unterscheiden, mit Legende.
- Live-Checkliste „Was fehlt noch?“ in der Seitenleiste je Workflow-Schritt.
- Editor-Muster: Tabs, Karten, Seitenleiste, Speichern/Verwerfen bei ungespeicherten Änderungen,
  Ablauf-Schritte, Aktionen nach Rechten.
- Barrierefreiheit: Labels, Tastaturbedienung (Enter auf Tabellenzeilen), Dialoge per Escape schließen.

## 7. Design
- Designsystem <NAME + LINK>: Farben, Schrift, Abstände und Radien als CSS-Variablen (Tokens); keine festen
  Hex-Werte oder px-Schriftgrößen in Komponenten.
  <Kernwerte: Primärfarbe, Grautöne, Feedbackfarben, Schrift, Radien, Abstände>
- Hausschrift <NAME> aus <PFAD> als WOFF im Frontend und TTF in PDFs. Lizenz beachten (Repository privat).
- Logo <NAME> in Kopfzeile und Login.

## 8. Code-Qualität
- ESLint mit gts (Google TypeScript Style inkl. Prettier) + eslint-plugin-sonarjs + angular-eslint (inkl.
  Template-Barrierefreiheit, OnPush, Signals). Ziel: 0 Fehler, 0 Warnungen; Ausnahmen nur begründet im Code.
- Unit-Tests für die Fachlogik, API-Tests gegen die Mocks (In-Memory-PGlite), Adapter-Tests mit simulierten
  Quellen. **100 % Testabdeckung als Schwelle** in Backend und Frontend.
- sonar-project.properties für SonarQube.
- Abhängigkeiten in exakten, nicht ganz frischen Versionen (mind. ca. 2 Wochen alt); npm audit ohne hohe Befunde.

## 9. Betrieb
- Updates ohne Datenverlust (Sicherung vor Migration, scripts/update.sh).
- CI/CD-Pipeline (<Azure DevOps | GitHub Actions>):
  - Lint, Tests mit Abdeckung, Builds, Migrationen gegen PostgreSQL, Docker-Images, npm audit;
  - optional SonarQube und Deploy.

## 10. Dokumentation
- README (Start mit Docker und lokal, Mock-Benutzer, Qualität)
- docs/ANALYSE.md (FM → neu, Entscheidungen, offene Punkte, Sicherheitsbefunde)
- docs/ARCHITEKTUR.md
- docs/BETRIEB.md (Integrationen umschalten, Datenübernahme, Produktions-Checkliste)
- docs/SCHNITTSTELLEN.md

## 11. Prüfung vor Abschluss
- Lint, Typecheck, Tests und Produktions-Build grün; `npm ci` unter Linux bzw. im Docker-Build geprüft.
- App im Browser wirklich durchklicken (Login je Rolle, Kernabläufe, Stammdaten, Rechteprüfung).
- Erzeugte PDFs visuell prüfen, XML gegen Schema validieren.
- Klar berichten, was nicht verifiziert werden konnte (z. B. echte Fremdsysteme, Docker).
