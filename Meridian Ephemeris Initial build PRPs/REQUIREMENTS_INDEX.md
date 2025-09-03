# Meridian Ephemeris – Requirements Index

Unified mapping of functional & non‑functional requirements across PRP documents, README claims, and inferred backlog items.

## 1. Functional Requirements (FR)
| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| FR-001 | Calculate natal chart with planets, houses, angles | PRP_3, API README | Implemented |
| FR-002 | Support multiple house systems (Placidus, Koch, Equal, etc.) | README Features | Implemented |
| FR-003 | Accept multiple coordinate input formats (decimal, DMS, components) | API README | Implemented |
| FR-004 | Accept multiple datetime formats (ISO, JD, components) | API README | Implemented |
| FR-005 | Timezone support via IANA name or numeric offset | API README | Implemented |
| FR-006 | Batch natal chart calculations | API README | Implemented (optimize further) |
| FR-007 | ACG lines calculation endpoint | ACG PRPs | Implemented |
| FR-008 | ACG animation frames endpoint | ACG PRPs | Implemented |
| FR-009 | Provide schema/metadata endpoints (house systems, objects) | API README | Partial (verify) |
| FR-010 | Expose health & detailed status endpoints | API README | Implemented |
| FR-011 | Provide performance metrics endpoints | README (metrics) | Partial (verify emissions) |
| FR-012 | Provide client SDKs (Python, TS, Go) | PRP 6 | Implemented (automation scripts) |
| FR-013 | Auto-detect timezone from coordinates | README Supported Formats | Beta / Planned |
| FR-014 | Rate limiting (per IP, burst, daily) | README Rate Limits | Partial (confirm code) |
| FR-015 | Cache results (memory + optional Redis) | PRP 7 | Memory OK; Redis partial |
| FR-016 | Provide aspects in natal chart | PRP 3 | Implemented (verify completeness) |
| FR-017 | Provide fixed stars and additional points | PRP 1 scope | Partial (some objects) |
| FR-018 | OpenAPI documentation & interactive UI | README | Implemented |
| FR-019 | Charts for transits/progressions | PRP 3 (optional) | Not started |
| FR-020 | GraphQL API variant | PRP 6 optional | Not started |
| FR-021 | Geocoding / place-name input | Not stated | Not started |
| FR-022 | Timezone↔coordinate consistency validation | Improvement note | Not started |

## 2. Non-Functional Requirements (NFR)
| ID | Requirement | Source | Target | Status |
|----|-------------|--------|--------|--------|
| NFR-001 | Median response time <100ms | README Performance | <100ms | Achieved (natal) |
| NFR-002 | P95 response time <150ms | Benchmarks | <150ms | Likely (needs metrics) |
| NFR-003 | Batch speedup ≥10x vs serial | PRP 7 | 10x | Achieved |
| NFR-004 | Cache hit latency <15ms | Benchmarks | <15ms | Achieved |
| NFR-005 | Test coverage ≥90% | PRP 5 | 90% | Not met (76%) |
| NFR-006 | Cross-platform (Win/Linux/Mac) | PRP 0 | All | Windows validated; Linux CI assumed |
| NFR-007 | Accuracy within 3" arc vs reference | PRP 5 | 3" | Partial (need fixtures) |
| NFR-008 | Observability: metrics + structured logs | README | Full stack | Partial |
| NFR-009 | Zero-downtime deploys | PRP 8 | 0 downtime | Planned |
| NFR-010 | Automated rollbacks on failure | PRP 8 | Auto rollback | Planned |
| NFR-011 | Security: rate limiting, auth layers | Diagram + README | Basic controls | Partial |
| NFR-012 | API backward compatibility for v1.x | Versioning strategy | Stable | In effect |
| NFR-013 | Reproducible builds via pinning | PRP 0 | Locked deps | Achieved |
| NFR-014 | Deterministic caching keys | Cache design | Deterministic | Achieved |
| NFR-015 | Horizontal scalability | Architecture vision | Stateless API | Planned verification |

## 3. Derived / Implied Requirements
| ID | Requirement | Derivation | Status |
|----|-------------|-----------|--------|
| DR-001 | Startup ephemeris file validation | Dependence on Swiss data | Partial (function exists) |
| DR-002 | Graceful failure if ephemeris files missing | Robustness | Partial |
| DR-003 | Performance headers in responses | Monitoring needs | Implemented |
| DR-004 | Consistent error schema across endpoints | Mixed examples | In progress |
| DR-005 | Remove deprecated Pydantic API usage | Upcoming v3 removal | Pending |
| DR-006 | Document coordinate/timezone mismatch policy | Data integrity | Pending |

## 4. Open Gaps & Recommended Actions
| Gap | Impact | Priority | Action |
|-----|--------|---------|--------|
| Coverage 76% < target | Confidence, regression risk | High | Add tests for batch, Redis, metrics |
| Redis cache unverified | Potential runtime failure if enabled | High | Add integration tests or disable flag |
| Error schema inconsistency | Client integration confusion | High | Normalize & update docs |
| Pydantic deprecation warnings | Future breakage | High | Replace dict()/parse_obj() |
| Metrics emission coverage | Blind spots in prod | Medium | Write metric assertion tests |
| Timezone auto-detect Beta | UX ambiguity | Medium | Clarify API contract / flag |
| Geocoding absent | Feature demand (frontend) | Medium | Add external service module |
| Aspects completeness not tested | Domain accuracy | Medium | Add reference fixtures |
| Security (auth/rate limit impl) | Risk in open deployment | Medium | Implement FastAPI dependency / middleware |
| Optimization module (~5% use) | Noise / confusion | Low | Prune or implement properly |

## 5. Traceability Matrix (Excerpt)
| Requirement | Module(s) | Test(s) (representative) |
|-------------|----------|--------------------------|
| FR-001 | charts/natal.py, tools/ephemeris.py | tests/core/ephemeris/... natal tests |
| FR-006 | tools/batch.py | tests/benchmarks/test_performance.py (scaling) |
| FR-007/8 | core/acg/*, api/routes/acg.py | tests/api/routes/test_acg.py, tests/core/acg/* |
| NFR-001 | performance optimizations, cache | benchmarks + headers |
| NFR-005 | overall | coverage report (htmlcov) |

## 6. Backlog Candidates
- Add transits/progressions module
- Add coordinate→timezone auto validation & mismatch policy
- GraphQL endpoint for flexible querying
- Push aspects refactor to modular rules engine
- Add feature flag system (env or settings) for beta features
- Strengthen dependency security scanning

## 7. Acceptance Gates
| Milestone | Criteria |
|-----------|---------|
| Public Beta | FR-001..010 implemented; NFR-001..004 met; error schema stable |
| v1.1 | Redis cache validated; coverage ≥85%; metrics verified |
| v2.0 Planning | Breaking schema changes queued; GraphQL decision; transits module POC |

---
Update this index whenever a PRP is closed or new feature PR is merged.
