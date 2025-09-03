# Meridian Ephemeris – Architecture Overview

## 1. Purpose
Single reference map of the system's technical architecture for humans and agentic workers. Summarizes domains, flows, stack, quality attributes.

## 2. High-Level System Context
```
+-------------+        HTTPS / JSON        +------------------+        Swiss Ephemeris DLL/Data
|  Clients    |  -->  REST / SDK / (PWA) -> | FastAPI Gateway  | -->  Ephemeris Core (calc funcs)
|  (Web, CLI, |                            |  (app.main)      | -->  Redis (optional)
|   SDKs)     | <- metrics / errors ------- |                  | <--  Prometheus scrape / Grafana
+-------------+                             +------------------+
       ^                                                |
       | Installable (PWA)                              v
       +------------------------  Docs / OpenAPI / SDK Generators
```

## 3. Core Domains
| Domain | Responsibilities | Key Modules |
|--------|------------------|-------------|
| Ephemeris Core | Planet/house/angle computations, coordinate & datetime utilities, batching, caching | `app/core/ephemeris/*` |
| Charts | Domain orchestration for natal (and future transits/progressions) | `charts/natal.py`, `charts/subject.py` |
| API Layer | Request validation, response formatting, error handling, performance headers | `app/api/routes/*.py`, `schemas.py` |
| ACG (Astro*Carto*Graphy) | Line calculations, batch & animation, caching | `app/core/acg/*`, `app/api/routes/acg.py` |
| Caching | In‑memory LRU+TTL and (planned/partial) Redis | `classes/cache.py`, `classes/redis_cache.py` |
| Performance & Monitoring | Benchmarks, metrics, optimization hooks | `performance/`, `monitoring/metrics.py`, tests/benchmarks |
| Documentation | MkDocs site, OpenAPI & SDK generation | `docs/`, `scripts/generate-sdks.py` |
| Testing & Validation | Unit, integration, performance, coverage | `tests/`, `run_tests.ps1` |
| Deployment | Docker, docker-compose, CI/CD target | `Dockerfile`, `docker-compose.yml` |

## 4. Technology Stack
| Layer | Tech | Notes |
|-------|------|-------|
| Language | Python 3.10+ | Core backend & engine |
| Framework | FastAPI | Async web framework with Pydantic v2 |
| Astro Engine | Swiss Ephemeris (pyswisseph) | Authoritative astronomical source |
| Data Models | Pydantic | Validation & serialization (migrating from `.dict()` to `.model_dump()`) |
| Performance | NumPy, Numba | Vectorization & potential JIT paths |
| Caching | In-memory LRU, Redis (planned) | Global cache accessor & decorator |
| Monitoring | Prometheus client, Grafana dashboards | Metrics exposure `/metrics` |
| Docs | MkDocs Material, OpenAPI schema | Auto-generated + curated guides |
| SDKs | OpenAPI Generator (TS, Python, Go) | Regeneration script `generate-sdks.py` |
| Tests | pytest, pytest-xdist, pytest-benchmark, coverage | Parallel + performance tracking |
| Packaging | Docker / docker-compose | Local + prod parity |
| Frontend (planned) | Vite + React TS + PWA | Not yet in main path; scaffolding pending |
| Load Testing | k6 / custom JS scripts | `load-testing/` |

## 5. Runtime Components
- FastAPI ASGI app (`app.main:app`)
- Ephemeris Core services (pure functions + orchestrators)
- ACG subsystem (batch lines, animation frames)
- Caches: memory (LRU+TTL), optional Redis (incomplete coverage/tests)
- Metrics & performance instrumentation
- Test harness & benchmarking utilities

## 6. Primary Data Flows
### Natal Chart Calculation
```
Client -> /ephemeris/natal (POST)
  -> Pydantic validation (schemas)
  -> Subject normalization (charts/subject.py)
  -> Core calls: date -> JD, planet positions, houses, angles
  -> Chart assembly (natal.py)
  -> (Optional) aspects, metadata
  -> Response (JSON) + X-Process-Time + cache headers
```

### Batch Processing
```
Client -> /ephemeris/batch
  -> Validate list (size limits, shapes)
  -> Vectorized JD + planetary loops (batch.py)
  -> Aggregate successes/errors
  -> Return array of result objects
```

### ACG Lines / Animation (High-Level)
```
Client -> /acg/lines or /acg/animate
  -> Input epoch & natal base validation
  -> Generate planetary angular loci projected to Earth map
  -> Optional frame iteration (animate)
  -> Cache intermediate results (when enabled)
  -> Return line sets / frame list
```

### Caching Strategy
1. Attempt in-memory cache via deterministic key
2. (Future) Attempt Redis (serialization layer)
3. Compute using Swiss Ephemeris
4. Store back (respect TTL)

## 7. Configuration & Settings
`app/core/ephemeris/settings.py` provides dynamic runtime configuration: ephemeris path, house system defaults, cache enable flags, TTL, coordinate system. Environment variables + potential settings object updates.

## 8. Error Handling & Response Contract
- Uniform error envelope: currently backend migrating to `{"detail": {...}}` shape for FastAPI handlers (some docs show `{"success": false,...}`—align docs soon).
- Validation: 422 for schema errors (lat/lon bounds, datetime parsing, unknown tz).
- Rate limiting (described in README) – implementation hooks not fully enumerated in code excerpt (verify middleware presence).
- Performance headers: `X-Process-Time`, optionally cache status.

## 9. Quality Attributes
| Attribute | Mechanisms |
|-----------|------------|
| Accuracy | Swiss Ephemeris canonical data, reference parity tests planned vs Immanuel |
| Performance | Vectorization (batch.py), caching, parallel test validation |
| Reliability | High test count (520 passing); benchmarks ensure scaling |
| Observability | Prometheus metrics, planned Grafana dashboards, structured logging |
| Extensibility | Modular package boundaries (tools/charts/classes) |
| Portability | Dockerized; tzdata & path handling in settings |

## 10. Current Coverage & Risk Hotspots
| Module | Coverage | Notes |
|--------|----------|------|
| batch processing (`tools/batch.py`) | ~55% | Add error & edge-case tests |
| redis_cache.py | ~23% | Incomplete; decide to finish or remove until needed |
| performance/optimizations.py | ~5% | Largely placeholder; prune or implement |
| metrics.py | ~43% | Add tests for metric emission |
| acg_natal_integration.py | ~67% | Additional integration coverage recommended |

## 11. Pending Technical Debt / Alignments
- Standardize error schema (README vs actual runtime responses).
- Complete Redis cache integration & serialization paths; add tests.
- Replace deprecated Pydantic v2 usages (`dict()`, `parse_obj`) with `model_dump()` / `model_validate()`.
- Improve batch coverage for large size boundaries & partial failures.
- Decide on enabling / removing dormant optimization module & PyO3 stubs.

## 12. Security & Hardening (Planned / Partial)
| Concern | Current | Gap |
|---------|---------|-----|
| AuthZ/AuthN | Mentioned (Auth box in diagram) | Implementation not shown; add JWT/OAuth2 if needed |
| Rate Limiting | Documented in README | Confirm middleware; add tests & headers consistency |
| Input Validation | Strong Pydantic models | Add coordinate/timezone cross-consistency check |
| Dependency Scanning | Not documented | Add CI step (pip-audit, safety) |
| Secrets Management | Env vars | Add .env template & secret rotation guidelines |

## 13. Observability
- Metrics: request counts, durations, calculation counts, cache hit ratio (some may be placeholders—verify emission in metrics module).
- Logging: Structlog or standard logging configured for JSON (as per README statement).
- Future: Sentry / OpenTelemetry integration for tracing.

## 14. Deployment Model
- Containerized (Dockerfile + docker-compose for local). CI/CD described at PRP_8 level; production path: build image -> test -> deploy -> monitor -> rollback.
- Ephemeris data volume must be mounted/readable; path configured via settings.

## 15. Extensibility Roadmap
| Feature | Strategy |
|---------|----------|
| Transits/Progressions | New chart modules reusing core tools |
| GraphQL API | Layer Strawberry schema over service layer |
| Additional Celestial Objects | Extend const enumerations + ephemeris function wrappers |
| PWA Frontend | React/Vite PWA consuming existing REST + future WebSocket streaming (optional) |
| Push / Background Jobs | Add task runner (RQ/Celery/FastAPI background tasks) |

## 16. File & Module Quick Index (Selected)
```
backend/app/core/ephemeris/tools/ephemeris.py   # Swiss Ephemeris interface
backend/app/core/ephemeris/tools/date.py        # Datetime parsing & JD conversion
backend/app/core/ephemeris/tools/convert.py     # Coordinate/time conversion utilities
backend/app/core/ephemeris/tools/batch.py       # Vectorized batch calculator
backend/app/core/ephemeris/classes/cache.py     # LRU+TTL memory cache + decorator
backend/app/core/ephemeris/charts/natal.py      # Natal chart orchestration
backend/app/api/routes/ephemeris.py             # Primary ephemeris endpoints
backend/app/api/routes/acg.py                   # ACG endpoints (lines, animate, batch)
backend/app/services/ephemeris_service.py       # Service facade wiring charts to API
```

## 17. Data Model Highlights
| Model | Purpose | Key Fields |
|-------|---------|------------|
| ChartSubject | Normalized subject input | name, datetime, lat, lon, timezone |
| PlanetPosition | Planet data | longitude, latitude, distance, speed, retrograde |
| HouseSystem | House cusps & angles | cusps[12], angles{asc,mc,dc,ic} |
| NatalChart | Aggregated chart | subject, planets, houses, aspects, metadata |
| BatchRequest / BatchResult | Batch input/output | id/name, success, data/error |
| ACGRequest / ACGResult | ACG calculations | natal base, options, lines data |

## 18. Testing Architecture
| Layer | Examples |
|-------|----------|
| Unit | planets, houses, conversions |
| Integration | /ephemeris/natal, ACG endpoints |
| Performance | tests/benchmarks/test_performance.py |
| Validation | fixture parity (Immanuel) planned / partial |
| Cache Behavior | ACG cache tests, memory cache stats |

## 19. Operational Runbook (Concise)
| Action | Commands |
|--------|----------|
| Run API | `uvicorn app.main:app --port 8000` |
| Full test suite | `backend/run_tests.ps1` (PowerShell) |
| Coverage report | Open `backend/htmlcov/index.html` after tests |
| Generate SDKs | `python scripts/generate-sdks.py` |
| Build docs | `python scripts/build-docs.py` then `mkdocs serve` |

## 20. Glossary
| Term | Definition |
|------|------------|
| JD | Julian Day – continuous day count used in astronomy |
| ACG | Astrocartography – mapping planetary angular lines on Earth |
| House System | Method of dividing ecliptic/space around Earth into 12 houses |
| Aspect | Angular relationship between two planets (e.g., trine, square) |

---
**Status (2025-08-22)**: Core stable (520 tests passing). Key next steps: finalize Pydantic v2 migration; clarify error schema; expand coverage for batch & Redis; implement coordinate-timezone cross validation; integrate frontend PWA.
