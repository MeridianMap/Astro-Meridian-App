# EXTRACTION PRP: Arabic Parts (Hermetic Lots) System

## Feature Goal
Extract full professional Arabic Parts architecture with sect-aware traditional lots.

## Deliverable
- 4 modules copied intact:
  - arabic_parts.py (966 lines)
  - arabic_parts_formulas.py
  - arabic_parts_models.py
  - sect_calculator.py
- All 16+ traditional lots functional (fortune, spirit, basis, eros, necessity, victory, courage, nemesis, accusation, father, mother, marriage, children, siblings, friends, death)
- Sect switching logic preserved
- Batch calculation <40ms

## Success Definition
- Each traditional lot returns position (0-360)
- Day/night formula differences validated
- Performance meets <40ms target for full batch

## Context
```yaml
docs:
  - url: https://traditionalastrology.org/arabic-parts-overview
    focus: traditional lots definitions and formulas
  - url: https://pyswisseph.readthedocs.io/en/latest/api.html#planetary-positions
    focus: planetary longitude retrieval for calculations
  - url: https://docs.python.org/3/library/ast.html#ast.literal_eval
    focus: safe AST parsing (no eval() security risks)
patterns:
  - file: backend/app/core/ephemeris/tools/arabic_parts.py
    preserve: ArabicPartsCalculator class (966 lines)
    copy: "calculate_traditional_lots method lines 145-210"
  - file: backend/app/core/ephemeris/tools/arabic_parts_formulas.py
    preserve: FORMULAS registry & AST parse function
    copy: "formula parsing logic lines 89-134"
  - file: backend/app/core/ephemeris/tools/sect_calculator.py
    preserve: determine_chart_sect method
    critical: "Day/night birth determination logic"
  - file: backend/app/core/ephemeris/tools/arabic_parts_models.py
    preserve: data models and type definitions
dependencies:
  external:
    - pydantic>=2.0 (for data models)
    - ast (standard library for safe formula parsing)
  internal:
    - planetary_position_provider (can be mocked for extraction)
    - chart_data_model (planets, ascendant, lot context)
  provides:
    - ArabicPartsCalculator
    - 16+ traditional_lots_registry
    - sect_calculator
    - AST-based formula_parser
  requires_from:
    - PRP_FIXED_STARS_EXTRACTION: "Not directly, but both use planet positions"
resources:
  cache: "Redis optional - can work without caching"
  performance_target: "<40ms for all 16 lots batch calculation"
gotchas:
  - issue: formula parsing must remain AST-based for security
    fix: "DO NOT replace with eval() - maintain ast.literal_eval approach"
    security_risk: "HIGH if changed to eval()"
  - issue: sect switching depends on sun vs ascendant position comparison
    fix: "maintain determine_chart_sect logic exactly as-is"
    file: "backend/app/core/ephemeris/tools/sect_calculator.py:45-67"
  - issue: performance regression if recalculating planets per lot
    fix: "reuse injected planet positions dict, don't recalculate"
    optimization: "Pass planet_positions once, reference for all lots"
  - issue: traditional formula accuracy depends on exact implementations
    fix: "preserve traditional formulas exactly, including sect variants"
    example: "Fortune = Asc + Moon - Sun (day) vs Asc + Sun - Moon (night)"
import_fixes:
  - from: "from backend.app.core.ephemeris.tools"
    to: "from extracted.systems.arabic_parts"
  - from: "from app.core.ephemeris.models"
    to: "from extracted.systems.models"
```

## Tasks
```yaml
setup_extraction:
  action: CREATE
  target: extracted/systems/arabic_parts/
  validate:
    - mkdir -p extracted/systems/arabic_parts
    - mkdir -p tests/extraction
    - mkdir -p tests/perf

copy_modules:
  action: COPY
  from:
    - backend/app/core/ephemeris/tools/arabic_parts.py
    - backend/app/core/ephemeris/tools/arabic_parts_formulas.py
    - backend/app/core/ephemeris/tools/arabic_parts_models.py
    - backend/app/core/ephemeris/tools/sect_calculator.py
  to: extracted/systems/arabic_parts/
  post_process:
    - fix_imports: "Update backend imports to extracted structure"
    - verify_ast_parsing: "Ensure no eval() usage in formula parsing"
  validate:
    - python -c "import sys; sys.path.insert(0, '.'); from extracted.systems.arabic_parts.arabic_parts import ArabicPartsCalculator; calc = ArabicPartsCalculator(); assert hasattr(calc, 'get_traditional_lots'), 'Missing traditional lots method'; print('✅ MODULES OK')"

create_tests:
  action: CREATE
  file: tests/extraction/test_arabic_parts.py
  contents: |
    import pytest
    import sys
    sys.path.insert(0, '.')
    from extracted.systems.arabic_parts.arabic_parts import ArabicPartsCalculator
    from extracted.systems.arabic_parts.sect_calculator import determine_chart_sect
    
    def test_arabic_parts_initialization():
        calc = ArabicPartsCalculator()
        assert calc is not None
        
    def test_traditional_lots_count():
        calc = ArabicPartsCalculator()
        lots = calc.get_traditional_lots()
        assert len(lots) >= 16, f"Expected 16+ traditional lots, got {len(lots)}"
        
    def test_core_lots_present():
        calc = ArabicPartsCalculator()
        lots = calc.get_traditional_lots()
        lot_names = [lot.lower() for lot in lots]
        core_lots = ["fortune", "spirit", "basis", "eros", "necessity"]
        missing = [lot for lot in core_lots if lot not in lot_names]
        assert len(missing) == 0, f"Missing core lots: {missing}"
        
    def test_sect_determination():
        # Test day chart (Sun above horizon)
        day_sect = determine_chart_sect(sun_longitude=180, ascendant_longitude=90)
        assert day_sect.is_day_birth, "Day chart not detected correctly"
        
        # Test night chart (Sun below horizon) 
        night_sect = determine_chart_sect(sun_longitude=0, ascendant_longitude=90)
        assert not night_sect.is_day_birth, "Night chart not detected correctly"
        
    def test_fortune_spirit_sect_difference():
        # Mock chart data for testing
        mock_planets = {
            'sun': {'longitude': 120},
            'moon': {'longitude': 240}, 
            'ascendant': {'longitude': 0}
        }
        
        calc = ArabicPartsCalculator()
        
        # Calculate for day chart
        day_lots = calc.calculate_lots_for_chart(mock_planets, is_day_birth=True)
        day_fortune = next((lot for lot in day_lots if lot['name'].lower() == 'fortune'), None)
        
        # Calculate for night chart  
        night_lots = calc.calculate_lots_for_chart(mock_planets, is_day_birth=False)
        night_fortune = next((lot for lot in night_lots if lot['name'].lower() == 'fortune'), None)
        
        # Fortune should differ between day/night
        assert day_fortune['longitude'] != night_fortune['longitude'], "Fortune lot not sect-aware"

create_performance_test:
  action: CREATE  
  file: tests/perf/test_arabic_parts_perf.py
  contents: |
    import time
    import sys
    sys.path.insert(0, '.')
    from extracted.systems.arabic_parts.arabic_parts import ArabicPartsCalculator
    
    def test_batch_lots_performance():
        calc = ArabicPartsCalculator()
        
        # Mock full planetary data
        mock_planets = {
            'sun': {'longitude': 120}, 'moon': {'longitude': 240},
            'mercury': {'longitude': 110}, 'venus': {'longitude': 140},
            'mars': {'longitude': 200}, 'jupiter': {'longitude': 80},
            'saturn': {'longitude': 300}, 'ascendant': {'longitude': 0}
        }
        
        start = time.time()
        lots = calc.calculate_all_traditional_lots(mock_planets)
        elapsed = (time.time() - start) * 1000
        
        print(f"All traditional lots: {elapsed:.1f}ms")
        print(f"Calculated {len(lots)} lots")
        assert elapsed < 40, f"Batch too slow: {elapsed:.1f}ms > 40ms target"
        assert len(lots) >= 16, f"Expected 16+ lots, got {len(lots)}"

run_tests:
  action: VALIDATE
  command: pytest -q tests/extraction/test_arabic_parts.py -v
  expect: "All tests pass including sect awareness validation"

performance_test:
  action: VALIDATE
  command: python tests/perf/test_arabic_parts_perf.py
  expect: "Batch calculation <40ms with 16+ lots calculated"

commit_checkpoint:
  action: CHECKPOINT
  command: git add -A && git commit -m "PRP_ARABIC_PARTS: Complete 4-module extraction validated"
```

## Validation Checklist
- [ ] Import works
- [ ] 16+ lot identifiers returned
- [ ] Fortune & Spirit differ between day and night charts
- [ ] All lot longitudes 0-360
- [ ] Batch timing <40ms

## Rollback
Remove extracted/systems/arabic_parts and revert commit.

## Confidence
9/10
