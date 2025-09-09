# PRP 1: ACG Core Calculations – All Bodies & Features

## Reference: ACG_FEATURE_MASTER_CONTEXT.md

---

### Objective
Design and implement the core astrocartography (ACG) calculation engine as a new module in `backend/app/core/acg/`. This module must support all required line types (MC, IC, AC, DC, aspects, parans, etc.) and all supported celestial bodies (planets, asteroids, hermetic lots, fixed stars, lunar nodes, Black Moon Lilith, etc.), producing output and metadata as specified in the master context.

### Requirements
- **Module Structure:**
  - All code in `backend/app/core/acg/` with `acg_` prefix for files, classes, and functions.
  - Expose a main calculation entrypoint: `acg_calculate_lines()` (or similar).
- **Feature Coverage:**
  - Calculate all ACG line types: MC, IC, AC, DC, all major aspects, parans, and any additional lines per Astrolog conventions.
  - Support all required bodies: Sun, Moon, planets, asteroids, hermetic lots, fixed stars, lunar nodes, Black Moon Lilith, etc.
  - Accept full natal chart data (positions, dignity, house, retrograde, sign, element, modality, aspects, etc.).
- **Mathematical & Algorithmic Foundations:**
  - Use Swiss Ephemeris (or equivalent) for all astronomical calculations.
  - Implement great circle, horizon, and paran line calculations as described in the ACG Engine overview and Astrolog documentation.
  - Ensure all calculations are vectorized and batch-capable (NumPy, Numba, etc.).
- **Metadata & Output:**
  - Attach full metadata to each line/feature as per the schema in the master context.
  - Output GeoJSON FeatureCollections for all map data.
  - Use snake_case for all JSON keys.
- **Performance:**
  - Optimize for both single-chart and batch processing.
  - Prepare for caching layer integration (see PRP 3).
- **Testing:**
  - Provide unit tests for all core calculation functions.
  - Prepare reference output for cross-validation (Astrolog, Immanuel, Flatlib).

### Deliverables
- `acg_core.py` (or similar): All core calculation logic.
- `acg_types.py`: Data models and metadata schema.
- `acg_utils.py`: Shared math/utility functions.
- Unit tests in `backend/app/tests/core/acg/`.
- Example input/output files for validation.

### Acceptance Criteria
- All required line types and bodies are supported.
- Output matches metadata schema and GeoJSON conventions.
- Unit tests cover >90% of code paths.
- Output cross-validates with reference projects.
- Code is modular, well-documented, and ready for API integration.

### Validation Checklist
- pytest unit tests pass: `pytest -q backend/app/tests/core/acg`
- Coverage >90%: `pytest --cov=backend/app/core/acg --cov-report=term-missing`
- Performance: single chart p50 <100ms, p95 <200ms; batch(10) p50 <500ms, p95 <1s
- Cross-validate against Astrolog/Immanuel/Flatlib fixtures
- GeoJSON validates against schema; metadata keys match master context
- Aligns with API contract fields expected by `/api/v1/acg/lines`

---
**All implementation must reference and comply with `ACG_FEATURE_MASTER_CONTEXT.md`.**
