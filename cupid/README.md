# CUPID skills

Composable skills for Dan North's [CUPID properties](https://dannorth.net/blog/cupid-for-joyful-coding/):
a generic, language-agnostic core plus stack-specific implementation skills that layer on
top of it.

```
cupid/
├── properties/        cupid-properties       — the five properties, scorecard, review lens
├── python/            cupid-python           — practical Python implementation advice
├── java-spring-boot/  cupid-java-spring-boot — practical Java/Spring Boot implementation advice
└── sync.sh            installs to Claude Code and Tabnine
```

## Composition model

- `properties/` owns the definitions and judgment criteria: properties vs principles, the
  SOLID critique, the caller-combination test, the 0–3 scorecard, the review lens.
- Each stack skill owns only idioms, libraries, and code patterns for its technology, and
  declares in its frontmatter description that it composes with `cupid-properties`.
- `sync.sh` copies `properties/SKILL.md` into each stack skill dir as `cupid-properties.md`,
  so a stack skill can load the generic guidance even when the installed skill only sees its
  own directory.

Adding a new stack (e.g. TypeScript): create `typescript/SKILL.md` following the pattern of
an existing stack skill, add `typescript` to the `SKILLS` array in `sync.sh`, and leave
`properties/` untouched.

## Install / sync

```bash
./sync.sh          # copy skills to ~/.claude/skills and ~/.tabnine/agent/skills
./sync.sh link     # symlink instead — edits in this repo apply live
```

Override targets via `CLAUDE_SKILLS_DIR`, `TABNINE_SKILLS_DIR`. Re-run after any skill edit
(copy mode). Installed skill names are prefixed (`cupid-properties`, `cupid-python`,
`cupid-java-spring-boot`) to stay unique in the flat skills directory.

## Sources

- [CUPID — for joyful coding](https://dannorth.net/blog/cupid-for-joyful-coding/) — Dan North
- [CUPID — the back story](https://dannorth.net/blog/cupid-the-back-story/) — Dan North
- [cupid.dev](https://cupid.dev/)
