---
name: simple-design
description: Kent Beck's Four Rules of Simple Design as meta-guidance — passes the tests, reveals intention, no duplication, fewest elements, in priority order. Applies fractally at every level from a method to a system. Use as the tiebreaker when design guidance conflicts, when deciding whether to add or remove abstraction, or when judging whether a design is done. Composes above software-design-principles (class/method), cupid-properties (component/system), and coupling-analysis (between components).
---

# Four Rules of Simple Design (meta-guidance)

Kent Beck's definition of simple design, in **priority order** — a design is simple when it:

1. **Passes the tests** — it demonstrably does what it is supposed to do. Nothing else
   matters until this holds; "elegant but wrong" is not a design.
2. **Reveals intention** — a reader can tell *what* it does and *why* it exists without
   archaeology. Code is read far more than written.
3. **Contains no duplication** — once and only once: every piece of *knowledge* (a rule, a
   decision, a fact) has one authoritative home. This is about duplicated knowledge, not
   textually similar code — two similar-looking functions encoding different decisions are
   not duplication; one rule encoded in two places is, however different they look.
4. **Has the fewest elements** — no classes, methods, layers, or abstractions that don't
   serve the first three rules. Speculative generality fails this rule by definition.

When rules conflict, the earlier rule wins. (Beck's own orderings have varied on whether 2 or
3 comes first; the consensus is that the pair matters more than their order, and both are
subordinate to passing tests and senior to fewest elements.)

## Why this is meta-guidance

The rules are **fractal**: they apply unchanged to a method, a class, a component, a service
boundary, and a whole architecture. The altitude-specific skills in this repo are
elaborations of these rules at one level — so when guidance from those skills conflicts, or
is silent, resolve with the four rules in priority order.

## The rules at each altitude

| Rule | Class/method (`software-design-principles`) | Component/system (`cupid-properties` + stack) | Between components (`coupling-analysis`) |
|---|---|---|---|
| **1 Passes the tests** | Fail-fast, illegal states unrepresentable, constructs that are trivially testable | Predictable: deterministic, robust, observable; easy to characterise | Explicit contracts; consumer-driven contract tests |
| **2 Reveals intention** | Intention-revealing names, composed method, no generic names | Composable (intention-revealing surface), Unix (one nameable purpose), Domain-based language | Boundaries named after the domain; dependency direction tells the story |
| **3 No duplication** | Extract methods/values so each rule lives once | One component owns each domain concept; single source of truth | Duplicated knowledge across components is hidden coupling (shared knowledge is what couples) |
| **4 Fewest elements** | YAGNI; no single-implementation interfaces; no speculative parameters | Caller-combination test — don't split without a caller who needs the parts separately | Fewest integration points; don't distribute what can stay together |

## Using the rules as a tiebreaker

- **"Extract this duplication into a shared library used by two services?"** Rule 3 says
  dedupe — but only if it is one piece of knowledge. Across a boundary, a shared library
  couples deployments (an element and a coupling cost, rule 4). If the two copies can evolve
  independently, they were never duplication of knowledge; leave them.
- **"Add an interface so it's testable?"** Only if it genuinely serves rule 1; if the concrete
  class is already testable, the interface fails rule 4.
- **"Split this class because it's over 150 lines?"** A micro rule (fewest-elements pressure
  in the other direction). Split only if the pieces each reveal an intention (rule 2) or a
  caller wants them separately; otherwise the seam adds elements.
- **When in doubt, delete** — remove the element and see whether a test (rule 1) or a
  reader (rule 2) actually suffers.

The rules also define **done**: a design that passes its tests, says what it means, states
everything once, and has nothing left to remove is finished — stop designing.

## Further reading

- Kent Beck, *Extreme Programming Explained* (the original formulation)
- [BeckDesignRules](https://martinfowler.com/bliki/BeckDesignRules.html) — Martin Fowler
- [Putting an Age-Old Battle to Rest](https://blog.thecodewhisperer.com/permalink/putting-an-age-old-battle-to-rest) — J.B. Rainsberger, on the rule 2/3 ordering
