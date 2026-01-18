---
name: software-design-principles
description: Use when reviewing code design, refactoring, or requested to improve code quality - covers object calisthenics, single level of abstraction, composed method pattern, dependency inversion, fail-fast error handling, feature envy detection, intention-revealing naming, and tell-don't-ask principle
---

# Software Design Principles - Comprehensive Reference

> **NOTE:** This is the comprehensive reference documentation for human readers and skill maintenance.
> **The active skill loaded by Claude Code is SKILL.md** (726 words - optimized for context efficiency).
> This README provides detailed examples and explanations to support understanding and future extensions.

## Overview

Comprehensive object-oriented design principles for writing maintainable, encapsulated code. Combines foundational OO practices with domain-driven design techniques.

**Language-agnostic principles with modern Java examples.** Principles apply to any OO language; adapt examples to your language's idioms.

**ATTRIBUTION:** Core principles (Object Calisthenics, Dependency Inversion, Fail-Fast, Feature Envy, Naming, Type-Driven Design, Immutability, YAGNI) adapted from NTCoding's software-design-principles skill (https://github.com/NTCoding/claude-skillz/blob/main/software-design-principles). Extended with Tell-Don't-Ask principle and structured for additional specializations.

## When to Use

**Auto-activates during:**
- Code refactoring
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
- "Apply composed method pattern"

## Critical Rules

Apply these rules during all code reviews and refactoring:

1. **Fail-fast over silent fallbacks** – Reject fallback chains. Validate rigorously and throw descriptive errors when data should exist.

2. **Maximum type-safety** – Eliminate unsafe casts, raw types, and suppressed warnings. The type system always provides a safer path forward.

3. **Unrepresentable illegal states** – Use sealed types/discriminated unions instead of optional fields. Prevent impossible state combinations through types.

4. **Dependency injection** – Never instantiate dependencies inside methods. Pass them via constructors for testability and flexibility.

5. **Intention-revealing names** – Banish generic terms (`data`, `utils`, `helpers`, `handler`, `processor`). Use domain-specific vocabulary.

6. **Tell objects what to do** – Don't extract data to make decisions. Push behavior into objects where the data lives.

7. **No code comments** – Comments indicate unclear code. Refactor for clarity instead of explaining what code does.

8. **Validation at boundaries** – Use validation libraries (Bean Validation, Vavr, etc.) for parsing external data, keeping types and validation synchronized.

## Object Calisthenics - Nine Rules

### Rule 1: One indentation level per method
Keep methods flat. Tolerate up to 3 levels in practice, but aim for 1.

### Rule 2: Eliminate ELSE keyword
Use early returns instead:

```java
// ❌ Nested else
String process(String value) {
    if (value != null) {
        return value.toUpperCase();
    } else {
        return "UNKNOWN";
    }
}

// ✅ Early return
String process(String value) {
    if (value == null) return "UNKNOWN";
    return value.toUpperCase();
}
```

### Rule 3: Wrap primitives and strings
Create value objects, encapsulate validation, make domain concepts explicit:

```java
// ❌ Primitive obsession
void createUser(String email) {
    if (!email.contains("@")) {
        throw new IllegalArgumentException("Invalid email");
    }
    // ...
}

// ✅ Value object (Java record)
record Email(String value) {
    Email {
        if (!value.contains("@")) {
            throw new IllegalArgumentException("Invalid email: " + value);
        }
    }

    String domain() {
        return value.split("@")[1];
    }
}

void createUser(Email email) {
    // Email is already validated
}
```

### Rule 4: First-class collections
Classes housing collections contain nothing else:

```java
// ❌ Mixed responsibilities
class Order {
    private List<Item> items;
    private Customer customer;
    private BigDecimal total;

    void addItem(Item item) { items.add(item); }
    int getItemCount() { return items.size(); }
}

// ✅ First-class collection
class OrderItems {
    private final List<Item> items;

    OrderItems(List<Item> items) {
        this.items = List.copyOf(items);
    }

    OrderItems add(Item item) {
        var newItems = new ArrayList<>(items);
        newItems.add(item);
        return new OrderItems(newItems);
    }

    int count() {
        return items.size();
    }

    Money total() {
        return items.stream()
            .map(Item::price)
            .reduce(Money.zero(), Money::add);
    }
}

class Order {
    private final OrderItems items;
    private final Customer customer;

    Order(OrderItems items, Customer customer) {
        this.items = items;
        this.customer = customer;
    }
}
```

### Rule 5: One dot per line
Limit method chaining to prevent Law of Demeter violations:

```java
// ❌ Multiple dots (train wreck)
order.getCustomer().getAddress().getCity();

// ✅ Tell, don't ask
order.customerCity();
```

### Rule 6: No abbreviations
Use complete, descriptive names:

```java
// ❌ Abbreviations
var usrMgr = new UsrMgr();
var qty = getQty();

// ✅ Full names
var userManager = new UserManager();
var quantity = getQuantity();
```

### Rule 7: Keep entities small
- Classes under 150 lines
- Methods under 10 lines
- Small modules for maintainability

### Rule 8: Avoid getters/setters/properties
Objects perform work; they don't just expose raw data. See Tell-Don't-Ask section below.

## Method Design Principles

### Single Level of Abstraction Principle (SLAP)

**Principle:** All statements in a method should be at the same level of abstraction.

Mixing high-level policy with low-level details makes methods hard to understand. Each method should read like a paragraph at one conceptual level.

**Related to:** Object Calisthenics Rule 1 (single indentation) - indentation often indicates mixed abstraction levels.

```java
// ❌ Mixed abstraction levels
void processOrder(Order order) {
    // High-level business logic
    if (order.isValid()) {
        // Low-level implementation details
        var connection = DriverManager.getConnection(DB_URL);
        var statement = connection.prepareStatement(
            "INSERT INTO orders VALUES (?, ?, ?)"
        );
        statement.setString(1, order.id());
        statement.setString(2, order.customerId());
        statement.setBigDecimal(3, order.total());
        statement.executeUpdate();

        // High-level again
        sendConfirmationEmail(order);
    }
}

// ✅ Single level of abstraction
void processOrder(Order order) {
    validateOrder(order);
    saveOrder(order);
    sendConfirmationEmail(order);
}

private void validateOrder(Order order) {
    if (!order.isValid()) {
        throw new InvalidOrderException("Order validation failed");
    }
}

private void saveOrder(Order order) {
    repository.save(order);
}

private void sendConfirmationEmail(Order order) {
    emailService.send(order.customerEmail(), createConfirmationMessage(order));
}
```

**How to identify violations:**

- Method mixes database calls with business logic
- Method mixes string parsing with domain operations
- Method mixes HTTP handling with business rules
- You can't describe the method at one level ("it validates AND saves AND sends email AND parses JSON AND...")

**Benefits:**
- Methods read top-to-bottom like prose
- Each method can be understood without reading implementation details
- Easier to test each abstraction level separately
- Refactoring becomes safer

### Composed Method Pattern

**Principle:** Methods should be composed of calls to other well-named methods at the same level of abstraction. Small methods that read like a story.

**The smell:** Long methods with comments explaining sections are candidates for extraction.

**Related to:**
- Object Calisthenics Rule 7 (keep entities small)
- Critical Rule 7 (no code comments)
- Single Level of Abstraction Principle

```java
// ❌ Long method with comments as section markers
void checkout(Cart cart, PaymentInfo payment) {
    // Validate cart
    if (cart.items().isEmpty()) {
        throw new EmptyCartException();
    }
    for (var item : cart.items()) {
        if (item.quantity() <= 0) {
            throw new InvalidQuantityException();
        }
        if (!item.isInStock()) {
            throw new OutOfStockException(item);
        }
    }

    // Calculate totals
    var subtotal = BigDecimal.ZERO;
    for (var item : cart.items()) {
        subtotal = subtotal.add(
            item.price().multiply(BigDecimal.valueOf(item.quantity()))
        );
    }
    var tax = subtotal.multiply(TAX_RATE);
    var shipping = calculateShippingCost(cart);
    var total = subtotal.add(tax).add(shipping);

    // Process payment
    if (payment.amount().compareTo(total) < 0) {
        throw new InsufficientPaymentException();
    }
    var transaction = paymentGateway.charge(payment, total);
    if (!transaction.isSuccessful()) {
        throw new PaymentFailedException(transaction.error());
    }

    // Create order
    var order = new Order(cart.items(), total, transaction.id());
    orderRepository.save(order);

    // Send confirmation
    emailService.send(
        cart.customer().email(),
        "Order confirmed: " + order.id()
    );
}

// ✅ Composed method - each comment becomes a method
void checkout(Cart cart, PaymentInfo payment) {
    validateCart(cart);
    var total = calculateTotal(cart);
    var transaction = processPayment(payment, total);
    var order = createOrder(cart, total, transaction);
    sendConfirmation(cart.customer(), order);
}

private void validateCart(Cart cart) {
    if (cart.items().isEmpty()) {
        throw new EmptyCartException();
    }
    cart.items().forEach(this::validateItem);
}

private void validateItem(Item item) {
    if (item.quantity() <= 0) {
        throw new InvalidQuantityException();
    }
    if (!item.isInStock()) {
        throw new OutOfStockException(item);
    }
}

private Money calculateTotal(Cart cart) {
    var subtotal = cart.items().stream()
        .map(item -> item.price().multiply(item.quantity()))
        .reduce(Money.zero(), Money::add);

    return subtotal
        .add(calculateTax(subtotal))
        .add(calculateShipping(cart));
}

private Transaction processPayment(PaymentInfo payment, Money total) {
    if (payment.amount().isLessThan(total)) {
        throw new InsufficientPaymentException();
    }

    var transaction = paymentGateway.charge(payment, total);
    if (!transaction.isSuccessful()) {
        throw new PaymentFailedException(transaction.error());
    }

    return transaction;
}

private Order createOrder(Cart cart, Money total, Transaction transaction) {
    var order = new Order(cart.items(), total, transaction.id());
    orderRepository.save(order);
    return order;
}

private void sendConfirmation(Customer customer, Order order) {
    emailService.send(
        customer.email(),
        "Order confirmed: " + order.id()
    );
}
```

**Comment as extraction signal:**

When you write a comment, ask: "Should this be a method name instead?"

```java
// ❌ Comment explains what follows
// Check if user has admin privileges
if (user.roles().contains("ADMIN") ||
    user.permissions().contains("MANAGE_USERS")) {
    // ...
}

// ✅ Method name replaces comment
if (user.hasAdminPrivileges()) {
    // ...
}

class User {
    boolean hasAdminPrivileges() {
        return roles.contains("ADMIN") ||
               permissions.contains("MANAGE_USERS");
    }
}
```

**Benefits:**
- Main method reads like table of contents
- Each extracted method can be understood in isolation
- Comments become unnecessary - method names are self-documenting
- Easier to test individual pieces
- Easier to reuse extracted methods

**When NOT to extract:**
- Method is already under 5 lines and clear
- Extraction creates a method used only once with no clarity benefit
- The extracted method would need many parameters (suggests wrong abstraction)

## Feature Envy Detection

**Problem:** When a method consumes another class's data more than its own, feature envy exists.

**Detection approach:** Count external versus internal references. Imbalance suggests misplaced logic.

```java
// ❌ Feature envy
class OrderProcessor {
    void processOrder(Order order) {
        // Uses order's data exclusively
        if (order.getStatus().equals("pending") &&
            order.getTotal().compareTo(BigDecimal.ZERO) > 0 &&
            order.getCustomer().isActive()) {
            order.setStatus("approved");
        }
    }
}

// ✅ Move logic to envied class
class Order {
    void approve() {
        if (!status.equals("pending")) {
            throw new IllegalStateException("Only pending orders can be approved");
        }
        if (total.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalStateException("Cannot approve order with zero total");
        }
        if (!customer.isActive()) {
            throw new IllegalStateException("Cannot approve order for inactive customer");
        }

        this.status = "approved";
    }
}

class OrderProcessor {
    void processOrder(Order order) {
        order.approve(); // Tell, don't ask
    }
}
```

## Dependency Inversion Principle

**Problem:** Instantiating dependencies inside methods creates tight coupling and testing difficulties.

**Solution:** Inject dependencies through constructors, making them explicit and mockable.

```java
// ❌ Tight coupling
class OrderService {
    void createOrder(List<Item> items) {
        var repository = new OrderRepository(); // Hard dependency
        var order = new Order(items);
        repository.save(order);
    }
}

// ✅ Dependency injection
class OrderService {
    private final OrderRepository repository;

    OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    void createOrder(List<Item> items) {
        var order = new Order(items);
        repository.save(order);
    }
}
```

**Scan for:** `new X()` calls within methods and static invocations—extract these to the constructor.

## Fail-Fast Error Handling

**Reject silent fallback chains.** Instead, validate aggressively:

```java
// ❌ Silent fallback chain (using Optional poorly)
String name = Optional.ofNullable(user)
    .map(User::name)
    .or(() -> Optional.ofNullable(backup).map(User::name))
    .orElse("Unknown");

// ✅ Fail fast with context
if (user == null) {
    throw new IllegalStateException(
        "Expected user to be defined. Context: processing checkout"
    );
}
if (user.name() == null) {
    throw new IllegalStateException(
        "Expected user.name to be defined. Got: " + user
    );
}
String name = user.name();
```

**Error format:** "Expected [X]. Got [Y]. Context: [debugging information]"

This approach surfaces bugs immediately rather than masking them.

## Tell-Don't-Ask Principle

**Tell objects what to do; don't ask them for data and make decisions for them.**

Behavior belongs with the data it operates on. When you extract data from an object to make decisions, you violate encapsulation and scatter domain logic across callers.

### Symptoms of Violations

- Chains of getters followed by conditionals: `if (user.getStatus().equals("active") && user.getBalance() > 0)`
- Data classes with all getters, no behavior
- Service classes making decisions about other objects' data
- Repeated patterns: "get data → decide → call method"

### Core Pattern

```java
// ❌ Ask-Then-Tell (Violation)
class PaymentProcessor {
    void processPayment(Account account, Money amount) {
        if (account.balance().isGreaterThan(amount) &&
            account.status().equals("active") &&
            !account.isFrozen()) {
            account.deduct(amount);
        }
    }
}

// ✅ Tell-Don't-Ask (Fixed)
class PaymentProcessor {
    void processPayment(Account account, Money amount) {
        account.withdraw(amount); // Tell, don't ask
    }
}

class Account {
    void withdraw(Money amount) {
        if (balance.isLessThan(amount)) {
            throw new InsufficientFundsException("Insufficient funds");
        }
        if (!status.equals("active")) {
            throw new IllegalStateException("Account is not active");
        }
        if (frozen) {
            throw new IllegalStateException("Account is frozen");
        }

        this.balance = balance.subtract(amount);
    }
}
```

### Tell-Don't-Ask Quick Reference

| Pattern | Ask-Then-Tell (Bad) | Tell-Don't-Ask (Good) |
|---------|---------------------|----------------------|
| **Decision location** | Caller extracts data, decides | Object decides internally |
| **Getters** | Many public getters | Minimal, only for genuine queries |
| **Conditionals** | In caller: `if (obj.getX())` | Inside object methods |
| **Behavior** | Scattered across callers | Concentrated in domain objects |
| **Validation** | Caller validates before calling | Object validates when called |

### When Getters Are Acceptable

Getters are fine for:
- **Genuine queries** where no behavior follows: `name()` for display
- **Serialization boundaries**: Converting to JSON/DTO for API responses
- **DDD value objects** that already encapsulate their behavior

**Red flag:** Getter followed by conditional = decision that belongs inside the object.

### Value Objects and Tell-Don't-Ask

DDD value objects should have behavior, not just getters:

```java
// ❌ Anemic value object (just getters)
record Money(BigDecimal amount, String currency) {
    // No behavior, just data accessors
}

// Caller forced to extract and decide
if (price.amount().compareTo(new BigDecimal("100")) > 0 &&
    price.currency().equals("USD")) {
    applyDiscount();
}

// ✅ Rich value object with behavior
record Money(BigDecimal amount, String currency) {
    Money {
        requireNonNull(amount, "amount");
        requireNonNull(currency, "currency");
    }

    // Behavior encapsulated in value object
    boolean isGreaterThan(Money other) {
        ensureSameCurrency(other);
        return amount.compareTo(other.amount) > 0;
    }

    Money add(Money other) {
        ensureSameCurrency(other);
        return new Money(amount.add(other.amount), currency);
    }

    Money multiply(int factor) {
        return new Money(
            amount.multiply(BigDecimal.valueOf(factor)),
            currency
        );
    }

    private void ensureSameCurrency(Money other) {
        if (!currency.equals(other.currency)) {
            throw new IllegalArgumentException(
                "Cannot operate on different currencies: %s vs %s"
                    .formatted(currency, other.currency)
            );
        }
    }

    static Money zero(String currency) {
        return new Money(BigDecimal.ZERO, currency);
    }
}

// Caller tells value object what to do
if (price.isGreaterThan(threshold)) {
    applyDiscount();
}

Money total = price.add(tax).multiply(quantity);
```

**Key principle:** Value objects have getters when you need raw values (for display, persistence), but they should also encapsulate operations on those values.

### Common Tell-Don't-Ask Mistakes

**1. "But I need to know the status for display!"**

This is a decision based on state. Provide intention-revealing queries:

```java
// ❌ Getter for decision
if (order.status().equals("shipped")) {
    showTrackingInfo();
}

// ✅ Intention-revealing query
if (order.isTrackable()) {
    showTrackingInfo();
}
```

**2. "The object can't make this decision - it needs external context!"**

Pass context to the command:

```java
// ❌ Caller decides
if (user.role().equals("admin") ||
    user.id().equals(document.ownerId())) {
    document.delete();
}

// ✅ Object decides with context
document.deleteBy(user); // Document checks permissions internally
```

**3. "My framework requires getters/setters"**

Framework requirements are boundaries, not excuses:

```java
// Domain object (rich, tells)
class Order {
    void approve() { /* business logic */ }
}

// DTO for framework (data bag - record is perfect)
record OrderDTO(String status, BigDecimal total) {
    // Just data for serialization
}
```

## Naming Conventions

**Forbidden generic names:**
`data`, `utils`, `helpers`, `common`, `shared`, `manager`, `handler`, `processor`

These convey nothing about actual purpose.

**Checklist for classes:**
- Does the name reveal responsibility?
- Is it a domain noun?
- Would domain experts recognize it?

**Checklist for methods:**
- Does the name reveal the action?
- Is it a domain verb?
- Does it describe the business operation?

**Checklist for variables:**
- Does the name reveal content?
- Is it context-specific?
- Is it understandable without reading the implementation?

**Refactoring process:** Understand purpose → consult domain experts → extract domain concepts → rename comprehensively.

## Type-Driven Design

### Make Illegal States Unrepresentable

Use sealed types to encode business rules:

```java
// ✅ Sealed types prevent impossible states
sealed interface Order permits UnconfirmedOrder, ConfirmedOrder, ShippedOrder {
    List<Item> items();
}

record UnconfirmedOrder(List<Item> items) implements Order {}

record ConfirmedOrder(
    List<Item> items,
    String confirmationNumber
) implements Order {}

record ShippedOrder(
    List<Item> items,
    String confirmationNumber,
    LocalDate shippedDate
) implements Order {}

// Now impossible to have shippedDate without confirmationNumber
// Pattern matching makes state handling type-safe
String formatOrder(Order order) {
    return switch (order) {
        case UnconfirmedOrder u -> "Pending confirmation";
        case ConfirmedOrder c -> "Confirmed: " + c.confirmationNumber();
        case ShippedOrder s -> "Shipped on: " + s.shippedDate();
    };
}
```

### Avoid Type Escape Hatches

**Strictly forbidden:**
- Raw types (`List` instead of `List<Item>`)
- Unchecked casts (`(List<Item>) rawList`)
- `@SuppressWarnings("unchecked")`
- Reflection for bypassing encapsulation

A type-safe solution always exists.

### Use the Type System for Validation

Employ domain types to enforce validation:

```java
// ✅ Type enforces validation
record PositiveAmount(BigDecimal value) {
    PositiveAmount {
        if (value.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException(
                "Expected positive amount, got " + value
            );
        }
    }
}

void calculateInterest(PositiveAmount principal) {
    // Type system guarantees principal is positive
}
```

## Prefer Immutability

**Problem:** Mutable state causes unexpected changes, race conditions, and debugging complexity.

**Solution:** Return new values instead of mutating inputs.

**Application rules:**
- Prefer `final` fields
- Use immutable collections (`List.of()`, `List.copyOf()`)
- Use records for simple data carriers
- Prefer `Stream` operations over loops with mutation
- When mutation is necessary, make it explicit and contained

```java
// ❌ Mutation
List<Item> addItem(List<Item> items, Item newItem) {
    items.add(newItem); // Mutates input
    return items;
}

// ✅ Immutable
List<Item> addItem(List<Item> items, Item newItem) {
    return Stream.concat(items.stream(), Stream.of(newItem))
        .toList(); // Returns new immutable list
}

// Or more explicitly
List<Item> addItem(List<Item> items, Item newItem) {
    var newList = new ArrayList<>(items);
    newList.add(newItem);
    return List.copyOf(newList); // Return immutable copy
}
```

## YAGNI - You Aren't Gonna Need It

**Principle:** Build only what's required now. Speculative code wastes time and maintenance effort.

**Application rules:**
- Implement the simplest working solution
- Add capabilities when requirements demand them
- "We might need it" is not a valid requirement

```java
// ❌ Over-engineered for future
interface PaymentProcessor {
    void processPayment(Money amount);
    void processBatchPayments(List<Money> amounts); // Not needed yet
    void scheduleRecurringPayment(Money amount, Duration interval); // Not needed yet
    void cancelScheduledPayment(String id); // Not needed yet
}

// ✅ Build what's needed now
interface PaymentProcessor {
    void processPayment(Money amount);
}
// Add other methods when requirements emerge
```

## Code Review Checklist

Use this checklist when reviewing code:

**Encapsulation:**
- [ ] Behavior located with the data it operates on?
- [ ] Tell-don't-ask: objects told what to do, not interrogated?
- [ ] Getters only for genuine queries, not followed by decisions?

**Dependencies:**
- [ ] Dependencies injected via constructor, not instantiated internally?
- [ ] No `new X()` calls inside methods?

**Error Handling:**
- [ ] Fail-fast errors with clear messages?
- [ ] No silent fallback chains?

**Types:**
- [ ] No raw types, unchecked casts, or suppressed warnings?
- [ ] Illegal states unrepresentable through type design?

**Naming:**
- [ ] No generic names (data, utils, handler, manager)?
- [ ] Domain vocabulary used throughout?

**Complexity:**
- [ ] One indentation level per method (max 3)?
- [ ] No else keywords (early returns instead)?
- [ ] Methods under 10 lines, classes under 150?

**Method Design:**
- [ ] Single level of abstraction per method?
- [ ] Methods composed of well-named method calls?
- [ ] Comments replaced with intention-revealing method names?
- [ ] Long methods with comment sections extracted into separate methods?

**Immutability:**
- [ ] Methods return new values rather than mutating inputs?
- [ ] Final fields preferred?
- [ ] Immutable collections used?

**YAGNI:**
- [ ] No speculative features ("might need it later")?
- [ ] Simplest solution that meets current requirements?

## When Tempted to Cut Corners

Stop before:
- Using fallback chains → fail fast with clear errors
- Using raw types/unchecked casts → fix types properly
- Using `new X()` inside methods → inject via constructor
- Naming with `data`, `utils`, `handler` → adopt domain language
- Adding getters for decisions → move decision into object
- Mixing abstraction levels in one method → extract to single-level methods
- Writing comments to explain code sections → extract methods with intention-revealing names
- Leaving long methods because "extraction is tedious" → apply composed method pattern
- Skipping refactor → refactoring is part of the work
- Mutating parameters → return new values
- Building "for later" → build what's needed now
