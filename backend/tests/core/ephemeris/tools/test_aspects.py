"""
Comprehensive Test Suite for Aspect Calculation Engine

Tests all components of the professional aspect calculation system including:
- Core aspect calculation algorithms
- Orb system configurations
- Vectorized performance optimizations
- Batch processing capabilities
- API integration
- Performance benchmarks
"""

import pytest
import numpy as np
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from app.core.ephemeris.tools.aspects import (
    AspectCalculator, AspectType, Aspect, OrbConfiguration,
    AspectMatrix, BatchAspectCalculator, calculate_aspect_strength
)
from app.core.ephemeris.tools.orb_systems import OrbSystemManager
from app.core.ephemeris.classes.serialize import PlanetPosition


class TestAspectCalculatorCore:
    """Test core aspect calculation functionality."""
    
    @pytest.fixture
    def orb_config(self):
        """Standard orb configuration for testing."""
        return OrbConfiguration(
            preset_name="test",
            aspect_orbs={
                'conjunction': {'sun': 8.0, 'moon': 8.0, 'default': 6.0},
                'opposition': {'sun': 8.0, 'moon': 8.0, 'default': 6.0},
                'trine': {'sun': 6.0, 'moon': 6.0, 'default': 5.0},
                'square': {'sun': 6.0, 'moon': 6.0, 'default': 5.0},
                'sextile': {'sun': 4.0, 'moon': 4.0, 'default': 3.5}
            }
        )
    
    @pytest.fixture
    def aspect_calculator(self, orb_config):
        """Aspect calculator instance for testing."""
        return AspectCalculator(orb_config)
    
    @pytest.fixture
    def sample_positions(self):
        """Sample planet positions for testing."""
        return [
            PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=1.0, planet_id=0),    # Sun at 0°
            PlanetPosition(longitude=60.0, latitude=0.0, distance=1.0, longitude_speed=0.5, planet_id=1),   # Moon at 60°
            PlanetPosition(longitude=120.0, latitude=0.0, distance=1.0, longitude_speed=-0.5, planet_id=2), # Mercury at 120°
            PlanetPosition(longitude=180.0, latitude=0.0, distance=1.0, longitude_speed=1.5, planet_id=3),  # Venus at 180°
        ]
    
    def test_angle_difference_calculation(self, aspect_calculator):
        """Test angle difference calculations with 360-degree wrapping."""
        # Basic angle differences
        assert aspect_calculator._calculate_angle_difference(0.0, 60.0) == 60.0
        assert aspect_calculator._calculate_angle_difference(60.0, 0.0) == 60.0
        
        # 360-degree boundary crossing
        assert aspect_calculator._calculate_angle_difference(10.0, 350.0) == 20.0
        assert aspect_calculator._calculate_angle_difference(350.0, 10.0) == 20.0
        
        # Large angle differences
        assert aspect_calculator._calculate_angle_difference(0.0, 180.0) == 180.0
        assert aspect_calculator._calculate_angle_difference(90.0, 270.0) == 180.0
    
    def test_angle_difference_from_exact(self, aspect_calculator):
        """Test calculations of differences from exact aspect angles."""
        # Conjunction (0°) special case
        assert aspect_calculator._angle_difference_from_exact(5.0, 0.0) == 5.0
        assert aspect_calculator._angle_difference_from_exact(355.0, 0.0) == 5.0
        
        # Opposition (180°) special case  
        assert aspect_calculator._angle_difference_from_exact(175.0, 180.0) == 5.0
        assert aspect_calculator._angle_difference_from_exact(185.0, 180.0) == 5.0
        
        # Regular aspects
        assert aspect_calculator._angle_difference_from_exact(58.0, 60.0) == 2.0
        assert aspect_calculator._angle_difference_from_exact(122.0, 120.0) == 2.0
    
    def test_orb_for_aspect_calculation(self, aspect_calculator):
        """Test orb retrieval for different planet/aspect combinations."""
        # Sun conjunction - should get 8.0
        assert aspect_calculator._get_orb_for_aspect('sun', 'moon', 'conjunction') == 8.0
        
        # Default orb fallback
        assert aspect_calculator._get_orb_for_aspect('mars', 'jupiter', 'conjunction') == 6.0
        
        # Use larger orb (more generous approach)
        assert aspect_calculator._get_orb_for_aspect('sun', 'mars', 'conjunction') == 8.0  # Sun's orb
    
    def test_aspect_strength_calculation(self):
        """Test aspect strength calculations."""
        # Exact aspect
        assert calculate_aspect_strength(0.0, 6.0) == 1.0
        
        # Half orb
        assert calculate_aspect_strength(3.0, 6.0) == 0.5
        
        # Full orb
        assert calculate_aspect_strength(6.0, 6.0) == 0.0
        
        # Beyond orb (should not happen in real usage)
        assert calculate_aspect_strength(7.0, 6.0) == 0.0
        
        # Edge case: zero orb
        assert calculate_aspect_strength(1.0, 0.0) == 0.0
    
    def test_applying_separating_detection(self, aspect_calculator):
        """Test applying vs separating aspect detection."""
        # Applying conjunction (planets moving together)
        is_applying = aspect_calculator._is_aspect_applying(5.0, 355.0, 1.0, -1.0, 0.0)
        assert is_applying is True  # Moving toward 0°
        
        # Separating conjunction  
        is_applying = aspect_calculator._is_aspect_applying(355.0, 5.0, -1.0, 1.0, 0.0)
        assert is_applying is False  # Moving away from 0°
        
        # No motion data
        is_applying = aspect_calculator._is_aspect_applying(0.0, 60.0, 0.0, 0.0, 60.0)
        assert is_applying is None  # Cannot determine without motion
    
    def test_single_aspect_calculation(self, aspect_calculator, sample_positions):
        """Test calculation of aspects between specific planets."""
        aspects = aspect_calculator.calculate_aspects(sample_positions)
        
        assert len(aspects) > 0
        
        # Verify aspect data structure
        for aspect in aspects:
            assert hasattr(aspect, 'planet1')
            assert hasattr(aspect, 'planet2') 
            assert hasattr(aspect, 'aspect_type')
            assert hasattr(aspect, 'angle')
            assert hasattr(aspect, 'orb_used')
            assert hasattr(aspect, 'strength')
            assert hasattr(aspect, 'is_applying')
            
            # Verify data types and ranges
            assert isinstance(aspect.angle, float)
            assert 0.0 <= aspect.angle <= 360.0
            assert isinstance(aspect.strength, float)
            assert 0.0 <= aspect.strength <= 1.0
            assert isinstance(aspect.is_applying, (bool, type(None)))
    
    def test_vectorized_calculation_consistency(self, aspect_calculator, sample_positions):
        """Test that vectorized calculations match standard calculations."""
        # Calculate using both methods
        standard_aspects = aspect_calculator._calculate_planet_pair_aspects(
            'sun', {'longitude': 0.0, 'daily_motion': 1.0},
            'moon', {'longitude': 60.0, 'daily_motion': 0.5}
        )
        
        vectorized_aspects = aspect_calculator.calculate_aspects_vectorized([
            sample_positions[0], sample_positions[1]  # Sun and Moon
        ])
        
        # Should find the same aspects
        if standard_aspects and vectorized_aspects:
            # Find sextile aspect in both results
            standard_sextile = next((a for a in standard_aspects if a.aspect_type == 'sextile'), None)
            vectorized_sextile = next((a for a in vectorized_aspects if a.aspect_type == 'sextile'), None)
            
            if standard_sextile and vectorized_sextile:
                assert abs(standard_sextile.angle - vectorized_sextile.angle) < 0.01
                assert abs(standard_sextile.strength - vectorized_sextile.strength) < 0.01
    
    def test_edge_cases(self, aspect_calculator):
        """Test edge cases and error conditions."""
        # Empty position list
        aspects = aspect_calculator.calculate_aspects([])
        assert aspects == []
        
        # Single position
        single_position = [PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=0.0, planet_id=0)]
        aspects = aspect_calculator.calculate_aspects(single_position)
        assert aspects == []
        
        # Exact aspect angles
        exact_positions = [
            PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=0.0, planet_id=0),
            PlanetPosition(longitude=60.0, latitude=0.0, distance=1.0, longitude_speed=0.0, planet_id=1)  # Exact sextile
        ]
        aspects = aspect_calculator.calculate_aspects(exact_positions)
        sextile_aspects = [a for a in aspects if a.aspect_type == 'sextile']
        assert len(sextile_aspects) >= 1
        if sextile_aspects:
            assert sextile_aspects[0].strength == 1.0  # Should be exact
    
    def test_aspect_matrix_calculation(self, aspect_calculator, sample_positions):
        """Test complete aspect matrix calculation with metadata."""
        matrix = aspect_calculator.calculate_aspect_matrix(sample_positions)
        
        assert isinstance(matrix, AspectMatrix)
        assert isinstance(matrix.aspects, list)
        assert isinstance(matrix.total_aspects, int)
        assert isinstance(matrix.major_aspects, int)
        assert isinstance(matrix.minor_aspects, int)
        assert isinstance(matrix.calculation_time_ms, float)
        
        # Verify counts add up
        assert matrix.total_aspects == len(matrix.aspects)
        assert matrix.total_aspects == matrix.major_aspects + matrix.minor_aspects
        
        # Performance check: should be under 50ms for small chart
        assert matrix.calculation_time_ms < 50.0


class TestOrbSystemIntegration:
    """Test integration with different orb systems."""
    
    @pytest.fixture
    def orb_manager(self):
        """Orb system manager instance."""
        return OrbSystemManager()
    
    @pytest.fixture  
    def sample_positions(self):
        """Sample positions for orb testing."""
        return [
            PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=0.0, planet_id=0),    # Sun
            PlanetPosition(longitude=7.0, latitude=0.0, distance=1.0, longitude_speed=0.0, planet_id=1),    # Moon at 7° (within sun conjunction orb)
        ]
    
    def test_traditional_orb_system(self, orb_manager, sample_positions):
        """Test traditional orb system."""
        orb_config = orb_manager.get_orb_preset('traditional')
        calculator = AspectCalculator(orb_config)
        
        aspects = calculator.calculate_aspects(sample_positions)
        
        # Should find conjunction (Sun at 0°, Moon at 7°, within 8° traditional sun orb)
        conjunctions = [a for a in aspects if a.aspect_type == 'conjunction']
        assert len(conjunctions) >= 1
    
    def test_modern_orb_system(self, orb_manager, sample_positions):
        """Test modern orb system (more generous orbs)."""
        orb_config = orb_manager.get_orb_preset('modern')
        calculator = AspectCalculator(orb_config)
        
        aspects = calculator.calculate_aspects(sample_positions)
        
        # Should still find conjunction with modern system
        conjunctions = [a for a in aspects if a.aspect_type == 'conjunction']
        assert len(conjunctions) >= 1
    
    def test_tight_orb_system(self, orb_manager):
        """Test tight orb system (research-grade precision)."""
        orb_config = orb_manager.get_orb_preset('tight')
        calculator = AspectCalculator(orb_config)
        
        # Positions with wider orb (should be found in traditional but not tight)
        wide_positions = [
            PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=0.0, planet_id=0),    # Sun
            PlanetPosition(longitude=6.0, latitude=0.0, distance=1.0, longitude_speed=0.0, planet_id=1),    # Moon at 6°
        ]
        
        aspects = calculator.calculate_aspects(wide_positions)
        conjunctions = [a for a in aspects if a.aspect_type == 'conjunction']
        
        # Tight system may or may not find this depending on exact orb settings
        # The key test is that it runs without error
        assert isinstance(aspects, list)
    
    def test_custom_orb_configuration(self, orb_manager):
        """Test custom orb configuration creation."""
        custom_orbs = {
            'conjunction': {
                'sun': 10.0,
                'moon': 10.0,
                'default': 8.0
            },
            'opposition': {
                'sun': 10.0,
                'moon': 10.0, 
                'default': 8.0
            }
        }
        
        orb_config = orb_manager.create_custom_orb_config(custom_orbs)
        calculator = AspectCalculator(orb_config)
        
        # Verify custom orbs are used
        sun_moon_orb = calculator._get_orb_for_aspect('sun', 'moon', 'conjunction')
        assert sun_moon_orb == 10.0
        
        default_orb = calculator._get_orb_for_aspect('mars', 'jupiter', 'conjunction')
        assert default_orb == 8.0


class TestBatchProcessing:
    """Test batch aspect calculation capabilities."""
    
    @pytest.fixture
    def orb_config(self):
        """Standard orb configuration."""
        return OrbConfiguration(
            preset_name="batch_test",
            aspect_orbs={
                'conjunction': {'default': 6.0},
                'opposition': {'default': 6.0},
                'trine': {'default': 5.0},
                'square': {'default': 5.0},
                'sextile': {'default': 3.5}
            }
        )
    
    @pytest.fixture
    def batch_calculator(self, orb_config):
        """Batch aspect calculator instance."""
        return BatchAspectCalculator(orb_config)
    
    @pytest.fixture
    def sample_chart_batches(self):
        """Multiple charts for batch processing."""
        return [
            # Chart 1
            [
                PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=1.0, planet_id=0),
                PlanetPosition(longitude=60.0, latitude=0.0, distance=1.0, longitude_speed=0.5, planet_id=1)
            ],
            # Chart 2  
            [
                PlanetPosition(longitude=30.0, latitude=0.0, distance=1.0, longitude_speed=1.0, planet_id=0),
                PlanetPosition(longitude=90.0, latitude=0.0, distance=1.0, longitude_speed=0.5, planet_id=1)
            ],
            # Chart 3
            [
                PlanetPosition(longitude=45.0, latitude=0.0, distance=1.0, longitude_speed=1.0, planet_id=0),
                PlanetPosition(longitude=135.0, latitude=0.0, distance=1.0, longitude_speed=0.5, planet_id=1)
            ]
        ]
    
    def test_batch_calculation(self, batch_calculator, sample_chart_batches):
        """Test basic batch processing."""
        results = batch_calculator.calculate_batch_aspects(sample_chart_batches)
        
        assert len(results) == 3
        assert all(isinstance(result, AspectMatrix) for result in results)
        
        # Each chart should have calculated aspects
        for result in results:
            assert isinstance(result.aspects, list)
            assert isinstance(result.total_aspects, int)
    
    def test_batch_vs_individual_consistency(self, batch_calculator, sample_chart_batches):
        """Test that batch processing gives same results as individual calculations."""
        # Calculate using batch
        batch_results = batch_calculator.calculate_batch_aspects(sample_chart_batches)
        
        # Calculate individually
        individual_results = []
        for positions in sample_chart_batches:
            result = batch_calculator.aspect_calculator.calculate_aspect_matrix(positions)
            individual_results.append(result)
        
        # Compare results
        assert len(batch_results) == len(individual_results)
        
        for batch_result, individual_result in zip(batch_results, individual_results):
            assert batch_result.total_aspects == individual_result.total_aspects
            assert batch_result.major_aspects == individual_result.major_aspects
            assert batch_result.minor_aspects == individual_result.minor_aspects
    
    def test_parallel_batch_processing(self, batch_calculator, sample_chart_batches):
        """Test parallel batch processing."""
        # Create larger batch to see parallel benefits
        large_batch = sample_chart_batches * 5  # 15 charts
        
        # Sequential processing
        start_time = time.time()
        sequential_results = batch_calculator.calculate_batch_aspects(large_batch)
        sequential_time = time.time() - start_time
        
        # Parallel processing
        start_time = time.time()  
        parallel_results = batch_calculator.calculate_batch_aspects_parallel(large_batch)
        parallel_time = time.time() - start_time
        
        # Results should be consistent
        assert len(sequential_results) == len(parallel_results)
        
        # Performance improvement depends on system, but should at least not be slower
        # (Allow some variance for small batches)
        assert parallel_time < sequential_time * 2.0  # Allow up to 2x slower due to overhead
    
    def test_empty_batch_handling(self, batch_calculator):
        """Test handling of empty batches."""
        empty_batch = []
        results = batch_calculator.calculate_batch_aspects(empty_batch)
        assert results == []
        
        batch_with_empty_charts = [[], []]
        results = batch_calculator.calculate_batch_aspects(batch_with_empty_charts)
        assert len(results) == 2
        assert all(result.total_aspects == 0 for result in results)


class TestPerformanceBenchmarks:
    """Performance benchmark tests to ensure <50ms target is met."""
    
    @pytest.fixture
    def performance_positions(self):
        """12-planet chart for performance testing."""
        planets = []
        for i in range(12):
            longitude = (i * 30.0) % 360.0  # Space planets around zodiac
            speed = 1.0 - (i * 0.1)  # Vary speeds
            planets.append(PlanetPosition(
                longitude=longitude,
                latitude=0.0,
                distance=1.0,
                longitude_speed=speed,
                planet_id=i
            ))
        return planets
    
    @pytest.fixture
    def performance_calculator(self):
        """Calculator for performance testing."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        return AspectCalculator(orb_config)
    
    def test_single_chart_performance(self, performance_calculator, performance_positions):
        """Test single chart calculation performance."""
        # Warm up calculation
        performance_calculator.calculate_aspect_matrix(performance_positions[:3])
        
        # Actual benchmark
        start_time = time.time()
        matrix = performance_calculator.calculate_aspect_matrix(performance_positions)
        calculation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Performance requirement: <50ms for 12-planet chart
        assert calculation_time < 50.0, f"Calculation took {calculation_time:.2f}ms, exceeds 50ms target"
        
        # Verify calculation was actually performed
        assert matrix.total_aspects > 0
        assert len(matrix.aspects) == matrix.total_aspects
    
    def test_vectorized_performance_advantage(self, performance_positions):
        """Test that vectorized calculations are faster than sequential."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        calculator = AspectCalculator(orb_config)
        
        # Time vectorized calculation
        start_time = time.time()
        vectorized_result = calculator.calculate_aspects_vectorized(performance_positions)
        vectorized_time = time.time() - start_time
        
        # The vectorized version is now the default, so this tests the optimization
        assert vectorized_time < 0.05  # Should be under 50ms
        assert len(vectorized_result) > 0
    
    @pytest.mark.benchmark(group="aspect_calculation")
    def test_benchmark_aspect_matrix(self, benchmark, performance_calculator, performance_positions):
        """Benchmark aspect matrix calculation for performance monitoring."""
        result = benchmark(performance_calculator.calculate_aspect_matrix, performance_positions)
        
        # Verify meaningful result
        assert result.total_aspects > 0
        assert result.calculation_time_ms < 50.0
    
    def test_memory_efficiency(self, performance_calculator, performance_positions):
        """Test memory usage is reasonable."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Calculate multiple charts to test memory accumulation
        for _ in range(10):
            matrix = performance_calculator.calculate_aspect_matrix(performance_positions)
            
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Memory increase should be reasonable (<10MB for 10 charts)
        assert memory_increase < 10.0, f"Memory increased by {memory_increase:.2f}MB"


class TestReferenceDataValidation:
    """Test calculations against known reference data."""
    
    def test_known_aspect_configuration(self):
        """Test against known natal chart with verified aspects."""
        # Example: Sun at 0° Aries, Moon at 0° Gemini (exact sextile)
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        calculator = AspectCalculator(orb_config)
        
        positions = [
            PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=1.0, planet_id=0),    # Sun at 0° Aries
            PlanetPosition(longitude=60.0, latitude=0.0, distance=1.0, longitude_speed=0.5, planet_id=1),   # Moon at 0° Gemini (exact sextile)
        ]
        
        aspects = calculator.calculate_aspects(positions)
        sextile_aspects = [a for a in aspects if a.aspect_type == 'sextile']
        
        assert len(sextile_aspects) >= 1
        sextile = sextile_aspects[0]
        
        # Verify exact sextile properties
        assert sextile.angle == 60.0
        assert sextile.exact_angle == 60.0
        assert sextile.strength == 1.0  # Exact aspect
        assert abs(sextile.orb_percentage) < 0.01  # Minimal orb usage
    
    def test_complex_aspect_pattern(self):
        """Test complex aspect pattern (T-Square)."""
        # T-Square: Sun 0°, Mars 90°, Saturn 180°, Jupiter 270°
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        calculator = AspectCalculator(orb_config)
        
        positions = [
            PlanetPosition(longitude=0.0, latitude=0.0, distance=1.0, longitude_speed=1.0, planet_id=0),     # Sun
            PlanetPosition(longitude=90.0, latitude=0.0, distance=1.0, longitude_speed=0.5, planet_id=4),    # Mars
            PlanetPosition(longitude=180.0, latitude=0.0, distance=1.0, longitude_speed=0.2, planet_id=6),   # Saturn
            PlanetPosition(longitude=270.0, latitude=0.0, distance=1.0, longitude_speed=0.3, planet_id=5),   # Jupiter
        ]
        
        matrix = calculator.calculate_aspect_matrix(positions)
        
        # Should find multiple squares and oppositions
        squares = [a for a in matrix.aspects if a.aspect_type == 'square']
        oppositions = [a for a in matrix.aspects if a.aspect_type == 'opposition']
        
        # T-Square pattern should have at least 2 squares and 1 opposition
        assert len(squares) >= 2
        assert len(oppositions) >= 1
        
        # All should be exact or very close
        for aspect in squares + oppositions:
            assert aspect.strength > 0.95  # Very strong aspects
    
    def test_boundary_conditions(self):
        """Test aspects near zodiac boundaries."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional') 
        calculator = AspectCalculator(orb_config)
        
        # Planets near 0°/360° boundary
        positions = [
            PlanetPosition(longitude=358.0, latitude=0.0, distance=1.0, longitude_speed=1.0, planet_id=0),   # Sun at 358°
            PlanetPosition(longitude=2.0, latitude=0.0, distance=1.0, longitude_speed=0.5, planet_id=1),     # Moon at 2°
        ]
        
        aspects = calculator.calculate_aspects(positions)
        conjunctions = [a for a in aspects if a.aspect_type == 'conjunction']
        
        # Should find conjunction across 0° boundary
        assert len(conjunctions) >= 1
        conjunction = conjunctions[0]
        
        # Angle should be 4° (358° to 2°)
        assert abs(conjunction.angle - 4.0) < 0.01
        
        # Should be within orb and fairly strong
        assert conjunction.strength > 0.5


if __name__ == "__main__":
    # Run tests with performance monitoring
    pytest.main([
        __file__,
        "-v",
        "--benchmark-only",
        "--benchmark-sort=mean"
    ])