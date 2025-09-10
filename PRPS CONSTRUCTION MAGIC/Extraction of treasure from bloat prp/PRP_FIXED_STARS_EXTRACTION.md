# (MOVED to final_prps/) EXTRACTION PRP: Fixed Stars Professional System

## Feature Goal
**Extract complete professional Fixed Stars implementation from ephemeris-core-fixes branch**

## Deliverable
- Fully functional FixedStarCalculator class (564 lines)
- Swiss Ephemeris integration patterns preserved
- Foundation 24 + Extended 77 star registry operational
- Magnitude filtering system working
- Test coverage >90%

## Success Definition
- Fixed Stars API endpoint returns accurate positions for all Foundation 24 stars
- Swiss Ephemeris integration works without path errors
- Response time <10ms for single star calculation
- Batch calculation <50ms for all Foundation 24 stars

---

## Context

```yaml
context:
  docs:
    - url: "https://pyswisseph.readthedocs.io/en/latest/api.html#swe.fixstar"
      focus: "Fixed star calculation method and parameters"
    - url: "https://github.com/astrorigin/pyswisseph/blob/master/pyswisseph/__init__.py"
      focus: "Error codes and status handling for swe.fixstar()"
  
  patterns:
    - file: "backend/app/core/ephemeris/tools/fixed_stars.py"
      copy: "Complete FixedStarCalculator class lines 1-564"
      preserve: "Swiss Ephemeris path setup, error handling, caching patterns"
    
    - file: "backend/app/services/ephemeris_service.py" 
      copy: "Swiss Ephemeris integration pattern lines 156-189"
      preserve: "Path validation and fallback logic"
  
  gotchas:
    - issue: "Swiss Ephemeris requires sefstars.txt file in correct path"
      fix: "Use _setup_swiss_ephemeris_path() before any swe.fixstar() calls"
      file: "backend/app/core/ephemeris/tools/fixed_stars.py:45"
    
    - issue: "Star names must match exact Swiss Ephemeris catalog format"
      fix: "Use traditional star names from star_registry, not common names"
      file: "backend/app/core/ephemeris/tools/fixed_stars.py:89"
    
    - issue: "Magnitude filtering performance critical for Foundation 24 vs Extended 77"
      fix: "Pre-filter by magnitude before expensive Swiss Eph calculations"
      file: "backend/app/core/ephemeris/tools/fixed_stars.py:234"

  dependencies:
    - Swiss Ephemeris files: ["sefstars.txt", "seas_18.se1"] 
    - Python packages: ["pyswisseph>=2.8.0", "pydantic>=2.0"]
    - Internal modules: ["app.core.ephemeris.models", "app.core.ephemeris.utils"]
```

---

## Implementation Tasks

### Task 1: COPY Complete Fixed Stars System
```yaml
copy_fixed_stars:
  action: COPY
  source: backend/app/core/ephemeris/tools/fixed_stars.py
  target: extracted/professional_systems/fixed_stars.py
  preserve_lines: 1-564
  validation:
    - command: "python -c 'from extracted.professional_systems.fixed_stars import FixedStarCalculator; calc = FixedStarCalculator()'"
    - expect: "No import errors"
  rollback: "Delete extracted/professional_systems/fixed_stars.py"
```

### Task 2: EXTRACT Swiss Ephemeris Integration Patterns
```yaml
extract_swiss_patterns:
  action: EXTRACT
  source_methods:
    - "backend/app/core/ephemeris/tools/fixed_stars.py:_setup_swiss_ephemeris_path()"
    - "backend/app/core/ephemeris/tools/fixed_stars.py:_test_star_catalog_availability()"
  target: extracted/patterns/swiss_ephemeris_integration.py
  validation:
    - command: "python -m pytest tests/test_swiss_integration.py::test_path_setup"
    - expect: "Swiss Ephemeris path configured correctly"
```

### Task 3: VALIDATE Star Registry Completeness
```yaml
validate_star_registry:
  action: TEST
  target: extracted/professional_systems/fixed_stars.py
  test_methods:
    - test_foundation_24_present()
    - test_extended_77_accessible()
    - test_royal_stars_accuracy()
  validation:
    - command: "python -m pytest tests/test_fixed_stars_extraction.py -v"
    - expect: "24 Foundation stars found, 4 Royal stars (Regulus, Aldebaran, Antares, Fomalhaut) present"
  success_criteria:
    - "len(foundation_stars) >= 24"
    - "all(royal in star_names for royal in ['Regulus', 'Aldebaran', 'Antares', 'Fomalhaut'])"
```

---

## Final Validation Checklist

- [ ] FixedStarCalculator class instantiates without errors
- [ ] Swiss Ephemeris integration functional (swe.fixstar() calls work)
- [ ] Foundation 24 stars all accessible and return valid positions
- [ ] Royal stars (Regulus, Aldebaran, Antares, Fomalhaut) positions accurate
- [ ] Magnitude filtering works (Foundation 24 vs Extended 77)
- [ ] Error handling preserves graceful degradation
- [ ] Performance: Single star <10ms, batch Foundation 24 <50ms
- [ ] No external dependencies on bloated service layer
- [ ] Test coverage >90% on extracted system

---

**Confidence Score**: 9/10 for one-pass implementation success (canonical copy now in final_prps/)
