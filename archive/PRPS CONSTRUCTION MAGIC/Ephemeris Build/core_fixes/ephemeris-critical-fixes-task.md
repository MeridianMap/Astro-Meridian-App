# TASK PRP: Ephemeris Critical Fixes

## Feature Goal
Fix immediate data consistency issues in the Meridian Ephemeris system that cause client confusion and API inconsistency.

## Deliverable
- Fixed stars count field naming consistency
- Standardized house system terminology 
- Basic angles aspects implementation
- All existing functionality preserved

## Success Definition
- Zero breaking changes to existing API responses
- All identified inconsistencies resolved
- Performance maintained at <100ms median response time
- 100% test coverage for fixes

## Context

### Documentation
```yaml
docs:
  - url: https://github.com/aloistr/swisseph/blob/master/src/swephexp.h
    focus: "Fixed star functions and constants"
  - url: https://www.astro.com/swisseph/swephprg.htm#_Toc46391648
    focus: "House system calculations"
```

### Patterns to Follow
```yaml
patterns:
  error_handling:
    - file: backend/app/api/routes/ephemeris.py
      copy: "lines 45-67 JSONResponse error pattern"
      example: "InputValidationError → 400, CalculationError → 500"
      
  calculation_pattern:
    - file: backend/app/core/ephemeris/charts/natal.py
      copy: "lines 84-120 thread-safe calculation with caching"
      follow: "ThreadPoolExecutor + _calculation_lock pattern"
      
  test_structure:
    - file: backend/tests/api/routes/test_ephemeris.py
      copy: "lines 108-150 test class structure"
      follow: "get_basic_request() factory pattern"
      
  api_response:
    - file: backend/app/api/models/schemas.py
      copy: "lines 89-156 response model pattern"
      follow: "success, data, metadata structure"
```

### Gotchas
```yaml
gotchas:
  - issue: "Fixed stars count field used in multiple places"
    fix: "Search all files for 'foundation_24_count' before changing"
    command: "cd backend && grep -r 'foundation_24_count' --include='*.py'"
    
  - issue: "House system terminology in cache keys"
    fix: "Clear cache after terminology changes"
    impact: "Redis cache keys may become invalid"
    
  - issue: "Angles aspects affect performance"
    fix: "Use vectorized calculations like existing aspects"
    reference: "backend/app/core/ephemeris/tools/aspects.py:94-172"
```

## Implementation Tasks

### TASK 1: Fix Fixed Stars Count Field Naming
```yaml
MODIFY backend/app/core/ephemeris/tools/fixed_stars.py:
  - REPLACE: "foundation_24_count": 23 → "selected_stars_count": 23 (line ~471)
  - ADD: metadata dict with selection_criteria field
  - UPDATE: docstrings to reflect new field name
  VALIDATE: "cd backend && python -m pytest tests/core/ephemeris/test_fixed_stars.py::test_star_count_naming -v"
  IF_FAIL: "Check for other references with: grep -r 'foundation_24_count' backend/"
  ROLLBACK: "Git revert specific commit, verify tests pass"
```

### TASK 2: Update API Response Schema
```yaml
MODIFY backend/app/api/models/schemas.py:
  - LOCATE: FixedStarsResult model (around line ~200)
  - REPLACE: foundation_24_count field definition
  - ADD: selected_stars_count: int = Field(..., description="Number of selected stars")
  - ADD: selection_criteria: Optional[Dict] = Field(None, description="Star selection metadata")
  VALIDATE: "cd backend && python -c 'from app.api.models.schemas import FixedStarsResult; print(FixedStarsResult.__fields__)'"
  IF_FAIL: "Check Pydantic field definition syntax"
  ROLLBACK: "Restore original field definition"
```

### TASK 3: Standardize House System Terminology
```yaml
MODIFY backend/app/core/ephemeris/const.py:
  - LOCATE: HOUSE_SYSTEMS mapping (around line ~45)
  - REPLACE: all instances of "P" with "placidus"
  - ENSURE: consistent string values across all house system references
  VALIDATE: "cd backend && python -c 'from app.core.ephemeris.const import HOUSE_SYSTEMS; print(HOUSE_SYSTEMS)'"
  IF_FAIL: "Check for typos in house system names"
  ROLLBACK: "Restore original HOUSE_SYSTEMS mapping"
```

### TASK 4: Update House System Usage
```yaml
MODIFY backend/app/core/ephemeris/charts/natal.py:
  - LOCATE: house calculation method (around line ~350)
  - REPLACE: any "P" references with "placidus"
  - VERIFY: Swiss Ephemeris call uses correct constant
  VALIDATE: "cd backend && python -m pytest tests/core/ephemeris/test_natal.py::test_house_system_consistency -v"
  IF_FAIL: "Check Swiss Ephemeris house system constants"
  ROLLBACK: "Restore original house system references"
```

### TASK 5: Clear Cache After Terminology Changes
```yaml
EXECUTE backend/scripts/clear_cache.py:
  - RUN: cache clearing for house system changes
  - TARGET: both Redis and memory caches
  - VERIFY: new requests use updated terminology
  VALIDATE: "cd backend && python scripts/verify_cache_clear.py"
  IF_FAIL: "Manually clear Redis: redis-cli FLUSHALL"
  ROLLBACK: "Not applicable - cache clearing is safe"
```

### TASK 6: Implement Basic Angles Aspects
```yaml
MODIFY backend/app/core/ephemeris/tools/aspects.py:
  - LOCATE: AspectCalculator class (line ~71)
  - ADD: calculate_angle_aspects method following vectorized pattern (line ~94)
  - COPY: orb configuration pattern from existing aspects
  - INTEGRATE: with existing AspectResult model
  VALIDATE: "cd backend && python -m pytest tests/core/ephemeris/test_aspects.py::test_angle_aspects -v"
  IF_FAIL: "Check angle position extraction from ChartData"
  ROLLBACK: "Remove calculate_angle_aspects method"
```

### TASK 7: Add Angle Aspect Integration
```yaml
MODIFY backend/app/core/ephemeris/charts/natal.py:
  - LOCATE: aspect calculation section (around line ~280)
  - ADD: call to calculate_angle_aspects after planet aspects
  - MERGE: angle aspects with existing planet aspects
  - MAINTAIN: existing response structure compatibility
  VALIDATE: "cd backend && python -m pytest tests/core/ephemeris/test_natal.py::test_complete_aspects -v"
  IF_FAIL: "Check aspect merging logic"
  ROLLBACK: "Remove angle aspect integration code"
```

### TASK 8: Update Test Suite
```yaml
CREATE backend/tests/core/ephemeris/test_critical_fixes.py:
  - ADD: test_fixed_stars_count_field_naming()
  - ADD: test_house_system_terminology_consistency()
  - ADD: test_angle_aspects_basic_functionality()
  - FOLLOW: existing test patterns from test_ephemeris.py:108-150
  VALIDATE: "cd backend && python -m pytest tests/core/ephemeris/test_critical_fixes.py -v"
  IF_FAIL: "Check test setup and fixture imports"
  ROLLBACK: "Delete test file"
```

## Task Dependencies
```yaml
task_dependencies:
  schema_update:
    depends_on: ["fixed_stars_field_fix"]
    reason: "Schema must match implementation"
    
  cache_clear:
    depends_on: ["house_system_standardization"]
    reason: "Cache contains old terminology"
    
  angle_aspects_integration:
    depends_on: ["angle_aspects_implementation"]
    reason: "Method must exist before integration"
    
  test_creation:
    depends_on: ["all_implementation_tasks"]
    reason: "Tests validate completed implementations"
```

## Final Validation Checklist

### Functional Validation
```bash
# Test all fixed functionality
cd backend && python -m pytest tests/core/ephemeris/test_critical_fixes.py -v

# Verify API response consistency
cd backend && python scripts/test_api_consistency.py

# Check performance maintained
cd backend && python scripts/benchmark_ephemeris.py --baseline
```

### Integration Validation
```bash
# Full integration test suite
cd backend && python -m pytest tests/integration/ -v

# API contract validation
cd backend && python scripts/validate_api_contracts.py --endpoint /ephemeris/natal
```

### Regression Validation
```bash
# Existing functionality unchanged
cd backend && python -m pytest tests/api/routes/test_ephemeris.py -v

# Performance regression check
cd backend && python scripts/performance_regression_test.py --threshold 100ms
```

## Success Metrics
- [ ] Zero breaking API changes
- [ ] All inconsistencies resolved
- [ ] Performance <100ms maintained
- [ ] 100% test coverage for new code
- [ ] All existing tests still pass

## Rollback Strategy
1. **Git revert** specific commits for each task
2. **Clear caches** to remove any cached inconsistent data
3. **Run full test suite** to verify rollback success
4. **Performance benchmark** to ensure rollback complete

## Notes
- This is a **low-risk, high-impact** set of fixes
- Changes are **backwards compatible** 
- Focus on **consistency and clarity** without breaking existing functionality
- **Performance impact should be minimal** due to vectorized calculations pattern