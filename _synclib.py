"""Shared helpers for the sync.py scripts in this repo and its skill families.

Not a skill itself — imported by sync.py at the repo root and by the family
scripts under skills/writing/notes/ and skills/design/cupid/. Kept at the repo
root (not under skills/) so it installs to nobody's skill directory.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def targets() -> list[Path]:
    home = Path.home()
    return [
        Path(os.environ.get("CLAUDE_SKILLS_DIR", home / ".claude" / "skills")),
        Path(os.environ.get("TABNINE_SKILLS_DIR", home / ".tabnine" / "agent" / "skills")),
    ]


def remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def link(source: Path, dest: Path) -> None:
    if dest.is_symlink() or dest.exists():
        remove(dest)
    try:
        dest.symlink_to(source, target_is_directory=True)
    except OSError as exc:
        raise SystemExit(
            f"Could not create symlink at {dest}: {exc}\n"
            "On Windows, symlinks need Developer Mode enabled (Settings > "
            "Privacy & security > For developers) or an elevated shell."
        ) from exc


def parse_mode(argv: list[str]) -> str:
    mode = argv[1] if len(argv) > 1 else "copy"
    if mode not in ("copy", "link"):
        print(f"usage: {argv[0]} [copy|link]", file=sys.stderr)
        raise SystemExit(2)
    return mode


def print_done() -> None:
    print()
    print("Done. Reload to pick up changes:")
    print("  Claude Code: restart session (or /skills if available)")
    print("  Tabnine CLI: /skills reload")
