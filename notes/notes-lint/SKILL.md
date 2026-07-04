---
name: notes-lint
description: Health check for the notes directory. Triggered when the user types /lint-notes or asks to check, tidy, or health-check their notes. Flags problems; never deletes.
---

# notes-lint

Triggered by `/lint-notes`, "check my notes", "lint the notes", or similar. Run occasionally (monthly, or when the notes feel untrustworthy) — not on every session.

Notes root: `~/notes`.

## Checks (run in order)

### 1. Deterministic checks first

Run `python3 ~/notes/tools/notes_tools.py check`. This reports broken internal links and anchors, missing frontmatter fields, and a stale index. Include its output in the report; fix anything it flags where the correct fix is unambiguous (e.g. a heading was renamed — repoint the anchor).

### 2. TODO rot

Read `todos.md`. Flag open items older than 30 days. For each: still relevant, superseded, or quietly done? Propose a disposition but do not move or delete without approval.

### 3. TL;DR drift

For pages modified since the last lint, check the TL;DR still matches the body. A page edited three times often has a TL;DR describing version one. Rewrite where clearly stale.

### 4. Contradictions and stale claims

Scan pages within each area for claims that newer pages (or newer sections) contradict or supersede. Flag each pair; propose which page to revise. Do not revise unilaterally.

### 5. Near-duplicates

Look for pages in the same area covering the same topic under different names. List suspected pairs. Do NOT merge or delete — flag for approval.

### 6. Promotion candidates

Note topics mentioned across 3+ pages that lack their own page — suggest creating one at the next `/wrap` that touches the topic.

### 7. Style pass

Sample recently modified pages against `writing-style.md` (alongside this skill). Flag prose that pads without informing — filler transitions, unattributed claims, restated facts, rhetorical framing. Rewrite only where the fix is a deletion or a direct restatement; otherwise propose.

## Output

A short markdown report in chat: one-line health status (🟢/🟡/🔴), findings per check, then a numbered list of proposed actions marking which need approval.

## Hard rules

- **Never delete or merge files unilaterally.** Flag; act only on explicit approval.
- Content revisions (checks 3–4) may be applied only where the correct fix is unambiguous; otherwise propose.
- Finish by rebuilding the index: `python3 ~/notes/tools/notes_tools.py index`.
