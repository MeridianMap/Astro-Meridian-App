# PRP 7: ACG Integration with Natal Chart Data

## Reference: ACG_FEATURE_MASTER_CONTEXT.md

---

### Objective
Design and implement robust integration between the ACG engine and natal chart data. Ensure all relevant natal chart attributes are accessible and correctly incorporated into ACG calculations and metadata.

### Requirements
- **Data Integration:**
  - Accept and validate full natal chart data (positions, dignity, house, retrograde, sign, element, modality, aspects, etc.) as input to ACG calculations.
  - Ensure all relevant natal data is attached to ACG feature metadata as per schema.
  - Support both direct input and integration with existing chart modules/services.
- **API & Models:**
  - Define input models for natal chart data (Pydantic or equivalent).
  - Validate completeness and correctness of natal data before processing.
  - Expose endpoints for submitting, retrieving, and validating natal chart data.
- **Testing & Validation:**
  - Unit and integration tests for natal data handling and integration.
  - Cross-validation with reference projects for natal data mapping.
- **Documentation:**
  - Document natal chart data requirements, formats, and integration points.
  - Provide example input/output files and usage scenarios.

### Deliverables
- Natal chart data models and validation logic.
- API endpoints for natal data integration.
- Unit and integration tests in `backend/app/tests/core/acg/`.
- Example input/output files for natal data integration.
- Documentation of natal data requirements and integration.

### Acceptance Criteria
- All relevant natal chart data is correctly integrated and validated.
- Metadata schema is fully populated with natal attributes.
- Endpoints and models are documented and tested.
- Code is modular, robust, and ready for production.

### Validation Checklist
- Input validation enforces geographic and datetime bounds
- Natal schema fields map correctly to ACG metadata.natal
- Contract parity with `PRPs/contracts/acg-api-contract.md` where natal is included
- Cross-validation with reference implementations passes
- Negative tests for missing/invalid natal data behave as expected

---
**All implementation must reference and comply with `ACG_FEATURE_MASTER_CONTEXT.md`.**
