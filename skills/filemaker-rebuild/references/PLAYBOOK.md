# Playbook: Rebuild a FileMaker application as a web app

Proven on several redevelopments, including one application with more than 100 tables, 300 scripts and
270 layouts. The goal: **the same business behaviour as in FileMaker** on a modern architecture. The app runs
locally right away, is 100 % tested and is ready for operation with Docker and CI/CD.

Each phase builds on the one before. Every phase ends with a commit and a short report to the client: what is
done, what is open, what could not be verified.

---

## Principles (apply in every phase)

1. **Behave like FileMaker.** Take texts, formulas and rules over verbatim and never write texts of your own.
   Deviations, improvements included, only with explicit confirmation. Every decision gets a number (D-1,
   D-2, …) in `docs/ANALYSIS.md`, with its date and origin ("your decision of …").
2. **Surface FileMaker bugs instead of silently fixing them.** Checks that have no effect, unreachable branches
   and hard-coded accounts are presented as decisions: keep 1:1, correct or drop.
3. **Never take over credentials.** Passwords and ODBC logins from the DDR must not appear in code, docs or
   chat. Report them only as a security finding with a recommendation to rotate.
4. **Real data stays local.** Exports containing personal data live in a git-ignored folder (e.g.
   `import-local/`) and are never committed. Chats and logs never show names or values. Test and demo data
   are pseudonymised.
5. **Runs with mocks right away.** Every external system gets an adapter with a mock, switched by `*_MODE`.
   There is one mock user per role; the password equals the login.
6. **Permissions are enforced on the server.** Hiding buttons is not enough. Every action checks its permission
   in the backend, and tests cover 403/422.
7. **Quality is mandatory, not a target.** Lint 0/0 and 100 % test coverage, enforced by thresholds, and a green
   production build. Exceptions only with a justification in the code.
8. **Report honestly.** Whatever was not verified (real external systems, Docker, mail delivery) goes into the
   report. "Done" means verified.

---

## Phase 0 – Preparation

- Collect the extracts:
  - DDR (`<file>_fmp12.xml`) and database report for each FileMaker file, including files reached through
    file references;
  - CSV/Excel data exports;
  - logo and design-system guidelines.
- Choose a reference project: a project already built on this scheme supplies the base classes (`core/`,
  `db/`, `auth/`, `shared/`), the design, the lint/Sonar configuration and the documentation structure. From
  the second project on, this saves the most time.
- Create the project folder and Git repository. Right away, add the real-data folder, `.env`, data directories
  and backups to `.gitignore`.
- Fill in the start prompt from `START-PROMPT.md`.

## Phase 1 – Analyse the FileMaker extracts

- The DDR is UTF-16. `scripts/ddr_inventory.py` converts it itself and produces the inventory: base tables,
  table occurrences, relationships, scripts, layouts, value lists, privilege sets, accounts, custom functions,
  external data sources and security findings.
- `--texts` extracts every text object from the layouts. Print layouts contain letter, payment, dunning and
  checklist texts, and those are taken over verbatim.
- Read the scripts for their business meaning: which are use cases, which drive the UI, which are legacy? The
  mapping from FM script to new function goes into `docs/ANALYSIS.md`, section "Scripts → functions".
- If a formula has several variants (commented out / active), the active one applies.
- Fields that come from other files are listed in the docs as open points, with a request for the missing DDR.
- Name unused objects, but do not rebuild them.
- **Result:** `docs/ANALYSIS.md` with scope, business flow, data model, script mapping, roles, legacy objects,
  decisions, security finding and open points. Have these decisions confirmed before implementation starts.

## Phase 2 – Scaffold and architecture

- **Backend:** Node.js 22 LTS, strict TypeScript, Express 5, Zod, PostgreSQL 16. Locally, the embedded PGlite
  runs behind the same database abstraction, with nothing to install. Migrations are SQL files with a checksum.
- **Frontend:** Angular (current version), standalone, signals, zoneless, OnPush, strictTemplates, no `any`.
- **Web server:** nginx (SPA + reverse proxy `/api`, security headers, CSP without inline scripts, Angular with
  `inlineCritical=false`). Docker Compose with `db`, `backend` and `web`.
- **Layers:** controllers → services → repositories → db. Business logic lives in `domain/` as classes without
  database access. The composition root (`Application`) uses constructor injection and no singletons; the
  configuration is an immutable `AppConfig.fromEnv()`.
- **Patterns:** use them deliberately and document each one with its location in `docs/ARCHITECTURE.md`:
  Abstract Factory (integrations), Adapter, Template Method (controllers, PDF), Strategy (release per process
  type, delivery), Specification + Composite (validation rules), Chain of Responsibility (defaults/lookups),
  Builder (SQL, XML), Repository, Value Objects, error class hierarchy.
- SQL is always parameterised; dynamic column names only through checked identifiers.

## Phase 3 – Implement the business logic

- Every business-relevant script becomes a use case or endpoint, with its message texts verbatim.
- Derive roles from the privilege sets, and implement object or tenant filters per user.
- Optimistic locking (version number), change history per record, log book for deletions and syncs.
- **Audit trail through DB triggers:** it attaches automatically to every new business table, records the
  source (manual, import, system) and an operation ID, and can be exported as CSV.
- Assign document numbers inside a transaction and lock the record afterwards (GoBD). GDPR deletion or
  anonymisation needs a double confirmation.
- PDFs follow the FM print layouts, with texts verbatim, the corporate font embedded and a draft copy
  watermarked.
- Invoices, if any: XRechnung 3.0 (UBL 2.1, EN 16931), XSD validation, archive with SHA-256.
- **Statuses derived from child records** (e.g. "order done when all items are done") must also be evaluated
  right after creation. Otherwise a record without child records stays open forever.

## Phase 4 – External systems and imports

- Every system gets an adapter with a mock. If one system fails, the others keep running; the error appears in
  the result and in the log.
- `docs/INTERFACES.md`: every field per system with its need (required / print / optional), the former FM field
  name and the view specification (schema, columns, types, keys, NULL rules, acceptance criteria).
- Sign-in through AD groups → roles, preferably OIDC/Entra ID, LDAP only as an alternative. Agree on this
  before implementing.
- Master data from external systems is read-only (403 in the backend). Extra fields maintained locally are
  marked "local", and the sync never overwrites them.
- **Incoming deliveries** (e.g. a full HR/ERP extract as CSV):
  - Detect real changes only, by comparing with the previous delivery and the current data.
  - Turn them into *proposals* (drafts), not direct changes.
  - Every event gets a status with a recommendation (open, "ignore recommended", already recorded, released,
    ignored). No event is left "without a proposal".
  - Offer "ignore change" with a reason and "resume", both written to the log book.
  - Use a stable key per event so nothing shows up twice.
  - Lock fields in the form that come from the delivery.
- Data migration script from FM exports: keep IDs, advance sequences, `--dry-run`.

## Phase 5 – Usability and design

- Never show either-or fields at the same time: first choose the kind (segment control), then show only the
  matching field. Switching clears the others.
- Mark required fields by purpose (always / for release / only in certain cases), with a legend.
- A live checklist "What is still missing?" for each workflow step.
- Editor pattern: tabs, cards, sidebar, protection against losing unsaved changes, actions by permission.
- **Make the process lifecycle visible:** in capture → in progress → completed, with filters, overdue markers
  and "waiting for n days".
- Accessibility: labels, Enter on table rows, Escape closes dialogs.
- **Complete design system:**
  - All colours, spacings, radii and font sizes as CSS variables (tokens), no hex values or px font sizes in
    components.
  - Load the corporate font via `@font-face` (WOFF), with `font-synthesis: none` and
    `button, input, select, textarea { font-family: inherit }`.
  - Embed the corporate font in PDFs too (TTF). Reduce characters the font lacks to their base character.
  - Check the licence: keep font files in private repositories only.

## Phase 6 – Extensions on demand

Typical requests once the 1:1 rebuild stands. Every extension gets a D number:

- Input validation (email, phone, IBAN, check digits), in the backend too.
- Integration of further FM files that used to run separately.
- **Email notifications:**
  - event catalogue, personal subscriptions (immediate or digest) and recipient rules in the admin area;
  - reminders before the deadline and multi-level escalation when overdue;
  - delivery log with deduplication, deep link for editing;
  - a scheduled job does the sending.
- Overview/dashboard with a highlighted "to do" tile.

## Phase 7 – Quality

- ESLint with gts (Google TypeScript Style + Prettier), eslint-plugin-sonarjs and angular-eslint (template
  accessibility, OnPush, signals). Target: 0 errors, 0 warnings.
- Tests:
  - unit tests for the business logic;
  - API tests against the mocks with in-memory PGlite;
  - adapter tests with simulated sources;
  - frontend tests with vitest.
- **100 % coverage as a threshold** in backend and frontend (statements, branches, functions, lines).
- `sonar-project.properties` for SonarQube (ESLint, lcov and JUnit reports).
- Dependencies at exact versions that are at least about two weeks old. `npm audit --omit=dev
  --audit-level=high` must be clean.

## Phase 8 – Operations and CI/CD

- **Updates without data loss:**
  - migrations with a checksum; an already applied migration that has changed aborts the run;
  - an automatic backup before every migration;
  - `scripts/update.sh`: backup → new images → restart → wait for the health check.
- `docs/OPERATIONS.md`: switching integrations, data migration, production checklist, Docker, import schedule,
  audit, notifications.
- **Pipeline** (Azure DevOps or GitHub Actions):
  - Checks: backend (lint, type check, tests with coverage, build), frontend (lint, tests, production build),
    migrations against real PostgreSQL (run twice), Docker images and `npm audit`.
  - Optional SonarQube.
  - Optional deployment via SSH, from `main` only and with an approval through an environment.
- **Test `npm ci` on Linux before the first pipeline run**; see `LESSONS-LEARNED.md` (lockfile from macOS).

## Phase 9 – Acceptance

Work through `checklists/BEFORE-DONE.md`, click through the app in the browser for every role, look at the PDFs,
and report open points and anything unverified clearly.

---

## Documentation (keep it current)

| File | Content |
|---|---|
| `README.md` | Quick start (Docker / local), mock users, step-by-step installation, tests, CI/CD |
| `docs/ANALYSIS.md` | FM → new, script mapping, roles, legacy objects, **decisions D-n**, security finding, open points |
| `docs/ARCHITECTURE.md` | Layers, patterns with location, cross-cutting rules, swapping external systems |
| `docs/OPERATIONS.md` | Integrations, data migration, production, updates, imports, audit, CI/CD |
| `docs/INTERFACES.md` | Fields per external system, view specifications, minimal set for production |

Templates are in `templates/`.
