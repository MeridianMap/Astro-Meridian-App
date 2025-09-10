# EXTRACTION PRP: ACG Mathematical Engine

## Feature Goal
Extract accurate astrocartography core line calculation engine (MC/IC/AC/DC) with coordinate transforms.

## Deliverable
- Core methods from acg_core.py preserved:
  - calculate_mc_ic_lines
  - calculate_ac_dc_lines
  - calculate_body_position
  - projection / coordinate transforms
- Supporting files copied: acg_utils.py, acg_types.py, acg_cache.py
- GeoJSON generation patterns retained

## Success Definition
- MC/IC/AC/DC lines generated for Sun produce non-empty coordinate sequences
- Longitude/latitude ranges valid (-180..180 / -90..90)
- GMST-based calculations consistent run-to-run

## Context
```yaml
docs:
  - url: https://astronomy.stackexchange.com/questions/23772/local-midheaven-computation
    focus: MC calculation theory and coordinate systems
  - url: https://pyswisseph.readthedocs.io/en/latest/api.html#sidereal-time
    focus: sidereal time / GMST usage in calculations
  - url: https://aa.usno.navy.mil/faq/GMT
    focus: time conversion background for coordinate calculations
  - url: https://www.astro.com/astrology/in_acglines_e.htm
    focus: Astrocartography line theory
patterns:
  - file: backend/app/core/acg/acg_core.py
    preserve: line calculation math blocks (lines 156-245, 267-334)
    critical: "calculate_mc_ic_lines and calculate_ac_dc_lines methods"
  - file: backend/app/core/acg/acg_utils.py
    preserve: coordinate transformation utilities (lines 45-123)
    critical: "gmst_deg_from_jd_ut1 and coordinate projection functions"
  - file: backend/app/core/acg/acg_types.py
    preserve: dataclasses and models for ACG data structures
  - file: backend/app/core/acg/acg_cache.py
    preserve: caching interfaces and performance optimizations
dependencies:
  external:
    - pyswisseph>=2.10.3 (for body position calculations)
    - numpy>=1.20 (for coordinate transformations)
    - pydantic>=2.0 (for data models)
  internal:
    - body_position_calculator (Swiss Ephemeris integration)
    - coordinate_transformation_utils
    - time_conversion_utilities
  provides:
    - ACGCalculationEngine
    - mc_ic_line_generators 
    - ac_dc_line_generators
    - coordinate_transformations
    - geojson_export_patterns
gotchas:
  - issue: discontinuity at International Date Line (±180° longitude)
    fix: "split line segments when delta_longitude > 180°"
    location: "acg_utils.py line 89 - handle_dateline_crossing()"
  - issue: polar singularities near ±90° latitude
    fix: "clamp latitude calculations near ±89.5° to prevent math errors"
    location: "coordinate projection functions"
  - issue: performance degradation with redundant Swiss Ephemeris calls
    fix: "reuse body position data for all line types (MC/IC/AC/DC)"
    optimization: "calculate_body_position once, pass to all line generators"
  - issue: GMST calculation drift over long time periods
    fix: "use consistent Julian Day precision, avoid floating point drift"
    location: "gmst_deg_from_jd_ut1 function"
  - issue: coordinate system confusion (ecliptic vs equatorial)
    fix: "maintain coordinate system consistency throughout calculations"
import_fixes:
  - from: "from backend.app.core.acg"
    to: "from extracted.systems.acg_engine"
  - from: "from app.core.ephemeris"
    to: "from extracted.systems"
performance_notes:
  - single_body_all_lines: "Target <15ms for Sun MC/IC/AC/DC complete set"
  - coordinate_transforms: "Batch process to avoid repeated calculations"
  - caching_strategy: "Cache by Julian Day + body combination"
```

## Tasks
```yaml
setup_extraction:
  action: CREATE
  target: extracted/systems/acg_engine/
  validate:
    - mkdir -p extracted/systems/acg_engine
    - mkdir -p tests/extraction
    - mkdir -p tests/perf

copy_engine:
  action: COPY
  from:
    - backend/app/core/acg/acg_core.py
    - backend/app/core/acg/acg_utils.py
    - backend/app/core/acg/acg_types.py
    - backend/app/core/acg/acg_cache.py
  to: extracted/systems/acg_engine/
  post_process:
    - fix_imports: "Update backend.app.core imports to extracted.systems"
    - verify_math_functions: "Ensure coordinate transform functions preserved"
  validate:
    - python -c "import sys; sys.path.insert(0, '.'); from extracted.systems.acg_engine.acg_core import ACGCalculationEngine; engine = ACGCalculationEngine(); assert hasattr(engine, 'calculate_mc_ic_lines'), 'Missing MC/IC calculation'; assert hasattr(engine, 'calculate_ac_dc_lines'), 'Missing AC/DC calculation'; print('✅ ENGINE OK')"

create_tests:
  action: CREATE
  file: tests/extraction/test_acg_engine.py
  contents: |
    import pytest
    import sys
    sys.path.insert(0, '.')
    from extracted.systems.acg_engine.acg_core import ACGCalculationEngine
    from extracted.systems.acg_engine.acg_utils import gmst_deg_from_jd_ut1
    from extracted.systems.acg_engine.acg_types import ACGBody, ACGBodyType
    
    def test_acg_engine_initialization():
        engine = ACGCalculationEngine()
        assert engine is not None
        
    def test_gmst_calculation():
        # Test GMST calculation for known Julian Day
        jd = 2460000.5  # Reference Julian Day
        gmst = gmst_deg_from_jd_ut1(jd)
        assert isinstance(gmst, (int, float)), f"GMST should be numeric, got {type(gmst)}"
        assert 0 <= gmst <= 360, f"GMST should be 0-360°, got {gmst}"
        
    def test_sun_mc_ic_lines():
        engine = ACGCalculationEngine()
        sun_body = ACGBody(name="Sun", body_type=ACGBodyType.PLANET, swiss_ephemeris_id=0)
        
        # Calculate body position first
        jd = 2460000.5
        sun_data = engine.calculate_body_position(sun_body, jd)
        assert sun_data is not None, "Sun position calculation failed"
        assert hasattr(sun_data, 'coordinates'), "Missing coordinates in sun data"
        
        # Calculate MC/IC lines
        gmst = gmst_deg_from_jd_ut1(jd)
        mc_ic_lines = engine.calculate_mc_ic_lines(sun_data, gmst, {})
        
        assert len(mc_ic_lines) >= 1, "No MC/IC lines generated"
        for line in mc_ic_lines:
            assert hasattr(line, 'coordinates'), "Missing coordinates in line data"
            # Validate coordinate ranges
            for coord in line.coordinates[:5]:  # Check first 5 points
                assert -180 <= coord['longitude'] <= 180, f"Invalid longitude: {coord['longitude']}"
                assert -90 <= coord['latitude'] <= 90, f"Invalid latitude: {coord['latitude']}"
                
    def test_sun_ac_dc_lines():
        engine = ACGCalculationEngine()
        sun_body = ACGBody(name="Sun", body_type=ACGBodyType.PLANET, swiss_ephemeris_id=0)
        
        jd = 2460000.5
        sun_data = engine.calculate_body_position(sun_body, jd)
        gmst = gmst_deg_from_jd_ut1(jd)
        ac_dc_lines = engine.calculate_ac_dc_lines(sun_data, gmst, {})
        
        assert len(ac_dc_lines) >= 1, "No AC/DC lines generated"
        for line in ac_dc_lines:
            assert hasattr(line, 'coordinates'), "Missing coordinates in line data"
            
    def test_coordinate_bounds():
        """Test that all coordinates stay within valid ranges"""
        engine = ACGCalculationEngine()
        sun_body = ACGBody(name="Sun", body_type=ACGBodyType.PLANET, swiss_ephemeris_id=0)
        
        jd = 2460000.5
        sun_data = engine.calculate_body_position(sun_body, jd)
        gmst = gmst_deg_from_jd_ut1(jd)
        
        # Test both line types
        all_lines = []
        all_lines.extend(engine.calculate_mc_ic_lines(sun_data, gmst, {}))
        all_lines.extend(engine.calculate_ac_dc_lines(sun_data, gmst, {}))
        
        assert len(all_lines) > 0, "No lines generated for coordinate bounds test"
        
        for line in all_lines:
            for coord in line.coordinates:
                assert -180 <= coord['longitude'] <= 180, f"Longitude out of bounds: {coord['longitude']}"
                assert -90 <= coord['latitude'] <= 90, f"Latitude out of bounds: {coord['latitude']}"

create_performance_test:
  action: CREATE
  file: tests/perf/test_acg_perf.py
  contents: |
    import time
    import sys
    sys.path.insert(0, '.')
    from extracted.systems.acg_engine.acg_core import ACGCalculationEngine
    from extracted.systems.acg_engine.acg_utils import gmst_deg_from_jd_ut1
    from extracted.systems.acg_engine.acg_types import ACGBody, ACGBodyType
    
    def test_single_body_performance():
        """Test performance for complete line set generation"""
        engine = ACGCalculationEngine()
        sun_body = ACGBody(name="Sun", body_type=ACGBodyType.PLANET, swiss_ephemeris_id=0)
        
        jd = 2460000.5
        
        start = time.time()
        # Calculate body position once
        sun_data = engine.calculate_body_position(sun_body, jd)
        gmst = gmst_deg_from_jd_ut1(jd)
        
        # Generate all line types
        mc_ic_lines = engine.calculate_mc_ic_lines(sun_data, gmst, {})
        ac_dc_lines = engine.calculate_ac_dc_lines(sun_data, gmst, {})
        
        elapsed = (time.time() - start) * 1000
        total_lines = len(mc_ic_lines) + len(ac_dc_lines)
        
        print(f"Complete Sun line set: {elapsed:.1f}ms")
        print(f"Generated {total_lines} lines total")
        print(f"MC/IC lines: {len(mc_ic_lines)}, AC/DC lines: {len(ac_dc_lines)}")
        
        assert elapsed < 15, f"Line generation too slow: {elapsed:.1f}ms > 15ms target"
        assert total_lines > 0, "No lines generated"

run_tests:
  action: VALIDATE
  command: pytest -q tests/extraction/test_acg_engine.py -v
  expect: "All tests pass with coordinate validation"

performance_test:
  action: VALIDATE  
  command: python tests/perf/test_acg_perf.py
  expect: "Complete line set generation <15ms"

integration_test:
  action: CREATE
  file: tests/extraction/test_acg_integration.py
  contents: |
    """Test ACG engine integration with Swiss Ephemeris"""
    import sys
    sys.path.insert(0, '.')
    from extracted.systems.acg_engine.acg_core import ACGCalculationEngine
    
    def test_swiss_ephemeris_integration():
        """Verify Swiss Ephemeris integration works end-to-end"""
        engine = ACGCalculationEngine()
        
        # Test multiple bodies to ensure Swiss Eph integration
        test_bodies = [
            ("Sun", 0), ("Moon", 1), ("Mercury", 2), ("Venus", 3), ("Mars", 4)
        ]
        
        for body_name, swiss_id in test_bodies:
            try:
                from extracted.systems.acg_engine.acg_types import ACGBody, ACGBodyType
                body = ACGBody(name=body_name, body_type=ACGBodyType.PLANET, swiss_ephemeris_id=swiss_id)
                position = engine.calculate_body_position(body, 2460000.5)
                assert position is not None, f"Failed to calculate {body_name} position"
                print(f"✅ {body_name} position calculated successfully")
            except Exception as e:
                print(f"❌ {body_name} calculation failed: {e}")
                assert False, f"Swiss Ephemeris integration failed for {body_name}"

commit_checkpoint:
  action: CHECKPOINT
  command: git add -A && git commit -m "PRP_ACG_ENGINE: Mathematical core extracted with coordinate validation"
```

## Validation Checklist
- [ ] Engine imports
- [ ] Sun lines MC/IC present
- [ ] Sun lines AC/DC present
- [ ] All coordinates numeric and in bounds
- [ ] No exceptions during batch generation

## Rollback
Remove extracted/systems/acg_engine and revert commit.

## Confidence
8.5/10
