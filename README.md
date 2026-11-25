# FileMaker Rebuild Playbook

A reusable approach for redeveloping FileMaker applications as modern web apps with Claude Code. It grew out of
several real redevelopments and is deliberately generic: no company data, no credentials, no real data.

**The goal of every redevelopment:**
- business behaviour 1:1 as in FileMaker;
- Node.js/TypeScript, Angular and PostgreSQL;
- runs locally with mocks right away;
- 100 % test coverage, Docker and CI/CD.

## Contents

| Path | Purpose |
|---|---|
| [`skills/filemaker-rebuild/SKILL.md`](skills/filemaker-rebuild/SKILL.md) | Claude Code skill: hard rules, workflow, pitfalls |
| [`…/references/PLAYBOOK.md`](skills/filemaker-rebuild/references/PLAYBOOK.md) | The playbook: principles and phases 0–9 |
| [`…/references/START-PROMPT.md`](skills/filemaker-rebuild/references/START-PROMPT.md) | Fill-in start prompt for a new project |
| [`…/references/LESSONS-LEARNED.md`](skills/filemaker-rebuild/references/LESSONS-LEARNED.md) | Pitfalls with cause and fix |
| [`…/references/templates/`](skills/filemaker-rebuild/references/templates) | Templates for ANALYSIS, ARCHITECTURE, OPERATIONS, INTERFACES |
| [`…/references/checklists/BEFORE-DONE.md`](skills/filemaker-rebuild/references/checklists/BEFORE-DONE.md) | Checklist before completion and push |
| [`…/scripts/ddr_inventory.py`](skills/filemaker-rebuild/scripts/ddr_inventory.py) | DDR inventory as Markdown, layout texts, security findings (without values) |

## Install the skill

For all your projects (personal):

```bash
./install.sh
```

This links `skills/filemaker-rebuild` to `~/.claude/skills/filemaker-rebuild`, so a `git pull` keeps the
skill up to date. For a single project only: copy the folder to `<project>/.claude/skills/`.

## Start a new project

1. Export the DDR and the database report from FileMaker (Tools → Database Design Report, format XML).
2. Create the inventory:
   ```bash
   python3 -I skills/filemaker-rebuild/scripts/ddr_inventory.py MyApp_fmp12.xml --texts layout-texts.md > inventory.md
   ```
3. Fill in [`START-PROMPT.md`](skills/filemaker-rebuild/references/START-PROMPT.md) and give it to Claude Code
   together with the extracts. The skill kicks in automatically as soon as FileMaker or a DDR comes up.
4. Confirm the decisions in `docs/ANALYSIS.md`, then have it implemented phase by phase.

## Requirements

- Python 3.9+ (standard library only) for the script.
- Node.js 22 for the generated projects.
- Claude Code.

## Licence

MIT, see [LICENSE](LICENSE).
