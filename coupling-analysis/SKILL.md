---
name: coupling-analysis
description: Analyse codebase coupling using Vlad Khononov's framework from "Balancing Coupling in Software Design". Use when asked to analyse coupling, dependencies, modularity, component boundaries, or code architecture quality. Identifies integration strength, distance, and volatility issues. Works with Java/Spring, TypeScript, Python, and other codebases.
---

# Coupling Analysis (Khononov Framework)

Analyse codebases using Vlad Khononov's three-dimensional coupling model: **Strength**, **Distance**, and **Volatility**.

## Quick Reference

See `references/khononov-framework.md` for detailed definitions of coupling types and the full theoretical framework.

## Analysis Workflow

### 1. Initial Discovery

```bash
# Get project structure overview
find . -type f \( -name "*.java" -o -name "*.kt" -o -name "*.ts" -o -name "*.py" \) | head -100

# For Java/Spring projects - find module boundaries
find . -name "pom.xml" -o -name "build.gradle*" | head -20

# Find package structure
find . -type d -name "src" -exec find {} -type d \; | grep -E "(domain|service|controller|repository|adapter|port|infrastructure)" | head -30
```

### 2. Analyse Integration Strength

Examine imports and dependencies to classify coupling strength (from loosest to tightest):

| Level | Type | Indicator | Risk |
|-------|------|-----------|------|
| 1 | Signature | Primitive types only | Low |
| 2 | Contract | Interfaces, DTOs | Low |
| 3 | Model | Shared domain objects | Medium |
| 4 | Functional | Behaviour dependencies | High |
| 5 | Intrusive | Internal access, reflection | Critical |

**Java patterns to search:**
```bash
# Intrusive coupling - reflection, internal access
grep -rn "\.class\b" --include="*.java" | grep -v "test"
grep -rn "getDeclaredField\|getDeclaredMethod\|setAccessible" --include="*.java"

# Model coupling - shared entities across packages
grep -rn "^import.*\.domain\.\|^import.*\.model\.\|^import.*\.entity\." --include="*.java" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20

# Contract coupling - interface usage
grep -rn "^import.*\.api\.\|^import.*\.contract\.\|^import.*\.dto\." --include="*.java"
```

### 3. Analyse Distance

Distance = how far apart components are architecturally. Coupling across boundaries is costlier.

**Boundary types (increasing distance):**
1. Same module/package
2. Same bounded context
3. Different bounded contexts (same system)
4. Different systems/services

**Detection patterns:**
```bash
# Cross-module dependencies (multi-module projects)
for pom in $(find . -name "pom.xml" -not -path "*/target/*"); do
  echo "=== $pom ===" 
  grep -A2 "<dependency>" "$pom" | grep -E "<(groupId|artifactId)>" | head -20
done

# Package dependency direction (should flow inward to domain)
grep -rn "^import" --include="*.java" | \
  grep -E "(infrastructure|adapter).*import.*(domain|core)" 

# Database access from wrong layers
grep -rn "@Repository\|@Entity\|JpaRepository" --include="*.java" | grep -v repository
```

### 4. Analyse Volatility

Volatility = how often the coupled component changes. Coupling to volatile components is riskier.

**Use git history:**
```bash
# Most frequently changed files (high volatility)
git log --pretty=format: --name-only --since="6 months ago" | \
  grep -E "\.(java|kt|ts|py)$" | sort | uniq -c | sort -rn | head -30

# Files that change together (temporal coupling)
git log --pretty=format:"%h" --since="6 months ago" | while read commit; do
  git show --name-only --pretty=format: "$commit" | grep -E "\.(java|kt)$" | sort
  echo "---"
done | head -200

# Churn rate by package
git log --pretty=format: --name-only --since="6 months ago" | \
  grep -E "\.java$" | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -20
```

### 5. Identify Anti-Patterns

**Circular dependencies:**
```bash
# Use scripts/detect-cycles.py for comprehensive cycle detection
python3 scripts/detect-cycles.py --path . --lang java
```

**God classes (high afferent coupling):**
```bash
# Classes imported by many others
grep -rhn "^import" --include="*.java" | \
  sed 's/.*import \(static \)\?//' | sed 's/;.*//' | \
  sort | uniq -c | sort -rn | head -20
```

**Feature envy:**
```bash
# Classes calling many methods on other objects
grep -rn "\.[a-z][a-zA-Z]*\.[a-z][a-zA-Z]*(" --include="*.java" | \
  awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -20
```

### 6. Generate Report

Structure findings as:

```markdown
## Coupling Analysis Report

### Executive Summary
- Overall coupling health: [Good/Moderate/Concerning/Critical]
- Key risks identified: [count]
- Recommended priority actions: [list top 3]

### Findings by Dimension

#### Integration Strength Issues
[List intrusive/functional coupling violations]

#### Distance Violations  
[List cross-boundary coupling, especially infrastructure→domain]

#### Volatility Risks
[List stable components coupled to volatile ones]

### Recommendations
[Prioritised list with effort/impact assessment]
```

## Language-Specific Guides

- **Java/Spring**: Primary focus. Use package structure and Spring stereotypes.
- **TypeScript**: Analyse barrel exports, module boundaries, package.json workspaces.
- **Python**: Check `__init__.py` exports, relative vs absolute imports.

## Key Principles

1. **Coupling is not inherently bad** — it's about coupling the right things appropriately
2. **Minimise coupling across boundaries** — especially bounded context boundaries
3. **Couple to stable abstractions** — interfaces and contracts, not implementations
4. **Direction matters** — dependencies should point toward stability
