# ACG (Astrocartography) Feature Master Context

Agent execution model (Claude Code): claude-3.5-sonnet, temperature 0.1, tools enabled (filesystem/terminal), long timeout. Pin this file and PRPs/contracts/acg-api-contract.md in context; exclude reference/**.

## Module Location
- All ACG (astrocartography) code will reside in `backend/app/core/acg/`
- API endpoints will be under `/acg/` (e.g., `/acg/lines`)
- All files, classes, and functions will use the `acg_` prefix for clarity and future extensibility

## Codebase Integration Points
- Existing ephemeris module: `backend/app/core/ephemeris/`
- Base calculation class to extend: `backend/app/core/ephemeris/base.py`
- Current API router pattern: `backend/app/api/v1/endpoints/`
- Redis cache config: `backend/app/core/config.py`
- Test patterns: `backend/app/tests/conftest.py`

## Feature Scope
- All line types: MC, IC, AC, DC, aspects to AC and MC, and parans, etc.
- All supported bodies: primary planets, asteroids, hermetic lots, fixed stars, lunar nodes, Black Moon Lilith, etc.
- All relevant natal chart data (including planetary dignity, house, retrograde, sign, element, modality, aspects, etc.) must be accessible in the ACG context and metadata

## Dependencies
- pyswisseph>=2.10.0 (Swiss Ephemeris)
- numpy>=1.24.0 (vectorization)
- shapely>=2.0.0 (geometry operations)
- orjson>=3.9.0 (GeoJSON serialization)
- numba>=0.57.0 (optional JIT compilation)

## Metadata Schema (Astrolog-Inspired, Best Practice)
- id: string (e.g., "Sun", "Venus", "Regulus")
- type: string (planet, asteroid, lot, node, fixed_star, etc.)
- number: int (Swiss Ephemeris or internal index)
- epoch: ISO UTC string
- jd: Julian Day
- gmst: Greenwich Mean Sidereal Time (deg)
- obliquity: true obliquity (deg)
- coords: { ra, dec, lambda, beta, distance, speed }
- line: { angle, aspect, line_type, method, segment_id, orb }
- natal: { dignity, house, retrograde, sign, element, modality, aspects }
- flags: Swiss Ephemeris flags used
- se_version: Swiss Ephemeris version
- source: calculation source (e.g., "Meridian-ACG")
- calculation_time_ms: float
- color, style, z_index, hit_radius: for frontend use
- custom: dict (for future extensibility)

## Conventions
- Follow Astrolog’s naming and line conventions for angles, aspects, and parans
- Use snake_case for all JSON keys
- Output GeoJSON FeatureCollections for all map data
- Attach full metadata to each feature
- Use the ACG prefix for all backend code, but not in output metadata

## Testing & Validation
- Automated visual regression tests (compare output to reference images/datasets)
- Cross-validation against Astrolog, Immanuel, and Flatlib outputs
- >90% test coverage, performance benchmarks, and monitoring integration

## Performance & Caching
- Integrate Redis/memory caching for all line calculations
- Optimize for batch and single-chart requests

## Documentation
- All PRPs and supporting docs will be placed in `Meridian Ephemeris Initial build PRPs/ACG prp/`
- Create summary docs in `PRPs/ai_docs/` for any critical external reference


## PRP Dependencies & Data Flow
1. Natal Chart Integration (PRP 7) → provides input to Core Calculations
2. Core Calculations (PRP 1) → produces `ACGResult` type
3. Metadata & Provenance (PRP 5) → enriches all outputs
4. API Endpoints & Data Models (PRP 2) → consumes `ACGResult`, produces `GeoJSON`
5. Caching & Optimization (PRP 3) → wraps calculation functions
6. Test & Validation Suite (PRP 4) → validates all above
7. Batch & Animation Support (PRP 6) → extends single-chart logic
8. Documentation & Example Scripts (PRP 8) → covers all above

## Error Handling
- Use existing `AppException` patterns from `backend/app/core/exceptions.py`
- Validate all inputs with Pydantic models
- Return standardized error responses per API conventions (see API contract template)
- Log all calculation failures with context

## Versioning & Migration
- API version: v2 endpoints under `/api/v2/acg/` (future-proofing)
- Feature flags for gradual rollout
- Database migrations for cached data (if needed)
- Rollback procedure documented in PRPs

## Performance Requirements
- Single chart: <100ms p50, <200ms p95
- Batch (10 charts): <500ms p50, <1s p95
- Cache hit ratio: >80% after warmup
- Memory usage: <100MB per request
- Concurrent requests: 100+ without degradation

## Security
- Input validation for all geographic coordinates
- Rate limiting per existing API patterns
- Sanitize metadata before output
- No PII in cache keys

## Monitoring
- Prometheus metrics: calculation_time, cache_hits, error_rate
- Structured logging with correlation IDs
- Performance traces for slow calculations
- Alert thresholds for error rates

## PRP Breakdown (Dependency Order)
1. ACG Integration with Natal Chart Data (PRP 7)
2. ACG Core Calculations: All Bodies & Features (PRP 1)
3. ACG Metadata & Provenance Handling (PRP 5)
4. ACG API Endpoints & Data Models (PRP 2)
5. ACG Caching & Optimization Layer (PRP 3)
6. ACG Test & Validation Suite (PRP 4)
7. ACG Batch & Animation Support (PRP 6)
8. ACG Documentation & Example Scripts (PRP 8)

---
This file is the single source of truth for the ACG feature build. All PRPs must reference this file for context, conventions, and requirements.
