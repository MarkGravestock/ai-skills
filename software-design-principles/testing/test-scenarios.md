# Test Scenarios for Software Design Principles Skill

## Scenario 1: Tell-Don't-Ask Violation Detection

**Context:** User asks for code review of a payment processing class.

**Test Code:**
```java
class PaymentProcessor {
    void processPayment(Account account, Money amount) {
        // Multiple getters followed by decision logic
        if (account.getBalance().compareTo(amount) >= 0 &&
            account.getStatus().equals("ACTIVE") &&
            !account.isFrozen()) {

            var newBalance = account.getBalance().subtract(amount);
            account.setBalance(newBalance);
            account.addTransaction(new Transaction(amount, LocalDateTime.now()));
        } else {
            throw new InsufficientFundsException();
        }
    }
}
```

**Expected Behavior WITH Skill:**
- Identify tell-don't-ask violation
- Point out getters followed by conditionals
- Suggest moving logic into Account class
- Recommend `account.withdraw(amount)` pattern

**Baseline Behavior WITHOUT Skill (to establish):**
- May miss the pattern
- Might suggest minor improvements (naming, etc.) but miss encapsulation issue
- May not recommend extracting to Account

---

## Scenario 2: Mixed Abstraction Levels (SLAP)

**Context:** User asks to review an order processing method.

**Test Code:**
```java
void processOrder(Order order) {
    // High-level business logic
    if (!order.hasItems()) {
        throw new EmptyOrderException();
    }

    // Low-level JDBC details mixed in
    var conn = DriverManager.getConnection(
        "jdbc:mysql://localhost:3306/orders",
        "user",
        "pass"
    );
    var stmt = conn.prepareStatement(
        "INSERT INTO orders (id, customer_id, total) VALUES (?, ?, ?)"
    );
    stmt.setString(1, order.getId());
    stmt.setString(2, order.getCustomerId());
    stmt.setBigDecimal(3, order.getTotal());
    stmt.executeUpdate();
    conn.close();

    // High-level again
    emailService.sendConfirmation(order);
}
```

**Expected Behavior WITH Skill:**
- Identify mixed abstraction levels
- Point out JDBC details mixed with business logic
- Recommend extracting to `saveOrder(order)` method
- Suggest dependency injection for database access

**Baseline Behavior WITHOUT Skill:**
- May suggest extracting JDBC code for clarity
- Might not frame it as "abstraction level" issue
- May miss the deeper SLAP principle

---

## Scenario 3: Comments as Method Extraction Opportunity

**Context:** User shows a checkout method with comment sections.

**Test Code:**
```java
void checkout(Cart cart, PaymentInfo payment) {
    // Validate cart items
    for (var item : cart.getItems()) {
        if (item.getQuantity() <= 0) {
            throw new InvalidQuantityException();
        }
        if (!inventory.isInStock(item)) {
            throw new OutOfStockException();
        }
    }

    // Calculate total with tax
    var subtotal = BigDecimal.ZERO;
    for (var item : cart.getItems()) {
        var itemTotal = item.getPrice()
            .multiply(BigDecimal.valueOf(item.getQuantity()));
        subtotal = subtotal.add(itemTotal);
    }
    var tax = subtotal.multiply(new BigDecimal("0.08"));
    var total = subtotal.add(tax);

    // Process payment
    var result = paymentGateway.charge(payment.getCard(), total);
    if (!result.isSuccess()) {
        throw new PaymentFailedException();
    }

    // Create order record
    var order = new Order(cart.getItems(), total);
    orderRepository.save(order);
}
```

**Expected Behavior WITH Skill:**
- Identify comments as method extraction signal
- Recommend composed method pattern
- Suggest extracting: validateCartItems(), calculateTotal(), processPayment(), createOrder()
- Reference Critical Rule 7 (no comments)

**Baseline Behavior WITHOUT Skill:**
- May suggest method is too long
- Might recommend extraction but miss "comments = extraction opportunity" principle
- May not cite composed method pattern

---

## Scenario 4: Pressure Test - "Simple" Code

**Context:** User asks for review but says "this is simple code, just need a quick check."

**Test Code:**
```java
class UserService {
    void activateUser(String userId) {
        var conn = DriverManager.getConnection(DB_URL);
        var stmt = conn.prepareStatement(
            "UPDATE users SET status = 'ACTIVE' WHERE id = ?"
        );
        stmt.setString(1, userId);
        stmt.executeUpdate();
        conn.close();
    }
}
```

**Expected Behavior WITH Skill:**
- Apply principles regardless of "simple" framing
- Identify dependency injection violation (`new` connection inside method)
- Suggest repository/DAO pattern
- Don't skip review due to "simple" label

**Baseline Behavior WITHOUT Skill:**
- May accept "simple" framing and give superficial review
- Might miss DI violation due to code brevity
- May not push for proper architecture on "simple" code

---

## Scenario 5: Anemic Domain Model (Value Objects)

**Context:** User asks to review a Money value object.

**Test Code:**
```java
record Money(BigDecimal amount, String currency) {
    // Just accessors, no behavior
}

// Usage elsewhere
class PricingService {
    Money calculateDiscount(Money price, BigDecimal discountRate) {
        if (price.amount().compareTo(new BigDecimal("100")) > 0 &&
            price.currency().equals("USD")) {
            var discountAmount = price.amount().multiply(discountRate);
            var newAmount = price.amount().subtract(discountAmount);
            return new Money(newAmount, "USD");
        }
        return price;
    }
}
```

**Expected Behavior WITH Skill:**
- Identify anemic value object
- Recommend adding behavior: isGreaterThan(), subtract(), multiply()
- Point out tell-don't-ask violation in PricingService
- Suggest Money should encapsulate currency operations

**Baseline Behavior WITHOUT Skill:**
- May not identify anemic model issue
- Might suggest minor improvements but miss DDD value object pattern
- May not connect to tell-don't-ask principle

---

## Scenario 6: Generic Naming

**Context:** User asks for review of a utility class.

**Test Code:**
```java
class OrderUtils {
    static OrderData processOrderData(OrderData data) {
        // Processing logic
        return data;
    }
}
```

**Expected Behavior WITH Skill:**
- Identify forbidden generic names: Utils, Data
- Reference Critical Rule 5 (intention-revealing names)
- Ask about domain concepts being represented
- Suggest domain-specific names based on actual purpose

**Baseline Behavior WITHOUT Skill:**
- May not flag generic names as violations
- Might accept "Utils" as common pattern
- May not push for domain vocabulary

---

## Testing Protocol

### RED Phase (Baseline)
1. Run each scenario with a fresh agent WITHOUT this skill loaded
2. Document exact responses - what did agent catch? What did agent miss?
3. Identify rationalizations: "it's simple", "utils is standard", "good enough for now"

### GREEN Phase (With Skill)
1. Run same scenarios WITH skill loaded
2. Verify agent now catches all violations
3. Confirm agent references skill principles correctly

### REFACTOR Phase (Close Loopholes)
1. Identify new rationalizations from GREEN phase testing
2. Add explicit counters to skill if needed
3. Re-test until bulletproof

---

## Success Criteria

Agent WITH skill should:
- [ ] Detect tell-don't-ask violations (Scenario 1)
- [ ] Identify mixed abstraction levels (Scenario 2)
- [ ] Recognize comments as extraction signals (Scenario 3)
- [ ] Apply principles to "simple" code (Scenario 4)
- [ ] Identify anemic domain models (Scenario 5)
- [ ] Flag generic naming violations (Scenario 6)
- [ ] Reference specific skill sections in feedback
- [ ] Not skip reviews due to code seeming "simple" or "obvious"
