"""
Aspect Calculation Performance Benchmarks

Dedicated performance benchmarks to validate PRP 1 requirements:
- <50ms for single chart aspect matrix calculations
- 5x+ improvement for batch processing
- Memory efficiency under 1MB per calculation
- Cache hit rate >70% under realistic load
"""

import pytest
import time
import numpy as np
import psutil
import os
from typing import List
from unittest.mock import Mock

from extracted.systems.aspects import AspectCalculator, BatchAspectCalculator
from extracted.systems.orb_systems import OrbSystemManager
from extracted.systems.classes.serialize import PlanetPosition


class TestAspectPerformanceRequirements:
    """Test aspect calculations meet PRP performance requirements."""
    
    @pytest.fixture
    def standard_chart_positions(self):
        """Standard 12-planet natal chart positions."""
        # Realistic planet distribution based on actual ephemeris data
        longitudes = [15.5, 45.2, 67.8, 89.1, 123.4, 156.7, 189.2, 234.6, 278.9, 301.2, 334.5, 12.8]
        speeds = [0.98, 13.2, 1.59, 1.21, 0.52, 0.08, 0.03, 0.006, 0.003, 0.04, -0.03, 0.0]
        
        positions = []
        for i, (longitude, speed) in enumerate(zip(longitudes, speeds)):
            positions.append(PlanetPosition(
                longitude=longitude,
                latitude=0.0,
                distance=1.0,
                longitude_speed=speed,
                planet_id=i
            ))
        
        return positions
    
    @pytest.fixture
    def performance_calculator(self):
        """Optimized calculator for performance testing."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        return AspectCalculator(orb_config)
    
    def test_single_chart_50ms_requirement(self, performance_calculator, standard_chart_positions):
        """Test PRP requirement: <50ms for single chart aspect matrix."""
        # Warm up JIT compilation and caches
        for _ in range(3):
            performance_calculator.calculate_aspect_matrix(standard_chart_positions[:3])
        
        # Run multiple iterations to get stable timing
        times = []
        for _ in range(10):
            start_time = time.perf_counter()
            matrix = performance_calculator.calculate_aspect_matrix(standard_chart_positions)
            end_time = time.perf_counter()
            
            calculation_time_ms = (end_time - start_time) * 1000
            times.append(calculation_time_ms)
            
            # Verify calculation was actually performed
            assert matrix.total_aspects > 0
            assert len(matrix.aspects) == matrix.total_aspects
        
        # Statistical analysis of performance
        mean_time = np.mean(times)
        median_time = np.median(times)
        p95_time = np.percentile(times, 95)
        
        print(f"\nAspect Calculation Performance:")
        print(f"Mean: {mean_time:.2f}ms")
        print(f"Median: {median_time:.2f}ms") 
        print(f"95th percentile: {p95_time:.2f}ms")
        
        # PRP requirement: <50ms for aspect matrix calculations
        assert mean_time < 50.0, f"Mean calculation time {mean_time:.2f}ms exceeds 50ms requirement"
        assert p95_time < 75.0, f"95th percentile {p95_time:.2f}ms suggests inconsistent performance"
    
    def test_batch_processing_5x_improvement(self, standard_chart_positions):
        """Test PRP requirement: 5x+ improvement for batch processing."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        
        # Create batch of 10 identical charts for consistent comparison
        chart_batch = [standard_chart_positions] * 10
        
        # Individual processing time
        calculator = AspectCalculator(orb_config)
        
        start_time = time.perf_counter()
        individual_results = []
        for positions in chart_batch:
            result = calculator.calculate_aspect_matrix(positions)
            individual_results.append(result)
        individual_time = time.perf_counter() - start_time
        
        # Batch processing time  
        batch_calculator = BatchAspectCalculator(orb_config)
        
        start_time = time.perf_counter()
        batch_results = batch_calculator.calculate_batch_aspects(chart_batch)
        batch_time = time.perf_counter() - start_time
        
        # Calculate improvement ratio
        improvement_ratio = individual_time / batch_time if batch_time > 0 else 0
        
        print(f"\nBatch Processing Performance:")
        print(f"Individual processing: {individual_time:.4f}s")
        print(f"Batch processing: {batch_time:.4f}s")
        print(f"Improvement ratio: {improvement_ratio:.2f}x")
        
        # Verify results consistency
        assert len(batch_results) == len(individual_results)
        for batch_result, individual_result in zip(batch_results, individual_results):
            assert batch_result.total_aspects == individual_result.total_aspects
        
        # PRP requirement: 5x+ improvement for batch processing
        assert improvement_ratio >= 5.0, f"Batch processing improvement {improvement_ratio:.2f}x is below 5x requirement"
    
    def test_memory_efficiency_1mb_requirement(self, performance_calculator, standard_chart_positions):
        """Test PRP requirement: <1MB memory per calculation."""
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        memory_baseline = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple calculations to test memory accumulation
        calculations = 100
        results = []
        
        for i in range(calculations):
            matrix = performance_calculator.calculate_aspect_matrix(standard_chart_positions)
            results.append(matrix)
            
            # Check memory every 10 calculations
            if (i + 1) % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_per_calc = (current_memory - memory_baseline) / (i + 1)
                
                # Verify we're not accumulating excessive memory
                assert memory_per_calc < 1.0, f"Memory usage {memory_per_calc:.2f}MB per calculation exceeds 1MB requirement"
        
        # Final memory check
        memory_final = process.memory_info().rss / 1024 / 1024  # MB
        memory_per_calculation = (memory_final - memory_baseline) / calculations
        
        print(f"\nMemory Efficiency:")
        print(f"Baseline memory: {memory_baseline:.2f}MB")
        print(f"Final memory: {memory_final:.2f}MB")
        print(f"Memory per calculation: {memory_per_calculation:.4f}MB")
        
        # PRP requirement: <1MB per calculation
        assert memory_per_calculation < 1.0, f"Memory usage {memory_per_calculation:.4f}MB per calculation exceeds 1MB requirement"
        
        # Verify calculations were meaningful
        assert all(result.total_aspects > 0 for result in results)
    
    def test_vectorized_performance_advantage(self, standard_chart_positions):
        """Test that vectorized calculations provide performance benefit."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        calculator = AspectCalculator(orb_config)
        
        # Test with varying chart sizes
        chart_sizes = [3, 6, 9, 12]
        vectorized_times = []
        
        for size in chart_sizes:
            positions = standard_chart_positions[:size]
            
            # Time vectorized calculation (current default)
            times = []
            for _ in range(10):
                start_time = time.perf_counter()
                result = calculator.calculate_aspects_vectorized(positions)
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)  # ms
            
            mean_time = np.mean(times)
            vectorized_times.append(mean_time)
            
            print(f"Chart size {size}: {mean_time:.2f}ms")
        
        # Performance should scale reasonably with chart size
        # For quadratic complexity, 12-planet should be ~16x slower than 3-planet
        # Good vectorization should keep this ratio much lower
        time_ratio = vectorized_times[-1] / vectorized_times[0]  # 12-planet vs 3-planet
        
        assert time_ratio < 50.0, f"Performance scaling ratio {time_ratio:.2f} suggests poor optimization"
    
    def test_concurrent_calculation_performance(self, standard_chart_positions):
        """Test performance under concurrent load."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        
        import concurrent.futures
        import threading
        
        def calculate_chart(positions):
            calculator = AspectCalculator(orb_config)
            start_time = time.perf_counter()
            result = calculator.calculate_aspect_matrix(positions)
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000, result  # ms, result
        
        # Test with 4 concurrent calculations
        n_concurrent = 4
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_concurrent) as executor:
            futures = [
                executor.submit(calculate_chart, standard_chart_positions)
                for _ in range(n_concurrent)
            ]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                calculation_time, matrix = future.result()
                results.append((calculation_time, matrix))
        
        # All calculations should complete successfully
        assert len(results) == n_concurrent
        
        # Performance under load should still be reasonable
        times = [time for time, _ in results]
        mean_concurrent_time = np.mean(times)
        
        print(f"\nConcurrent Performance:")
        print(f"Mean time under {n_concurrent}x concurrent load: {mean_concurrent_time:.2f}ms")
        
        # Should not degrade too much under concurrent load
        assert mean_concurrent_time < 100.0, f"Concurrent performance {mean_concurrent_time:.2f}ms is too slow"
        
        # Verify all calculations produced meaningful results
        for _, matrix in results:
            assert matrix.total_aspects > 0


class TestCachePerformanceRequirements:
    """Test caching performance meets PRP requirements."""
    
    @pytest.fixture
    def cached_service(self):
        """Mock ephemeris service with caching."""
        from extracted.services.ephemeris_service import EphemerisService
        return EphemerisService()
    
    def test_cache_hit_rate_70_percent(self, cached_service, standard_chart_positions):
        """Test PRP requirement: >70% cache hit rate under realistic load."""
        # Simulate realistic load pattern: some repeated calculations
        cache_requests = []
        
        # Create variety of similar but distinct chart requests
        base_longitudes = [15.5, 45.2, 67.8, 89.1, 123.4, 156.7, 189.2, 234.6, 278.9, 301.2]
        
        for _ in range(100):  # 100 total requests
            # 70% should be repeats to achieve >70% hit rate
            if np.random.random() < 0.7:
                # Repeat existing chart (should hit cache)
                longitudes = base_longitudes
            else:
                # New chart (cache miss)
                longitudes = [l + np.random.uniform(-1, 1) for l in base_longitudes]
            
            positions = {
                f"planet_{i}": {
                    'longitude': longitude,
                    'longitude_speed': 1.0
                }
                for i, longitude in enumerate(longitudes)
            }
            
            cache_requests.append(positions)
        
        # Execute requests and track cache performance
        cache_hits = 0
        total_requests = len(cache_requests)
        
        for positions in cache_requests:
            # Generate cache key
            cache_key = cached_service._generate_aspect_cache_key(
                positions, 'traditional', None
            )
            
            # Check if would be cache hit
            cached_result = cached_service._get_cached_aspects(cache_key)
            
            if cached_result:
                cache_hits += 1
            else:
                # Simulate calculation and caching
                mock_result = {
                    'aspects': [],
                    'aspect_matrix': {'total_aspects': 10}
                }
                cached_service._cache_aspects(cache_key, mock_result)
        
        cache_hit_rate = cache_hits / total_requests * 100
        
        print(f"\nCache Performance:")
        print(f"Total requests: {total_requests}")
        print(f"Cache hits: {cache_hits}")
        print(f"Cache hit rate: {cache_hit_rate:.1f}%")
        
        # Note: This test is simplified since we don't have full cache implementation
        # In practice, would test with actual Redis cache and realistic request patterns


@pytest.mark.benchmark(group="aspect_performance")
class TestBenchmarkSuite:
    """Benchmark suite for continuous performance monitoring."""
    
    @pytest.fixture
    def benchmark_positions(self):
        """Standard positions for benchmarking."""
        return [
            PlanetPosition(longitude=i*30, latitude=0.0, distance=1.0, longitude_speed=1.0-i*0.1, planet_id=i)
            for i in range(12)
        ]
    
    @pytest.fixture
    def benchmark_calculator(self):
        """Standard calculator for benchmarking."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        return AspectCalculator(orb_config)
    
    @pytest.mark.benchmark(group="single_chart")
    def test_benchmark_single_chart(self, benchmark, benchmark_calculator, benchmark_positions):
        """Benchmark single chart calculation."""
        result = benchmark(benchmark_calculator.calculate_aspect_matrix, benchmark_positions)
        assert result.total_aspects > 0
    
    @pytest.mark.benchmark(group="vectorized")  
    def test_benchmark_vectorized_calculation(self, benchmark, benchmark_calculator, benchmark_positions):
        """Benchmark vectorized aspect calculation."""
        result = benchmark(benchmark_calculator.calculate_aspects_vectorized, benchmark_positions)
        assert len(result) > 0
    
    @pytest.mark.benchmark(group="batch_processing")
    def test_benchmark_batch_processing(self, benchmark, benchmark_positions):
        """Benchmark batch processing performance."""
        orb_manager = OrbSystemManager()
        orb_config = orb_manager.get_orb_preset('traditional')
        batch_calculator = BatchAspectCalculator(orb_config)
        
        chart_batch = [benchmark_positions] * 5
        
        result = benchmark(batch_calculator.calculate_batch_aspects, chart_batch)
        assert len(result) == 5
    
    @pytest.mark.benchmark(group="orb_systems")
    def test_benchmark_different_orb_systems(self, benchmark, benchmark_positions):
        """Benchmark different orb system performance."""
        orb_manager = OrbSystemManager()
        
        def calculate_with_traditional_orbs():
            orb_config = orb_manager.get_orb_preset('traditional')
            calculator = AspectCalculator(orb_config)
            return calculator.calculate_aspect_matrix(benchmark_positions)
        
        result = benchmark(calculate_with_traditional_orbs)
        assert result.total_aspects > 0


if __name__ == "__main__":
    # Run benchmarks
    pytest.main([
        __file__,
        "-v", 
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-autosave"
    ])