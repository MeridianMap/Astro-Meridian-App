# PRP 5: Paran Lines Implementation – Advanced Astrocartography Simultaneity

## Reference: Ephemeris Extensions Content and Plan - Priority 2 Advanced Feature & Paran Technical Reference

---

## Feature Goal
Implement a comprehensive paran line calculation system that determines locations where two planetary bodies are simultaneously angular (on different angles), using rigorous mathematical methods with ≤0.03° latitude precision.

## Deliverable
A complete paran calculation module (`backend/app/core/acg/paran_calculator.py`) with dedicated API endpoints, supporting closed-form solutions for meridian-horizon pairs and numerical methods for horizon-horizon pairs.

## Success Definition
- Calculate paran lines with ≤0.03° latitude accuracy for all planet pairs
- Support simultaneity conditions: meridian-horizon, horizon-horizon, meridian-meridian
- Achieve <2000ms response time for global paran searches
- Include visibility filters: both visible, meridian visible only, geometric horizon
- Cross-validate results against established astrological software

---

## Context

### Key Files and Patterns
```yaml
reference_files:
  - "docs/reference/Parans reference doc.md": Complete mathematical specifications
  - "backend/app/core/acg/acg_core.py": Existing ACG calculation patterns
  - "backend/app/core/ephemeris/tools/ephemeris.py": Swiss Ephemeris integration
  - "backend/app/api/routes/acg.py": ACG API endpoint patterns
  
mathematical_foundations:
  simultaneity_conditions:
    - "Two bodies on different angles simultaneously"
    - "Body A on meridian (MC/IC) when Body B on horizon (ASC/DSC)"
    - "Both bodies on horizon simultaneously (complex case)"
    - "Meridian-meridian impossible (same longitude)"
    
  precision_requirements:
    - "≤0.03° latitude error for planets"
    - "Robust float64 operations throughout"
    - "Numerical stability for edge cases"
    - "Circumpolar region handling"

paran_calculation_methods:
  closed_form_solutions:
    - "Meridian-Horizon: Analytical solution using required horizon angle"
    - "One body crossing meridian, other crossing horizon"
    - "Direct latitude calculation from declinations and separations"
    
  numerical_methods:
    - "Horizon-Horizon: Numerical root finding (Brent's method/bisection)"
    - "Both bodies simultaneously crossing horizon"
    - "More complex due to coupled equations"
    - "Requires careful initial bracketing"
```

### Paran Types and Visibility
```yaml
paran_types:
  meridian_horizon:
    - "A on MC, B on ASC" # Body A culminating, Body B rising
    - "A on MC, B on DSC" # Body A culminating, Body B setting  
    - "A on IC, B on ASC" # Body A anticulminating, Body B rising
    - "A on IC, B on DSC" # Body A anticulminating, Body B setting
    
  horizon_horizon:
    - "A on ASC, B on DSC" # Body A rising, Body B setting
    - "A on DSC, B on ASC" # Body A setting, Body B rising
    
  meridian_meridian:
    - "Not possible" # Same longitude, different times
    
visibility_conditions:
  both_visible: "Both bodies above apparent horizon"
  meridian_visible: "Only meridian body must be visible"
  geometric: "Use geometric horizon (no refraction)"
  apparent: "Use apparent horizon (with refraction)"
```

---

## Implementation Tasks

### Task 1: Create Core Paran Calculation Engine
**Target**: `backend/app/core/acg/paran_calculator.py`
```yaml
paran_calculator_core:
  ParanCalculator:
    - calculate_paran_line(body_a, body_b, paran_type) -> ParanLine
    - calculate_all_paran_combinations(bodies) -> List[ParanLine]
    - _solve_meridian_horizon_paran(body_a, body_b, angles) -> List[float]
    - _solve_horizon_horizon_paran(body_a, body_b) -> List[float] 
    - _validate_paran_visibility(lat, bodies, visibility_type) -> bool
    
  closed_form_implementation:
    # From Paran reference doc §3.1
    solve_paran_meridian_horizon():
      - Input: declinations, right_ascensions, angle_configuration
      - Calculate: required_horizon_angle = f(delta_alpha, angles)
      - Solve: latitude = arctan2(-cos(H0)·cos(δ), sin(δ))
      - Return: latitude_degrees with precision validation
      
  numerical_solver_implementation:
    # From Paran reference doc §3.2  
    solve_horizon_horizon_paran():
      - Setup: coupled equations for simultaneous horizon crossing
      - Method: Brent's method or bisection for root finding
      - Bracketing: intelligent initial latitude range estimation
      - Convergence: iterate until ≤0.03° precision achieved
```

### Task 2: Implement Mathematical Algorithms
**Target**: `backend/app/core/acg/paran_math.py`
```yaml
mathematical_implementations:
  required_horizon_angle_calculation:
    # Core algorithm from reference doc
    calculate_required_horizon_angle():
      - Input: delta_alpha (RA separation), angle_events
      - Logic: H_req = f(cos(δA)·cos(δB)·cos(Δα) + sin(δA)·sin(δB))
      - Handle: edge cases where cos(H_req) > 1 (no solution)
      - Return: required horizon angle in radians
      
  latitude_solving:
    solve_latitude_from_horizon_angle():
      - Input: declination, required_horizon_angle
      - Formula: φ = arctan2(-cos(H0)·cos(δ), sin(δ))
      - Handle: circumpolar cases (body never sets/rises)
      - Validate: latitude within ±90° range
      
  visibility_calculations:
    check_body_visibility():
      - Calculate: local hour angle at given latitude
      - Determine: if body is above apparent/geometric horizon
      - Apply: atmospheric refraction corrections if needed
      - Return: visibility status and horizon crossing details
      
  numerical_optimization:
    brent_method_solver():
      - Implement: Brent's method for horizon-horizon cases
      - Bracket: intelligent initial range for latitude search
      - Converge: to ≤0.03° precision requirement
      - Handle: multiple solutions and edge cases
```

### Task 3: Create Paran Data Models
**Target**: `backend/app/core/acg/paran_models.py`
```yaml
paran_data_models:
  ParanLine:
    - body_a: PlanetaryBody
    - body_b: PlanetaryBody  
    - paran_type: str  # "mc_asc", "mc_dsc", "ic_asc", "ic_dsc", "asc_dsc"
    - latitude_degrees: float
    - longitude_coverage: Tuple[float, float]  # Full longitude range
    - calculation_method: str  # "closed_form" or "numerical"
    - precision_achieved: float  # Actual precision in degrees
    - visibility_condition: str  # "both_visible", "meridian_only", "geometric"
    - calculation_metadata: Dict[str, Any]
    
  ParanConfiguration:
    - body_pairs: List[Tuple[str, str]]  # Planet pairs to calculate
    - paran_types: List[str]  # Which angle combinations
    - visibility_filter: str  # Visibility requirements
    - precision_target: float  # Target precision (default 0.03°)
    - max_latitude: float  # Latitude bounds (default ±85°)
    - include_circumpolar: bool  # Include extreme latitude solutions
    
  ParanResult:
    - calculated_parans: List[ParanLine]
    - total_combinations: int
    - successful_calculations: int
    - failed_calculations: List[Dict]  # Failed combinations with reasons
    - calculation_time_ms: float
    - average_precision: float
    - precision_statistics: Dict[str, float]
```

### Task 4: Implement Visibility Filtering System
**Target**: `backend/app/core/acg/paran_visibility.py`
```yaml
visibility_system:
  VisibilityFilter:
    - apply_both_visible_filter(paran_lines) -> List[ParanLine]
    - apply_meridian_visible_filter(paran_lines) -> List[ParanLine]
    - apply_geometric_horizon_filter(paran_lines) -> List[ParanLine]
    - calculate_body_visibility_at_latitude(body, lat) -> VisibilityData
    
  visibility_calculations:
    body_visibility_analysis():
      - Calculate: local hour angle for body at given latitude
      - Determine: if body crosses horizon at that latitude  
      - Apply: refraction corrections for apparent horizon
      - Return: detailed visibility information
      
    atmospheric_refraction():
      - Standard: 34' refraction at horizon
      - Altitude-dependent: refraction varies with body height
      - Temperature/pressure: corrections for observing conditions
      - Return: refracted apparent altitude
      
  circumpolar_handling:
    detect_circumpolar_bodies():
      - Identify: bodies that never set/rise at given latitude
      - Calculate: circumpolar limits based on declination
      - Handle: parans involving circumpolar bodies
      - Provide: appropriate warnings/metadata
```

### Task 5: Create Paran API Endpoints
**Target**: `backend/app/api/routes/acg.py` (extend existing)
```yaml
paran_api_endpoints:
  "/v2/acg/paran-lines":
    - Calculate paran lines for specified planet pairs
    - Support multiple paran types in single request
    - Visibility filtering options
    - Precision and performance configuration
    
  "/v2/acg/paran-search":
    - Search for all possible parans in chart
    - Filter by visibility conditions
    - Limit results by precision requirements
    - Batch processing for multiple charts
    
  request_schemas:
    ParanCalculationRequest:
      - planet_pairs: List[Tuple[str, str]]
      - paran_types: List[str] = ["mc_asc", "mc_dsc", "ic_asc", "ic_dsc"]
      - visibility_filter: str = "both_visible"
      - precision_target: float = 0.03
      - max_calculation_time_ms: int = 2000
      - include_calculation_metadata: bool = True
      
    ParanSearchRequest:
      - chart_data: NatalChartData
      - include_all_combinations: bool = True
      - visibility_requirements: str = "both_visible"
      - precision_threshold: float = 0.1  # Filter out low-precision results
      - max_results: int = 100
      
  response_schemas:
    ParanCalculationResponse:
      - success: bool
      - paran_lines: List[ParanLine]
      - calculation_summary: ParanCalculationSummary
      - performance_metrics: Dict[str, Any]
      - warnings: List[str]  # Precision warnings, circumpolar notifications
```

### Task 6: Optimize Performance for Complex Calculations
**Target**: Performance optimization for computationally intensive parans
```yaml
performance_optimizations:
  calculation_efficiency:
    - Vectorize declination and RA calculations across planet pairs
    - Pre-compute trigonometric values for repeated use
    - Parallel processing for independent paran calculations
    - Intelligent caching of intermediate mathematical results
    
  numerical_solver_optimization:
    - Smart initial bracketing for faster convergence
    - Adaptive step sizing based on function behavior
    - Early termination when precision target achieved
    - Fallback methods for difficult convergence cases
    
  memory_management:
    - Efficient storage of paran line coordinate data
    - Lazy evaluation for large planet combination sets
    - Memory pool management for repeated calculations
    - Garbage collection optimization for long-running searches
    
  caching_strategy:
    paran_specific_caching:
      - Cache paran calculations with planet pair + chart data as key
      - Medium TTL (6 hours) for paran results
      - Separate cache for high-precision vs standard calculations
      - Redis integration for production scaling
```

### Task 7: Integration with Existing ACG System
**Target**: Integrate parans with existing astrocartography features
```yaml
acg_integration:
  unified_acg_response:
    - Add paran lines to existing ACG line collections
    - Maintain GeoJSON format consistency
    - Provide unified styling and metadata
    - Support combined filtering (regular lines + parans)
    
  enhanced_acg_endpoints:
    # Modify existing endpoints
    "/v2/acg/lines":
      - Add include_paran_lines parameter
      - Add paran_configuration parameter
      - Integrate paran results with regular ACG lines
      - Maintain performance standards for combined calculations
      
  visualization_integration:
    - Provide paran-specific styling metadata
    - Generate interactive tooltips for paran line intersections
    - Support paran line highlighting and filtering
    - Create legend entries for different paran types
```

### Task 8: Comprehensive Testing and Validation
**Target**: `backend/tests/core/acg/test_paran_calculator.py`
```yaml
test_coverage:
  mathematical_accuracy_tests:
    - test_closed_form_solution_accuracy()
    - test_numerical_solver_convergence()
    - test_precision_requirements_met()
    - test_edge_case_handling()
    - test_circumpolar_region_calculations()
    
  paran_type_tests:
    - test_meridian_horizon_paran_calculations()
    - test_horizon_horizon_paran_calculations()
    - test_all_angle_combinations()
    - test_visibility_filtering_accuracy()
    
  integration_tests:
    - test_paran_api_endpoints()
    - test_acg_integration()
    - test_performance_benchmarks()
    - test_cache_integration()
    
  validation_against_references:
    - Cross-validate against established astrological software
    - Test known planetary configurations with verified paran positions
    - Validate mathematical implementations against reference sources
    - Test precision across full range of declinations and separations
    
  performance_benchmarks:
    - Single paran calculation <50ms
    - Full planet combination set <2000ms
    - Memory usage optimization validation
    - Cache effectiveness under load
```

---

## Validation Gates

### Mathematical Validation
- [ ] All paran calculations achieve ≤0.03° latitude precision
- [ ] Closed-form solutions match analytical expectations
- [ ] Numerical solvers converge within precision requirements
- [ ] Circumpolar region handling mathematically correct
- [ ] Visibility calculations accurate for all latitude ranges
- [ ] Cross-validation against established astrological software

### Technical Validation
- [ ] All unit tests pass with >90% code coverage
- [ ] Performance benchmarks meet <2000ms global search target
- [ ] API endpoints handle all error conditions gracefully
- [ ] Integration with existing ACG system maintains performance
- [ ] Cache integration optimizes repeated calculations
- [ ] Memory usage remains within acceptable limits

### Astrological Validation
- [ ] Paran line positions match traditional astrological sources
- [ ] Visibility filtering enables meaningful astrological analysis
- [ ] All paran types (meridian-horizon, horizon-horizon) calculated correctly
- [ ] Results validate against professional astrological software
- [ ] Edge cases produce appropriate warnings and metadata
- [ ] Precision standards meet professional astrology requirements

### Integration Validation
- [ ] Paran API endpoints integrate with ACG system architecture
- [ ] Response schemas include all required paran metadata
- [ ] Service layer follows established error handling patterns
- [ ] Feature can be enabled/disabled via configuration flags
- [ ] Documentation includes mathematical references and usage examples
- [ ] Rate limiting appropriate for computationally intensive operations

---

## Final Validation Checklist

### Code Quality
- [ ] `pytest backend/tests/core/acg/test_paran_calculator.py -v`
- [ ] `pytest --cov=backend/app/core/acg/paran_calculator --cov-report=term-missing`
- [ ] `ruff check backend/app/core/acg/paran_calculator.py`
- [ ] `mypy backend/app/core/acg/paran_calculator.py`

### Mathematical Accuracy
- [ ] `python backend/scripts/validate_paran_precision.py` shows ≤0.03° error
- [ ] Cross-validation against Swiss Ephemeris mathematical functions
- [ ] Numerical solver convergence testing across full parameter ranges
- [ ] Edge case validation for extreme declinations and separations

### Performance Validation
- [ ] Paran search performance meets <2000ms target for full planet set
- [ ] Single paran calculation <50ms for typical cases
- [ ] Memory usage <50MB for largest paran calculation sets
- [ ] Cache hit rate >50% for repeated paran requests

### API Integration
- [ ] `/v2/acg/paran-lines` endpoint fully functional
- [ ] `/v2/acg/paran-search` endpoint operational
- [ ] Enhanced `/v2/acg/lines` includes paran integration
- [ ] Response validation passes for all paran calculation types
- [ ] Error handling returns meaningful feedback for failed calculations

### Astrological Professional Standards
- [ ] Paran calculations match established astrological references
- [ ] Precision meets standards for professional astrological software
- [ ] Visibility filtering enables traditional astrological analysis
- [ ] Results cross-validated against multiple astrological software packages
- [ ] Documentation includes astrological context and interpretation guidance

---

**Implementation Priority: MEDIUM - Advanced feature for specialized astrocartography**

**Dependencies**: Existing ACG system, advanced mathematical libraries, numerical optimization

**Estimated Complexity**: HIGH (complex mathematical implementations, precision requirements)

**Success Metrics**: ≤0.03° precision, <2000ms global search, validated against professional software