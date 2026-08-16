# Harness

How the agentic coding harness is configured, and why. The skills in this repo are portable
across harnesses; this section covers the parts that aren't.

Current harnesses: Claude Code (personal), opencode (work).

Skill installation is a separate concern and lives in the root
[ReadMe](../../ReadMe.md#install--sync) — `tooling/sync.py` already installs to all three. This section
is about everything else: models, providers, agents, spend.

## Principles

These hold across harnesses. Everything below them is configuration, and configuration
expires.

### 1. Enforcement belongs in the tooling, not the prompt

A system prompt asking a model to stop after five reads, stay under budget, or run the tests
is advisory. Models ignore advisory instructions, and the ones that ignore them most are
often the strongest. Anything that actually matters gets enforced somewhere the model can't
argue with: a Gradle check, a permissions denial, a spend cap that returns 403, a step limit
in config.

Prompts are for intent. Tooling is for rules.

The corollary: when a rule can only be expressed as a prompt, accept that it will sometimes
be ignored, and make sure the failure mode is cheap.

### 2. Simple beats clever

Every mechanism added to the harness is a thing to maintain, debug and explain. The bar for
adding one is that it solves a problem you've actually hit, not one you can imagine hitting.

Prefer, in order: no mechanism, config, a script you own, someone else's plugin.

### 3. Structural decisions, not per-task ones

An engineer should not be choosing a model, a context strategy or a tool allowlist per task.
Those choices belong to a role — an agent, a command, a project — checked into a repo where
they can be reviewed and changed once. The engineer picks the role, which is a decision they
were making anyway.

Where a per-task decision genuinely is needed, make it a keystroke rather than a judgement
delegated to a model.

### 4. Investment proportionate to half-life

Models, plugin APIs and config schemas change on a timescale of months. Skills, principles
and deterministic guardrails don't. Put the effort into the second group and keep the first
group isolated so refreshing it is an edit rather than an excavation.

Practically: no model IDs in prose, no prices in documentation, no tier taxonomies baked into
guides. Those live in one dated file per harness, with the reasoning recorded so the next
refresh is informed.

### 5. Distilled docs reference, they don't copy

Anything that will drift — API shapes, flag names, pricing, benchmark numbers — gets a link,
not a transcription. A stale copy is worse than no copy, because it's believed.

## Contents

- [`opencode/`](./opencode) — opencode setup, including the two-tier model configuration
- Claude Code — no harness-specific config beyond the skills; see the repo root
- Tabnine — skills only; nothing to configure here
