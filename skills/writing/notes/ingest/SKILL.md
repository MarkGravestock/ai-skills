---
name: ingest
description: Ingest an external source — a URL, article, document, or PDF — into the notes directory. Triggered when the user shares a source and says /ingest, "ingest this", "file this", "add this to my notes", or similar.
---

# ingest

Triggered by `/ingest <url-or-path>`, "add this article to my notes", "file this doc", or similar.

Notes root: `~/notes`.

## What this skill does

1. Reads the source: fetch the URL (or read the file/PDF directly).
2. Saves an immutable raw copy to `~/notes/raw/YYYY-MM-DD-[slug].md` with frontmatter recording `type: source`, `title:`, `resource:` (the original URL or path — the canonical URI of the asset), `retrieved:` (date), and `generated: { by: [actor], at: [ISO 8601 datetime] }`. Never edit files in `raw/` afterwards.
3. Discusses key takeaways with the user briefly — what matters here, what to emphasise — unless they asked for silent filing.
4. Reads `~/notes/index.md` and identifies every topic page the source touches.
5. Integrates into those pages (see "Integration rules"). One source may touch several pages.
6. Updates `~/notes/todos.md` if the source spawns actions.
7. Rebuilds the index: `python3 ~/notes/tools/notes_tools.py index`.
8. Confirms exactly what was written and where.

## Integration rules

- **Dissolve, don't mirror.** Fold the source's facts into existing topic pages. Do NOT create a per-source summary page by default — a page that restates one source is worth less than the raw copy that already exists.
- **New page only if it passes all four gates** (adapted from the OKF web-ingestion agent):
  1. **Topic shape** — it defines something referenceable by name (a tool, technique, decision, entity), not a grab-bag of notes.
  2. **Not meta** — never mint a page for overview, introduction, getting-started, tutorial, FAQ, changelog, or landing-page content; that material dissolves into existing pages or is skipped.
  3. **Citation test** — you can write a concrete sentence in another page: "See [X](x.md) for …" where X is a proper noun. "See the overview for context" fails.
  4. **Reuse test** — at least two existing pages would link to it, or one page needs it as load-bearing background that doesn't fit inline.

  When in doubt, dissolve. A vault with few pages is fine; a vault of overview stubs is noise.
- **No orphans.** Every page the ingest creates must be linked from at least one existing page in the same session; an unlinked new page means the integration isn't finished.
- **Augment, don't shrink.** When revising an existing page: merge `tags` (union of old and new), merge `sources` (union — never drop an existing entry), and keep existing citations attached to the claims they support. Prose may be revised freely per the update-in-place rule, but provenance only grows.
- **Only record what you actually read.** A `sources` entry (and its raw copy) must correspond to a URL or file you fetched this session — never cite a link you merely saw mentioned.
- **Cite as you integrate** ([OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) `sources` + footnotes). Add the source to the topic page's frontmatter:

  ```yaml
  sources:
    - id: 2026-07-04-slug
      resource: ../raw/2026-07-04-slug.md
      title: [Source title]
  ```

  Then cite each claim with a footnote keyed to that id: `Claim taken from the source.[^2026-07-04-slug]`, with the definition at the end of the page: `[^2026-07-04-slug]: [Source title]`. The footnote label must match a `sources[].id`; the original URL lives in the raw copy's own `resource:` field, so don't repeat it inline.
- **Contradictions**: if the source contradicts an existing claim, revise the page to what you now believe true, citing the new source. If it's genuinely unresolved, state both claims with both footnotes and flag it in the confirmation to the user.
- Update-vs-create and formatting rules are as in the session-wrap skill — same frontmatter, same TL;DR rules, TODOs only in todos.md.
- **Follow-on sources**: if the source leans on one clearly load-bearing in-domain link (a spec it implements, a doc it summarises), offer to ingest that too — but never crawl silently; each fetch is a user decision.
- Prose style: follow `writing-style.md` (alongside this skill). Summarise in plain declarative sentences; never import the source's own rhetoric.
