# PRP 4: Enhanced ACG Lines – Retrograde-Aware Astrocartography

## Reference: Ephemeris Extensions Content and Plan - Priority 2 ACG Enhancement & Astrocartography Technical References

---

## Feature Goal
Enhance the existing ACG (Astrocartography) system with retrograde-aware line metadata, aspect-to-angle lines, and advanced visualization features while maintaining the current GeoJSON performance standards.

## Deliverable
Enhanced ACG line calculation system with retrograde motion integration, aspect-to-angle line support, and comprehensive metadata for advanced astrocartography visualizations.

## Success Definition
- Integrate retrograde status into all ACG line calculations and metadata
- Implement aspect-to-angle lines (aspects to MC/ASC/IC/DSC)
- Add filtering capabilities based on planet motion status
- Maintain existing ACG performance benchmarks (<800ms for global calculations)
- Provide styling metadata for retrograde vs direct motion visualization

---

## Context

### Key Files and Patterns
```yaml
existing_acg_system:
  - "backend/app/core/acg/": Existing ACG calculation engine
  - "backend/app/api/routes/acg.py": Current ACG API endpoints
  - "backend/app/core/ephemeris/tools/enhanced_calculations.py": Retrograde detection
  - "docs/reference/Astrocartography Lines — Technical Implementation Reference.md": Mathematical foundations
  - "docs/reference/Aspect astrocartography math ref.md": Aspect line mathematics

mathematical_references:
  astrocartography_foundations:
    - "Angular Lines: MC/IC (meridian), ASC/DSC (horizon)"
    - "Great circle projections from topocentric coordinates"
    - "Local Space mapping with azimuth calculations"
    - "Node handling: South Node = North Node + 180°"
    
  aspect_to_angle_calculations:
    - "Local angle longitude calculations from LST and obliquity"
    - "Aspect condition checking with orb tolerances"
    - "Contour methods for curved aspect loci"
    - "Edge case handling for circumpolar regions"

existing_retrograde_integration:
  - "Retrograde detection already implemented in enhanced_calculations.py"
  - "Daily motion analysis available"
  - "Motion status metadata ready for integration"
```

### Enhancement Architecture
```yaml
retrograde_aware_features:
  line_metadata_enhancements:
    - "Motion status for each ACG line (direct/retrograde/stationary)"
    - "Motion speed and direction information"
    - "Retrograde period duration and timing"
    - "Styling hints for different motion states"
    
  filtering_capabilities:
    - "Filter lines by motion status"
    - "Show only retrograde/direct lines"
    - "Motion-based color coding"
    - "Time-based motion visualization"

aspect_to_angle_lines:
  supported_aspects:
    - "Major aspects to MC: conjunction, opposition, trine, square, sextile"
    - "Major aspects to ASC: conjunction, opposition, trine, square, sextile"  
    - "Optional minor aspects: semi-sextile, quincunx"
    - "Configurable orb system matching aspect calculations"
    
  calculation_methods:
    - "Local MC/ASC longitude calculation from coordinates"
    - "Aspect condition evaluation with orb tolerance" 
    - "Contour line generation for curved aspect paths"
    - "GeoJSON feature generation with aspect metadata"
```

---

## Implementation Tasks

### Task 1: Enhance ACG Line Metadata System
**Target**: `backend/app/core/acg/enhanced_metadata.py`
```yaml
metadata_enhancements:
  RetrogradeAwareLineMetadata:
    - motion_status: str  # "direct", "retrograde", "stationary_direct", "stationary_retrograde"
    - daily_motion: float  # degrees per day
    - motion_speed_percentile: float  # relative to normal speed
    - is_approaching_station: bool
    - days_until_station: Optional[int]
    - retrograde_period_info: Optional[Dict]
    - styling_hints: Dict[str, Any]  # Color, opacity, line style hints
    
  enhanced_line_properties:
    - planetary_dignity: str  # rulership, exaltation, detriment, fall
    - sign_position: str  # current zodiacal sign
    - element_and_modality: Dict[str, str]  # fire/earth/air/water, cardinal/fixed/mutable
    - house_system_positions: Dict[str, int]  # positions in various house systems
    
  visualization_metadata:
    motion_styling:
      retrograde:
        color_hint: "#cc3333"  # Reddish for retrograde
        line_style: "dashed"
        opacity: 0.7
      direct:
        color_hint: "#3366cc"  # Blue for direct
        line_style: "solid" 
        opacity: 0.9
      stationary:
        color_hint: "#ffaa00"  # Orange for stations
        line_style: "dotted"
        opacity: 0.8
```

### Task 2: Implement Aspect-to-Angle Line Calculator
**Target**: `backend/app/core/acg/aspect_lines.py`
```yaml
aspect_line_calculator:
  AspectToAngleCalculator:
    - calculate_aspect_to_mc_lines(planet, aspect_type, orb) -> GeoJSONFeature
    - calculate_aspect_to_asc_lines(planet, aspect_type, orb) -> GeoJSONFeature
    - calculate_all_aspect_lines(planet, aspects_config) -> List[GeoJSONFeature]
    - _local_mc_longitude(lat, lon, planet_position) -> float
    - _local_asc_longitude(lat, lon, planet_position) -> float
    
  mathematical_implementations:
    # From aspect astrocartography math reference
    local_angle_calculations:
      - calculate_local_mc_longitude(LST, obliquity) -> longitude
      - calculate_local_asc_longitude(LST, obliquity, latitude) -> longitude
      - aspect_condition_check(planet_lon, angle_lon, aspect, orb) -> bool
      
    contour_generation:
      - generate_aspect_contours(planet, aspect_angle, orb) -> List[coordinates]
      - handle_circumpolar_regions() -> modified_contours
      - optimize_line_resolution(contours) -> optimized_coordinates
      
  orb_integration:
    - Use same orb system as main aspect calculations
    - Support custom orbs for aspect-to-angle lines
    - Provide orb visualization (wider/narrower line rendering)
```

### Task 3: Integrate Retrograde Data with Existing ACG System
**Target**: `backend/app/core/acg/acg_core.py` (modify existing)
```yaml
existing_system_enhancements:
  acg_calculate_lines_enhancement:
    # Modify existing function to include retrograde metadata
    - Integrate with enhanced_calculations.py retrograde detection
    - Add motion status to existing line calculations
    - Preserve existing performance characteristics
    - Maintain backward compatibility for existing API consumers
    
  line_generation_updates:
    planetary_line_enhancement:
      - Add retrograde status to MC/IC/ASC/DSC line metadata
      - Include motion speed and direction information
      - Add station timing and approach information
      - Generate styling hints based on motion status
      
    node_line_special_handling:
      # Lunar nodes are always retrograde in mean calculation
      - Mark North Node lines as "mean_retrograde"
      - Calculate South Node as NN + 180° with derived retrograde status
      - Add node-specific motion characteristics
```

### Task 4: Create Aspect-to-Angle API Endpoints
**Target**: `backend/app/api/routes/acg.py` (enhance existing)
```yaml
new_acg_endpoints:
  "/v2/acg/aspect-lines":
    - Calculate aspect-to-angle lines for specific planet
    - Support multiple aspect types in single request
    - Orb configuration matching main aspect system
    - Planet filtering and batch processing
    
  enhanced_existing_endpoints:
    "/v2/acg/lines":
      - Add include_retrograde_metadata parameter
      - Add motion_status_filter parameter  
      - Add include_aspect_lines parameter
      - Maintain existing response structure with metadata additions
      
  request_schema_updates:
    ACGLinesRequest:
      - include_retrograde_metadata: bool = True
      - motion_status_filter: Optional[List[str]] = None  # ["direct", "retrograde"]
      - include_aspect_lines: bool = False
      - aspect_lines_config: Optional[AspectLinesConfig] = None
      
    AspectLinesConfig:
      - aspects: List[str] = ["conjunction", "opposition", "trine", "square"]
      - orb_preset: str = "traditional"
      - custom_orbs: Optional[Dict[str, float]] = None
      - include_minor_aspects: bool = False
```

### Task 5: Implement Motion-Based Filtering System
**Target**: `backend/app/core/acg/filters.py`
```yaml
filtering_system:
  MotionBasedFilter:
    - filter_by_motion_status(lines, status_list) -> filtered_lines
    - filter_by_motion_speed(lines, speed_range) -> filtered_lines
    - filter_approaching_stations(lines, days_threshold) -> filtered_lines
    - apply_motion_styling(lines, style_config) -> styled_lines
    
  advanced_filtering:
    - filter_by_retrograde_period(lines, date_range) -> filtered_lines
    - filter_by_planetary_dignity(lines, dignity_types) -> filtered_lines
    - combine_multiple_filters(lines, filter_config) -> filtered_lines
    
  performance_optimization:
    - pre_index_lines_by_motion_status() # Optimize filtering
    - cache_filtered_results() # Cache common filter combinations
    - lazy_load_metadata() # Only load metadata when needed
```

### Task 6: Enhance Visualization Metadata System
**Target**: `backend/app/core/acg/visualization.py`
```yaml
visualization_enhancements:
  VisualizationMetadataGenerator:
    - generate_motion_styling(motion_status, planet) -> StyleMetadata
    - generate_aspect_styling(aspect_type, strength) -> StyleMetadata
    - generate_interactive_metadata(line_type, planet) -> InteractiveMetadata
    - create_legend_metadata(active_filters) -> LegendData
    
  styling_system:
    motion_based_styling:
      - Color schemes for different motion states
      - Line style variations (solid, dashed, dotted)
      - Opacity adjustments for motion emphasis
      - Animation hints for time-based visualization
      
    aspect_line_styling:
      - Distinct colors for different aspect types
      - Line width based on orb exactness
      - Curved line rendering hints
      - Interactive tooltip data
      
  frontend_integration_metadata:
    - Three.js compatible styling hints
    - D3.js/Leaflet compatible properties
    - Interactive behavior specifications
    - Animation timing and easing suggestions
```

### Task 7: Performance Optimization for Enhanced Features
**Target**: Maintain existing ACG performance standards
```yaml
performance_optimizations:
  calculation_efficiency:
    - Vectorize retrograde status checks across multiple planets
    - Pre-compute aspect line base calculations  
    - Cache motion metadata for repeated requests
    - Optimize contour generation algorithms
    
  memory_management:
    - Efficient storage of enhanced metadata
    - Lazy loading of optional enhancement features
    - Memory pool management for large line datasets
    - Garbage collection optimization for GeoJSON generation
    
  caching_strategy:
    enhanced_cache_keys:
      - Include retrograde status in cache keys
      - Separate cache for aspect lines
      - TTL optimization for motion-based data (shorter for retrograde)
      - Redis clustering for enhanced metadata storage
```

### Task 8: Comprehensive Testing Suite
**Target**: `backend/tests/core/acg/test_enhanced_acg.py`
```yaml
test_coverage:
  retrograde_integration_tests:
    - test_retrograde_metadata_accuracy()
    - test_motion_status_filtering()
    - test_retrograde_styling_generation()
    - test_station_timing_calculations()
    - test_motion_speed_percentile_accuracy()
    
  aspect_line_tests:
    - test_aspect_to_mc_line_accuracy()
    - test_aspect_to_asc_line_accuracy()
    - test_contour_generation_precision()
    - test_orb_system_integration()
    - test_circumpolar_region_handling()
    
  performance_benchmarks:
    - benchmark_enhanced_acg_calculation_speed()
    - test_memory_usage_with_enhancements()
    - benchmark_aspect_line_generation_performance()
    - test_filtering_system_efficiency()
    
  integration_tests:
    - test_enhanced_api_endpoints()
    - test_backward_compatibility()
    - test_visualization_metadata_generation()
    - test_cache_integration_with_enhancements()
    
  mathematical_validation:
    - validate_aspect_line_positions_against_reference()
    - test_local_angle_calculation_accuracy()
    - validate_contour_mathematical_correctness()
    - cross_reference_motion_calculations()
```

---

## Validation Gates

### Technical Validation
- [ ] All unit tests pass with >90% code coverage
- [ ] Performance benchmarks maintain existing <800ms global ACG calculation
- [ ] Retrograde metadata integration accurate across all planets
- [ ] Aspect-to-angle calculations match mathematical references
- [ ] API endpoints maintain backward compatibility
- [ ] Enhanced features can be disabled via configuration

### Mathematical Validation
- [ ] Aspect-to-angle lines validate against mathematical references
- [ ] Local angle calculations accurate to 0.1 arcsecond precision
- [ ] Contour generation produces mathematically correct curves
- [ ] Retrograde motion integration matches Swiss Ephemeris data
- [ ] Node line derivation (SN = NN + 180°) maintains mathematical accuracy
- [ ] Circumpolar region handling robust for extreme coordinates

### Integration Validation
- [ ] Enhanced ACG endpoints functional with all new features
- [ ] Visualization metadata enables proper frontend rendering
- [ ] Motion-based filtering works correctly for all filter combinations
- [ ] Styling hints produce visually distinct retrograde/direct lines
- [ ] Caching system handles enhanced metadata efficiently
- [ ] API responses include all required enhancement metadata

### Astrological Validation
- [ ] Retrograde line identification matches astrological software
- [ ] Aspect-to-angle lines align with traditional astrological interpretations
- [ ] Motion status filtering enables meaningful astrological analysis
- [ ] Styling recommendations support astrological visualization practices
- [ ] Station timing calculations assist in predictive astrology

---

## Final Validation Checklist

### Code Quality
- [ ] `pytest backend/tests/core/acg/test_enhanced_acg.py -v`
- [ ] `pytest --cov=backend/app/core/acg --cov-report=term-missing`
- [ ] `ruff check backend/app/core/acg/`
- [ ] `mypy backend/app/core/acg/`

### Performance Validation
- [ ] Enhanced ACG calculations maintain <800ms global performance
- [ ] Aspect line generation completes within <600ms for all planets
- [ ] Memory usage increase <20% compared to base ACG system
- [ ] Cache hit rate remains >70% with enhanced features

### API Integration
- [ ] `/v2/acg/lines` enhanced endpoint functional with new parameters
- [ ] `/v2/acg/aspect-lines` new endpoint fully operational
- [ ] Response validation passes for all enhancement features
- [ ] Error handling appropriate for malformed enhancement requests

### Mathematical Accuracy
- [ ] `python backend/scripts/validate_aspect_lines.py` shows <0.1" precision
- [ ] Cross-validation against Swiss Ephemeris for motion data
- [ ] Contour generation validates against reference calculations
- [ ] Local angle calculations match astronomical software

### Astrological Professional Standards
- [ ] Retrograde visualizations match professional astrological software
- [ ] Aspect-to-angle lines provide meaningful astrological information
- [ ] Motion filtering enables professional astrological analysis
- [ ] Styling system supports traditional astrological color schemes

---

**Implementation Priority: MEDIUM-HIGH - Enhances existing successful ACG system**

**Dependencies**: Existing ACG system, retrograde detection, aspect calculation system

**Estimated Complexity**: MEDIUM (building on existing system, mathematical validation required)

**Success Metrics**: Performance parity with base system, accurate mathematical implementations, professional astrological visualization support