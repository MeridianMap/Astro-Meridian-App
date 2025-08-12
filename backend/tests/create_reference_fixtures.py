"""
Create reference fixtures from Immanuel for validation.

This script generates reference test data using the Immanuel library
to validate our Meridian Ephemeris implementation.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the immanuel directory to the path
sys.path.insert(0, str(Path(__file__).parents[2] / "immanuel-python"))

try:
    import immanuel
    from immanuel import charts
    from immanuel.tools import convert, date as imm_date
    IMMANUEL_AVAILABLE = True
except ImportError as e:
    print(f"Immanuel not available: {e}")
    IMMANUEL_AVAILABLE = False


def create_test_cases() -> List[Dict[str, Any]]:
    """Create standard test cases for validation."""
    return [
        {
            "name": "basic_natal_chart",
            "description": "Basic natal chart calculation",
            "subject": {
                "name": "Test Subject",
                "datetime": "2000-01-01T12:00:00",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        },
        {
            "name": "london_birth",
            "description": "Birth in London, UK",
            "subject": {
                "name": "London Test",
                "datetime": "1990-06-15T14:30:00",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "timezone": "Europe/London"
            }
        },
        {
            "name": "southern_hemisphere",
            "description": "Southern hemisphere birth",
            "subject": {
                "name": "Sydney Test",
                "datetime": "1985-12-25T18:00:00",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "timezone": "Australia/Sydney"
            }
        },
        {
            "name": "high_latitude",
            "description": "High latitude birth (close to polar circle)",
            "subject": {
                "name": "Reykjavik Test",
                "datetime": "2000-06-21T12:00:00",  # Summer solstice
                "latitude": 64.1466,
                "longitude": -21.9426,
                "timezone": "Atlantic/Reykjavik"
            }
        },
        {
            "name": "leap_year",
            "description": "Leap year birth",
            "subject": {
                "name": "Leap Year Test",
                "datetime": "2000-02-29T12:00:00",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC"
            }
        },
        {
            "name": "dst_transition",
            "description": "Birth during DST transition",
            "subject": {
                "name": "DST Test",
                "datetime": "2023-03-12T02:30:00",  # DST spring forward
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York"
            }
        },
        {
            "name": "j2000_epoch",
            "description": "J2000.0 epoch for reference",
            "subject": {
                "name": "J2000 Reference",
                "datetime": "2000-01-01T12:00:00",
                "latitude": 0.0,
                "longitude": 0.0,
                "timezone": "UTC"
            }
        },
        {
            "name": "historical_date",
            "description": "Historical date within ephemeris range",
            "subject": {
                "name": "Historical Test",
                "datetime": "1900-01-01T12:00:00",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "timezone": "Europe/Paris"
            }
        }
    ]


def create_immanuel_chart(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create chart using Immanuel library.
    
    Args:
        test_case: Test case data
        
    Returns:
        Chart data in Immanuel format
    """
    if not IMMANUEL_AVAILABLE:
        return {}
    
    subject_data = test_case["subject"]
    
    try:
        # Create Immanuel chart
        chart = charts.Natal(
            dt=subject_data["datetime"],
            lat=subject_data["latitude"],
            lon=subject_data["longitude"],
            tz=subject_data["timezone"]
        )
        
        # Extract relevant data
        result = {
            "name": test_case["name"],
            "description": test_case["description"],
            "input": subject_data,
            "immanuel_data": {
                "planets": {},
                "houses": {},
                "angles": {},
                "metadata": {
                    "julian_day": chart.julian_day,
                    "sidereal_time": getattr(chart, 'sidereal_time', None),
                    "obliquity": getattr(chart, 'obliquity', None)
                }
            }
        }
        
        # Extract planet positions
        if hasattr(chart, 'objects'):
            for obj_name, obj_data in chart.objects.items():
                if hasattr(obj_data, 'lon') and hasattr(obj_data, 'lat'):
                    result["immanuel_data"]["planets"][obj_name] = {
                        "longitude": float(obj_data.lon),
                        "latitude": float(obj_data.lat),
                        "distance": float(getattr(obj_data, 'distance', 0.0)),
                        "longitude_speed": float(getattr(obj_data, 'speed', 0.0)),
                        "sign": getattr(obj_data, 'sign', None),
                        "decan": getattr(obj_data, 'decan', None)
                    }
        
        # Extract house data
        if hasattr(chart, 'houses'):
            house_cusps = []
            for i in range(1, 13):
                if hasattr(chart.houses, f'house_{i}'):
                    house = getattr(chart.houses, f'house_{i}')
                    house_cusps.append(float(getattr(house, 'lon', 0.0)))
            
            result["immanuel_data"]["houses"] = {
                "cusps": house_cusps,
                "system": getattr(chart.houses, 'system', 'Placidus')
            }
        
        # Extract angles
        if hasattr(chart, 'angles'):
            result["immanuel_data"]["angles"] = {
                "ascendant": float(getattr(chart.angles, 'asc', 0.0)),
                "midheaven": float(getattr(chart.angles, 'mc', 0.0)),
                "descendant": float(getattr(chart.angles, 'desc', 0.0)),
                "imum_coeli": float(getattr(chart.angles, 'ic', 0.0))
            }
        
        return result
        
    except Exception as e:
        print(f"Error creating Immanuel chart for {test_case['name']}: {e}")
        return {
            "name": test_case["name"],
            "error": str(e),
            "input": subject_data
        }


def create_simple_reference_fixtures():
    """Create simple reference fixtures without Immanuel dependency."""
    print("Creating simple reference fixtures without Immanuel...")
    
    # Use known astronomical data for basic validation
    fixtures = {
        "basic_positions": {
            "description": "Known planetary positions for validation",
            "test_cases": [
                {
                    "name": "j2000_reference",
                    "julian_day": 2451545.0,  # J2000.0
                    "datetime": "2000-01-01T12:00:00+00:00",
                    "location": {"latitude": 0.0, "longitude": 0.0},
                    "expected_positions": {
                        # These are approximate positions at J2000.0
                        "sun": {"longitude": 280.0, "tolerance": 5.0},
                        "moon": {"longitude": 218.0, "tolerance": 10.0},
                        "mercury": {"longitude": 277.0, "tolerance": 10.0},
                        "venus": {"longitude": 324.0, "tolerance": 5.0},
                        "mars": {"longitude": 327.0, "tolerance": 5.0}
                    }
                }
            ]
        },
        "house_systems": {
            "description": "House system test cases",
            "test_cases": [
                {
                    "name": "placidus_london",
                    "datetime": "2000-01-01T12:00:00",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "house_system": "Placidus",
                    "expected": {
                        "asc_range": [260.0, 280.0],  # Expected range for ascendant
                        "mc_range": [170.0, 190.0]    # Expected range for midheaven
                    }
                }
            ]
        },
        "edge_cases": {
            "description": "Edge case scenarios for testing",
            "test_cases": [
                {
                    "name": "high_latitude_summer",
                    "description": "High latitude during summer solstice",
                    "datetime": "2000-06-21T12:00:00",
                    "latitude": 66.0,  # Above Arctic Circle
                    "longitude": 0.0,
                    "expected_behavior": "Should calculate without error despite extreme latitude"
                },
                {
                    "name": "leap_year_date",
                    "description": "February 29 on leap year",
                    "datetime": "2000-02-29T12:00:00",
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "expected_behavior": "Should handle leap year correctly"
                },
                {
                    "name": "coordinate_boundaries",
                    "description": "Test coordinate boundary values",
                    "test_coordinates": [
                        {"lat": 90.0, "lon": 0.0, "name": "North Pole"},
                        {"lat": -90.0, "lon": 0.0, "name": "South Pole"},
                        {"lat": 0.0, "lon": 180.0, "name": "International Date Line"},
                        {"lat": 0.0, "lon": -180.0, "name": "International Date Line West"}
                    ]
                }
            ]
        },
        "tolerance_requirements": {
            "description": "Tolerance requirements for validation",
            "angle_tolerance_arcsec": 3.0,  # ≤3" arc as per PRP 5
            "distance_tolerance": 1e-6,
            "speed_tolerance": 1e-6,
            "validation_notes": [
                "All angular measurements should be within 3 arcseconds of reference",
                "Distance measurements should be within 1e-6 units",
                "Speed measurements should be within 1e-6 units per day"
            ]
        }
    }
    
    return fixtures


def main():
    """Main function to create reference fixtures."""
    print("Creating reference fixtures for Meridian Ephemeris validation...")
    
    # Create fixtures directory
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)
    
    if IMMANUEL_AVAILABLE:
        print("Immanuel available - creating comprehensive reference fixtures...")
        
        # Create test cases
        test_cases = create_test_cases()
        
        # Generate Immanuel reference data
        immanuel_fixtures = []
        for test_case in test_cases:
            print(f"Processing: {test_case['name']}")
            result = create_immanuel_chart(test_case)
            if result:
                immanuel_fixtures.append(result)
        
        # Save Immanuel reference data
        if immanuel_fixtures:
            fixtures_path = fixtures_dir / "immanuel_reference.json"
            with open(fixtures_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "created": datetime.now().isoformat(),
                    "source": "Immanuel Python library",
                    "tolerance_arcsec": 3.0,
                    "test_cases": immanuel_fixtures
                }, f, indent=2)
            print(f"Saved Immanuel reference fixtures: {fixtures_path}")
    else:
        print("Immanuel not available - creating simple reference fixtures...")
    
    # Always create simple reference fixtures
    simple_fixtures = create_simple_reference_fixtures()
    
    fixtures_path = fixtures_dir / "reference_fixtures.json"
    with open(fixtures_path, 'w', encoding='utf-8') as f:
        json.dump({
            "created": datetime.now().isoformat(),
            "description": "Reference fixtures for Meridian Ephemeris validation",
            "tolerance_requirements": simple_fixtures.pop("tolerance_requirements"),
            "fixtures": simple_fixtures
        }, f, indent=2)
    
    print(f"Saved reference fixtures: {fixtures_path}")
    
    # Create test case templates
    template_cases = create_test_cases()
    template_path = fixtures_dir / "test_case_templates.json"
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump({
            "created": datetime.now().isoformat(),
            "description": "Test case templates for various scenarios",
            "test_cases": template_cases
        }, f, indent=2)
    
    print(f"Saved test case templates: {template_path}")
    print("Reference fixtures creation complete!")


if __name__ == "__main__":
    main()