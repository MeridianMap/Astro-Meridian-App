# BASE PRP: Astrocartography Integration System

## Feature Goal
Implement a complete astrocartography system for the Meridian Ephemeris, including planetary lines (ASC/MC/DC/IC), local space calculations, parans, and astromapping capabilities for professional relocation astrology.

## Deliverable
- Complete astrocartography line calculations for all planets and points
- Local space azimuth and bearing calculations from birth location
- Paran calculations (star/planet rising/setting combinations)
- Astromap coordinate generation for mapping integration
- Professional-grade relocation astrology capabilities

## Success Definition
- Industry-standard astrocartography calculations matching professional software
- Real-time line calculation for interactive mapping applications
- Comprehensive local space analysis from any reference location
- Performance optimized for mapping applications (<200ms line generation)
- Integration with existing ephemeris system without breaking changes

## Context

### Research Documentation
```yaml
docs:
  - url: https://www.astro.com/astrowiki/en/Astrocartography
    focus: "Astrocartography theory and professional applications"
    
  - url: https://www.astro.com/atlas/horoscope?config=acg.cgi
    focus: "Professional astrocartography implementation reference"
    
  - url: https://www.astro.com/swisseph/swephprg.htm#_Toc46391675
    focus: "Swiss Ephemeris coordinate transformations and precision"
    
  - url: https://www.geodatasource.com/developers/javascript
    focus: "Great circle calculations and coordinate geometry"
    
  - url: https://en.wikipedia.org/wiki/Great-circle_distance
    focus: "Mathematical foundations for astrocartography lines"
    
  - url: https://github.com/astronexus/HYG-Database
    focus: "Star catalog for paran calculations"
    
  academic_sources:
    - source: "Jim Lewis - Astrocartography: The Book of Maps"
      focus: "Original astrocartography methodology and theory"
    - source: "Martin Davis - Astrolocality Astrology"  
      focus: "Modern applications and technical implementations"
```

### Existing System Analysis
```yaml
patterns:
  coordinate_systems:
    - file: backend/app/core/ephemeris/charts/natal.py
      analysis: "Current system calculates ecliptic coordinates"
      need: "Add equatorial coordinate transformations"
      integration: "Use existing ChartData for base calculations"
      
  performance_patterns:
    - file: backend/app/core/ephemeris/tools/aspects.py
      copy: "lines 94-172 vectorized calculation patterns"
      follow: "Apply vectorization to astrocartography calculations"
      target: "<200ms for complete astromap generation"
      
  caching_integration:
    - file: backend/app/core/ephemeris/tools/arabic_parts.py
      copy: "lines 615-634 multi-level caching system"
      follow: "Cache astrocartography calculations with location keys"
      optimization: "Location-based cache keys for line reuse"
      
  thread_safety:
    - file: backend/app/core/ephemeris/charts/natal.py
      copy: "lines 142-150 thread-safe calculation pattern"
      follow: "Use existing _calculation_lock for astrocartography"
```

### Implementation Gotchas
```yaml
gotchas:
  - issue: "Great circle calculations computationally expensive"
    fix: "Pre-calculate line segments, not continuous curves"
    optimization: "Generate polyline coordinates for mapping efficiency"
    target: "1000 coordinate points max per line for performance"
    
  - issue: "Coordinate system transformations complexity"
    fix: "Swiss Ephemeris handles equatorial transformations"
    reference: "swe_fixstar_ut() for equatorial coordinates"
    integration: "Use existing SWE calls, add equatorial extraction"
    
  - issue: "Local space calculations relative to birth location"
    fix: "All local space bearings relative to natal chart location"
    formula: "Azimuth from birth location to planetary equivalent locations"
    validation: "Cross-validate with professional astrocartography software"
    
  - issue: "Paran calculations require precise star positions"  
    fix: "Integrate with existing fixed stars system"
    reference: "backend/app/core/ephemeris/tools/fixed_stars.py"
    complexity: "Rising/setting times for specific latitude ranges"
    
  - issue: "Memory usage for multiple planetary lines"
    fix: "Stream line calculations, don't store all in memory"
    pattern: "Generator functions for line coordinate streams"
    target: "<10MB memory usage for complete astromap"
    
  - issue: "Timezone and location accuracy critical"
    fix: "Use high-precision location data with timezone validation"
    integration: "Leverage existing timezone handling from natal charts"
    accuracy: "Sub-kilometer accuracy for professional applications"
```

## Research Process

### 1. Astrocartography Theory Research

#### Core Concepts
```yaml
astrocartography_fundamentals:
  planetary_lines:
    ASC_lines: "Where planets rise on eastern horizon"
    MC_lines: "Where planets culminate at midheaven" 
    DC_lines: "Where planets set on western horizon"
    IC_lines: "Where planets reach lowest point (nadir)"
    
  line_types:
    primary_lines: "Direct planetary contacts with angles"
    aspect_lines: "Square, trine, etc. to angles (secondary importance)"
    local_space: "Azimuth bearings from birth location"
    parans: "Star/planet simultaneous rising/setting"
    
  calculation_principles:
    great_circles: "Planetary lines follow great circle paths on Earth"
    coordinate_systems: "Transform ecliptic to equatorial to geographic"
    time_zones: "All calculations relative to birth time and location"
    precision: "Professional accuracy requires sub-minute precision"
```

#### Mathematical Foundations
```yaml
mathematical_requirements:
  coordinate_transformations:
    ecliptic_to_equatorial: "Obliquity of ecliptic transformation"
    equatorial_to_horizontal: "Local sidereal time and latitude"
    horizontal_to_geographic: "Great circle projection to Earth surface"
    
  great_circle_calculations:
    bearing_formula: "atan2(sin(Δlong)·cos(lat2), cos(lat1)·sin(lat2)−sin(lat1)·cos(lat2)·cos(Δlong))"
    distance_formula: "2·asin(√(sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlong/2)))"
    intermediate_points: "Interpolation along great circle for polyline generation"
    
  local_space_calculations:
    azimuth_formula: "Bearing from birth location to planetary equivalent"
    elevation_consideration: "Account for planetary altitude above horizon"
    distance_scaling: "Normalize distances for practical application"
```

### 2. Technical Architecture Research

#### System Architecture Requirements
```yaml
system_architecture:
  calculation_engine:
    - "AstrocartographyCalculator class for primary calculations"
    - "LocalSpaceCalculator for azimuth and bearing analysis"  
    - "ParanCalculator for star/planet simultaneous contacts"
    - "LineGeometryGenerator for mapping coordinate output"
    
  performance_optimization:
    - "Vectorized calculations using numpy for line generation"
    - "Streaming coordinate generation to minimize memory usage"
    - "Location-based caching for common astromap requests"
    - "Parallel processing for multiple planetary line calculations"
    
  integration_points:
    - "Existing ChartData as foundation for astrocartography"
    - "Swiss Ephemeris coordinate transformations"
    - "Fixed stars system for paran calculations"
    - "Caching system for location-based optimizations"
```

#### Professional Software Compatibility
```yaml
compatibility_research:
  industry_standards:
    coordinate_precision: "Sub-arc-minute accuracy for professional use"
    line_resolution: "1000 coordinate points maximum per line"
    calculation_speed: "<200ms for complete planetary line set"
    memory_efficiency: "<10MB for complete astromap data"
    
  output_formats:
    gis_compatible: "WGS84 coordinate system for mapping integration"
    json_api: "RESTful API with coordinate arrays for web applications"
    professional_export: "Compatible with existing astrology software formats"
    
  validation_requirements:
    cross_validation: "Compare with Solar Fire, Kepler, and other professional software"
    historical_accuracy: "Validate against known astrocartography interpretations"
    mathematical_precision: "Verify great circle calculations with geodetic standards"
```

### 3. Integration Strategy Research

#### Existing System Integration
```yaml
integration_analysis:
  natal_chart_foundation:
    - "Use existing planetary positions from ChartData"
    - "Leverage existing Swiss Ephemeris integration"
    - "Extend existing calculation caching system"
    - "Maintain performance standards and patterns"
    
  api_enhancement:
    - "Add astrocartography endpoints to existing API structure"
    - "Extend existing response models for astromap data"
    - "Maintain backwards compatibility with current implementations"
    - "Add optional astrocartography data to natal chart responses"
    
  performance_integration:
    - "Use existing monitoring and metrics system"
    - "Integrate with existing cache management"
    - "Follow existing thread-safety patterns"
    - "Maintain overall system performance targets"
```

## Implementation Tasks

### TASK 1: Core Astrocartography Calculator
```yaml
CREATE backend/app/core/ephemeris/astrocartography/calculator.py:
  action: CREATE
  changes: |
    - CREATE AstrocartographyCalculator class
    - ADD planetary line calculation methods (ASC/MC/DC/IC)
    - ADD coordinate transformation utilities (ecliptic → equatorial → geographic)
    - ADD great circle calculation functions
    - INTEGRATE with existing ChartData and planetary positions
    - ADD thread-safe calculation patterns following existing code
  validation:
    command: "cd backend && python -c 'from app.core.ephemeris.astrocartography.calculator import AstrocartographyCalculator; ac = AstrocartographyCalculator(); print(ac.calculate_planetary_lines.__doc__)'"
    expect: "Astrocartography calculator instantiated successfully"
```

### TASK 2: Line Geometry Generator
```yaml
CREATE backend/app/core/ephemeris/astrocartography/geometry.py:
  action: CREATE
  changes: |
    - CREATE LineGeometryGenerator class
    - ADD polyline coordinate generation for mapping applications
    - ADD great circle interpolation methods
    - ADD coordinate precision optimization (sub-kilometer accuracy)
    - ADD memory-efficient streaming coordinate generation
    - ADD WGS84 coordinate system compliance
  validation:
    command: "cd backend && python -m pytest tests/core/ephemeris/astrocartography/test_geometry.py::test_great_circle_generation -v"
    expect: "Line geometry generation tests pass"
```

### TASK 3: Local Space Calculator
```yaml
CREATE backend/app/core/ephemeris/astrocartography/local_space.py:
  action: CREATE
  changes: |
    - CREATE LocalSpaceCalculator class
    - ADD azimuth calculation from birth location to planetary equivalents
    - ADD bearing and distance calculations
    - ADD local space line generation for mapping
    - ADD elevation consideration for above/below horizon planets
    - INTEGRATE with existing coordinate transformation system
  validation:
    command: "cd backend && python -m pytest tests/core/ephemeris/astrocartography/test_local_space.py::test_azimuth_calculation -v"
    expect: "Local space calculations accurate to professional standards"
```

### TASK 4: Paran Calculator Integration  
```yaml
CREATE backend/app/core/ephemeris/astrocartography/parans.py:
  action: CREATE
  changes: |
    - CREATE ParanCalculator class
    - ADD star/planet simultaneous rising/setting calculations
    - INTEGRATE with existing fixed stars system
    - ADD latitude range calculations for paran visibility
    - ADD angular separation validation for true parans
    - ADD performance optimization for multiple paran calculations
  validation:
    command: "cd backend && python -m pytest tests/core/ephemeris/astrocartography/test_parans.py::test_star_planet_parans -v"
    expect: "Paran calculations match traditional astrology standards"
```

### TASK 5: Performance Optimization System
```yaml
MODIFY backend/app/core/ephemeris/astrocartography/calculator.py:
  action: MODIFY
  changes: |
    - ADD vectorized calculations using numpy for line generation
    - ADD location-based caching system for common astromap requests
    - ADD parallel processing for multiple planetary lines
    - ADD streaming coordinate generation to minimize memory usage
    - ADD performance benchmarking and monitoring integration
    - TARGET <200ms for complete astromap generation
  validation:
    command: "cd backend && python scripts/benchmark_astrocartography.py --complete-astromap --target-200ms"
    expect: "Astrocartography performance meets professional standards"
```

### TASK 6: API Integration Enhancement
```yaml
MODIFY backend/app/api/models/schemas.py:
  action: MODIFY
  changes: |
    - ADD AstrocartographyRequest model for astromap generation
    - ADD AstrocartographyResult model with planetary lines data
    - ADD LocalSpaceRequest/Result models for azimuth calculations
    - ADD ParanRequest/Result models for star/planet contacts
    - ADD GeoCoordinate models for mapping integration
    - MAINTAIN backwards compatibility with existing models
  validation:
    command: "cd backend && python -c 'from app.api.models.schemas import AstrocartographyResult; print(AstrocartographyResult.schema())'"
    expect: "Comprehensive astrocartography schema validation"
```

### TASK 7: API Endpoints Implementation
```yaml
CREATE backend/app/api/routes/astrocartography.py:
  action: CREATE
  changes: |
    - CREATE astrocartography router with professional endpoints
    - ADD /astrocartography/lines endpoint for planetary lines
    - ADD /astrocartography/local-space endpoint for azimuth calculations
    - ADD /astrocartography/parans endpoint for star/planet contacts
    - ADD /astrocartography/complete endpoint for full astromap data
    - FOLLOW existing API patterns and error handling
    - ADD comprehensive input validation and error responses
  validation:
    command: "cd backend && python -m pytest tests/api/routes/test_astrocartography.py::test_planetary_lines_endpoint -v"
    expect: "Astrocartography API endpoints functional and validated"
```

### TASK 8: Natal Chart Integration
```yaml
MODIFY backend/app/core/ephemeris/charts/natal.py:
  action: MODIFY
  changes: |
    - ADD optional astrocartography data to natal chart response
    - INTEGRATE astrocartography calculation with existing chart calculation
    - ADD astrocartography parameter to chart calculation options
    - MAINTAIN existing performance standards with optional enhancement
    - ADD astrocartography data to ChartData model
    - PRESERVE backwards compatibility with existing natal chart API
  validation:
    command: "cd backend && python -m pytest tests/core/ephemeris/test_natal.py::test_astrocartography_integration -v"
    expect: "Natal chart astrocartography integration seamless"
```

### TASK 9: Comprehensive Testing Suite
```yaml
CREATE backend/tests/core/ephemeris/astrocartography/:
  action: CREATE
  changes: |
    - CREATE test_calculator.py for core astrocartography calculations
    - CREATE test_geometry.py for line geometry and coordinate generation
    - CREATE test_local_space.py for azimuth and bearing calculations
    - CREATE test_parans.py for star/planet contact calculations
    - CREATE test_performance.py for optimization and benchmarking
    - CREATE test_integration.py for system integration validation
    - ADD professional software cross-validation tests
    - FOLLOW existing test patterns from ephemeris test suites
  validation:
    command: "cd backend && python -m pytest tests/core/ephemeris/astrocartography/ -v --cov=app.core.ephemeris.astrocartography"
    expect: ">90% test coverage for astrocartography system"
```

### TASK 10: Professional Validation System  
```yaml
CREATE backend/scripts/astrocartography_validation.py:
  action: CREATE
  changes: |
    - CREATE professional validation script for astrocartography accuracy
    - ADD cross-validation with Solar Fire, Kepler, and other professional software
    - ADD mathematical validation of great circle calculations
    - ADD historical chart validation with known astrocartography interpretations
    - ADD performance benchmarking against professional standards
    - ADD coordinate precision validation (sub-kilometer accuracy)
    - ADD comprehensive accuracy reporting
  validation:
    command: "cd backend && python scripts/astrocartography_validation.py --comprehensive --professional-cross-validation"
    expect: "95%+ accuracy against professional astrocartography software"
```

## Final Validation Checklist

### Functional Validation
```bash
# Complete astrocartography system testing
cd backend && python -m pytest tests/core/ephemeris/astrocartography/ -v

# Professional accuracy cross-validation
cd backend && python scripts/astrocartography_validation.py --cross-validation

# Performance validation for mapping applications  
cd backend && python scripts/benchmark_astrocartography.py --mapping-performance --target-200ms
```

### Integration Validation
```bash
# API integration testing
cd backend && python -m pytest tests/api/routes/test_astrocartography.py -v

# Natal chart integration validation
cd backend && python -m pytest tests/core/ephemeris/test_natal.py::test_astrocartography_integration -v

# System performance with astrocartography enabled
cd backend && python scripts/system_performance_test.py --include-astrocartography
```

### Professional Validation
```bash
# Mathematical precision validation
cd backend && python scripts/validate_great_circle_math.py --geodetic-standards

# Professional software compatibility testing
cd backend && python scripts/professional_compatibility_test.py --astrocartography

# Historical accuracy validation
cd backend && python scripts/validate_historical_astromaps.py --famous-relocations
```

## Success Metrics
- [ ] Complete planetary line calculations for all planets and angles
- [ ] <200ms performance for complete astromap generation
- [ ] Sub-kilometer coordinate accuracy for professional applications
- [ ] 95%+ accuracy against professional astrocartography software
- [ ] <10MB memory usage for complete astromap data
- [ ] Integration with existing system without breaking changes
- [ ] Professional-grade local space and paran calculations

## Professional Applications

### Relocation Astrology
- **Planetary Lines**: Complete ASC/MC/DC/IC lines for all planets
- **Local Space**: Azimuth calculations for directional analysis
- **Parans**: Star/planet contacts for specific latitude ranges
- **Interactive Mapping**: Real-time coordinate generation for web applications

### Technical Applications
- **GIS Integration**: WGS84 compatible coordinate output
- **Mapping APIs**: Polyline coordinates for Google Maps, Leaflet, etc.
- **Professional Software**: Compatible data formats for astrology applications
- **Academic Research**: Precise mathematical foundations for scholarly work

## Research Citations & References

### Astrocartography Sources
- **Jim Lewis**: Astrocartography: The Book of Maps (foundational methodology)
- **Martin Davis**: Astrolocality Astrology (modern applications)
- **Astro.com**: Professional astrocartography implementation reference
- **Swiss Ephemeris**: Coordinate transformation documentation

### Mathematical References
- **Great Circle Mathematics**: Wikipedia and geodetic calculation standards
- **Coordinate Systems**: Swiss Ephemeris programming guide
- **GIS Standards**: WGS84 coordinate system specifications
- **Performance Optimization**: NumPy vectorization and Python optimization guides

### Professional Validation
- **Solar Fire**: Professional astrology software for cross-validation
- **Kepler**: Traditional astrology software compatibility testing
- **Academic Papers**: Peer-reviewed research on astrocartography accuracy
- **Historical Charts**: Known relocations and astrocartography interpretations

This BASE PRP provides comprehensive guidance for implementing a complete, professional-grade astrocartography system that integrates seamlessly with the existing Meridian Ephemeris while adding powerful relocation astrology capabilities.