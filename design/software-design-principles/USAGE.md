# Software Design Principles Skill - Usage Guide

## Quick Start

This skill automatically activates during code reviews and refactoring. You can also invoke it explicitly:

```
"Review this code using software-design-principles"
"Check for tell-don't-ask violations"
"Apply object calisthenics to this class"
"Check for SLAP violations in this method"
```

## What This Skill Does

Provides systematic code review based on:
- **8 Critical Rules** (fail-fast, type-safety, dependency injection, tell-don't-ask, etc.)
- **9 Object Calisthenics Rules** (indentation, no else, wrap primitives, etc.)
- **Method Design Principles** (SLAP, Composed Method)
- **Core Patterns** (Feature Envy, Value Objects, Type-Driven Design, YAGNI)

## Structure

### Active Skill (Loaded by Agents)
- **SKILL.md** (726 words) - Compressed reference with checklists and quick lookup tables
- Optimized for context efficiency
- Scannable format (tables, bullets)

### Reference Documentation (For Humans)
- **README.md** (3,259 words) - Comprehensive guide with detailed examples
- Use for onboarding, training, deep understanding
- Full explanations of each principle

### Testing Artifacts
- **test-scenarios.md** - Test cases used to validate skill
- **test-results-RED-phase.md** - Baseline agent behavior without skill
- **test-results-COMPARISON.md** - Detailed RED vs GREEN analysis

## Value Proposition

The skill doesn't teach NEW principles (modern Claude models already know them).

**The skill provides:**
1. **Systematic application** - Checklist-driven reviews
2. **Consistent terminology** - Always "SLAP", "Tell-Don't-Ask", "Feature Envy"
3. **Structured output** - Tables and violation summaries
4. **Explicit rule references** - "Critical Rule #6", "Object Calisthenics Rule #9"
5. **Team alignment** - Shared vocabulary and documented standards

## When to Use

**Auto-activates:**
- Code refactoring sessions
- Design reviews
- Architecture discussions

**Explicit triggers:**
- "Review this code's design"
- "Check for feature envy"
- "Apply object calisthenics"
- "Improve naming in this file"
- "Check for tell-don't-ask violations"
- "Apply single level of abstraction"
- "Extract methods from comments"

## Code Review Checklist

The skill applies this systematic checklist:

**Encapsulation:**
- [ ] Behavior located with data?
- [ ] Tell-don't-ask applied?
- [ ] Getters only for queries, not decisions?

**Dependencies:**
- [ ] Constructor injection only?
- [ ] No `new X()` in methods?

**Error Handling:**
- [ ] Fail-fast with context?
- [ ] No silent fallbacks?

**Types:**
- [ ] No raw types/unchecked casts?
- [ ] Illegal states unrepresentable?

**Method Design:**
- [ ] Single abstraction level per method?
- [ ] Comments replaced with method names?
- [ ] Methods <10 lines?

**Naming:**
- [ ] No generic names (data, utils, handler, manager)?
- [ ] Domain vocabulary used?

**Immutability:**
- [ ] Return new values vs mutation?
- [ ] Final fields preferred?

## Critical Rules Reference

1. **Fail-fast** – Reject fallback chains. Validate and throw descriptive errors
2. **Type-safety** – Eliminate unsafe casts, raw types, suppressed warnings
3. **Illegal states unrepresentable** – Use sealed types/discriminated unions
4. **Dependency injection** – Never instantiate dependencies inside methods
5. **Intention-revealing names** – Ban generic terms: data, utils, helpers, handler, processor
6. **Tell, don't ask** – Push behavior into objects where data lives
7. **No comments** – Refactor for clarity instead
8. **Validation at boundaries** – Use validation libraries for external data

## Object Calisthenics Quick Reference

| Rule | Red Flag |
|------|----------|
| 1. One indentation level | Nested loops/conditionals |
| 2. No else keyword | if-else chains |
| 3. Wrap primitives | Primitive parameters without domain meaning |
| 4. First-class collections | Classes mixing collection with other fields |
| 5. One dot per line | `order.getCustomer().getAddress().getCity()` |
| 6. No abbreviations | usrMgr, qty, ctx |
| 7. Keep small | Methods >10 lines, classes >150 lines |
| 8. Avoid getters/setters | Getters followed by conditionals |

## Examples

### Tell-Don't-Ask Pattern

```java
// ❌ Ask-then-tell
if (account.balance().isGreaterThan(amount) &&
    account.status().equals("active")) {
    account.deduct(amount);
}

// ✅ Tell-don't-ask
account.withdraw(amount); // Object decides internally
```

### SLAP (Single Level of Abstraction)

```java
// ❌ Mixed abstractions
void processOrder(Order order) {
    if (!order.isValid()) throw new InvalidOrderException();
    var conn = DriverManager.getConnection(DB_URL); // Low-level
    var stmt = conn.prepareStatement("INSERT...");
    emailService.send(order.customerEmail(), "Confirmed");
}

// ✅ Single abstraction
void processOrder(Order order) {
    validateOrder(order);
    saveOrder(order);
    notifyCustomer(order);
}
```

### Composed Method

```java
// ❌ Comments as section markers
void checkout(Cart cart) {
    // Validate cart items
    for (var item : cart.getItems()) { ... }

    // Calculate total with tax
    var total = ...;

    // Process payment
    paymentGateway.charge(...);
}

// ✅ Comments extracted to methods
void checkout(Cart cart) {
    validateCartItems(cart);
    Money total = calculateTotalWithTax(cart);
    processPayment(total);
}
```

## Attribution

Core principles adapted from NTCoding's software-design-principles skill:
https://github.com/NTCoding/claude-skillz/blob/main/software-design-principles

Extended with:
- Tell-Don't-Ask principle with DDD value objects
- Single Level of Abstraction Principle (SLAP)
- Composed Method pattern
- Systematic Code Review Checklist
- Modern Java examples (records, sealed types, pattern matching)

## Version

1.0.0 - Initial release with comprehensive testing
