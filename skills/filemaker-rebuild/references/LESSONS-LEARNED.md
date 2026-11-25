# Lessons learned

Concrete pitfalls from real projects, each with its cause and the countermeasure.

## Analysis

- **The DDR is UTF-16**, so grep and most editors find nothing in it. Always convert it first or use
  `scripts/ddr_inventory.py`.
- **Credentials are stored as formulas** (`<Password><Calculation>…`) under ODBC sources and file references.
  Checking only the element text misses them.
- **Print texts live in layout text objects**, not in scripts. Reading layouts only for their structure leads
  to invented texts later.
- **FM checks that never fire** (e.g. a text pattern compared with a numeric ID): present them as a decision
  and take them over 1:1 by default, so behaviour does not change unnoticed.
- **Hard-coded user accounts** in scripts: do not take them over; ask.

## Business logic

- **Derived status without child records:** if "no items ⇒ done" holds but the status is only recalculated
  when an item changes, an empty order stays "new" forever, and the process waits forever. Evaluate the status
  right after creation.
- **"Inactive" is not "left the company":** employees on leave are often inactive in the old system but still
  belong to the workforce. Change rules must not filter them out.
- **Imports without proposals create endless work:** every event needs an automatic recommendation, or unclear
  entries pile up. There must be an "ignore" action, with a reason and a way to undo it.
- **Stable event keys** (e.g. `TYPE:personnel-number:effective-date`): they let the import recognise what has
  already been proposed, released or ignored, so nothing shows up twice.

## Data and privacy

- Keep real exports only in a git-ignored folder. Before every push, check the whole history:
  `git log --all --name-only | grep -iE "\.csv|\.xlsx|\.env|import-local"`.
- Pseudonymise test data: master data (org units, profiles) may be real, people may not.
- Never print names or values from real data in chat or logs, only counts.

## Local development

- **PGlite tolerates only one process per data directory.** Never start a second backend on the same
  `DATA_DIR`; it can corrupt the database. Use in-memory PGlite for tests.
- Mock password = login. Say so in the README so nobody has to guess.

## Design

- Enforce the corporate font in components: form controls do not inherit `font-family` on their own.
- Set `font-synthesis: none`, or the browser fakes bold or italic when a weight is missing.
- PDF libraries need TTF. Check the font's character set (e.g. `ş`, `Ł`, `µ`) and replace missing characters
  cleanly.
- Font licence: store fonts only in private repositories and note this in `docs/ARCHITECTURE.md`.

## Build and CI

- **`npm ci` fails on Linux although it works on macOS.** Cause: optional peer dependencies (e.g.
  `@emnapi/core` and `@emnapi/runtime` of `@napi-rs/wasm-runtime`) are missing from a lockfile generated on
  macOS. Re-resolving does not help. Fix: add the packages as devDependencies with exact versions. Test before
  pushing, in an empty folder:
  `cp package*.json $(mktemp -d) && cd $_ && npm ci --ignore-scripts`.
- Run `npm audit --omit=dev --audit-level=high` as a separate pipeline job: vulnerabilities in runtime
  dependencies block the run, those in dev tools do not.
- Run migrations twice in the pipeline. The second run must report "nothing to do"; otherwise checksums or
  idempotency are off.
- After merging parallel work (branches, sessions), run the tests again on the combined state before pushing.

## Working with Claude Code

- Have large, independent extensions (e.g. notifications) built in separate sessions, then test on the
  combined state.
- Never paste credentials (tokens, passkeys) into the chat. Run the first push yourself in the terminal; after
  that, the token sits in the keychain.
- Record decisions in `docs/ANALYSIS.md` immediately. It is the project's memory across sessions.
