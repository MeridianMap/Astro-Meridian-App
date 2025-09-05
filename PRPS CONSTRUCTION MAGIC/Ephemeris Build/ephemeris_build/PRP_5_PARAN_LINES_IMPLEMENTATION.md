# PRP 5: Jim Lewis ACG Paran Lines Implementation – Planetary Simultaneity

## Reference: Jim Lewis ACG Parans Technical Reference & ACG Planetary Simultaneity

---

## Feature Goal
Implement Jim Lewis-style ACG planetary paran calculations where two planets are simultaneously angular on different cardinal angles (ASC, DSC, MC, IC), producing constant-latitude parallels with ≤0.03° precision.

## Deliverable
A complete ACG paran calculation module (`backend/app/core/acg/paran_calculator.py`) implementing closed-form meridian-horizon solutions and numerical horizon-horizon methods according to Jim Lewis ACG standards.

## Success Definition
- Calculate ACG planetary parans with ≤0.03° latitude accuracy using Jim Lewis methods
- Support all simultaneity conditions: meridian-horizon (primary), horizon-horizon 
- Achieve <800ms response time for global paran searches (optimized for closed-form dominance)
- Include ACG-standard visibility filters: all, both_visible, meridian_visible_only
- Validate against Jim Lewis ACG software and established ACG references

---

## Context

### Key Files and Patterns
```yaml
reference_files:
  - "BUILD RESOURCES/Astrological Reference/Parans reference doc.md": Jim Lewis ACG paran specifications
  - "backend/app/core/acg/acg_core.py": Existing ACG calculation patterns
  - "backend/app/core/ephemeris/tools/ephemeris.py": Swiss Ephemeris integration
  - "backend/app/api/routes/acg.py": ACG API endpoint patterns
  
jim_lewis_acg_foundations:
  simultaneity_equation:
    - "α_A + H_e(A, φ) = α_B + H_e(B, φ) (mod 2π)"
    - "Planets A and B simultaneously angular at latitude φ"
    - "Uses geocentric apparent places on true equator/equinox of date"
    
  event_types:
    - "R (rising): H^R = -H₀"
    - "S (setting): H^S = +H₀" 
    - "MC (upper culmination): H^MC = 0"
    - "IC (lower culmination): H^IC = π"
    
  closed_form_solutions:
    - "Meridian-Horizon: φ = atan2(-cos(H₀)·cos(δ), sin(δ))"
    - "H₀ = wrap_0_π(Δα + H_const) for meridian-horizon pairs"
    - "Direct analytical solution, no iteration required"
    
  numerical_methods:
    - "Horizon-Horizon: Brent root finding on coupled equations"
    - "F(φ) = s_A·arccos(-tan(φ)·tan(δ_A)) - s_B·arccos(-tan(φ)·tan(δ_B)) - Δα"
    - "Robust bracketing with domain validation"
```

### Jim Lewis ACG Paran Types
```yaml
acg_paran_pairs:
  recommended_default_set:
    # For each unordered planet pair {A, B}, compute:
    - "A on horizon (R,S) with B on MC,IC (4 combinations)"
    - "B on horizon (R,S) with A on MC,IC (4 combinations)"
    # Total: 8 paran lines per planet pair
    
  meridian_horizon_pairs:
    - "MC-R, MC-S, IC-R, IC-S" # Meridian body with horizon body
    - "Closed-form analytical solution available"
    - "Primary ACG paran type - most commonly used"
    
  horizon_horizon_pairs:
    - "R-S combinations" # Both bodies on horizon
    - "Numerical solution required (Brent method)"
    - "Less common but mathematically valid"
    
  degenerate_cases:
    - "MC-MC, IC-IC, MC-IC" # Both on meridian
    - "Solutions only when Δα ∈ {0, ±π} - suppress as trivial"

acg_visibility_modes:
  all: "No visibility filter - geometric only"
  both_visible: "Both planets above geometric horizon"
  meridian_visible_only: "Only meridian planet must be visible"
  
horizon_conventions:
  default: "Geometric horizon (h = 0°) for line placement"
  optional: "Apparent horizon with refraction (-0.5667°) for visibility only"
```

---

## Implementation Tasks

### Task 1: Create Jim Lewis ACG Paran Calculator
**Target**: `backend/app/core/acg/paran_calculator.py`
```yaml
acg_paran_calculator:
  ACGParanCalculator:
    - calculate_planetary_parans(planets, pairs) -> List[ParanLine]
    - _solve_meridian_horizon_closed_form(body_a, body_b, events) -> float
    - _solve_horizon_horizon_numerical(body_a, body_b, events) -> Optional[float]
    - _apply_visibility_filter(paran_line, mode) -> bool
    - _validate_domain_constraints(phi, delta_values) -> bool
    
  jim_lewis_closed_form:
    # Direct implementation of reference doc equations
    meridian_horizon_solution():
      - Input: alpha_meridian, delta_meridian, alpha_horizon, delta_horizon
      - Calculate: delta_alpha = wrap_minus_pi_pi(alpha_meridian - alpha_horizon)
      - Calculate: H0 = wrap_0_pi(delta_alpha + H_const_meridian)
      - Solve: phi = atan2(-cos(H0) * cos(delta_horizon), sin(delta_horizon))
      - Return: latitude in degrees with validation
      
  jim_lewis_numerical_solver:
    # From reference doc §3.2 - horizon vs horizon
    solve_horizon_horizon_paran():
      - Setup: F(φ) = s_A·arccos(-tan(φ)·tan(δ_A)) - s_B·arccos(-tan(φ)·tan(δ_B)) - Δα
      - Method: Brent root finding with domain validation
      - Domain: reject intervals where |tan(φ)tan(δ)| > 1 (no horizon crossing)
      - Convergence: target ≤0.03° latitude precision
```

### Task 2: Implement ACG Paran Mathematical Algorithms
**Target**: `backend/app/core/acg/paran_math.py`
```yaml
jim_lewis_mathematical_implementations:
  spherical_astronomy_helpers:
    # Core identities from reference doc §2
    hour_angle_constants():
      - H_MC = 0 (upper culmination)
      - H_IC = π (lower culmination) 
      - H_R = -H₀ (rising, negative hour angle)
      - H_S = +H₀ (setting, positive hour angle)
      - H₀ = arccos(-tan(φ)·tan(δ)) when |tan(φ)tan(δ)| ≤ 1
      
  closed_form_meridian_horizon:
    # Direct implementation of reference doc §3.1
    solve_meridian_horizon_paran():
      - Input: (α_meridian, δ_meridian), (α_horizon, δ_horizon), event_types
      - Calculate: Δα = wrap_minus_pi_pi(α_meridian - α_horizon)
      - Calculate: H₀ = wrap_0_pi(Δα + H_const_meridian)
      - Solve: φ = atan2(-cos(H₀)·cos(δ_horizon), sin(δ_horizon))
      - Validate: result within [-89.999°, +89.999°]
      
  numerical_horizon_horizon:
    # Implementation of reference doc §3.2
    brent_solver_horizon_horizon():
      - Setup: F(φ) = s_A·arccos(clip(-tan(φ)·tan(δ_A))) - s_B·arccos(clip(-tan(φ)·tan(δ_B))) - Δα_general
      - Domain: validate |tan(φ)tan(δ)| ≤ 1 for both bodies
      - Bracket: φ ∈ [-89.9°, +89.9°] with domain exclusions
      - Converge: tolerance = 1e-8 radians (≤0.03° precision)
      
  visibility_filters:
    # ACG-standard visibility checking
    apply_acg_visibility_filter():
      - Mode 'all': no filtering beyond geometric constraints
      - Mode 'both_visible': both planets h > 0° at calculated latitude
      - Mode 'meridian_visible_only': only meridian body h > 0°
      - Use: sin(h) = sin(φ)sin(δ) + cos(φ)cos(δ)cos(H)
```

### Task 3: Create ACG Paran Data Models
**Target**: `backend/app/core/acg/paran_models.py`
```yaml
acg_paran_data_models:
  ACGParanLine:
    - planet_a: str  # "Sun", "Moon", "Mercury", etc.
    - event_a: str   # "MC", "IC", "R", "S"
    - planet_b: str  # Second planet
    - event_b: str   # Second planet's event
    - latitude_deg: float  # Constant latitude where simultaneity occurs
    - calculation_method: str  # "closed_form" or "numerical"
    - precision_achieved: float  # Actual precision in degrees
    - visibility_status: str  # "all", "both_visible", "meridian_only"
    - epoch_utc: datetime  # Calculation epoch
    - line_id: str  # Unique identifier for this paran line
    
  ACGParanConfiguration:
    - planet_pairs: List[Tuple[str, str]]  # Unordered pairs like [("Sun", "Mars")]
    - event_combinations: List[str] = ["meridian_horizon", "horizon_horizon"]
    - visibility_mode: str = "all"  # ACG standard visibility filter
    - horizon_convention: str = "geometric"  # "geometric" or "apparent" 
    - precision_target: float = 0.03  # Target precision in degrees
    - time_anchor: str = "12:00Z"  # Fixed daily epoch for deterministic results
    - include_both_directions: bool = True  # A-B and B-A pairs
    
  ACGParanResult:
    - paran_lines: List[ACGParanLine]
    - total_planet_pairs: int
    - total_paran_lines_calculated: int
    - failed_calculations: List[Dict[str, Any]]  # With failure reasons
    - calculation_summary: Dict[str, int]  # counts by method type
    - performance_metrics: Dict[str, float]  # timing and precision stats
    - metadata: Dict[str, Any]  # epoch, models used, etc.
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

### Task 6: Optimize Performance for ACG Paran Calculations
**Target**: Performance optimization for production ACG paran usage
```yaml
acg_performance_optimizations:
  calculation_efficiency:
    - Vectorize closed-form meridian-horizon calculations (majority of parans)
    - Pre-compute sin(δ), cos(δ), tan(δ) arrays for all planets
    - Batch process planet pairs to minimize function call overhead
    - Use numpy operations for angle wrapping and trigonometric functions
    
  numerical_solver_optimization:
    - Limit numerical methods to horizon-horizon cases only (minority)
    - Smart domain bracketing to avoid |tan(φ)tan(δ)| > 1 regions
    - Early termination for Brent solver when precision achieved
    - Fallback to bisection if Brent method fails to converge
    
  memory_management:
    - Efficient storage of constant-latitude parallel coordinates
    - Reuse trig pre-computations across multiple paran calculations
    - Lazy generation of longitude grids for parallel rendering
    - Memory pool for repeated ACG calculations
    
  acg_caching_strategy:
    epoch_based_caching:
      - Cache planetary positions by epoch (12:00Z anchor)
      - Cache paran results with planet_pair + epoch key
      - TTL: 24 hours (planetary positions change slowly)
      - Separate cache tiers for different precision requirements
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

### Task 8: Comprehensive ACG Paran Testing and Validation
**Target**: `backend/tests/core/acg/test_acg_paran_calculator.py`
```yaml
acg_test_coverage:
  jim_lewis_mathematical_accuracy:
    - test_closed_form_meridian_horizon_accuracy()
    - test_numerical_horizon_horizon_convergence()
    - test_simultaneity_equation_validation()
    - test_latitude_precision_requirements()
    - test_domain_constraint_handling()
    
  acg_paran_type_validation:
    - test_all_meridian_horizon_combinations()
    - test_horizon_horizon_numerical_solutions()
    - test_planet_pair_enumeration_policy()
    - test_acg_visibility_filtering_modes()
    - test_degenerate_case_suppression()
    
  integration_and_performance:
    - test_acg_paran_api_endpoints()
    - test_integration_with_existing_acg_system()
    - test_performance_benchmarks_meet_targets()
    - test_cache_integration_and_effectiveness()
    
  jim_lewis_acg_validation:
    - test_against_jim_lewis_acg_software_results()
    - test_known_planetary_configurations_from_acg_literature()
    - test_mathematical_implementation_against_reference_doc()
    - test_precision_across_declination_ranges()
    - test_constant_latitude_parallel_generation()
    
  acg_performance_benchmarks:
    - Single meridian-horizon paran <10ms (closed-form)
    - Single horizon-horizon paran <100ms (numerical)
    - Full 10-planet ACG paran set <800ms total
    - Memory usage <20MB for complete paran calculation
    - Cache effectiveness >60% for repeated ACG requests
```

---

## Validation Gates

### Mathematical Validation
- [ ] All ACG paran calculations achieve ≤0.03° latitude precision
- [ ] Closed-form meridian-horizon solutions match Jim Lewis ACG standards
- [ ] Numerical horizon-horizon solvers converge within precision requirements
- [ ] Simultaneity equation: α_A + H_e(A, φ) = α_B + H_e(B, φ) verified
- [ ] Domain validation prevents |tan(φ)tan(δ)| > 1 calculation attempts
- [ ] Results produce true constant-latitude parallels (no longitude curvature)

### Technical Validation
- [ ] All unit tests pass with >90% code coverage
- [ ] Performance benchmarks meet <2000ms global search target
- [ ] API endpoints handle all error conditions gracefully
- [ ] Integration with existing ACG system maintains performance
- [ ] Cache integration optimizes repeated calculations
- [ ] Memory usage remains within acceptable limits

### Jim Lewis ACG Validation
- [ ] Paran line positions match Jim Lewis ACG software and literature
- [ ] ACG visibility filtering modes work according to astrocartography standards
- [ ] Planet-planet parans (not fixed-star) calculated per ACG conventions
- [ ] Results use geocentric apparent places on true equator/equinox of date
- [ ] Geometric horizon (h=0°) used for line placement, refraction only for visibility
- [ ] Constant-latitude parallels match established ACG mapping standards

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

### ACG Professional Standards
- [ ] Paran calculations match Jim Lewis ACG methodology and standards
- [ ] Precision meets or exceeds commercial ACG software accuracy
- [ ] Visibility filtering supports traditional ACG astrocartography practice
- [ ] Results cross-validated against established ACG software packages
- [ ] Documentation includes ACG historical context and usage guidance
- [ ] Implementation supports classic ACG pair enumeration policies

---

**Implementation Priority: MEDIUM - Advanced ACG feature, simplified from original Brady parans**

**Dependencies**: Existing ACG system, numpy for vectorized operations, scipy for numerical solvers

**Estimated Complexity**: MEDIUM (mostly closed-form solutions, well-defined mathematical spec)

**Success Metrics**: ≤0.03° precision, <800ms global search, validated against Jim Lewis ACG standards