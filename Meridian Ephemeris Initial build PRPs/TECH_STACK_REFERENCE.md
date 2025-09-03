# Meridian Ephemeris – Technology Stack Reference

Canonical inventory of technologies, versions (where known), rationale, and replacement considerations.

## 1. Languages & Runtimes
| Layer | Tech | Version (current) | Rationale | Notes |
|-------|------|-------------------|-----------|-------|
| Backend | Python | 3.10.x | Ecosystem maturity, scientific libs | 3.11 speedups a future target |
| Frontend (planned) | TypeScript | 5.x (assumed) | Type safety + large ecosystem | PWA via Vite |
| Infra scripts | Shell / PowerShell | N/A | Cross-platform ops | run_tests.ps1 for Windows dev |

## 2. Core Libraries
| Category | Library | Purpose | Status |
|----------|---------|---------|--------|
| Web Framework | FastAPI | Async API | Stable |
| Data Validation | Pydantic v2 | Schemas & settings | Migration cleanup needed (dict->model_dump) |
| Astro Engine | pyswisseph (Swiss Ephemeris) | Planetary & house calcs | Gold standard |
| Numerics | NumPy, Numba | Vectorization, performance | Used in batch paths |
| Timezones | timezonefinder, tzdata | TZ inference & portability | Add coordinate cross-check soon |
| Caching | Custom LRU, Redis (hiredis) | Performance improvement | Redis layer partial |
| Monitoring | prometheus-client | Metrics export | Needs coverage tests |
| Logging | structlog | Structured logs | Ensure config centralization |
| Testing | pytest (+xdist, cov, benchmark, json-report) | Test suite / performance | Benchmarks auto-disabled under xdist |
| Packaging | Docker / docker-compose | Runtime encapsulation | Production ready plan |
| Docs | MkDocs Material | Human docs | Present |
| SDK Gen | openapi.json (+ custom scripts) | Client generation | Scripts present (python/go/ts) |
| Load Testing | k6 (JavaScript scripts) | Throughput validation | Scripts exist |

## 3. Optional / Planned
| Area | Candidate | Trigger Condition |
|------|----------|------------------|
| GraphQL | Strawberry GraphQL | When clients need flexible querying |
| Rust Speedups | PyO3 modules | Profiling identifies hot loops unsuited to NumPy |
| Tracing | OpenTelemetry | Distributed tracing across services |
| Error Tracking | Sentry | Production deployment phase |
| Background Jobs | Celery / RQ / Dramatiq | Long-running or queued tasks (bulk chart sets) |

## 4. Service Responsibilities
| Service/Module | Responsibility | Replacement Risk |
|----------------|----------------|-----------------|
| `ephemeris.py` | SwissEp interface | Low (core) |
| `batch.py` | Vector batch engine | Medium (perf sensitive) |
| `cache.py` | Memory cache | Low |
| `redis_cache.py` | Redis integration | High (incomplete) |
| `acg_*` | ACG line calculations | Medium (domain complexity) |
| `metrics.py` | Metric export | Medium (observability correctness) |

## 5. External Data & Assets
| Asset | Source | Use | Notes |
|-------|--------|-----|-------|
| Swiss Ephemeris data files | astro.com | Core calc data | Must be bundled/mounted |
| Fixed star catalog | Swiss Ephemeris | Extended objects | Verified integrity required |

## 6. Build & Automation
| Pipeline Step | Tooling | Artifacts |
|---------------|---------|----------|
| Lint | ruff | Style & static checks |
| Type Check | mypy | Type safety gating |
| Test | pytest | junit.xml, coverage HTML, JSON report |
| Docs | mkdocs | Static site |
| SDK Gen | scripts/generate-sdks.py | Language SDK packages |
| Bench / Load | pytest-benchmark, k6 | Benchmark JSON, load stats |

## 7. Versioning Strategy
- Semantic for API: v1.x stable; v2 reserved for breaking fields/structures.
- Library pins in `requirements-prod.txt` for deterministic builds.
- Recommendation: introduce Dependabot / Renovate for controlled upgrades.

## 8. Risk & Replacement Matrix
| Component | Current Risk | Mitigation |
|-----------|--------------|------------|
| Redis cache (partial) | Logic divergence / low coverage | Add integration tests or disable until needed |
| Pydantic migration gaps | Deprecation warnings | Replace `.dict()` & `.parse_obj()` usages |
| Performance assumptions | Drift over time | Scheduled benchmark CI job |
| Metrics completeness | Potential blind spots | Add unit + integration tests for emitted metrics |

## 9. Compliance & Licensing
| Library | License | Notes |
|---------|---------|------|
| FastAPI | MIT | Compatible |
| pyswisseph | GPL-like (Swiss Ephemeris license) | Confirm redistribution terms if SaaS |
| NumPy | BSD | OK |
| Numba | BSD | OK |
| Prometheus client | Apache 2 | OK |
| structlog | MIT | OK |

## 10. Upgrade Roadmap
| Target | Benefit | Action |
|--------|---------|--------|
| Python 3.11 | Perf + typing | Run test suite under 3.11 matrix |
| FastAPI >=0.110 | Bug fixes / features | Validate openapi schema stability |
| Adopt Ruff for format (instead of black) | Single toolchain | Configure `ruff format` pipeline |
| Add mypy strict mode | Bug prevention | Gradually enable per module |

---
Status: Living document. Update when adding new infra/services.
