# PRP 2: Input/Output Utilities

## Goal
Implement robust utilities for coordinate parsing, date/time handling, and position analysis, ensuring parity with Immanuel and full test coverage.

## Deliverables
- backend/app/core/ephemeris/tools/convert.py
- backend/app/core/ephemeris/tools/date.py
- backend/app/core/ephemeris/tools/position.py
- Unit tests for all utilities

## Success Criteria
- DMS/decimal parsing and formatting matches Immanuel
- Timezone and JD calculations are DST-safe and cross-platform
- Position helpers (sign, decan, element, modality) are correct
- All edge cases (ambiguous times, high latitudes, leap years) are covered

## Validation Steps
- Run `pytest` on utility modules
- Validate conversions and JD calculations against reference data

---

# [END OF UTILITIES PRP]
