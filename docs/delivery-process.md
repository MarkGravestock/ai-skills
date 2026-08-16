# The delivery process

## The loop

Delivery runs as one continuous loop, not a sequence of phases: **Observe →
Orient → Decide → Act**, repeated at the smallest grain that still produces
real signal.

- **Observe** — run the current increment against something real: tests,
  a deployed environment, an actual user. Signal, not a plan document.
- **Orient** — read that signal against the actual goal. What did we learn
  that changes the next step?
- **Decide** — pick the next slice: the thinnest vertical cut that proves or
  disproves the next assumption, not the next technically tidy unit of work.
- **Act** — build it, guarded by the deterministic controls in
  [approach.md](approach.md), and leave the system releasable when you stop.

Short-circuiting the loop anywhere is the usual failure mode: skipping
Observe (shipping without checking it works), skipping Orient (treating a
backlog as fixed instead of re-reading it against new signal), or padding
Decide/Act with ceremony that doesn't change what gets built.

## Why OODA over phase gates

The evidence in [approach.md](approach.md) already points here from a
different angle: a full multi-phase spec workflow bought +0.05 on a 5-point
composite for ~70% more wall-clock time, while deterministic hooks bought
roughly three times that gain for a fraction of the cost. Read as a delivery
question rather than a controls question, the lesson is the same — front-load
as little as possible, and spend the saved time cycling the loop faster
rather than planning it more thoroughly. Big-design-up-front is a bet that
Orient can be done once, in advance, correctly. It usually can't; the loop
exists because the cheapest way to find out what's actually needed is to ship
something small and watch what happens.

## Practices that keep the loop short

- **Walking skeleton first.** Before depth in any one component, get the
  thinnest possible path end-to-end and deployable (Cockburn) — even if every
  part of it is a stub. It exists to open a real feedback channel (build,
  deploy, a user touching it) before investing in any part of the system.
- **MVP slicing.** Cut vertically, by the smallest thing that produces real
  signal, not by the smallest thing that's technically coherent to build.
  A slice that doesn't reach a real observer isn't a slice, it's unfinished
  work in progress.
- **Always releasable.** Small commits, trunk-based, every increment leaves
  the system working. This is what makes the loop fast rather than risky —
  the deterministic gates in [guardrails-catalogue.md](guardrails-catalogue.md)
  are what make "releasable after every change" affordable instead of
  aspirational.
- **Feedback as close to real as it can afford to be.** Prefer the fastest
  channel that still tells the truth: a type error beats a test, a test
  beats code review, code review beats staging, staging beats production —
  but a fast lie (a mock that always passes) is worse than a slower truth.

## Where agents change the loop

Agents collapse the cost of Act toward zero. That moves the bottleneck to
Observe and Orient — to the quality of the feedback available and the
judgement about what it means — not to typing speed. The corollary: time
saved by agent-generated code should go into tightening feedback loops
(better tests, faster CI, real usage sooner), not into generating more code
per iteration. A faster Act phase feeding a slow or noisy Observe phase just
produces more unvalidated work in progress.

The guardrails catalogue is what makes Act safe to run at agent speed:
deterministic gates replace the slow, careful judgement a human would apply
by hand, so the loop can stay tight without the usual quality trade-off.

## Consequences for this repo

- This doc is the "what loop are we running" answer; [approach.md](approach.md)
  is "how do we make Act fast and safe" underneath it. Skills are tools
  invoked inside Act — they don't own the loop and shouldn't grow ceremony
  that competes with it.
- Any process addition to this repo gets the same question the guardrails
  get: does this shorten or lengthen the Observe→Act cycle? Ceremony that
  doesn't pay for itself in better or faster signal doesn't belong here.
