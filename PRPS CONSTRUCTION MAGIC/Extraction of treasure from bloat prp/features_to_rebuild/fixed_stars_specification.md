# Fixed Stars - Implementation Specification

## Overview  
Complete implementation required - no fixed star support found in current codebase.

## Target Features (from cheatsheet)
- **Foundation 24 Stars** (100-mile orb radius)
- **Extended 77 Stars** (80-mile orb radius) 
- **Swiss Ephemeris swe.fixstar()** integration
- **Magnitude-based orb sizing**
- **ACG orb display** (no lines, only location circles)

## Implementation Plan

### Foundation 24 Stars
Key royal stars and prominent fixed stars:
- Regulus (α Leo) - The Royal Star
- Aldebaran (α Tau) - The Watcher of the East  
- Antares (α Sco) - The Watcher of the West
- Fomalhaut (α PsA) - The Watcher of the South
[... complete list from cheatsheet]

### Technical Architecture
```python
class FixedStarCalculator:
    FOUNDATION_24 = [
        {"name": "Regulus", "se_name": "Regulus", "magnitude": 1.4},
        {"name": "Aldebaran", "se_name": "Aldebaran", "magnitude": 0.9},
        # ... all 24 stars
    ]
    
    def calculate_star_positions(self, jd: float, star_set: str = "foundation") -> List[FixedStar]:
        # Swiss Ephemeris swe.fixstar() integration
        
    def calculate_star_orbs_for_acg(self, star_positions: List[FixedStar]) -> List[ACGOrb]:
        # Generate geographic orbs for ACG display
```

### Integration Points
- **Natal Chart**: Include fixed stars with proper names
- **ACG Engine**: Generate orb circles only (no AC/DC/MC/IC lines)
- **Magnitude System**: Orb size based on apparent magnitude
- **Geographic Calculation**: Proper lat/lon orb positioning

---
*Completely new implementation required*
