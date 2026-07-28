#!/usr/bin/env python3
"""Root sync: delegates to the family sync scripts (skills/writing/notes/,
skills/design/cupid/), which own their internal layout, then installs every
standalone skill (any directory containing a SKILL.md, at the top level of
skills/ or under a topic dir — testing/, design/, writing/) to Claude Code
and Tabnine skill locations.

Usage:
    uv run poe sync          # copy (default)
    uv run poe sync-link     # symlink skill dirs instead — edits here apply live

    python sync.py [copy|link]   # same, without poe

Overridable via env: CLAUDE_SKILLS_DIR, TABNINE_SKILLS_DIR, NOTES_ROOT
"""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
from _synclib import link, parse_mode, print_done, remove, targets  # noqa: E402

FAMILIES = ["skills/writing/notes", "skills/design/cupid"]
TOPIC_DIRS = ["skills", "skills/testing", "skills/design", "skills/writing"]


def run_family_syncs(mode: str) -> None:
    for family in FAMILIES:
        print(f"== {family}")
        result = subprocess.run([sys.executable, str(SRC / family / "sync.py"), mode])
        if result.returncode != 0:
            raise SystemExit(result.returncode)
        print()


def standalone_skills() -> list[Path]:
    seen: set[Path] = set()
    dirs: list[Path] = []
    for topic in TOPIC_DIRS:
        base = SRC / topic
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and (entry / "SKILL.md").is_file() and entry not in seen:
                seen.add(entry)
                dirs.append(entry)
    return dirs


def install_standalone(mode: str) -> None:
    print("== standalone skills")
    for skill_dir in standalone_skills():
        skill = skill_dir.name
        for target in targets():
            target.mkdir(parents=True, exist_ok=True)
            dest = target / skill
            if mode == "link":
                link(skill_dir, dest)
            else:
                if dest.exists():
                    remove(dest)
                shutil.copytree(skill_dir, dest)
            print(f"  {mode}  {skill} -> {dest}")


def main(argv: list[str]) -> int:
    # line-buffer stdout so parent prints interleave correctly with the
    # family scripts' subprocess output when this runs under a pipe (e.g. poe)
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)
    mode = parse_mode(argv)
    run_family_syncs(mode)
    install_standalone(mode)
    print_done()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
