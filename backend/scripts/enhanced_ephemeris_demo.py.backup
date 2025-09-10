#!/usr/bin/env python3
"""
Enhanced Ephemeris Demonstration

This script demonstrates the enhanced ephemeris calculations including:
- South Node calculations (mean and true)
- Retrograde motion detection
- Complete planetary positions with motion analysis
- Lunar node axis information

Usage:
    python enhanced_ephemeris_demo.py [--date YYYY-MM-DD] [--time HH:MM:SS] [--all]
"""

import argparse
import json
from datetime import datetime, timezone
from typing import Dict, Any

# Import our enhanced calculations
try:
    from app.core.ephemeris.tools.enhanced_calculations import (
        get_comprehensive_ephemeris_output,
        calculate_complete_lunar_nodes,
        calculate_node_axis_info,
        get_retrograde_planets_only,
        analyze_retrograde_patterns,
        julian_day_from_datetime
    )
    print("✓ Enhanced ephemeris calculations loaded successfully")
except ImportError as e:
    print(f"⚠ Warning: Could not import enhanced calculations: {e}")
    print("Make sure you're running from the correct directory")
    exit(1)


def format_longitude(degrees: float) -> str:
    """Format longitude in degrees to zodiac sign notation."""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    sign_index = int(degrees // 30)
    sign_degrees = degrees % 30
    sign_minutes = int((sign_degrees % 1) * 60)
    sign_seconds = int(((sign_degrees % 1) * 60 % 1) * 60)
    
    return f"{int(sign_degrees)}° {sign_minutes}' {sign_seconds}\" {signs[sign_index]}"


def print_planet_position(name: str, position: Dict[str, Any], include_speed: bool = True):
    """Print formatted planet position information."""
    longitude = position['longitude']
    motion_symbol = "R" if position['is_retrograde'] else "D"
    if position['motion_type'] == 'stationary':
        motion_symbol = "S"
    
    print(f"  {name:<20} {format_longitude(longitude):<25} ({motion_symbol})")
    
    if include_speed:
        speed = position.get('longitude_speed', 0)
        print(f"                      Speed: {speed:+7.4f}°/day")


def demonstrate_south_node_calculations(test_datetime: datetime):
    """Demonstrate South Node calculations."""
    print("\n" + "="*80)
    print("SOUTH NODE CALCULATIONS DEMONSTRATION")
    print("="*80)
    
    julian_day = julian_day_from_datetime(test_datetime)
    
    try:
        # Calculate complete lunar nodes
        node_data = calculate_complete_lunar_nodes(julian_day)
        
        print(f"\nLunar Node Positions for {test_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("-" * 60)
        
        print("NORTH NODES:")
        print_planet_position("Mean North Node", node_data.mean_north.to_dict())
        print_planet_position("True North Node", node_data.true_north.to_dict())
        
        print("\nSOUTH NODES:")
        print_planet_position("Mean South Node", node_data.mean_south.to_dict())
        print_planet_position("True South Node", node_data.true_south.to_dict())
        
        # Demonstrate the 180° relationship
        print("\nNODE AXIS ANALYSIS:")
        print("-" * 30)
        mean_north_lon = node_data.mean_north.longitude
        mean_south_lon = node_data.mean_south.longitude
        difference = abs(mean_south_lon - mean_north_lon)
        if difference > 180:
            difference = 360 - difference
        
        print(f"Mean North Node: {mean_north_lon:.3f}°")
        print(f"Mean South Node: {mean_south_lon:.3f}°")
        print(f"Axis Difference: {difference:.3f}° (should be ~180°)")
        
        # Node axis information
        axis_info = calculate_node_axis_info(julian_day)
        print(f"Mean-True Difference: {axis_info['mean_true_difference_degrees']:.3f}°")
        print(f"Node Speed: {axis_info['node_speed_degrees_per_day']:.4f}°/day")
        print(f"Nodes Retrograde: {axis_info['nodes_retrograde']}")
        
    except Exception as e:
        print(f"Error calculating lunar nodes: {e}")


def demonstrate_retrograde_detection(test_datetime: datetime):
    """Demonstrate retrograde motion detection."""
    print("\n" + "="*80)
    print("RETROGRADE MOTION DETECTION DEMONSTRATION")
    print("="*80)
    
    try:
        # Get comprehensive ephemeris data
        result = get_comprehensive_ephemeris_output(
            test_datetime,
            include_analysis=True,
            include_asteroids=True,
            include_nodes=False,  # We'll handle nodes separately
            include_lilith=True
        )
        
        positions = result['positions']
        analysis = result['retrograde_analysis']
        
        print(f"\nPlanetary Positions for {test_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("-" * 70)
        print("Planet               Position                  Motion")
        print("-" * 70)
        
        # Sort planets by traditional order
        planet_order = ['sun', 'moon', 'mercury', 'venus', 'mars', 
                       'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        
        for planet_name in planet_order:
            if planet_name in positions:
                print_planet_position(planet_name.title(), positions[planet_name], include_speed=False)
        
        # Show asteroids if included
        asteroid_names = ['chiron', 'ceres', 'pallas', 'juno', 'vesta']
        if any(name in positions for name in asteroid_names):
            print("\nMAJOR ASTEROIDS:")
            print("-" * 20)
            for asteroid_name in asteroid_names:
                if asteroid_name in positions:
                    print_planet_position(asteroid_name.title(), positions[asteroid_name], include_speed=False)
        
        # Show Lilith points if included
        lilith_names = ['lilith_mean', 'lilith_true']
        if any(name in positions for name in lilith_names):
            print("\nLILITH POINTS:")
            print("-" * 15)
            for lilith_name in lilith_names:
                if lilith_name in positions:
                    display_name = lilith_name.replace('_', ' ').title()
                    print_planet_position(display_name, positions[lilith_name], include_speed=False)
        
        # Show retrograde analysis
        print(f"\nRETROGRADE ANALYSIS:")
        print("-" * 25)
        print(f"Total Bodies: {analysis['total_bodies']}")
        print(f"Retrograde: {analysis['retrograde_count']} ({analysis['retrograde_percentage']:.1f}%)")
        print(f"Direct: {analysis['direct_count']}")
        print(f"Stationary: {analysis['stationary_count']}")
        
        if analysis['retrograde_bodies']:
            print(f"\nCurrently Retrograde Planets:")
            for body in analysis['retrograde_bodies']:
                print(f"  • {body['name'].title():<15} {format_longitude(body['longitude'])}")
        
    except Exception as e:
        print(f"Error performing retrograde analysis: {e}")


def demonstrate_comprehensive_output(test_datetime: datetime, save_json: bool = False):
    """Demonstrate comprehensive ephemeris output."""
    print("\n" + "="*80)
    print("COMPREHENSIVE EPHEMERIS OUTPUT DEMONSTRATION")
    print("="*80)
    
    try:
        # Get complete ephemeris data
        result = get_comprehensive_ephemeris_output(
            test_datetime,
            include_analysis=True,
            include_asteroids=True,
            include_nodes=True,
            include_lilith=True
        )
        
        calc_info = result['calculation_info']
        positions = result['positions']
        analysis = result['retrograde_analysis']
        
        print(f"\nCalculation Information:")
        print("-" * 25)
        print(f"DateTime (UTC): {calc_info['datetime_utc']}")
        print(f"Julian Day: {calc_info['julian_day']:.6f}")
        print(f"Swiss Ephemeris Version: {calc_info['swiss_ephemeris_version']}")
        print(f"Coordinate System: {calc_info['coordinate_system']}")
        print(f"Precision: {calc_info['precision']}")
        
        print(f"\nTotal Objects Calculated: {len(positions)}")
        print("-" * 30)
        
        # Categories
        traditional_planets = 0
        asteroids = 0
        nodes = 0
        lilith_points = 0
        
        for name in positions.keys():
            if name in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 
                       'saturn', 'uranus', 'neptune', 'pluto']:
                traditional_planets += 1
            elif 'node' in name:
                nodes += 1
            elif 'lilith' in name:
                lilith_points += 1
            else:
                asteroids += 1
        
        print(f"Traditional Planets: {traditional_planets}")
        print(f"Asteroids: {asteroids}")
        print(f"Lunar Nodes: {nodes}")
        print(f"Lilith Points: {lilith_points}")
        
        # Show sample detailed data for one planet
        if 'mercury' in positions:
            print(f"\nSample Detailed Data (Mercury):")
            print("-" * 35)
            mercury = positions['mercury']
            print(f"Longitude: {mercury['longitude']:.6f}° ({format_longitude(mercury['longitude'])})")
            print(f"Latitude: {mercury['latitude']:.6f}°")
            print(f"Distance: {mercury['distance']:.6f} AU")
            print(f"Longitude Speed: {mercury['longitude_speed']:+.6f}°/day")
            print(f"Is Retrograde: {mercury['is_retrograde']}")
            print(f"Motion Type: {mercury['motion_type']}")
        
        # Show lunar nodes summary
        if any('node' in name for name in positions.keys()):
            print(f"\nLunar Nodes Summary:")
            print("-" * 22)
            node_names = [name for name in positions.keys() if 'node' in name]
            for node_name in sorted(node_names):
                node_data = positions[node_name]
                display_name = node_name.replace('_', ' ').title()
                print(f"{display_name:<18} {format_longitude(node_data['longitude'])}")
        
        # Save JSON if requested
        if save_json:
            filename = f"ephemeris_output_{test_datetime.strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n✓ Complete data saved to: {filename}")
    
    except Exception as e:
        print(f"Error generating comprehensive output: {e}")


def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(description='Enhanced Ephemeris Demonstration')
    parser.add_argument('--date', default=None, 
                       help='Date for calculation (YYYY-MM-DD), default: today')
    parser.add_argument('--time', default='12:00:00',
                       help='Time for calculation (HH:MM:SS), default: 12:00:00')
    parser.add_argument('--all', action='store_true',
                       help='Run all demonstrations')
    parser.add_argument('--south-nodes', action='store_true',
                       help='Demonstrate South Node calculations')
    parser.add_argument('--retrograde', action='store_true',
                       help='Demonstrate retrograde detection')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Demonstrate comprehensive output')
    parser.add_argument('--save-json', action='store_true',
                       help='Save comprehensive output to JSON file')
    
    args = parser.parse_args()
    
    # Determine date and time
    if args.date:
        try:
            date_obj = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            return 1
    else:
        date_obj = datetime.now().date()
    
    try:
        time_obj = datetime.strptime(args.time, '%H:%M:%S').time()
    except ValueError:
        print("Error: Invalid time format. Use HH:MM:SS")
        return 1
    
    test_datetime = datetime.combine(date_obj, time_obj, timezone.utc)
    
    print("Enhanced Ephemeris Calculations Demonstration")
    print("=" * 50)
    print(f"Swiss Ephemeris Integration with Retrograde Detection")
    print(f"Calculation Date/Time: {test_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Determine which demonstrations to run
    run_all = args.all
    run_south_nodes = args.south_nodes or run_all
    run_retrograde = args.retrograde or run_all
    run_comprehensive = args.comprehensive or run_all
    
    # If no specific flags, run all
    if not (run_south_nodes or run_retrograde or run_comprehensive):
        run_all = True
        run_south_nodes = run_retrograde = run_comprehensive = True
    
    try:
        if run_south_nodes:
            demonstrate_south_node_calculations(test_datetime)
        
        if run_retrograde:
            demonstrate_retrograde_detection(test_datetime)
        
        if run_comprehensive:
            demonstrate_comprehensive_output(test_datetime, args.save_json)
        
        print("\n" + "="*80)
        print("DEMONSTRATION COMPLETE")
        print("="*80)
        print("Key Features Demonstrated:")
        print("• South Node calculations (180° opposite North Node)")
        print("• Retrograde motion detection (longitude_speed < 0)")
        print("• Complete planetary positions with motion analysis")
        print("• Swiss Ephemeris integration with enhanced functionality")
        print("• JSON serialization for data exchange")
        
        if run_comprehensive:
            print("\nThis implements the 'all planets and features output from ephemeris'")
            print("as described in the technical specification document.")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
