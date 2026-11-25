# Checklist before completion / push

## Code
- [ ] Lint backend and frontend: 0 errors, 0 warnings
- [ ] Type check including tests and scripts
- [ ] Tests green, coverage 100 % (thresholds not lowered)
- [ ] Frontend production build, backend build
- [ ] `npm ci` in an empty folder (lockfile complete, also for Linux)
- [ ] `npm audit --omit=dev --audit-level=high` clean
- [ ] Migrations on an empty DB, then a second time ("nothing to do")

## Business
- [ ] Logged in with every mock role, core flows clicked through
- [ ] Permissions: forbidden actions return 403 (not just hidden)
- [ ] PDFs reviewed (texts verbatim, font, special characters)
- [ ] New decisions recorded as D-n in docs/ANALYSIS.md

## Data and security
- [ ] No real data, `.env` or keys in the Git history
- [ ] No credentials from the DDR in code or docs
- [ ] Font files only in a private repository

## Report
- [ ] What is done, what is open, what could not be verified
