# ACG Mathematical Formulas - Manual Extraction

**Description**: Working ACG calculation formulas manually extracted from acg_core.py  
**Generated**: 2025-09-09 14:00:00  
**Source**: backend/app/core/acg/acg_core.py  
**Status**: HIGH VALUE - EXTRACT THESE EXACT FORMULAS

## 🏆 CRITICAL MATHEMATICAL FORMULAS TO PRESERVE

### 1. MC/IC Line Calculations

**Location**: `calculate_mc_ic_lines()` method  
**Value Score**: 5/5 ⭐⭐⭐⭐⭐  
**Status**: WORKING - Extract exactly as-is

```python
def calculate_mc_ic_lines(self, body_data: ACGBodyData, gmst_deg: float, metadata_base: Dict[str, Any]) -> List[ACGLineData]:
    """Calculate MC and IC lines for a body - PRESERVE THIS EXACT METHOD"""
    lines = []
    
    try:
        # Calculate MC and IC longitudes - THIS FORMULA WORKS
        lam_mc, lam_ic = mc_ic_longitudes(body_data.coordinates.ra, gmst_deg)
        
        # Build meridian coordinates - PRESERVE THIS APPROACH
        mc_coords = build_ns_meridian(lam_mc)
        ic_coords = build_ns_meridian(lam_ic)
        
        # Create GeoJSON structure - WORKING PATTERN
        mc_line = ACGLineData(
            line_type=ACGLineType.MC,
            geometry={
                "type": "LineString", 
                "coordinates": mc_coords.tolist()
            },
            body_data=body_data,
            metadata=mc_metadata
        )
        
        return lines
    except Exception as e:
        # Error handling pattern to preserve
        pass
```

**Dependencies to Extract**:
- `mc_ic_longitudes()` utility function
- `build_ns_meridian()` coordinate builder
- ACG data models (ACGLineData, ACGLineType, etc.)

### 2. AC/DC Line Calculations  

**Location**: `calculate_ac_dc_lines()` method  
**Value Score**: 5/5 ⭐⭐⭐⭐⭐  
**Status**: WORKING - Extract exactly as-is

```python
def calculate_ac_dc_lines(self, body_data: ACGBodyData, gmst_deg: float, metadata_base: Dict[str, Any]) -> List[ACGLineData]:
    """Calculate AC and DC lines for a body - PRESERVE THIS EXACT METHOD"""
    lines = []
    
    try:
        # Calculate AC line coordinates - THIS FORMULA WORKS
        ac_coords = ac_dc_line(
            body_data.coordinates.ra,
            body_data.coordinates.dec, 
            gmst_deg,
            kind='AC'
        )
        
        if len(ac_coords) > 0:
            # Handle line discontinuities - IMPORTANT PATTERN
            ac_segments = segment_line_at_discontinuities(ac_coords)
            
            if ac_segments:
                # GeoJSON structure for complex lines - PRESERVE THIS
                raw_coordinates = [seg.tolist() for seg in ac_segments] if len(ac_segments) > 1 else ac_segments[0].tolist()
                geometry = {
                    "type": "MultiLineString" if len(ac_segments) > 1 else "LineString",
                    "coordinates": normalize_geojson_coordinates(raw_coordinates)
                }
```

**Dependencies to Extract**:
- `ac_dc_line()` horizon calculation utility
- `segment_line_at_discontinuities()` line processing
- `normalize_geojson_coordinates()` coordinate normalization

### 3. Aspect Line Calculations

**Location**: `calculate_mc_aspect_lines()` and `calculate_ac_aspect_lines()` methods  
**Value Score**: 4/5 ⭐⭐⭐⭐  
**Status**: WORKING - Extract and enhance

```python
def calculate_mc_aspect_lines(self, body_data: ACGBodyData, gmst_deg: float, metadata_base: Dict[str, Any]) -> List[ACGLineData]:
    """Calculate MC aspect lines (trine, square, sextile) - PRESERVE APPROACH"""
    lines = []
    
    aspect_angles = [60, 90, 120]  # sextile, square, trine
    
    for angle in aspect_angles:
        try:
            # Aspect line calculation - WORKING FORMULA
            aspect_coords = self._calculate_aspect_line_coordinates(
                body_data.coordinates.ra,
                body_data.coordinates.dec, 
                gmst_deg,
                angle,
                'MC'
            )
            
            if len(aspect_coords) > 0:
                # Create aspect line data - PRESERVE STRUCTURE
                aspect_line = ACGLineData(
                    line_type=self._get_aspect_line_type(angle, 'MC'),
                    geometry={
                        "type": "LineString",
                        "coordinates": aspect_coords.tolist()
                    },
                    body_data=body_data,
                    metadata=aspect_metadata
                )
                lines.append(aspect_line)
```

**Dependencies to Extract**:
- Aspect angle definitions (60°, 90°, 120°)
- Aspect coordinate calculation utilities
- Aspect-specific line type mapping

### 4. Paran Calculations

**Location**: `calculate_paran_lines()` method  
**Value Score**: 4/5 ⭐⭐⭐⭐  
**Status**: PARTIAL - Extract mathematical foundation, complete implementation

```python 
def calculate_paran_lines(self, body1_data: ACGBodyData, body2_data: ACGBodyData, gmst_deg: float) -> List[ACGLineData]:
    """Calculate paran intersection lines - EXTRACT MATHEMATICAL APPROACH"""
    lines = []
    
    # Paran events to calculate
    events = ['RISE', 'SET', 'CULM', 'ANTI']
    
    for event1 in events:
        for event2 in events:
            if event1 != event2:  # Different events for each body
                try:
                    # Find latitudes where paran occurs - PRESERVE THIS LOGIC
                    paran_lats = find_paran_latitudes(
                        body1_data.coordinates.ra, body1_data.coordinates.dec,
                        body2_data.coordinates.ra, body2_data.coordinates.dec,
                        event1, event2
                    )
                    
                    if len(paran_lats) > 0:
                        # Calculate longitude for each latitude - WORKING APPROACH
                        paran_coords = []
                        for lat in paran_lats:
                            lon = paran_longitude(
                                body1_data.coordinates.ra, body1_data.coordinates.dec,
                                lat, gmst_deg, event1
                            )
                            paran_coords.append([lon, lat])
                        
                        # Create paran line - PRESERVE STRUCTURE  
                        paran_line = ACGLineData(
                            line_type=ACGLineType.PARAN,
                            geometry={
                                "type": "LineString",
                                "coordinates": paran_coords
                            },
                            metadata=paran_metadata
                        )
```

**Dependencies to Extract**:
- `find_paran_latitudes()` utility function
- `paran_longitude()` calculation utility  
- Paran event definitions (RISE, SET, CULM, ANTI)

### 5. Body Position Calculation

**Location**: `calculate_body_position()` method  
**Value Score**: 5/5 ⭐⭐⭐⭐⭐  
**Status**: WORKING - Critical Swiss Ephemeris integration

```python
def calculate_body_position(self, body: ACGBody, julian_day: float) -> ACGBodyData:
    """Calculate celestial body position - PRESERVE THIS SWISS EPHEMERIS INTEGRATION"""
    try:
        # Swiss Ephemeris calculation - EXACT PATTERN TO PRESERVE
        if body.body_type == ACGBodyType.PLANET:
            # Direct planet calculation
            result = swe.calc_ut(julian_day, body.swiss_ephemeris_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
            longitude = result[0][0]
            latitude = result[0][1] 
            distance = result[0][2]
            
        elif body.body_type == ACGBodyType.ASTEROID:
            # Asteroid calculation pattern
            result = swe.calc_ut(julian_day, body.swiss_ephemeris_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
            longitude = result[0][0]
            latitude = result[0][1]
            distance = result[0][2]
            
        elif body.body_type == ACGBodyType.FIXED_STAR:
            # Fixed star calculation - PRESERVE THIS PATTERN
            result = swe.fixstar(body.star_name, julian_day)
            longitude = result[0][0] 
            latitude = result[0][1]
            distance = result[0][2]
        
        # Convert to equatorial coordinates - WORKING TRANSFORMATION
        ra, dec = ecl_to_eq(longitude, latitude, julian_day)
        
        # Create body data structure - PRESERVE THIS MODEL
        coordinates = ACGCoordinates(
            longitude=longitude,
            latitude=latitude, 
            ra=ra,
            dec=dec,
            distance=distance
        )
        
        return ACGBodyData(
            body=body,
            coordinates=coordinates,
            julian_day=julian_day
        )
        
    except Exception as e:
        # Error handling to preserve
        self.logger.error(f"Failed to calculate position for {body.name}: {e}")
        return None
```

**Dependencies to Extract**:
- Swiss Ephemeris integration patterns (swe.calc_ut, swe.fixstar)
- `ecl_to_eq()` coordinate transformation utility
- ACGBodyData, ACGCoordinates data models
- Proper error handling patterns

## 🔧 SUPPORTING UTILITIES TO EXTRACT

### Key Utility Functions (from acg_utils.py)

1. **`mc_ic_longitudes(ra, gmst_deg)`** - MC/IC longitude calculation
2. **`build_ns_meridian(longitude)`** - North-South meridian builder  
3. **`ac_dc_line(ra, dec, gmst_deg, kind)`** - Horizon line calculation
4. **`segment_line_at_discontinuities(coords)`** - Line discontinuity handling
5. **`normalize_geojson_coordinates(coords)`** - GeoJSON coordinate normalization
6. **`ecl_to_eq(longitude, latitude, jd)`** - Ecliptic to equatorial conversion
7. **`find_paran_latitudes(...)`** - Paran latitude finding
8. **`paran_longitude(...)`** - Paran longitude calculation

### Caching Patterns (from acg_cache.py)

1. **`get_acg_cache_manager()`** - Cache manager initialization
2. **`generate_cache_key(...)`** - Cache key generation  
3. **`get_cached_result(...)`** - Cache retrieval pattern

## 📋 EXTRACTION PRIORITY

### Phase 1: Core Mathematical Functions (Week 1, Days 1-2)
1. Extract `mc_ic_longitudes()` and `build_ns_meridian()` 
2. Extract `ac_dc_line()` and discontinuity handling
3. Extract `ecl_to_eq()` coordinate transformation
4. Extract body position calculation patterns

### Phase 2: Line Generation Logic (Week 1, Days 3-5)  
1. Extract complete `calculate_mc_ic_lines()` method
2. Extract complete `calculate_ac_dc_lines()` method
3. Extract aspect line calculation approach
4. Extract paran mathematical foundation

### Phase 3: Data Models and Caching (Week 2, Days 1-2)
1. Extract ACGBodyData, ACGCoordinates, ACGLineData models
2. Extract caching patterns and cache key generation
3. Extract error handling and logging patterns

## ⚠️ CRITICAL NOTES

1. **Preserve Swiss Ephemeris integration patterns exactly** - These are proven to work
2. **Keep coordinate transformation utilities** - Mathematical formulas are correct
3. **Maintain GeoJSON structure patterns** - Client compatibility depends on this
4. **Preserve line discontinuity handling** - Essential for proper ACG display
5. **Keep caching patterns** - Performance optimization that works

---

*These are the proven mathematical formulas and integration patterns that must be preserved in the lean rebuild. Everything else can be simplified or rebuilt.*

