# ai-skills

Working practice for AI-assisted software delivery. The process comes first:
a short, iterative loop — walking skeleton, thinnest next slice, always
releasable, real feedback over up-front planning. The guardrails thesis and
the skills below exist to keep that loop fast and safe, and are synced to
Claude Code and Tabnine.

## Process

Delivery runs as an OODA loop — Observe, Orient, Decide, Act — at the
smallest grain that produces real signal, not as sequential phases.

Reasoning and evidence: [docs/delivery-process.md](docs/delivery-process.md).

## Thesis (guardrails)

Deterministic guardrails beat prompt volume. Frameworks shipping large prompt
corpora ("software factories") underperform their marketing; the reproducible
gain comes from the computational controls they happen to bundle — formatters,
type checkers, architecture rules, tests — rather than from personas and
workflow ceremony. Spend on sensors. This is what makes the Act step of the
loop above fast without being reckless.

Reasoning and evidence: [docs/approach.md](docs/approach.md).

## Contents

```
ai-skills/
├── docs/       delivery process, guardrails approach, dependency/supply-chain gates
├── skills/     on-demand skills — design/, testing/, writing/ topic dirs
└── sync.py     installs everything (via uv run poe sync)
```

| Path | What |
|---|---|
| `docs/delivery-process.md` | The OODA loop, walking skeleton, MVP slicing, why short feedback loops |
| `docs/approach.md` | Guardrails thesis, control taxonomy, evidence base, known limits |
| `docs/guardrails-catalogue.md` | Guardrails by category and type, Java and Python |
| `docs/dependencies.md` | Libraries as guardrails; supply-chain gates |
| `skills/` | On-demand skills — design, testing, writing (catalogue: [skills/README.md](skills/README.md)) |

## Rules

- Deterministic tools own everything they can judge. Skills cover only the rest.
- Auto-fix over review comment; gate over suggestion.
- Any rule expressible as a check becomes a check, not prose.
- Never weaken a quality check to reach green.
- Harness-agnostic where possible. The gauntlet survives a harness swap; a
  prompt corpus does not.

## Install / sync

```bash
uv run poe sync                      # copy everything to ~/.claude/skills and ~/.tabnine/agent/skills
uv run poe sync-link                 # symlink instead — edits in this repo apply live
uv run poe sync -- design/cupid      # narrow to one topic or skill dir, recursively

python sync.py [copy|link] [subdir]   # same, without uv/poe — the script is stdlib-only
```

Pure Python (`sync.py`), so it runs the same way on Windows, macOS and Linux. `uv run poe
...` is the convenience wrapper; `python sync.py` works anywhere a Python 3.9+ interpreter
is on `PATH`, uv or not. Symlink mode (`sync-link`) needs Developer Mode enabled on Windows
(Settings > Privacy & security > For developers) or an elevated shell — unprivileged
`os.symlink` is blocked otherwise.

One script: it walks `skills/` recursively for any directory containing a `SKILL.md` and
installs it under the name in that file's `name:` frontmatter (`skills/design/cupid/python/`
installs as `cupid-python`) — no per-family list of names to maintain. A `subdir` argument
narrows the walk to one topic or a single skill (`design`, `design/cupid`,
`design/cupid/python`) instead of installing everything. A couple of skills also need a
canonical file copied in alongside their `SKILL.md` because an installed skill only ever
sees its own directory (e.g. the CUPID stack skills need `cupid-properties.md`) — declared
in `COMPANION_FILES` near the top of `sync.py`. Override install targets via
`CLAUDE_SKILLS_DIR`, `TABNINE_SKILLS_DIR`, `NOTES_ROOT`. Installed skill names are flat —
the topic dirs organise the repo, not the install targets.

## Skills

The full skill catalogue, plus the altitude model that explains how the design skills
compose with each other, lives in [skills/README.md](skills/README.md).
