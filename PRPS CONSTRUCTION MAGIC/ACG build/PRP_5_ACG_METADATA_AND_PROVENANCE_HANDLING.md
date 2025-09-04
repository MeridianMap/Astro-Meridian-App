# PRP 5: ACG Metadata & Provenance Handling

## Reference: ACG_FEATURE_MASTER_CONTEXT.md

---

### Objective
Design and implement robust metadata and provenance handling for all ACG outputs. Ensure every feature includes complete, standards-compliant metadata, and that provenance (calculation source, version, flags, etc.) is always attached and queryable.

### Requirements
- **Metadata Schema:**
  - Implement the full metadata schema as defined in the master context for every ACG feature.
  - Ensure all required fields (id, type, number, epoch, jd, gmst, obliquity, coords, line, natal, flags, se_version, source, calculation_time_ms, color, style, z_index, hit_radius, custom) are present and correctly populated.
  - Use snake_case for all JSON keys.
- **Provenance:**
  - Attach calculation source, Swiss Ephemeris version, flags, and timing to every output.
  - Track and expose provenance for batch and single-chart requests.
  - Provide API endpoint(s) for querying provenance and metadata schema.
- **Validation:**
  - Validate all metadata for completeness and correctness before output.
  - Provide tests for edge cases and missing/invalid metadata.
- **Documentation:**
  - Document the metadata schema, provenance fields, and usage examples.
  - Provide example outputs and reference mappings to Astrolog conventions.
- **Extensibility:**
  - Allow for custom metadata fields via the `custom` dict.

### Deliverables
- Metadata and provenance logic in `acg_types.py` and related modules.
- API endpoint(s) for metadata/provenance queries (if not already present).
- Unit tests for metadata and provenance handling.
- Documentation and example outputs.

### Acceptance Criteria
- All outputs include complete, standards-compliant metadata and provenance.
- Metadata schema is validated and documented.
- Provenance is queryable and correct for all requests.
- Code is modular, well-documented, and ready for production.

### Validation Checklist
- Metadata completeness checks pass for all features
- Provenance fields populated (source, se_version, flags, calculation_time_ms)
- JSON Schema validation for properties succeeds
- Contract parity with `PRPs/contracts/acg-api-contract.md` (properties names/types)
- Unit tests cover invalid/missing metadata scenarios

---
**All implementation must reference and comply with `ACG_FEATURE_MASTER_CONTEXT.md`.**
