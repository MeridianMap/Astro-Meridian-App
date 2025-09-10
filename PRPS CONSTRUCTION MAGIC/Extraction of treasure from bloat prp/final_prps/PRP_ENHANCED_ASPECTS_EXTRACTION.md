# EXTRACTION PRP: Enhanced Aspects System

## Feature Goal
Extract enhanced aspects engine with variable orb systems and pattern recognition.

## Deliverable
- AspectCalculator implementation
- OrbSystemManager / orb presets
- Aspect matrix + pattern detection logic
- Support for 15+ aspects (major, minor, creative)

## Success Definition
- Major aspects (0, 60, 90, 120, 180) detected between sample planetary set
- Orb system preset 'traditional' loads with expected orbs
- At least one minor aspect (quincunx 150) detected

## Context
```yaml
docs:
  - url: https://www.astro.com/astrology/in_aspect_e.htm
    focus: aspect definitions
  - url: https://cafeastrology.com/articles/aspects.html
    focus: orb conventions
patterns:
  - file: backend/app/core/ephemeris/tools/aspects.py
    preserve: aspect detection loop & orb logic
  - file: backend/app/core/ephemeris/tools/orb_systems.py
    preserve: preset definitions and retrieval
  - file: backend/app/core/ephemeris/tools/arabic_parts.py
    copy: example batch calculation pattern for efficiency
gotchas:
  - issue: double counting aspects
    fix: enforce ordered pairs (i<j)
  - issue: wide orbs inflating count
    fix: use preset defaults unless overridden
  - issue: performance O(n^2)
    fix: small planet set acceptable (<20 bodies)
```

## Tasks
```yaml
copy_aspects:
  action: COPY
  from:
    - backend/app/core/ephemeris/tools/aspects.py
    - backend/app/core/ephemeris/tools/orb_systems.py
  to: extracted/systems/aspects/
  validate:
    - python - <<'PY'\nfrom extracted.systems.aspects.aspects import AspectCalculator; AspectCalculator(); print('INIT OK')\nPY

create_tests:
  action: CREATE
  file: tests/extraction/test_aspects.py
  contents: synthetic planet set verifying major + minor aspects

run_tests:
  action: VALIDATE
  command: pytest -q tests/extraction/test_aspects.py
```

## Validation Checklist
- [ ] Imports succeed
- [ ] Traditional orb preset loads
- [ ] Major aspects detected
- [ ] Minor aspect detected
- [ ] No duplicates

## Rollback
Remove extracted/systems/aspects and revert commit.

## Confidence
8.5/10
