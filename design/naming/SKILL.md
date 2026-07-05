---
name: naming
description: Deep guidance on naming functions, types, and variables - optimize for the calling context, use wishful thinking to derive names before implementations exist, let domain types liberate parameter names, scope-determines-length, and avoid getters/setters, I-prefixes, and dumpster names (Utils/Helper/Manager). Use when naming or renaming any identifier, reviewing code for naming quality, or when "intention-revealing names" guidance from other skills needs concrete technique rather than a banned-words list. Composes with software-design-principles (which enforces the resulting rules) and cupid-properties (Domain-based, Composable).
---

# Naming

Adapted from Adam Tornhill's
[*"An opinionated (and mainly correct) guide to naming things"*](https://adamtornhill.substack.com/p/an-opinionated-and-mainly-correct)
(CodeScene / Substack). Naming is a design activity, not a labelling one: names are a
cognitive compression mechanism — the stronger the names, the more a reader (human or agent)
can hold in working memory while reasoning about the code. Identifier quality measurably
affects debugging time and LLM code comprehension, so this is not aesthetics.

## How this skill composes

`software-design-principles` **enforces** the output of this skill (ban generic names, no
abbreviations, avoid getters/setters) as quick checklist items during construction. This
skill supplies the **technique** for arriving at good names in the first place — load it
when a name needs to be *derived*, not just checked. `cupid-properties` cares about naming
at the Composable (intention-revealing) and Domain-based (language) properties; the
techniques below are how you get there in practice, at any altitude from a variable to a
public API.

## Optimise for the calling context, not the declaration

Declarations are written once; call sites are read constantly. Choose names so the *call*
reads as a sentence, not so the *signature* reads well in isolation:

```python
notify_all(registered_clients, about=the_new_version)
```

A call site that reads as a sentence becomes one chunk for the reader's working memory
instead of several — the same reason well-named functions compress reasoning the way a
well-named variable does. When naming a function, draft the call site first.

## Wishful thinking: name before you implement

From *Structure and Interpretation of Computer Programs*: write the calling code as if the
function you need already exists, using the name and shape that makes that call site read
naturally. Only once the sentence is right do you go implement it.

```python
# Write this first, as if send_welcome_email and provision_account already exist:
def onboard(new_user):
    account = provision_account(new_user)
    send_welcome_email(account)
    return account
```

This produces code that reads close to natural language without padding it with words.
Naming comes first; implementation fills in behind it.

## Let domain types liberate parameter names

Primitive obsession doesn't just weaken the type system — it steals the parameter name's
only job. When the type is a raw primitive, the name has to carry both *what* the value is
and *why* it's there, and usually only manages the first:

```java
// Smell: int tells us nothing; the name has to do all the work, and doesn't
public ActionResult ListRss(int languageId) { ... }
public ActionResult NewsItem(int newsItemId) { ... }

// Better: the type says what it is; the name is freed to say why it's here
public ActionResult ListRss(Language preferredRssFeedLanguage) { ... }
public ActionResult NewsItem(NewsItem clickedArticle) { ... }
```

`clickedArticle` vs. `featuredArticle` vs. `relatedArticle` are three different roles for the
same domain type — roles a primitive `int newsItemId` can never express. This is the same
move as the domain-types material in `cupid-properties` (Domain-based) and
`cupid-java-spring-boot`/`cupid-python` (Money, PaymentId, etc.); here it's specifically the
naming payoff of making that move.

## Scope determines length

Names don't carry meaning in isolation — they borrow it from the surrounding context. The
smaller and tighter the scope, the less a name needs to say for itself:

```python
for i, article in enumerate(front_page_articles):
    publish(article)
```

`i` is fine here: the loop is one small, self-contained chunk, and the context (`enumerate`,
`front_page_articles`) supplies the meaning. The same single-letter name in an instance
field or a public API is a defect — there is no surrounding chunk to lend it meaning, so the
name must carry the full weight alone. When reviewing a short name, ask what context is
doing the explaining, and check that context is actually still there in scope.

## Naming conventions that detract

**Drop the `I`-prefix.** `ChatConnection`, not `IChatConnection`. Whether a type is a
concrete class, an abstract class, or an interface is the least interesting fact about it —
a caller holding a reference shouldn't need to care, so don't put that implementation detail
in every use of the name. (Consistent with `software-design-principles`' rejection of
interface-per-class: if the interface earns its place — see the DIP guidance there — it
still doesn't earn an `I`.)

**Get rid of getters and setters.** `get`/`set` names are procedural, and procedural names
invite ask-then-tell code:

```python
# Ask-then-tell, invited by procedural names
customer = get_customer(customer_id)
set_customer_status(customer, SUSPENDED)

# Tell-don't-ask — the behaviour has a name of its own
suspend(a_customer)

# Even a pure query reads better without the get-prefix
buyer = customer_for(customer_id)
```

This is the same Tell-Don't-Ask rule `software-design-principles` already enforces; the
naming angle is that `get`/`set` prefixes are what *attract* the violation in the first
place — rename the accessor and the ask-then-tell pattern becomes visually awkward enough
that it self-corrects.

If a convention feels non-negotiable only because it's familiar, that's worth noticing:
repeated exposure alone makes practices feel correct (the mere-exposure effect). Prefer
conventions you can justify over conventions you're merely used to.

**Avoid the dumpster.** `Utils`, `Misc`, `Helper`, `Common` — a vague name doesn't just fail
to communicate, it actively attracts more of whatever doesn't fit elsewhere, because it
gives the next person permission to dump there too. Reaching for one of these names is a
signal that a domain concept hasn't been found yet, not a container problem. `Manager` and
`Handler` fail the same way — the `software-design-principles` naming ban already lists all
of these; the reason they're banned is this attractor effect, not mere ugliness.

## Applying this during review

- **New code, before writing it:** derive the call site with wishful thinking before the
  implementation exists.
- **Reviewing a name:** ask what type is standing behind each parameter — if it's a
  primitive doing a domain concept's job, the name is compensating for a missing type.
- **Reviewing a short name:** check that the scope around it actually supplies the missing
  context; if the scope is large or the name crosses a boundary, the name needs to expand.
- **Any name with `get`/`set`/`Utils`/`Manager`/`I`-prefix:** treat as a prompt to find the
  behaviour or domain concept that the vague name is standing in for.

## Further reading

- [An opinionated (and mainly correct) guide to naming things](https://adamtornhill.substack.com/p/an-opinionated-and-mainly-correct) — Adam Tornhill (source article for this skill)
- [Structure and Interpretation of Computer Programs](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/index.html) — wishful thinking as a design tool
- [Tell, Don't Ask](https://martinfowler.com/bliki/TellDontAsk.html) — Martin Fowler
- [Two Hard Things](https://martinfowler.com/bliki/TwoHardThings.html) — Martin Fowler, on naming and cache invalidation
- [What's in a name? A study of names, readability and license violations](https://link.springer.com/article/10.1007/s10664-018-9621-x) — identifier quality and debugging time
- [Improving LLM Code Comprehension via Structural Signals](https://arxiv.org/html/2505.10443v3) — identifier naming as the highest-leverage structural signal for LLM comprehension
