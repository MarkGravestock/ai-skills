---
name: java-junit5-testing
description: Write Java/JUnit 5 tests using BDD-style nested classes, custom AssertJ assertion DSLs, Test Data Builders, and Object Mother patterns. Use when writing tests for domain aggregates in Java, creating fluent assertion chains with domain vocabulary, implementing fixture factories, or structuring tests with @Nested/@DisplayName for readability. Particularly relevant for Java projects using DDD, Spring Boot, or event-sourced architectures.
---

# Java/JUnit 5 Testing with DSL and Fixtures

Write Java/JUnit 5 tests with maximum expressiveness using `@Nested`/`@DisplayName` for BDD structure, AssertJ custom assertions for domain-specific vocabulary, and the Object Mother + Test Data Builder pattern for readable fixture creation.

## Core Principles

1. **BDD via `@Nested`**: Use nested inner classes to express Given/When/Then hierarchy
2. **`@DisplayName` as Specification**: Every test name reads as a business rule
3. **Custom AssertJ Assertions**: Extend `AbstractAssert` to build a domain assertion DSL
4. **Object Mother + Fluent Builder**: Combine for default fixtures with targeted variation
5. **Parameterised Tests for Tables**: `@ParameterizedTest` + `@MethodSource` replaces Spock's `where:` block
6. **Static Imports**: Hide construction noise behind expressive factory method names

## Test Structure Pattern

### BDD with `@Nested` + `@DisplayName`

The Java equivalent of Spock's `given:/when:/then:` blocks — nested classes create visible hierarchy:

```java
@DisplayName("Book placing on hold")
class BookPlacingOnHoldTest {

    @Nested
    @DisplayName("given a circulating book that is available")
    class GivenCirculatingAvailableBook {

        private final AvailableBook book = circulatingAvailableBook();

        @Nested
        @DisplayName("when a regular patron with no holds places it on hold")
        class WhenRegularPatronPlacesHold {

            private final Either<BookHoldFailed, BookPlacedOnHoldEvents> result =
                regularPatronWithHolds(0).placeOnHold(book, closeEnded(3));

            @Test
            @DisplayName("then the hold should succeed")
            void holdSucceeds() {
                assertThat(result).isRight();
            }

            @Test
            @DisplayName("then a BookPlacedOnHold event should be emitted")
            void bookPlacedOnHoldEventEmitted() {
                assertThat(result).isRightSatisfying(events ->
                    assertThat(events).hasSize(1)
                );
            }
        }

        @Nested
        @DisplayName("when a regular patron already at the 5-book hold limit tries to hold")
        class WhenPatronAtHoldLimit {

            private final Either<BookHoldFailed, BookPlacedOnHoldEvents> result =
                regularPatronWithHolds(5).placeOnHold(book, closeEnded(3));

            @Test
            @DisplayName("then the hold should fail")
            void holdFails() {
                assertThat(result).isLeft();
            }

            @Test
            @DisplayName("then the failure reason should explain the hold limit")
            void failureReasonExplainsLimit() {
                assertThat(result).isLeftSatisfying(failure ->
                    assertThat(failure.getReason()).contains("cannot hold more books")
                );
            }
        }
    }
}
```

### Flat Style for Simple Unit Tests

For simpler cases, `@DisplayName` alone is enough — no nesting required:

```java
class BookReturningTest {

    @Test
    @DisplayName("should make a book available after it is returned from hold")
    void shouldMakeBookAvailableAfterReturnFromHold() {
        PatronId patron = anyPatron();
        BookOnHold onHold = bookOnHold(heldBy(patron));

        AvailableBook available = onHold.returnBook(patron);

        assertThat(available).isAvailable().isAtBranch(onHold.getHoldPlacedAt());
    }

    @Test
    @DisplayName("should preserve the book ID after return")
    void shouldPreserveBookIdAfterReturn() {
        BookOnHold onHold = bookOnHold();

        AvailableBook available = onHold.returnBook(anyPatron());

        assertThat(available.getBookId()).isEqualTo(onHold.getBookId());
    }
}
```

## Custom AssertJ Assertions — The Domain DSL

### Base Pattern: Extending `AbstractAssert`

Create an assertion class for each core domain type. This is the Java equivalent of Kotest's custom `Matcher<T>` and infix extension functions:

```java
// The assertion class — one per aggregate/value object
public class BookAssert extends AbstractAssert<BookAssert, Book> {

    private BookAssert(Book book) {
        super(book, BookAssert.class);
    }

    // Entry point — mirrors AssertJ's assertThat(X)
    public static BookAssert assertThat(Book book) {
        return new BookAssert(book);
    }

    public BookAssert isAvailable() {
        isNotNull();
        if (!(actual instanceof AvailableBook)) {
            failWithMessage(
                "Expected book <%s> to be available but it was <%s>",
                actual.getBookId(), actual.getClass().getSimpleName()
            );
        }
        return this;
    }

    public BookAssert isOnHold() {
        isNotNull();
        if (!(actual instanceof BookOnHold)) {
            failWithMessage("Expected book to be on hold but was <%s>", actual.getClass().getSimpleName());
        }
        return this;
    }

    public BookAssert isHeldBy(PatronId patron) {
        isOnHold();
        BookOnHold onHold = (BookOnHold) actual;
        if (!onHold.getByPatron().equals(patron)) {
            failWithMessage(
                "Expected book to be held by <%s> but was held by <%s>",
                patron, onHold.getByPatron()
            );
        }
        return this;
    }

    public BookAssert isAtBranch(LibraryBranchId branch) {
        isNotNull();
        if (!actual.getLibraryBranch().equals(branch)) {
            failWithMessage(
                "Expected book to be at branch <%s> but was at <%s>",
                branch, actual.getLibraryBranch()
            );
        }
        return this;
    }
}
```

### Assertion for Functional Types (Either)

```java
public class HoldResultAssert extends AbstractAssert<HoldResultAssert, Either<BookHoldFailed, BookPlacedOnHoldEvents>> {

    private HoldResultAssert(Either<BookHoldFailed, BookPlacedOnHoldEvents> result) {
        super(result, HoldResultAssert.class);
    }

    public static HoldResultAssert assertThatHoldResult(Either<BookHoldFailed, BookPlacedOnHoldEvents> result) {
        return new HoldResultAssert(result);
    }

    public HoldResultAssert isSuccessful() {
        isNotNull();
        if (actual.isLeft()) {
            failWithMessage(
                "Expected hold to succeed but it failed with: <%s>",
                actual.getLeft().getReason()
            );
        }
        return this;
    }

    public HoldResultAssert isFailed() {
        isNotNull();
        if (actual.isRight()) {
            failWithMessage("Expected hold to fail but it succeeded");
        }
        return this;
    }

    public HoldResultAssert hasFailureReasonContaining(String text) {
        isFailed();
        String reason = actual.getLeft().getReason();
        if (!reason.contains(text)) {
            failWithMessage(
                "Expected failure reason to contain <%s> but was <%s>", text, reason
            );
        }
        return this;
    }

    public HoldResultAssert emitsExactly(int count) {
        isSuccessful();
        int actual = this.actual.get().size();
        if (actual != count) {
            failWithMessage("Expected <%d> events but got <%d>", count, actual);
        }
        return this;
    }
}
```

### Centralised Assertions Entry Point

Provide a single import point for all domain assertions — replaces multiple `import static` calls:

```java
public class LendingAssertions extends Assertions {

    // Domain assertion entry points alongside standard AssertJ
    public static BookAssert assertThat(Book book) {
        return BookAssert.assertThat(book);
    }

    public static HoldResultAssert assertThatHoldResult(
            Either<BookHoldFailed, BookPlacedOnHoldEvents> result) {
        return HoldResultAssert.assertThatHoldResult(result);
    }

    public static PatronAssert assertThat(Patron patron) {
        return PatronAssert.assertThat(patron);
    }
}

// In tests — single import covers everything:
import static io.pillopl.library.lending.LendingAssertions.*;

assertThat(book).isAvailable().isAtBranch(branch);
assertThatHoldResult(result).isSuccessful().emitsExactly(1);
```

## Fixture Classes — Object Mother + Fluent Builder

### Object Mother Pattern

Static factory methods with sensible defaults — the Java equivalent of Kotlin's `object Fixtures`:

```java
public class BookFixture {

    // any*() — random IDs, no significance
    public static BookId anyBookId() {
        return new BookId(UUID.randomUUID());
    }

    public static Version version0() {
        return new Version(0);
    }

    // Named default objects
    public static AvailableBook circulatingAvailableBook() {
        return new AvailableBook(
            new BookInformation(anyBookId(), Circulating),
            anyBranch(),
            version0()
        );
    }

    // Parameterised for specific scenarios
    public static AvailableBook circulatingAvailableBookAt(LibraryBranchId branch) {
        return new AvailableBook(
            new BookInformation(anyBookId(), Circulating),
            branch,
            version0()
        );
    }

    public static BookOnHold bookOnHold() {
        return new BookOnHold(
            new BookInformation(anyBookId(), Circulating),
            anyBranch(),
            anyPatronId(),
            Instant.now(),
            version0()
        );
    }

    public static BookOnHold bookOnHold(PatronId patron) {
        return new BookOnHold(
            new BookInformation(anyBookId(), Circulating),
            anyBranch(),
            patron,
            Instant.now(),
            version0()
        );
    }

    private static PatronId anyPatronId() {
        return new PatronId(UUID.randomUUID());
    }
}
```

### Test Data Builder Pattern

When Object Mother isn't flexible enough — combine with a fluent builder for targeted variation:

```java
public class BookBuilder {

    private BookId bookId = anyBookId();
    private LibraryBranchId branch = anyBranch();
    private PatronId patron = anyPatronId();
    private BookType type = Circulating;
    private Version version = version0();

    // Static entry point — reads like natural language
    public static BookBuilder aCirculatingBook() {
        return new BookBuilder();
    }

    public static BookBuilder aRestrictedBook() {
        return new BookBuilder().ofType(Restricted);
    }

    // Fluent setters — each returns `this` for chaining
    public BookBuilder withId(BookId bookId) {
        this.bookId = bookId;
        return this;
    }

    public BookBuilder locatedAt(LibraryBranchId branch) {
        this.branch = branch;
        return this;
    }

    public BookBuilder heldBy(PatronId patron) {
        this.patron = patron;
        return this;
    }

    public BookBuilder ofType(BookType type) {
        this.type = type;
        return this;
    }

    // Terminal builders — create the domain object in a specific state
    public AvailableBook available() {
        return new AvailableBook(new BookInformation(bookId, type), branch, version);
    }

    public BookOnHold onHold() {
        return new BookOnHold(new BookInformation(bookId, type), branch, patron, Instant.now(), version);
    }

    public CheckedOutBook checkedOut() {
        return new CheckedOutBook(new BookInformation(bookId, type), branch, patron, version);
    }
}

// Usage in tests — reads like a specification:
AvailableBook book = aCirculatingBook()
    .withId(specificBookId)
    .locatedAt(mainBranch)
    .available();

BookOnHold holdAtBranch = aCirculatingBook()
    .locatedAt(specificBranch)
    .heldBy(specificPatron)
    .onHold();
```

### Combining Object Mother + Builder (Best of Both)

Object Mother returns builders (not objects), allowing one-line defaults with easy customisation:

```java
public class BookFixture {

    // Returns builder for flexible customisation
    public static BookBuilder aCirculatingBook() {
        return BookBuilder.aCirculatingBook();
    }

    // Still keep shortcut methods for the most common case
    public static AvailableBook circulatingAvailableBook() {
        return aCirculatingBook().available();
    }
}

// In tests:
AvailableBook defaultBook  = circulatingAvailableBook();                          // zero config
AvailableBook specificBook = aCirculatingBook().locatedAt(mainBranch).available(); // targeted change
```

## Parameterised Tests — Replacing Spock's `where:` Block

### `@MethodSource` for Data Tables

```java
@DisplayName("a regular patron's hold limit")
class PatronHoldLimitTest {

    @ParameterizedTest(name = "can hold when existing holds = {0}")
    @MethodSource("holdsUnderLimit")
    @DisplayName("can place a hold when under the 5-book limit")
    void canHoldWhenUnderLimit(int existingHolds) {
        Either<BookHoldFailed, BookPlacedOnHoldEvents> result =
            regularPatronWithHolds(existingHolds).placeOnHold(circulatingBook(), closeEnded(3));

        assertThat(result).isRight();
    }

    @ParameterizedTest(name = "cannot hold when existing holds = {0}")
    @MethodSource("holdsAtOrOverLimit")
    @DisplayName("cannot place a hold when at or over the 5-book limit")
    void cannotHoldAtOrOverLimit(int existingHolds) {
        Either<BookHoldFailed, BookPlacedOnHoldEvents> result =
            regularPatronWithHolds(existingHolds).placeOnHold(circulatingBook(), closeEnded(3));

        assertThat(result).isLeft();
    }

    static Stream<Integer> holdsUnderLimit() {
        return Stream.of(0, 1, 2, 3, 4);
    }

    static Stream<Integer> holdsAtOrOverLimit() {
        return Stream.of(5, 6, 3000);
    }
}
```

### `@MethodSource` with Multi-Column Data (Records as Rows)

```java
record HoldScenario(int holds, boolean canHold, String description) {}

@ParameterizedTest(name = "{2}")
@MethodSource("holdScenarios")
@DisplayName("hold limit scenarios for regular patron")
void holdLimitScenarios(int holds, boolean canHold, String description) {
    var result = regularPatronWithHolds(holds).placeOnHold(circulatingBook(), closeEnded(3));
    assertThat(result.isRight()).isEqualTo(canHold);
}

static Stream<HoldScenario> holdScenarios() {
    return Stream.of(
        new HoldScenario(0,    true,  "can hold with 0 existing holds"),
        new HoldScenario(4,    true,  "can hold at boundary (4 holds)"),
        new HoldScenario(5,    false, "cannot hold at limit (5 holds)"),
        new HoldScenario(3000, false, "cannot hold when far over limit")
    );
}
```

### `@CsvSource` for Simple Tables

```java
@ParameterizedTest(name = "{0} days hold duration → valid: {1}")
@CsvSource({
    "1,  true",
    "7,  true",
    "60, true",
    "61, false",
    "0,  false"
})
@DisplayName("hold duration validity")
void holdDurationValidity(int days, boolean expected) {
    assertThat(HoldDuration.closeEnded(days).isValid()).isEqualTo(expected);
}
```

## Static Imports Strategy

Organise static imports by role — in Java, this replaces Spock's implicit DSL scope:

```java
// Custom assertions entry point (single import covers all domain types)
import static io.pillopl.library.lending.LendingAssertions.*;

// Object Mother / fixture factories
import static io.pillopl.library.lending.book.model.BookFixture.anyBookId;
import static io.pillopl.library.lending.book.model.BookFixture.circulatingAvailableBook;
import static io.pillopl.library.lending.book.model.BookFixture.bookOnHold;
import static io.pillopl.library.lending.book.model.BookBuilder.aCirculatingBook;
import static io.pillopl.library.lending.librarybranch.model.LibraryBranchFixture.anyBranch;
import static io.pillopl.library.lending.patron.model.PatronFixture.anyPatron;
import static io.pillopl.library.lending.patron.model.PatronFixture.regularPatronWithHolds;

// Domain value objects
import static io.pillopl.library.catalogue.BookType.Circulating;
import static io.pillopl.library.catalogue.BookType.Restricted;
import static io.pillopl.library.lending.patron.model.HoldDuration.closeEnded;
```

## Test Naming Conventions

- **Test class**: `[Aggregate][Behaviour]Test` — `BookPlacingOnHoldTest`, `PatronHoldLimitTest`
- **`@Nested` class** (`@DisplayName`): condition sentence — `"given a circulating book that is available"`, `"when the patron is at the hold limit"`
- **`@Test` method** (`@DisplayName`): outcome sentence — `"then a BookPlacedOnHold event should be emitted"`
- **`@ParameterizedTest` name**: include the varying parameter — `"cannot hold when existing holds = {0}"`
- **Method name** (fallback): `shouldXxxWhenYyy` — `shouldFailWhenPatronAtHoldLimit`

## Implementation Checklist

When adding tests for a new domain aggregate:

- [ ] Create `[Aggregate]Fixture.java` in test package
  - [ ] `any[Entity]()` static methods for random IDs/values
  - [ ] Static factory methods with defaults (e.g., `circulatingAvailableBook()`)
  - [ ] Overloads for common specific scenarios
  - [ ] Methods that return builders (`aCirculatingBook()` → `BookBuilder`)

- [ ] Create `[Aggregate]Builder.java` (the Test Data Builder)
  - [ ] Static named constructor(s) expressing intent (e.g., `aCirculatingBook()`)
  - [ ] Fluent `with*()` / `located*()` methods returning `this`
  - [ ] Terminal builder methods per state (`available()`, `onHold()`, `checkedOut()`)

- [ ] Create `[Aggregate]Assert.java` (extends `AbstractAssert`)
  - [ ] Domain-specific assertion methods with failure messages in ubiquitous language
  - [ ] Chaining (each method returns `this`)
  - [ ] Register in central `[BoundedContext]Assertions` entry-point class

- [ ] Create test classes per behaviour group
  - [ ] `@DisplayName` on the class describing the aggregate/feature
  - [ ] `@Nested` + `@DisplayName` for Given/When grouping
  - [ ] `@Test` + `@DisplayName` for Then outcomes
  - [ ] `@ParameterizedTest` + `@MethodSource` for data-driven scenarios

## Anti-Patterns to Avoid

1. **Don't use `assertEquals` / `assertTrue`** — AssertJ's messages are far more readable on failure
2. **Don't skip `@DisplayName`** — method names like `test1` or `shouldWork` convey nothing
3. **Don't nest more than 3 levels** — Given → When → Then is the maximum useful depth
4. **Don't put setup in `@BeforeEach` when it varies** — put it in each nested class so it's visible
5. **Don't share mutable state across `@Nested` siblings** — each nested class owns its setup
6. **Don't let builders leak into production code** — builders live in `src/test` only
7. **Don't repeat fixture logic in test bodies** — if you call `new X(UUID.randomUUID(), ...)` twice, extract to a fixture method

## Dependencies

```kotlin
// build.gradle.kts
testImplementation("org.junit.jupiter:junit-jupiter:5.11.x")
testImplementation("org.assertj:assertj-core:3.26.x")
testImplementation("org.mockito:mockito-junit-jupiter:5.x")   // or Mockito-Kotlin for mixed projects

// For parameterised tests
testImplementation("org.junit.jupiter:junit-jupiter-params:5.11.x")
```

```xml
<!-- Maven -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.11.x</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>3.26.x</version>
    <scope>test</scope>
</dependency>
```
