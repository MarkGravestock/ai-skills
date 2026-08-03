---
name: session-wrap
description: End-of-session notes writer. Captures findings, decisions, and open questions from any conversation into a structured notes directory. Triggered when the user types /wrap or asks to wrap up, close out, or save session notes.
---

# session-wrap

Triggered by `/wrap`, "wrap up", "save session notes", or similar closing intent.

Notes root: `~/notes` (adjust here if you keep notes elsewhere).

## What this skill does

1. Reviews the conversation history for findings, discoveries, decisions, and open questions.
2. Reads `~/notes/index.md` to see existing areas and pages, then decides whether to update an existing page or create a new one (see "Update or create").
3. Writes or revises the notes file with a structured summary following the standard format.
4. Updates `~/notes/todos.md` with any new TODOs or completed items.
5. Rebuilds the index: `python3 ~/notes/tools/notes_tools.py index`.
6. Confirms to the user exactly what was written and where.

## Update or create

- **Update in place** when the session adds to, corrects, or supersedes a topic that already has a page. Revise the page so it reads true today — do not append contradictory history. If something previously written is now wrong, replace it; git history preserves the old claim.
- **New page** only for a distinct topic you would link to from other pages. Filename: kebab-case, singular.
- **New subdirectory** only when a note fits no area listed in the index. Name it after the domain area (kebab-case), not the session.

## Notes format (mandatory)

Every notes file must follow this structure:

```markdown
---
type: topic
title: [Human-readable title — same as the H1]
description: [one sentence — what this page covers; shown in the index]
tags: [comma-separated, keywords, for, discoverability]
when-to-load: [one sentence — when should a future agent load this file?]
generated: { by: [actor], at: [ISO 8601 datetime] }
---

# [Title]

## TL;DR

- [Key fact 1]
- [Key fact 2]
- [Key fact 3 — link to todos.md if TODOs exist]

---

## [Main content sections]

...

## TODOs

[Do NOT put TODOs here — reference todos.md instead]
> See [../todos.md](../todos.md)
```

**Rules:**

- TL;DR bullets must be self-contained — a future agent reading only the TL;DR should know whether to load the full file.
- `when-to-load` is the primary filter for relevance — write it as a trigger condition, not a description. `description` says what the page is; `when-to-load` says when to read it.
- `generated.by` follows the [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) actor convention: `claude-code/<model-id>` when this skill writes the page, `human:<id>` for hand-authored content. Update `generated` (both fields) on every meaningful revision.
- Optional lifecycle keys, only when they apply: `status: draft | stable | deprecated` (absent means stable) and `stale_after: YYYY-MM-DD` for content with a known expiry (version-pinned findings, time-boxed decisions).
- Do not duplicate TODOs in the notes file — they live only in `todos.md`.
- Cross-links use relative paths and only point at pages that exist. One link per page mention per section is enough; never link from headings or inside code blocks.
- Prose style: follow `writing-style.md` (alongside this skill). Plain declarative sentences, specific facts, no AI rhetoric. Structural elements (frontmatter, TL;DR headings, keyed todo bullets) are exempt.

## todos.md format

File: `~/notes/todos.md`

The file starts with minimal frontmatter (`type: todo-list` between `---` lines) so every non-reserved file in the vault is a valid OKF concept — add it if missing.

Each new TODO entry:

```markdown
- [ ] [YYYY-MM-DD] **[Short title]** — [description]. See [notes-file.md#section](path/to/notes-file.md).
```

Move completed items to the `## Completed` section with `[x]` and completion date.

## Routing

There is no fixed directory map. The `##` headings in `index.md` are the current areas — route to the best match, and only create a new area when nothing fits. The index is generated, so new areas appear in it automatically on the next rebuild.
