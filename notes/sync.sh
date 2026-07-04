#!/usr/bin/env bash
# Sync skills from this directory (the source of truth) to Claude Code and
# Tabnine skill locations, and the notes tooling to the notes root.
#
# Usage:
#   ./sync.sh          # copy (default)
#   ./sync.sh link     # symlink skill dirs instead — edits here apply live
#
# Overridable via env: CLAUDE_SKILLS_DIR, TABNINE_SKILLS_DIR, NOTES_ROOT
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS=(session-wrap notes-lint ingest)

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
TABNINE_SKILLS_DIR="${TABNINE_SKILLS_DIR:-$HOME/.tabnine/agent/skills}"
NOTES_ROOT="${NOTES_ROOT:-$HOME/notes}"
MODE="${1:-copy}"

case "$MODE" in copy|link) ;; *) echo "usage: $0 [copy|link]" >&2; exit 2 ;; esac

# references/writing-style.md is canonical; copy it into each skill dir so the
# skill has it alongside SKILL.md (skills only see their own directory)
for skill in "${SKILLS[@]}"; do
  cp -f "$SRC/references/writing-style.md" "$SRC/$skill/writing-style.md"
done

for target in "$CLAUDE_SKILLS_DIR" "$TABNINE_SKILLS_DIR"; do
  mkdir -p "$target"
  for skill in "${SKILLS[@]}"; do
    if [ "$MODE" = "link" ]; then
      # replace any previous copy or stale link with a symlink to the source
      rm -rf "${target:?}/${skill}"
      ln -sfn "$SRC/$skill" "$target/$skill"
    else
      mkdir -p "$target/$skill"
      cp -f "$SRC/$skill/"*.md "$target/$skill/"
    fi
    echo "  $MODE  $skill -> $target/$skill"
  done
done

mkdir -p "$NOTES_ROOT/tools" "$NOTES_ROOT/raw"
cp -f "$SRC/tools/notes_tools.py" "$NOTES_ROOT/tools/"
echo "  copy  tools/notes_tools.py -> $NOTES_ROOT/tools/"

echo
echo "Done. Reload to pick up changes:"
echo "  Claude Code: restart session (or /skills if available)"
echo "  Tabnine CLI: /skills reload"
