# PRP 6: ACG Batch & Animation Support

## Reference: ACG_FEATURE_MASTER_CONTEXT.md

---

### Objective
Design and implement batch processing and animation support for the ACG engine. Enable efficient calculation and output of ACG features for multiple charts and time-based animations, with full metadata and performance optimization.

### Requirements
- **Batch Processing:**
  - Support batch calculation of ACG lines for multiple charts in a single request.
  - Optimize for speed and memory usage (vectorization, parallelization, caching).
  - Ensure all batch outputs include full metadata and provenance.
- **Animation Support:**
  - Enable calculation of ACG features over time (e.g., progressions, transits, time-lapse animations).
  - Provide API endpoints for requesting animation frames or sequences.
  - Output GeoJSON FeatureCollections for each frame, with consistent metadata.
- **API Integration:**
  - `/acg/batch` and `/acg/animate` endpoints for batch and animation requests.
  - Input models for batch/animation parameters (time range, step, etc.).
- **Testing & Validation:**
  - Unit and integration tests for batch and animation logic.
  - Reference outputs for batch and animation scenarios.
- **Documentation:**
  - Document batch and animation features, input/output formats, and usage examples.

### Deliverables
- Batch and animation logic in `acg_core.py` or dedicated modules.
- API endpoints and models for batch/animation.
- Unit and integration tests in `backend/app/tests/core/acg/`.
- Example input/output files for batch and animation.
- Documentation of batch and animation features.

### Acceptance Criteria
- Batch and animation features are fully implemented and documented.
- Outputs include full metadata and match GeoJSON conventions.
- Performance is optimized for large batch and animation requests.
- All code is modular, well-tested, and ready for production.

### Validation Checklist
- Batch workloads meet latency targets (p50/p95 from master context)
- Animation frames maintain temporal consistency and correct ordering
- Contract parity with `PRPs/contracts/acg-api-contract.md` for `/batch` and `/animate`
- Memory usage within defined bounds during large sequences
- Integration tests simulate mixed single/batch/animation flows

---
**All implementation must reference and comply with `ACG_FEATURE_MASTER_CONTEXT.md`.**
