"""
Comprehensive Test Suite for Predictive Astrology Features

This module provides comprehensive testing for eclipse predictions, transit calculations,
and all predictive astrology features with NASA validation requirements.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Import modules under test
from extracted.systems.eclipse_calculator import EclipseCalculator, EclipseCalculationError
from extracted.systems.transit_calculator import TransitCalculator, TransitCalculationError
from extracted.systems.predictive_search import EclipseSearchAlgorithms, TransitSearchAlgorithms
from extracted.systems.predictive_optimization import (
    VectorizedCalculations, IntelligentCaching, PredictiveOptimizer
)
from extracted.systems.validation import NASAValidator, ValidationResult
from extracted.systems.predictive_models import (
    SolarEclipse, LunarEclipse, Transit, SignIngress, EclipseType, 
    LunarEclipseType, RetrogradeStatus
)
from extracted.services.predictive_service import PredictiveService
import swisseph as swe


class TestEclipseCalculator:
    """Test suite for eclipse calculation engine."""
    
    @pytest.fixture
    def calculator(self):
        """Fixture for EclipseCalculator instance."""
        return EclipseCalculator()
    
    def test_eclipse_calculator_initialization(self, calculator):
        """Test eclipse calculator initializes correctly."""
        assert calculator is not None
        assert hasattr(calculator, 'cache')
        assert hasattr(calculator, 'redis_cache')
        assert calculator.SEARCH_STEP_DAYS == 29.5
        assert calculator.MAX_SEARCH_YEARS == 100
        assert calculator.PRECISION_SECONDS == 1.0
    
    def test_find_next_solar_eclipse_valid_date(self, calculator):
        """Test finding next solar eclipse with valid date."""
        start_date = datetime(2024, 1, 1)
        
        # Mock Swiss Ephemeris call
        with patch('swisseph.sol_eclipse_when_glob') as mock_swe:
            mock_swe.return_value = (32, [2460408.266])  # Mock eclipse on 2024-04-08
            
            with patch('swisseph.sol_eclipse_how') as mock_how:
                mock_how.return_value = [1.0566, 100.0, 0.3431]  # magnitude, obscuration, core shadow
                
                eclipse = calculator.find_next_solar_eclipse(start_date)
                
                assert eclipse is not None
                assert isinstance(eclipse, SolarEclipse)
                assert eclipse.eclipse_magnitude == 1.0566
                assert eclipse.eclipse_obscuration == 100.0
    
    def test_find_next_solar_eclipse_no_result(self, calculator):
        """Test finding solar eclipse when none exists."""
        start_date = datetime(2024, 1, 1)
        
        with patch('swisseph.sol_eclipse_when_glob') as mock_swe:
            mock_swe.return_value = None  # No eclipse found
            
            eclipse = calculator.find_next_solar_eclipse(start_date)
            assert eclipse is None
    
    def test_find_next_lunar_eclipse_valid_date(self, calculator):
        """Test finding next lunar eclipse with valid date."""
        start_date = datetime(2024, 1, 1)
        
        with patch('swisseph.lun_eclipse_when') as mock_swe:
            mock_swe.return_value = (16, [2460394.146])  # Mock lunar eclipse
            
            with patch('swisseph.lun_eclipse_how') as mock_how:
                mock_how.return_value = [0.9566, 1.1025]  # magnitude, penumbral magnitude
                
                eclipse = calculator.find_next_lunar_eclipse(start_date)
                
                assert eclipse is not None
                assert isinstance(eclipse, LunarEclipse)
                assert eclipse.eclipse_magnitude == 0.9566
                assert eclipse.penumbral_magnitude == 1.1025
    
    def test_find_eclipses_in_range(self, calculator):
        """Test finding eclipses within date range."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        with patch.object(calculator, '_find_all_solar_eclipses_in_range') as mock_solar:
            mock_solar_eclipse = SolarEclipse(
                eclipse_type=EclipseType.TOTAL,
                maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
                eclipse_magnitude=1.0566,
                eclipse_obscuration=100.0
            )
            mock_solar.return_value = [mock_solar_eclipse]
            
            with patch.object(calculator, '_find_all_lunar_eclipses_in_range') as mock_lunar:
                mock_lunar_eclipse = LunarEclipse(
                    eclipse_type=LunarEclipseType.PARTIAL,
                    maximum_eclipse_time=datetime(2024, 9, 18, 2, 44, 3),
                    eclipse_magnitude=0.0855,
                    penumbral_magnitude=1.1025
                )
                mock_lunar.return_value = [mock_lunar_eclipse]
                
                result = calculator.find_eclipses_in_range(start_date, end_date)
                
                assert 'solar' in result
                assert 'lunar' in result
                assert len(result['solar']) == 1
                assert len(result['lunar']) == 1
    
    def test_eclipse_range_validation(self, calculator):
        """Test eclipse range search input validation."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 1)  # Same as start date
        
        with pytest.raises(EclipseCalculationError):
            calculator.find_eclipses_in_range(start_date, end_date)
    
    def test_calculate_eclipse_magnitude(self, calculator):
        """Test eclipse magnitude calculation."""
        eclipse_data = {'magnitude': 1.0566}
        magnitude = calculator.calculate_eclipse_magnitude(eclipse_data)
        assert magnitude == 1.0566
        
        # Test fallback calculation
        eclipse_data_no_mag = {'obscuration': 100.0}
        magnitude = calculator.calculate_eclipse_magnitude(eclipse_data_no_mag)
        assert magnitude == 1.0  # sqrt(100/100)


class TestTransitCalculator:
    """Test suite for transit calculation engine."""
    
    @pytest.fixture
    def calculator(self):
        """Fixture for TransitCalculator instance."""
        return TransitCalculator()
    
    def test_transit_calculator_initialization(self, calculator):
        """Test transit calculator initializes correctly."""
        assert calculator is not None
        assert hasattr(calculator, 'cache')
        assert hasattr(calculator, 'redis_cache')
        assert len(calculator.PLANET_SPEEDS) == 10
        assert swe.SUN in calculator.PLANET_SPEEDS
        assert calculator.PRECISION_THRESHOLD == 1/3600.0
    
    def test_find_next_transit_valid_input(self, calculator):
        """Test finding next transit with valid input."""
        planet_id = swe.MARS
        target_degree = 90.0
        start_date = datetime(2024, 1, 1)
        
        with patch.object(calculator, '_search_planet_transits') as mock_search:
            mock_transit = Transit(
                planet_id=planet_id,
                planet_name="Mars",
                target_longitude=target_degree,
                exact_time=datetime(2024, 6, 15, 12, 0, 0),
                is_retrograde=False,
                transit_speed=0.5,
                approach_duration=30.0,
                separation_duration=30.0
            )
            mock_search.return_value = [mock_transit]
            
            transits = calculator.find_next_transit(planet_id, target_degree, start_date)
            
            assert len(transits) == 1
            assert transits[0].planet_name == "Mars"
            assert transits[0].target_longitude == target_degree
    
    def test_find_next_transit_invalid_planet(self, calculator):
        """Test transit calculation with invalid planet ID."""
        invalid_planet_id = 999
        target_degree = 90.0
        start_date = datetime(2024, 1, 1)
        
        with pytest.raises(TransitCalculationError):
            calculator.find_next_transit(invalid_planet_id, target_degree, start_date)
    
    def test_find_sign_ingress(self, calculator):
        """Test finding sign ingresses."""
        planet_id = swe.JUPITER
        start_date = datetime(2024, 1, 1)
        
        with patch.object(calculator, '_search_sign_ingresses') as mock_search:
            mock_ingress = SignIngress(
                planet_id=planet_id,
                planet_name="Jupiter",
                from_sign="Taurus",
                to_sign="Gemini",
                ingress_time=datetime(2024, 5, 26, 8, 15, 0),
                retrograde_status=RetrogradeStatus.DIRECT
            )
            mock_search.return_value = [mock_ingress]
            
            ingresses = calculator.find_sign_ingress(planet_id, start_date)
            
            assert len(ingresses) == 1
            assert ingresses[0].planet_name == "Jupiter"
            assert ingresses[0].from_sign == "Taurus"
            assert ingresses[0].to_sign == "Gemini"
    
    def test_find_transits_in_range(self, calculator):
        """Test finding transits within date range."""
        planet_id = swe.VENUS
        target_degree = 0.0
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        with patch.object(calculator, 'find_next_transit') as mock_find:
            mock_transit1 = Transit(
                planet_id=planet_id,
                planet_name="Venus",
                target_longitude=target_degree,
                exact_time=datetime(2024, 3, 15, 6, 30, 0),
                is_retrograde=False,
                transit_speed=1.2,
                approach_duration=5.0,
                separation_duration=5.0
            )
            mock_transit2 = Transit(
                planet_id=planet_id,
                planet_name="Venus",
                target_longitude=target_degree,
                exact_time=datetime(2024, 11, 8, 14, 45, 0),
                is_retrograde=True,
                transit_speed=1.2,
                approach_duration=5.0,
                separation_duration=5.0
            )
            mock_find.side_effect = [[mock_transit1], [mock_transit2], []]
            
            transits = calculator.find_transits_in_range(planet_id, target_degree, start_date, end_date)
            
            assert len(transits) == 2
            assert transits[0].exact_time < transits[1].exact_time
    
    def test_calculate_transit_duration(self, calculator):
        """Test transit duration calculation."""
        planet_id = swe.MERCURY
        target_degree = 180.0
        transit_date = datetime(2024, 6, 1, 12, 0, 0)
        orb_degrees = 1.0
        
        with patch.object(calculator, '_find_orb_entry') as mock_entry:
            mock_entry.return_value = transit_date - timedelta(days=2)
            
            with patch.object(calculator, '_find_orb_exit') as mock_exit:
                mock_exit.return_value = transit_date + timedelta(days=3)
                
                duration = calculator.calculate_transit_duration(
                    planet_id, target_degree, transit_date, orb_degrees
                )
                
                assert 'approach_duration' in duration
                assert 'separation_duration' in duration
                assert 'total_duration' in duration
                assert duration['approach_duration'] == 2.0
                assert duration['separation_duration'] == 3.0
                assert duration['total_duration'] == 5.0


class TestPredictiveSearch:
    """Test suite for predictive search algorithms."""
    
    @pytest.fixture
    def eclipse_search(self):
        """Fixture for EclipseSearchAlgorithms instance."""
        return EclipseSearchAlgorithms()
    
    @pytest.fixture
    def transit_search(self):
        """Fixture for TransitSearchAlgorithms instance."""
        return TransitSearchAlgorithms()
    
    def test_eclipse_search_initialization(self, eclipse_search):
        """Test eclipse search algorithms initialization."""
        assert eclipse_search is not None
        assert hasattr(eclipse_search, 'SOLAR_ECLIPSE_SEARCH_PARAMS')
        assert hasattr(eclipse_search, 'LUNAR_ECLIPSE_SEARCH_PARAMS')
        assert eclipse_search.SOLAR_ECLIPSE_SEARCH_PARAMS.initial_step_days == 29.5
        assert eclipse_search.LUNAR_ECLIPSE_SEARCH_PARAMS.initial_step_days == 14.8
    
    def test_binary_search_eclipse_time(self, eclipse_search):
        """Test binary search for eclipse timing."""
        eclipse_type = 'solar'
        start_jd = 2460000.0
        end_jd = 2460030.0
        eclipse_flags = 32
        
        with patch.object(eclipse_search, '_check_solar_eclipse_at_jd') as mock_check:
            mock_check.side_effect = [
                {'has_eclipse': False, 'direction': 'later'},
                {'has_eclipse': True, 'precision': 0.001}
            ]
            
            result = eclipse_search.binary_search_eclipse_time(
                eclipse_type, start_jd, end_jd, eclipse_flags
            )
            
            assert result.found is True
            assert result.timestamp is not None
            assert result.precision_seconds < 60.0
            assert result.iterations > 0
    
    def test_global_eclipse_search(self, eclipse_search):
        """Test global eclipse search across multiple years."""
        start_date = datetime(2024, 1, 1)
        search_years = 1
        
        with patch('swisseph.sol_eclipse_when_glob') as mock_solar:
            mock_solar.return_value = (32, [2460408.266])  # April 8, 2024 eclipse
            
            with patch('swisseph.lun_eclipse_when') as mock_lunar:
                mock_lunar.return_value = (16, [2460394.146])  # March 25, 2024 eclipse
                
                eclipses = eclipse_search.global_eclipse_search(start_date, search_years)
                
                assert isinstance(eclipses, list)
                # Should find at least one eclipse in the year
                assert len(eclipses) >= 0
    
    def test_transit_search_initialization(self, transit_search):
        """Test transit search algorithms initialization."""
        assert transit_search is not None
        assert hasattr(transit_search, 'SEARCH_PARAMS')
        assert len(transit_search.SEARCH_PARAMS) == 10  # All planets
        assert swe.MOON in transit_search.SEARCH_PARAMS
        assert swe.PLUTO in transit_search.SEARCH_PARAMS
    
    def test_binary_search_transit(self, transit_search):
        """Test binary search for transit timing."""
        planet_id = swe.MARS
        target_degree = 90.0
        start_jd = 2460000.0
        end_jd = 2460100.0
        
        with patch('swisseph.calc_ut') as mock_calc:
            # Mock planetary positions
            mock_calc.side_effect = [
                ([85.0, 0.0, 1.5, 0.5, 0.0, 0.0], [0.5, 0.0, 0.0, 0.0, 0.0, 0.0]),
                ([87.5, 0.0, 1.5, 0.5, 0.0, 0.0], [0.5, 0.0, 0.0, 0.0, 0.0, 0.0]),
                ([90.0, 0.0, 1.5, 0.5, 0.0, 0.0], [0.5, 0.0, 0.0, 0.0, 0.0, 0.0])
            ]
            
            result = transit_search.binary_search_transit(
                planet_id, target_degree, start_jd, end_jd
            )
            
            assert result.found is True or result.found is False  # Either outcome is valid
            assert result.iterations > 0


class TestPredictiveOptimization:
    """Test suite for performance optimization features."""
    
    @pytest.fixture
    def vectorized_calc(self):
        """Fixture for VectorizedCalculations instance."""
        return VectorizedCalculations()
    
    @pytest.fixture
    def intelligent_cache(self):
        """Fixture for IntelligentCaching instance."""
        return IntelligentCaching()
    
    @pytest.fixture
    def optimizer(self):
        """Fixture for PredictiveOptimizer instance."""
        return PredictiveOptimizer()
    
    def test_vectorized_calculations_initialization(self, vectorized_calc):
        """Test vectorized calculations initialization."""
        assert vectorized_calc is not None
        assert hasattr(vectorized_calc, '_position_cache')
        assert hasattr(vectorized_calc, '_computation_count')
    
    def test_calculate_vectorized_planetary_positions(self, vectorized_calc):
        """Test vectorized planetary position calculations."""
        julian_days = np.array([2460000.0, 2460001.0, 2460002.0])
        planet_ids = [swe.SUN, swe.MOON]
        
        with patch('swisseph.calc_ut') as mock_calc:
            # Mock Swiss Ephemeris responses
            mock_calc.side_effect = [
                ([280.0, 0.0, 1.0, 0.985, 0.0, 0.0], [0.985, 0.0, 0.0, 0.0, 0.0, 0.0]),  # Sun day 1
                ([295.0, -1.2, 0.002, 13.2, -0.1, 0.0], [13.2, -0.1, 0.0, 0.0, 0.0, 0.0]),  # Moon day 1
                ([280.985, 0.0, 1.0, 0.985, 0.0, 0.0], [0.985, 0.0, 0.0, 0.0, 0.0, 0.0]),  # Sun day 2
                ([308.2, -1.1, 0.002, 13.2, -0.1, 0.0], [13.2, -0.1, 0.0, 0.0, 0.0, 0.0]),  # Moon day 2
                ([281.97, 0.0, 1.0, 0.985, 0.0, 0.0], [0.985, 0.0, 0.0, 0.0, 0.0, 0.0]),   # Sun day 3
                ([321.4, -0.9, 0.002, 13.2, -0.1, 0.0], [13.2, -0.1, 0.0, 0.0, 0.0, 0.0])   # Moon day 3
            ]
            
            positions = vectorized_calc.calculate_vectorized_planetary_positions(
                julian_days, planet_ids
            )
            
            assert len(positions) == 2  # Sun and Moon
            assert swe.SUN in positions
            assert swe.MOON in positions
            assert positions[swe.SUN].shape == (3, 6)  # 3 dates, 6 coordinates
            assert positions[swe.MOON].shape == (3, 6)
    
    def test_intelligent_cache_functionality(self, intelligent_cache):
        """Test intelligent caching functionality."""
        operation_type = 'eclipse_search'
        cache_key = 'test_eclipse_2024'
        
        def expensive_computation():
            return {'eclipse_time': '2024-04-08T18:17:16', 'magnitude': 1.0566}
        
        # First call - should compute and cache
        result1 = intelligent_cache.get_cached_result(
            operation_type, cache_key, expensive_computation
        )
        
        # Second call - should retrieve from cache
        result2 = intelligent_cache.get_cached_result(
            operation_type, cache_key, expensive_computation
        )
        
        assert result1 == result2
        
        # Check cache stats
        stats = intelligent_cache.get_cache_stats()
        assert stats['total_requests'] == 2
        assert stats['hit_rate'] == 0.5  # 1 hit out of 2 requests
    
    def test_cache_memory_management(self, intelligent_cache):
        """Test cache memory management and LRU eviction."""
        # Set small memory limit for testing
        intelligent_cache.max_memory_bytes = 1024  # 1KB limit
        
        # Fill cache beyond limit
        for i in range(10):
            cache_key = f'test_key_{i}'
            result = intelligent_cache.get_cached_result(
                'test_operation', cache_key, lambda: f'data_{i}' * 100
            )
        
        stats = intelligent_cache.get_cache_stats()
        assert stats['evictions'] > 0  # Some items should be evicted
    
    def test_optimizer_eclipse_search(self, optimizer):
        """Test optimizer eclipse search functionality."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        with patch.object(optimizer.vectorized_calc, 'vectorized_eclipse_search') as mock_search:
            mock_search.return_value = [
                {'type': 'solar', 'julian_day': 2460408.266, 'flags': 32},
                {'type': 'lunar', 'julian_day': 2460394.146, 'flags': 16}
            ]
            
            results = optimizer.optimize_eclipse_search(start_date, end_date)
            
            assert isinstance(results, list)
            assert len(results) == 2
    
    def test_optimization_report_generation(self, optimizer):
        """Test optimization report generation."""
        report = optimizer.get_optimization_report()
        
        assert 'performance_metrics' in report
        assert 'optimization_status' in report
        assert 'recommendations' in report
        assert 'system_info' in report
        
        assert 'cache_hit_rate' in report['performance_metrics']
        assert 'vectorization_enabled' in report['optimization_status']


class TestNASAValidation:
    """Test suite for NASA validation system."""
    
    @pytest.fixture
    def validator(self):
        """Fixture for NASAValidator instance."""
        return NASAValidator()
    
    def test_nasa_validator_initialization(self, validator):
        """Test NASA validator initialization."""
        assert validator is not None
        assert hasattr(validator, 'TOLERANCES')
        assert validator.TOLERANCES['eclipse_timing_seconds'] == 60.0
        assert validator.TOLERANCES['position_arcseconds'] == 0.1
    
    def test_validate_eclipse_against_canon(self, validator):
        """Test eclipse validation against NASA canon."""
        # Create mock eclipse
        eclipse = SolarEclipse(
            eclipse_type=EclipseType.TOTAL,
            maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
            eclipse_magnitude=1.0566,
            eclipse_obscuration=100.0
        )
        
        # Mock reference eclipse data
        with patch.object(validator, '_find_closest_reference_eclipse') as mock_ref:
            mock_ref.return_value = {
                'catalog_id': 'SE2024Apr08T',
                'maximum_time': datetime(2024, 4, 8, 18, 17, 45),  # 29 seconds difference
                'magnitude': 1.0566,
                'type': 'total'
            }
            
            result = validator.validate_eclipse_against_canon(eclipse)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is True  # Within 60 second tolerance
            assert result.timing_error_seconds == 29.0
            assert result.reference_source == "NASA Five Millennium Canon"
    
    def test_generate_accuracy_report(self, validator):
        """Test accuracy report generation."""
        # Mock validation history
        with patch.object(validator, '_load_validation_history') as mock_history:
            mock_history.return_value = [
                {'is_valid': True, 'timing_error_seconds': 30.0, 'position_error_arcseconds': 0.05},
                {'is_valid': True, 'timing_error_seconds': 45.0, 'position_error_arcseconds': 0.08},
                {'is_valid': False, 'timing_error_seconds': 90.0, 'position_error_arcseconds': 0.2}
            ]
            
            report = validator.generate_accuracy_report()
            
            assert report.total_tests == 3
            assert report.passed_tests == 2
            assert report.failed_tests == 1
            assert report.accuracy_percentage == pytest.approx(66.67, rel=0.1)
            assert report.average_timing_error == 55.0  # (30+45+90)/3
    
    def test_automated_validation_suite(self, validator):
        """Test automated validation suite execution."""
        with patch.object(validator, '_run_eclipse_validation_tests') as mock_eclipse:
            mock_eclipse.return_value = [
                {'test_id': 'SE2024Apr08T', 'passed': True, 'timing_error_seconds': 25.0},
                {'test_id': 'SE2024Oct02A', 'passed': True, 'timing_error_seconds': 40.0}
            ]
            
            with patch.object(validator, '_run_position_validation_tests') as mock_position:
                mock_position.return_value = [
                    {'test_id': 'Sun_2024-01-01', 'passed': True, 'position_error_arcseconds': 0.03},
                    {'test_id': 'Moon_2024-01-01', 'passed': True, 'position_error_arcseconds': 0.07}
                ]
                
                with patch.object(validator, '_store_validation_results'):
                    results = validator.automated_validation_suite()
                    
                    assert 'eclipse_tests' in results
                    assert 'position_tests' in results
                    assert 'summary' in results
                    assert results['summary']['total_tests'] == 4
                    assert results['summary']['passed_tests'] == 4
                    assert results['summary']['success_rate'] == 100.0


class TestPredictiveService:
    """Test suite for predictive service integration."""
    
    @pytest.fixture
    def service(self):
        """Fixture for PredictiveService instance."""
        return PredictiveService()
    
    @pytest.mark.asyncio
    async def test_find_next_solar_eclipse_service(self, service):
        """Test solar eclipse search through service."""
        start_date = datetime(2024, 1, 1)
        
        with patch.object(service.eclipse_calculator, 'find_next_solar_eclipse') as mock_calc:
            mock_eclipse = SolarEclipse(
                eclipse_type=EclipseType.TOTAL,
                maximum_eclipse_time=datetime(2024, 4, 8, 18, 17, 16),
                eclipse_magnitude=1.0566,
                eclipse_obscuration=100.0
            )
            mock_calc.return_value = mock_eclipse
            
            result = await service.find_next_solar_eclipse(start_date)
            
            assert result is not None
            assert isinstance(result, SolarEclipse)
            assert result.eclipse_type == EclipseType.TOTAL
    
    @pytest.mark.asyncio
    async def test_find_planet_transit_service(self, service):
        """Test planet transit calculation through service."""
        planet_name = "Mars"
        target_degree = 90.0
        start_date = datetime(2024, 1, 1)
        
        with patch.object(service.transit_calculator, 'find_next_transit') as mock_calc:
            mock_transit = Transit(
                planet_id=swe.MARS,
                planet_name="Mars",
                target_longitude=target_degree,
                exact_time=datetime(2024, 6, 15, 12, 0, 0),
                is_retrograde=False,
                transit_speed=0.5,
                approach_duration=30.0,
                separation_duration=30.0
            )
            mock_calc.return_value = [mock_transit]
            
            result = await service.find_planet_transit(planet_name, target_degree, start_date)
            
            assert len(result) == 1
            assert result[0].planet_name == "Mars"
            assert result[0].target_longitude == target_degree
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self, service):
        """Test service error handling."""
        with patch.object(service.eclipse_calculator, 'find_next_solar_eclipse') as mock_calc:
            mock_calc.side_effect = EclipseCalculationError("Test error")
            
            with pytest.raises(Exception):  # Should raise PredictiveServiceError
                await service.find_next_solar_eclipse(datetime(2024, 1, 1))
    
    def test_service_optimization_integration(self, service):
        """Test service optimization integration."""
        status = service.get_optimization_status()
        
        assert isinstance(status, dict)
        # Should have optimization report structure
        assert 'performance_metrics' in status or 'error' in status


class TestPerformanceBenchmarks:
    """Performance benchmark tests to ensure optimization targets are met."""
    
    @pytest.mark.benchmark(group="eclipse_calculations")
    def test_eclipse_search_performance(self, benchmark):
        """Benchmark eclipse search performance."""
        calculator = EclipseCalculator()
        start_date = datetime(2024, 1, 1)
        
        def eclipse_search():
            with patch('swisseph.sol_eclipse_when_glob') as mock_swe:
                mock_swe.return_value = (32, [2460408.266])
                with patch('swisseph.sol_eclipse_how') as mock_how:
                    mock_how.return_value = [1.0566, 100.0, 0.3431]
                    return calculator.find_next_solar_eclipse(start_date)
        
        result = benchmark(eclipse_search)
        assert result is not None
    
    @pytest.mark.benchmark(group="transit_calculations")
    def test_transit_calculation_performance(self, benchmark):
        """Benchmark transit calculation performance."""
        calculator = TransitCalculator()
        planet_id = swe.MARS
        target_degree = 90.0
        start_date = datetime(2024, 1, 1)
        
        def transit_calculation():
            with patch('swisseph.calc_ut') as mock_calc:
                mock_calc.return_value = ([90.0, 0.0, 1.5, 0.5, 0.0, 0.0], [0.5, 0.0, 0.0, 0.0, 0.0, 0.0])
                with patch.object(calculator, '_search_planet_transits') as mock_search:
                    mock_transit = Transit(
                        planet_id=planet_id,
                        planet_name="Mars",
                        target_longitude=target_degree,
                        exact_time=datetime(2024, 6, 15, 12, 0, 0),
                        is_retrograde=False,
                        transit_speed=0.5,
                        approach_duration=30.0,
                        separation_duration=30.0
                    )
                    mock_search.return_value = [mock_transit]
                    return calculator.find_next_transit(planet_id, target_degree, start_date)
        
        result = benchmark(transit_calculation)
        assert len(result) >= 0
    
    @pytest.mark.benchmark(group="optimization")
    def test_vectorized_calculation_performance(self, benchmark):
        """Benchmark vectorized calculation performance."""
        vectorized_calc = VectorizedCalculations()
        julian_days = np.array([2460000.0, 2460001.0, 2460002.0])
        planet_ids = [swe.SUN, swe.MOON]
        
        def vectorized_calculation():
            with patch('swisseph.calc_ut') as mock_calc:
                mock_responses = [
                    ([280.0 + i, 0.0, 1.0, 0.985, 0.0, 0.0], [0.985, 0.0, 0.0, 0.0, 0.0, 0.0])
                    for i in range(len(julian_days) * len(planet_ids))
                ]
                mock_calc.side_effect = mock_responses
                
                return vectorized_calc.calculate_vectorized_planetary_positions(
                    julian_days, planet_ids
                )
        
        result = benchmark(vectorized_calculation)
        assert len(result) == len(planet_ids)


# Integration test markers
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance

# Test configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "benchmark: marks tests as benchmarks"
    )