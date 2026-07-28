#!/usr/bin/env python3
"""Sync skills from this directory to Claude Code and Tabnine skill
locations, and the notes tooling to the notes root.

Usage:
    python sync.py          # copy (default)
    python sync.py link     # symlink skill dirs instead — edits here apply live

Overridable via env: CLAUDE_SKILLS_DIR, TABNINE_SKILLS_DIR, NOTES_ROOT
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from _synclib import link, parse_mode, print_done, remove, targets  # noqa: E402

SKILLS = ["session-wrap", "notes-lint", "ingest"]


def install(mode: str) -> None:
    # references/writing-style.md is canonical; copy it into each skill dir so
    # the skill has it alongside SKILL.md (skills only see their own directory)
    for skill in SKILLS:
        shutil.copy2(SRC / "references" / "writing-style.md", SRC / skill / "writing-style.md")

    for target in targets():
        target.mkdir(parents=True, exist_ok=True)
        for skill in SKILLS:
            dest = target / skill
            if mode == "link":
                link(SRC / skill, dest)
            else:
                if dest.exists():
                    remove(dest)
                dest.mkdir(parents=True, exist_ok=True)
                for md in (SRC / skill).glob("*.md"):
                    shutil.copy2(md, dest / md.name)
            print(f"  {mode}  {skill} -> {dest}")

    notes_root = Path(os.environ.get("NOTES_ROOT", Path.home() / "notes"))
    (notes_root / "tools").mkdir(parents=True, exist_ok=True)
    (notes_root / "raw").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / "tools" / "notes_tools.py", notes_root / "tools" / "notes_tools.py")
    print(f"  copy  tools/notes_tools.py -> {notes_root / 'tools'}")


def main(argv: list[str]) -> int:
    install(parse_mode(argv))
    print_done()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
