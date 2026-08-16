# Dependencies

## Libraries as guardrails

A validated library is feedforward: it removes the generation problem rather
than checking the result. "Write correct retry and backoff logic" becomes "call
resilience4j or tenacity correctly", which the compiler or type checker can
verify. Correctness was established once, and every call site inherits it.

This matters more with agents than with people. Generating code is nearly free
for an agent, so the friction that pushes a human towards a dependency does not
exist. Left alone, agents hand-roll retries, parsing, pagination, crypto and
money handling — and commit analyses from the AI era show exactly that
signature, with duplication rising and reuse falling.

Making it stick means banning the hand-rolled alternative rather than merely
discouraging it: a preference in an instructions file is inferential
feedforward, the weak quadrant, where Semgrep rules, ArchUnit rules and
banned-import checks are the enforceable version. It also means making the
sanctioned path the cheap one — a reference file mapping solved problems to
their libraries beats ten prohibitions, because agents follow affordances.
And it means distinguishing popular libraries from internal ones. Agents
know Spring, Guava, pandas and tenacity well, so mandating them lowers error
rates for free; internal libraries are invisible to the model, so mandating
them costs accuracy unless repaid with documented API surface or generated
stubs.

## Supply chain

More dependencies means more attack surface, and agents hallucinate package
names — slopsquatting is an exploited attack, not a theoretical one. Gates by
risk:

| Risk | Guardrail | Java | Python |
|---|---|---|---|
| Known CVEs | Scan as build gate with severity threshold | OWASP Dependency-Check, Grype | pip-audit, Grype |
| Hallucinated or typosquatted packages | Curated registry as sole resolvable source | Artifactory/Nexus virtual repo | Same proxy; pinned index, no fallback |
| Malicious behaviour in new packages | Behavioural analysis at PR time | Socket.dev, Snyk | Socket.dev, GuardDog |
| Compromised maintainer releases | Version cooldown, security updates exempt | Renovate minimumReleaseAge | Same |
| Tampered artefacts | Checksum and signature verification | Gradle dependency verification, sigstore | PyPI attestations, hash-checking mode |
| Abandoned or low-quality libraries | Scorecard threshold as PR gate | OpenSSF Scorecard via deps.dev | Same |
| Licence risk | Allowlist gate | Gradle License Report | pip-licenses, licensecheck |
| Unknown transitive surface | SBOM per build, diffed per PR | CycloneDX | CycloneDX, Syft |

Three to implement first, roughly an hour each, and they compose:

1. Lockfile-only installs are prevention rather than detection: a hallucinated
   package becomes a resolution failure. A curated proxy is the full version;
   frozen lockfiles plus a CI rule on lockfile diffs is the version that works
   without running Artifactory.
2. A cooldown period catches the rest. The xz-utils, ultralytics and
   tj-actions incidents all followed the same shape — malicious version
   published, caught, pulled within days — so a seven-day minimum release age
   is one line of config.
3. A Scorecard gate keeps quality visible at the point a dependency is added.
   deps.dev exposes results via API, so failing a PR when a newly added
   dependency scores below threshold is a short script. It also legitimises
   adding dependencies, which is the direction we want the agent pushed.

Start with the open stack — OSV-backed scanners, Scorecard, sigstore, Renovate.
Add a commercial behavioural scanner only once young or small packages become
load-bearing.
