#!/usr/bin/env bash
# Links the skill into ~/.claude/skills (personal, for all projects)
set -euo pipefail
source_dir="$(cd "$(dirname "$0")" && pwd)/skills/filemaker-rebuild"
target="${HOME}/.claude/skills/filemaker-rebuild"
mkdir -p "$(dirname "$target")"
if [ -e "$target" ] && [ ! -L "$target" ]; then
  echo "$target already exists and is not a link - please check." >&2
  exit 1
fi
ln -sfn "$source_dir" "$target"
echo "Skill installed: $target -> $source_dir"
