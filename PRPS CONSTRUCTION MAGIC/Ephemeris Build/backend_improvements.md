# Meridian Ephemeris Backend Improvements

## Backend Problems to Fix

### 1. Inconsistent Nomenclature
- **Asteroid naming**: Replace generic "Object 17", "Object 18", etc. with proper astronomical names
- **Enhanced aspect references**: Fix inconsistent naming like "Planet 10", "Planet 12", "True Node" to match planet keys

### 2. Missing Retrograde Information
- Add explicit `is_retrograde` boolean flag to planet objects
- Implement `retrograde_analysis` to include station points and retrograde periods
- Calculate shadow phases (pre-retrograde and post-retrograde)

### 3. Data Structure Issues
- Normalize duplicate data between `basic_natal` and `enhanced_natal`
- Standardize aspect structure between basic and enhanced versions
- Fix empty promised fields (`retrograde_analysis: null`, `arabic_parts: null`)

### 4. Technical Performance
- Optimize response size (currently 12-15KB per chart)
- Improve calculation performance for multi-chart operations
- Add client-side options to selectively include calculation components

## Backend Expansion Opportunities

### 1. Core Astronomical Enhancements
- **Declination data**:
  - Add declination values for all celestial objects
  - Flag out-of-bounds planets (beyond 23°27')
  - Calculate parallel/contraparallel aspects

- **Fixed stars**:
  - Add major fixed star positions and properties
  - Calculate star-planet conjunctions
  - Include paran relationships (rising/setting/culminating)

- **Arabic Parts/Lots**:
  - Calculate Part of Fortune, Spirit, Eros, and other significant lots
  - Support day/night formula variations

### 2. Advanced Chart Analysis
- **Dignity & Debility Calculations**:
  - Calculate essential dignities (rulership, exaltation, triplicity, term, face)
  - Generate dignity/debility scores
  - Identify mutual receptions

- **Chart Pattern Detection**:
  - Major aspect patterns (T-squares, Grand Trines, Yods, etc.)
  - Stellium identification (3+ planets in sign/house)
  - Dispositorship chains/trees
  - House rulership mapping

- **Statistical Analysis**:
  - Element/modality distribution metrics
  - Planet strength scoring
  - Aspect density measurements
  - House/hemisphere/quadrant emphasis
  - Chart shape classification

### 3. Predictive Technologies
- **Secondary progressions**
- **Solar arc directions**
- **Annual profections**
- **Time lord systems** (zodiacal releasing)
- **Transit timing** and peak influence calculations

### 4. API Enhancements
- Add option to calculate multiple chart types in one request
- Support batch operations for multiple charts
- Create endpoints for specialized calculations (midpoints, harmonics)
- Implement cross-chart aspect calculations (synastry, composites)
- Add chart comparison metrics and compatibility scores
