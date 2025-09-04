# PRP 4: API & Service Layer

## Goal
Expose the ephemeris engine via FastAPI endpoints, with standardized Pydantic schemas and robust input validation.

## Deliverables
- backend/app/services/ephemeris_service.py
- backend/app/api/routes/ephemeris.py
- Pydantic models for API inputs/outputs
- Integration tests for API endpoints

## Success Criteria
- POST /ephemeris/natal returns correct, standardized JSON
- All input types (ISO, DMS, decimals, TZ, offset) are supported
- API schema is stable and documented
- Integration tests pass and match reference outputs

## Validation Steps
- Run API integration tests
- Validate API responses against fixtures

---

# [END OF API & SERVICE PRP]
