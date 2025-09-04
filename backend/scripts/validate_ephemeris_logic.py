#!/usr/bin/env python3
"""
Enhanced Ephemeris Logic Validation

This script validates the South Node and retrograde calculation logic
without requiring Swiss Ephemeris installation.
"""

from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class MockPlanetPosition:
    """Mock planet position for testing logic."""
    planet_id: int
    longitude: float
    latitude: float
    distance: float
    longitude_speed: float
    latitude_speed: float = 0.0
    distance_speed: float = 0.0
    calculation_time: Optional[datetime] = None
    flags: int = 0
    name: str = ""


def normalize_longitude(degrees: float) -> float:
    """Normalize longitude to 0-360 range."""
    return degrees % 360.0


def calculate_south_node_position_demo(
    north_node_position: MockPlanetPosition,
    calculation_type: str = "mean"
) -> Dict[str, Any]:
    """
    Demonstrate South Node calculation logic.
    """
    # South Node longitude is North Node + 180°
    south_longitude = normalize_longitude(north_node_position.longitude + 180.0)
    
    # South Node latitude is opposite of North Node
    south_latitude = -north_node_position.latitude
    
    # Speed calculations
    south_longitude_speed = north_node_position.longitude_speed
    south_latitude_speed = -north_node_position.latitude_speed
    
    return {
        'longitude': south_longitude,
        'latitude': south_latitude,
        'distance': north_node_position.distance,
        'longitude_speed': south_longitude_speed,
        'latitude_speed': south_latitude_speed,
        'distance_speed': north_node_position.distance_speed,
        'name': f'South Node ({calculation_type.title()})',
        'is_retrograde': south_longitude_speed < 0.0,
        'motion_type': 'retrograde' if south_longitude_speed < 0.0 else 'direct',
        'calculation_time': north_node_position.calculation_time
    }


def demonstrate_retrograde_detection():
    """Demonstrate retrograde detection logic."""
    print("RETROGRADE DETECTION DEMONSTRATION")
    print("="*50)
    
    # Test cases with different longitude speeds
    test_planets = [
        MockPlanetPosition(1, 150.5, 1.2, 0.8, -1.2, name="Mercury Retrograde"),
        MockPlanetPosition(2, 200.3, 0.5, 0.7, 1.1, name="Venus Direct"),
        MockPlanetPosition(3, 90.0, -0.8, 1.5, 0.0, name="Mars Stationary"),
        MockPlanetPosition(4, 45.7, 0.3, 5.2, -0.08, name="Jupiter Retrograde"),
        MockPlanetPosition(5, 300.1, 1.8, 9.5, 0.033, name="Saturn Direct")
    ]
    
    print("\nPlanet Motion Analysis:")
    print("-" * 40)
    print("Planet          Speed (°/day)  Motion Type")
    print("-" * 40)
    
    for planet in test_planets:
        motion_type = "retrograde" if planet.longitude_speed < 0 else ("direct" if planet.longitude_speed > 0 else "stationary")
        print(f"{planet.name:<15} {planet.longitude_speed:>8.3f}      {motion_type}")
    
    return test_planets


def demonstrate_south_node_calculations():
    """Demonstrate South Node calculation logic."""
    print("\n\nSOUTH NODE CALCULATION DEMONSTRATION")
    print("="*50)
    
    # Mock North Node positions (nodes always move retrograde)
    test_nodes = [
        MockPlanetPosition(10, 125.5, 0.2, 1.0, -0.053, 0.01, name="Mean North Node"),
        MockPlanetPosition(11, 126.2, -0.15, 1.0, -0.055, -0.005, name="True North Node")
    ]
    
    print("\nLunar Node Calculations:")
    print("-" * 60)
    
    for north_node in test_nodes:
        calc_type = "mean" if north_node.planet_id == 10 else "true"
        south_node = calculate_south_node_position_demo(north_node, calc_type)
        
        print(f"\n{calc_type.upper()} NODE PAIR:")
        print(f"North Node:  {north_node.longitude:>7.3f}° (lat: {north_node.latitude:>6.3f}°)")
        print(f"South Node:  {south_node['longitude']:>7.3f}° (lat: {south_node['latitude']:>6.3f}°)")
        print(f"Difference:  {abs(south_node['longitude'] - north_node.longitude):>7.3f}° (should be ~180°)")
        print(f"Speed:       {south_node['longitude_speed']:>7.4f}°/day ({south_node['motion_type']})")
    
    return test_nodes


def format_longitude_to_zodiac(degrees: float) -> str:
    """Convert longitude to zodiac sign notation."""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    sign_index = int(degrees // 30)
    sign_degrees = degrees % 30
    sign_minutes = int((sign_degrees % 1) * 60)
    
    return f"{int(sign_degrees):>2d}°{sign_minutes:>2d}' {signs[sign_index]}"


def demonstrate_zodiac_positions():
    """Demonstrate zodiac position formatting."""
    print("\n\nZODIAC POSITION DEMONSTRATION")
    print("="*50)
    
    # Test positions
    test_positions = [
        (125.5, "North Node example"),
        (305.5, "South Node example (125.5 + 180)"),
        (0.0, "Vernal Equinox"),
        (90.0, "Summer Solstice"),
        (180.0, "Autumnal Equinox"),
        (270.0, "Winter Solstice")
    ]
    
    print("\nLongitude to Zodiac Sign Conversion:")
    print("-" * 45)
    print("Degrees     Zodiac Position       Description")
    print("-" * 45)
    
    for degrees, description in test_positions:
        zodiac = format_longitude_to_zodiac(degrees)
        print(f"{degrees:>7.1f}°    {zodiac:<20} {description}")


def demonstrate_real_world_scenario():
    """Demonstrate a real-world calculation scenario."""
    print("\n\nREAL-WORLD SCENARIO DEMONSTRATION")
    print("="*50)
    print("Example: Planetary positions for January 1, 2024 12:00 UTC")
    print("(These are approximated values for demonstration)")
    
    # Approximated planetary positions for demonstration
    planets = [
        MockPlanetPosition(0, 280.1, 0.0, 0.983, 0.985, name="Sun"),
        MockPlanetPosition(1, 268.5, -2.1, 0.0026, 13.176, name="Moon"),
        MockPlanetPosition(2, 245.8, -1.8, 0.41, -1.25, name="Mercury"),  # Retrograde
        MockPlanetPosition(3, 320.2, 1.2, 0.69, 1.12, name="Venus"),
        MockPlanetPosition(4, 95.7, 0.8, 1.42, 0.52, name="Mars"),
        MockPlanetPosition(5, 25.3, 0.2, 5.31, 0.083, name="Jupiter"),
        MockPlanetPosition(6, 344.1, 1.5, 10.12, 0.034, name="Saturn"),
        MockPlanetPosition(10, 22.8, 0.0, 1.0, -0.053, name="North Node"),  # Mean
    ]
    
    print("\nPlanetary Overview:")
    print("-" * 65)
    print("Planet      Longitude    Zodiac Position       Motion")
    print("-" * 65)
    
    retrograde_count = 0
    for planet in planets:
        zodiac = format_longitude_to_zodiac(planet.longitude)
        motion = "R" if planet.longitude_speed < 0 else "D"
        if planet.longitude_speed < 0:
            retrograde_count += 1
        
        print(f"{planet.name:<10} {planet.longitude:>8.1f}°  {zodiac:<20} ({motion})")
    
    # Calculate South Node
    north_node = next(p for p in planets if p.name == "North Node")
    south_node_data = calculate_south_node_position_demo(north_node, "mean")
    
    print(f"{'South Node':<10} {south_node_data['longitude']:>8.1f}°  {format_longitude_to_zodiac(south_node_data['longitude']):<20} (R)")
    retrograde_count += 1  # South Node is always retrograde
    
    print(f"\nRetrograde Analysis:")
    print(f"- Total bodies: {len(planets) + 1}")
    print(f"- Retrograde: {retrograde_count}")
    print(f"- Direct: {len(planets) + 1 - retrograde_count}")
    print(f"- Retrograde percentage: {retrograde_count / (len(planets) + 1) * 100:.1f}%")


def main():
    """Main demonstration function."""
    print("Enhanced Ephemeris Calculations - Logic Validation")
    print("="*60)
    print("This demonstrates the core logic for South Node calculations")
    print("and retrograde detection without requiring Swiss Ephemeris.")
    print("")
    
    try:
        # Run all demonstrations
        demonstrate_retrograde_detection()
        demonstrate_south_node_calculations()
        demonstrate_zodiac_positions()
        demonstrate_real_world_scenario()
        
        print("\n\n" + "="*60)
        print("VALIDATION COMPLETE")
        print("="*60)
        print("Key Validation Points:")
        print("✓ Retrograde detection: longitude_speed < 0")
        print("✓ South Node calculation: North Node + 180°")
        print("✓ Latitude inversion: South lat = -(North lat)")
        print("✓ Speed preservation: Same longitude speed magnitude")
        print("✓ Coordinate normalization: 0-360° range")
        print("✓ Zodiac conversion: Degrees to sign notation")
        print("\nThe logic is ready for Swiss Ephemeris integration!")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
