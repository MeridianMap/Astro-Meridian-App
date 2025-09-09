# Parans - Implementation Specification

## Overview
Partial mathematical groundwork exists but needs complete reimplementation.

## Target Features (from cheatsheet)
- **Jim Lewis paran method** 
- **Four angle events**: Rising, Setting, Culminating, Anti-culminating
- **Body-to-body parans**: Where two planets simultaneously occupy different angles
- **Geographic intersection lines**
- **Proper orb calculation** at intersection points

## Mathematical Foundation
Parans occur where:
- Planet A is Rising while Planet B is Setting
- Planet A is Culminating while Planet B is Anti-culminating  
- All permutations of these angular relationships

### Technical Architecture
```python
class ParanCalculator:
    def calculate_paran_lines(self, body1: dict, body2: dict, events: List[str]) -> List[ParanLine]:
        # Root-solving for longitude where angular conditions meet
        
    def find_paran_intersections(self, body1_data: dict, body2_data: dict, latitude: float) -> List[Tuple[float, float]]:
        # Solve for longitude where paran conditions occur
        
    def calculate_paran_orbs(self, paran_intersections: List[Tuple]) -> List[ACGOrb]:
        # Generate orb circles at paran intersection points
```

## Components to Extract
- Any existing paran mathematical foundations from current codebase
- Working coordinate transformation utilities  
- Root-solving numerical methods if implemented

---
*Refactor and complete existing partial implementation*
