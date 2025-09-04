# PRP 2: ACG API Endpoints & Data Models

## Reference: ACG_FEATURE_MASTER_CONTEXT.md

---

### Objective
Design and implement RESTful API endpoints for the ACG engine, exposing all core calculation features and returning data in the required GeoJSON and metadata formats. Define and document all data models for input and output, ensuring strict compliance with the master context.

### Requirements
- **API Structure:**
  - All endpoints under `/acg/` (e.g., `/acg/lines`, `/acg/batch`, `/acg/features`).
  - Use FastAPI (or project-standard framework) for endpoint definitions.
  - All endpoint handlers and models use the `acg_` prefix.
- **Endpoints:**
  - `/acg/lines`: Calculate and return all ACG lines for a given chart.
  - `/acg/batch`: Batch processing for multiple charts.
  - `/acg/features`: Return supported line types, bodies, and metadata schema.
  - Additional endpoints as needed for animation, validation, or metadata queries.
- **Data Models:**
  - Define Pydantic (or equivalent) models for all input and output data, matching the metadata schema in the master context.
  - Use snake_case for all JSON keys.
  - Validate all input for completeness and correctness.
- **Output:**
  - All map data as GeoJSON FeatureCollections, with full metadata attached to each feature.
  - Consistent error handling and status codes.
- **Documentation:**
  - Auto-generate OpenAPI schema and endpoint docs.
  - Provide example requests and responses for all endpoints.
- **Testing:**
  - Unit and integration tests for all endpoints and models.
  - Reference output for cross-validation.

### Deliverables
- `acg_api.py`: All endpoint definitions.
- `acg_models.py`: Input/output data models.
- OpenAPI schema (auto-generated).
- Unit and integration tests in `backend/app/tests/core/acg/`.
- Example request/response files.

### Acceptance Criteria
- All endpoints and models match the master context and metadata schema.
- Endpoints are fully documented and tested.
- Output is valid GeoJSON with full metadata.
- Code is modular, well-documented, and ready for caching and optimization layers.

### Validation Checklist
- OpenAPI schema validates; `/api/v1/acg` endpoints present
- Contract parity with `PRPs/contracts/acg-api-contract.md`
- End-to-end test: `pytest -q backend/app/tests/core/acg/test_api.py`
- Error responses match contract structure and status codes
- DTOs align 1:1 with Pydantic/Zod models (naming, types)

---
**All implementation must reference and comply with `ACG_FEATURE_MASTER_CONTEXT.md`.**
