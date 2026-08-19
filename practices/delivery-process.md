# The delivery process

## The loop

Delivery runs as one continuous loop, not a sequence of phases: **Observe →
Orient → Decide → Act**, repeated at the smallest grain that still produces
real signal.

- **Observe** — run the current increment against something real: tests, a
  deployed environment, an actual user. Signal, not a plan document.
- **Orient** — read that signal against the actual goal. What did we learn
  that changes the next step?
- **Decide** — pick the next slice: the thinnest vertical cut that proves or
  disproves the next assumption, not the next technically tidy unit of work.
- **Act** — build it, guarded by the deterministic controls in
  [approach.md](../tooling/approach.md), and leave the system releasable when
  you stop.

Short-circuiting it is the usual failure: shipping without checking it works
(no Observe), treating the backlog as fixed instead of re-reading it against
new signal (no Orient), or padding Decide and Act with ceremony that doesn't
change what gets built.

## Why OODA over phase gates

The evidence in [approach.md](../tooling/approach.md) points here from a
different angle: a full multi-phase spec workflow bought +0.05 on a 5-point
composite for ~70% more wall-clock time, while deterministic hooks bought
roughly three times that gain for a fraction of the cost.

Big-design-up-front bets that Orient can be done once, in advance, correctly.
It usually can't. The cheapest way to find out what's needed is to ship
something small and watch what happens.

## Practices that keep the loop short

- Walking skeleton first. The thinnest path end-to-end and deployable
  (Cockburn), even if every part of it is a stub. It exists to open a real
  feedback channel (build, deploy, a user touching it) before any one
  component gets depth. Thin everywhere but whole beats deep but disconnected.
- MVP slicing. Cut vertically, by the smallest thing that produces real
  signal, not the smallest thing that's technically coherent to build. A slice
  that doesn't reach a real observer isn't a slice, it's work in progress.
- Always releasable. Small commits, trunk-based, every increment leaves the
  system working. The deterministic gates in
  [guardrails-catalogue.md](guardrails-catalogue.md) are what make that
  affordable rather than aspirational.
- Feedback as close to real as it can afford to be. A type error beats a test,
  a test beats code review, code review beats staging, staging beats
  production. A fast lie — a mock that always passes — is worse than a slower
  truth.

## What agents change

Agents collapse the cost of Act toward zero. That does not make the loop
faster. By Little's Law, cycle time is work-in-progress divided by throughput,
and queue time (waiting for review, for CI, for the next decision) usually
dwarfs the work itself. Agents shrink process time and do nothing for queue
time.

So if the headroom goes into more branches and more parallel agent tasks,
work-in-progress rises and cycle time gets *worse* while everyone types less.
Cap what's in flight, and spend the saved time shrinking queues instead.

## Consequences for this repo

- Any process addition gets the guardrails question: does this shorten or
  lengthen Observe→Act? Ceremony that doesn't pay for itself in better or
  faster signal doesn't belong here.
- Cap work-in-progress rather than maximising agent throughput. One slice
  moving through Observe→Act beats five queued behind a review bottleneck.
- Skills are invoked inside Act. They don't own the loop, and shouldn't grow
  ceremony that competes with it.

## Grounding, and what doesn't transfer

The loop is Scrum's inspect-and-adapt cycle without the ceremony, and the
reasoning leans on [LeSS's principles](https://less.works/less/principles/overview):

| Principle | Where it lands above |
|---|---|
| [Empirical process control](https://less.works/less/principles/empirical-process-control), [Transparency](https://less.works/less/principles/transparency) | The loop itself — short cycles producing an inspectable increment |
| [Whole-product focus](https://less.works/less/principles/whole-product-focus) | Walking skeleton — customers don't buy part of a product |
| [Customer-centric](https://less.works/less/principles/customer-centric) | MVP slicing — value is defined by the observer, not the builder |
| [Continuous improvement towards perfection](https://less.works/less/principles/continuous-improvement-towards-perfection) | Always releasable — change direction at any time without extra cost |
| [Systems thinking](https://less.works/less/principles/systems-thinking), [Queuing theory](https://less.works/less/principles/queueing_theory), [Lean thinking](https://less.works/less/principles/lean-thinking) | What agents change — optimise the stream, not the step that got cheap |
| [More with LeSS](https://less.works/less/principles/more-with-less) | Why OODA over phase gates — more delivered, less ceremony |

What doesn't transfer is the framework itself. LeSS descales the
*coordination* problem of multiple teams on one product: sprints, a single
cross-team backlog, feature-team structure, one product owner. There's no
multi-team coordination problem here, so the perspective transfers and the
Scrum-at-scale mechanics don't.
