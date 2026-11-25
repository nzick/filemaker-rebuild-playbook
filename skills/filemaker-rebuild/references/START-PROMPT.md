# Start prompt (template)

Replace the placeholders in `<…>`, delete sections that do not apply and attach the extracts.

---

I want to redevelop the FileMaker application "<APP_NAME>". Attached are the FileMaker extracts
(DDR "<APP_NAME>_fmp12.xml" and database report "<APP_NAME>-report.xml") and our logo.
Work in the project folder <TARGET_FOLDER>. Answer in <LANGUAGE>.

Reference: the application "<REFERENCE_PROJECT>" in <REFERENCE_PATH> is built on exactly this scheme.
Take over its architecture, base classes (core/, db/, auth/, shared/), design (frontend/src/styles.scss,
logo, component patterns), lint/Sonar configuration and documentation structure.
(No reference project: delete this paragraph; the scaffold is built according to section 2.)

## 1. Analyse the FileMaker extracts
- The DDR is UTF-16: convert it to UTF-8 before the analysis (e.g. with `scripts/ddr_inventory.py`).
- Evaluate everything:
  - base tables, table occurrences, relationships;
  - fields, including calculated and global fields;
  - scripts, layouts, value lists;
  - accounts/privilege sets;
  - external data sources (file references, ODBC).
- Do NOT read layouts for their structure only: text objects (<Data>) in print layouts contain letter, payment
  and dunning texts. Take all texts, formulas and rules over 1:1 from FileMaker and never write your own.
  If there are several variants (commented out / active), the active formula applies.
- Principle: behave like FileMaker. Deviations (improvements included) only after my explicit confirmation.
  Record every decision in docs/ANALYSIS.md (D-1, D-2, …).
- Name unused objects and legacy, but do not rebuild them.
- Never take over or repeat credentials from the DDR (passwords, ODBC logins); report them only as a security
  finding (recommend rotation).
- List fields that are missing from the DDR or come from other files as open points, and request the DDRs of
  the referenced files.
- Real data exports are in <REAL_DATA_FOLDER> (git-ignored): never commit them, never print names or values in
  the chat.

## 2. Target architecture
- Backend:
  - Node.js 22, TypeScript (strict), Express 5, Zod, PostgreSQL 16.
  - Locally without installation through embedded PGlite (same database abstraction).
  - SQL migrations as files with a checksum.
- Frontend: Angular (current version), standalone components, signals, zoneless, OnPush everywhere, typed
  models (no `any`), strictTemplates.
- Web server: nginx (SPA + reverse proxy /api, security headers, CSP without inline scripts; Angular build
  therefore with inlineCritical=false). Operation via Docker Compose (db, backend, web).
- Strictly object-oriented:
  - layers controllers → services → repositories → db;
  - business logic in domain/ as classes without database access;
  - a composition root (Application class) with constructor injection, no global singletons;
  - configuration as an immutable AppConfig.fromEnv().
- Use design patterns deliberately and document each with its location in docs/ARCHITECTURE.md:
  - Abstract Factory (integrations), Factory Method, Adapter;
  - Template Method (controller base class, PDF layout);
  - Strategy (languages, delivery channels, release per process type);
  - Specification + Composite (validation rules), Chain of Responsibility (automatic defaults/lookups);
  - Builder (XML, SQL), Repository, Value Objects, error class hierarchy.
- SQL always parameterised; dynamic column names only through checked identifiers.

## 3. Business requirements (derived from FileMaker)
- Every business-relevant script becomes a use case/endpoint; mapping FM script → new in docs/ANALYSIS.md.
- Derive roles from the FM privilege sets. Enforce permissions on the server (not just by hiding buttons).
  Object and tenant filters per user as in FileMaker.
- Records with optimistic locking (version number).
- Logging:
  - change history per record;
  - an audit trail through DB triggers (source manual/import/system);
  - a log book for deletions and syncs.
- Document numbers (if any):
  - assign them inside a transaction and lock the record afterwards (GoBD);
  - never delete numbered documents;
  - GDPR deletion after the retention period, with double confirmation.
- PDF output following the FM print layouts (texts verbatim, language variants, corporate font embedded), a
  draft copy with a watermark.
- If invoices are produced: XRechnung 3.0 (UBL 2.1, EN 16931) with required-field checks, XML download,
  delivery by email/Peppol, archiving with SHA-256; validate the XML against the UBL XSD.
- Data migration script from FM CSV exports (keep IDs, advance sequences, --dry-run).

## 4. External systems
- For EVERY external system an adapter with a mock implementation, switched by *_MODE in .env.
  Systems: <LIST, e.g. FileMaker Data API, SQL Server views (technical read-only user, TLS), sign-in,
  SMTP (mock writes .eml), HR/ERP delivery>.
- The app must run locally with mocks right away (demo data, one mock user per role, password = login).
- If an external system fails during a sync, the others keep running; report the error in the result and the
  log.
- docs/INTERFACES.md: every field per external system with its need, the former FM field name and its use;
  view specifications with acceptance criteria.
- Incoming deliveries: detect real changes only and turn them into proposals. Every event gets a status with a
  recommendation, plus "ignore change" with a reason.
- Sign-in through AD groups → roles. Preferably Entra ID / OIDC; LDAP bind only as an alternative. Agree on
  this with me before implementing.

## 5. Master data
- Master data from external systems is read-only in the app; creating records only for purely local master
  data.
- Fields the app maintains in addition can be edited on external records too, are marked "local" and are never
  overwritten by the sync.
- Enforce this in the backend (403) and cover it with tests. The list shows the source of each record.

## 6. Usability (UX)
- Never show either-or fields at the same time: first choose the kind (segment control), then only the
  matching field; switching clears the other values.
- Mark required fields visibly and by purpose, with a legend.
- A live checklist "What is still missing?" in the sidebar for each workflow step.
- Editor pattern: tabs, cards, sidebar, save/discard for unsaved changes, workflow steps, actions by
  permission.
- Accessibility: labels, keyboard use (Enter on table rows), close dialogs with Escape.

## 7. Design
- Design system <NAME + LINK>: colours, font, spacings and radii as CSS variables (tokens); no fixed hex values
  or px font sizes in components.
  <Core values: primary colour, greys, feedback colours, font, radii, spacings>
- Corporate font <NAME> from <PATH>: WOFF in the frontend and TTF in PDFs. Mind the licence (private
  repository).
- Logo <NAME> in the header and on the login page.

## 8. Code quality
- ESLint with gts (Google TypeScript Style incl. Prettier) + eslint-plugin-sonarjs + angular-eslint (incl.
  template accessibility, OnPush, signals). Target: 0 errors, 0 warnings; exceptions only with a justification
  in the code.
- Unit tests for the business logic, API tests against the mocks (in-memory PGlite), adapter tests with
  simulated sources. **100 % test coverage as a threshold** in backend and frontend.
- sonar-project.properties for SonarQube.
- Dependencies at exact, not brand-new versions (at least about 2 weeks old); npm audit without high findings.

## 9. Operations
- Updates without data loss (backup before migration, scripts/update.sh).
- CI/CD pipeline (<Azure DevOps | GitHub Actions>):
  - lint, tests with coverage, builds, migrations against PostgreSQL, Docker images, npm audit;
  - optional SonarQube and deployment.

## 10. Documentation
- README (start with Docker and locally, mock users, quality)
- docs/ANALYSIS.md (FM → new, decisions, open points, security findings)
- docs/ARCHITECTURE.md
- docs/OPERATIONS.md (switching integrations, data migration, production checklist)
- docs/INTERFACES.md

## 11. Checks before completion
- Lint, type check, tests and production build green; `npm ci` verified on Linux or in the Docker build.
- Actually click through the app in the browser (login per role, core flows, master data, permission checks).
- Look at the generated PDFs, validate XML against its schema.
- Report clearly what could not be verified (e.g. real external systems, Docker).
