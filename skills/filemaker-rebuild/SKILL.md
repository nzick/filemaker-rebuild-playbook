---
name: filemaker-rebuild
description: Rebuild a FileMaker application as a modern web app (Node/TypeScript/Express/PostgreSQL + Angular) with FileMaker behaviour taken over 1:1. Use when the user wants to analyse a FileMaker DDR (Database Design Report, *_fmp12.xml) or database report, migrate or redevelop a FileMaker solution, or continue such a project (ANALYSIS.md with decisions D-n, mocks per external system, 100 % coverage, Docker/CI). Also use to extract layout texts or security findings from a DDR.
---

# Rebuild a FileMaker app as a web app

This skill guides a FileMaker redevelopment along a proven scheme. The full guide is
`references/PLAYBOOK.md`. Read all of it at the start of a new project; for follow-up tasks, read the section
that applies.

## Hard rules (never break)

1. **Behave like FileMaker.** Take texts, formulas and rules over verbatim. Any deviation, including an
   improvement, needs the user's confirmation and is recorded as `D-n` in `docs/ANALYSIS.md`, with its date.
2. **Credentials in the DDR** (passwords, ODBC logins): never take over, print or repeat them. Report only the
   location as a security finding and recommend rotation.
3. **Real data** (CSV/Excel exports containing people) stays in a git-ignored folder. Never commit it. In chat,
   give counts only, never names or values.
4. **Enforce permissions on the server**, give every external system a mock (`*_MODE`), and make the app run
   with mocks right away.
5. **Done means verified:** lint 0/0, tests with 100 % coverage, builds green, clicked through in the browser.
   Name explicitly whatever could not be verified.

## Workflow

1. **New project:** if details from `references/START-PROMPT.md` are missing (app name, target folder,
   reference project, design system, external systems, folder for real data), ask for them. If the prompt is
   filled in, follow it.
2. **Analysis:** create the inventory with the script, which reads UTF-16 itself:
   ```bash
   python3 -I <skill-dir>/scripts/ddr_inventory.py <DDR.xml> --texts docs/fm-layout-texts.md > docs/fm-inventory.md
   ```
   - The layout texts are the source for all print and message texts.
   - The script's security findings contain no values; keep it that way.
   - Build `docs/ANALYSIS.md` from `references/templates/ANALYSIS.md`.
   - Present the decisions to the user **before** implementing.
3. **Implementation:** phases 2–8 of the playbook. For every business rule, cite its FileMaker source (script,
   line, field formula) in a code comment or in ANALYSIS.md.
4. **Before every commit or push:** work through `references/checklists/BEFORE-DONE.md`. In particular, test
   `npm ci` in an empty folder, because a lockfile created on macOS can fail on Linux.
5. **Keep the docs current:** README, `docs/ANALYSIS.md`, `ARCHITECTURE.md`, `OPERATIONS.md`, `INTERFACES.md`.
   Templates are in `references/templates/`.

## Known pitfalls

Read `references/LESSONS-LEARNED.md` before you touch imports, derived statuses, design/fonts or the CI
pipeline. In short:

- **Derived status:** evaluate it right after creation too, or an order without items is never "done".
- **Imports:** every event needs an automatic recommendation, an "ignore" action with a reason, and a stable
  event key.
- **PGlite:** never run two processes on the same data directory.
- **Licences:** corporate fonts and logos belong only in private repositories.
