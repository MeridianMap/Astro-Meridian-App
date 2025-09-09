# PRP 1: Aspect Calculation Engine – Professional Astrology Feature

## Reference: Ephemeris Extensions Content and Plan - Priority 1 Essential Feature

---

## Feature Goal
Implement a comprehensive aspect calculation engine that computes aspects between all planetary positions in a chart with configurable orb presets, applying/separating detection, and professional-grade metadata.

## Deliverable
A complete aspect calculation module (`backend/app/core/ephemeris/tools/aspects.py`) integrated into the enhanced natal chart API endpoint, supporting traditional and modern orb systems with matrix-based performance optimization.

## Success Definition
- Calculate aspects between all planets in a chart with <30ms response time
- Support major aspects (conjunction, opposition, trine, square, sextile) with configurable orbs
- Include applying vs separating aspect detection
- Return aspect strength/exactitude percentage
- Achieve >90% test coverage with validation against known aspect configurations

---

## Context

### Key Files and Patterns
```yaml
reference_files:
  - "backend/app/core/ephemeris/tools/ephemeris.py": Existing calculation patterns
  - "backend/app/core/ephemeris/classes/serialize.py": Data model patterns
  - "backend/app/services/ephemeris_service.py": Service integration patterns
  - "backend/tests/core/ephemeris/tools/test_ephemeris.py": Testing patterns
  - "docs/api/overview.md": API documentation patterns

existing_orb_systems:
  traditional:
    sun_moon_orbs: "8.0 degrees for major aspects"
    planet_orbs: "6.0 degrees for major aspects, 4.0 for sextiles"
  modern:
    sun_moon_orbs: "10.0-12.0 degrees for major aspects"
    planet_orbs: "8.0 degrees for major aspects"
  custom:
    per_planet_per_aspect: "Individual orb settings"

mathematical_foundation:
  - "Swiss Ephemeris longitude positions as input"
  - "Angular difference calculations with 360-degree wrapping"
  - "Orb tolerance checking with applying/separating logic"
  - "Aspect strength as percentage of exactness"
```

### Codebase Integration Points
```yaml
integration_patterns:
  service_layer: "backend/app/services/ephemeris_service.py"
  api_endpoint: "backend/app/api/routes/ephemeris.py"
  data_models: "backend/app/api/models/schemas.py"
  cache_integration: "backend/app/core/ephemeris/classes/cache.py"
  
performance_requirements:
  single_calculation: "<30ms for 12-planet aspect matrix"
  batch_processing: "5x+ improvement over individual calculations"
  cache_strategy: "24h TTL for aspect calculations"
  memory_optimization: "Structure-of-arrays for large datasets"
```

### Known Gotchas
```yaml
astrological_considerations:
  - "Orbs vary by both aspect type AND planet involved"
  - "Sun and Moon traditionally get wider orbs than other planets"
  - "Applying aspects (planets moving toward exact) vs separating (moving away)"
  - "Aspect strength calculation affects interpretation priority"
  - "Minor aspects have significantly tighter orbs"

technical_challenges:
  - "360-degree boundary crossing in angle calculations"
  - "Performance optimization for O(n²) planet comparisons"
  - "Consistent orb configuration across different astrological traditions"
  - "Precision requirements for exact aspects"
```

---

## Implementation Tasks

### Task 1: Create Aspect Calculation Core Module
**Target**: `backend/app/core/ephemeris/tools/aspects.py`
```yaml
implementation_specs:
  - Create AspectCalculator class with configuration support
  - Implement angle_difference() with 360-degree wrapping
  - Implement is_aspect_within_orb() with configurable orb system
  - Implement calculate_aspect_strength() returning 0.0-1.0 percentage
  - Implement is_applying_aspect() using daily motion data
  - Create calculate_all_aspects() returning complete aspect matrix
  
class_structure:
  AspectCalculator:
    - __init__(orb_config: OrbConfiguration)
    - calculate_aspects(positions: List[PlanetPosition]) -> List[Aspect]
    - _get_orb_for_aspect(planet1, planet2, aspect_type) -> float
    - _calculate_angle_difference(pos1, pos2) -> float
    - _is_aspect_applying(pos1, pos2, daily_motion1, daily_motion2) -> bool
```

### Task 2: Create Aspect Data Models
**Target**: `backend/app/core/ephemeris/tools/aspect_models.py`
```yaml
data_models:
  Aspect:
    - planet1: str
    - planet2: str
    - aspect_type: str  # "conjunction", "opposition", etc.
    - angle: float
    - orb_used: float
    - exact_angle: float  # Expected angle for aspect type
    - strength: float  # 0.0-1.0 exactitude percentage
    - is_applying: bool
    - orb_percentage: float
    
  OrbConfiguration:
    - preset_name: str  # "traditional", "modern", "custom"
    - aspect_orbs: Dict[str, Dict[str, float]]  # aspect_type -> planet -> orb
    - applying_factor: float  # Multiplier for applying aspects
    - separating_factor: float  # Multiplier for separating aspects
    
  AspectMatrix:
    - aspects: List[Aspect]
    - total_aspects: int
    - major_aspects: int
    - minor_aspects: int
    - orb_config_used: str
```

### Task 3: Implement Orb Configuration System
**Target**: `backend/app/core/ephemeris/tools/orb_systems.py`
```yaml
orb_presets:
  TRADITIONAL_ORBS:
    conjunction:
      sun: 8.0
      moon: 8.0
      mercury: 6.0
      venus: 6.0
      mars: 6.0
      jupiter: 6.0
      saturn: 6.0
      uranus: 5.0
      neptune: 5.0
      pluto: 5.0
      default: 6.0
    # ... other aspects
  
  MODERN_ORBS: # More generous orbs
  TIGHT_ORBS: # Research-grade tight orbs
  
configuration_loader:
  - load_orb_preset(preset_name: str) -> OrbConfiguration
  - validate_custom_orbs(custom_orbs: dict) -> bool
  - merge_orb_configs(base, override) -> OrbConfiguration
```

### Task 4: Integrate with Enhanced Natal Chart Service
**Target**: `backend/app/services/ephemeris_service.py`
```yaml
service_integration:
  enhanced_natal_chart_method:
    - Add aspect_calculator initialization
    - Add include_aspects parameter handling
    - Add aspect_orb_preset parameter support
    - Integrate aspect calculation into response
    - Add error handling for aspect calculation failures
    
  new_method:
    calculate_natal_chart_enhanced():
      - Call existing calculate_natal_chart()
      - If include_aspects: calculate aspects using AspectCalculator
      - If include_arabic_parts: calculate parts (future PRP)
      - Return enhanced response with all calculated features
```

### Task 5: Create API Endpoint and Schema Updates
**Target**: `backend/app/api/routes/ephemeris.py` and `backend/app/api/models/schemas.py`
```yaml
api_endpoint:
  "/v2/ephemeris/natal-enhanced":
    - POST method accepting NatalChartEnhancedRequest
    - Include aspect configuration parameters
    - Return enhanced response with aspect matrix
    - Maintain backward compatibility with v1 endpoint
    
request_schema:
  NatalChartEnhancedRequest(NatalChartRequest):
    - include_aspects: bool = True
    - aspect_orb_preset: str = "traditional"
    - custom_orb_config: Optional[Dict] = None
    - metadata_level: str = "basic"  # "basic", "full", "audit"
    
response_schema:
  NatalChartEnhancedResponse(NatalChartResponse):
    - aspects: Optional[List[Aspect]]
    - aspect_matrix: Optional[AspectMatrix]
    - calculation_metadata: CalculationMetadata
```

### Task 6: Performance Optimization
**Target**: Optimize for professional-grade performance
```yaml
performance_optimizations:
  matrix_calculations:
    - Use numpy arrays for batch angle calculations
    - Vectorize orb checking across all planet pairs
    - Pre-compute aspect angle constants
    - Implement early termination for out-of-orb pairs
  
  caching_strategy:
    - Cache aspect calculations with positions as key
    - 24-hour TTL for aspect results
    - Redis integration for production scaling
    - Memory cache for frequent calculations
  
  batch_processing:
    - Support calculating aspects for multiple charts
    - Vectorized operations across chart batches
    - Memory-efficient processing for large datasets
```

### Task 7: Comprehensive Testing Suite
**Target**: `backend/tests/core/ephemeris/tools/test_aspects.py`
```yaml
test_coverage:
  unit_tests:
    - test_angle_difference_calculation()
    - test_orb_checking_all_aspect_types()
    - test_aspect_strength_calculation()
    - test_applying_separating_detection()
    - test_custom_orb_configuration()
    - test_edge_cases_360_degree_boundary()
  
  integration_tests:
    - test_enhanced_natal_chart_with_aspects()
    - test_aspect_calculation_performance()
    - test_batch_aspect_processing()
    - test_cache_integration()
  
  reference_data_validation:
    - Known chart configurations with verified aspects
    - Cross-validation against professional software
    - Edge case charts (exact aspects, wide orbs, etc.)
    
  performance_benchmarks:
    - Single chart aspect calculation <30ms
    - 12-planet matrix calculation performance
    - Memory usage under load testing
```

---

## Validation Gates

### Technical Validation
- [ ] All unit tests pass with >90% code coverage
- [ ] Performance benchmarks meet <30ms single chart target
- [ ] Aspect calculations match reference data within 0.1 degrees
- [ ] API endpoints return proper error handling for invalid input
- [ ] Cache integration works correctly with Redis and memory cache
- [ ] Batch processing shows 5x+ improvement over individual calculations

### Astrological Validation  
- [ ] Traditional orb system matches classical astrological sources
- [ ] Modern orb system aligns with contemporary practice standards
- [ ] Applying/separating logic correctly uses daily motion data
- [ ] Aspect strength calculations provide meaningful interpretation data
- [ ] All major aspects (conjunction, opposition, trine, square, sextile) calculated correctly
- [ ] Edge cases handled properly (exact aspects, cuspal positions)

### Integration Validation
- [ ] Enhanced natal chart endpoint maintains backward compatibility
- [ ] Response schema includes all required aspect metadata
- [ ] Service layer integration follows existing patterns
- [ ] Error handling provides meaningful feedback to API consumers
- [ ] Documentation includes aspect calculation examples
- [ ] Feature can be disabled via configuration flags

---

## Final Validation Checklist

### Code Quality
- [ ] `pytest backend/tests/core/ephemeris/tools/test_aspects.py -v`
- [ ] `pytest --cov=backend/app/core/ephemeris/tools/aspects --cov-report=term-missing`
- [ ] `ruff check backend/app/core/ephemeris/tools/aspects.py`
- [ ] `mypy backend/app/core/ephemeris/tools/aspects.py`

### Performance Validation
- [ ] `python backend/scripts/benchmark_aspects.py` shows <30ms p95
- [ ] Memory usage <1MB per chart calculation
- [ ] Cache hit rate >70% under realistic load testing
- [ ] Batch processing demonstrates linear scaling

### API Integration
- [ ] `/v2/ephemeris/natal-enhanced` endpoint functional with aspect inclusion
- [ ] Response schema validation passes
- [ ] Error handling returns appropriate HTTP status codes
- [ ] Rate limiting and monitoring integration working

### Professional Standards
- [ ] Calculations validated against Swiss Ephemeris precision standards
- [ ] Orb systems match established astrological traditions
- [ ] Aspect interpretations align with professional astrological software
- [ ] Documentation includes usage examples for all orb presets

---

**Implementation Priority: HIGHEST - This is the foundational feature for professional astrology analysis**

**Dependencies**: Swiss Ephemeris integration, existing planetary position calculations

**Estimated Complexity**: Medium-High (comprehensive orb system, performance optimization)

**Success Metrics**: <30ms response time, >90% test coverage, validated against professional astrological software