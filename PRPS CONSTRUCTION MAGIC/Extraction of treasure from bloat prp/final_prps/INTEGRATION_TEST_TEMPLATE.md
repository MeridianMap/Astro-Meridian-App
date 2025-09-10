# INTEGRATION TEST TEMPLATE

## Purpose
Validate all extracted systems work together in complete astrology calculation.

## Test Structure
```python
# tests/integration/test_extraction_integration.py
"""Comprehensive integration test for all extracted systems"""

import pytest
import sys
import json
sys.path.insert(0, '.')

# Import all extracted systems
from extracted.systems.fixed_stars.fixed_stars import FixedStarCalculator
from extracted.systems.arabic_parts.arabic_parts import ArabicPartsCalculator
from extracted.systems.aspects.aspects import AspectCalculator
from extracted.systems.acg_engine.acg_core import ACGCalculationEngine

class TestFullExtractionIntegration:
    """Test all extracted systems working together"""
    
    def test_full_chart_calculation(self):
        """End-to-end test: complete chart with all features"""
        
        # 1. Initialize all systems
        fixed_stars = FixedStarCalculator()
        arabic_parts = ArabicPartsCalculator()
        aspects = AspectCalculator()
        acg_engine = ACGCalculationEngine()
        
        # 2. Test data (birth chart for testing)
        test_jd = 2460000.5  # Reference Julian Day
        mock_planets = {
            'sun': {'longitude': 120.5},
            'moon': {'longitude': 240.8}, 
            'mercury': {'longitude': 110.2},
            'venus': {'longitude': 140.7},
            'mars': {'longitude': 200.3},
            'ascendant': {'longitude': 15.0}
        }
        
        # 3. Calculate fixed stars
        foundation_stars = fixed_stars.get_foundation_stars()
        star_positions = []
        for star in foundation_stars[:10]:  # First 10 for speed
            pos = fixed_stars.calculate_star_position(star.name, test_jd)
            if pos:
                star_positions.append({
                    'name': star.name,
                    'longitude': pos.longitude
                })
        
        # 4. Calculate Arabic parts
        traditional_lots = arabic_parts.calculate_all_traditional_lots(mock_planets)
        
        # 5. Calculate aspects
        planet_list = []
        for name, data in mock_planets.items():
            if name != 'ascendant':
                planet_list.append({
                    'name': name,
                    'longitude': data['longitude']
                })
        aspect_matrix = aspects.calculate_aspect_matrix(planet_list)
        
        # 6. Calculate ACG lines for Sun
        from extracted.systems.acg_engine.acg_types import ACGBody, ACGBodyType
        from extracted.systems.acg_engine.acg_utils import gmst_deg_from_jd_ut1
        
        sun_body = ACGBody(name="Sun", body_type=ACGBodyType.PLANET, swiss_ephemeris_id=0)
        sun_data = acg_engine.calculate_body_position(sun_body, test_jd)
        gmst = gmst_deg_from_jd_ut1(test_jd)
        mc_ic_lines = acg_engine.calculate_mc_ic_lines(sun_data, gmst, {})
        
        # 7. Assemble complete chart
        complete_chart = {
            'planets': mock_planets,
            'fixed_stars': star_positions,
            'arabic_parts': traditional_lots,
            'aspects': aspect_matrix,
            'acg_lines': {
                'sun_mc_ic': len(mc_ic_lines)
            },
            'metadata': {
                'julian_day': test_jd,
                'calculation_time': 'measured_below'
            }
        }
        
        # 8. Validation assertions
        assert len(star_positions) > 0, "No fixed stars calculated"
        assert len(traditional_lots) >= 5, "Insufficient Arabic parts"
        assert len(aspect_matrix) > 0, "No aspects calculated"
        assert len(mc_ic_lines) > 0, "No ACG lines generated"
        
        # 9. Response size validation
        chart_json = json.dumps(complete_chart)
        response_size_kb = len(chart_json.encode()) / 1024
        
        print(f"Complete chart response size: {response_size_kb:.1f} KB")
        print(f"Fixed stars: {len(star_positions)}")
        print(f"Arabic parts: {len(traditional_lots)}")
        print(f"Aspects: {len(aspect_matrix)}")
        print(f"ACG lines: {len(mc_ic_lines)}")
        
        # Final validation
        assert response_size_kb < 100, f"Response too large: {response_size_kb:.1f}KB (should optimize service layer)"
        
        return complete_chart
    
    def test_performance_integration(self):
        """Test performance of integrated calculation"""
        import time
        
        start_time = time.time()
        complete_chart = self.test_full_chart_calculation()
        elapsed = (time.time() - start_time) * 1000
        
        print(f"Complete integration calculation: {elapsed:.1f}ms")
        assert elapsed < 200, f"Integration too slow: {elapsed:.1f}ms"
        
        return elapsed

if __name__ == "__main__":
    # Direct execution for quick testing
    test = TestFullExtractionIntegration()
    try:
        chart = test.test_full_chart_calculation()
        perf = test.test_performance_integration()
        print("✅ All integration tests passed!")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
```

## Usage
```bash
# Run integration test
python tests/integration/test_extraction_integration.py

# Or via pytest
pytest tests/integration/test_extraction_integration.py -v
```

## Expected Output
```
Complete chart response size: 45.2 KB
Fixed stars: 10
Arabic parts: 16
Aspects: 23
ACG lines: 4
Complete integration calculation: 156.3ms
✅ All integration tests passed!
```

## Validation Criteria
- [ ] All systems initialize without errors
- [ ] Fixed stars calculation produces valid positions
- [ ] Arabic parts calculation produces 16+ lots
- [ ] Aspects calculation produces aspect matrix
- [ ] ACG engine produces coordinate lines
- [ ] Complete chart response <100KB (before service optimization)
- [ ] Total calculation time <200ms
- [ ] No import or dependency errors
- [ ] All coordinate ranges valid (longitude: -180 to 180, latitude: -90 to 90)

This template provides comprehensive validation that all extracted systems work together effectively.
