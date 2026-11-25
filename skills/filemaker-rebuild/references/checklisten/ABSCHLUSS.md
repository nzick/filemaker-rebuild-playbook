# Checkliste vor Abschluss / Push

## Code
- [ ] Lint Backend und Frontend: 0 Fehler, 0 Warnungen
- [ ] Typecheck inkl. Tests und Skripte
- [ ] Tests grün, Abdeckung 100 % (Schwellen nicht gesenkt)
- [ ] Produktions-Build Frontend, Build Backend
- [ ] `npm ci` in leerem Verzeichnis (Lockfile vollständig, auch für Linux)
- [ ] `npm audit --omit=dev --audit-level=high` sauber
- [ ] Migrationen auf leerer DB und ein zweites Mal („nichts zu tun“)

## Fachlich
- [ ] Login je Mock-Rolle, Kernabläufe durchgeklickt
- [ ] Rechte: verbotene Aktionen liefern 403 (nicht nur ausgeblendet)
- [ ] PDFs angesehen (Texte wörtlich, Schrift, Umlaute)
- [ ] Neue Entscheidungen als E-n in docs/ANALYSE.md

## Daten und Sicherheit
- [ ] Keine Echtdaten, `.env`, Schlüssel im Git-Verlauf
- [ ] Keine Zugangsdaten aus dem DDR in Code/Doku
- [ ] Schriftdateien nur in privatem Repository

## Bericht
- [ ] Was erledigt ist, was offen ist, was nicht verifiziert werden konnte
