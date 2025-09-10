# PRP: Service Layer Optimization & Response Slimming

## Feature Goal
Refactor service layer to selectively assemble astrology feature data with <50KB response size while preserving professional calculation engines.

## Deliverable
- New ProfessionalEphemerisService
- ResponseOptimizer (size gating + selective inclusion)
- Feature flags & option model
- Caching coordinator (chart-level reuse)

## Success Definition
- Full feature chart (core + aspects + lots + fixed stars) <50KB
- Core-only chart <15KB
- Calculation time <100ms (uncached) <30ms (cached)

## Context
```yaml
docs:
  - url: https://fastapi.tiangolo.com/advanced/response-directly/
    focus: optimized response handling
  - url: https://pydantic-docs.helpmanual.io/usage/exporting_models/
    focus: model_dump optimization
patterns:
  - file: backend/app/services/ephemeris_service.py
    anti_pattern: kitchen sink response assembly
  - file: backend/app/core/ephemeris/tools/*
    preserve: calculation engines unchanged
gotchas:
  - issue: nested model expansion huge
    fix: explicit projection in serializer
  - issue: repeated recalculation
    fix: pass shared chart context object
  - issue: large floats inflate JSON
    fix: round to 4 decimals
```

## Tasks
```yaml
create_service:
  action: CREATE
  file: backend/app/services/pro_ephemeris_service.py
  contents: new streamlined service

implement_optimizer:
  action: CREATE
  file: backend/app/services/response_optimizer.py
  contents: size enforcement & projection

wire_api:
  action: MODIFY
  file: backend/app/api/routes/*.py
  changes: use ProfessionalEphemerisService

add_tests:
  action: CREATE
  file: tests/service/test_response_size.py
  contents: asserts size thresholds

perf_bench:
  action: CREATE
  file: tests/perf/test_service_perf.py
  contents: timing measurements
```

## Validation Checklist
- [ ] New service returns core chart
- [ ] All feature flags work independently
- [ ] Combined features <50KB
- [ ] Core <15KB
- [ ] Timing targets met
- [ ] No calculation engine modifications

## Rollback
Switch imports back to legacy service and remove new files.

## Confidence
8/10
