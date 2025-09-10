"""
Integration test suite for complete remediation validation.

This test suite validates that all identified issues from the technical review
have been properly addressed in the integrated system:

1. Essential dignities calculation accuracy
2. Aspect labeling consistency 
3. Schema hygiene improvements
4. Performance maintenance
5. API output correctness

Tests the entire system end-to-end to ensure fixes work in production scenarios.
"""

import pytest
import time
import json
from datetime import datetime
from extracted.services.ephemeris_service import EphemerisService
from extracted.api.models.schemas import (
    NatalChartRequest, SubjectRequest, CoordinateInput, DateTimeInput, TimezoneInput
)


class TestRemediationValidation:
    """Complete remediation validation test suite."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EphemerisService()
        
        # Create test request matching the review data
        self.test_request = NatalChartRequest(
            subject=SubjectRequest(
                name="Debug Test",
                datetime=DateTimeInput(iso_string="1990-06-15T14:30:00-04:00"),
                latitude=CoordinateInput(decimal=40.7128),
                longitude=CoordinateInput(decimal=-74.0060),
                timezone=TimezoneInput(name="America/New_York")
            )
        )

    def test_essential_dignities_accuracy_complete(self):
        """Test complete essential dignities accuracy against known good values."""
        response = self.service.calculate_natal_chart_enhanced(
            self.test_request,
            include_dignities=True
        )
        
        response_dict = response if isinstance(response, dict) else response.model_dump()
        planets = response_dict.get('planets', {})
        
        # Test Sun in Gemini - should NOT have exaltation or triplicity
        sun_data = planets.get('Sun', {})
        if sun_data and 'essential_dignities' in sun_data:
            sun_dignities = sun_data['essential_dignities']
            
            # Sun should not have exaltation score (not exalted in Gemini)
            assert sun_dignities.get('exaltation_score', 0) == 0, \
                "Sun should not have exaltation in Gemini"
            
            # Sun should not have triplicity score in Air sign during day
            # (This depends on chart sect, but for this birth time should be day chart)
            assert sun_dignities.get('triplicity_score', 0) == 0, \
                "Sun should not have triplicity in Gemini (Air sign)"

        # Test Venus in Taurus - should have domicile, NOT detriment
        venus_data = planets.get('Venus', {})
        if venus_data and 'essential_dignities' in venus_data:
            venus_dignities = venus_data['essential_dignities']
            
            # Venus should have domicile (rules Taurus)
            assert venus_dignities.get('rulership_score', 0) == 5, \
                "Venus should have domicile (+5) in Taurus"
            
            # Should not have detriment
            assert venus_dignities.get('rulership_score', 0) > 0, \
                "Venus should not be in detriment in Taurus"
            
            # Total score should be positive and significant
            assert venus_dignities.get('total_score', 0) > 5, \
                "Venus should have high dignity score in Taurus"

        # Test Saturn in Capricorn - should have domicile, NOT fall
        saturn_data = planets.get('Saturn', {})
        if saturn_data and 'essential_dignities' in saturn_data:
            saturn_dignities = saturn_data['essential_dignities']
            
            # Saturn should have domicile (rules Capricorn)
            assert saturn_dignities.get('rulership_score', 0) == 5, \
                "Saturn should have domicile (+5) in Capricorn"
            
            # Should not have fall
            assert saturn_dignities.get('exaltation_score', 0) >= 0, \
                "Saturn should not be in fall in Capricorn"

        # Test Jupiter in Cancer - should have exaltation
        jupiter_data = planets.get('Jupiter', {})
        if jupiter_data and 'essential_dignities' in jupiter_data:
            jupiter_dignities = jupiter_data['essential_dignities']
            
            # Jupiter should have exaltation (exalted in Cancer)
            assert jupiter_dignities.get('exaltation_score', 0) == 4, \
                "Jupiter should have exaltation (+4) in Cancer"

    def test_aspect_labeling_consistency_complete(self):
        """Test complete aspect labeling consistency."""
        response = self.service.calculate_natal_chart_enhanced(
            self.test_request,
            include_aspects=True
        )
        
        response_dict = response if isinstance(response, dict) else response.model_dump()
        aspects = response_dict.get('aspects', [])
        
        # Check all aspects for proper naming
        for aspect in aspects:
            object1 = aspect.get('object1', '')
            object2 = aspect.get('object2', '')
            
            # Should not contain generic Planet N names
            assert not object1.startswith("Planet "), \
                f"Found generic name '{object1}' in aspect"
            assert not object2.startswith("Planet "), \
                f"Found generic name '{object2}' in aspect"
            
            # Names should be recognizable
            valid_names = {
                "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                "Uranus", "Neptune", "Pluto", "Chiron", "Pholus", "Ceres", 
                "Pallas", "Juno", "Vesta", "North Node (Mean)", "North Node (True)",
                "Lilith (Mean)", "Lilith (True)"
            }
            
            assert object1 in valid_names, f"Unrecognized object name '{object1}'"
            assert object2 in valid_names, f"Unrecognized object name '{object2}'"

    def test_schema_hygiene_improvements(self):
        """Test schema hygiene improvements."""
        response = self.service.calculate_natal_chart_enhanced(self.test_request)
        
        response_dict = response if isinstance(response, dict) else response.model_dump()
        
        # Test boolean types are proper booleans
        planets = response_dict.get('planets', {})
        for planet_name, planet_data in planets.items():
            is_retrograde = planet_data.get('is_retrograde')
            if is_retrograde is not None:
                assert isinstance(is_retrograde, bool), \
                    f"is_retrograde for {planet_name} should be boolean, got {type(is_retrograde)}"
        
        aspects = response_dict.get('aspects', [])
        for aspect in aspects:
            applying = aspect.get('applying')
            if applying is not None:
                assert isinstance(applying, bool), \
                    f"applying should be boolean, got {type(applying)}"
        
        # Test timezone offset handling
        subject = response_dict.get('subject', {})
        utc_offset = subject.get('utc_offset')
        timezone_name = subject.get('timezone_name')
        
        # If timezone name is provided, UTC offset should be calculated
        if timezone_name:
            assert utc_offset is not None, \
                "UTC offset should be calculated when timezone name is provided"
            assert isinstance(utc_offset, (int, float)), \
                f"UTC offset should be numeric, got {type(utc_offset)}"

    def test_performance_maintenance(self):
        """Test that fixes maintain performance standards."""
        # Test API response time <100ms
        start_time = time.time()
        response = self.service.calculate_natal_chart_enhanced(
            self.test_request,
            include_aspects=True,
            include_dignities=True,
            include_arabic_parts=True
        )
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 100.0, \
            f"API response time {response_time_ms:.2f}ms exceeds 100ms target"

    def test_api_output_completeness(self):
        """Test that API output is complete and well-formed."""
        response = self.service.calculate_natal_chart_enhanced(
            self.test_request,
            include_aspects=True,
            include_dignities=True,
            include_arabic_parts=True
        )
        
        response_dict = response if isinstance(response, dict) else response.model_dump()
        
        # Test required sections are present
        required_sections = ['subject', 'planets', 'houses', 'angles']
        for section in required_sections:
            assert section in response_dict, f"Missing required section '{section}'"
        
        # Test planets have dignity information when requested
        planets = response_dict.get('planets', {})
        for planet_name, planet_data in planets.items():
            if 'essential_dignities' in planet_data:
                dignities = planet_data['essential_dignities']
                
                # Should have all dignity scores
                required_scores = [
                    'total_score', 'rulership_score', 'exaltation_score',
                    'triplicity_score', 'term_score', 'face_score'
                ]
                for score in required_scores:
                    assert score in dignities, \
                        f"Missing dignity score '{score}' for {planet_name}"

    def test_data_consistency_across_formats(self):
        """Test data consistency across different output formats."""
        response = self.service.calculate_natal_chart_enhanced(self.test_request)
        
        # Test that serialization is consistent
        response_dict = response if isinstance(response, dict) else response.model_dump()
        
        # Re-serialize as JSON and parse back
        json_str = json.dumps(response_dict, default=str)
        parsed_back = json.loads(json_str)
        
        # Key data should remain consistent
        assert parsed_back['subject']['name'] == response_dict['subject']['name']
        assert len(parsed_back['planets']) == len(response_dict['planets'])
        
        # Check that no data was lost in serialization
        for planet_name in response_dict['planets']:
            assert planet_name in parsed_back['planets'], \
                f"Planet {planet_name} lost during serialization"

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling."""
        # Test with extreme coordinates
        extreme_request = NatalChartRequest(
            subject=SubjectRequest(
                name="Extreme Test",
                datetime=DateTimeInput(iso_string="2000-01-01T00:00:00"),
                latitude=CoordinateInput(decimal=89.9),  # Near North Pole
                longitude=CoordinateInput(decimal=179.9)  # Near International Date Line
            )
        )
        
        # Should not crash
        response = self.service.calculate_natal_chart_enhanced(extreme_request)
        assert response is not None, "Should handle extreme coordinates gracefully"

    def test_backwards_compatibility(self):
        """Test that fixes maintain backwards compatibility."""
        # Test basic natal chart (original API)
        basic_response = self.service.calculate_natal_chart(self.test_request)
        assert basic_response is not None, "Basic API should still work"
        
        # Enhanced API with default parameters
        enhanced_response = self.service.calculate_natal_chart_enhanced(self.test_request)
        assert enhanced_response is not None, "Enhanced API should work with defaults"
        
        # Core structure should be similar
        basic_dict = basic_response.model_dump() if hasattr(basic_response, 'dict') else basic_response
        enhanced_dict = enhanced_response if isinstance(enhanced_response, dict) else enhanced_response.model_dump()
        
        # Should have same core sections
        core_sections = ['subject', 'planets', 'houses', 'angles']
        for section in core_sections:
            assert section in basic_dict, f"Basic API missing {section}"
            assert section in enhanced_dict, f"Enhanced API missing {section}"

    def test_regression_prevention(self):
        """Test that specific regression issues are prevented."""
        response = self.service.calculate_natal_chart_enhanced(
            self.test_request,
            include_aspects=True,
            include_dignities=True
        )
        
        response_dict = response if isinstance(response, dict) else response.model_dump()
        
        # Specific regression checks based on original issues
        
        # 1. No "Planet X" in aspects
        aspects = response_dict.get('aspects', [])
        for aspect in aspects:
            assert "Planet " not in aspect.get('object1', ''), \
                "Regression: Generic planet naming in aspects"
            assert "Planet " not in aspect.get('object2', ''), \
                "Regression: Generic planet naming in aspects"
        
        # 2. Essential dignities should not have obvious errors
        planets = response_dict.get('planets', {})
        
        # Venus in Taurus should never be detriment
        if 'Venus' in planets and 'essential_dignities' in planets['Venus']:
            venus_dignities = planets['Venus']['essential_dignities']
            detriment_indicators = [
                score < 0 for score in [
                    venus_dignities.get('rulership_score', 0),
                    venus_dignities.get('total_score', 0)
                ]
            ]
            assert not any(detriment_indicators), \
                "Regression: Venus showing as detriment in Taurus"
        
        # 3. Boolean fields should be actual booleans
        for planet_name, planet_data in planets.items():
            is_retrograde = planet_data.get('is_retrograde')
            if is_retrograde is not None:
                assert isinstance(is_retrograde, bool), \
                    f"Regression: {planet_name} is_retrograde not boolean"


# Performance benchmark tests
@pytest.mark.benchmark(group="remediation")
def test_complete_calculation_benchmark(benchmark):
    """Benchmark complete calculation with all fixes applied."""
    service = EphemerisService()
    
    request = NatalChartRequest(
        subject=SubjectRequest(
            name="Benchmark Test",
            datetime=DateTimeInput(iso_string="1990-06-15T14:30:00"),
            latitude=CoordinateInput(decimal=40.7128),
            longitude=CoordinateInput(decimal=-74.0060)
        )
    )
    
    result = benchmark(
        service.calculate_natal_chart_enhanced,
        request,
        include_aspects=True,
        include_dignities=True,
        include_arabic_parts=True
    )
    
    # Verify result is complete
    result_dict = result if isinstance(result, dict) else result.model_dump()
    assert 'planets' in result_dict
    assert 'aspects' in result_dict or 'aspects' in result_dict.get('calculated_aspects', {})

@pytest.mark.integration
def test_real_world_scenario():
    """Test with real-world scenario to ensure robustness."""
    service = EphemerisService()
    
    # Test multiple different birth data scenarios
    test_scenarios = [
        {
            "name": "Modern Birth",
            "datetime": "2020-03-15T10:30:00",
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London"
        },
        {
            "name": "Historical Birth", 
            "datetime": "1950-07-20T14:00:00",
            "lat": 34.0522,
            "lon": -118.2437,
            "timezone": "America/Los_Angeles"
        },
        {
            "name": "Southern Hemisphere",
            "datetime": "1985-12-25T22:15:00",
            "lat": -33.8688,
            "lon": 151.2093,
            "timezone": "Australia/Sydney"
        }
    ]
    
    for scenario in test_scenarios:
        request = NatalChartRequest(
            subject=SubjectRequest(
                name=scenario["name"],
                datetime=DateTimeInput(iso_string=scenario["datetime"]),
                latitude=CoordinateInput(decimal=scenario["lat"]),
                longitude=CoordinateInput(decimal=scenario["lon"]),
                timezone=TimezoneInput(name=scenario["timezone"])
            )
        )
        
        # Should complete without errors
        response = service.calculate_natal_chart_enhanced(
            request,
            include_aspects=True,
            include_dignities=True
        )
        
        assert response is not None, f"Failed to calculate for {scenario['name']}"
        
        # Verify no regressions
        response_dict = response if isinstance(response, dict) else response.model_dump()
        
        # Check aspects don't have generic names
        aspects = response_dict.get('aspects', [])
        for aspect in aspects:
            object1 = aspect.get('object1', '')
            object2 = aspect.get('object2', '')
            assert not object1.startswith("Planet "), \
                f"Generic naming in {scenario['name']}: {object1}"
            assert not object2.startswith("Planet "), \
                f"Generic naming in {scenario['name']}: {object2}"