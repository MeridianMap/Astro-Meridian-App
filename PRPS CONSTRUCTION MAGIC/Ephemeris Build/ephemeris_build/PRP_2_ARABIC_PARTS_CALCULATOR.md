# PRP 2: Arabic Parts (Hermetic Lots) Calculator – Traditional Astrology Integration

## Reference: Ephemeris Extensions Content and Plan - Priority 1 Essential Feature & Hermetic Lots Library

---

## Feature Goal
Integrate the existing Hermetic Lots library with the ephemeris engine to calculate traditional Arabic parts with day/night sect variations, supporting at least 16 core lots with custom formula capabilities.

## Deliverable
A complete Arabic parts calculation module (`backend/app/core/ephemeris/tools/arabic_parts.py`) that leverages the existing hermetic lots implementation, integrated into the enhanced natal chart API with sect-aware formula switching.

## Success Definition
- Calculate 16+ traditional Arabic parts with day/night formula variations
- Achieve <40ms response time for complete lots calculation
- Support custom formula definitions with safe parsing
- Integrate with existing hermetic lots calculation engine
- Provide comprehensive metadata for each calculated part

---

## Context

### Key Files and Patterns
```yaml
reference_files:
  - "BUILD RESOURCES/Astrological Reference/Hermetic lots astro meridian implementation.md": Complete formula library
  - "backend/app/core/ephemeris/tools/ephemeris.py": Existing calculation patterns  
  - "backend/app/core/ephemeris/classes/serialize.py": Data model patterns
  - "backend/app/services/ephemeris_service.py": Service integration patterns
  - "hermetic_lots/": Existing hermetic lots calculation library

hermetic_lots_integration:
  core_library: "Existing hermetic lots calculation engine"
  formula_library: "16+ traditional lot formulas with day/night variations"
  sect_detection: "Automatic day/night chart determination"
  custom_formulas: "Safe AST-based formula parsing (no eval())"

arabic_parts_priority_list:
  core_lots:
    - "Part of Fortune (Fortuna)"
    - "Part of Spirit" 
    - "Part of Basis"
    - "Part of Travel"
    - "Part of Fame"
    - "Part of Work/Profession"
    - "Part of Property" 
    - "Part of Wealth"
  optional_lots:
    - "Part of Eros"
    - "Part of Necessity" 
    - "Part of Victory"
    - "Part of Nemesis"
    - "Part of Exaltation"
    - "Part of Marriage"
    - "Part of Faith"
    - "Part of Friends"
```

### Astrological Formula Context
```yaml
day_night_variations:
  sect_calculation: "Sun above horizon = day chart, below = night chart"
  fortune_day: "Ascendant + Moon - Sun"
  fortune_night: "Ascendant + Sun - Moon"
  spirit_day: "Ascendant + Sun - Moon" 
  spirit_night: "Ascendant + Moon - Sun"
  basis_formula: "Ascendant + Fortune - Spirit" # sect-independent

formula_structure:
  standard_format: "Point1 + Point2 - Point3"
  complex_format: "Point1 + Point2 - Point3 + Point4 - Point5"
  custom_operators: "+, -, *, /" # For advanced formulas
  angle_normalization: "All results normalized to 0-360 degrees"
```

### Integration Architecture
```yaml
adapter_pattern:
  hermetic_lots_adapter: "Convert between ephemeris and lots data formats"
  formula_registry: "Register and manage all lot formulas"
  calculation_service: "Coordinate between ephemeris and lots engines"
  
performance_considerations:
  batch_processing: "Calculate all requested lots in single pass"
  caching_strategy: "Cache lot calculations with chart data as key"
  memory_optimization: "Reuse position data across lot calculations"
```

---

## Implementation Tasks

### Task 1: Create Arabic Parts Adapter Service
**Target**: `backend/app/core/ephemeris/tools/arabic_parts.py`
```yaml
adapter_implementation:
  ArabicPartsCalculator:
    - __init__(hermetic_calculator: HermeticLotsCalculator)
    - calculate_parts(chart_data, requested_lots) -> List[ArabicPart]
    - _determine_chart_sect(sun_position, ascendant) -> bool
    - _convert_to_hermetic_format(positions) -> HermeticPositions
    - _convert_from_hermetic_format(results) -> List[ArabicPart]
  
  integration_methods:
    - adapt_ephemeris_positions() # Convert PlanetPosition to lots format
    - adapt_lot_results() # Convert lots results back to ephemeris format
    - handle_calculation_errors() # Graceful error handling
    - validate_formula_safety() # Ensure no eval() usage
```

### Task 2: Implement Formula Registry System
**Target**: `backend/app/core/ephemeris/tools/arabic_parts_formulas.py`
```yaml
formula_registry:
  HERMETIC_LOTS_FORMULAS:
    fortune:
      name: "Part of Fortune (Fortuna)"
      day_formula: "ascendant + moon - sun"
      night_formula: "ascendant + sun - moon"
      description: "Material prosperity and life circumstances"
      traditional_source: "Ptolemy, Tetrabiblos"
    
    spirit:
      name: "Part of Spirit"
      day_formula: "ascendant + sun - moon"
      night_formula: "ascendant + moon - sun"
      description: "Spiritual nature and inner vitality"
      traditional_source: "Ptolemy, Tetrabiblos"
      
    basis:
      name: "Part of Basis"
      day_formula: "ascendant + fortune - spirit"
      night_formula: "ascendant + fortune - spirit"
      description: "Foundation of life and existence"
      sect_independent: true
      
  # ... complete formula library from hermetic lots reference

formula_management:
  FormulaRegistry:
    - register_formula(name, formula_definition)
    - get_formula(name, is_day_chart) -> Formula
    - validate_formula(formula_string) -> bool
    - list_available_formulas() -> List[str]
```

### Task 3: Create Arabic Parts Data Models  
**Target**: `backend/app/core/ephemeris/tools/arabic_parts_models.py`
```yaml
data_models:
  ArabicPart:
    - name: str  # "fortune", "spirit", etc.
    - display_name: str  # "Part of Fortune"
    - longitude: float  # 0-360 degrees
    - sign: str  # "Aries", "Taurus", etc.
    - sign_degree: float  # Degree within sign
    - house: Optional[int]  # House position if available
    - formula_used: str  # Which formula was applied
    - is_day_chart: bool  # Sect determination
    - calculation_metadata: Dict[str, Any]
    
  ArabicPartsRequest:
    - requested_parts: List[str]  # Which lots to calculate
    - include_all_traditional: bool  # Calculate all 16 core lots
    - custom_formulas: Optional[Dict[str, str]]  # User-defined formulas
    - house_system: Optional[str]  # For house positions
    
  ArabicPartsResult:
    - calculated_parts: List[ArabicPart]
    - sect_determination: bool  # Day or night chart
    - total_parts_calculated: int
    - calculation_time_ms: float
    - formulas_used: Dict[str, str]
```

### Task 4: Implement Sect Detection Logic
**Target**: `backend/app/core/ephemeris/tools/sect_calculator.py`
```yaml
sect_detection:
  determine_chart_sect():
    - Input: sun_position, ascendant_position, house_positions
    - Logic: sun_house <= 6 = night, sun_house >= 7 = day
    - Alternative: sun above/below horizon calculation
    - Return: is_day_chart boolean
    
  advanced_sect_methods:
    - calculate_sun_horizon_position() # Precise above/below horizon
    - handle_polar_regions() # Special cases for extreme latitudes  
    - validate_sect_calculation() # Cross-check multiple methods
    
  edge_case_handling:
    - sun_on_horizon_exact # Use traditional house-based method
    - missing_ascendant_data # Fallback to noon assumption
    - polar_region_births # Special handling for 24h sun/darkness
```

### Task 5: Integrate with Enhanced Natal Chart Service
**Target**: `backend/app/services/ephemeris_service.py`
```yaml
service_integration:
  enhanced_natal_chart_updates:
    - Add arabic_parts_calculator initialization
    - Add include_arabic_parts parameter handling
    - Add arabic_parts_selection parameter support
    - Integrate parts calculation into enhanced response
    - Add error handling for parts calculation failures
    
  arabic_parts_service_methods:
    - calculate_arabic_parts(chart_data, request) -> ArabicPartsResult
    - _prepare_parts_data_for_hermetic_lots() # Format conversion
    - _integrate_parts_results_with_chart() # Merge into chart response
    - _handle_custom_formula_requests() # Safe custom formula processing
```

### Task 6: Create API Integration and Schema Updates
**Target**: API endpoints and request/response models
```yaml
api_integration:
  enhanced_endpoint_updates:
    "/v2/ephemeris/natal-enhanced":
      - Add include_arabic_parts parameter
      - Add arabic_parts_selection parameter
      - Add custom_formulas parameter
      - Return arabic_parts in response
      
  standalone_endpoint:
    "/v2/arabic-parts/calculate":
      - Dedicated endpoint for Arabic parts calculation
      - Accept minimal position data for calculation
      - Support batch calculation for multiple charts
      
request_schema_updates:
  NatalChartEnhancedRequest:
    - include_arabic_parts: bool = False
    - arabic_parts_selection: List[str] = ["fortune", "spirit"]
    - include_all_traditional_parts: bool = False
    - custom_arabic_formulas: Optional[Dict[str, str]] = None
    
response_schema_updates:
  NatalChartEnhancedResponse:
    - arabic_parts: Optional[List[ArabicPart]]
    - sect_determination: Optional[bool]
    - parts_calculation_metadata: Optional[Dict[str, Any]]
```

### Task 7: Performance Optimization and Caching
**Target**: Optimize Arabic parts calculations for production use
```yaml
performance_optimizations:
  calculation_efficiency:
    - Batch all lot calculations in single hermetic lots call
    - Cache intermediate formula parsing results
    - Reuse position data across multiple lot calculations
    - Pre-compile frequently used formulas
    
  caching_strategy:
    - Cache parts calculations with chart positions as key
    - 24-hour TTL for parts results
    - Redis integration for production scaling  
    - Separate cache keys for different lot combinations
    
  memory_optimization:
    - Efficient data structure conversion between systems
    - Minimize object creation in calculation loops
    - Use structure-of-arrays for batch processing
```

### Task 8: Comprehensive Testing and Validation
**Target**: `backend/tests/core/ephemeris/tools/test_arabic_parts.py`
```yaml
test_coverage:
  unit_tests:
    - test_sect_determination_accuracy()
    - test_formula_parsing_and_validation()
    - test_day_night_formula_switching()
    - test_traditional_lot_calculations()
    - test_custom_formula_processing()
    - test_hermetic_lots_integration()
    
  integration_tests:
    - test_enhanced_chart_with_arabic_parts()
    - test_standalone_arabic_parts_endpoint()
    - test_performance_with_all_lots()
    - test_cache_integration()
    - test_error_handling_invalid_formulas()
    
  validation_against_references:
    - Cross-validate against traditional astrological sources
    - Test known charts with verified part positions
    - Validate sect determination against multiple methods
    - Test edge cases (polar regions, exact aspects)
    
  performance_benchmarks:
    - All 16 traditional lots <40ms calculation time
    - Memory usage optimization validation
    - Cache hit rate under realistic load
```

---

## Validation Gates

### Technical Validation
- [ ] All unit tests pass with >90% code coverage
- [ ] Performance benchmarks meet <40ms target for 16 lots
- [ ] Hermetic lots library integration working correctly
- [ ] Safe formula parsing prevents eval() security issues
- [ ] API endpoints handle all error conditions gracefully
- [ ] Cache integration functions properly with Redis

### Astrological Validation
- [ ] Traditional lot formulas match historical sources (Ptolemy, Lilly, Bonatti)
- [ ] Day/night sect determination accurate in all test cases
- [ ] Formula variations correctly applied based on sect
- [ ] Custom formula system allows for advanced lot definitions
- [ ] All 16 core lots calculate correctly with proper metadata
- [ ] Results validate against established astrological software

### Integration Validation
- [ ] Enhanced natal chart includes Arabic parts when requested
- [ ] Standalone Arabic parts endpoint functional
- [ ] Response schemas include all required metadata
- [ ] Service layer integration follows existing patterns
- [ ] Error handling provides meaningful feedback
- [ ] Feature can be enabled/disabled via configuration

---

## Final Validation Checklist

### Code Quality
- [ ] `pytest backend/tests/core/ephemeris/tools/test_arabic_parts.py -v`
- [ ] `pytest --cov=backend/app/core/ephemeris/tools/arabic_parts --cov-report=term-missing`
- [ ] `ruff check backend/app/core/ephemeris/tools/arabic_parts.py`
- [ ] `mypy backend/app/core/ephemeris/tools/arabic_parts.py`

### Performance Validation
- [ ] `python backend/scripts/benchmark_arabic_parts.py` shows <40ms p95
- [ ] Memory usage <500KB for all traditional lots
- [ ] Cache hit rate >70% under load testing
- [ ] Hermetic lots integration overhead <10ms

### Integration Testing
- [ ] `/v2/ephemeris/natal-enhanced` functional with Arabic parts
- [ ] `/v2/arabic-parts/calculate` standalone endpoint working
- [ ] Response validation passes for all lot types
- [ ] Error handling returns appropriate HTTP status codes
- [ ] Custom formula system prevents security vulnerabilities

### Astrological Accuracy
- [ ] Traditional formulas match established sources
- [ ] Sect determination accuracy verified across test cases
- [ ] Results cross-validated against professional astrological software
- [ ] Edge cases handled correctly (polar regions, midnight births)
- [ ] Custom formulas produce mathematically correct results

---

**Implementation Priority: HIGH - Essential for traditional astrology practice**

**Dependencies**: Hermetic lots library, sect calculation logic, enhanced natal chart service

**Estimated Complexity**: Medium (integration complexity, formula safety, sect logic)

**Success Metrics**: <40ms response time, 16+ traditional lots, validated against astrological sources