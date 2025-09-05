# Meridian Ephemeris – Backend Flow Guide

End-to-end execution narratives for principal operations, plus sequence diagrams (textual) for agentic reasoning.

## 1. Request Lifecycle (General)
```
Client -> ASGI Server (uvicorn) -> FastAPI Router -> Dependency Resolution -> Pydantic Validation ->
Service Orchestration -> Core Computations (Swiss Ephemeris) -> Aggregation / Formatting ->
Caching (write) -> Response Serialization -> Middleware (headers, metrics) -> Client
```

### Key Middleware / Hooks
| Stage | Responsibility |
|-------|----------------|
| Startup | Load settings, optionally validate ephemeris path |
| Request | Timing start, rate-limit check (if enabled) |
| Route Handler | Validation + service logic |
| Response | Add performance headers, metrics increment |
| Exception Handler | Uniform error contract |

## 2. Sequence: Natal Chart
```
Participant Client
Participant API (FastAPI)
Participant SubjectNormalizer
Participant EphemerisCore
Participant Cache

Client->API: POST /ephemeris/natal (JSON)
API->SubjectNormalizer: normalize(subject payload)
SubjectNormalizer->EphemerisCore: build JD + call get_planet() x N
EphemerisCore->EphemerisCore: houses/angles computation
EphemerisCore->Cache: (optional) lookup/store
EphemerisCore->API: Chart components
API->Client: JSON (chart + metadata)
```

### Detailed Steps
1. Parse `NatalChartRequest` (subject + settings). 422 on invalid.
2. Normalize coordinates & timezone -> UTC datetime -> Julian Day.
3. Planet loop: for each planet id -> Swiss Ephemeris call -> PlanetPosition.
4. House system & angles (Asc, MC, DC, IC) computed.
5. (Optional) Aspect matrix calculation.
6. Assemble `NatalChart` object -> serialize.
7. Include metadata: processing time, cache_hit flag.

## 3. Sequence: Batch Natal
```
Client->API: POST /ephemeris/batch (subjects[])
API->Validator: size & shape checks
API->BatchCalculator: vectorized JD array
BatchCalculator->EphemerisCore: planetary arrays
BatchCalculator->API: list[BatchResult]
API->Client: JSON array (success/error per subject)
```

### Performance Considerations
- Shared arrays reduce Python loop overhead.
- Cache use is reduced benefit unless many subjects share identical inputs.

## 4. Sequence: ACG Lines
```
Client->API: POST /acg/lines
API->Validator: epoch + natal base data
API->ACGCore: compute planetary angular loci
ACGCore->EphemerisCore: planetary positions (baseline + projections)
ACGCore->Cache: store/retrieve result key
ACGCore->API: line structures (per planet, line type; designed for 3D globe/Three.js visualization)
API->Client: JSON lines + metadata
```

### Line Computation Outline
1. Determine which planetary angles (e.g., MC, IC, ASC, DSC) to map.
2. For each longitude sweep or grid cell -> solve for where body culminates/rises/sets.
3. Collect lines (polyline segments) tagged with planet & angle type.
4. Compress / simplify (future optimization).

## 5. Sequence: ACG Animation
```
Client->API: POST /acg/animate (start, end, step)
API->FramePlanner: expand epoch series
Loop (each frame):
  FramePlanner->ACGCore: calculate frame lines
  ACGCore->EphemerisCore: planetary snapshot
After loop: aggregate frames -> API -> Client
```

### Optimizations (Future)
- Reuse planetary ephemeris deltas between frame intervals
- Cache immutable frame segments

## 6. Error Handling Flow
```
Route Handler raises ValueError -> Exception Hook -> Build ErrorResponse -> JSON {"detail": {...}} -> 4xx/5xx
ValidationError (Pydantic) -> FastAPI builtin -> formatted 422 with field errors
Unhandled Exception -> 500 with sanitized message
```

## 7. Caching Flow
```
Call Wrapper -> generate key (function name + args normalized) ->
  if memory_cache.get(key): return value (hit)
  else: compute -> memory_cache.put(key, value, ttl)
  (Redis layer optional placeholder)
```

## 8. Metrics Emission (Planned / Partial)
| Metric | Source | Description |
|--------|--------|-------------|
| request_total | API middleware | Count by path & status |
| request_duration_seconds | Timing wrapper | Histogram of latencies |
| calculation_total | Core wrappers | Count by calc type |
| cache_hits_total / miss_total | Cache class | Cache performance |

## 9. Throughput Benchmarks (Observed)
| Operation | Median (cache miss) | Cache Hit | Notes |
|-----------|---------------------|-----------|-------|
| Single Natal | 35–65ms | 5–15ms | Variation by house system |
| Batch (100) | ~650ms total | N/A | 10x improvement vs serial |
| ACG Lines | 80–150ms | 30–60ms | Depends on options |

## 10. Failure Modes & Mitigations
| Mode | Cause | Mitigation |
|------|-------|-----------|
| High Latency | Missing cache / heavy batch | Increase batch usage, enable Redis |
| Inaccurate Result | Corrupt ephemeris files | Validate on startup with checksum |
| TZ Misalignment | User provided wrong tz | Add coordinate↔timezone validation layer |
| Memory Bloat | Large cache TTL & high churn | Enforce max size + eviction stats monitoring |
| Benchmark Flakiness | Parallel test timing variance | Run benchmarks single-process |

## 11. Extending a Flow (Example: Add Transits)
1. Add `charts/transits.py` with calculation orchestrator.
2. Reuse subject normalization + JD conversions.
3. Add endpoint `/ephemeris/transits` with request schema.
4. Introduce caching decorator or reuse existing.
5. Add tests: unit (transit math), integration (endpoint), performance.

## 12. Agentic Worker Hints
- Prefer batch endpoints when mutating large test corpora.
- Always inspect `openapi.json` for schema evolution before mass generation tasks.
- Leverage `backend/run_tests.ps1` to ensure environment parity prior to scripted refactors.

---
Status: Authoritative flow reference. Update when new endpoints or caching tiers are added.
