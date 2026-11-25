#!/usr/bin/env bash
# Verlinkt den Skill nach ~/.claude/skills (persönlich, für alle Projekte)
set -euo pipefail
quelle="$(cd "$(dirname "$0")" && pwd)/skills/filemaker-rebuild"
ziel="${HOME}/.claude/skills/filemaker-rebuild"
mkdir -p "$(dirname "$ziel")"
if [ -e "$ziel" ] && [ ! -L "$ziel" ]; then
  echo "$ziel existiert bereits und ist kein Link – bitte prüfen." >&2
  exit 1
fi
ln -sfn "$quelle" "$ziel"
echo "Skill installiert: $ziel -> $quelle"
