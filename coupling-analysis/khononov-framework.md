# Khononov Coupling Framework

Reference material from "Balancing Coupling in Software Design" by Vlad Khononov.

## The Three Dimensions

Coupling cost = **Strength × Distance × Volatility**

All three must be considered together. High coupling in one dimension can be offset by low coupling in others.

## Integration Strength (Weakest to Strongest)

### 1. Signature Coupling
- Components share only primitive types or language-native types
- Example: `processOrder(orderId: String, amount: BigDecimal)`
- **Risk**: Very low — changes rarely cascade

### 2. Contract Coupling  
- Components share a defined interface/contract
- Example: REST API contract, interface definitions, DTOs
- **Risk**: Low — contract can evolve independently of implementation
- **Best practice**: Use versioned contracts

### 3. Model Coupling
- Components share domain model objects
- Example: Passing `Order` entity between services
- **Risk**: Medium — model changes affect all consumers
- **Mitigation**: Anti-corruption layers, separate read/write models

### 4. Functional Coupling
- Component A depends on specific behaviour of component B
- Example: Expecting a service to validate before persisting
- **Risk**: High — behaviour changes break dependents
- **Indicator**: Tests that mock complex behaviours

### 5. Intrusive Coupling
- Component accesses internals of another
- Example: Reflection, accessing private fields, database shared between services
- **Risk**: Critical — any internal change causes breakage
- **Smell**: `setAccessible(true)`, direct DB access across modules

## Distance Categories

### Same Aggregate
- Objects within single aggregate root
- High coupling acceptable — they change together by definition

### Same Bounded Context
- Components share ubiquitous language
- Model coupling acceptable
- Functional coupling tolerable with care

### Different Bounded Contexts
- Require anti-corruption layer
- Only contract coupling acceptable
- Use integration events, not shared databases

### Different Systems
- Maximum distance
- Only signature or contract coupling
- Async communication preferred

## Volatility Assessment

### Stable Components (Low Volatility)
- Core domain logic
- Mature, well-tested code
- Rarely changes (< monthly)
- **Safe to couple to**

### Moderate Volatility
- Business rules that evolve
- Feature code
- Changes weekly/monthly
- **Couple via abstractions**

### High Volatility
- Experimental features
- Integration code
- External service adapters
- **Isolate behind interfaces**

### Indicators of Volatility
```bash
# Git-based volatility score
git log --format=format: --name-only --since="1 year ago" FILE | wc -l
```
- 1-5 changes/year: Stable
- 6-20 changes/year: Moderate  
- 20+ changes/year: Volatile

## Anti-Patterns

### Shared Database
- **Problem**: Intrusive coupling at maximum distance
- **Solution**: API-based integration, event-driven sync

### Distributed Monolith
- **Problem**: Services coupled at model level across network
- **Solution**: Proper bounded context decomposition

### Anemic Domain Model
- **Problem**: Functional coupling — behaviour scattered across services
- **Solution**: Rich domain model with encapsulated behaviour

### Shotgun Surgery
- **Problem**: Single change requires many file modifications
- **Indicator**: High temporal coupling in git history
- **Solution**: Better cohesion, single responsibility

## Healthy Coupling Patterns

### Ports and Adapters
- Domain core has zero outward dependencies
- Infrastructure adapts to domain interfaces
- Distance enforced via package structure

### Anti-Corruption Layer (ACL)
- Translates external models to internal
- Reduces model coupling across boundaries
- Isolates volatility of external systems

### Event-Driven Integration
- Contract coupling via event schemas
- Temporal decoupling
- Volatility isolated by async nature

### Dependency Inversion
- Depend on abstractions, not implementations
- Stable interface, volatile implementation
- Direction points toward stability
