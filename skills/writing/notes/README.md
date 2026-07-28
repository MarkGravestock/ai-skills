# ai-skills

Source of truth for personal agent skills, synced to Claude Code and Tabnine. Currently: a session-notes system — write path (`session-wrap`), external-source ingest (`ingest`), health check (`notes-lint`), and a deterministic index/link script (`tools/notes_tools.py`). Based on the [llm-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Install / sync

```bash
./sync.sh          # copy skills to ~/.claude/skills and ~/.tabnine/agent/skills,
                   # and tools/notes_tools.py to ~/notes/tools
./sync.sh link     # symlink instead — edits in this repo apply live
```

Override targets via `CLAUDE_SKILLS_DIR`, `TABNINE_SKILLS_DIR`, `NOTES_ROOT`. Re-run after any skill edit (copy mode). Keep this directory in git.

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
- Commit after wraps (`git add -A && git commit`) — history is your chronological log and your undo.

Note: on Tabnine, typed `/wrap`-style commands need a one-line command file in `.tabnine/agent/commands/`; the natural-language triggers ("wrap up", "ingest this") work without it.

## Format compatibility

The notes format (markdown + YAML frontmatter with a required `type` field) is deliberately [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)-shaped. If the vault ever needs to become a queryable knowledge graph, [Vault-LD Appendix B](https://github.com/The-Knowledge-Graph-Guys/vault-ld/blob/main/SPEC.md) defines the lift: add a root `context.jsonld`, modify no files, promote types and fields incrementally. Deferred deliberately — see the boundary condition: formal semantics pay at multi-author/interop scale, not for a single-author vault with a lint pass.
