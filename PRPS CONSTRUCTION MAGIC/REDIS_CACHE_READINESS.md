# Redis Cache Readiness Assessment

Evaluate current state of Redis integration and define steps to productionize or defer.

## 1. Current Implementation Snapshot
| Aspect | Status | Notes |
|--------|--------|-------|
| redis_cache.py presence | Implemented (large, low coverage) | 23% coverage (lines) |
| Serialization strategy | Pydantic `.dict()` usage | Needs v2 migration (`model_dump()`) |
| Error handling | Basic try/except | Lacks granular exception classes |
| Key namespace strategy | Partially hardcoded | Needs consistent prefixing (e.g. `meridian:`) |
| TTL handling | Present | Verify edge conditions (0 / None) |
| Metrics hooks | Not evident | Add hits, misses, errors |
| Fallback on failure | Not formalized | Should degrade to memory cache |

## 2. Risks
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| Silent cache corruption | Incorrect responses | Medium | Add value schema validation before return |
| Connection saturation | Elevated latency | Medium | Use connection pooling + timeouts |
| Serialization drift | Data shape mismatch | High | Version + schema hash prefix |
| Redis outage | Request slowdown | Medium | Circuit breaker + fallback |

## 3. Production Readiness Criteria
| Criterion | Target | Status |
|----------|--------|-------|
| Coverage | ≥80% lines & branches | Not met |
| Integration tests | Start/stop ephemeral Redis in CI | Not present |
| Observability | Metrics + structured logs for ops | Missing |
| Configuration | Env-driven URL, auth, TLS | Partial |
| Failure Policy | Explicit fallback & alerting | Missing |
| Key Versioning | `v1:` prefix | Missing |
| Security | AUTH password or ACL enforced | Unknown |

## 4. Required Enhancements
1. Migrate serialization to Pydantic v2 (`model_dump`, `model_validate`).
2. Introduce a RedisCache interface implementing `get/set/delete/clear/stats`.
3. Wrap calls with timeout & retry (exponential backoff, small attempts).
4. Add key builder utility: `build_key(domain: str, parts: dict, version='v1')`.
5. Validate cached payload structure on retrieval; if invalid, purge + recompute.
6. Instrument Prometheus counters: `cache_redis_hits_total`, `cache_redis_misses_total`, `cache_redis_errors_total`.
7. Circuit breaker: after N consecutive errors, disable Redis for window.
8. Add integration tests with ephemeral container (docker or testcontainer-py).
9. Provide feature flag: `ENABLE_REDIS_CACHE` (env) gating usage.
10. Document operational runbook (flush, inspect key, warm strategy).

## 5. Test Plan Additions
| Test | Purpose |
|------|---------|
| test_redis_hit_miss_cycle | Basic set → get flow |
| test_redis_ttl_expiry | Ensure expiry semantics |
| test_redis_corrupt_payload | Detect & purge invalid data |
| test_redis_timeout_fallback | Simulate slow Redis; fallback path |
| test_circuit_breaker_trip_reset | Reliability of breaker logic |

## 6. Example Key Strategy
```
meridian:v1:natal:{sha256(normalized_request)[:16]}
meridian:v1:acg-lines:{sha256(params)[:16]}
meridian:v1:batch:{batch_size}:{sha256(payload)[:12]}
```

## 7. Fallback Logic (Pseudo)
```
def redis_get_or_fallback(key, compute_fn):
    if not redis_enabled:
        return compute_fn()
    try:
        val = redis.get(key)
        if val:
            return deserialize(val)
    except RedisError:
        disable_temporarily()
    result = compute_fn()
    try_store_async(key, result)
    return result
```

## 8. Go / No-Go Decision Matrix
| Condition | Action |
|-----------|--------|
| Enhancements complete + tests green + load test stable | Enable Redis in production |
| Partial implementation, missing coverage | Keep disabled; rely on memory cache |
| Frequent transient errors | Deploy with circuit breaker & shorter TTL |

## 9. Timeline (Suggested)
| Week | Task |
|------|------|
| 1 | Refactor serialization + key builder + metrics |
| 2 | Add tests + circuit breaker + feature flag |
| 3 | Load test with Redis enabled; tune TTL & pool |
| 4 | Production canary, monitor hit rate & latency |

## 10. Recommendation (Current State)
Defer production activation until coverage + observability criteria met. In the interim, explicitly disable Redis via config to avoid silent partial use.

---
Status: Use as readiness gate before enabling Redis in staging/prod.
