---
name: ingest
description: Ingest an external source — a URL, article, document, or PDF — into the notes directory. Triggered when the user shares a source and says /ingest, "ingest this", "file this", "add this to my notes", or similar.
---

# ingest

Triggered by `/ingest <url-or-path>`, "add this article to my notes", "file this doc", or similar.

Notes root: `~/notes`.

## What this skill does

1. Reads the source: fetch the URL (or read the file/PDF directly).
2. Saves an immutable raw copy to `~/notes/raw/YYYY-MM-DD-[slug].md` with frontmatter recording `type: source`, `source:` (URL or original path), and `retrieved:` (date). Never edit files in `raw/` afterwards.
3. Discusses key takeaways with the user briefly — what matters here, what to emphasise — unless they asked for silent filing.
4. Reads `~/notes/index.md` and identifies every topic page the source touches.
5. Integrates into those pages (see "Integration rules"). One source may touch several pages.
6. Updates `~/notes/todos.md` if the source spawns actions.
7. Rebuilds the index: `python3 ~/notes/tools/notes_tools.py index`.
8. Confirms exactly what was written and where.

## Integration rules

- **Dissolve, don't mirror.** Fold the source's facts into existing topic pages. Do NOT create a per-source summary page by default — a page that restates one source is worth less than the raw copy that already exists.
- **Per-source page only when it earns it**: the source is dense enough that 3+ topic pages would each need long extracts from it. Then a source page compressing it once, linked from those pages, is cheaper.
- **Cite as you integrate.** Claims taken from the source get a citation: `([Title](../raw/2026-07-04-slug.md), [original](https://...))`.
- **Contradictions**: if the source contradicts an existing claim, revise the page to what you now believe true, citing the new source. If it's genuinely unresolved, state both claims with both citations and flag it in the confirmation to the user.
- Update-vs-create and formatting rules are as in the session-wrap skill — same frontmatter, same TL;DR rules, TODOs only in todos.md.
- Prose style: follow `writing-style.md` (alongside this skill). Summarise in plain declarative sentences; never import the source's own rhetoric.
