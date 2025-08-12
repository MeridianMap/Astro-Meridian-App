# PRP 1: Core Ephemeris Engine

## Goal
Implement the foundational modules for the ephemeris engine: settings, constants, cache, serialization, and core Swiss Ephemeris access.

## Deliverables
- backend/app/core/ephemeris/settings.py
- backend/app/core/ephemeris/const.py
- backend/app/core/ephemeris/classes/cache.py
- backend/app/core/ephemeris/classes/serialize.py
- backend/app/core/ephemeris/tools/ephemeris.py
- Unit tests for each module

## Success Criteria
- All modules import and function as intended
- Caching is thread-safe and configurable
- Constants match Swiss Ephemeris indices and house systems
- Settings handle ephemeris path and config
- Core ephemeris functions (get_planet, get_houses, get_angles, get_point, get_fixed_star) implemented with no hacks
- Tests pass on Windows with Python ≥ 3.10

## Validation Steps
- Run `pytest` on the new modules
- Confirm settings and cache work as expected
- Validate outputs against Immanuel reference fixtures

---

# [END OF CORE ENGINE PRP]
