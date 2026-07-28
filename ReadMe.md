# ai-skills

Working practice for agentic development. The approach comes first; skills are one
part of it, synced to Claude Code and Tabnine.

## Thesis

Deterministic guardrails beat prompt volume. Frameworks shipping large prompt
corpora ("software factories") underperform their marketing; the reproducible
gain comes from the computational controls they happen to bundle — formatters,
type checkers, architecture rules, tests — rather than from personas and
workflow ceremony. Spend on sensors.

Reasoning and evidence: [docs/approach.md](docs/approach.md).

## Contents

```
ai-skills/
├── docs/       approach, guardrails catalogue, dependency/supply-chain gates
├── skills/     on-demand skills — design/, testing/, writing/ topic dirs
└── sync.py     installs everything (via uv run poe sync)
```

| Path | What |
|---|---|
| `docs/approach.md` | Thesis, control taxonomy, evidence base, known limits |
| `docs/guardrails-catalogue.md` | Guardrails by category and type, Java and Python |
| `docs/dependencies.md` | Libraries as guardrails; supply-chain gates |
| `skills/` | On-demand skills — design, testing, writing |

## Non-negotiables

- Deterministic tools own everything they can judge. Skills cover only the rest.
- Auto-fix over review comment; gate over suggestion.
- Any rule expressible as a check becomes a check, not prose.
- Never weaken a quality check to reach green.
- Harness-agnostic where possible. The gauntlet survives a harness swap; a
  prompt corpus does not.

## Install / sync

```bash
uv run poe sync         # copy everything to ~/.claude/skills and ~/.tabnine/agent/skills
uv run poe sync-link    # symlink instead — edits in this repo apply live

python sync.py [copy|link]   # same, without uv/poe — the scripts are stdlib-only
```

Pure Python (`sync.py`, plus `_synclib.py` and the family scripts), so it runs the same way
on Windows, macOS and Linux. `uv run poe ...` is the convenience wrapper; `python sync.py`
works anywhere a Python 3.9+ interpreter is on `PATH`, uv or not. Symlink mode
(`sync-link`) needs Developer Mode enabled on Windows (Settings > Privacy & security > For
developers) or an elevated shell — unprivileged `os.symlink` is blocked otherwise.

The root script delegates to the family syncs (`skills/writing/notes/sync.py`,
`skills/design/cupid/sync.py`) and then installs every standalone skill (any directory
with a `SKILL.md`, at the top level of `skills/` or under a topic dir). Override targets
via `CLAUDE_SKILLS_DIR`, `TABNINE_SKILLS_DIR`, `NOTES_ROOT`. Installed skill names are
flat — the topic dirs organise the repo, not the install targets.

## Mental model: guidance at altitudes

The design skills are complementary because each operates at a different **altitude** and
answers a different question. One meta layer sits above them all and acts as the tiebreaker.

| Altitude | Skill(s) | Question it answers |
|---|---|---|
| **Meta — any level** | `simple-design` (Beck's Four Rules) | Is this the simplest design that works? Which guidance wins when they conflict? |
| **Cross-cutting — any level** | `naming` | Does this identifier communicate as much as it could, given its scope and context? |
| Class / method (micro) | `software-design-principles` | Is this code well constructed? |
| Component / system (macro) | `cupid-properties` + stack skill (`cupid-python`, `cupid-java-spring-boot`) | Is this a good component to live with? |
| Between components | `coupling-analysis` | Are the dependencies between parts healthy? |

Kent Beck's Four Rules of Simple Design (passes the tests → reveals intention → no
duplication → fewest elements, in priority order) are **fractal** — they apply unchanged at
every altitude, and each altitude skill is an elaboration of them at one level. When rules
from different skills conflict in context, resolve with the four rules in priority order;
`simple-design/SKILL.md` maps each rule to its expression at each altitude.

Day to day: writing or refactoring code makes `software-design-principles` the
active checklist, with `simple-design` deciding when to stop (nothing left to
remove). For design or code review, lead with `cupid-properties` (plus the
stack skill for concrete evidence), then descend to
`software-design-principles` for findings inside specific classes.
Architecture and boundary questions route to `coupling-analysis`, paired with
CUPID's Composable and Domain-based properties. Don't load every skill for
every task — the frontmatter descriptions encode the altitudes so agents
route to the right one, and each skill's composition section says when to
escalate or descend.

## Skills

**Design (`skills/design/`)**

| Skill | Purpose |
|---|---|
| `simple-design` | Beck's Four Rules as meta-guidance and tiebreaker |
| `naming` | Technique for deriving names — calling-context, wishful thinking, domain types, scope-length |
| `software-design-principles` | Class/method construction rules (calisthenics, tell-don't-ask, SLAP) |
| `cupid/` | CUPID properties: generic core + Python and Java/Spring Boot stack skills ([README](skills/design/cupid/README.md)) |
| `coupling-analysis` | Stub delegating to Khononov's [Modularity plugin](https://github.com/vladikk/modularity) |
| `validation-review` | Domain model validation review for Java/Spring/DDD (Design by Contract lens) |
| `plan-eng-review` | Interactive eng-manager-mode plan review before implementation |

**Testing (`skills/testing/`)**

| Skill | Purpose |
|---|---|
| `bug-magnet` | Edge-case and bug-discovery prompts for testing |
| `groovy-spock-testing` | Groovy/Spock test DSL and fixture patterns |
| `java-junit5-testing` | Java/JUnit 5 BDD-style tests, assertion DSLs, test data builders |
| `kotlin-kotest-testing` | Kotlin/Kotest specs, matcher DSLs, data-driven testing |

**Writing (`skills/writing/`)**

| Skill | Purpose |
|---|---|
| `notes/` | Session-notes system: wrap, ingest, lint ([README](skills/writing/notes/README.md)) |
| `tropes` | Avoid AI writing tells — wraps the [tropes.fyi](https://tropes.fyi) catalogue |

**Other**

| Skill | Purpose |
|---|---|
| `spring-boot-4-gradle-9-upgrade` | Task skill for the Spring Boot 4 / Gradle 9 migration (own dir directly under `skills/` — task skills may get their own topic dir if more accrue) |
