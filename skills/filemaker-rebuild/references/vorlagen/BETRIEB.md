# Betrieb <APP_NAME>

## 1. Integrationen umschalten (Mock → echt)
| Variable | Werte | Bedeutung |
|---|---|---|

## 2. Datenübernahme aus FileMaker
`npm run import -- --dry-run <ordner>` → prüfen → ohne `--dry-run` ausführen.

## 3. Produktion – Checkliste
- [ ] Geheimnisse (JWT, DB, Schlüssel) gesetzt, nicht im Repository
- [ ] alle `*_MODE` auf echt, `AUTH_MODE` nicht mock
- [ ] Sicherung und Wiederherstellung getestet
- [ ] TLS, Security-Header, CSP aktiv
- [ ] im DDR gefundene Zugangsdaten rotiert

## 4. Update einspielen ohne Datenverlust
`scripts/update.sh`: Sicherung → neue Images → Neustart → Health-Check.

## 5. Betrieb mit Docker

## 6. Importe und Zeitpläne

## 7. Audit-Trail

## 8. CI/CD
