# PRP 3: Chart Construction

## Goal
Implement chart domain models and computation logic for Subject, Natal, and (optionally) Transits/Progressions.

## Deliverables
- backend/app/core/ephemeris/charts/subject.py
- backend/app/core/ephemeris/charts/natal.py
- (Optional) backend/app/core/ephemeris/charts/transits.py, progressions.py
- Unit tests for chart logic

## Success Criteria
- Subject input normalization and validation is robust
- Natal chart aggregates all objects, houses, angles, and points
- Output structure matches Immanuel and is extensible
- Tests pass for all chart types and edge cases

## Validation Steps
- Run `pytest` on chart modules
- Validate chart outputs against Immanuel fixtures

---

# [END OF CHARTS PRP]
