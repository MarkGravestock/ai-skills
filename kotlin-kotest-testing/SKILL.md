---
name: kotlin-kotest-testing
description: Write Kotlin/Kotest tests using BDD-style specs, custom matcher DSLs, data-driven testing, and test data builders. Use when writing tests for domain aggregates in Kotlin, creating test DSLs with infix functions and lambda receivers, implementing fixture factories, or working with Kotest specifications in DDD contexts. Particularly relevant for Kotlin projects using Kotest, domain-driven design, event-sourced architectures, or functional types (Arrow, Vavr).
---

# Kotlin/Kotest Testing with DSL and Fixtures

Write Kotlin/Kotest tests following patterns that mirror the expressiveness of Groovy/Spock, leveraging Kotlin's native language features: infix functions, lambda-with-receiver, extension functions, and data classes.

## Core Principles

1. **Readable Tests**: Tests should read like specifications using Kotlin's DSL capabilities
2. **BehaviorSpec for BDD**: Use `given/when/then` blocks for domain behaviour tests
3. **Fixtures via Companion Objects**: Factory methods in companion objects with sensible defaults
4. **Custom Matchers as DSL**: Build domain-specific assertion vocabulary with infix extensions
5. **Data Classes for Immutable Builders**: Use `copy()` for expressive test data construction
6. **Infix Functions for Natural Language**: Chain conditions and assertions like prose

## Test Structure Pattern

### BehaviorSpec — BDD Given/When/Then

The closest Kotlin/Kotest equivalent to Spock's `given:/when:/then:` blocks:

```kotlin
package io.pillopl.library.lending.book.model

import io.kotest.core.spec.style.BehaviorSpec
import io.kotest.matchers.shouldBe
import io.pillopl.library.lending.book.model.BookFixtures.anyBookId
import io.pillopl.library.lending.book.model.BookFixtures.anyBranch
import io.pillopl.library.lending.patron.model.PatronFixtures.anyPatron
import io.pillopl.library.lending.patron.model.PatronFixtures.regularPatronWithHolds

class BookPlacingOnHoldTest : BehaviorSpec({

    given("a circulating book that is available") {
        val book = circulatingAvailableBook()

        and("a regular patron with no holds") {
            val patron = regularPatronWithHolds(0)

            `when`("the patron places the book on hold") {
                val result = patron.placeOnHold(book, closeEnded(3))

                then("the hold should succeed") {
                    result.isRight() shouldBe true
                }

                then("a BookPlacedOnHold event should be raised") {
                    val events = result.get()
                    events shouldHaveSize 1
                }
            }
        }

        and("a regular patron who already has 5 holds") {
            val patron = regularPatronWithHolds(5)

            `when`("the patron tries to place another hold") {
                val result = patron.placeOnHold(book, closeEnded(3))

                then("the hold should fail") {
                    result.isLeft() shouldBe true
                }

                then("the failure reason should explain the limit") {
                    result.getLeft().reason shouldContain "cannot hold more books"
                }
            }
        }
    }
})
```

> **Note:** `when` is a Kotlin keyword — use backticks `` `when` `` or the capitalised alias `When`.

### FunSpec with Context Blocks — Lightweight Alternative

When BDD ceremony is too heavy, `FunSpec` with `context` is clean and fast:

```kotlin
class BookReturningTest : FunSpec({

    context("returning a book that is on hold") {
        val patron = anyPatron()
        val book = circulatingBookOnHold(heldBy = patron)

        test("should make the book available again") {
            val result = patron.returnBook(book)
            result.isRight() shouldBe true
            result.get().book.shouldBeAvailable()
        }
    }

    context("returning a book that was not checked out") {
        test("should fail with a meaningful error") {
            val book = circulatingAvailableBook()
            val result = anyPatron().returnBook(book)
            result.isLeft() shouldBe true
        }
    }
})
```

### DescribeSpec — For Hierarchical Domain Rules

```kotlin
class PatronHoldLimitTest : DescribeSpec({

    describe("a regular patron") {
        describe("hold limit enforcement") {
            it("can place a hold when under the limit of 5") {
                regularPatronWithHolds(4).placeOnHold(circulatingBook()).isRight() shouldBe true
            }

            it("cannot place a hold when at the limit of 5") {
                regularPatronWithHolds(5).placeOnHold(circulatingBook()).isLeft() shouldBe true
            }

            it("cannot place a hold when over the limit") {
                regularPatronWithHolds(6).placeOnHold(circulatingBook()).isLeft() shouldBe true
            }
        }
    }

    describe("a researcher patron") {
        it("can hold unlimited books") {
            researcherPatronWithHolds(100).placeOnHold(circulatingBook()).isRight() shouldBe true
        }
    }
})
```

## Building Test DSLs in Kotlin

### Infix Functions for Natural-Language Test Setup

Kotlin infix functions allow `subject verb object` syntax, directly analogous to Spock DSL chaining:

```kotlin
// Spock: the book isPlacedOnHoldBy patron at branch from now till later
// Kotlin: book isPlacedOnHoldBy patron at branch from Instant.now() till oneHourLater()

data class BookDsl(
    val bookId: BookId = anyBookId(),
    val branchId: LibraryBranchId = anyBranch(),
    val patronId: PatronId? = null,
    val bookState: BookState = BookState.AVAILABLE
) {
    infix fun isPlacedOnHoldBy(patron: PatronId): HoldDsl =
        HoldDsl(book = this, patronId = patron)

    fun build(): Book = when (bookState) {
        BookState.AVAILABLE -> AvailableBook(BookInformation(bookId, Circulating), branchId, version0())
        BookState.ON_HOLD   -> BookOnHold(BookInformation(bookId, Circulating), branchId, patronId!!, Instant.now(), version0())
        BookState.CHECKED_OUT -> CheckedOutBook(BookInformation(bookId, Circulating), branchId, patronId!!, version0())
    }
}

data class HoldDsl(
    val book: BookDsl,
    val patronId: PatronId,
    val branchId: LibraryBranchId = anyBranch(),
    val from: Instant = Instant.now()
) {
    infix fun at(branch: LibraryBranchId): HoldDsl = copy(branchId = branch)
    infix fun from(instant: Instant): HoldDsl = copy(from = instant)

    infix fun till(till: Instant): BookPlacedOnHold =
        BookPlacedOnHold(
            eventDate = Instant.now(),
            patronId = patronId.patronId,
            bookId = book.bookId.bookId,
            bookType = Circulating,
            libraryBranchId = branchId.libraryBranchId,
            holdFrom = from,
            holdTill = till
        )
}

// Usage in tests:
val event = book isPlacedOnHoldBy patron at branch from Instant.now() till oneHourLater()
```

### Lambda-with-Receiver Builders

For complex domain object setup, lambda-with-receiver gives a clean block syntax:

```kotlin
class BookDslBuilder {
    var bookId: BookId = anyBookId()
    var branchId: LibraryBranchId = anyBranch()
    var patronId: PatronId = anyPatron()
    var bookType: BookType = Circulating

    fun available(): AvailableBook =
        AvailableBook(BookInformation(bookId, bookType), branchId, version0())

    fun onHold(): BookOnHold =
        BookOnHold(BookInformation(bookId, bookType), branchId, patronId, Instant.now(), version0())
}

fun aBook(init: BookDslBuilder.() -> Unit = {}): BookDslBuilder =
    BookDslBuilder().apply(init)

// Usage:
val book = aBook {
    bookId = anyBookId()
    branchId = specificBranch
    bookType = Restricted
}.available()
```

### Extension Functions as Domain Assertions

Add custom assertion vocabulary directly on domain types:

```kotlin
// Custom infix assertion extension
infix fun <L, R> Either<L, R>.shouldBeRightContaining(check: (R) -> Unit) {
    this.isRight() shouldBe true
    check(this.get())
}

infix fun <L, R> Either<L, R>.shouldBeLeftWith(check: (L) -> Unit) {
    this.isLeft() shouldBe true
    check(this.getLeft())
}

fun Book.shouldBeAvailable() = this.shouldBeInstanceOf<AvailableBook>()
fun Book.shouldBeOnHold() = this.shouldBeInstanceOf<BookOnHold>()
fun Book.shouldBeCheckedOut() = this.shouldBeInstanceOf<CheckedOutBook>()

// Usage reads cleanly in tests:
result shouldBeRightContaining { events ->
    events shouldHaveSize 1
    events.first().shouldBeInstanceOf<BookPlacedOnHold>()
}

result shouldBeLeftWith { failure ->
    failure.reason shouldContain "cannot hold more books"
}

the(book).reactsTo(event).shouldBeAvailable()
```

## Custom Matcher DSL

### Implementing `Matcher<T>` Interface

```kotlin
import io.kotest.matchers.Matcher
import io.kotest.matchers.MatcherResult
import io.kotest.matchers.should
import io.kotest.matchers.shouldNot

// Define the matcher
fun beAvailable() = Matcher<Book> { book ->
    MatcherResult(
        book is AvailableBook,
        { "Book was expected to be available but was ${book::class.simpleName}" },
        { "Book was not expected to be available" }
    )
}

fun beHeldBy(patron: PatronId) = Matcher<Book> { book ->
    val held = book is BookOnHold && (book as BookOnHold).byPatron == patron
    MatcherResult(
        held,
        { "Book was expected to be held by $patron but was ${book::class.simpleName}" },
        { "Book was not expected to be held by $patron" }
    )
}

// Extension infix functions for clean usage
infix fun Book.shouldBeHeldBy(patron: PatronId) = this should beHeldBy(patron)
infix fun Book.shouldNotBeHeldBy(patron: PatronId) = this shouldNot beHeldBy(patron)
fun Book.shouldBeAvailable() = this should beAvailable()

// Composed matchers
fun beValidHoldResult() = Matcher<Either<BookHoldFailed, BookPlacedOnHoldEvents>> { result ->
    MatcherResult(
        result.isRight(),
        { "Expected successful hold but got failure: ${result.getLeft()}" },
        { "Expected failed hold" }
    )
}
```

### Custom Assertions Entry Point

Create a project-wide assertions object (analogous to static imports in the Spock skill):

```kotlin
object BookAssertions {
    fun assertThat(book: Book) = BookAssert(book)
    fun assertThat(result: Either<BookHoldFailed, BookPlacedOnHoldEvents>) = HoldResultAssert(result)
}

class BookAssert(private val book: Book) {
    fun isAvailable(): BookAssert {
        book.shouldBeAvailable()
        return this
    }
    fun isHeldBy(patron: PatronId): BookAssert {
        book shouldBeHeldBy patron
        return this
    }
    fun isAtBranch(branch: LibraryBranchId): BookAssert {
        book.holdPlacedAt shouldBe branch
        return this
    }
}
```

## Fixture Classes

### Companion Object Pattern (Kotlin equivalent of Java fixture classes)

```kotlin
object BookFixtures {
    fun anyBookId(): BookId = BookId(UUID.randomUUID())
    fun anyBranch(): LibraryBranchId = LibraryBranchId(UUID.randomUUID())
    fun version0(): Version = Version(0)

    fun circulatingAvailableBook(): AvailableBook =
        AvailableBook(BookInformation(anyBookId(), Circulating), anyBranch(), version0())

    fun circulatingAvailableBookAt(branch: LibraryBranchId): AvailableBook =
        AvailableBook(BookInformation(anyBookId(), Circulating), branch, version0())

    fun circulatingAvailableBook(bookId: BookId, branch: LibraryBranchId): AvailableBook =
        AvailableBook(BookInformation(bookId, Circulating), branch, version0())

    fun bookOnHold(
        bookId: BookId = anyBookId(),
        branch: LibraryBranchId = anyBranch(),
        patron: PatronId = PatronFixtures.anyPatron()
    ): BookOnHold =
        BookOnHold(BookInformation(bookId, Circulating), branch, patron, Instant.now(), version0())
}

object PatronFixtures {
    fun anyPatron(): PatronId = PatronId(UUID.randomUUID())

    fun regularPatronWithHolds(numberOfHolds: Int): Patron =
        Patron(PatronInformation(anyPatron(), Regular), holds(numberOfHolds), emptySet())

    fun researcherPatron(): Patron =
        Patron(PatronInformation(anyPatron(), Researcher), emptySet(), emptySet())

    private fun holds(count: Int): Set<Hold> =
        (1..count).map { Hold(anyBookId(), anyBranch()) }.toSet()
}
```

### Data Classes with `copy()` for Targeted Variation

Kotlin `data class` + `copy()` is the cleanest way to express "default object, but with this one thing different":

```kotlin
val defaultBook = circulatingAvailableBook()

// Test with a specific branch — only change what matters
val bookAtSpecificBranch = defaultBook.copy(libraryBranch = mainBranch)

// Test data class as fixture root
data class PlaceOnHoldScenario(
    val patron: Patron = regularPatronWithHolds(0),
    val book: AvailableBook = circulatingAvailableBook(),
    val duration: HoldDuration = closeEnded(3)
)

// Each test customises only what it cares about
val overLimitScenario = PlaceOnHoldScenario(patron = regularPatronWithHolds(5))
val researcherScenario = PlaceOnHoldScenario(patron = researcherPatron())
```

## Data-Driven Testing

### `withData` — Kotest's Equivalent of Spock's `where:` Block

```kotlin
data class HoldLimitTestCase(
    val holds: Int,
    val expectSuccess: Boolean,
    val description: String
) : WithDataTestName {
    override fun dataTestName() = description
}

class PatronHoldLimitDataTest : FunSpec({

    context("regular patron hold limit") {
        withData(
            HoldLimitTestCase(0,    true,  "can hold with 0 existing holds"),
            HoldLimitTestCase(1,    true,  "can hold with 1 existing hold"),
            HoldLimitTestCase(4,    true,  "can hold at limit boundary (4)"),
            HoldLimitTestCase(5,    false, "cannot hold at limit (5)"),
            HoldLimitTestCase(6,    false, "cannot hold when over limit (6)"),
            HoldLimitTestCase(3000, false, "cannot hold with absurdly many holds")
        ) { (holds, expectSuccess, _) ->
            val result = regularPatronWithHolds(holds).placeOnHold(circulatingBook())
            result.isRight() shouldBe expectSuccess
        }
    }
})
```

### Combining BehaviorSpec + Data-Driven

```kotlin
class BookTypeHoldRulesTest : BehaviorSpec({

    given("a restricted book") {
        val book = restrictedBook()

        `when`("different patron types try to place it on hold") {
            withData(
                nameFn = { (patronType, _) -> "a $patronType patron" },
                RegularPatron to false,
                ResearcherPatron to true
            ) { (patronType, canHold) ->
                then("${if (canHold) "succeeds" else "fails"}") {
                    val result = patronOf(patronType).placeOnHold(book)
                    result.isRight() shouldBe canHold
                }
            }
        }
    }
})
```

## Common Patterns

### Pattern 1: Arrange with Infix DSL

```kotlin
// Spock equivalent: aCirculatingBook() with anyBookId() locatedIn anyBranch() stillAvailable()
val book = aBook {
    bookId = anyBookId()
    branchId = anyBranch()
}.available()

// Or with infix:
val holdEvent = book isPlacedOnHoldBy patron at branch from Instant.now() till oneHourLater()
```

### Pattern 2: Domain Extension Assertions

```kotlin
// Instead of: result.isRight() shouldBe true; result.get().size shouldBe 1
result shouldBeRightContaining { events ->
    events shouldHaveSize 1
    events.first() shouldBeInstanceOf BookPlacedOnHold::class
}
```

### Pattern 3: Direct Fixtures When DSL Is Overkill

```kotlin
// Simple case — no need for a DSL
given("a circulating book") {
    val book = circulatingAvailableBook()
    val patron = regularPatronWithHolds(4)
    `when`("patron places a hold") {
        val result = patron.placeOnHold(book, closeEnded(3))
        then("it succeeds") { result.isRight() shouldBe true }
    }
}
```

### Pattern 4: Coroutine-Aware Tests

Kotest has first-class coroutine support — use `BehaviorSpec` or `FunSpec` with `suspend` test bodies:

```kotlin
class AsyncBookReservationTest : FunSpec({
    test("should reserve book asynchronously") {
        val result = bookService.reserveAsync(anyBookId(), anyPatron())
        result.await() shouldBe ReservationSuccess
    }
})
```

## Imports Strategy

Organise imports by role with blank lines between groups:

```kotlin
// Test framework
import io.kotest.core.spec.style.BehaviorSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.types.shouldBeInstanceOf

// Domain fixture factories (use Kotlin import aliases for clarity)
import io.pillopl.library.lending.book.model.BookFixtures.anyBookId
import io.pillopl.library.lending.book.model.BookFixtures.circulatingAvailableBook
import io.pillopl.library.lending.book.model.BookFixtures.bookOnHold
import io.pillopl.library.lending.patron.model.PatronFixtures.anyPatron
import io.pillopl.library.lending.patron.model.PatronFixtures.regularPatronWithHolds

// Test DSL
import io.pillopl.library.lending.book.model.BookDsl.Companion.aBook
import io.pillopl.library.lending.patron.model.HoldDuration.closeEnded

// Domain events and types
import io.pillopl.library.catalogue.BookType.Circulating
import io.pillopl.library.lending.patron.model.PatronEvent.BookPlacedOnHold
```

## Naming Conventions

- **Test class**: `[Aggregate][Behaviour]Test` — e.g., `BookPlacingOnHoldTest`, `PatronHoldLimitTest`
- **`given`**: noun phrase describing precondition — `"a circulating book that is available"`
- **`` `when` ``**: verb phrase for the action — `"the patron places the book on hold"`
- **`then`**: present-tense outcome — `"a BookPlacedOnHold event is emitted"`
- **`context`** (FunSpec): short noun or noun phrase — `"returning a checked-out book"`
- **`test`** (FunSpec): full behaviour sentence — `"should make the book available after return"`

## Implementation Checklist

When adding tests for a new domain aggregate:

- [ ] Create `[Aggregate]Fixtures.kt` in test package
  - [ ] `any[Entity]()` functions returning random IDs
  - [ ] Default factory functions (e.g., `circulatingAvailableBook()`)
  - [ ] Parameterised factory functions for specific scenarios
  - [ ] Group in `object [Aggregate]Fixtures` for clean import style

- [ ] Create `[Aggregate]Dsl.kt` (optional — for complex setup chains)
  - [ ] `data class` with infix functions for action chains
  - [ ] Lambda-with-receiver builder function (`fun aBook(init: BookDslBuilder.() -> Unit)`)
  - [ ] Extension assertion functions (e.g., `fun Book.shouldBeAvailable()`)
  - [ ] Custom `Matcher<T>` implementations for composed assertions

- [ ] Create test spec classes per behaviour group
  - [ ] Choose spec style: `BehaviorSpec` for DDD/BDD, `FunSpec` for simple unit tests
  - [ ] Use `withData` for parameterised table-style tests
  - [ ] Use `DescribeSpec` for hierarchical domain rule documentation

## Anti-Patterns to Avoid

1. **Don't use Java fixture classes in Kotlin tests** — Kotlin `object` + `companion object` is cleaner
2. **Don't force BehaviorSpec everywhere** — `FunSpec` is fine for simple unit tests
3. **Don't overload infix functions** — if the chain becomes hard to parse, use named parameters
4. **Don't skip `WithDataTestName`** — test names from `toString()` are often unreadable in CI output
5. **Don't mix fixture creation in test bodies** — push all construction into fixture functions
6. **Don't test implementation** — assert on emitted events and returned domain objects, not internal state

## Dependencies

```kotlin
// build.gradle.kts
testImplementation("io.kotest:kotest-runner-junit5:5.9.x")
testImplementation("io.kotest:kotest-assertions-core:5.9.x")
testImplementation("io.kotest:kotest-framework-datatest:5.9.x")
testImplementation("io.kotest:kotest-property:5.9.x")   // optional: property-based testing
testImplementation("io.mockk:mockk:1.13.x")              // mocking
```

```kotlin
// src/test/resources/kotest.properties
kotest.framework.parallelism=4
```
