---
name: tropes
description: Avoid AI writing tropes in prose. Use when writing or editing text meant for human readers — docs, READMEs, blog posts, announcements, PR descriptions, emails, notes — or when asked to make text sound less AI-generated, review writing style, or de-slop a draft. Wraps the tropes.fyi catalogue of AI writing tells (negative parallelism, delve-family vocabulary, rule-of-three abuse, em-dash overuse, and ~30 more patterns).
---

# AI Writing Tropes (wrapper)

This skill wraps the [tropes.fyi](https://tropes.fyi) catalogue by [ossama.is](https://ossama.is)
— a list of patterns that mark text as AI-generated. The full catalogue is in
[tropes.md](tropes.md) in this skill's directory. **Read it before writing or editing prose.**

## How to apply

1. **While drafting** — treat the catalogue as constraints, not post-processing. The worst
   offenders to suppress from the first sentence:
   - Negative parallelism ("It's not X — it's Y") and all its variants — the single most
     recognised AI tell
   - The delve-family vocabulary (delve, leverage, robust, harness, tapestry, landscape)
   - "Serves as" / "stands as" where "is" would do
   - Self-posed questions ("The result? Devastating.")
   - Rule-of-three lists used as rhythm rather than content
2. **After drafting** — do one explicit lint pass against `tropes.md`. Read each section
   heading and scan the draft for that pattern. Rewrite hits; don't just delete them —
   the underlying point usually deserves a plainer sentence.
3. **When editing someone else's text** — flag tropes with the pattern name from the
   catalogue so the author learns the vocabulary, and propose a rewrite.

## Calibration

- The goal is prose that reads like a competent human wrote it, not prose that is
  aggressively plain. One rhetorical flourish in a piece can land; the tropes become tells
  through *density and repetition*. Fix the frequency, not every single instance.
- Don't over-correct into blandness or choppiness. If removing a pattern makes the sentence
  worse and no alternative reads naturally, keep the original.
- Some contexts legitimately use flagged vocabulary (e.g. "robust" in a statistics paper,
  "framework" for an actual software framework). The catalogue targets decorative use,
  not technical meaning.

## Keeping the catalogue current

`tropes.md` is a snapshot of the [source gist](https://gist.github.com/ossa-ma/f3baa9d25154c33095e22272c631f5a1)
(fetched July 2026). Refresh occasionally:

```bash
curl -sL "https://gist.githubusercontent.com/ossa-ma/f3baa9d25154c33095e22272c631f5a1/raw" -o tropes.md
```
