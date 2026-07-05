---
name: cupid-properties
description: Dan North's CUPID properties for joyful, maintainable code — Composable, Unix philosophy, Predictable, Idiomatic, Domain-based. Language and technology agnostic. Use when asked to review or improve code design quality, assess a codebase against CUPID, compare CUPID with SOLID, or plan a refactoring direction. Composes with stack-specific skills (e.g. cupid-python, cupid-java-spring-boot) which supply concrete implementation advice.
---

# CUPID Properties (Generic Guidance)

CUPID is Dan North's framework of five **properties** that make code a joy to work with:
**C**omposable, **U**nix philosophy, **P**redictable, **I**diomatic, **D**omain-based.

## How this skill composes

This skill is the language-agnostic core: definitions, assessment model, and review lens.
When working in a specific technology, **also load the matching stack-specific skill** if one
exists (e.g. `cupid-python` for Python, `cupid-java-spring-boot` for Java/Spring Boot). The
stack skill supplies concrete idioms, libraries, and code patterns; this skill supplies the
properties themselves and how to judge them. If no stack skill exists, apply this guidance
directly and translate the property tests into the idioms of the language at hand.

This skill judges design at **component and system level** (macro). Two complementary skills
operate at other altitudes and compose with it:

- `software-design-principles` — class/method-level construction rules (calisthenics,
  tell-don't-ask, SLAP). Load it when writing or refactoring the code *inside* components.
- `coupling-analysis` — Khononov's coupling model (strength × distance × volatility) for
  analysing dependencies *between* components; pairs with Composable and Domain-based.

## Properties, not principles

The central philosophical move: CUPID describes **properties** (qualities code exhibits to a
degree), not **principles** (rules you comply with or violate).

- Principles are binary — you pass or fail. Properties are **directional** — code is closer to
  or further from the centre, and there is always a clear direction of travel.
- Any movement toward a property improves the code, regardless of starting point. This makes
  CUPID practical for legacy code: you never need a big-bang rewrite, only a direction.
- The properties are **mutually reinforcing**: improving one typically improves others
  (e.g. domain-based structure tends to make components single-purpose and composable).

North chose the properties against three criteria — they must be **practical** (easy to
articulate, assess, and adopt incrementally), **human** (about the experience of people working
with the code, not abstract metrics), and **layered** (simple guidance for newcomers, depth for
experts).

## Why CUPID? The gaps in SOLID

Use SOLID-style rules, if at all, for local code organisation; use CUPID to judge whether a
system is good to live with. North's critique of each SOLID principle:

| SOLID principle | Critique |
|---|---|
| **S**ingle Responsibility | Vague — "one reason to change" is undefinable for non-trivial code, and drives artificial seams. Alternative: code that *fits in your head* at every level of granularity. |
| **O**pen/Closed | A 1990s constraint from when changing code was risky. Version control and refactoring tools made code malleable — just change it. |
| **L**iskov Substitution | Conflates subtypes with subclasses; presupposes inheritance hierarchies. Prefer small, simple types that compose. |
| **I**nterface Segregation | Remediation for interfaces that were already too big — a "stable door" strategy, not a principle. Don't create the mess. |
| **D**ependency Inversion | Valuable only when multiple implementations genuinely exist, which is rare. Applied universally it produces abstraction forests; a single-implementation interface adds cost, not value. |

None of these address what actually hurts in production and maintenance: unclear purpose,
unpredictable behaviour under stress, alien style, and structure that fights the domain.

---

## The five properties

### C — Composable: plays well with others

Software that is easy to use gets reused. Assess three sub-properties:

1. **Small surface area** — a narrow, opinionated API. A prospective user should be able to
   assess fit in about two minutes and walk away early if it doesn't fit. Too broad invites
   conflicts and cognitive load; too granular creates tacit-knowledge puzzles about how the
   pieces go together.
2. **Intention-revealing** — names and structure communicate purpose without reading the
   implementation. Favour tiered discoverability: a 2-minute readme, a 10-minute guide, a deep
   dive — each letting the user invest incrementally.
3. **Minimal dependencies** — every dependency a component declares is imposed on every
   consumer (version conflicts, transitive weight). Beware the *gorilla problem*: the user
   wanted a banana and got a gorilla holding the banana, and the entire jungle. Keep core
   domain types dependency-free; let consumers opt in to integrations.

### U — Unix philosophy: does one thing well

A component should have a single, well-defined **purpose from the outside** — from the
perspective of its callers, not its internal organisation.

**Single purpose (outside-in) is not Single Responsibility (inside-out):**

| | Unix philosophy (CUPID) | Single Responsibility (SOLID) |
|---|---|---|
| Perspective | Outside-in — what do callers need from me? | Inside-out — how many reasons to change? |
| Split criterion | Callers need the parts in different combinations | Internal change vectors differ |
| Failure mode | Under-splitting loses focus | Over-splitting creates artificial seams |

**The caller-combination test** — the key practical tool for deciding whether to split:
*Would a caller ever want piece A without piece B, or wire them in a different combination?*

- **Yes** → separating them creates genuine composability. This is exactly why Unix pipes work:
  `grep`, `sort`, `uniq` are separate because callers genuinely recombine them
  (`grep ERROR | sort | uniq -c` vs `grep ERROR | sort -k1 | head`).
- **No** → the split is internal housekeeping leaking into the public API. Two components that
  must always change and deploy together are one component with interface overhead.

A component whose name needs "and" to describe, or a `Manager`/`Processor` with unrelated
method clusters, likely contains several single-purpose components that haven't been named yet.

### P — Predictable: does what you expect

Code behaves consistently and reliably — and verifying this is not just possible but *easy*.
Predictability is a generalisation of testability that extends to runtime behaviour.

1. **Behaves as expected** — intended behaviour is apparent from structure and naming alone;
   even untested code should be straightforward to write characterisation tests for.
2. **Deterministic** — same inputs, same observable outcome, within stated operational bounds.
   Three dimensions:
   - **Robustness** — breadth of situations covered; limitations are obvious, not surprising.
   - **Reliability** — consistent behaviour within the covered scenarios.
   - **Resilience** — graceful degradation under unexpected perturbation (load, failure,
     bad input), not collapse.
3. **Observable** — the code is designed to tell you what it is doing. North's six-stage
   maturity model (most software never gets past stage 1):

   | Stage | Meaning |
   |---|---|
   | 1 Instrumentation | The software communicates what it is doing |
   | 2 Telemetry | That information is available remotely |
   | 3 Monitoring | Someone/something receives and visualises it |
   | 4 Alerting | Patterns in the data trigger reactions |
   | 5 Predicting | Historical data anticipates events |
   | 6 Adapting | The system changes itself in response |

Recurring predictability concerns in any stack: deterministic functions over hidden state;
explicit handling of time, randomness, and I/O; bounded queues and backpressure instead of
unbounded buffering; idempotent handling of retried requests; timeouts, retries with backoff
and jitter, and circuit breaking at integration points.

### I — Idiomatic: feels natural

Code should feel familiar to someone fluent in the language and ecosystem who has never seen
this codebase. Non-idiomatic code imposes extraneous cognitive load on everyone who reads it.
The target reader is **an experienced practitioner of the stack who doesn't know this code** —
not a beginner, and not the original author.

1. **Language idioms** — every ecosystem has conventions (naming, error handling, resource
   management, project layout). Learn them deliberately; the only way to be confident you write
   idiomatic code is to take the time to learn the idioms. Watch for "accent" code — writing
   one language with the habits of another.
2. **Local (team) idioms** — where the language permits many styles, the team must choose and
   record its own: formatters and linters enforced in CI, and Architecture Decision Records for
   conventions tooling can't enforce (error envelope, logging events vs metrics, package
   layout, exception strategy). These decisions deserve the same rigour as architecture
   decisions.

### D — Domain-based: in language and structure

Code should minimise the cognitive distance between the business need and its implementation —
someone listening to a design discussion shouldn't be able to tell whether it's about the code
or the business.

1. **Domain-based language** — express concepts as domain types, not computer-science
   constructs. `Surname` beats `string[30]`; `Money` beats a float. Domain types carry
   invariants and intent; primitives carry neither.
2. **Domain-based structure** — the directory/module layout mirrors the domain, not the
   framework scaffold. A layout of `controllers/`, `services/`, `models/` scatters every
   domain change across the tree; a layout of `appointments/`, `patient_history/`,
   `compliance/` keeps each change local. Adding a domain capability should add a directory,
   not touch five.
3. **Domain-based boundaries** — when structure aligns with domain boundaries, those
   boundaries can become deployment boundaries. Extracting a service becomes a move, not a
   rewrite; the monolith/microservice decision becomes reversible.

---

## Assessment scorecard

Rate each property 0–3:

| Score | Meaning |
|---|---|
| 0 | No evidence of this property |
| 1 | Informal / inconsistent application |
| 2 | Consistent, evidenced in code, tests, or metrics |
| 3 | Embedded in tooling, pipelines, and process with automated verification |

Thresholds (for production-readiness style reviews):
- Average ≥ 2.5 — ready to scale
- 1.5–2.4 — limited release; fix the lowest-scoring property first
- < 1.5 — improve before scaling

Because properties are directional, the output of an assessment is not a pass/fail verdict but
a **direction of travel**: name the lowest-scoring property and the smallest next step toward
its centre. Stack-specific skills define what each score looks like as concrete evidence.

## CUPID as a code-review lens

| Property | Review question |
|---|---|
| **Composable** | Can I use this component without pulling in things I don't need? Is the API surface the minimum needed? |
| **Unix philosophy** | From a caller's perspective, does this do exactly one thing? Would a different name reveal a hidden second purpose? Does the caller-combination test justify each seam? |
| **Predictable** | Is the result always the same for the same input? What happens when a dependency is slow, a request is retried, a queue fills? Can I tell what it's doing in production? |
| **Idiomatic** | Does this look like it was written by someone fluent in this stack and this team's conventions? Would a new joiner find it familiar? |
| **Domain-based** | Do the names come from the business domain or from the framework? If I renamed this module, would the new name mean something to a domain expert? |

## Further reading

- [CUPID — for joyful coding](https://dannorth.net/blog/cupid-for-joyful-coding/) — Dan North (the definitive article)
- [CUPID — the back story](https://dannorth.net/blog/cupid-the-back-story/) — Dan North (the SOLID critique)
- [cupid.dev](https://cupid.dev/) — community site with per-property pages and case studies
- [Unpacking CUPID for infrastructure code](https://infrastructure-as-code.com/posts/cupid-for-infrastructure.html) — Kief Morris (applying the properties beyond application code)
