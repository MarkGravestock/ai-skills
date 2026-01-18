---
name: software-design-principles
description: Use when reviewing code design, refactoring, or requested to improve code quality - covers object calisthenics, single level of abstraction, composed method pattern, dependency inversion, fail-fast error handling, feature envy detection, intention-revealing naming, and tell-don't-ask principle
---

# Software Design Principles

Language-agnostic OO design principles. Examples use modern Java; adapt to your language.

**ATTRIBUTION:** Core principles adapted from NTCoding's software-design-principles skill (https://github.com/NTCoding/claude-skillz/blob/main/software-design-principles). Extended with Tell-Don't-Ask, SLAP, and Composed Method.

## Critical Rules

Apply during all code reviews:

1. **Fail-fast** – Reject fallback chains. Validate and throw descriptive errors: "Expected [X]. Got [Y]. Context: [info]"
2. **Type-safety** – Eliminate unsafe casts, raw types, suppressed warnings
3. **Illegal states unrepresentable** – Use sealed types/discriminated unions
4. **Dependency injection** – Never instantiate dependencies inside methods
5. **Intention-revealing names** – Ban generic terms: `data`, `utils`, `helpers`, `handler`, `processor`
6. **Tell, don't ask** – Push behavior into objects where data lives
7. **No comments** – Refactor for clarity instead
8. **Validation at boundaries** – Use validation libraries for external data

## Object Calisthenics (9 Rules)

| Rule | Principle | Red Flag |
|------|-----------|----------|
| 1 | One indentation level per method (max 3) | Nested loops/conditionals |
| 2 | No else keyword | `if-else` chains |
| 3 | Wrap primitives/strings | Primitive parameters without domain meaning |
| 4 | First-class collections | Classes mixing collection with other fields |
| 5 | One dot per line | `order.getCustomer().getAddress().getCity()` |
| 6 | No abbreviations | `usrMgr`, `qty`, `ctx` |
| 7 | Keep small | Methods >10 lines, classes >150 lines |
| 8 | Avoid getters/setters | Getters followed by conditionals |

## Method Design

**Single Level of Abstraction (SLAP):** All statements at same conceptual level. Don't mix high-level logic with low-level details in one method.

**Composed Method:** Extract comment sections into well-named methods. Comments = method extraction opportunity.

```java
// ❌ Mixed abstractions + comment sections
void processOrder(Order order) {
    // Validate
    if (!order.isValid()) throw new InvalidOrderException();

    // Save (low-level JDBC mixed with business logic)
    var conn = DriverManager.getConnection(DB_URL);
    var stmt = conn.prepareStatement("INSERT...");
    stmt.setString(1, order.id());
    stmt.executeUpdate();

    // Notify
    emailService.send(order.customerEmail(), "Confirmed");
}

// ✅ Single abstraction + composed methods
void processOrder(Order order) {
    validateOrder(order);
    saveOrder(order);
    notifyCustomer(order);
}
```

## Core Patterns

**Feature Envy:** Method uses another class's data more than its own → move logic to envied class

**Tell-Don't-Ask:** Don't extract data to make decisions. Push decisions into objects.

```java
// ❌ Ask-then-tell
if (account.balance().isGreaterThan(amount) &&
    account.status().equals("active")) {
    account.deduct(amount);
}

// ✅ Tell-don't-ask
account.withdraw(amount); // Object decides internally
```

**When getters acceptable:**
- Display/serialization only
- DDD value objects WITH behavior (not just accessors)

**Value objects:** Encapsulate operations, not just expose data.

```java
// ❌ Anemic
record Money(BigDecimal amount, String currency) {}
if (price.amount().compareTo(threshold) > 0) { ... }

// ✅ Rich behavior
record Money(BigDecimal amount, String currency) {
    boolean isGreaterThan(Money other) { ... }
    Money add(Money other) { ... }
}
if (price.isGreaterThan(threshold)) { ... }
```

**Dependency Inversion:** Inject via constructor, never `new X()` inside methods.

**Type-Driven Design:** Use sealed types to make illegal states unrepresentable. Pattern matching for exhaustive handling.

**Immutability:** Prefer `final` fields, immutable collections (`List.of()`, `List.copyOf()`), return new values vs mutation.

**YAGNI:** Build only what's required now. "We might need it" is not a requirement.

## Quick Reference

**Naming forbidden:** `data`, `utils`, `helpers`, `common`, `shared`, `manager`, `handler`, `processor`

**Refactoring triggers:**
- Comments explaining sections → extract methods
- Getters followed by conditionals → push logic into object
- Mixed abstraction levels → extract single-level methods
- Long methods (>10 lines) → apply composed method
- `new X()` in methods → inject via constructor
- Fallback chains → fail-fast with context

## Code Review Checklist

**Encapsulation:**
- [ ] Behavior with data? Tell-don't-ask applied?
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
- [ ] No generic names?
- [ ] Domain vocabulary used?

**Immutability:**
- [ ] Return new values vs mutation?
- [ ] Final fields preferred?
