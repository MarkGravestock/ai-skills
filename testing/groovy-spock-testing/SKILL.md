---
name: groovy-spock-testing
description: Write Groovy/Spock integration tests using DSL patterns and fixture classes. Use when writing tests for domain aggregates, creating test DSLs with fluent builders, implementing fixture factories, or working with Spock specifications in DDD contexts. Particularly relevant for projects using Groovy, Spock Framework, JUnit testing, or event-sourced architectures.
---

# Groovy/Spock Integration Testing with DSL and Fixtures

Write Groovy/Spock integration tests following the patterns established in this project, with emphasis on domain-driven design (DDD), test DSLs, and fixture-based test data creation.

## Core Principles

1. **Readable Tests**: Tests should read like specifications using fluent DSL methods
2. **Given-When-Then**: Always use Spock's BDD-style blocks for clear test structure
3. **Fixtures for Defaults**: Use fixture classes to provide sensible defaults and reduce test noise
4. **DSL for Scenarios**: Build test DSLs that express domain scenarios in natural language
5. **Static Imports**: Leverage static imports extensively for maximum readability

## Test Structure Pattern

### Basic Spock Test Template

```groovy
package io.pillopl.library.lending.book.model

import spock.lang.Specification

import static BookDSL.aCirculatingBook
import static BookDSL.the
import static io.pillopl.library.lending.book.model.BookFixture.anyBookId
import static io.pillopl.library.lending.librarybranch.model.LibraryBranchFixture.anyBranch
import static io.pillopl.library.lending.patron.model.PatronFixture.anyPatron

class BookPlacingOnHoldTest extends Specification {

    def 'should place on hold book which is marked as available in the system'() {
        given:
            BookDSL availableBook = aCirculatingBook() with anyBookId() locatedIn anyBranch() stillAvailable()

        and:
            PatronId aPatron = anyPatron()

        and:
            LibraryBranchId aBranch = anyBranch()

        and:
            PatronEvent.BookPlacedOnHold bookPlacedOnHoldEvent = the availableBook isPlacedOnHoldBy aPatron at aBranch from now till oneHourLater

        when:
            BookOnHold onHold = the availableBook reactsTo bookPlacedOnHoldEvent

        then:
            onHold.bookId == availableBook.bookId
            onHold.byPatron == aPatron
            onHold.holdTill == oneHourLater
            onHold.holdPlacedAt == aBranch
            onHold.version == availableBook.version
    }
}
```

### Key Elements

- **Class**: Extends `Specification` from Spock
- **Test Method**: Descriptive method name with `def 'natural language description'()`
- **Blocks**: Use `given:`, `and:`, `when:`, `then:` for BDD structure
- **Static Imports**: Import DSL methods and fixture factory methods statically

## Building Test DSLs

### DSL Class Pattern

Create a fluent builder-style DSL class for your domain aggregate:

```groovy
class BookDSL {
    BookType bookType
    BookId bookId
    LibraryBranchId libraryBranchId
    PatronId patronId
    Closure<Book> bookProvider
    Version version = version0()

    static BookDSL the(BookDSL book) {
        return book
    }

    static BookDSL aCirculatingBook() {
        return new BookDSL(Circulating)
    }

    BookDSL(BookType type) {
        this.bookType = type
    }

    BookDSL(BookDSL from) {
        this.bookType = from.bookType
        this.bookId = from.bookId
        this.libraryBranchId = from.libraryBranchId
        this.patronId = from.patronId
        this.bookProvider = from.bookProvider
        this.version = from.version
    }

    BookDSL with(BookId id) {
        this.bookId = id
        return this
    }

    BookDSL locatedIn(LibraryBranchId libraryBranch) {
        this.libraryBranchId = libraryBranch
        return this
    }

    BookDSL placedOnHoldBy(PatronId aPatron) {
        this.patronId = aPatron
        this.bookProvider = { ->
            new BookOnHold(new BookInformation(bookId, bookType), libraryBranchId, patronId, Instant.now(), version0())
        }
        return this
    }

    BookDSL stillAvailable() {
        bookProvider = { -> new AvailableBook(new BookInformation(bookId, bookType), libraryBranchId, version0()) }
        return this
    }

    BookDSL checkedOutBy(PatronId aPatron) {
        bookProvider = { ->
            new CheckedOutBook(new BookInformation(bookId, bookType), libraryBranchId, aPatron, version0())
        }
        return this
    }

    def isPlacedOnHoldBy(PatronId aPatron) {
        return new BookDSL(this) {
            PatronId onHoldPatronId
            LibraryBranchId placeOnHoldBranchId
            Instant onHoldFrom

            {
                onHoldPatronId = aPatron
                onHoldFrom = Instant.now()
            }

            def at(LibraryBranchId branchId) {
                placeOnHoldBranchId = branchId
                return this
            }

            def from(Instant from) {
                onHoldFrom = from
                return this
            }

            PatronEvent.BookPlacedOnHold till(Instant till) {
                return bookPlacedOnHold(bookProvider(), onHoldPatronId, placeOnHoldBranchId, onHoldFrom, till)
            }
        }
    }

    def isReturnedBy(PatronId aPatron) {
        return new BookDSL(this) {
            PatronEvent.BookReturned at(LibraryBranchId branchId) {
                return bookReturned(bookProvider(), aPatron, branchId)
            }
        }
    }

    Book reactsTo(PatronEvent event) {
        return bookProvider().handle(event)
    }

    private static PatronEvent.BookPlacedOnHold bookPlacedOnHold(Book availableBook, PatronId byPatron, LibraryBranchId libraryBranchId, Instant from, Instant till) {
        return new PatronEvent.BookPlacedOnHold(Instant.now(),
                byPatron.patronId,
                availableBook.getBookId().bookId,
                availableBook.bookInformation.bookType,
                libraryBranchId.libraryBranchId,
                from,
                till)
    }

    private static PatronEvent.BookReturned bookReturned(Book bookCheckedOut, PatronId patronId, LibraryBranchId libraryBranchId) {
        return new PatronEvent.BookReturned(Instant.now(),
                patronId.patronId,
                bookCheckedOut.getBookId().bookId,
                bookCheckedOut.bookInformation.bookType,
                libraryBranchId.libraryBranchId)
    }
}
```

### DSL Design Guidelines

1. **Static Factory Methods**: Start chains with readable factory methods like `aCirculatingBook()`
2. **The Pattern**: Add a `static the(DSL obj)` method for readability: `the book isReturnedBy patron`
3. **Method Chaining**: Each builder method returns `this` for fluent chaining
4. **Copy Constructor**: Implement copy constructor for safe state copying in inner classes
5. **Closure Provider**: Use `Closure<DomainObject>` to defer object creation until needed
6. **Anonymous Inner Classes**: For complex action chains, return anonymous inner classes with continuation methods
7. **Natural Language**: Name methods to read like natural language when chained together
8. **Private Helpers**: Hide event construction details in private methods

## Fixture Classes

### Fixture Class Pattern (Java)

Fixture classes provide factory methods for test data with sensible defaults:

```java
package io.pillopl.library.lending.book.model;

import io.pillopl.library.catalogue.BookId;
import io.pillopl.library.commons.aggregates.Version;
import io.pillopl.library.lending.librarybranch.model.LibraryBranchId;
import io.pillopl.library.lending.patron.model.PatronId;

import java.time.Instant;
import java.util.UUID;

import static io.pillopl.library.catalogue.BookType.Circulating;
import static io.pillopl.library.catalogue.BookType.Restricted;
import static io.pillopl.library.lending.librarybranch.model.LibraryBranchFixture.anyBranch;

public class BookFixture {

    public static BookOnHold bookOnHold(BookId bookId, LibraryBranchId libraryBranchId) {
        return new BookOnHold(new BookInformation(bookId, Circulating), libraryBranchId, anyPatronId(), Instant.now(), version0());
    }

    public static AvailableBook circulatingBook() {
        return new AvailableBook(new BookInformation(anyBookId(), Circulating), anyBranch(), version0());
    }

    public static BookOnHold bookOnHold() {
        return new BookOnHold(new BookInformation(anyBookId(), Circulating), anyBranch(), anyPatronId(), Instant.now(), version0());
    }

    public static AvailableBook circulatingAvailableBookAt(LibraryBranchId libraryBranchId) {
        return new AvailableBook(new BookInformation(anyBookId(), Circulating), libraryBranchId, version0());
    }

    public static AvailableBook circulatingAvailableBookAt(BookId bookId, LibraryBranchId libraryBranchId) {
        return new AvailableBook(new BookInformation(bookId, Circulating), libraryBranchId, version0());
    }

    public static BookId anyBookId() {
        return new BookId(UUID.randomUUID());
    }

    public static Version version0() {
        return new Version(0);
    }

    private static PatronId anyPatronId() {
        return new PatronId(UUID.randomUUID());
    }
}
```

### Fixture Design Guidelines

1. **Use Java**: Fixtures can be Java classes even in Groovy projects for simplicity
2. **Static Methods**: All fixture methods should be static
3. **Any Prefix**: Use `any*()` for random/default ID generation methods
4. **Overloading**: Provide multiple overloads with different specificity levels
5. **Composition**: Fixtures can call other fixtures for dependencies
6. **Defaults**: Always provide sensible defaults that work for most tests
7. **Specificity**: Name methods by what makes them unique (e.g., `circulatingAvailableBookAt()`)

## Spock-Specific Patterns

### Parameterized Tests with `where:` Blocks

```groovy
def 'a regular patron cannot place on hold more than 5 books'() {
    when:
        Either<BookHoldFailed, BookPlacedOnHoldEvents> hold = regularPatronWithHolds(holds).placeOnHold(circulatingBook())
    then:
        hold.isLeft()
        BookHoldFailed e = hold.getLeft()
        e.reason.contains("patron cannot hold more books")
    where:
        holds << [5, 6, 3000]
}

def 'a regular patron can place on hold book when he did not place on hold more than 4 books'() {
    given:
        AvailableBook book = circulatingBook()
    when:
        Either<BookHoldFailed, BookPlacedOnHoldEvents> hold = regularPatronWithHolds(holds).placeOnHold(book, closeEnded(3))
    then:
        hold.isRight()
    where:
        holds << [0, 1, 2, 3, 4]
}

def 'should handle various book configurations'() {
    expect:
        result == expected
    where:
        books                                           || expected
        [anyBookId(), anyBookId()] as Set               || 2
        [anyBookId(), anyBookId(), anyBookId()] as Set  || 3
}
```

### Testing Functional Types (Either, Option, etc.) when a functional library like 'io.vavr' is used

```groovy
def 'should return Left when operation fails'() {
    when:
        Either<BookHoldFailed, BookPlacedOnHoldEvents> result = patron.placeOnHold(book)
    then:
        result.isLeft()
        BookHoldFailed failure = result.getLeft()
        failure.reason.contains("expected failure message")
}

def 'should return Right when operation succeeds'() {
    when:
        Either<BookHoldFailed, BookPlacedOnHoldEvents> result = patron.placeOnHold(book)
    then:
        result.isRight()
        BookPlacedOnHoldEvents events = result.get()
        events.size() > 0
}
```

### Multiple `and:` Blocks for Clarity

Use `and:` blocks to logically group related setup within `given:`:

```groovy
def 'should perform complex operation'() {
    given:
        BookDSL book = aCirculatingBook() with anyBookId() locatedIn anyBranch() stillAvailable()

    and:
        PatronId patron = anyPatron()

    and:
        LibraryBranchId branch = anyBranch()

    and:
        PatronEvent.BookPlacedOnHold event = the book isPlacedOnHoldBy patron at branch from now till later

    when:
        Book result = the book reactsTo event

    then:
        result.bookId == book.bookId
}
```

## Static Imports Strategy

Organize static imports by category with blank lines separating each group:

```groovy
import static BookDSL.aCirculatingBook
import static BookDSL.the

import static io.pillopl.library.lending.book.model.BookFixture.anyBookId
import static io.pillopl.library.lending.book.model.BookFixture.circulatingBook
import static io.pillopl.library.lending.librarybranch.model.LibraryBranchFixture.anyBranch
import static io.pillopl.library.lending.patron.model.PatronFixture.anyPatron
import static io.pillopl.library.lending.patron.model.PatronFixture.regularPatronWithHolds

import static io.pillopl.library.lending.patron.model.HoldDuration.closeEnded

import static PatronEvent.BookHoldFailed
import static PatronEvent.BookPlacedOnHoldEvents

import static java.util.Collections.emptySet
```

Group imports in this order:
1. DSL classes (BookDSL, PatronDSL, etc.)
2. Fixture factory methods
3. Domain value objects and enums
4. Event types
5. Standard library utilities

## Test Naming Conventions

1. **Test Class Names**: `[Aggregate/Feature][Action]Test` (e.g., `BookPlacingOnHoldTest`, `BookReturningTest`)
2. **Test Method Names**: Use `def 'should [expected behavior] when [conditions]'()` or just `def '[business rule description]'()`
3. **Be Descriptive**: Test names should read like specifications

Examples:
- `def 'should place on hold book which is marked as available in the system'()`
- `def 'should return book which is marked as placed on hold in the system'()`
- `def 'a regular patron cannot place on hold more than 5 books'()`
- `def 'a regular patron can place on hold books even though he has 2 overdue checkouts at different library'()`

## Common Patterns

### Pattern 1: Arrange Domain Object with DSL

```groovy
given:
    BookDSL book = aCirculatingBook()
        with anyBookId()
        locatedIn anyBranch()
        checkedOutBy anyPatron()
```

### Pattern 2: Create Event with DSL

```groovy
and:
    PatronEvent.BookReturned event = the book isReturnedBy anyPatron() at anyBranch()
```

### Pattern 3: Execute and Assert

```groovy
when:
    AvailableBook result = the book reactsTo event

then:
    result.bookId == book.bookId
    result.libraryBranch == expectedBranch
```

### Pattern 4: Direct Fixture Usage

When DSL is overkill, use fixtures directly:

```groovy
given:
    AvailableBook book = circulatingBook()
    Patron patron = regularPatronWithHolds(4)

when:
    Either<BookHoldFailed, BookPlacedOnHoldEvents> result = patron.placeOnHold(book, closeEnded(3))

then:
    result.isRight()
```

## Implementation Checklist

When adding tests for a new domain aggregate:

- [ ] Create `[Aggregate]DSL.groovy` in test package
  - [ ] Add static factory method (e.g., `aNewAggregate()`)
  - [ ] Add `the()` helper method
  - [ ] Add fluent builder methods for attributes
  - [ ] Add state setup methods (e.g., `inState()`, `withConfiguration()`)
  - [ ] Add action methods that return anonymous classes for chaining
  - [ ] Add `reactsTo()` or similar execution method
  - [ ] Add private helper methods for event creation

- [ ] Create `[Aggregate]Fixture.java` in test package
  - [ ] Add `any[Attribute]()` methods for random IDs/values
  - [ ] Add factory methods with sensible defaults
  - [ ] Add factory methods with specific configurations
  - [ ] Add methods for common test scenarios

- [ ] Create test classes per behavior
  - [ ] Name class `[Aggregate][Behavior]Test`
  - [ ] Extend `Specification`
  - [ ] Add static imports for DSL and fixtures
  - [ ] Write tests using `given-and-when-then` structure
  - [ ] Use descriptive test method names

## Anti-Patterns to Avoid

1. **Don't Use DSL Everywhere**: If a simple fixture call is clearer, use it
2. **Don't Over-Engineer**: Start simple, add DSL complexity only when tests become hard to read
3. **Don't Repeat Setup**: If multiple tests need the same setup, add a fixture method
4. **Don't Skip Static Imports**: Tests are harder to read without them
5. **Don't Break the Chain**: DSL methods should always return something chainable
6. **Don't Expose Internals**: Fixtures should hide construction complexity
7. **Don't Test Implementation**: Test behavior and outcomes, not internal state

## Integration with Domain-Driven Design

This testing style works particularly well with:

- **Aggregates**: Each aggregate gets its own DSL class
- **Events**: DSL methods create domain events
- **Value Objects**: Fixtures provide value object creation
- **Invariants**: Tests express business rules as specifications
- **Ubiquitous Language**: DSL methods use domain terminology

The test code should read like the business requirements written by domain experts.
