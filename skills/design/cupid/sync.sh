#!/usr/bin/env bash
# Sync CUPID skills from this directory (the source of truth) to Claude Code
# and Tabnine skill locations. Installed names are prefixed: properties/ is
# installed as cupid-properties, python/ as cupid-python, etc., matching the
# `name:` field in each SKILL.md frontmatter.
#
# Usage:
#   ./sync.sh          # copy (default)
#   ./sync.sh link     # symlink skill dirs instead — edits here apply live
#
# Overridable via env: CLAUDE_SKILLS_DIR, TABNINE_SKILLS_DIR
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS=(properties python java-spring-boot)

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
TABNINE_SKILLS_DIR="${TABNINE_SKILLS_DIR:-$HOME/.tabnine/agent/skills}"
MODE="${1:-copy}"

case "$MODE" in copy|link) ;; *) echo "usage: $0 [copy|link]" >&2; exit 2 ;; esac

# properties/SKILL.md is the canonical generic guidance; copy it into each
# stack skill dir so composition works even when the installed skill can only
# see its own directory (same pattern as notes/references/writing-style.md)
for skill in "${SKILLS[@]}"; do
  [ "$skill" = "properties" ] && continue
  cp -f "$SRC/properties/SKILL.md" "$SRC/$skill/cupid-properties.md"
done

for target in "$CLAUDE_SKILLS_DIR" "$TABNINE_SKILLS_DIR"; do
  mkdir -p "$target"
  for skill in "${SKILLS[@]}"; do
    name="cupid-$skill"
    if [ "$MODE" = "link" ]; then
      # replace any previous copy or stale link with a symlink to the source
      rm -rf "${target:?}/${name}"
      ln -sfn "$SRC/$skill" "$target/$name"
    else
      mkdir -p "$target/$name"
      cp -f "$SRC/$skill/"*.md "$target/$name/"
    fi
    echo "  $MODE  $skill -> $target/$name"
  done
done

echo
echo "Done. Reload to pick up changes:"
echo "  Claude Code: restart session (or /skills if available)"
echo "  Tabnine CLI: /skills reload"
