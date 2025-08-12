# Meridian Ephemeris Engine – Master Project Context

This file is the single source of truth for project-wide context, references, philosophy, and high-level goals. All sub-PRPs and contributors must reference this file to maintain alignment and avoid context drift.

---

## Project Vision
A modular, agentic, and test-validated ephemeris engine and API, inspired by Immanuel, delivering high-accuracy, standardized outputs for astrology, analytics, and AI integrations.

## Key References
- Immanuel Python: https://github.com/theriftlab/immanuel-python
- PySwisseph: https://github.com/astrorigin/pyswisseph
- Swiss Ephemeris docs: https://www.astro.com/swisseph/swephinfo_e.htm
- Meridian dev philosophy: [link or doc]
- PRP process: [link or doc]

## Core Principles
- No hacks: Use correct Swiss Ephemeris APIs, no manual angle corrections
- Test-driven: Reference outputs, property-based, and integration tests
- Modular: Each concern in its own module, clear boundaries
- Configurable: Paths, caching, and settings are not hardcoded
- Extensible: Support for planets, asteroids, lunar points, fixed stars, custom points
- Cross-platform: Windows, Linux, Mac; tzdata and path quirks handled

## Project Structure
- Initiation phase: Environment, tools, and documentation
- Core engine: settings, const, cache, serialize, tools, charts
- API & service: FastAPI endpoints, schemas
- Testing: Fixtures, utilities, validation
- CI/CD: Lint, typecheck, test, deploy

## Always Reference
- This file for project-wide context
- The current sub-PRP for your phase/task
- The dev philosophy and PRP process

---

# [END OF MASTER CONTEXT]
