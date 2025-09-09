# Hermetic Lots (Arabic Parts) - Implementation Specification

## Overview
Complete rebuild required - current implementation is empty stub.

## Target Features (from cheatsheet)
- **16 Hermetic Lots** with proper day/night formulas
- **Day Birth vs Night Birth** awareness
- **Proper astronomical calculation** integration
- **ACG line generation** for all lots

## Implementation Plan

### Core Lots to Implement
1. **Lot of Fortune** - Foundation lot (Asc + Moon - Sun / Asc + Sun - Moon)
2. **Lot of Spirit** - Activating principle (Asc + Sun - Moon / Asc + Moon - Sun)  
3. **Lot of Basis** - Material foundation
4. **Lot of Eros** - Desire and attraction
5. **Lot of Necessity** - Karmic obligations
6. **Lot of Courage** - Mars-related fortitude
7. **Lot of Victory** - Jupiter-related success
8. **Lot of Nemesis** - Saturn-related challenges
[... continue for all 16 lots]

### Technical Architecture
```python
class HermeticLotsCalculator:
    def __init__(self):
        self.lot_definitions = self._load_lot_formulas()
    
    def calculate_all_lots(self, positions: dict, houses: dict, is_day_birth: bool) -> List[HermeticLot]:
        # Implementation plan
        
    def _determine_day_birth(self, sun_pos: float, asc_pos: float) -> bool:
        # Day birth determination logic
```

### Integration Points
- **Natal Chart**: Include lots in main natal response  
- **ACG Engine**: Generate AC/DC/MC/IC lines for all lots
- **Swiss Ephemeris**: Use proper coordinate calculations
- **Caching**: Cache lot calculations by birth data hash

## Dependencies to Extract
- Working Swiss Ephemeris coordinate calculations
- Proper day/night birth determination
- Angle normalization utilities

---
*To be implemented in lean rebuild branch*
