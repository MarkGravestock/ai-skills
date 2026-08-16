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
  [approach.md](../tooling/approach.md), and leave the system releasable when you stop.

Short-circuiting the loop anywhere is the usual failure mode: skipping
Observe (shipping without checking it works), skipping Orient (treating a
backlog as fixed instead of re-reading it against new signal), or padding
Decide/Act with ceremony that doesn't change what gets built.

This is the same mechanism Scrum runs at team scale: a short cycle that
produces a real, inspectable increment, with transparency as the property
that makes inspection honest and adaptation possible ([Empirical Process
Control](https://less.works/less/principles/empirical-process-control),
[Transparency](https://less.works/less/principles/transparency)). The loop
here just runs it without the ceremony, because there's no multi-team
coordination problem to justify the ceremony's cost. See
[Grounding, and what doesn't transfer](#grounding-and-what-doesnt-transfer)
below.

## Why OODA over phase gates

The evidence in [approach.md](../tooling/approach.md) already points here from a
different angle: a full multi-phase spec workflow bought +0.05 on a 5-point
composite for ~70% more wall-clock time, while deterministic hooks bought
roughly three times that gain for a fraction of the cost. Read as a delivery
question rather than a controls question, the lesson is the same: front-load
as little as possible, and spend the saved time cycling the loop faster
rather than planning it more thoroughly. Big-design-up-front is a bet that
Orient can be done once, in advance, correctly. It usually can't; the loop
exists because the cheapest way to find out what's actually needed is to ship
something small and watch what happens.

This is [More with LeSS](https://less.works/less/principles/more-with-less)
applied to process instead of org design: more delivered, with less role,
artifact and ceremony overhead. It's the same instinct behind this repo's
existing rule that any rule expressible as a check becomes a check, not
prose.

## Practices that keep the loop short

- Walking skeleton first. Before depth in any one component, get the
  thinnest possible path end-to-end and deployable (Cockburn), even if every
  part of it is a stub. It exists to open a real feedback channel (build,
  deploy, a user touching it) before investing in any part of the system.
  It's [whole-product thinking](https://less.works/less/principles/whole-product-focus)
  taken to its extreme: customers don't buy a part of the product, so a
  skeleton that's thin everywhere but whole beats a component that's deep
  but disconnected.
- MVP slicing. Cut vertically, by the smallest thing that produces real
  signal, not by the smallest thing that's technically coherent to build.
  A slice that doesn't reach a real observer isn't a slice, it's unfinished
  work in progress. Value and waste are defined by what the observer on the
  other end perceives, not by what's convenient to build. That's
  [customer-centric thinking](https://less.works/less/principles/customer-centric),
  scaled down to whoever is actually receiving the increment.
- Always releasable. Small commits, trunk-based, every increment leaves the
  system working. This is what makes the loop fast rather than risky: the
  deterministic gates in [guardrails-catalogue.md](guardrails-catalogue.md)
  are what make "releasable after every change" affordable instead of
  aspirational. It's a literal, code-level reading of LeSS's perfection
  vision, the ability to change direction at any time without additional
  cost ([Continuous Improvement Towards
  Perfection](https://less.works/less/principles/continuous-improvement-towards-perfection)).
- Feedback as close to real as it can afford to be. Prefer the fastest
  channel that still tells the truth: a type error beats a test, a test
  beats code review, code review beats staging, and staging beats
  production. A fast lie (a mock that always passes) is worse than a slower
  truth, though.

## Systems thinking and queuing theory: what agents change

Agents collapse the cost of Act toward zero: the "typing" part of building
software gets fast. It's tempting to read that as the loop getting faster
everywhere, but
[systems thinking](https://less.works/less/principles/systems-thinking) says
otherwise. Optimizing one part of a system (Act) sub-optimizes the whole
unless the parts around it keep up, and customers experience end-to-end
cycle time, not how fast any one step ran.

[Queuing theory](https://less.works/less/principles/queueing_theory) explains
why this bites in practice. By Little's Law, cycle time is work-in-progress
divided by throughput, and in most delivery systems queue time (waiting for
review, waiting for CI, waiting for the next decision) dwarfs process time
(the work itself). Agents shrink process time; they do nothing for queue
time on their own. If the extra headroom gets spent opening more branches
or running more agent tasks in parallel, work-in-progress rises and cycle
time gets *worse*, not better, even though everyone is typing less.

The consequence: cap how much is in flight at once, and put the time agents
save into shrinking queues (faster review, faster CI, real usage sooner)
rather than into producing more parallel, unreviewed work. A faster Act
phase feeding a slow or backed-up Observe phase just produces more
unvalidated work in progress. The [Lean
Thinking](https://less.works/less/principles/lean-thinking) framing agrees:
optimize the whole stream and remove the bottleneck, don't maximize
utilization of the step that got cheap.

The guardrails catalogue is what makes Act safe to run at agent speed.
Deterministic gates replace the slow, careful judgement a human would apply
by hand, so the loop can stay tight without the usual quality trade-off, but
speed in Act alone doesn't shorten the loop unless Observe and Orient keep
pace.

## Consequences for this repo

- This doc is the "what loop are we running" answer; [approach.md](../tooling/approach.md)
  is "how do we make Act fast and safe" underneath it. Skills are tools
  invoked inside Act, and they don't own the loop; they shouldn't grow
  ceremony that competes with it.
- Any process addition to this repo gets the same question the guardrails
  get: does this shorten or lengthen the Observe→Act cycle? Ceremony that
  doesn't pay for itself in better or faster signal doesn't belong here.
- Cap work-in-progress explicitly rather than maximizing agent throughput:
  one slice moving through Observe→Act at a time beats five slices queued
  behind a review or CI bottleneck.

## Grounding, and what doesn't transfer

The perspective above draws on [LeSS's
principles](https://less.works/less/principles/overview) — empirical process
control, transparency, whole-product focus, customer-centric thinking,
systems thinking, queuing theory, lean thinking, more-with-less, and
continuous improvement towards perfection all map cleanly onto a tight
delivery loop, agent-assisted or not.

What doesn't transfer is the framework itself: LeSS exists to descale the
*coordination* problem of multiple Scrum teams sharing one product (sprints,
a single cross-team backlog, feature-team structure, one product owner).
None of that applies here; there's no multi-team coordination problem to
solve. What's adopted is the perspective (flow, systems thinking,
empirically verified small increments, customer-defined value), not the
Scrum-at-scale mechanics that principle exists to support.
