# From SOLID to CUPID: Design Principles for Production Java/Spring Boot

> Translated from Dan North's CUPID framework and the article
> *"From SOLID to CUPID: Design Principles That Survive Production in Cloud-Native .NET"*
> into Java/Spring Boot idioms and patterns.

---

## Overview

**SOLID** defines rules for internal code organisation. **CUPID** defines properties that running systems should exhibit — especially under the conditions of cloud-native deployment: distributed failure, sustained load, and independent deployability.

The key philosophical shift: SOLID principles are **binary** (you comply or you violate). CUPID properties are **directional** — code is simply closer to or further from the centre. Any movement toward a CUPID property improves the code, regardless of where it starts.

Use **SOLID within a service boundary** and **CUPID across service boundaries and for deployment readiness**.

---

## Why CUPID? — SOLID's Production Blindspots

| SOLID Principle | Production Gap |
|---|---|
| **S** — Single Responsibility | Ambiguous. "One reason to change" drives artificial seams that scatter related code. |
| **O** — Open/Closed | 1990s constraint. VCS + safe refactoring tools eliminated the need to treat code as an immutable asset. |
| **L** — Liskov Substitution | Presupposes inheritance hierarchies; composition is the modern alternative. |
| **I** — Interface Segregation | Remediation for already-oversized interfaces. Prevents symptoms, not causes. |
| **D** — Dependency Inversion | Universally applied, produces abstraction forests no one can navigate; interfaces with a single implementation add cost, not value. |

None of SOLID's principles address what kills production systems: retry storms, unbounded queues, duplicate processing, missing observability, fragile startup sequences.

---

## The CUPID Properties

### C — Composable: *Plays Well With Others*

Software that is easy to use gets reused. Composability is about how easily a component integrates with, and can be assembled alongside, other components.

**Three sub-properties:**

| Sub-property | What it means |
|---|---|
| Small surface area | A narrow, opinionated API. Developers should be able to assess fit within two minutes and exit early if it does not fit. |
| Intention-revealing | Names and structure communicate purpose without requiring implementation reads. |
| Minimal dependencies | Avoid the "gorilla problem" — the user wanted a banana but got a gorilla holding the banana and the entire jungle. |

**Minimal dependency surface — before and after:**

```java
// Smell: shared "core" library declares a Spring Data dependency.
// Every consumer now transitively depends on Spring Data,
// even if they only wanted the Money type.
public class MoneyConverter {
    // Uses org.springframework.data.convert.WritingConverter
    // → drags in spring-data-commons for all consumers
}

// Better: keep the domain type dependency-free.
// Consumers who need the Spring Data converter declare it themselves,
// in their own infrastructure layer.
public record Money(BigDecimal amount, Currency currency) {
    // no framework imports — composes freely with any persistence layer
}
```

**Domain-scoped `@Configuration` — before and after:**

```java
// Smell: one God config registers everything
@Configuration
public class AppConfig {
    @Bean PaymentService paymentService() { ... }
    @Bean FraudScreeningService fraudService() { ... }
    @Bean NotificationService notificationService() { ... }
    @Bean DataSource dataSource() { ... }
    @Bean KafkaTemplate<?,?> kafkaTemplate() { ... }
    // ... 200 more lines
}

// Better: one @Configuration per bounded context
@Configuration
class PaymentsConfig {
    @Bean PaymentAuthorisationService paymentAuthorisationService(...) { ... }
    @Bean OutboxRelayService outboxRelayService(...) { ... }
}

@Configuration
class FraudConfig {
    @Bean FraudScreeningService fraudScreeningService(...) { ... }
}
```

Each config can be tested, replaced, or conditionally loaded independently. A new team member reading `PaymentsConfig` sees only payments concerns.

---

### U — Unix Philosophy: *Does One Thing Well*

A component should have a single, well-defined **purpose from the outside** — from the perspective of the user of the component, not from the perspective of its internal organisation.

**Critical distinction from SRP:**

| | Unix Philosophy (CUPID) | Single Responsibility (SOLID) |
|---|---|---|
| Perspective | Outside-in — what does callers need from me? | Inside-out — how many reasons can this change? |
| Split criterion | Callers need the parts in different combinations | Internal change vectors differ |
| Risk | Under-splitting loses focus | Over-splitting creates artificial seams |

#### The report example — and when it cuts both ways

SRP tells you to separate `ReportContentService` from `ReportFormatterService` because content and format are different "reasons to change." CUPID asks a different question: **would callers ever want these pieces in different combinations?**

If every caller always needs both — the content is meaningless without the format — then the split is artificial. You have created two classes that must always be changed and deployed together anyway. The seam adds interface overhead without composability.

```java
// Artificial split: callers always need both; no one ever wants raw content alone
@Service ReportContentService contentService;   // useless without formatter
@Service ReportFormatterService formatterService; // useless without content

// One purpose from the outside: generate a formatted report
@Service
public class MonthlySalesReportService {
    Report generate(ReportParameters params) { ... }
}
```

But if callers genuinely need the parts independently — say, PDF and Excel formats applied to the same content, or the same format applied to different data sources — *then* separating them is correct. Now each piece has a genuine, standalone purpose to its callers, and the split creates real composability.

```java
// Genuine composability: callers mix and match format and content independently
public interface ReportContent { ... }
public interface ReportFormatter { ReportFile format(ReportContent content); }

// Callers compose:
var report = pdfFormatter.format(monthlySalesContent);
var report = excelFormatter.format(monthlySalesContent);
var report = pdfFormatter.format(ytdSalesContent);
```

**The test:** *Would a caller ever want piece A without piece B, or wire them in a different combination?* If yes, separating them creates composable components — this is exactly what the Unix pipeline demonstrates. If no, the separation is internal housekeeping that leaks into the public API for no benefit.

#### Why the Unix pipeline is not a contradiction

Unix tools (`grep`, `sort`, `uniq`) are separated not because their *internals* have different change vectors, but because callers genuinely need them in different combinations:

```bash
cat access.log | grep ERROR | sort | uniq -c   # frequency of unique errors
cat access.log | grep ERROR | sort -k1 | head  # first occurrence of each error
```

`sort` does not know what `grep` filtered. `uniq` does not know what `sort` ordered. Each has one purpose to its caller, and callers compose freely. That composability is the point.

Spring Batch's Reader → Processor → Writer applies the same logic: a `JdbcCursorItemReader` can feed a `PaymentValidationProcessor`, and the same processor can be reused with a `FlatFileItemReader` for a batch file import. The separation creates real caller value.

```java
@Bean
public Step paymentProcessingStep(
        ItemReader<RawPayment> reader,       // swap: DB or flat-file
        ItemProcessor<RawPayment, Payment> processor,  // reused across sources
        ItemWriter<Payment> writer) {
    return stepBuilderFactory.get("processPayments")
        .<RawPayment, Payment>chunk(100)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .build();
}
```

#### Applying this in Spring Boot

```java
// Smell: purpose is unclear — does "process" mean authorise, persist, notify, all three?
@Service
public class PaymentService {
    void process(PaymentRequest request) { ... }
}

// Good: one purpose, stated explicitly
@Service
public class PaymentAuthorisationService {
    AuthorisationResult authorise(PaymentRequest request) { ... }
}
```

- Each `@RestController` owns one resource or capability — not a cluster of loosely related endpoints
- Kafka consumers receive, validate, and **delegate** to a domain service; they do not also persist, notify, and publish inside the same listener method
- A service named `PaymentService` with methods `authorise`, `refund`, `notify`, `archive` is a smell — it likely contains two or three single-purpose services that have not been named yet

---

### P — Predictable: *Does What You Expect*

Code behaves consistently and reliably, and it is not only possible but **easy** to verify this. Predictability is a generalisation of testability that covers runtime behaviour, not just unit correctness.

**Three dimensions of predictability:**

| Dimension | Definition |
|---|---|
| Robustness | Breadth of situations covered; limitations are obvious |
| Reliability | Consistent behaviour within covered scenarios |
| Resilience | Graceful degradation under unexpected perturbations |

#### Backpressure — Bounded Queues

Unbounded queues cause memory spikes and thread starvation under sustained load. Bounding them makes system behaviour predictable under stress.

```java
// .NET: Channel.CreateBounded(100) with FullMode.Wait
// Java equivalent:
BlockingQueue<PaymentJob> queue = new ArrayBlockingQueue<>(100);

// Or with Spring Integration:
@Bean
public QueueChannel paymentChannel() {
    return new QueueChannel(100); // bounded
}

// Or with Project Reactor:
Flux.create(sink -> /* producer */, FluxSink.OverflowStrategy.ERROR)
    .onBackpressureBuffer(100);
```

With Kafka: constrain consumer throughput with `max.poll.records` and process time budgets rather than letting the consumer thread fall arbitrarily behind.

#### Idempotency Key Pattern

Clients retry transient failures. Without idempotency, retries cause double-charges, duplicate records, or inconsistent state. The server must guarantee that replaying the same logical request produces the same observable outcome.

```java
// Filter or interceptor — runs before the controller
@Component
public class IdempotencyFilter extends OncePerRequestFilter {

    private final IdempotencyStore store;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws IOException, ServletException {
        String key = request.getHeader("Idempotency-Key");
        if (key == null) {
            chain.doFilter(request, response);
            return;
        }
        Optional<CachedResponse> cached = store.get(key);
        if (cached.isPresent()) {
            writeCachedResponse(response, cached.get());
            return;
        }
        // Wrap response to capture and store after processing
        CachingResponseWrapper wrapper = new CachingResponseWrapper(response);
        chain.doFilter(request, wrapper);
        store.put(key, wrapper.getCachedResponse());
    }
}
```

Store idempotency keys in Redis with a TTL matching the client's retry window (e.g. 24 hours).

#### Transactional Outbox / Inbox (Exactly-Once Processing)

The core distributed systems problem: a database write and a message publish cannot be atomic across different systems. The outbox pattern bridges them.

```java
@Transactional
public void authorisePayment(PaymentRequest request) {
    Payment payment = paymentRepository.save(new Payment(request));

    // Same transaction — atomic commit with the payment record
    OutboxMessage message = new OutboxMessage(
        "PaymentAuthorised",
        objectMapper.writeValueAsString(payment)
    );
    outboxRepository.save(message);
}
```

**Relay options (publish from the outbox):**

| Approach | Mechanism |
|---|---|
| Polling scheduler | `@Scheduled` task polls the outbox table and publishes unpublished rows |
| Debezium CDC | Attaches to the database transaction log; publishes automatically with no polling |
| Spring Modulith | `@ApplicationModuleListener` + `EventPublication` repository (built-in outbox support) |

**Inbox (consumer-side deduplication):**

```java
@KafkaListener(topics = "payments.authorised")
@Transactional
public void onPaymentAuthorised(PaymentAuthorisedEvent event) {
    if (inboxRepository.existsByEventId(event.getEventId())) {
        return; // already processed — idempotent consumer
    }
    processEvent(event);
    inboxRepository.save(new InboxEntry(event.getEventId()));
}
```

#### Resilience Layering with Resilience4j

Policy order matters: **timeout → retry → circuit breaker → bulkhead**. Each layer applies at the right stage to prevent retry storms and cascading failures.

```java
@CircuitBreaker(name = "bankClient", fallbackMethod = "authoriseFallback")
@Retry(name = "bankClient")
@TimeLimiter(name = "bankClient")
@Bulkhead(name = "bankClient", type = Bulkhead.Type.THREADPOOL)
public CompletableFuture<AuthResult> authorisePayment(PaymentRequest req) {
    return CompletableFuture.supplyAsync(() -> bankClient.authorise(req));
}

private CompletableFuture<AuthResult> authoriseFallback(
        PaymentRequest req, Throwable t) {
    return CompletableFuture.completedFuture(AuthResult.deferred());
}
```

```yaml
# application.yml
resilience4j:
  timelimiter:
    instances:
      bankClient:
        timeoutDuration: 2s

  retry:
    instances:
      bankClient:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        retryExceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
        ignoreExceptions:
          - com.example.payments.BadRequestException

  circuitbreaker:
    instances:
      bankClient:
        slidingWindowSize: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 10s
        permittedNumberOfCallsInHalfOpenState: 3

  bulkhead:
    instances:
      bankClient:
        maxConcurrentCalls: 20
        maxWaitDuration: 100ms
```

> **Note:** Resilience4j annotation execution order is Bulkhead > TimeLimiter > CircuitBreaker > Retry — regardless of annotation declaration order on the method. Configure via properties to reason about behaviour clearly.

**Retries with jitter** (manual configuration to prevent thundering herds):

```java
@Bean
public RetryConfig bankClientRetryConfig() {
    return RetryConfig.custom()
        .maxAttempts(3)
        .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(500, 2.0, 0.5))
        .build();
}
```

#### Observability — Dan North's Six-Stage Maturity Model

Most services never progress beyond stage 1. Deliberate design for observability is a Predictable property.

| Stage | What it means | Spring Boot / Java implementation |
|---|---|---|
| 1 Instrumentation | Software communicates what it is doing | SLF4J structured logs, `Observation` API spans |
| 2 Telemetry | Making that information available | Actuator `/actuator/prometheus`, OTEL exporter |
| 3 Monitoring | Receiving and visualising instrumentation | Prometheus + Grafana |
| 4 Alerting | Reacting to monitored data patterns | Alertmanager rules |
| 5 Predicting | Anticipating events from historical data | Grafana ML / external tooling |
| 6 Adapting | Dynamic system changes responding to predictions | HPA on custom metrics via KEDA |

**Spring Boot 3+ observability setup:**

```xml
<!-- pom.xml -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```yaml
# application.yml
management:
  tracing:
    sampling:
      probability: 1.0       # 1.0 in dev/test; 0.05–0.1 in production
  otlp:
    tracing:
      endpoint: http://otel-collector:4318/v1/traces
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
```

**Micrometer Observation API for custom spans:**

```java
@Service
public class PaymentAuthorisationService {

    private final ObservationRegistry registry;

    public AuthResult authorise(PaymentRequest request) {
        return Observation.createNotStarted("payment.authorise", registry)
            .lowCardinalityKeyValue("payment.type", request.getType().name())
            .observe(() -> doAuthorise(request));
    }
}
```

**Structured logging with trace correlation:**

```java
// With Logback + logstash-logback-encoder, MDC is populated automatically
// from Micrometer Tracing context
log.info("Payment authorised",
    kv("paymentId", payment.getId()),
    kv("amount", payment.getAmount()),
    kv("currency", payment.getCurrency()));
```

---

### I — Idiomatic: *Feels Natural*

Code reflects the conventions of the language, ecosystem, and team. The target audience is **an experienced Java developer who does not know this codebase** — not a beginner, not the original author.

**Constructor injection — the idiomatic Spring Boot style:**

```java
// Smell: field injection hides dependencies and makes testing harder
@Service
public class PaymentAuthorisationService {
    @Autowired private BankClient bankClient;
    @Autowired private PaymentRepository repository;
}

// Good: dependencies are explicit; no Spring needed to construct in tests
@Service
public class PaymentAuthorisationService {

    private final BankClient bankClient;
    private final PaymentRepository repository;

    public PaymentAuthorisationService(BankClient bankClient,
                                       PaymentRepository repository) {
        this.bankClient = bankClient;
        this.repository = repository;
    }
}
```

**`@ConfigurationProperties` over scattered `@Value`:**

```java
// Smell: @Value strings scattered across services; typos silently become null
@Service
public class BankClient {
    @Value("${bank.api.url}") private String url;
    @Value("${bank.api.timeout-ms}") private int timeoutMs;
    @Value("${bank.api.key}") private String apiKey;
}

// Good: typed, validated, discoverable configuration in one place
@ConfigurationProperties(prefix = "bank.api")
public record BankClientProperties(
    @NotBlank String url,
    @Min(100) int timeoutMs,
    @NotBlank String apiKey
) {}

// application.yml — structured, auto-completed by IDE
bank:
  api:
    url: https://bank.example.com
    timeout-ms: 2000
    api-key: ${BANK_API_KEY}
```

**Sealed interfaces for result types — avoid exceptions as control flow:**

```java
// Smell: callers must catch to distinguish decline from error
AuthorisationResult authorise(PaymentRequest req) throws BankDeclinedException { ... }

// Good: the type system expresses all outcomes; callers handle with pattern matching
public sealed interface AuthorisationResult
    permits AuthorisationResult.Approved,
            AuthorisationResult.Declined,
            AuthorisationResult.Deferred {

    record Approved(String authCode) implements AuthorisationResult {}
    record Declined(String reason) implements AuthorisationResult {}
    record Deferred(String trackingId) implements AuthorisationResult {}
}

// Caller — exhaustive, readable, no exception handling
AuthorisationResult result = service.authorise(request);
return switch (result) {
    case Approved a  -> ResponseEntity.ok(new ApprovalResponse(a.authCode()));
    case Declined d  -> ResponseEntity.status(402).body(new DeclineResponse(d.reason()));
    case Deferred df -> ResponseEntity.accepted().body(new DeferralResponse(df.trackingId()));
};
```

**Test slices — test only what the layer owns:**

```java
// Smell: @SpringBootTest for every test; starts full context for a controller test
@SpringBootTest
class PaymentControllerTest { ... }

// Good: test slices load only what the layer needs
@WebMvcTest(PaymentAuthorisationController.class)   // controller layer only
class PaymentAuthorisationControllerTest {
    @MockBean PaymentAuthorisationService service;
    // tests HTTP mapping, validation, error responses — not service logic
}

@DataJpaTest  // JPA + in-memory DB only; no web layer, no services
class PaymentRepositoryTest { ... }

@SpringBootTest  // full context: integration tests only
class PaymentAuthorisationIntegrationTest { ... }
```

**Code smell — framework annotations leaking into the domain model:**

```java
// Smell: domain class carries JPA concerns; cannot be used without Hibernate
@Entity
@Table(name = "payment")
public class Payment {
    @Id @GeneratedValue
    private Long id;
    @Column(name = "amount_minor_units")
    private long amountMinorUnits;
}

// Better: separate persistence entity from domain model
// Domain model — pure, framework-ignorant
public record Payment(PaymentId id, Money amount, PaymentStatus status) {}

// Persistence entity — carries JPA annotations; lives in the infrastructure layer
@Entity @Table(name = "payment")
class PaymentEntity {
    @Id Long id;
    long amountMinorUnits;
    String currency;
    // maps to/from Payment in a repository adapter
}
```

**Team idioms — document in Architecture Decision Records (ADRs):**

- Logging format (JSON via `logstash-logback-encoder` vs. plain-text) and what constitutes a loggable event vs. a metric
- Error response envelope (`ProblemDetail` RFC 9457 is the Spring 6 default — adopt it unless there is a specific reason not to)
- Package structure convention (see Domain-based section)
- Exception hierarchy: unchecked domain exceptions (`PaymentDeclinedException`) vs. infrastructure exceptions, and which layer translates which
- Profile strategy: `local`, `test`, `staging`, `production` — and which properties each profile overrides

---

### D — Domain-based: *In Language and Structure*

Code conveys its purpose in problem domain vocabulary, and its physical structure mirrors the domain — not the framework's scaffolding.

**Domain-based language:**

Prefer domain types over primitives:

```java
// Smell: stringly-typed / primitive-obsessed
public void authorise(String paymentId, BigDecimal amount, String currency) {}

// Better: domain types carry invariants and intent
public void authorise(PaymentId id, Money amount) {}

public record PaymentId(UUID value) {
    public PaymentId { Objects.requireNonNull(value); }
}

public record Money(BigDecimal amount, Currency currency) {
    public Money {
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        if (amount.scale() > currency.getDefaultFractionDigits())
            throw new IllegalArgumentException("Amount precision exceeds currency scale");
    }
}
```

**Domain-based structure:**

Avoid the framework scaffold as your top-level package layout:

```
# Anti-pattern: framework-first layout
src/main/java/com/example/
├── controllers/
├── services/
├── repositories/
├── models/
├── dtos/
└── config/
```

This layout scatters a single domain capability (e.g. payment authorisation) across five packages and forces developers to navigate the whole tree for every change.

```
# CUPID-aligned: domain-first layout
src/main/java/com/example/
├── payments/
│   ├── authorisation/
│   │   ├── PaymentAuthorisationService.java
│   │   ├── PaymentAuthorisationController.java
│   │   ├── AuthorisationRepository.java
│   │   └── AuthorisationResult.java
│   ├── outbox/
│   │   ├── OutboxMessage.java
│   │   └── OutboxRelayService.java
│   └── model/
│       ├── Payment.java
│       ├── PaymentId.java
│       └── Money.java
├── fraud/
│   └── screening/
└── notifications/
```

All code for a bounded context lives together. A change to payment authorisation touches one directory tree. Adding a new domain adds one new directory.

**Domain boundaries as deployment boundaries:**

When structure aligns with domains, extracting a service is a move, not a rewrite. The boundary already exists in the code; deployment just makes it a process boundary too.

Spring Modulith enforces these boundaries at test time:

```java
// Verify that the payments module only exposes its intended API surface
// and that no other module reaches into its internals
@ApplicationModuleTest
class PaymentsModuleTest {

    @Test
    void verifiesModuleStructure(ApplicationModules modules) {
        modules.getModuleByName("payments")
               .ifPresent(m -> m.verifyDependencies(modules));
    }
}
```

```java
// Spring Modulith application event — cross-module communication without
// direct dependency. Fraud module subscribes without importing from payments.
// payments module publishes:
@Transactional
public void authorise(PaymentRequest request) {
    Payment payment = repository.save(new Payment(request));
    events.publishEvent(new PaymentAuthorisedEvent(payment.getId()));
    // ^ Spring Modulith records this in EventPublication for reliable delivery
}

// fraud module listens — no import of payments internals:
@ApplicationModuleListener
public void onPaymentAuthorised(PaymentAuthorisedEvent event) {
    fraudScreeningService.screen(event.paymentId());
}
```

Generate a living architecture diagram from the actual module structure:

```java
// In a test — outputs PlantUML / Mermaid diagrams from real code structure
@Test
void writesModuleDocumentation(ApplicationModules modules) throws Exception {
    new Documenter(modules)
        .writeModulesAsPlantUml()
        .writeIndividualModulesAsPlantUml();
}
```

---

## Production Readiness Scorecard

Rate each CUPID property 0–3 before scaling:

| Score | Meaning |
|---|---|
| 0 | No evidence of this property |
| 1 | Informal / inconsistent application |
| 2 | Consistent, evidenced in code, tests, or metrics |
| 3 | Embedded in tooling, pipelines, and process with automated verification |

| Property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Composable** | God `AppConfig`, shared core drags in everything | Some domain configs, but still cross-cutting | Domain-scoped `@Configuration`, narrow interfaces | Auto-configuration with documented surface area, contract tests |
| **Unix Philosophy** | Multi-purpose services/controllers | Coarse capability groupings | One resource per controller, one purpose per service | Enforced via architecture tests (ArchUnit) |
| **Predictable** | No resilience, no idempotency, unbounded queues | Ad-hoc `try/catch`, some retries | Resilience4j per-client, idempotency filter, bounded queues | Chaos engineering, fault injection tests, SLO dashboards |
| **Idiomatic** | Mixed styles, annotation scatter, inconsistent patterns | Team has rough conventions | Checkstyle / SpotBugs / PMD enforced in CI | ADRs maintained, linting in pre-commit, onboarding guide verified |
| **Domain-based** | Framework scaffold as package structure | Some domain groupings | Domain-first layout, domain types for key concepts | Spring Modulith module tests, domain glossary maintained |

**Thresholds:**
- Average ≥ 2.5 → ready for production at scale
- Average 1.5–2.4 → limited release only; identify the lowest-scoring property and address it first
- Average < 1.5 → refactor before scaling

---

## Common Smells and Quick Fixes

| Smell | Symptom | Fix |
|---|---|---|
| God `AppConfig` | Single `@Configuration` class with 200+ `@Bean` definitions | Split by domain; one `@Configuration` per bounded context |
| Sync startup initialisation | Blocking calls in `@PostConstruct` slow start; timeout in health checks | Move to `ApplicationListener<ApplicationReadyEvent>` |
| Unbounded internal queues | OOM under load; GC pressure spikes | `ArrayBlockingQueue(N)` or `QueueChannel(N)` |
| Catch-all retry | `@Retry` on every call regardless of exception type | Per-client `RetryConfig` with explicit `retryExceptions` list |
| Primitive obsession | `String paymentId`, `BigDecimal amount` at every boundary | Introduce `PaymentId`, `Money` value objects |
| Framework scaffold as package | `com.example.controllers`, `com.example.services` | Reorganise to `com.example.payments.authorisation` |
| No idempotency on mutations | Retry storms cause duplicate records or double-charges | `OncePerRequestFilter` checking Redis-backed idempotency key |
| Field injection | `@Autowired` on instance fields | Constructor injection; make dependencies explicit |
| Missing observability | Logs exist but no traces, no metrics on business operations | Micrometer Observation API + Actuator + OTEL exporter |
| API versioning by removal | Renaming or removing fields breaks deployed consumers | Additive changes only; use `@JsonProperty` aliases; `Sunset` headers |

---

## Library Reference

| Concern | Library / Mechanism | Notes |
|---|---|---|
| Resilience (retry, CB, bulkhead, timeout) | `resilience4j-spring-boot3` | Direct Polly equivalent; use annotations + `application.yml` |
| Distributed tracing | `micrometer-tracing-bridge-otel` + OTEL Java agent | Spring Boot 3+ native support |
| Metrics | `micrometer-registry-prometheus` + Spring Actuator | `/actuator/prometheus` endpoint |
| Structured logging | `logstash-logback-encoder` | JSON logs with automatic trace/span ID injection |
| Transactional outbox | `spring-modulith-events-*` or `transaction-outbox` (gruelbox) | Spring Modulith is the idiomatic Spring choice |
| Kafka idempotent consumer | `spring-kafka` + manual inbox table | Or Kafka transactions + `isolation.level=read_committed` |
| Consumer-driven contract tests | `pact-jvm-provider-spring` | Identical workflow to Pact for .NET |
| API gateway / version routing | `spring-cloud-gateway` | Equivalent to YARP |
| Architecture enforcement | `archunit` | Enforce module boundaries, layer rules, naming conventions |
| Module boundary testing | `spring-modulith-test` | `@ApplicationModuleTest` per bounded context |
| Configuration binding | `@ConfigurationProperties` | Prefer over scattered `@Value` |
| API versioning | Path-based (`/api/v1/...`) + `springdoc-openapi` | Plus `Sunset` / `Deprecation` response headers |
| Validation | `spring-boot-starter-validation` + Hibernate Validator | `@Valid` on controller params; `@NotNull`, `@Size` etc. |

---

## Quick Reference: CUPID as a Code Review Lens

Ask these questions at code review time:

| Property | Review question |
|---|---|
| **Composable** | Can I use this component without pulling in things I don't need? Is the API surface the minimum needed? |
| **Unix Philosophy** | From a caller's perspective, does this do exactly one thing? Would a different name reveal a hidden second purpose? |
| **Predictable** | What happens when a downstream dependency is slow? When a request is retried? Is the result always the same for the same input? |
| **Idiomatic** | Does this look like code written by someone who knows Spring Boot and our team conventions? Would a new joiner find it familiar? |
| **Domain-based** | Do the names come from the business domain or the framework? If I rename this package, does the new name mean something to a domain expert? |

---

## Further Reading

- [CUPID — for joyful coding](https://dannorth.net/blog/cupid-for-joyful-coding/) — Dan North
- [CUPID — the back story](https://dannorth.net/blog/cupid-the-back-story/) — Dan North
- [From SOLID to CUPID: Design Principles That Survive Production in Cloud-Native .NET](https://developersvoice.com/blog/architecture/solid-to-cupid-playbook/) — Developers Voice
- [Resilience4j User Guide](https://resilience4j.readme.io/docs/getting-started)
- [Spring Modulith Reference Documentation](https://docs.spring.io/spring-modulith/reference/)
- [Micrometer Tracing](https://micrometer.io/docs/tracing)
- [OpenTelemetry Java](https://opentelemetry.io/docs/languages/java/)
- [ArchUnit User Guide](https://www.archunit.org/userguide/html/000_Index.html)
- [Pact JVM](https://docs.pact.io/implementation_guides/jvm)
