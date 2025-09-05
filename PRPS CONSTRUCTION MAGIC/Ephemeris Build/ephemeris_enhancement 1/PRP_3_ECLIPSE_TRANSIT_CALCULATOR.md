# PRP 3: Eclipse & Transit Calculator – Predictive Astrology Features

## Reference: Ephemeris Extensions Content and Plan - Priority 1 Essential Feature

---

## Feature Goal
Implement a comprehensive eclipse and transit calculation engine that can find upcoming eclipses, planetary transits to specific degrees, and sign ingresses with NASA-validated accuracy.

## Deliverable
A complete predictive calculation module (`backend/app/core/ephemeris/tools/predictive.py`) with dedicated API endpoints for eclipse and transit searches, achieving astronomical accuracy validated against NASA's Five Millennium Canon.

## Success Definition
- Find next solar/lunar eclipses from any given date with <1 minute accuracy
- Calculate planetary transits to specific degrees with precise timing
- Determine sign ingresses for all planets with sub-minute precision
- Achieve <500ms response time for yearly eclipse searches
- Cross-validate results against NASA JPL Horizons data

---

## Context

### Key Files and Patterns
```yaml
reference_files:
  - "backend/app/core/ephemeris/tools/ephemeris.py": Existing Swiss Ephemeris integration
  - "backend/app/core/ephemeris/classes/serialize.py": Data model patterns
  - "backend/app/services/ephemeris_service.py": Service integration patterns
  - "backend/app/api/routes/ephemeris.py": API endpoint patterns
  
swiss_ephemeris_eclipse_functions:
  - "swe_sol_eclipse_when_glob()": Global solar eclipse search
  - "swe_lun_eclipse_when()": Lunar eclipse timing
  - "swe_sol_eclipse_where()": Eclipse visibility calculations
  - "swe_rise_trans()": Transit timing calculations
  
nasa_validation_sources:
  - "NASA Five Millennium Canon of Solar Eclipses": Reference for validation
  - "JPL Horizons System": Planetary position validation
  - "US Naval Observatory Data": Additional cross-reference
```

### Predictive Calculation Types
```yaml
eclipse_calculations:
  solar_eclipses:
    - "Next solar eclipse globally from date"
    - "Solar eclipses in date range"
    - "Eclipse visibility for specific location"
    - "Eclipse type classification (total, partial, annular)"
    
  lunar_eclipses:
    - "Next lunar eclipse from date"
    - "Lunar eclipses in date range" 
    - "Eclipse magnitude and duration"
    - "Penumbral vs umbral eclipse detection"

transit_calculations:
  planetary_transits:
    - "When planet transits specific longitude degree"
    - "Transit duration and exact timing"
    - "Multiple planet transit searches"
    - "Retrograde-aware transit calculations"
    
  sign_ingresses:
    - "When planet enters new zodiacal sign"
    - "All planetary ingresses in time period"
    - "Retrograde ingress handling"
    - "Ingress duration calculations"

advanced_features:
  - "Transit aspects to natal chart points"
  - "Solar/lunar returns timing"
  - "Planetary stations (retrograde/direct)"
  - "Planetary conjunctions and separations"
```

### Performance Requirements
```yaml
response_time_targets:
  single_eclipse_search: "<100ms"
  yearly_eclipse_search: "<500ms"
  single_transit_calculation: "<50ms"
  batch_ingress_calculations: "<200ms"
  
accuracy_requirements:
  eclipse_timing: "±1 minute compared to NASA data"
  transit_timing: "±30 seconds for inner planets"
  ingress_timing: "±10 seconds for sign changes"
  
validation_standards:
  nasa_cross_reference: "100% of eclipse predictions must match NASA Canon"
  jpl_horizons_validation: "Planetary positions within 0.1 arcsecond"
```

---

## Implementation Tasks

### Task 1: Create Eclipse Calculation Engine
**Target**: `backend/app/core/ephemeris/tools/eclipse_calculator.py`
```yaml
eclipse_engine:
  EclipseCalculator:
    - find_next_solar_eclipse(start_date, eclipse_type) -> SolarEclipse
    - find_next_lunar_eclipse(start_date) -> LunarEclipse  
    - find_eclipses_in_range(start_date, end_date, type) -> List[Eclipse]
    - get_eclipse_visibility(eclipse, location) -> EclipseVisibility
    - calculate_eclipse_magnitude(eclipse_data) -> float
    
  swiss_ephemeris_integration:
    - _call_swe_sol_eclipse_when_glob() # Wrapper with error handling
    - _call_swe_lun_eclipse_when() # Wrapper with error handling
    - _call_swe_sol_eclipse_where() # Visibility calculations
    - _process_eclipse_flags() # Interpret Swiss Ephemeris flag results
    - _calculate_eclipse_duration() # Duration from eclipse data
```

### Task 2: Create Transit Calculation Engine
**Target**: `backend/app/core/ephemeris/tools/transit_calculator.py`
```yaml
transit_engine:
  TransitCalculator:
    - find_next_transit(planet_id, target_degree, start_date) -> Transit
    - find_sign_ingress(planet_id, start_date) -> SignIngress
    - find_transits_in_range(planet, degree, start, end) -> List[Transit]
    - find_all_ingresses_in_range(start_date, end_date) -> List[Ingress]
    - calculate_transit_duration(planet, degree, date) -> Duration
    
  retrograde_aware_calculations:
    - _handle_retrograde_transits() # Account for retrograde motion
    - _find_multiple_crossings() # Handle retrograde re-crossings
    - _calculate_station_points() # Find retrograde/direct stations
    - _optimize_search_intervals() # Efficient date range searching
```

### Task 3: Create Predictive Data Models
**Target**: `backend/app/core/ephemeris/tools/predictive_models.py`
```yaml
eclipse_models:
  SolarEclipse:
    - eclipse_type: str  # "total", "partial", "annular", "hybrid"
    - maximum_eclipse_time: datetime
    - eclipse_magnitude: float
    - eclipse_obscuration: float  
    - duration_totality: Optional[float]  # seconds
    - visibility_path: Optional[List[Tuple[float, float]]]  # lat/lon
    - saros_series: int
    - gamma: float  # Eclipse parameter
    
  LunarEclipse:
    - eclipse_type: str  # "total", "partial", "penumbral"
    - maximum_eclipse_time: datetime
    - eclipse_magnitude: float
    - penumbral_magnitude: float
    - totality_duration: Optional[float]  # seconds
    - penumbral_duration: float  # seconds
    - umbral_duration: float  # seconds
    
transit_models:
  Transit:
    - planet_id: int
    - planet_name: str
    - target_longitude: float
    - exact_time: datetime
    - is_retrograde: bool
    - transit_speed: float  # degrees per day
    - approach_duration: float  # days
    - separation_duration: float  # days
    
  SignIngress:
    - planet_id: int
    - planet_name: str
    - from_sign: str
    - to_sign: str
    - ingress_time: datetime
    - retrograde_status: str  # "direct", "retrograde", "stationary"
```

### Task 4: Implement Search Algorithms
**Target**: `backend/app/core/ephemeris/tools/predictive_search.py`
```yaml
search_algorithms:
  EclipseSearchAlgorithms:
    - binary_search_eclipse_time() # Efficient eclipse timing
    - global_eclipse_search() # Worldwide eclipse detection
    - local_eclipse_visibility() # Location-specific calculations
    - eclipse_path_calculation() # Totality path geometry
    
  TransitSearchAlgorithms:
    - binary_search_transit() # Efficient transit timing  
    - interpolated_position_search() # Sub-second precision
    - retrograde_crossing_detection() # Handle complex motion
    - batch_ingress_optimization() # Efficient multi-planet search
    
  optimization_techniques:
    - intelligent_step_sizing() # Adaptive search intervals
    - cache_intermediate_positions() # Performance optimization
    - parallel_planet_processing() # Multi-core utilization
    - early_termination_conditions() # Stop searches when appropriate
```

### Task 5: Create Predictive API Endpoints
**Target**: `backend/app/api/routes/predictive.py`
```yaml
api_endpoints:
  eclipse_endpoints:
    "/v2/eclipses/next-solar":
      - Find next solar eclipse from date
      - Optional location for visibility
      - Eclipse type filtering
      
    "/v2/eclipses/next-lunar":
      - Find next lunar eclipse from date
      - Eclipse magnitude filtering
      - Duration information
      
    "/v2/eclipses/search":
      - Search eclipses in date range
      - Type and location filtering
      - Batch eclipse information
      
  transit_endpoints:
    "/v2/transits/planet-to-degree":
      - Calculate when planet transits specific degree
      - Retrograde handling options
      - Multiple crossing detection
      
    "/v2/transits/sign-ingresses":
      - Find planetary sign changes
      - Date range filtering
      - All planets or specific planet
      
    "/v2/transits/search":
      - General transit search endpoint
      - Multiple criteria support
      - Batch processing capabilities
```

### Task 6: Integrate with Main Service
**Target**: `backend/app/services/ephemeris_service.py`
```yaml
service_integration:
  predictive_service_methods:
    - get_upcoming_eclipses(start_date, count) -> List[Eclipse]
    - find_planetary_transits(planet, criteria) -> List[Transit]
    - calculate_ingress_calendar(date_range) -> IngressCalendar
    - get_eclipse_visibility(eclipse, location) -> Visibility
    
  enhanced_chart_integration:
    - Add predictive features to enhanced endpoint
    - Include upcoming transits to chart points
    - Add eclipse relevance to natal positions
    - Provide solar/lunar return timing
```

### Task 7: NASA Validation and Cross-Reference
**Target**: `backend/app/core/ephemeris/tools/validation.py`
```yaml
validation_system:
  NASAValidator:
    - validate_eclipse_against_canon(eclipse) -> ValidationResult
    - cross_reference_jpl_horizons(positions) -> ValidationReport
    - generate_accuracy_report() -> AccuracyMetrics
    - automated_validation_suite() -> TestResults
    
  reference_data_management:
    - load_nasa_eclipse_catalog() # Reference eclipse data
    - load_jpl_ephemeris_data() # Planetary position references
    - generate_test_cases() # Automated test case creation
    - update_reference_data() # Periodic reference updates
    
  accuracy_monitoring:
    - continuous_accuracy_tracking() # Monitor prediction accuracy
    - deviation_alerting() # Alert on accuracy issues
    - performance_metrics() # Track calculation performance
    - validation_reporting() # Regular accuracy reports
```

### Task 8: Performance Optimization
**Target**: Optimize for real-time predictive calculations
```yaml
performance_optimizations:
  calculation_efficiency:
    - Pre-compute common search intervals
    - Cache frequently requested eclipses/transits
    - Vectorize multiple planet calculations
    - Optimize Swiss Ephemeris call patterns
    
  caching_strategy:
    - Cache eclipse calculations with longer TTL (7 days)
    - Cache transit calculations with medium TTL (24 hours)
    - Redis integration for production scaling
    - Intelligent cache invalidation
    
  search_optimization:
    - Adaptive step sizing for different planets
    - Early termination for impossible conditions
    - Parallel processing for batch requests
    - Memory-efficient data structures
```

### Task 9: Comprehensive Testing Suite
**Target**: `backend/tests/core/ephemeris/tools/test_predictive.py`
```yaml
test_coverage:
  eclipse_testing:
    - test_solar_eclipse_prediction_accuracy()
    - test_lunar_eclipse_timing_precision()
    - test_eclipse_visibility_calculations()
    - test_eclipse_type_classification()
    - test_eclipse_duration_calculations()
    
  transit_testing:
    - test_planetary_transit_accuracy()
    - test_sign_ingress_timing()
    - test_retrograde_transit_handling()
    - test_multiple_crossing_detection()
    - test_batch_ingress_calculations()
    
  nasa_validation_testing:
    - test_against_nasa_eclipse_catalog()
    - test_jpl_horizons_position_accuracy()
    - test_reference_data_consistency()
    - test_automated_validation_suite()
    
  performance_testing:
    - benchmark_eclipse_search_speed()
    - benchmark_transit_calculation_performance()
    - test_memory_usage_optimization()
    - test_cache_effectiveness()
```

---

## Validation Gates

### Technical Validation
- [ ] All unit tests pass with >90% code coverage
- [ ] Performance benchmarks meet <500ms yearly eclipse search
- [ ] Swiss Ephemeris integration handles all error conditions
- [ ] API endpoints provide comprehensive error handling
- [ ] Caching system optimizes repeated calculations
- [ ] Search algorithms handle edge cases (polar regions, leap years)

### Astronomical Validation
- [ ] Eclipse predictions match NASA Five Millennium Canon within 1 minute
- [ ] Planetary positions cross-validate with JPL Horizons within 0.1"
- [ ] Transit timing accurate to ±30 seconds for inner planets
- [ ] Sign ingress calculations accurate to ±10 seconds
- [ ] Retrograde motion handling produces correct multiple crossings
- [ ] Eclipse visibility calculations match astronomical references

### Integration Validation
- [ ] Predictive endpoints integrate with main API architecture
- [ ] Response schemas include all required astronomical metadata
- [ ] Service layer follows established error handling patterns
- [ ] Feature can be enabled/disabled via configuration flags
- [ ] Documentation includes usage examples for all features
- [ ] Rate limiting appropriate for computationally intensive operations

---

## Final Validation Checklist

### Code Quality
- [ ] `pytest backend/tests/core/ephemeris/tools/test_predictive.py -v`
- [ ] `pytest --cov=backend/app/core/ephemeris/tools/predictive --cov-report=term-missing`
- [ ] `ruff check backend/app/core/ephemeris/tools/predictive.py`
- [ ] `mypy backend/app/core/ephemeris/tools/predictive.py`

### Astronomical Accuracy
- [ ] `python backend/scripts/validate_against_nasa.py` shows 100% eclipse match
- [ ] `python backend/scripts/validate_against_jpl.py` shows <0.1" position error
- [ ] Cross-validation against multiple astronomical software packages
- [ ] Edge case testing for extreme dates and locations

### Performance Validation  
- [ ] Eclipse search performance meets <500ms target for 1 year range
- [ ] Transit calculations meet <50ms target for single planet
- [ ] Memory usage stays below 10MB for largest calculations
- [ ] Cache hit rate >60% under realistic load

### API Integration
- [ ] All predictive endpoints functional and documented
- [ ] Response validation passes for all calculation types
- [ ] Error handling returns appropriate HTTP status codes
- [ ] Rate limiting prevents abuse of computationally expensive operations

### Production Readiness
- [ ] NASA validation system runs automatically in CI/CD
- [ ] Monitoring and alerting configured for accuracy deviations
- [ ] Documentation includes usage examples and accuracy statements
- [ ] Feature flags allow gradual rollout of predictive capabilities

---

**Implementation Priority: HIGH - Essential for advanced astrological practice**

**Dependencies**: Swiss Ephemeris eclipse functions, NASA reference data, predictive algorithms

**Estimated Complexity**: HIGH (astronomical accuracy requirements, validation complexity)

**Success Metrics**: NASA-validated accuracy, <500ms yearly searches, comprehensive astronomical features