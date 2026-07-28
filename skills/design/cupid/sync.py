#!/usr/bin/env python3
"""Sync CUPID skills to Claude Code and Tabnine skill locations.

Installed names are prefixed: properties/ is installed as cupid-properties,
python/ as cupid-python, etc., matching the `name:` field in each SKILL.md
frontmatter.

Usage:
    python sync.py          # copy (default)
    python sync.py link     # symlink skill dirs instead — edits here apply live

Overridable via env: CLAUDE_SKILLS_DIR, TABNINE_SKILLS_DIR
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from _synclib import link, parse_mode, print_done, remove, targets  # noqa: E402

SKILLS = ["properties", "python", "java-spring-boot"]


def install(mode: str) -> None:
    # properties/SKILL.md is the canonical generic guidance; copy it into each
    # stack skill dir so composition works even when the installed skill can
    # only see its own directory (same pattern as notes/references/writing-style.md)
    for skill in SKILLS:
        if skill == "properties":
            continue
        shutil.copy2(SRC / "properties" / "SKILL.md", SRC / skill / "cupid-properties.md")

    for target in targets():
        target.mkdir(parents=True, exist_ok=True)
        for skill in SKILLS:
            name = f"cupid-{skill}"
            dest = target / name
            if mode == "link":
                link(SRC / skill, dest)
            else:
                if dest.exists():
                    remove(dest)
                dest.mkdir(parents=True, exist_ok=True)
                for md in (SRC / skill).glob("*.md"):
                    shutil.copy2(md, dest / md.name)
            print(f"  {mode}  {skill} -> {dest}")


def main(argv: list[str]) -> int:
    install(parse_mode(argv))
    print_done()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
