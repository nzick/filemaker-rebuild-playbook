# Architektur <APP_NAME>

## Gesamtsystem
Browser → nginx (SPA, /api-Proxy, CSP) → Backend (Express) → PostgreSQL / PGlite; Fremdsysteme über Adapter.

## Backend – Schichten
controllers → services → repositories → db; Fachlogik in `domain/` ohne DB-Zugriff; Composition Root `Application`.

## Eingesetzte Design Patterns
| Pattern | Fundstelle | Zweck |
|---|---|---|

## Querschnittsregeln
Optimistic Locking, Audit-Trail (Trigger), Logbuch, Fehlerklassen → HTTP-Status, parametrisiertes SQL.

## Fremdsysteme austauschen
`*_MODE` je System (mock | echt), Abstract Factory `Integrationen`.

## Frontend
Standalone, Signals, zoneless, OnPush; Design-Tokens in `styles.scss`; Hausschrift (Lizenz: Repository privat).
