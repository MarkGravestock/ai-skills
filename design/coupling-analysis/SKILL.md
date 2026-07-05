---
name: coupling-analysis
description: Stub that delegates to Vlad Khononov's official Modularity plugin. Use when asked to analyse coupling, dependencies, modularity, component boundaries, or code architecture quality using the Balanced Coupling model (integration strength, distance, volatility). Routes to /modularity:review for existing codebases and /modularity:design for new architectures; includes install instructions if the plugin is missing.
---

# Coupling Analysis (stub → Khononov's Modularity plugin)

This skill is superseded by the author's own Claude Code plugin:
**[vladikk/modularity](https://github.com/vladikk/modularity)** — Vlad Khononov's official
implementation of the Balanced Coupling model from *Balancing Coupling in Software Design*.

## What to do when this skill triggers

1. **If the Modularity plugin's skills are available in this session, use them and stop here:**
   - `/modularity:review` — analyse an existing codebase for coupling imbalances and
     knowledge leakage across component boundaries
   - `/modularity:design` — design a modular architecture from functional requirements,
     producing module design docs with integration contracts and test specifications

2. **If they are not available**, tell the user to install the plugin (Claude Code v1.0.33+):

   ```
   /plugin marketplace add vladikk/modularity
   /plugin install modularity@vladikk-modularity
   ```

   Or clone and load directly: `claude --plugin-dir ./modularity` after
   `git clone https://github.com/vladikk/modularity`.

3. **Only if the plugin cannot be installed**, fall back on the model summary below —
   it is deliberately minimal; the plugin is the real implementation.

## Fallback: the Balanced Coupling model in brief

Coupling is evaluated across three dimensions:

- **Integration strength** — how much knowledge is shared across the boundary, from
  weakest to strongest: contract → model → functional → intrusive.
- **Distance** — how far apart the coupled components are (same class → package →
  module → service → organisation). Shared knowledge costs more over greater distance.
- **Volatility** — how often the shared knowledge changes. Stable knowledge neutralises
  otherwise-costly coupling.

**Balance rule:** coupling is balanced when strength and distance counterbalance each other
(strong coupling only over short distances, only weak contracts over long distances), or when
volatility is low enough to neutralise the imbalance. Pain = strength × distance × volatility.

## Composes with

- `cupid-properties` — coupling analysis pairs with the Composable and Domain-based
  properties at the component/system altitude
- `simple-design` — rule 3 (no duplication) between components: duplicated knowledge *is*
  coupling, whatever the imports say
