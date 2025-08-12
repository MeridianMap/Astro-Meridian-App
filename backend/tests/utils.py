"""
Test utilities for Meridian Ephemeris Engine validation.

Provides common assertion helpers, fixture loading, and comparison utilities
for accurate validation of astrological calculations.
"""

import json
import math
import os
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple
from datetime import datetime

import pytest


# Constants for angular comparisons
ARCSECONDS_PER_DEGREE = 3600
DEFAULT_ANGLE_TOLERANCE = 3.0  # 3 arcseconds as per PRP 5 requirement
DEFAULT_DISTANCE_TOLERANCE = 1e-6
DEFAULT_SPEED_TOLERANCE = 1e-6


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to 0-360 degree range.
    
    Args:
        angle: Angle in degrees
        
    Returns:
        Normalized angle in 0-360 range
    """
    return angle % 360.0


def angular_difference(angle1: float, angle2: float) -> float:
    """
    Calculate the smallest angular difference between two angles.
    
    Args:
        angle1: First angle in degrees
        angle2: Second angle in degrees
        
    Returns:
        Angular difference in degrees (0-180)
    """
    diff = abs(normalize_angle(angle1) - normalize_angle(angle2))
    return min(diff, 360.0 - diff)


def degrees_to_arcseconds(degrees: float) -> float:
    """
    Convert degrees to arcseconds.
    
    Args:
        degrees: Angle in degrees
        
    Returns:
        Angle in arcseconds
    """
    return degrees * ARCSECONDS_PER_DEGREE


def arcseconds_to_degrees(arcseconds: float) -> float:
    """
    Convert arcseconds to degrees.
    
    Args:
        arcseconds: Angle in arcseconds
        
    Returns:
        Angle in degrees
    """
    return arcseconds / ARCSECONDS_PER_DEGREE


def assert_angle_close(
    actual: float, 
    expected: float, 
    tolerance_arcsec: float = DEFAULT_ANGLE_TOLERANCE,
    msg: Optional[str] = None
) -> None:
    """
    Assert that two angles are within specified tolerance.
    
    Args:
        actual: Actual angle in degrees
        expected: Expected angle in degrees
        tolerance_arcsec: Tolerance in arcseconds (default: 3)
        msg: Optional custom error message
        
    Raises:
        AssertionError: If angles differ by more than tolerance
    """
    diff_degrees = angular_difference(actual, expected)
    diff_arcsec = degrees_to_arcseconds(diff_degrees)
    
    if diff_arcsec > tolerance_arcsec:
        error_msg = (
            f"Angular difference {diff_arcsec:.3f}\" exceeds tolerance {tolerance_arcsec}\" "
            f"(actual: {actual:.6f}°, expected: {expected:.6f}°, diff: {diff_degrees:.6f}°)"
        )
        if msg:
            error_msg = f"{msg}: {error_msg}"
        raise AssertionError(error_msg)


def assert_distance_close(
    actual: float,
    expected: float, 
    tolerance: float = DEFAULT_DISTANCE_TOLERANCE,
    msg: Optional[str] = None
) -> None:
    """
    Assert that two distance values are within tolerance.
    
    Args:
        actual: Actual distance value
        expected: Expected distance value
        tolerance: Tolerance for comparison
        msg: Optional custom error message
        
    Raises:
        AssertionError: If distances differ by more than tolerance
    """
    diff = abs(actual - expected)
    if diff > tolerance:
        error_msg = (
            f"Distance difference {diff:.8f} exceeds tolerance {tolerance} "
            f"(actual: {actual:.8f}, expected: {expected:.8f})"
        )
        if msg:
            error_msg = f"{msg}: {error_msg}"
        raise AssertionError(error_msg)


def assert_speed_close(
    actual: float,
    expected: float,
    tolerance: float = DEFAULT_SPEED_TOLERANCE,
    msg: Optional[str] = None
) -> None:
    """
    Assert that two speed values are within tolerance.
    
    Args:
        actual: Actual speed value
        expected: Expected speed value  
        tolerance: Tolerance for comparison
        msg: Optional custom error message
        
    Raises:
        AssertionError: If speeds differ by more than tolerance
    """
    diff = abs(actual - expected)
    if diff > tolerance:
        error_msg = (
            f"Speed difference {diff:.8f} exceeds tolerance {tolerance} "
            f"(actual: {actual:.8f}, expected: {expected:.8f})"
        )
        if msg:
            error_msg = f"{msg}: {error_msg}"
        raise AssertionError(error_msg)


def assert_vec_close(
    actual: List[float],
    expected: List[float],
    tolerance: Union[float, List[float]] = DEFAULT_DISTANCE_TOLERANCE,
    msg: Optional[str] = None
) -> None:
    """
    Assert that two vectors are within tolerance component-wise.
    
    Args:
        actual: Actual vector values
        expected: Expected vector values
        tolerance: Single tolerance or per-component tolerances
        msg: Optional custom error message
        
    Raises:
        AssertionError: If vectors differ by more than tolerance
    """
    if len(actual) != len(expected):
        raise AssertionError(f"Vector lengths differ: {len(actual)} vs {len(expected)}")
    
    if isinstance(tolerance, (int, float)):
        tolerances = [tolerance] * len(actual)
    else:
        tolerances = tolerance
        
    if len(tolerances) != len(actual):
        raise AssertionError(f"Tolerance length {len(tolerances)} doesn't match vector length {len(actual)}")
    
    for i, (a, e, t) in enumerate(zip(actual, expected, tolerances)):
        diff = abs(a - e)
        if diff > t:
            error_msg = (
                f"Component {i} difference {diff:.8f} exceeds tolerance {t} "
                f"(actual[{i}]: {a:.8f}, expected[{i}]: {e:.8f})"
            )
            if msg:
                error_msg = f"{msg}: {error_msg}"
            raise AssertionError(error_msg)


def assert_planet_position_close(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    angle_tolerance_arcsec: float = DEFAULT_ANGLE_TOLERANCE,
    distance_tolerance: float = DEFAULT_DISTANCE_TOLERANCE,
    speed_tolerance: float = DEFAULT_SPEED_TOLERANCE
) -> None:
    """
    Assert that two planet positions are within tolerances.
    
    Args:
        actual: Actual planet position data
        expected: Expected planet position data
        angle_tolerance_arcsec: Angular tolerance in arcseconds
        distance_tolerance: Distance tolerance
        speed_tolerance: Speed tolerance
    """
    # Check longitude
    if 'longitude' in expected:
        assert 'longitude' in actual, "Missing longitude in actual data"
        assert_angle_close(
            actual['longitude'], 
            expected['longitude'], 
            angle_tolerance_arcsec,
            "Planet longitude"
        )
    
    # Check latitude
    if 'latitude' in expected:
        assert 'latitude' in actual, "Missing latitude in actual data"
        assert_angle_close(
            actual['latitude'], 
            expected['latitude'], 
            angle_tolerance_arcsec,
            "Planet latitude"
        )
    
    # Check distance
    if 'distance' in expected:
        assert 'distance' in actual, "Missing distance in actual data"
        assert_distance_close(
            actual['distance'], 
            expected['distance'], 
            distance_tolerance,
            "Planet distance"
        )
    
    # Check speeds
    for speed_key in ['longitude_speed', 'latitude_speed', 'distance_speed']:
        if speed_key in expected:
            assert speed_key in actual, f"Missing {speed_key} in actual data"
            assert_speed_close(
                actual[speed_key], 
                expected[speed_key], 
                speed_tolerance,
                f"Planet {speed_key}"
            )


def load_fixture(fixture_name: str) -> Dict[str, Any]:
    """
    Load a test fixture from the fixtures directory.
    
    Args:
        fixture_name: Name of fixture file (without .json extension)
        
    Returns:
        Loaded fixture data
        
    Raises:
        FileNotFoundError: If fixture file doesn't exist
        json.JSONDecodeError: If fixture is not valid JSON
    """
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    fixture_path = test_dir / "fixtures" / f"{fixture_name}.json"
    
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
    
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_fixture(data: Dict[str, Any], fixture_name: str) -> None:
    """
    Save data as a test fixture.
    
    Args:
        data: Data to save
        fixture_name: Name of fixture file (without .json extension)
    """
    # Get the directory containing this file
    test_dir = Path(__file__).parent
    fixtures_dir = test_dir / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    
    fixture_path = fixtures_dir / f"{fixture_name}.json"
    
    with open(fixture_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def create_test_subject_data(
    name: str = "Test Subject",
    datetime_iso: str = "2000-01-01T12:00:00",
    latitude: float = 40.7128,
    longitude: float = -74.0060,
    timezone: str = "America/New_York",
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized test subject data.
    
    Args:
        name: Subject name
        datetime_iso: ISO datetime string
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        timezone: Timezone name
        **kwargs: Additional subject parameters
        
    Returns:
        Subject data dictionary
    """
    return {
        "name": name,
        "datetime": {"iso_string": datetime_iso},
        "latitude": {"decimal": latitude},
        "longitude": {"decimal": longitude},
        "timezone": {"name": timezone},
        **kwargs
    }


def create_chart_test_case(
    name: str,
    subject_data: Dict[str, Any],
    expected_results: Optional[Dict[str, Any]] = None,
    configuration: Optional[Dict[str, Any]] = None,
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a standardized chart test case.
    
    Args:
        name: Test case name
        subject_data: Subject birth data
        expected_results: Expected calculation results
        configuration: Chart configuration options
        description: Test case description
        
    Returns:
        Complete test case data
    """
    return {
        "name": name,
        "description": description,
        "subject": subject_data,
        "configuration": configuration or {},
        "expected": expected_results or {},
        "metadata": {
            "created": datetime.now().isoformat(),
            "tolerance_arcsec": DEFAULT_ANGLE_TOLERANCE
        }
    }


class PerformanceTracker:
    """Track performance metrics during testing."""
    
    def __init__(self):
        self.measurements = []
    
    def measure(self, operation: str, duration: float, **metadata):
        """Record a performance measurement."""
        self.measurements.append({
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            **metadata
        })
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        measurements = self.measurements
        if operation:
            measurements = [m for m in measurements if m["operation"] == operation]
        
        if not measurements:
            return {}
        
        durations = [m["duration"] for m in measurements]
        return {
            "count": len(durations),
            "total": sum(durations),
            "mean": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "measurements": measurements
        }
    
    def save_report(self, filename: str):
        """Save performance report to file."""
        test_dir = Path(__file__).parent
        reports_dir = test_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": self.get_stats(),
                "by_operation": {
                    op: self.get_stats(op) 
                    for op in set(m["operation"] for m in self.measurements)
                },
                "all_measurements": self.measurements
            }, f, indent=2)


# Pytest fixtures for common test utilities
@pytest.fixture
def performance_tracker():
    """Provide a performance tracker for tests."""
    return PerformanceTracker()


@pytest.fixture
def test_subject_data():
    """Provide standard test subject data."""
    return create_test_subject_data()


@pytest.fixture
def chart_test_case():
    """Provide a chart test case factory."""
    return create_chart_test_case