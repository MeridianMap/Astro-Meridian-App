"""
Test suite for aspect labeling fixes.

Validates that aspect calculations use proper planet names instead of
generic "Planet N" fallback names for asteroids and other celestial objects.
"""

import pytest
from app.core.ephemeris.tools.aspects import AspectCalculator
from app.core.ephemeris.charts.natal import NatalChart
from app.core.ephemeris.charts.subject import Subject
from app.core.ephemeris.const import get_planet_name, SwePlanets
from app.core.ephemeris.classes.serialize import PlanetPosition
from datetime import datetime


class TestAspectNamingFixes:
    """Test aspect naming consistency fixes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = AspectCalculator()
        
        # Create test subject for chart calculations
        self.test_subject = Subject(
            name="Test Subject",
            datetime=datetime(1990, 6, 15, 14, 30, 0),
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York"
        )

    def test_planet_name_consistency(self):
        """Test that all planet IDs resolve to consistent names."""
        # Test all planet IDs that appear in aspects
        test_planet_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20]
        
        for planet_id in test_planet_ids:
            name = get_planet_name(planet_id)
            
            # Should not be generic fallback format
            assert not name.startswith("Planet "), f"Planet ID {planet_id} resolves to generic '{name}'"
            
            # Should be a proper name (at least 3 characters)
            assert len(name) >= 3, f"Planet ID {planet_id} has suspiciously short name '{name}'"
            
            # Should not be empty or None
            assert name and name.strip(), f"Planet ID {planet_id} resolves to empty name"

    def test_aspect_calculator_planet_naming(self):
        """Test that AspectCalculator uses consistent planet naming."""
        # Create mock planet positions
        positions = [
            PlanetPosition(
                planet_id=SwePlanets.SUN,
                longitude=45.0,  # 15° Leo
                latitude=0.0,
                distance=1.0,
                longitude_speed=0.98
            ),
            PlanetPosition(
                planet_id=16,  # Pholus (asteroid)
                longitude=135.0,  # 15° Leo (90° aspect)
                latitude=0.0,
                distance=20.0,
                longitude_speed=0.02
            ),
            PlanetPosition(
                planet_id=19,  # Juno (asteroid) 
                longitude=225.0,  # 15° Scorpio (180° aspect with Sun)
                latitude=0.0,
                distance=2.5,
                longitude_speed=0.5
            )
        ]
        
        # Calculate aspects
        result = self.calculator.calculate_aspects(positions)
        
        # Check that all aspect object names are proper names
        for aspect in result:
            # Should not contain generic fallback patterns
            assert not aspect.planet1.startswith("Planet "), f"Aspect planet1 '{aspect.planet1}' uses generic naming"
            assert not aspect.planet2.startswith("Planet "), f"Aspect planet2 '{aspect.planet2}' uses generic naming"
            assert not aspect.planet1.startswith("planet_"), f"Aspect planet1 '{aspect.planet1}' uses fallback naming"
            assert not aspect.planet2.startswith("planet_"), f"Aspect planet2 '{aspect.planet2}' uses fallback naming"
            
            # Should be recognizable planet names
            valid_names = [
                "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                "Uranus", "Neptune", "Pluto", "North Node (Mean)", "North Node (True)",
                "Lilith (Mean)", "Lilith (True)", "Chiron", "Pholus", "Ceres", 
                "Pallas", "Juno", "Vesta"
            ]
            
            assert aspect.planet1 in valid_names, f"Unrecognized planet name '{aspect.planet1}'"
            assert aspect.planet2 in valid_names, f"Unrecognized planet name '{aspect.planet2}'"

    def test_natal_chart_aspect_naming(self):
        """Test that NatalChart produces proper aspect naming in output."""
        # Create a natal chart with asteroids included
        chart = NatalChart(
            subject=self.test_subject,
            include_asteroids=True,
            include_nodes=True
        )
        
        # Calculate chart
        chart_data = chart.calculate()
        
        # Check aspects for proper naming
        for aspect in chart_data.aspects:
            # Should use proper object names, not generic fallbacks
            assert not aspect.object1_name.startswith("Planet "), \
                f"Chart aspect object1 '{aspect.object1_name}' uses generic naming"
            assert not aspect.object2_name.startswith("Planet "), \
                f"Chart aspect object2 '{aspect.object2_name}' uses generic naming"
            
            # Names should be consistent with const.py naming
            name1 = get_planet_name(aspect.object1_id)
            name2 = get_planet_name(aspect.object2_id)
            
            assert aspect.object1_name == name1, \
                f"Inconsistent naming: aspect has '{aspect.object1_name}', const.py has '{name1}'"
            assert aspect.object2_name == name2, \
                f"Inconsistent naming: aspect has '{aspect.object2_name}', const.py has '{name2}'"

    def test_aspect_serialization_naming(self):
        """Test that aspect serialization maintains proper names."""
        # Create chart and serialize to dict format (like API output)
        chart = NatalChart(
            subject=self.test_subject,
            include_asteroids=True
        )
        
        chart_data = chart.calculate()
        serialized = chart_data.to_dict()
        
        # Check serialized aspects
        if 'aspects' in serialized:
            for aspect_dict in serialized['aspects']:
                object1 = aspect_dict.get('object1', '')
                object2 = aspect_dict.get('object2', '')
                
                # Should not have generic names in serialized output
                assert not object1.startswith("Planet "), \
                    f"Serialized aspect object1 '{object1}' uses generic naming"
                assert not object2.startswith("Planet "), \
                    f"Serialized aspect object2 '{object2}' uses generic naming"

    def test_asteroid_name_resolution(self):
        """Test that asteroid IDs resolve to proper names."""
        asteroid_ids = {
            16: "Pholus",
            17: "Ceres", 
            18: "Pallas",
            19: "Juno",
            20: "Vesta"
        }
        
        for planet_id, expected_name in asteroid_ids.items():
            actual_name = get_planet_name(planet_id)
            assert actual_name == expected_name, \
                f"Planet ID {planet_id} should resolve to '{expected_name}', got '{actual_name}'"

    def test_aspect_calculator_internal_consistency(self):
        """Test that AspectCalculator's internal planet naming is consistent."""
        # Test both _get_planet_name methods in AspectCalculator
        calculator = AspectCalculator()
        
        # Test common planet IDs
        test_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17, 18, 19, 20]
        
        for planet_id in test_ids:
            # Get name from calculator's internal method
            calc_name = calculator._get_planet_name(planet_id)
            
            # Get name from const.py
            const_name = get_planet_name(planet_id)
            
            # Should be identical
            assert calc_name == const_name, \
                f"Inconsistent naming for ID {planet_id}: calculator='{calc_name}', const='{const_name}'"

    def test_no_generic_planet_names_in_output(self):
        """Integration test ensuring no generic 'Planet N' names appear in final output."""
        from app.services.ephemeris_service import EphemerisService
        from app.api.models.schemas import NatalChartRequest, SubjectRequest, CoordinateInput, DateTimeInput
        
        # Create service and request
        service = EphemerisService()
        
        request = NatalChartRequest(
            subject=SubjectRequest(
                name="Integration Test",
                datetime=DateTimeInput(iso_string="1990-06-15T14:30:00"),
                latitude=CoordinateInput(decimal=40.7128),
                longitude=CoordinateInput(decimal=-74.0060)
            )
        )
        
        # Calculate enhanced chart with all features
        response = service.calculate_natal_chart_enhanced(
            request,
            include_aspects=True,
            include_arabic_parts=True,
            include_dignities=True
        )
        
        # Convert to dict for easier inspection
        response_dict = response if isinstance(response, dict) else response.dict()
        
        # Check aspects for generic names
        if 'aspects' in response_dict:
            for aspect in response_dict['aspects']:
                object1 = aspect.get('object1', '')
                object2 = aspect.get('object2', '')
                
                assert not object1.startswith("Planet "), \
                    f"Found generic name '{object1}' in aspect output"
                assert not object2.startswith("Planet "), \
                    f"Found generic name '{object2}' in aspect output"

    def test_performance_aspect_naming(self):
        """Test that aspect naming fixes don't impact performance."""
        import time
        
        positions = [
            PlanetPosition(i, float(i * 30), 0.0, 1.0, 0.5)
            for i in range(10)  # 10 planets
        ]
        
        start_time = time.time()
        for _ in range(50):  # 50 calculations
            aspects = self.calculator.calculate_aspects(positions)
            # Ensure names are being generated
            for aspect in aspects:
                assert len(aspect.planet1) > 0
                assert len(aspect.planet2) > 0
        end_time = time.time()
        
        avg_time_ms = ((end_time - start_time) / 50) * 1000
        assert avg_time_ms < 50.0, f"Aspect calculation with naming {avg_time_ms:.2f}ms exceeds 50ms target"


@pytest.mark.benchmark(group="aspects")
def test_aspect_calculation_benchmark(benchmark):
    """Benchmark aspect calculation performance with proper naming."""
    calculator = AspectCalculator()
    
    positions = [
        PlanetPosition(i, float(i * 45), 0.0, 1.0, 0.5)
        for i in range(7)
    ]
    
    result = benchmark(calculator.calculate_aspects, positions)
    
    # Verify proper naming in results
    for aspect in result:
        assert not aspect.planet1.startswith("Planet ")
        assert not aspect.planet2.startswith("Planet ")