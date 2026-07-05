---
name: cupid-python
description: Practical CUPID implementation guidance for Python — concrete idioms, libraries, and patterns for Composable, Unix philosophy, Predictable, Idiomatic, Domain-based code. Use when reviewing, designing, or refactoring Python code (scripts, libraries, FastAPI/Django/Flask services, data pipelines) against CUPID. Composes with the cupid-properties skill, which defines the properties themselves.
---

# CUPID for Python

Stack-specific implementation guidance. **This skill composes with `cupid-properties`** — the
generic skill defines the five properties, the properties-vs-principles philosophy, the
caller-combination test, the scorecard, and the review lens. Load it first if it is not
already in context: read `cupid-properties.md` in this skill's directory (a synced copy), or
`../properties/SKILL.md` in the source repo. This file only says what each property looks
like *in Python*.

---

## C — Composable

**Small surface area — make the public API explicit:**

```python
# mypackage/__init__.py — the 2-minute surface
from mypackage.money import Money
from mypackage.pricing import price_order

__all__ = ["Money", "price_order"]
```

- Prefix internals with `_` and keep them out of `__all__`. What you export is what you support.
- Prefer functions over classes when there is no state to hold; prefer a class over a tangle of
  functions passing the same five arguments around.

**Narrow interfaces — `Protocol` over inheritance:**

```python
# Smell: importing a concrete client couples every consumer to boto3
def archive(order: Order, s3_client: boto3.client) -> None: ...

# Better: declare only what you need; anything with .put() composes
from typing import Protocol

class BlobStore(Protocol):
    def put(self, key: str, data: bytes) -> None: ...

def archive(order: Order, store: BlobStore) -> None: ...
```

`Protocol` is structural — callers don't inherit anything, so the dependency arrow points at a
two-line contract, not a library.

**Minimal dependencies — avoid the gorilla problem:**

- Don't pull in `pandas` to read one CSV (`csv` is in the stdlib); don't pull in `requests`
  for one call if `urllib.request` or an existing `httpx` dependency will do.
- Keep domain packages free of framework imports. A `Money` type that imports Django can't be
  used in the Lambda, the CLI, or the notebook.
- Use `pyproject.toml` **optional-dependencies** (extras) so consumers opt in:
  `pip install mylib[postgres]` rather than every consumer inheriting `psycopg`.

**Compose with injected callables, not module-level singletons:**

```python
# Smell: hidden module-global — import-order-sensitive, untestable without patching
_client = SmtpClient(settings.SMTP_URL)
def notify(order): _client.send(...)

# Better: dependency passed in; compose at the edge (main, app factory, DI container)
def notify(order: Order, send: Callable[[Email], None]) -> None: ...
```

---

## U — Unix philosophy

Apply the **caller-combination test** (see generic skill) with these Python-flavoured checks:

- A module named `utils.py`, `helpers.py`, or `common.py` is a bag, not a purpose. Move each
  function next to the domain that uses it, or give the module an honest single-purpose name.
- A class named `*Manager`, `*Processor`, or `*Handler` with unrelated method clusters is
  several unnamed single-purpose components.
- One purpose per module; the module docstring should state it in one sentence. If the
  docstring needs "and", consider splitting.

**Generators are Python's pipes** — compose single-purpose steps lazily:

```python
def read_lines(path: Path) -> Iterator[str]: ...
def parse_events(lines: Iterable[str]) -> Iterator[Event]: ...
def only_errors(events: Iterable[Event]) -> Iterator[Event]: ...

# Callers compose freely, like grep | sort | uniq — nothing loads the whole file
for event in only_errors(parse_events(read_lines(log_path))):
    ...
```

Each stage has one purpose to its caller, is independently testable with a plain list, and
streams. Reuse `itertools` before writing your own combinators.

**CLI tools:** read stdin / write stdout so they compose in shell pipelines; put logic in an
importable function and keep `argparse`/`click`/`typer` wiring in a thin `main()`. Exit codes
and stderr for diagnostics, stdout for data.

**Web handlers delegate:** a FastAPI/Django view should parse/validate the request, call one
domain function, and shape the response — not also persist, notify, and publish inline.

---

## P — Predictable

**Kill the classic Python surprise sources:**

```python
# Mutable default argument — shared across calls
def add_item(item, items=[]): ...          # bug
def add_item(item, items=None):            # idiomatic fix
    items = [] if items is None else items
```

- No behaviour at import time (network calls, file reads, heavy computation in module scope).
  Importing a module should be free and side-effect-less.
- Inject time and randomness: pass `now: Callable[[], datetime]` or a `random.Random(seed)`
  instance instead of calling `datetime.now()` / `random.random()` deep inside logic. Tests
  then freeze time without monkeypatching (or use `freezegun` at the boundary).
- Type-hint public functions and run `mypy`/`pyright` in CI — the signature becomes a checked
  contract, which is predictability made cheap.

**Model outcomes in the type system — exceptions for the exceptional:**

```python
@dataclass(frozen=True)
class Approved:
    auth_code: str

@dataclass(frozen=True)
class Declined:
    reason: str

AuthResult = Approved | Declined   # closed union

def authorise(req: PaymentRequest) -> AuthResult: ...

match authorise(req):               # exhaustive with mypy strict + assert_never
    case Approved(code): ...
    case Declined(reason): ...
```

Reserve raised exceptions for genuinely exceptional failures (I/O errors, invariant
violations), and raise the most specific type you have — never bare `except:`.

**Resilience at integration points:**

```python
# Timeouts: httpx has sane defaults — never disable them; requests has NO default timeout,
# so always pass one:
resp = requests.get(url, timeout=5)

# Retries with exponential backoff and jitter (tenacity):
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

@retry(stop=stop_after_attempt(3),
       wait=wait_random_exponential(multiplier=0.5, max=10),
       retry=retry_if_exception_type(httpx.TransportError))   # never retry 4xx
def fetch_rate(base: Currency) -> Decimal: ...
```

- **Bounded queues / backpressure:** `queue.Queue(maxsize=100)` between threads;
  `asyncio.Queue(maxsize=100)` and `asyncio.Semaphore(n)` to cap concurrent downstream calls;
  in Celery/RQ set prefetch and rate limits rather than letting workers fall arbitrarily behind.
- **Idempotency:** for mutating HTTP endpoints, honour an `Idempotency-Key` header via
  middleware backed by Redis `SET key value NX EX ttl`; for queue consumers, dedupe on a
  message/event id in the same transaction as the side effect.

**Observability (stages 1–2 of the maturity model are on you):**

```python
# Structured logging with structlog — key-value events, not interpolated strings
log.info("payment_authorised", payment_id=str(pid), amount_minor=amount, currency="GBP")
```

- `opentelemetry-instrumentation-{fastapi,django,requests,httpx,sqlalchemy}` gives traces for
  little effort; add manual spans (`tracer.start_as_current_span("price_order")`) around key
  domain operations.
- Metrics: `prometheus-client` or OTEL metrics; expose `/metrics`; count business events, not
  just HTTP statuses.
- Configure logging once, at the entry point (`logging.dictConfig` / `structlog.configure`) —
  libraries only ever call `logging.getLogger(__name__)`, never configure.

---

## I — Idiomatic

Target reader: an experienced Python developer who has never seen this codebase.

**Non-negotiable tooling (enforce in CI, not in review comments):**

| Concern | Tool |
|---|---|
| Formatting | `ruff format` (or `black`) |
| Linting + import order | `ruff check` (replaces flake8/isort/pyupgrade) |
| Types | `mypy --strict` or `pyright` |
| Packaging / project metadata | `pyproject.toml` (PEP 621) — not `setup.py` |
| Tests | `pytest` — plain asserts, fixtures, `@pytest.mark.parametrize` |

**Core idioms to prefer:**

- Context managers for every resource: `with open(...)`, `with httpx.Client()`, and
  `@contextmanager` for your own acquire/release pairs.
- EAFP over LBYL: `try: ... except KeyError:` rather than pre-checking, when the race matters
  or the check duplicates the operation.
- `pathlib.Path` over `os.path`; f-strings over `%`/`.format()`; comprehensions and generator
  expressions over accumulate-loops (until they stop fitting on ~two lines).
- `dataclasses` (or `attrs`/`pydantic` where validation is needed) over hand-rolled
  `__init__`/`__eq__`/`__repr__`; `enum.Enum`/`StrEnum` over string constants.
- Iteration: `for item in items`, `enumerate`, `zip` — never `range(len(items))`.

**Watch for accent code (Java/C# habits in Python):**

```python
# Accent: getters/setters
class Account:
    def get_balance(self): return self._balance
    def set_balance(self, v): self._balance = v

# Idiomatic: plain attribute; introduce @property only when behaviour appears
@dataclass
class Account:
    balance: Money
```

- No single-implementation ABC "interfaces" mirroring each class (`AccountServiceImpl`) — use
  duck typing, and reach for `Protocol` only at genuine seams.
- No `Impl`/`I`-prefix naming; no deep package nesting for its own sake; modules are
  namespaces — a file with several related classes is normal Python.

**Local idioms:** where Python offers choices (pydantic vs dataclasses, sync vs async,
Django vs FastAPI layering), record the team's choice in an ADR and lint for it where
possible — don't relitigate it in every PR.

---

## D — Domain-based

**Domain types over primitives — invariants live in the type:**

```python
# Smell: stringly/primitive-typed
def authorise(payment_id: str, amount: float, currency: str) -> None: ...  # float for money!

# Better: value objects with enforced invariants
PaymentId = NewType("PaymentId", UUID)          # zero-runtime-cost distinct type

@dataclass(frozen=True)
class Money:
    amount: Decimal            # never float for money
    currency: Currency

    def __post_init__(self) -> None:
        if self.amount.as_tuple().exponent < -self.currency.exponent:
            raise ValueError("amount precision exceeds currency scale")

def authorise(payment_id: PaymentId, amount: Money) -> AuthResult: ...
```

`NewType` for cheap identity distinctions the type checker enforces; frozen dataclasses (or
pydantic models) when there are invariants to guard. At system boundaries, parse into these
types immediately — *parse, don't validate* — so the core never sees raw primitives.

**Domain-first package layout:**

```
# Anti-pattern: framework scaffold          # CUPID-aligned: domain-first
src/app/                                    src/app/
├── routers/                                ├── payments/
├── services/                               │   ├── router.py
├── repositories/                           │   ├── service.py
├── schemas/                                │   ├── repository.py
└── models/                                 │   └── domain.py      # framework-free
                                            ├── fraud/
                                            └── notifications/
```

- FastAPI: one `APIRouter` per domain package, included from a thin `main.py`.
- Django: apps *are* bounded contexts — `payments`, `appointments`; not one god app named
  after the site. Keep domain logic in plain modules the ORM models call into, not in views.
- Data pipelines: name DAGs/tasks and dbt models after business processes
  (`settle_invoices`), not mechanics (`etl_job_2`).

**Enforce boundaries with import-linter:**

```ini
# .importlinter — fails CI if fraud reaches into payments internals
[importlinter:contract:domain-independence]
name = Domains stay independent
type = independence
modules = app.payments, app.fraud, app.notifications
```

Combine with a `layers` contract (domain must not import infrastructure) to keep domain
packages framework-free. When structure and contracts align with the domain, extracting a
service later is a move, not a rewrite.

---

## Common smells and quick fixes

| Smell | Symptom | Fix |
|---|---|---|
| `utils.py` / `helpers.py` | Unrelated functions accrete forever | Relocate next to their domain; name modules by purpose |
| Mutable default argument | State leaks across calls | `None` sentinel; enable ruff rule B006 |
| Import-time side effects | Slow/flaky imports, order dependence | Move work into functions; app factory pattern |
| `float` for money | Rounding errors in totals | `Decimal` inside a `Money` value object |
| Bare `except:` / `except Exception: pass` | Swallowed failures, mystery states | Catch specific types; re-raise or log with context |
| `requests` call without `timeout` | Worker hangs forever on a dead host | Always pass `timeout=`; prefer `httpx` defaults |
| Module-level singleton clients | Untestable, config frozen at import | Inject via parameters or app factory |
| Framework scaffold packages | Every change touches 4 directories | Domain-first layout + import-linter contracts |
| `Impl` classes and ABC-per-class | Java accent; abstraction forest | Duck typing; `Protocol` at genuine seams only |
| String constants for states | Typos pass silently | `StrEnum`; exhaustive `match` with `assert_never` |

## Library reference

| Concern | Library / mechanism |
|---|---|
| Lint + format | `ruff` |
| Static types | `mypy` / `pyright` |
| Retries with backoff + jitter | `tenacity` |
| HTTP with sane timeouts | `httpx` |
| Structured logging | `structlog` (or stdlib `logging` + JSON formatter) |
| Tracing / metrics | `opentelemetry-*`, `prometheus-client` |
| Validation at boundaries | `pydantic` v2 |
| Value objects | `dataclasses(frozen=True)`, `NewType`, `attrs` |
| Architecture enforcement | `import-linter` |
| Property-based testing | `hypothesis` |
| Task queues with bounded prefetch | `celery` (`worker_prefetch_multiplier`), `arq` |

## Scorecard evidence (what 0–3 looks like in Python)

Use the scoring model from `cupid-properties`; Python-specific evidence:

| Property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Composable** | God modules, framework imports in domain code | Some extras/optional deps | Explicit `__all__`, Protocol seams, framework-free domain | Contract-tested public API, extras documented |
| **Unix philosophy** | `utils.py` everywhere, Manager classes | Coarse groupings | One purpose per module, generator pipelines | Purpose stated in docstrings, enforced review checklist |
| **Predictable** | No timeouts, bare excepts, float money | Ad-hoc try/except, some retries | tenacity policies, bounded queues, typed results, mypy in CI | Chaos/fault-injection tests, SLO dashboards, hypothesis suites |
| **Idiomatic** | Mixed styles, Java accent | Rough conventions | ruff + mypy strict enforced in CI | ADRs maintained, pre-commit hooks, onboarding guide verified |
| **Domain-based** | Framework scaffold, primitives everywhere | Some domain groupings | Domain-first packages, Money/Id value objects | import-linter contracts in CI, domain glossary maintained |
