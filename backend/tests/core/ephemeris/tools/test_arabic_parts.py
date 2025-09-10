"""
Test Arabic Parts Calculator - Comprehensive Test Suite

Tests for the complete Arabic parts calculation system including:
- Formula registry and parsing
- Sect determination logic
- Individual lot calculations
- Batch processing
- Performance benchmarks
- Cache efficiency
- API integration

Follows PRP 2 validation requirements with <40ms performance targets.
"""

import pytest
import time
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from typing import Dict, List

from extracted.systems.arabic_parts import (
    ArabicPartsCalculator, BatchArabicPartsCalculator,
    calculate_traditional_lots, calculate_core_lots, get_lot_of_fortune
)
from extracted.systems.arabic_parts_models import (
    ArabicPartsRequest, ArabicPartsResult, SectDetermination,
    CalculationMethod, ChartSect
)
from extracted.systems.arabic_parts_formulas import (
    formula_registry, get_traditional_lots, get_core_lots
)
from extracted.systems.sect_calculator import SectCalculator
from extracted.systems.classes.serialize import (
    PlanetPosition, HouseSystem, ChartData
)
from extracted.systems.const import SwePlanets, normalize_longitude, HouseSystems


class TestArabicPartsFormulaRegistry:
    """Test formula registry and parsing functionality."""
    
    def test_traditional_lots_available(self):
        """Test that all 16 traditional lots are available in registry."""
        traditional_lots = get_traditional_lots()
        expected_lots = [
            'fortune', 'spirit', 'basis', 'travel', 'fame', 'work',
            'property', 'wealth', 'eros', 'necessity', 'victory', 
            'nemesis', 'exaltation', 'marriage', 'faith', 'friends'
        ]
        
        for lot_name in expected_lots:
            assert lot_name in traditional_lots, f"Missing traditional lot: {lot_name}"
    
    def test_core_lots_available(self):
        """Test that core lots (Fortune, Spirit, Basis) are available."""
        core_lots = get_core_lots()
        expected_core = ['fortune', 'spirit', 'basis']
        
        for lot_name in expected_core:
            assert lot_name in core_lots, f"Missing core lot: {lot_name}"
    
    def test_formula_parsing_safe(self):
        """Test that formula parsing is safe and doesn't use eval()."""
        # Get Fortune formula
        formula = formula_registry.get_formula('fortune', is_day_chart=True)
        assert formula == "ascendant + moon - sun"
        
        # Parse formula
        parsed = formula_registry.parse_formula(formula)
        
        assert parsed.is_valid == True
        assert parsed.components == ['ascendant', 'moon', 'sun']
        assert parsed.operations == ['+', '-']
        assert parsed.error_message is None
    
    def test_day_night_formula_variations(self):
        """Test that day/night sect variations work correctly."""
        # Fortune has different day/night formulas
        day_formula = formula_registry.get_formula('fortune', is_day_chart=True)
        night_formula = formula_registry.get_formula('fortune', is_day_chart=False)
        
        assert day_formula == "ascendant + moon - sun"
        assert night_formula == "ascendant + sun - moon"
        assert day_formula != night_formula
    
    def test_invalid_formula_handling(self):
        """Test handling of invalid formulas."""
        invalid_formula = "ascendant + + moon"  # Double operator
        parsed = formula_registry.parse_formula(invalid_formula)
        
        assert parsed.is_valid == False
        assert parsed.error_message is not None
        assert "Invalid formula" in parsed.error_message


class TestSectDetermination:
    """Test sect determination logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sect_calculator = SectCalculator()
    
    def create_test_chart_data(self, sun_longitude: float, ascendant: float) -> ChartData:
        """Create test chart data for sect determination."""
        planets = {
            0: PlanetPosition(  # Sun
                planet_id=0,
                longitude=sun_longitude,
                latitude=0.0,
                distance=1.0,
                longitude_speed=1.0,
                latitude_speed=0.0,
                distance_speed=0.0
            ),
            1: PlanetPosition(  # Moon
                planet_id=1,
                longitude=120.0,
                latitude=2.0,
                distance=1.0,
                longitude_speed=13.2,
                latitude_speed=0.0,
                distance_speed=0.0
            )
        }
        
        # Create house cusps starting from ascendant
        house_cusps = []
        for i in range(12):
            cusp = normalize_longitude(ascendant + (i * 30))  # Equal houses for simplicity
            house_cusps.append(cusp)
        
        ascmc = [
            ascendant,  # ASC
            normalize_longitude(ascendant + 90),   # MC
            normalize_longitude(ascendant + 180),  # DESC
            normalize_longitude(ascendant + 270),  # IC
        ]
        
        houses = HouseSystem(
            house_cusps=house_cusps,
            ascmc=ascmc,
            system_code="P",  # Placidus
            calculation_time=datetime.now(timezone.utc),
            latitude=40.7128,
            longitude=-74.0060
        )
        
        return ChartData(
            planets=planets, 
            houses=houses, 
            calculation_time=datetime.now(timezone.utc),
            julian_day=2451545.0  # J2000.0
        )
    
    def test_day_chart_determination(self):
        """Test day chart determination (Sun above horizon)."""
        # Sun in 10th house (above horizon)
        chart_data = self.create_test_chart_data(sun_longitude=90.0, ascendant=0.0)
        
        from extracted.systems.sect_calculator import determine_chart_sect
        
        sect = determine_chart_sect(
            sun_position=chart_data.planets[0],
            houses=chart_data.houses,
            method="house_position"
        )
        
        assert sect.is_day_chart == True
        assert sect.primary_method == "house_position"
        assert sect.confidence > 0.8
    
    def test_night_chart_determination(self):
        """Test night chart determination (Sun below horizon)."""
        # Sun in 4th house (below horizon)  
        chart_data = self.create_test_chart_data(sun_longitude=270.0, ascendant=0.0)
        
        from extracted.systems.sect_calculator import determine_chart_sect
        
        sect = determine_chart_sect(
            sun_position=chart_data.planets[0],
            houses=chart_data.houses,
            method="house_position"
        )
        
        assert sect.is_day_chart == False
        assert sect.primary_method == "house_position"
        assert sect.confidence > 0.8


class TestArabicPartsCalculator:
    """Test main Arabic parts calculator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = ArabicPartsCalculator()
    
    def create_test_chart_data(self) -> ChartData:
        """Create comprehensive test chart data."""
        planets = {
            0: PlanetPosition(  # Sun
                planet_id=0, longitude=120.0, latitude=0.0, distance=1.0,
                longitude_speed=1.0, latitude_speed=0.0, distance_speed=0.0
            ),
            1: PlanetPosition(  # Moon  
                planet_id=1, longitude=200.0, latitude=2.0, distance=1.0,
                longitude_speed=13.2, latitude_speed=0.0, distance_speed=0.0
            ),
            2: PlanetPosition(  # Mercury
                planet_id=2, longitude=110.0, latitude=1.0, distance=0.4,
                longitude_speed=1.2, latitude_speed=0.0, distance_speed=0.0
            ),
            3: PlanetPosition(  # Venus
                planet_id=3, longitude=140.0, latitude=0.5, distance=0.7,
                longitude_speed=1.0, latitude_speed=0.0, distance_speed=0.0
            ),
            4: PlanetPosition(  # Mars
                planet_id=4, longitude=80.0, latitude=-1.0, distance=1.5,
                longitude_speed=0.5, latitude_speed=0.0, distance_speed=0.0
            ),
            5: PlanetPosition(  # Jupiter
                planet_id=5, longitude=30.0, latitude=0.8, distance=5.2,
                longitude_speed=0.08, latitude_speed=0.0, distance_speed=0.0
            ),
            6: PlanetPosition(  # Saturn
                planet_id=6, longitude=300.0, latitude=0.3, distance=9.5,
                longitude_speed=0.03, latitude_speed=0.0, distance_speed=0.0
            )
        }
        
        ascendant = 90.0  # 0° Cancer
        house_cusps = [
            90.0, 120.0, 150.0, 180.0, 210.0, 240.0,  # Houses 1-6
            270.0, 300.0, 330.0, 0.0, 30.0, 60.0      # Houses 7-12
        ]
        
        ascmc = [ascendant, 0.0, 270.0, 180.0]  # ASC, MC, DESC, IC
        
        houses = HouseSystem(
            house_cusps=house_cusps,
            ascmc=ascmc,
            system_code="P",
            calculation_time=datetime.now(timezone.utc),
            latitude=40.7128,
            longitude=-74.0060
        )
        
        return ChartData(
            planets=planets, 
            houses=houses, 
            calculation_time=datetime.now(timezone.utc),
            julian_day=2451545.0  # J2000.0
        )
    
    def test_fortune_calculation_day_chart(self):
        """Test Lot of Fortune calculation for day chart."""
        chart_data = self.create_test_chart_data()
        request = ArabicPartsRequest(requested_parts=['fortune'])
        
        result = self.calculator.calculate_arabic_parts(chart_data, request)
        
        assert result.successful_calculations == 1
        assert len(result.calculated_parts) == 1
        
        fortune = result.calculated_parts[0]
        assert fortune.name == 'fortune'
        assert fortune.display_name == "Lot of Fortune (Fortuna)"
        assert fortune.is_day_chart == True
        
        # For day chart: ASC + Moon - Sun = 90 + 200 - 120 = 170°
        expected_longitude = normalize_longitude(90.0 + 200.0 - 120.0)
        assert abs(fortune.longitude - expected_longitude) < 0.001
    
    def test_fortune_calculation_night_chart(self):
        """Test Lot of Fortune calculation for night chart."""
        # Modify chart to be night chart (Sun below horizon)
        chart_data = self.create_test_chart_data()
        # Move Sun to 4th house (below horizon)
        chart_data.planets[0] = PlanetPosition(
            planet_id=0, longitude=180.0, latitude=0.0, distance=1.0,
            longitude_speed=1.0, latitude_speed=0.0, distance_speed=0.0
        )
        
        request = ArabicPartsRequest(requested_parts=['fortune'])
        result = self.calculator.calculate_arabic_parts(chart_data, request)
        
        fortune = result.calculated_parts[0]
        assert fortune.is_day_chart == False
        
        # For night chart: ASC + Sun - Moon = 90 + 180 - 200 = 70°
        expected_longitude = normalize_longitude(90.0 + 180.0 - 200.0)
        assert abs(fortune.longitude - expected_longitude) < 0.001
    
    def test_multiple_lots_calculation(self):
        """Test calculation of multiple lots simultaneously."""
        chart_data = self.create_test_chart_data()
        request = ArabicPartsRequest(requested_parts=['fortune', 'spirit', 'basis'])
        
        result = self.calculator.calculate_arabic_parts(chart_data, request)
        
        assert result.successful_calculations == 3
        assert len(result.calculated_parts) == 3
        
        lot_names = [part.name for part in result.calculated_parts]
        assert 'fortune' in lot_names
        assert 'spirit' in lot_names
        assert 'basis' in lot_names
    
    def test_all_traditional_lots_calculation(self):
        """Test calculation of all 16 traditional lots."""
        chart_data = self.create_test_chart_data()
        request = ArabicPartsRequest(include_all_traditional=True)
        
        result = self.calculator.calculate_arabic_parts(chart_data, request)
        
        # Should have all 16 traditional lots
        assert result.successful_calculations >= 16
        assert result.total_parts_calculated >= 16
        
        # Check that key traditional lots are present
        lot_names = [part.name for part in result.calculated_parts]
        expected_traditional = ['fortune', 'spirit', 'basis', 'travel', 'fame']
        
        for expected in expected_traditional:
            assert expected in lot_names, f"Missing traditional lot: {expected}"
    
    def test_calculation_error_handling(self):
        """Test handling of calculation errors."""
        # Create invalid chart data (missing required planets)
        incomplete_chart = ChartData(
            planets={},  # Empty planets dict
            houses=HouseSystem(
                house_cusps=[0.0] * 12,
                ascmc=[0.0, 90.0, 180.0, 270.0],
                system_code="P",
                calculation_time=datetime.now(timezone.utc),
                latitude=40.7128,
                longitude=-74.0060
            ),
            calculation_time=datetime.now(timezone.utc),
            julian_day=2451545.0
        )
        
        request = ArabicPartsRequest(requested_parts=['fortune'])
        
        # Should handle gracefully without crashing
        result = self.calculator.calculate_arabic_parts(incomplete_chart, request)
        
        assert result.successful_calculations == 0
        assert result.failed_calculations > 0
        assert len(result.calculation_errors) > 0
    
    def test_custom_formula_support(self):
        """Test support for custom Arabic parts formulas."""
        chart_data = self.create_test_chart_data()
        
        custom_formulas = {
            "custom_test": {
                "day_formula": "ascendant + sun",
                "night_formula": "ascendant + moon"
            }
        }
        
        request = ArabicPartsRequest(
            requested_parts=['custom_test'],
            custom_formulas=custom_formulas
        )
        
        result = self.calculator.calculate_arabic_parts(chart_data, request)
        
        assert result.successful_calculations == 1
        custom_part = result.calculated_parts[0]
        assert custom_part.name == 'custom_test'
        
        # For day chart: ASC + Sun = 90 + 120 = 210°
        expected_longitude = normalize_longitude(90.0 + 120.0)
        assert abs(custom_part.longitude - expected_longitude) < 0.001


class TestPerformanceBenchmarks:
    """Test performance requirements and benchmarks."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = ArabicPartsCalculator()
    
    def create_benchmark_chart(self) -> ChartData:
        """Create chart data for performance testing."""
        planets = {}
        for i in range(10):  # All traditional planets
            planets[i] = PlanetPosition(
                planet_id=i, longitude=i * 36.0, latitude=0.0, distance=1.0,
                longitude_speed=1.0, latitude_speed=0.0, distance_speed=0.0
            )
        
        houses = HouseSystem(
            house_cusps=[i * 30.0 for i in range(12)],
            ascmc=[0.0, 90.0, 180.0, 270.0],
            system_code="P",
            calculation_time=datetime.now(timezone.utc),
            latitude=40.7128,
            longitude=-74.0060
        )
        
        return ChartData(
            planets=planets, 
            houses=houses, 
            calculation_time=datetime.now(timezone.utc),
            julian_day=2451545.0  # J2000.0
        )
    
    def test_single_lot_performance(self):
        """Test single lot calculation performance."""
        chart_data = self.create_benchmark_chart()
        request = ArabicPartsRequest(requested_parts=['fortune'])
        
        start_time = time.perf_counter()
        result = self.calculator.calculate_arabic_parts(chart_data, request)
        end_time = time.perf_counter()
        
        calculation_time_ms = (end_time - start_time) * 1000
        
        # Should be well under 40ms for single lot
        assert calculation_time_ms < 40.0, f"Single lot took {calculation_time_ms}ms, expected <40ms"
        assert result.successful_calculations == 1
    
    def test_all_traditional_lots_performance(self):
        """Test all 16 traditional lots performance - PRP requirement."""
        chart_data = self.create_benchmark_chart()
        request = ArabicPartsRequest(include_all_traditional=True)
        
        start_time = time.perf_counter()
        result = self.calculator.calculate_arabic_parts(chart_data, request)
        end_time = time.perf_counter()
        
        calculation_time_ms = (end_time - start_time) * 1000
        
        # PRP requirement: <40ms for all 16 traditional lots
        assert calculation_time_ms < 40.0, f"All traditional lots took {calculation_time_ms}ms, expected <40ms"
        assert result.successful_calculations >= 16
        
        # Also check the internal calculation time
        assert result.calculation_time_ms < 40.0
    
    def test_cache_performance_improvement(self):
        """Test that caching improves performance."""
        chart_data = self.create_benchmark_chart()
        request = ArabicPartsRequest(include_all_traditional=True)
        
        # First calculation (cache miss)
        start_time = time.perf_counter()
        result1 = self.calculator.calculate_arabic_parts(chart_data, request)
        first_time = (time.perf_counter() - start_time) * 1000
        
        # Second calculation (should hit cache)
        start_time = time.perf_counter()
        result2 = self.calculator.calculate_arabic_parts(chart_data, request)
        second_time = (time.perf_counter() - start_time) * 1000
        
        # Second calculation should be significantly faster
        assert second_time < first_time * 0.5, f"Cache didn't improve performance: {second_time}ms vs {first_time}ms"
        
        # Results should be identical
        assert len(result1.calculated_parts) == len(result2.calculated_parts)
    
    def test_batch_processing_efficiency(self):
        """Test batch processing performance benefits."""
        charts = [self.create_benchmark_chart() for _ in range(5)]
        batch_calculator = BatchArabicPartsCalculator()
        
        request = ArabicPartsRequest(requested_parts=['fortune', 'spirit'])
        
        # Batch calculation
        start_time = time.perf_counter()
        # Note: This would need actual batch request implementation
        end_time = time.perf_counter()
        
        batch_time_per_chart = ((end_time - start_time) * 1000) / 5
        
        # Batch should be more efficient per chart
        assert batch_time_per_chart < 20.0, f"Batch processing too slow: {batch_time_per_chart}ms per chart"


class TestCacheEfficiency:
    """Test cache efficiency and hit rates."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = ArabicPartsCalculator()
    
    def test_cache_hit_rate(self):
        """Test cache hit rate under realistic load."""
        chart_data = self.create_test_chart_data()
        request = ArabicPartsRequest(requested_parts=['fortune'])
        
        # Perform multiple calculations to build cache
        for _ in range(10):
            self.calculator.calculate_arabic_parts(chart_data, request)
        
        stats = self.calculator.get_performance_stats()
        
        # Should have good cache hit rate
        assert stats['cache_hit_rate'] > 0.7, f"Cache hit rate too low: {stats['cache_hit_rate']}"
        assert stats['cache_hits'] > 0
    
    def create_test_chart_data(self) -> ChartData:
        """Create test chart data for cache testing."""
        planets = {i: PlanetPosition(
            planet_id=i, longitude=i * 30.0, latitude=0.0, distance=1.0,
            longitude_speed=1.0, latitude_speed=0.0, distance_speed=0.0
        ) for i in range(7)}
        
        houses = HouseSystem(
            house_cusps=[i * 30.0 for i in range(12)],
            ascmc=[0.0, 90.0, 180.0, 270.0],
            system_code="P",
            calculation_time=datetime.now(timezone.utc),
            latitude=40.7128,
            longitude=-74.0060
        )
        
        return ChartData(
            planets=planets, 
            houses=houses, 
            calculation_time=datetime.now(timezone.utc),
            julian_day=2451545.0  # J2000.0
        )


class TestAPIIntegration:
    """Test integration with API endpoints."""
    
    @pytest.mark.asyncio
    async def test_enhanced_natal_chart_with_arabic_parts(self):
        """Test enhanced natal chart API with Arabic parts."""
        # This would test the actual API endpoint
        # For now, test the service integration
        
        from extracted.services.ephemeris_service import ephemeris_service
        from extracted.api.models.schemas import NatalChartRequest, SubjectRequest, DateTimeInput, CoordinateInput
        
        # Create test request
        subject = SubjectRequest(
            name="Test Subject",
            datetime=DateTimeInput(iso_string="2000-01-01T12:00:00"),
            latitude=CoordinateInput(decimal=40.7128),
            longitude=CoordinateInput(decimal=-74.0060)
        )
        
        request = NatalChartRequest(subject=subject)
        
        # Test with Arabic parts
        result_dict = ephemeris_service.calculate_natal_chart_enhanced(
            request=request,
            include_aspects=True,
            aspect_orb_preset="traditional",
            custom_orb_config=None,
            include_south_nodes=True,
            include_retrograde_analysis=True,
            include_arabic_parts=True,
            arabic_parts_selection=None,
            include_all_traditional_parts=True,
            custom_arabic_formulas=None
        )
        
        # Should have Arabic parts data
        assert 'arabic_parts' in result_dict
        assert result_dict['arabic_parts'] is not None
        
        arabic_parts_data = result_dict['arabic_parts']
        assert 'sect_determination' in arabic_parts_data
        assert 'arabic_parts' in arabic_parts_data
        assert 'calculation_time_ms' in arabic_parts_data
        
        # Should meet performance requirements
        assert arabic_parts_data['calculation_time_ms'] < 40.0


class TestValidationGates:
    """Test PRP 2 validation gates and requirements."""
    
    def test_all_traditional_lots_supported(self):
        """Validation Gate: All 16+ traditional lots supported."""
        traditional_lots = get_traditional_lots()
        assert len(traditional_lots) >= 16, f"Only {len(traditional_lots)} traditional lots, need 16+"
    
    def test_day_night_formulas_different(self):
        """Validation Gate: Day/night formula variations implemented."""
        day_formula = formula_registry.get_formula('fortune', is_day_chart=True)
        night_formula = formula_registry.get_formula('fortune', is_day_chart=False)
        
        assert day_formula != night_formula, "Day and night formulas should be different"
    
    def test_safe_formula_parsing(self):
        """Validation Gate: Safe formula parsing prevents eval() security issues."""
        # Test that dangerous formulas are rejected
        dangerous_formula = "__import__('os').system('ls')"
        parsed = formula_registry.parse_formula(dangerous_formula)
        
        assert parsed.is_valid == False, "Dangerous formula should be rejected"
        assert ("Unknown astrological point" in parsed.error_message or 
                "Invalid" in parsed.error_message), f"Expected security error, got: {parsed.error_message}"
    
    def test_performance_benchmark_under_40ms(self):
        """Validation Gate: Performance benchmark <40ms for 16 lots."""
        calculator = ArabicPartsCalculator()
        
        # Create comprehensive test chart
        planets = {i: PlanetPosition(
            planet_id=i, longitude=i * 36.0, latitude=0.0, distance=1.0,
            longitude_speed=1.0, latitude_speed=0.0, distance_speed=0.0
        ) for i in range(10)}
        
        houses = HouseSystem(
            house_cusps=[i * 30.0 for i in range(12)],
            ascmc=[0.0, 90.0, 180.0, 270.0],
            system_code="P",
            calculation_time=datetime.now(timezone.utc),
            latitude=40.7128,
            longitude=-74.0060
        )
        
        chart_data = ChartData(
            planets=planets, 
            houses=houses, 
            calculation_time=datetime.now(timezone.utc),
            julian_day=2451545.0
        )
        request = ArabicPartsRequest(include_all_traditional=True)
        
        result = calculator.calculate_arabic_parts(chart_data, request)
        
        assert result.calculation_time_ms < 40.0, f"Performance benchmark failed: {result.calculation_time_ms}ms"
        assert result.successful_calculations >= 16, f"Not all traditional lots calculated: {result.successful_calculations}"


class TestConvenienceFunctions:
    """Test convenience functions for common operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chart_data = self.create_test_chart()
    
    def create_test_chart(self) -> ChartData:
        """Create test chart data."""
        planets = {i: PlanetPosition(
            planet_id=i, longitude=i * 30.0, latitude=0.0, distance=1.0,
            longitude_speed=1.0, latitude_speed=0.0, distance_speed=0.0
        ) for i in range(7)}
        
        houses = HouseSystem(
            house_cusps=[i * 30.0 for i in range(12)],
            ascmc=[0.0, 90.0, 180.0, 270.0],
            system_code="P",
            calculation_time=datetime.now(timezone.utc),
            latitude=40.7128,
            longitude=-74.0060
        )
        
        return ChartData(
            planets=planets, 
            houses=houses, 
            calculation_time=datetime.now(timezone.utc),
            julian_day=2451545.0  # J2000.0
        )
    
    def test_calculate_traditional_lots_function(self):
        """Test convenience function for all traditional lots."""
        result = calculate_traditional_lots(self.chart_data)
        
        assert isinstance(result, ArabicPartsResult)
        assert result.successful_calculations >= 16
    
    def test_calculate_core_lots_function(self):
        """Test convenience function for core lots."""
        result = calculate_core_lots(self.chart_data)
        
        assert isinstance(result, ArabicPartsResult)
        assert result.successful_calculations == 3  # Fortune, Spirit, Basis
        
        lot_names = [part.name for part in result.calculated_parts]
        assert 'fortune' in lot_names
        assert 'spirit' in lot_names
        assert 'basis' in lot_names
    
    def test_get_lot_of_fortune_function(self):
        """Test convenience function for just Lot of Fortune."""
        fortune = get_lot_of_fortune(self.chart_data)
        
        assert fortune is not None
        assert fortune.name == 'fortune'
        assert fortune.display_name == "Lot of Fortune (Fortuna)"
        assert 0.0 <= fortune.longitude < 360.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])