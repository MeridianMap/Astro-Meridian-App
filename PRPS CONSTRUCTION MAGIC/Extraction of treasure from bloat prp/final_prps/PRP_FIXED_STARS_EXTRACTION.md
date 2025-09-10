# EXTRACTION PRP: Fixed Stars Professional System

## Feature Goal
Extract complete professional Fixed Stars implementation.

## Deliverable
- FixedStarCalculator (564 lines) preserved
- Star registry (Foundation 24 + Extended 77)
- Magnitude filtering operational
- Swiss Ephemeris integration intact
- Tests + validation harness

## Success Definition
- All foundation stars return valid positions
- Royal stars present and accurate
- Single star calc <10ms; batch <50ms

## Context
```yaml
docs:
  - url: https://pyswisseph.readthedocs.io/en/latest/api.html#swe.fixstar
    focus: fixed star calculation parameters
  - url: https://github.com/astrorigin/pyswisseph/blob/master/pyswisseph/__init__.py#L1847
    focus: swe.fixstar return values and error codes
patterns:
  - file: backend/app/core/ephemeris/tools/fixed_stars.py
    preserve: FixedStarCalculator class lines 1-564
    copy: "_setup_swiss_ephemeris_path() method lines 45-67"
  - file: backend/app/services/ephemeris_service.py
    preserve: path setup pattern lines 156-189
dependencies:
  external:
    - pyswisseph>=2.10.3
    - pydantic>=2.0,<3.0
  data_files:
    - Swiss Eph Library Files/sefstars.txt (CRITICAL)
    - Swiss Eph Library Files/seas_18.se1
  provides:
    - FixedStarCalculator
    - star_registry (Foundation 24 + Extended 77)
    - swiss_ephemeris_path_setup
gotchas:
  - issue: path must be set before swe.fixstar
    fix: call _setup_swiss_ephemeris_path once in __init__
    file: backend/app/core/ephemeris/tools/fixed_stars.py:45
  - issue: star names must match catalog exactly
    fix: use registry canonical names, not common names
    example: "Regulus" not "Alpha Leonis"
  - issue: magnitude filtering affects performance significantly
    fix: pre-filter by magnitude before expensive Swiss Eph calculations
  - issue: sefstars.txt catalog must be in correct location
    fix: verify file exists before attempting star calculations
import_fixes:
  - from: "from backend.app.core.ephemeris.models"
    to: "from extracted.systems.models"
  - from: "from app.services"
    to: "from extracted.services"
```

## Tasks
```yaml
setup_extraction:
  action: CREATE
  target: extracted/systems/fixed_stars/
  validate:
    - mkdir -p extracted/systems/fixed_stars
    - mkdir -p tests/extraction
    - mkdir -p tests/perf

copy_source:
  action: COPY
  from: backend/app/core/ephemeris/tools/fixed_stars.py
  to: extracted/systems/fixed_stars/fixed_stars.py
  post_process:
    - fix_imports: "Update backend.app imports to extracted.systems"
    - verify_swiss_eph_catalog: "Check sefstars.txt accessibility"
  validate:
    - python -c "import sys; sys.path.insert(0, '.'); from extracted.systems.fixed_stars.fixed_stars import FixedStarCalculator; calc = FixedStarCalculator(); assert hasattr(calc, 'get_foundation_stars'), 'Missing foundation stars method'; print('✅ INIT OK')"

copy_dependencies:
  action: COPY
  from: backend/app/core/ephemeris/models/
  to: extracted/systems/models/
  files: ["planet_position.py", "star_data.py"]
  validate:
    - python -c "from extracted.systems.models.planet_position import PlanetPosition; print('✅ MODELS OK')"

create_tests:
  action: CREATE
  file: tests/extraction/test_fixed_stars.py
  contents: |
    import pytest
    import sys
    sys.path.insert(0, '.')
    from extracted.systems.fixed_stars.fixed_stars import FixedStarCalculator
    
    def test_fixed_stars_initialization():
        calc = FixedStarCalculator()
        assert calc is not None
        
    def test_foundation_24_count():
        calc = FixedStarCalculator()
        foundation = calc.get_foundation_stars()
        assert len(foundation) >= 24, f"Expected 24+ foundation stars, got {len(foundation)}"
        
    def test_royal_stars_present():
        calc = FixedStarCalculator()
        foundation = calc.get_foundation_stars()
        star_names = [star.name for star in foundation]
        royal_stars = ["Regulus", "Aldebaran", "Antares", "Fomalhaut"]
        present = sum(1 for royal in royal_stars if royal in star_names)
        assert present >= 4, f"Missing royal stars. Found: {[r for r in royal_stars if r in star_names]}"
        
    def test_star_position_calculation():
        calc = FixedStarCalculator()
        # Test with a known star
        regulus_pos = calc.calculate_star_position("Regulus", 2460000.5)
        assert regulus_pos is not None
        assert 0 <= regulus_pos.longitude <= 360, f"Invalid longitude: {regulus_pos.longitude}"

create_perf_test:
  action: CREATE
  file: tests/perf/test_fixed_stars_perf.py
  contents: |
    import time
    import sys
    sys.path.insert(0, '.')
    from extracted.systems.fixed_stars.fixed_stars import FixedStarCalculator
    
    def test_single_star_performance():
        calc = FixedStarCalculator()
        start = time.time()
        pos = calc.calculate_star_position("Regulus", 2460000.5)
        elapsed = (time.time() - start) * 1000
        print(f"Single star calc: {elapsed:.1f}ms")
        assert elapsed < 10, f"Too slow: {elapsed:.1f}ms > 10ms target"
        
    def test_batch_performance():
        calc = FixedStarCalculator()
        foundation = calc.get_foundation_stars()[:24]  # First 24
        start = time.time()
        for star in foundation:
            calc.calculate_star_position(star.name, 2460000.5)
        elapsed = (time.time() - start) * 1000
        print(f"Batch 24 stars: {elapsed:.1f}ms")
        assert elapsed < 50, f"Batch too slow: {elapsed:.1f}ms > 50ms target"

run_tests:
  action: VALIDATE
  command: pytest -q tests/extraction/test_fixed_stars.py -v
  expect: "All tests pass with ✅ indicators"

performance_check:
  action: VALIDATE
  command: python tests/perf/test_fixed_stars_perf.py
  expect: "Single <10ms, batch <50ms reported"

commit_checkpoint:
  action: CHECKPOINT
  command: git add -A && git commit -m "PRP_FIXED_STARS: Extraction complete and validated"
```

## Validation Checklist
- [ ] Import works
- [ ] Path setup success
- [ ] 24 foundation stars accessible
- [ ] 4 royal stars present
- [ ] Position longitudes 0-360
- [ ] Batch timing <50ms

## Rollback
Delete extracted/systems/fixed_stars and revert git commit.

## Confidence
9/10
