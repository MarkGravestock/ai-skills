---
name: validation-review
description: >
  Review domain model validation in a Java/Spring/DDD codebase. Use this skill whenever
  the user asks to review, audit, or improve validation in a domain model, aggregate, value
  object, application service, or Spring controller. Triggers on: "review my validation",
  "is my validation correct", "where should validation go", "should I use exceptions or
  result types", "how should I validate my domain", "check my aggregate validation",
  "review this service/entity/value object for validation issues", or whenever the user
  shares code and asks if validation is done correctly in a DDD or Spring context.
---

# Domain Model Validation Review

Review Java/Spring/DDD validation code and give a structured, pragmatic assessment.
The goal is to identify misplaced validation, wrong mechanisms for the context, and
missing invariant protection — then suggest concrete fixes with code.

---

## Core Mental Model

Use **Design by Contract** as the primary lens:

| Situation | Correct response |
|---|---|
| Caller violated a method contract (null, structurally invalid) | `IllegalArgumentException` / NPE — contract violation, fix the caller |
| Domain invariant broken (object would be in invalid state) | Domain exception — always-valid model |
| Expected business outcome ("insufficient funds", "already cancelled") | Domain exception OR Result type — it's a known flow, not a bug |
| Genuinely unexpected failure (DB down, etc.) | Unchecked runtime exception, bubble up |

The key rule: **if fixing it requires changing the calling code, it's a contract violation — throw**.
Result types only earn their keep for *expected business outcomes* the caller must reason about.

---

## Layer Responsibilities

### Domain Layer (Entities, Aggregates, Value Objects)
- **Enforce invariants in constructors and factory methods** — make illegal states unrepresentable
- **Enforce state transition rules in behaviour methods** — throw `DomainRuleViolationException`
- **Do NOT use Bean Validation annotations** (`@NotNull`, `@Size` etc.) — these leak infrastructure concerns
- **Do NOT let entities enter invalid state and then self-validate** — the aggregate must always be valid

### Application Service Layer
- Translate domain exceptions to appropriate responses
- Handle cross-aggregate validation via Domain Services
- Use Notification pattern only when you genuinely need to collect multiple errors before failing

### API / Infrastructure Boundary (Controllers, DTOs)
- **Bean Validation (JSR-380) belongs here**, on DTOs and request records — not on domain entities
- `@Valid` on controller method params is correct
- `@RestControllerAdvice` translates domain exceptions to HTTP responses

---

## Review Checklist

When reviewing code, work through these in order:

### 1. Is Bean Validation on domain entities?
```java
// ❌ Wrong — infrastructure concern in domain
public class Order {
    @NotNull private CustomerId customerId;
    @DecimalMin("0") private BigDecimal total;
}

// ✅ Correct — validation belongs on the DTO
public record CreateOrderRequest(
    @NotNull String customerId,
    @DecimalMin("0.01") BigDecimal amount
) {}
```

### 2. Can the aggregate enter an invalid state?
```java
// ❌ Wrong — object exists in invalid state, validated later
Order order = new Order();
order.setCustomerId(customerId);
order.setTotal(total);
validator.validate(order); // too late

// ✅ Correct — invariants enforced at construction
public static Order create(CustomerId customerId, Money total) {
    Objects.requireNonNull(customerId, "customerId required");
    Objects.requireNonNull(total,      "total required");
    return new Order(OrderId.generate(), customerId, total);
}
```

### 3. Are state transition rules enforced in behaviour methods?
```java
// ❌ Wrong — caller can transition to any state
order.setStatus(OrderStatus.DISPATCHED);

// ✅ Correct — domain enforces the rule
public void dispatch(String deliveryAddress) {
    if (this.status != OrderStatus.CONFIRMED)
        throw new DomainRuleViolationException(
            "Order must be confirmed before dispatch");
    if (deliveryAddress == null || deliveryAddress.isBlank())
        throw new IllegalArgumentException("deliveryAddress required");
    this.status = OrderStatus.DISPATCHED;
    this.deliveryAddress = deliveryAddress;
}
```

### 4. Is the exception hierarchy appropriate?
```java
// Recommended hierarchy — all unchecked (extend RuntimeException)
public class DomainException extends RuntimeException {
    public DomainException(String message) { super(message); }
    public DomainException(String message, Throwable cause) { super(message, cause); }
}

// Business rule / state transition violation
public class DomainRuleViolationException extends DomainException {
    public DomainRuleViolationException(String message) { super(message); }
}

// Cross-aggregate or external lookup failure
public class DomainServiceException extends DomainException {
    public DomainServiceException(String message) { super(message); }
}
```

See the **Runtime Exceptions** section below for why all domain exceptions must be unchecked.

### 5. Is a Result type being used where an exception would be clearer?
```java
// ❌ Questionable — contract violation returned as Result
public Result<Order> create(CustomerId id, Money total) {
    if (id == null) return Result.failure("id required"); // caller bug, not business outcome
}

// ✅ Result is justified — "declined" is a genuine business outcome
public Result<Payment> processPayment(PaymentRequest req) {
    if (!authorisationService.authorise(req))
        return Result.failure("Payment declined by issuer");
    ...
}
```

### 6. Is there a global exception handler translating domain exceptions?
```java
@RestControllerAdvice
public class DomainExceptionHandler {

    @ExceptionHandler(DomainRuleViolationException.class)
    @ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
    public ProblemDetail handleRuleViolation(DomainRuleViolationException ex) {
        return ProblemDetail.forStatusAndDetail(
            HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage());
    }

    @ExceptionHandler(DomainException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleDomainException(DomainException ex) {
        return ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST, ex.getMessage());
    }
}
```

### 7. Are Value Objects self-validating and immutable?
```java
// ✅ Value Object — validates on construction, no setters
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        Objects.requireNonNull(amount,   "amount required");
        Objects.requireNonNull(currency, "currency required");
        if (amount.compareTo(BigDecimal.ZERO) < 0)
            throw new IllegalArgumentException("amount cannot be negative");
        this.amount   = amount.setScale(2, RoundingMode.HALF_UP);
        this.currency = currency;
    }
}
```

### 8. Cross-aggregate validation — is it in a Domain Service?
```java
// ❌ Wrong — aggregate reaches outside its boundary
public class Order {
    public void assignCustomer(CustomerId id, CustomerRepository repo) { ... }
}

// ✅ Correct — Domain Service owns cross-aggregate rules
@DomainService
public class CustomerEligibilityService {
    public void assertEligible(CustomerId customerId) {
        var customer = customerRepository.findById(customerId)
            .orElseThrow(() -> new DomainException("Customer not found"));
        if (!customer.isActive())
            throw new DomainRuleViolationException("Customer account is not active");
    }
}
```

---

## Runtime Exceptions and Domain Validation

This is a fundamental Java design point that affects every domain exception decision.

### Checked vs Unchecked — the core distinction

Java has two kinds of exceptions:

- **Checked** (`extends Exception`) — the compiler forces every caller to either catch or declare them with `throws`. They are part of the method signature.
- **Unchecked** (`extends RuntimeException`) — propagate freely up the call stack without any compiler enforcement. Callers handle them if they choose to, or let them bubble.

**All domain validation exceptions must be unchecked.** Here's why.

### Why checked exceptions are wrong for domain validation

```java
// ❌ Checked domain exception — pollutes every method signature
public class Order {
    public void dispatch(String address) throws OrderDispatchException { ... }
}

// Now every caller is forced into this:
public class OrderApplicationService {
    public void processDispatch(UUID id, String address)
            throws OrderDispatchException {  // forced to declare or catch
        orderRepository.findById(id)
            .orElseThrow()
            .dispatch(address);              // compiler demands handling
    }
}

// And every layer above that too:
public class OrderController {
    public ResponseEntity<?> dispatch(...) throws OrderDispatchException { ... }
}
```

The checked exception has now leaked through every layer. The controller has no business knowing about `OrderDispatchException` — that's the domain's concern. This is the opposite of what DDD demands.

```java
// ✅ Unchecked domain exception — propagates freely, handled once at the boundary
public class Order {
    public void dispatch(String address) {  // clean signature
        if (this.status != OrderStatus.CONFIRMED)
            throw new DomainRuleViolationException("Order must be confirmed before dispatch");
        ...
    }
}

// Application service — no throws declaration needed
public class OrderApplicationService {
    public void processDispatch(UUID id, String address) {
        orderRepository.findById(id).orElseThrow().dispatch(address);
        // DomainRuleViolationException propagates naturally if thrown
    }
}

// Caught once, at the boundary
@RestControllerAdvice
public class DomainExceptionHandler {
    @ExceptionHandler(DomainRuleViolationException.class)
    @ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
    public ProblemDetail handle(DomainRuleViolationException ex) { ... }
}
```

### The JVM exception hierarchy — where domain exceptions sit

```
Throwable
├── Error                          ← JVM-level (OutOfMemoryError etc.) — never catch
└── Exception
    ├── IOException                ← Checked — recoverable infrastructure failures
    ├── SQLException               ← Checked — but Spring wraps these for you
    └── RuntimeException           ← Unchecked — your domain exceptions live here
        ├── IllegalArgumentException   ← Contract violation (null, bad format)
        ├── IllegalStateException       ← Object in wrong state for the call
        ├── NullPointerException        ← Contract violation (should have been null-checked)
        └── DomainException            ← Your hierarchy root
            ├── DomainRuleViolationException
            └── DomainServiceException
```

Note: `IllegalArgumentException` and `IllegalStateException` are already unchecked and are
entirely appropriate for contract violations — you don't always need a custom type.

### The Spring @Transactional interaction — critical to get right

Spring's default transaction rollback behaviour differs based on exception type:

```java
// Spring's default:
// - RuntimeException (unchecked) → ROLLBACK ✅
// - Exception (checked)          → COMMIT ❌  (almost certainly not what you want)

// ❌ Dangerous — checked exception, Spring COMMITS the transaction
@Transactional
public void processOrder(UUID id) throws OrderException {  // checked
    order.dispatch(address);
    throw new OrderException("something wrong"); // transaction COMMITS
}

// ✅ Safe — unchecked exception, Spring ROLLS BACK
@Transactional
public void processOrder(UUID id) {
    order.dispatch(address);
    // DomainRuleViolationException (unchecked) → Spring rolls back
}
```

This is a common silent bug: a checked domain exception causes Spring to commit a
partial transaction because it only rolls back on `RuntimeException` by default.
You can override with `@Transactional(rollbackFor = Exception.class)` but that's
a workaround for a design mistake — use unchecked exceptions instead.

### When are checked exceptions appropriate?

Checked exceptions make sense for **recoverable infrastructure failures** where the
caller genuinely has a choice of recovery strategy:

```java
// Reasonable use of checked exception — caller may want to retry, use fallback, etc.
public interface DocumentStore {
    Document fetch(DocumentId id) throws DocumentStoreUnavailableException;
}
```

But even here, Spring's `@Repository` and infrastructure layers typically wrap these
in unchecked `DataAccessException` subclasses so the domain stays clean.

**The practical rule:** if it's a domain or application concern, unchecked.
If it's a recoverable infrastructure failure with meaningful caller-side recovery
options, checked — but expect Spring to wrap it anyway.

---

## Output Format

Structure the review as:

1. **Summary** — one paragraph: overall approach, main issues, severity
2. **Issues found** — for each issue:
   - What it is
   - Why it matters
   - Fixed code example
3. **What's correct** — briefly acknowledge good patterns already present
4. **Recommendation** — the one or two highest-priority changes

Keep the tone direct and pragmatic. Reference the layer/contract model when explaining *why* something is wrong, not just *what* is wrong. Always show corrected code.

---

## Common Patterns to Flag

- Bean Validation annotations on domain entities (very common mistake)
- Anemic domain model with validation only in service layer
- **Checked exceptions for domain validation** — pollutes method signatures across all layers and causes silent Spring transaction commits
- Result types used for contract violations (null inputs, wrong types) rather than business outcomes
- Validation duplicated across multiple layers without clear ownership
- Missing `@RestControllerAdvice` — domain exceptions leaking as 500s
- `@Transactional` without rollback on checked exceptions — partial commits on domain failures
- JPA requiring no-arg constructors that bypass validation — flag this and suggest a solution (separate persistence model or post-load validation)
