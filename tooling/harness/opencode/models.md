# Model picks

The volatile file. Everything with a three-month half-life lives here so the rest of the
harness docs stay accurate (principle 4).

**Last reviewed: 2026-08-16**

## Current

| Tier | Model | Why |
| --- | --- | --- |
| `or-heavy` | Claude Sonnet 5 | Best of the current field on long-horizon agentic work, which is what Java refactoring across a Gradle module graph actually is. Coordinates, plans, edits. |
| `or-cheap` | Gemini 3 Flash | Cost and latency. Read-only exploration and mechanical edits. Chosen for price rather than quality; the weakest link in this setup. |

The OpenRouter IDs and per-model limits for both are filled in at
[examples/opencode.jsonc](./examples/opencode.jsonc), taken from the model pages on the
review date above. The cheap tier sits on a preview slug, which OpenRouter can withdraw at
short notice — see the candidate below.

## Reasoning, August 2026

Java is under-measured. SWE-bench Verified is entirely Python; the only mainstream Java
coverage is [SWE-bench Multilingual](https://www.swebench.com/multilingual-leaderboard.html)
(43 Java instances of 300) and Multi-SWE-Bench, which vendors rarely report. Microsoft's
SWE-Sharp-Bench work found identical configurations solving 70% of Python tasks against 40%
of C# ones, so assume a real haircut off any Python number.

Cross-vendor comparison of headline scores is close to meaningless anyway: vendors run tuned
agent harnesses while Scale runs identical scaffolding, and
[Morph's breakdown](https://www.morphllm.com/swe-bench-pro) puts the gap at 10–30 points.

So the picks lean on long-horizon agentic behaviour rather than patch-generation scores, and
on the assumption that the cheap tier's failures are caught by the strong tier reviewing what
comes back.

Considered and rejected:

- **Kimi K2.6** — a head-to-head on workflow orchestration showed it losing badly on lease
  handling, cross-run scheduling and streaming, which is close to the Kafka and Spring
  Modulith work this is for. Superseded by K2.7 Code, which cut its hallucination rate
  substantially; revisit that instead.
- **Hy3** — strong on tool orchestration and unusually stable across scaffoldings, but
  Tencent's own tables concede the agentic coding suite to GLM-5.2. If an open-weight model
  is wanted, GLM-5.2 or later is the better pick.

## Candidate for the next refresh

**Gemini 3.7 Flash** ([model page](https://openrouter.ai/google/gemini-3.7-flash)), released
three days before this review. Same context and output limits as the current cheap tier, and
a stable release rather than a preview, so the slug won't be withdrawn under you. Its
headline rate is a little above the current pick; the cheapest endpoint OpenRouter routes to
comes in below it.

Not adopted here because nothing has actually been run on it. Try it on a week of `@explore`
sweeps, compare the spend on the two keys, and switch if it holds up.

## Refresh trigger

The OpenRouter activity dashboard, not a benchmark post. Review when the tier split looks
wrong (see [README.md](./README.md)) or when a cheap-tier release plausibly changes the sums,
since that's where a better model has most effect.

Record the date and the reasoning on each refresh. The reasoning is what makes the next one
quick.
