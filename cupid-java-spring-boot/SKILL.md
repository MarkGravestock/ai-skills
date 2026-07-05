---
name: cupid-java-spring-boot
description: Practical CUPID implementation guidance for Java and Spring Boot — concrete idioms, libraries, and production patterns for Composable, Unix philosophy, Predictable, Idiomatic, Domain-based code. Use when reviewing, designing, or refactoring Java/Spring Boot services against CUPID, especially cloud-native deployment concerns (resilience, idempotency, observability, module boundaries). Composes with the cupid-properties skill, which defines the properties themselves.
---

# CUPID for Java / Spring Boot

Stack-specific implementation guidance. **This skill composes with `cupid-properties`** — the
generic skill defines the five properties, the properties-vs-principles philosophy, the
caller-combination test, the SOLID critique, the scorecard, and the review lens. Load it first
(read `../cupid-properties/SKILL.md` if it is not already in context). This file only says what
each property looks like *in Java and Spring Boot*, with emphasis on what survives production:
retry storms, unbounded queues, duplicate processing, missing observability, fragile startup.

---

## C — Composable

**Minimal dependency surface — keep domain types framework-free:**

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

**Domain-scoped `@Configuration` — no God config:**

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

Each config can be tested, replaced, or conditionally loaded independently. A new team member
reading `PaymentsConfig` sees only payments concerns.

---

## U — Unix philosophy

Apply the **caller-combination test** from the generic skill: split only where callers
genuinely want the pieces in different combinations.

**The report example — how the test cuts both ways:**

```java
// Artificial split: callers always need both; no one ever wants raw content alone
@Service ReportContentService contentService;     // useless without formatter
@Service ReportFormatterService formatterService; // useless without content

// One purpose from the outside: generate a formatted report
@Service
public class MonthlySalesReportService {
    Report generate(ReportParameters params) { ... }
}
```

But when callers genuinely mix and match — PDF and Excel over the same content, one format
over different data sources — the split creates real composability:

```java
// Genuine composability: callers combine format and content independently
public interface ReportContent { ... }
public interface ReportFormatter { ReportFile format(ReportContent content); }

var report = pdfFormatter.format(monthlySalesContent);
var report = excelFormatter.format(monthlySalesContent);
var report = pdfFormatter.format(ytdSalesContent);
```

Spring Batch's Reader → Processor → Writer is the same logic: a `JdbcCursorItemReader` can feed
a `PaymentValidationProcessor`, and the same processor is reused with a `FlatFileItemReader`
for batch file imports — the separation creates real caller value:

```java
@Bean
public Step paymentProcessingStep(
        ItemReader<RawPayment> reader,                 // swap: DB or flat-file
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

**Single purpose in Spring Boot terms:**

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

- Each `@RestController` owns one resource or capability — not a cluster of loosely related
  endpoints.
- Kafka consumers receive, validate, and **delegate** to a domain service; they do not also
  persist, notify, and publish inside the same listener method.
- A service named `PaymentService` with methods `authorise`, `refund`, `notify`, `archive` is
  a smell — it likely contains two or three single-purpose services that have not been named yet.

---

## P — Predictable

### Backpressure — bounded queues

Unbounded queues cause memory spikes and thread starvation under sustained load:

```java
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

With Kafka: constrain consumer throughput with `max.poll.records` and process time budgets
rather than letting the consumer thread fall arbitrarily behind.

### Idempotency key pattern

Clients retry transient failures; the server must guarantee replaying the same logical request
produces the same observable outcome:

```java
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
        CachingResponseWrapper wrapper = new CachingResponseWrapper(response);
        chain.doFilter(request, wrapper);
        store.put(key, wrapper.getCachedResponse());
    }
}
```

Store idempotency keys in Redis with a TTL matching the client's retry window (e.g. 24 hours).

### Transactional outbox / inbox (exactly-once processing)

A database write and a message publish cannot be atomic across systems; the outbox bridges them:

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

### Resilience layering with Resilience4j

Policy order matters: **timeout → retry → circuit breaker → bulkhead**. Each layer applies at
the right stage to prevent retry storms and cascading failures.

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

> **Note:** Resilience4j annotation execution order is Bulkhead > TimeLimiter > CircuitBreaker
> > Retry — regardless of annotation declaration order on the method. Configure via properties
> to reason about behaviour clearly.

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

### Observability

Implementation of the six-stage maturity model from the generic skill:

| Stage | Spring Boot / Java implementation |
|---|---|
| 1 Instrumentation | SLF4J structured logs, `Observation` API spans |
| 2 Telemetry | Actuator `/actuator/prometheus`, OTEL exporter |
| 3 Monitoring | Prometheus + Grafana |
| 4 Alerting | Alertmanager rules |
| 5 Predicting | Grafana ML / external tooling |
| 6 Adapting | HPA on custom metrics via KEDA |

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

## I — Idiomatic

Target reader: an experienced Java developer who does not know this codebase.

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
```

```yaml
# application.yml — structured, auto-completed by IDE
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

- Logging format (JSON via `logstash-logback-encoder` vs. plain-text) and what constitutes a
  loggable event vs. a metric
- Error response envelope (`ProblemDetail` RFC 9457 is the Spring 6 default — adopt it unless
  there is a specific reason not to)
- Package structure convention (see Domain-based section)
- Exception hierarchy: unchecked domain exceptions (`PaymentDeclinedException`) vs.
  infrastructure exceptions, and which layer translates which
- Profile strategy: `local`, `test`, `staging`, `production` — and which properties each
  profile overrides

---

## D — Domain-based

**Domain types over primitives:**

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

**Domain-first package layout:**

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

This layout scatters a single domain capability (e.g. payment authorisation) across five
packages and forces developers to navigate the whole tree for every change.

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

All code for a bounded context lives together. A change to payment authorisation touches one
directory tree. Adding a new domain adds one new directory.

**Domain boundaries as deployment boundaries — Spring Modulith:**

When structure aligns with domains, extracting a service is a move, not a rewrite. Spring
Modulith enforces the boundaries at test time:

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

## Common smells and quick fixes

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

## Library reference

| Concern | Library / mechanism | Notes |
|---|---|---|
| Resilience (retry, CB, bulkhead, timeout) | `resilience4j-spring-boot3` | Use annotations + `application.yml` |
| Distributed tracing | `micrometer-tracing-bridge-otel` + OTEL Java agent | Spring Boot 3+ native support |
| Metrics | `micrometer-registry-prometheus` + Spring Actuator | `/actuator/prometheus` endpoint |
| Structured logging | `logstash-logback-encoder` | JSON logs with automatic trace/span ID injection |
| Transactional outbox | `spring-modulith-events-*` or `transaction-outbox` (gruelbox) | Spring Modulith is the idiomatic Spring choice |
| Kafka idempotent consumer | `spring-kafka` + manual inbox table | Or Kafka transactions + `isolation.level=read_committed` |
| Consumer-driven contract tests | `pact-jvm-provider-spring` | |
| API gateway / version routing | `spring-cloud-gateway` | |
| Architecture enforcement | `archunit` | Enforce module boundaries, layer rules, naming conventions |
| Module boundary testing | `spring-modulith-test` | `@ApplicationModuleTest` per bounded context |
| Configuration binding | `@ConfigurationProperties` | Prefer over scattered `@Value` |
| API versioning | Path-based (`/api/v1/...`) + `springdoc-openapi` | Plus `Sunset` / `Deprecation` response headers |
| Validation | `spring-boot-starter-validation` + Hibernate Validator | `@Valid` on controller params; `@NotNull`, `@Size` etc. |

## Scorecard evidence (what 0–3 looks like in Spring Boot)

Use the scoring model from `cupid-properties`; Java/Spring-specific evidence:

| Property | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Composable** | God `AppConfig`, shared core drags in everything | Some domain configs, but still cross-cutting | Domain-scoped `@Configuration`, narrow interfaces | Auto-configuration with documented surface area, contract tests |
| **Unix philosophy** | Multi-purpose services/controllers | Coarse capability groupings | One resource per controller, one purpose per service | Enforced via architecture tests (ArchUnit) |
| **Predictable** | No resilience, no idempotency, unbounded queues | Ad-hoc `try/catch`, some retries | Resilience4j per-client, idempotency filter, bounded queues | Chaos engineering, fault injection tests, SLO dashboards |
| **Idiomatic** | Mixed styles, annotation scatter, inconsistent patterns | Team has rough conventions | Checkstyle / SpotBugs / PMD enforced in CI | ADRs maintained, linting in pre-commit, onboarding guide verified |
| **Domain-based** | Framework scaffold as package structure | Some domain groupings | Domain-first layout, domain types for key concepts | Spring Modulith module tests, domain glossary maintained |

## Further reading (stack-specific)

- [Resilience4j User Guide](https://resilience4j.readme.io/docs/getting-started)
- [Spring Modulith Reference Documentation](https://docs.spring.io/spring-modulith/reference/)
- [Micrometer Tracing](https://micrometer.io/docs/tracing)
- [OpenTelemetry Java](https://opentelemetry.io/docs/languages/java/)
- [ArchUnit User Guide](https://www.archunit.org/userguide/html/000_Index.html)
- [Pact JVM](https://docs.pact.io/implementation_guides/jvm)
