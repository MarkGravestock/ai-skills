---
name: spring-boot-4-gradle-9-upgrade
description: Use when upgrading a Spring Boot project to Spring Boot 4 (Gradle 8→9 or Maven), switching from io.spring.dependency-management plugin to native Gradle BOM, adding a version catalog, or when getting "could not find X:" resolution errors after removing the dependency-management plugin. Also covers Boot 4 migration gotchas independent of build tool - Jackson 3 package split, Testcontainers 2 artifact renames, @MockBean deprecation, and modular test starters.
---

# Spring Boot 4 + Gradle 9 Upgrade

## Overview

Spring Boot 4 + Gradle 9 introduce several breaking changes that are not obvious from the migration guide alone. The biggest source of breakage is replacing `io.spring.dependency-management` with native Gradle `platform()` BOMs — the two behave differently in ways that cause silent resolution failures.

---

## The Biggest Gotcha: platform() Doesn't Propagate

With the old `io.spring.dependency-management` plugin, version constraints applied to **all** configurations automatically. With native Gradle `platform()`, constraints only apply to the configuration you declare it on — and its **extending** configurations.

`annotationProcessor`, `developmentOnly`, and `testImplementation` do **not** extend `implementation`. They need the platform declared explicitly.

```kotlin
// ❌ WRONG — Lombok and devtools will fail with "could not find X:"
dependencies {
    implementation(platform(SpringBootPlugin.BOM_COORDINATES))
    compileOnly("org.projectlombok:lombok")           // no version → fails
    annotationProcessor("org.projectlombok:lombok")   // no version → fails
    developmentOnly("org.springframework.boot:spring-boot-devtools") // fails
}

// ✅ CORRECT — declare platform on every non-inheriting configuration
dependencies {
    val springBom = platform(SpringBootPlugin.BOM_COORDINATES)
    implementation(springBom)
    annotationProcessor(springBom)
    developmentOnly(springBom)
    testImplementation(springBom)

    compileOnly("org.projectlombok:lombok")           // version from BOM
    annotationProcessor("org.projectlombok:lombok")   // version from BOM
    developmentOnly("org.springframework.boot:spring-boot-devtools")
}
```

**Rule of thumb:** after removing the dependency-management plugin, run `./gradlew dependencies` and check every configuration that uses BOM-managed artifacts without explicit versions.

## platform() Can Only Be Called Inside dependencies {}

`platform()` is a method on `DependencyHandler` — not a top-level function.

```kotlin
// ❌ FAILS at script compilation — "Unresolved reference: platform"
val springBom = platform(SpringBootPlugin.BOM_COORDINATES)

// ✅ CORRECT — local val inside the block
dependencies {
    val springBom = platform(SpringBootPlugin.BOM_COORDINATES)
    implementation(springBom)
    annotationProcessor(springBom)
    ...
}
```

---

## Database Drivers

Spring Boot BOM manages versions for common JDBC drivers. The right coordinates differ by database.

| Database | Artifact | Notes |
|---|---|---|
| MySQL | `com.mysql:mysql-connector-j` | Group changed in 8.0.31 — old `mysql:mysql-connector-java` is deprecated |
| PostgreSQL | `org.postgresql:postgresql` | Coordinates unchanged; version BOM-managed |
| H2 (testing) | `com.h2database:h2` | Coordinates unchanged; version BOM-managed |
| MariaDB | `org.mariadb.jdbc:mariadb-java-client` | Coordinates unchanged; version BOM-managed |
| MSSQL | `com.microsoft.sqlserver:mssql-jdbc` | Coordinates unchanged; version BOM-managed |

For PostgreSQL, the typical setup:
```kotlin
runtimeOnly("org.postgresql:postgresql")  // version from Spring Boot BOM
```

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=myuser
spring.datasource.password=mypassword
```

No dialect configuration needed — Spring Boot and Hibernate 7 auto-detect it.

### Hibernate 7 Notes (Spring Boot 4)

Spring Boot 4 ships with **Hibernate 7** (ORM 7). Key differences:

- `GenerationType.AUTO` now defaults to the **sequence** strategy on most databases (including MySQL/PostgreSQL). If you relied on AUTO mapping to identity columns, switch to `GenerationType.IDENTITY` explicitly.
- Hibernate 7 uses **Jakarta Persistence 3.2** — ensure no leftover `javax.persistence` imports.
- `spring.jpa.hibernate.ddl-auto=update` still works but is discouraged for production; use Flyway or Liquibase instead.

---

## Spring Boot 4 Breaking Changes

### RestClient.Builder No Longer Auto-Configured

Spring Boot 4 removed the `RestClient.Builder` prototype bean. Any constructor-injected `RestClient.Builder` fails to start with "required a bean of type RestClient$Builder that could not be found."

```java
@Bean
RestClient.Builder restClientBuilder() {
    return RestClient.builder();
}
```

If you use observability/tracing and want the builder to pick up Micrometer observation:
```java
@Bean
RestClient.Builder restClientBuilder(ObservationRegistry registry) {
    return RestClient.builder().observationRegistry(registry);
}
```

### spring.jpa.show-sql Bypasses Logging Framework

`spring.jpa.show-sql=true` prints to stdout — not through SLF4J/Logback. Replace with:

```properties
logging.level.org.hibernate.SQL=DEBUG
# Also log bind parameters (Hibernate 6+/7):
logging.level.org.hibernate.orm.jdbc.bind=TRACE
```

### Notable Property Renames in Spring Boot 4

| Old | New |
|---|---|
| `server.error.*` | `spring.web.error.*` |
| `spring.dao.exceptiontranslation.enabled` | `spring.persistence.exceptiontranslation.enabled` |
| `spring.jpa.hibernate.naming.implicit-strategy` (class path) | Package renamed: `org.springframework.boot.orm.jpa.hibernate` → `org.springframework.boot.hibernate` |

Run the [OpenRewrite Spring Boot 4 migration recipe](https://docs.openrewrite.org/recipes/java/spring/boot4) to catch renames automatically.

### Virtual Threads (Java 21+)

Spring Boot 4 makes virtual thread support first-class. Enable with one property:

```properties
spring.threads.virtual.enabled=true
```

This switches Tomcat, scheduled tasks, and `@Async` to use virtual threads. Has no effect below Java 21. No code changes needed — worthwhile on Java 25.

### Jackson 3: API Classes Move, Annotations Don't

Spring Boot 4 ships Jackson 3, which splits packages in a way that trips up both humans and
code generators. **API classes** move to `tools.jackson`; **annotations stay** in
`com.fasterxml.jackson.annotation`:

```java
// ✅ CORRECT — annotations do NOT change package
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonFormat;

// ✅ CORRECT — API classes move to tools.jackson
import tools.jackson.databind.ObjectMapper;

// ❌ WRONG — this package does not exist
import tools.jackson.annotation.JsonProperty;
```

### Testcontainers 2: Artifact and Package Renames

Module artifacts gain a `testcontainers-` prefix, and module packages change:

```xml
<!-- ❌ TC 1.x artifact -->
<artifactId>postgresql</artifactId>

<!-- ✅ TC 2.x artifact -->
<artifactId>testcontainers-postgresql</artifactId>
```

```java
import org.testcontainers.postgresql.PostgreSQLContainer;  // TC 2.x package

@TestConfiguration(proxyBeanMethods = false)
class TestcontainersConfiguration {   // must be package-private in Boot 4 — no `public`
    @Bean
    @ServiceConnection
    PostgreSQLContainer postgresContainer() {
        return new PostgreSQLContainer("postgres:16-alpine");
    }
}
```

`@ServiceConnection` replaces manual `@DynamicPropertySource` wiring — Spring Boot derives the
datasource properties from the container. Import into integration tests with
`@Import(TestcontainersConfiguration.class)`.

### Testing: @MockBean Deprecated, Test Starters Modularised

- **`@MockBean` / `@SpyBean` are deprecated** — use `@MockitoBean` / `@MockitoSpyBean` from
  `org.springframework.test.context.bean.override.mockito` (Spring Framework, not Boot).
- **Test slice annotations moved to modular starters**: `@WebMvcTest` and
  `@AutoConfigureMockMvc` now live in `org.springframework.boot.webmvc.test.autoconfigure`
  and require the `spring-boot-starter-webmvc-test` dependency (similarly
  `spring-boot-starter-data-jpa-test` for `@DataJpaTest`). If `@WebMvcTest` fails to resolve
  after the upgrade, add the starter — `spring-boot-starter-test` alone no longer provides it.

### Maven Projects

The Gradle `platform()` gotchas above don't apply to Maven: `spring-boot-starter-parent` (or a
`dependencyManagement` BOM import) continues to manage versions across all scopes unchanged.
Maven upgrades hit the build-tool-independent changes only: Jackson 3 packages,
Testcontainers 2 artifacts, test starter modularisation, and the property renames listed
above.

---

## Gradle 9 Test Structure

### JVM Test Suite Plugin (Recommended for Integration Tests)

Gradle 9 promotes the `jvm-test-suite` plugin as the standard way to define separate test source sets. The old pattern of manually wiring a second source set is replaced:

```kotlin
plugins {
    java
    `jvm-test-suite`  // built-in, no version needed
}

testing {
    suites {
        val test by getting(JvmTestSuite::class) {
            useJUnitJupiter()
        }

        register<JvmTestSuite>("integrationTest") {
            useJUnitJupiter()
            dependencies {
                implementation(project())  // access main source set classes
            }
            targets {
                all {
                    testTask.configure {
                        shouldRunAfter(test)
                    }
                }
            }
        }
    }
}

// Run integration tests as part of check
tasks.named("check") {
    dependsOn(testing.suites.named("integrationTest"))
}
```

The suite automatically creates `src/integrationTest/java` and `src/integrationTest/resources`. In the version catalog, you can add the platform to the suite's own configuration:

```kotlin
testing {
    suites {
        register<JvmTestSuite>("integrationTest") {
            dependencies {
                implementation(project())
                implementation(platform(SpringBootPlugin.BOM_COORDINATES))
                implementation("org.springframework.boot:spring-boot-starter-test")
            }
        }
    }
}
```

### tasks.withType\<Test\> Still Works

The `tasks.withType<Test> { useJUnitPlatform() }` pattern applies to all test tasks including custom suites. No change needed if you already use this.

### Test Isolation in Gradle 9

Gradle 9 enforces stricter task isolation. If tests share mutable state via system properties or static fields, failures become harder to reproduce. Use `--rerun-tasks` if you suspect stale test outputs, or add:

```kotlin
tasks.withType<Test> {
    // Re-run tests even if inputs haven't changed (useful for integration tests)
    outputs.upToDateWhen { false }
}
```

---

## Version Catalog + Spring Boot Plugin

With a version catalog, the plugin is applied via alias. You still need the import for `BOM_COORDINATES`:

```toml
# gradle/libs.versions.toml
[versions]
spring-boot = "4.0.4"
otel        = "2.26.1-alpha"     # example: include non-BOM-managed BOMs here

[libraries]
otel-bom = { module = "io.opentelemetry.instrumentation:opentelemetry-instrumentation-bom-alpha", version.ref = "otel" }
# BOM-managed libs: declare without version
spring-boot-starter-web  = { module = "org.springframework.boot:spring-boot-starter-web" }
postgresql               = { module = "org.postgresql:postgresql" }
lombok                   = { module = "org.projectlombok:lombok" }

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

```kotlin
// build.gradle.kts
import org.springframework.boot.gradle.plugin.SpringBootPlugin  // still required even with alias

plugins {
    alias(libs.plugins.spring.boot)
}

dependencies {
    val springBom = platform(SpringBootPlugin.BOM_COORDINATES)
    implementation(springBom)
    annotationProcessor(springBom)
    ...
    runtimeOnly(libs.postgresql)   // no version — BOM manages it
    compileOnly(libs.lombok)
}
```

---

## Centralizing Repositories in settings.gradle.kts

`repositoriesMode` is a Gradle `Property<T>` — use `.set()`:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
    }
}
```

Remove `repositories { mavenCentral() }` from `build.gradle.kts`. With `FAIL_ON_PROJECT_REPOS`, Gradle fails if any project-level `repositories {}` block exists — this catches accidental splits.

---

## Gradle 9: Other Notable Changes

### Toolchain Auto-Provisioning

Gradle 9 can automatically download JDKs if the declared toolchain version isn't locally installed. Add to `gradle.properties` to control the provisioning vendor:

```properties
org.gradle.java.installations.auto-download=true
```

If you switch from Java 21 → 25 in the toolchain and CI doesn't have JDK 25, this will download it automatically rather than failing.

### Provider API — Avoid .get() at Configuration Time

Gradle 9 enforces the Provider API more strictly. Calling `.get()` on a `Provider` during the configuration phase (outside a task action) generates warnings and will eventually be an error. Use `.map {}` or `.flatMap {}` to chain providers lazily.

```kotlin
// ❌ Can cause "provider value queried at configuration time" warning
val version = project.version.toString()

// ✅ Lazy — only evaluated at execution time
tasks.named("someTask") {
    doFirst { println(project.version) }
}
```

### Configuration Cache

Stable since Gradle 8.1 — not on by default in Gradle 9 but strongly recommended:

```properties
# gradle.properties
org.gradle.configuration-cache=true
```

Spring Boot Gradle plugin fully supports it. Build output confirms: "Configuration cache entry stored."

### Removed: configurations.all {} with Eager Resolution

In Gradle 9, using `configurations.all {}` to eagerly resolve or mutate configurations at configuration time is restricted. Prefer `configurations.configureEach {}` (lazy):

```kotlin
// ❌ Gradle 9 may warn or fail
configurations.all {
    resolutionStrategy.eachDependency { ... }
}

// ✅ Lazy evaluation
configurations.configureEach {
    resolutionStrategy.eachDependency { ... }
}
```

---

## Known Limitation: Lombok on Java 23+

Lombok emits a warning on Java 23+ about `sun.misc.Unsafe::objectFieldOffset`:

```
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by lombok.permit.Permit
```

This is an upstream Lombok issue — nothing in your project can fix it. The warning is harmless until a future JDK removes the API entirely. Watch for a Lombok release that addresses it.

---

## Quick Reference: What Changed

| Item | Spring Boot 3 / Gradle 8 | Spring Boot 4 / Gradle 9 |
|---|---|---|
| Dependency management | `io.spring.dependency-management` plugin | Native `platform()` per configuration |
| MySQL artifact | `mysql:mysql-connector-java` | `com.mysql:mysql-connector-j` |
| `RestClient.Builder` bean | Auto-configured | Must declare `@Bean` manually |
| Java recommended | 21 (LTS) | 25 (LTS) |
| SQL logging | `spring.jpa.show-sql=true` | `logging.level.org.hibernate.SQL=DEBUG` |
| Configuration cache | Off by default | Off by default — enable in `gradle.properties` |
| Repositories | In `build.gradle.kts` | Centralize in `settings.gradle.kts` |
| Plugin in catalog | `id("...") version "..."` | `alias(libs.plugins.spring-boot)` |
| Integration tests | Manual source set wiring | `jvm-test-suite` plugin |
| Hibernate version | 6.x | 7.x — `GenerationType.AUTO` behavior changed |
| Configs eager mutation | `configurations.all {}` | `configurations.configureEach {}` |
| Virtual threads | Opt-in, limited | `spring.threads.virtual.enabled=true` |
| Jackson API classes | `com.fasterxml.jackson.databind.*` | `tools.jackson.databind.*` (annotations unchanged) |
| Testcontainers module | `org.testcontainers:postgresql` | `org.testcontainers:testcontainers-postgresql` |
| Mocking in slices | `@MockBean` / `@SpyBean` | `@MockitoBean` / `@MockitoSpyBean` |
| `@WebMvcTest` provided by | `spring-boot-starter-test` | `spring-boot-starter-webmvc-test` |
| Container datasource wiring | `@DynamicPropertySource` | `@ServiceConnection` |