---
name: plain-idiom
description: Strip culture-bound idiom from prose — US sports metaphors, war and violence imagery, and management-speak dead metaphors — while keeping the text informal and human. Use when writing or editing docs, READMEs, ADRs, PR descriptions, incident write-ups, announcements, emails or notes; when asked to make writing less American, less corporate, or more readable for an international audience; or alongside the `tropes` skill on any prose review.
---

# Plain idiom

Companion to the `tropes` skill. That one targets *AI* writing tells. This one targets
*cultural* ones: metaphor borrowed from American ball sports, from war and violence, and
from the management-speak that dead metaphors decay into.

Synthesised from Google's inclusive-documentation and global-audience guidance, Microsoft's
global-communications tips, the GOV.UK words-to-avoid list, and the metaphor-framing
research — full source list at the end of registers.md.

Full catalogue of registers and swaps: **[registers.md](registers.md)** — read it before a
lint pass.

## Why bother

Two separate arguments, worth keeping apart because they justify different strengths of fix:

- **Comprehension.** A metaphorical "handoff", "punt" or "full-court press" only means
  anything to someone who knows American football. Roughly nobody outside the US does. Same
  for cricket in the other direction. This is the argument Google and Microsoft make in their
  global-audience guidance, and it's why the fix is *fewer* culture-bound metaphors, not
  locally-flavoured ones.
- **Framing.** War metaphors don't just obscure — they change what solutions people reach
  for: urgency, adversaries, zero-sum, heroics. Calling a retro a "post-mortem" or a comms
  channel a "war room" quietly imports that. See Flusberg, Matlock & Thibodeau (2018) in
  registers.md.

The comprehension argument says *substitute*. The framing argument says *reconsider the
sentence*.

## The discriminating rule

Borrowed from Google's inclusive-documentation guidance, and it does most of the work:

> **A precise technical term of art is fine. A figurative extension of it is not.**

- `kill -9`, `SIGKILL`, `abort()`, `execute a query`, `attack surface`, `blast radius`,
  `smoke test`, `deadlock` — technical terms, no accurate synonym, leave them alone.
- "we killed that feature", "battle-tested", "in the trenches", "war room", "death march",
  "silver bullet", "moving the goalposts", "punt on it", "ballpark" — figurative, and every
  one has a plainer, shorter alternative.

When a non-inclusive or violent term is baked into an API, config key or CLI flag, keep it
in code font, use it once, then use the plain term in prose.

## Keep the informality

This matters as much as the stripping. Plain-English guides tend to remove voice along with
idiom, and you end up with the flat corporate register — which is worse than the sports
metaphor. Informality does not live in the metaphors. It lives in:

- contractions — *don't*, *it's*, *we'll*
- second person and direct address — *you'll need to*, not *the operator must*
- short sentences, and the occasional very short one
- concrete verbs — *we deleted the index*, not *the index was decommissioned*
- admitting uncertainty in plain words — *I'm not sure this holds under load*
- an occasional aside, joke or parenthetical

Strip the imagery, keep all of the above. If a rewrite makes the sentence stiffer, it's the
wrong rewrite.

## How to apply

1. **While drafting** — the top four to suppress from the first sentence: US ball-sport
   metaphor, war/battle framing, the GOV.UK banned verbs (*drive, unlock, deliver, leverage,
   deep dive, robust, ring-fence, landscape, ecosystem, going forward*), and ableist figures
   of speech (*sanity check, blind to, crazy*).
2. **After drafting** — one explicit pass against registers.md, section by section. For each
   hit, ask which argument applies: if comprehension, substitute; if framing, rewrite the
   thought.
3. **Editing someone else's** — name the register ("that's a baseball one") and propose the
   swap. Don't reflexively rewrite quotes, ticket titles, product names, or established
   internal vocabulary.

## Zero-tolerance list

Everything else in this skill is a judgement call. These are not — delete on sight, no
substitution needed, the sentence is always better without them:

**going forward**, **at this moment in time**, **circle back**, **double-click on that**,
**socialise (an idea)**, **reach out** (say *email*, *ask*, *call*), **learnings** (say
*lessons* or *what we learned*), **utilise** (say *use*).

*going forward* in particular: it's either redundant (the sentence is already in the future
tense) or it's hiding a date. If it's load-bearing, replace it with the actual date —
"from the next release", "after 3 August" — otherwise cut it.

## Calibration

- **The target is density, not zero.** One well-placed idiom in a page reads as personality.
  Four reads as a US management book. The house position is not averse to idiom but against
  it being pervasive: at most one or two per document, and prefer them in asides rather than
  in the load-bearing sentences.
- **Don't swap US idiom for British idiom.** Cricket ("sticky wicket", "knocked for six",
  "on the back foot", "played a straight bat"), rugby, snooker and horse racing are equally
  opaque to a Polish or Indian colleague — often more so. This is the single most common
  mistake when someone tries to de-Americanise their writing.
- **Some things aren't worth the fight.** "Roadmap", "milestone", "pipeline", "backlog" are
  so thoroughly naturalised that replacing them costs clarity. Flag only what still reads as
  a metaphor.
- **Never edit for this at the cost of accuracy.** If the precise word is the violent or
  sporting one, use it.

## Related

- `tropes` — AI writing tells, catalogued in that skill's `tropes.md`. Different axis, same
  object: run both on anything going to a wide audience. A draft can be trope-free and still
  read as a US management memo, or plain and still read as AI.
- The `notes` skills (`session-wrap`, `ingest`, `notes-lint`) carry a short subset of both
  catalogues in their `writing-style.md`, for note prose specifically. Load this skill for
  anything longer or outward-facing.
- British English spelling and date formats are a separate axis; see registers.md § Other
  US defaults.
