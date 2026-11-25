# Architecture of <APP_NAME>

## Overall system
Browser → nginx (SPA, /api proxy, CSP) → backend (Express) → PostgreSQL / PGlite; external systems through adapters.

## Backend layers
controllers → services → repositories → db; business logic in `domain/` without database access; composition root `Application`.

## Design patterns used
| Pattern | Location | Purpose |
|---|---|---|

## Cross-cutting rules
Optimistic locking, audit trail (triggers), log book, error classes → HTTP status, parameterised SQL.

## Swapping external systems
`*_MODE` per system (mock | real), Abstract Factory `Integrations`.

## Frontend
Standalone, signals, zoneless, OnPush; design tokens in `styles.scss`; corporate font (licence: private repository).
