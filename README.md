# FileMaker-Rebuild-Playbook

Wiederverwendbares Vorgehen, um FileMaker-Anwendungen als moderne Web-Apps neu zu entwickeln, mit Claude Code.
Es entstand aus mehreren realen Neuentwicklungen und ist bewusst allgemein gehalten: keine Firmendaten,
keine Zugangsdaten, keine Echtdaten.

**Ziel jeder Neuentwicklung:** fachliches Verhalten 1:1 wie in FileMaker, Node.js/TypeScript + Angular +
PostgreSQL, sofort lokal lauffähig mit Mocks, 100 % Testabdeckung, Docker und CI/CD.

## Inhalt

| Pfad | Zweck |
|---|---|
| [`skills/filemaker-rebuild/SKILL.md`](skills/filemaker-rebuild/SKILL.md) | Claude-Code-Skill: harte Regeln, Ablauf, Fallen |
| [`…/references/PLAYBOOK.md`](skills/filemaker-rebuild/references/PLAYBOOK.md) | Das Playbook: Grundsätze und Phasen 0–9 |
| [`…/references/START-PROMPT.md`](skills/filemaker-rebuild/references/START-PROMPT.md) | Ausfüllbarer Start-Prompt für ein neues Projekt |
| [`…/references/LESSONS-LEARNED.md`](skills/filemaker-rebuild/references/LESSONS-LEARNED.md) | Stolpersteine mit Ursache und Lösung |
| [`…/references/vorlagen/`](skills/filemaker-rebuild/references/vorlagen) | Vorlagen für ANALYSE, ARCHITEKTUR, BETRIEB, SCHNITTSTELLEN |
| [`…/references/checklisten/ABSCHLUSS.md`](skills/filemaker-rebuild/references/checklisten/ABSCHLUSS.md) | Checkliste vor Abschluss und Push |
| [`…/scripts/ddr_inventar.py`](skills/filemaker-rebuild/scripts/ddr_inventar.py) | DDR-Inventar als Markdown, Layout-Texte, Sicherheitsbefunde (ohne Werte) |

## Skill installieren

Für alle Projekte (persönlich):

```bash
./install.sh
```

Das verlinkt `skills/filemaker-rebuild` nach `~/.claude/skills/filemaker-rebuild`. Nach einem `git pull`
ist der Skill automatisch aktuell. Nur für ein Projekt: den Ordner nach `<projekt>/.claude/skills/` kopieren.

## So startest du ein neues Projekt

1. DDR und Datenbankbericht aus FileMaker exportieren (Werkzeuge → Datenbankentwurfsbericht, Format XML).
2. Inventar erzeugen:
   ```bash
   python3 -I skills/filemaker-rebuild/scripts/ddr_inventar.py MeineApp_fmp12.xml --texte layout-texte.md > inventar.md
   ```
3. [`START-PROMPT.md`](skills/filemaker-rebuild/references/START-PROMPT.md) ausfüllen und mit den Extrakten
   in Claude Code geben. Der Skill greift automatisch, sobald es um FileMaker/DDR geht.
4. Entscheidungen aus `docs/ANALYSE.md` bestätigen, dann Phase für Phase umsetzen lassen.

## Voraussetzungen

Python 3.9+ (nur Standardbibliothek) für das Skript, Node.js 22 für die erzeugten Projekte und Claude Code.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
