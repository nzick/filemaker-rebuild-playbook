# Operating <APP_NAME>

## 1. Switching integrations (mock → real)
| Variable | Values | Meaning |
|---|---|---|

## 2. Data migration from FileMaker
`npm run import -- --dry-run <folder>` → review → run without `--dry-run`.

## 3. Production checklist
- [ ] Secrets (JWT, DB, keys) set, not in the repository
- [ ] All `*_MODE` set to real, `AUTH_MODE` not mock
- [ ] Backup and restore tested
- [ ] TLS, security headers, CSP active
- [ ] Credentials found in the DDR rotated

## 4. Applying an update without data loss
`scripts/update.sh`: backup → new images → restart → health check.

## 5. Running with Docker

## 6. Imports and schedules

## 7. Audit trail

## 8. CI/CD
