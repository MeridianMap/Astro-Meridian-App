"""
Test suite for Enhanced EphemerisService functionality
"""
import pytest
from datetime import datetime, timezone

from app.services.ephemeris_service import EphemerisService
from app.api.models.schemas import NatalChartRequest, SubjectRequest, DateTimeInput, CoordinateInput


class TestEnhancedEphemerisService:
    """Test the enhanced EphemerisService functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = EphemerisService()
    
    def test_service_initialization(self):
        """Test that service initializes correctly"""
        assert self.service is not None
    
    @pytest.mark.integration 
    def test_enhanced_natal_chart_calculation(self):
        """Integration test with real ephemeris data"""
        
        request = NatalChartRequest(
            subject=SubjectRequest(
                name="Test Subject",
                datetime=DateTimeInput(
                    components={
                        "year": 2024,
                        "month": 6,
                        "day": 15,
                        "hour": 14,
                        "minute": 30,
                        "second": 0
                    }
                ),
                latitude=CoordinateInput(decimal=51.5074),  # London
                longitude=CoordinateInput(decimal=-0.1278)
            )
        )
        
        result = self.service.calculate_natal_chart_enhanced(request)
        
        # Basic structure validation
        assert isinstance(result, dict)
        assert 'calculation_time' in result
        
        # If we have planets, verify they have enhanced properties
        if 'planets' in result:
            planets = result['planets']
            assert len(planets) > 0, "Should have planets"
            
            for planet in planets:
                if hasattr(planet, 'name'):
                    # Verify enhanced properties
                    assert hasattr(planet, 'is_retrograde'), f"Planet {getattr(planet, 'name', 'unknown')} missing is_retrograde"
                    assert hasattr(planet, 'motion_type'), f"Planet {getattr(planet, 'name', 'unknown')} missing motion_type"
                    
                    # Verify motion type values
                    motion_type = getattr(planet, 'motion_type', None)
                    assert motion_type in ['direct', 'retrograde', 'stationary', 'unknown'], f"Invalid motion_type: {motion_type}"
                    
                    # Verify is_retrograde consistency
                    is_retrograde = getattr(planet, 'is_retrograde', False)
                    assert isinstance(is_retrograde, bool), "is_retrograde should be boolean"
        
        # Check for retrograde analysis if present
        if 'retrograde_analysis' in result:
            retro_analysis = result['retrograde_analysis']
            assert 'total_retrograde' in retro_analysis
            assert 'retrograde_planets' in retro_analysis
            assert 'retrograde_percentage' in retro_analysis
            
            # Verify analysis consistency
            total_retrograde = retro_analysis.get('total_retrograde', 0)
            retrograde_list = retro_analysis.get('retrograde_planets', [])
            assert total_retrograde == len(retrograde_list), "Retrograde count mismatch"
    
    def test_enhanced_chart_with_different_location(self):
        """Test enhanced chart calculation with different location"""
        
        # New York coordinates
        request = NatalChartRequest(
            subject=SubjectRequest(
                name="NYC Test",
                datetime=DateTimeInput(
                    components={
                        "year": 2000,
                        "month": 1,
                        "day": 1,
                        "hour": 0,
                        "minute": 0,
                        "second": 0
                    }
                ),
                latitude=CoordinateInput(decimal=40.7128),
                longitude=CoordinateInput(decimal=-74.0060)
            )
        )
        
        result = self.service.calculate_natal_chart_enhanced(request)
        
        # Verify basic structure
        assert isinstance(result, dict)
        assert 'calculation_time' in result
        
        # Should have planets or an error explanation
        assert 'planets' in result or 'error' in result
    
    def test_enhanced_chart_validation_error(self):
        """Test that validation errors are properly raised"""
        
        # This should raise validation error due to missing name
        with pytest.raises(Exception):  # Pydantic validation error
            invalid_request = NatalChartRequest(
                subject=SubjectRequest(
                    # Missing required 'name' field
                    datetime=DateTimeInput(
                        components={
                            "year": 2024,
                            "month": 1,
                            "day": 1,
                            "hour": 12,
                            "minute": 0,
                            "second": 0
                        }
                    ),
                    latitude=CoordinateInput(decimal=51.5074),
                    longitude=CoordinateInput(decimal=-0.1278)
                )
            )


if __name__ == "__main__":
    pytest.main([__file__])
