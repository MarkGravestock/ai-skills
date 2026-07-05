# ai-skills

Source of truth for personal agent skills, synced to Claude Code and Tabnine.

## Install / sync

```bash
./sync.sh          # copy everything to ~/.claude/skills and ~/.tabnine/agent/skills
./sync.sh link     # symlink instead — edits in this repo apply live
```

The root script delegates to the family syncs (`notes/sync.sh`, `cupid/sync.sh`) and then
installs every standalone top-level skill (any directory with a `SKILL.md`). Override targets
via `CLAUDE_SKILLS_DIR`, `TABNINE_SKILLS_DIR`, `NOTES_ROOT`.

## Mental model: guidance at altitudes

The design skills are complementary because each operates at a different **altitude** and
answers a different question. One meta layer sits above them all and acts as the tiebreaker.

| Altitude | Skill(s) | Question it answers |
|---|---|---|
| **Meta — any level** | `simple-design` (Beck's Four Rules) | Is this the simplest design that works? Which guidance wins when they conflict? |
| Class / method (micro) | `software-design-principles` | Is this code well constructed? |
| Component / system (macro) | `cupid/properties` + stack skill (`cupid/python`, `cupid/java-spring-boot`) | Is this a good component to live with? |
| Between components | `coupling-analysis` | Are the dependencies between parts healthy? |

Kent Beck's Four Rules of Simple Design (passes the tests → reveals intention → no
duplication → fewest elements, in priority order) are **fractal** — they apply unchanged at
every altitude, and each altitude skill is an elaboration of them at one level. When rules
from different skills conflict in context, resolve with the four rules in priority order;
`simple-design/SKILL.md` maps each rule to its expression at each altitude.

**Day to day:**

- **Writing / refactoring code** — `software-design-principles` is the active checklist;
  `simple-design` decides when to stop (nothing left to remove).
- **Design or code review** — lead with `cupid/properties` (+ the stack skill for concrete
  evidence); descend to `software-design-principles` for findings inside specific classes.
- **Architecture / boundary questions** — `coupling-analysis`, paired with CUPID's
  Composable and Domain-based properties.
- **Avoid loading every skill for every task** — the frontmatter descriptions encode the
  altitudes so agents route to the right one; each skill's composition section says when to
  escalate or descend.

## Skills

| Skill | Purpose |
|---|---|
| `simple-design` | Beck's Four Rules as meta-guidance and tiebreaker |
| `software-design-principles` | Class/method construction rules (calisthenics, tell-don't-ask, SLAP) |
| `cupid/` | CUPID properties: generic core + Python and Java/Spring Boot stack skills ([README](cupid/README.md)) |
| `coupling-analysis` | Khononov coupling model (strength × distance × volatility) |
| `bug-magnet` | Edge-case and bug-discovery prompts for testing |
| `groovy-spock-testing` | Groovy/Spock test DSL and fixture patterns |
| `java-junit5-testing` | Java/JUnit 5 BDD-style tests, assertion DSLs, test data builders |
| `kotlin-kotest-testing` | Kotlin/Kotest specs, matcher DSLs, data-driven testing |
| `spring-boot-4-gradle-9-upgrade` | Task skill for the Spring Boot 4 / Gradle 9 migration |
| `notes/` | Session-notes system: wrap, ingest, lint ([README](notes/README.md)) |

## Worth including later

- [Tropes.md](https://gist.github.com/ossa-ma/f3baa9d25154c33095e22272c631f5a1) (for writing)
- [Modularity Skills](https://github.com/vladikk/modularity)
