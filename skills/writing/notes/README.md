# ai-skills

Source of truth for personal agent skills, synced to Claude Code and Tabnine. Currently: a session-notes system — write path (`session-wrap`), external-source ingest (`ingest`), health check (`notes-lint`), and a deterministic index/link script (`tools/notes_tools.py`). Based on the [llm-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Install / sync

```bash
uv run poe sync -- writing/notes       # copy just the notes skills,
                                        # and tools/notes_tools.py to ~/notes/tools
uv run poe sync-link -- writing/notes  # symlink instead — edits in this repo apply live

python sync.py copy writing/notes   # same, without uv/poe (stdlib only)
```

Run from the repo root (or omit the subdir to install everything — see the root
[ReadMe.md](../../../ReadMe.md#install--sync)). Override targets via `CLAUDE_SKILLS_DIR`,
`TABNINE_SKILLS_DIR`, `NOTES_ROOT`. Re-run after any skill edit (copy mode). Keep this
directory in git.

```bash
cd ~/notes && git init && git add -A && git commit -m "init"
```

## Read path (required)

The wrap skill is write-only memory without this. Add to `~/.claude/CLAUDE.md` **and** your `TABNINE.md`/guidelines:

```markdown
## Notes
Personal notes live in ~/notes. Before starting a task, read ~/notes/index.md
and load any file whose "load when" condition matches the task at hand.
Load nothing that doesn't match.
```

## Day to day

- End of session: `/wrap` — files the session into topic pages, updates todos.md, rebuilds the index.
- Found an article/doc worth keeping: `/ingest <url-or-path>` — raw copy to `raw/` (immutable, excluded from index), facts dissolved into topic pages with citations.
- Monthly-ish: `/lint-notes` — flags rot, drift, duplicates, broken links. Flags only; never deletes.
- To see the vault as a graph: `python3 ~/notes/tools/notes_tools.py viz` writes `~/notes/viz.html` — an interactive page/link graph (nodes coloured by area, click for the rendered page, search and area filters). Open it in a browser; it loads cytoscape.js and marked from a CDN, mirroring the OKF reference viewer.
- Commit after wraps (`git add -A && git commit`) — history is your chronological log and your undo.

Note: on Tabnine, typed `/wrap`-style commands need a one-line command file in `.tabnine/agent/commands/`; the natural-language triggers ("wrap up", "ingest this") work without it.

## Format compatibility

The vault is a conformant [OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle:

- Every non-reserved `.md` file carries YAML frontmatter with a `type` (`topic`, `source`, `todo-list`); `title`, `description`, and `tags` follow the spec's recommended keys.
- The generated root `index.md` declares `okf_version: "0.2"` and lists `[Title](path) - description` entries grouped by area.
- Provenance uses the `sources` family plus footnote citations keyed to `sources[].id`; content origin is stamped as `generated: { by, at }` with the actor convention (`claude-code/<model>`, `human:<id>`).
- Lifecycle keys `status` and `stale_after` are honoured by the lint pass.

Deliberate divergences, all legal under OKF's tolerate-unknown-keys rule: `when-to-load` and `retrieved` are extension keys; `raw/` plays the role of the spec's `references/` convention but is excluded from the index (raw mirrors are provenance, not concepts to load); there is no `log.md` — git history is the chronological log.

**Migrating an existing vault**: `/lint-notes` (or `notes_tools.py check`) flags the pre-OKF keys — `scope` (drop), `topics` (→ `tags`), `source` (→ `resource`) — and pages missing `description`. The renames are mechanical; write `description` lines as you next touch each page.

If the vault ever needs to become a queryable knowledge graph, [Vault-LD Appendix B](https://github.com/The-Knowledge-Graph-Guys/vault-ld/blob/main/SPEC.md) defines the lift: add a root `context.jsonld`, modify no files, promote types and fields incrementally. Deferred deliberately — see the boundary condition: formal semantics pay at multi-author/interop scale, not for a single-author vault with a lint pass.
