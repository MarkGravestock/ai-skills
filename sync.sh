#!/usr/bin/env bash
# Root sync: delegates to the family sync scripts (notes/, cupid/), which own
# their internal layout, then installs every standalone top-level skill (any
# directory containing a SKILL.md) to Claude Code and Tabnine skill locations.
#
# Usage:
#   ./sync.sh          # copy (default)
#   ./sync.sh link     # symlink skill dirs instead — edits here apply live
#
# Overridable via env: CLAUDE_SKILLS_DIR, TABNINE_SKILLS_DIR, NOTES_ROOT
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-copy}"
case "$MODE" in copy|link) ;; *) echo "usage: $0 [copy|link]" >&2; exit 2 ;; esac

CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
TABNINE_SKILLS_DIR="${TABNINE_SKILLS_DIR:-$HOME/.tabnine/agent/skills}"

# Skill families with their own sync scripts
for family in notes cupid; do
  echo "== $family"
  "$SRC/$family/sync.sh" "$MODE"
  echo
done

# Standalone skills: any top-level directory containing SKILL.md
echo "== standalone skills"
for dir in "$SRC"/*/; do
  skill="$(basename "$dir")"
  [ -f "$dir/SKILL.md" ] || continue
  for target in "$CLAUDE_SKILLS_DIR" "$TABNINE_SKILLS_DIR"; do
    mkdir -p "$target"
    if [ "$MODE" = "link" ]; then
      rm -rf "${target:?}/${skill}"
      ln -sfn "${dir%/}" "$target/$skill"
    else
      mkdir -p "$target/$skill"
      cp -Rf "$dir"* "$target/$skill/"
    fi
    echo "  $MODE  $skill -> $target/$skill"
  done
done

echo
echo "Done. Reload to pick up changes:"
echo "  Claude Code: restart session (or /skills if available)"
echo "  Tabnine CLI: /skills reload"
