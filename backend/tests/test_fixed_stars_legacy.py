"""
Test script for fixed star integration
"""

import sys
import os
sys.path.append('backend')

from extracted.services.ephemeris_service import EphemerisService
from extracted.api.models.schemas import (
    NatalChartRequest, SubjectRequest, CoordinateInput, DateTimeInput, TimezoneInput
)

def test_fixed_stars():
    print("=== TESTING FIXED STAR INTEGRATION ===")
    
    # Create service instance
    service = EphemerisService()
    
    # Test fixed star availability first
    print("\n1. Testing Fixed Star Availability:")
    availability = service.get_fixed_star_availability()
    print(f"Swiss Ephemeris catalog available: {availability['swe_catalog_available']}")
    print(f"Total stars in registry: {availability['total_stars_in_registry']}")
    print(f"Available stars: {availability['available_stars']}")
    print(f"Foundation 24 available: {availability['foundation_24_available']}/{availability['foundation_24_total']}")
    
    if not availability['available_stars']:
        print("❌ No fixed stars available - Swiss Ephemeris catalog may be missing")
        return
    
    # Test individual star calculation
    print("\n2. Testing Individual Fixed Star Calculations:")
    
    # Create test natal chart request
    request = NatalChartRequest(
        subject=SubjectRequest(
            name='Fixed Stars Test',
            datetime=DateTimeInput(iso_string='1990-06-15T14:30:00-04:00'),
            latitude=CoordinateInput(decimal=40.7128),
            longitude=CoordinateInput(decimal=-74.0060),
            timezone=TimezoneInput(name='America/New_York')
        )
    )
    
    try:
        # Test standalone fixed stars calculation
        stars_result = service.calculate_fixed_stars(
            request, 
            star_names=None,  # All available
            include_aspects=True,
            magnitude_limit=3.0  # Include dimmer stars
        )
        
        print(f"✓ Fixed stars calculated: {stars_result['count']}")
        print(f"✓ Foundation 24 stars: {stars_result['foundation_24_count']}")
        
        # Show available stars
        if stars_result['stars']:
            print("\nAvailable Fixed Stars:")
            for star_name, star_data in stars_result['stars'].items():
                print(f"  {star_name}: {star_data['longitude']:.2f}° in {star_data['sign_name']} "
                      f"(mag {star_data['magnitude']:.1f})")
        
        # Show aspects if any
        if 'aspects' in stars_result and stars_result['aspects']:
            print(f"\nFixed Star-Planet Aspects: {len(stars_result['aspects'])}")
            for aspect in stars_result['aspects'][:3]:  # Show first 3
                print(f"  {aspect['star']} {aspect['aspect']} {aspect['planet']} "
                      f"(orb: {aspect['orb']:.2f}°)")
        else:
            print("\nNo significant fixed star aspects found")
        
        print("\n✓ Fixed stars calculation successful!")
        
    except Exception as e:
        print(f"❌ Fixed stars calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test integration with enhanced natal chart
    print("\n3. Testing Enhanced Natal Chart with Fixed Stars:")
    
    try:
        enhanced_chart = service.calculate_natal_chart_enhanced(
            request,
            include_aspects=True,
            include_dignities=True,
            include_arabic_parts=False,  # Skip to focus on fixed stars
            include_fixed_stars=True,
            fixed_star_magnitude_limit=2.0
        )
        
        if 'fixed_stars' in enhanced_chart:
            fs_data = enhanced_chart['fixed_stars']
            print(f"✓ Fixed stars integrated in enhanced chart: {fs_data['count']} stars")
            print(f"✓ Foundation 24 count: {fs_data['foundation_24_count']}")
            
            # Check for calculation error
            if 'calculation_error' in fs_data:
                print(f"⚠️ Calculation error: {fs_data['calculation_error']}")
            else:
                print("✓ No calculation errors")
        else:
            print("❌ Fixed stars not found in enhanced chart response")
            
        print("\n✓ Enhanced chart with fixed stars successful!")
        
    except Exception as e:
        print(f"❌ Enhanced chart with fixed stars failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== FIXED STAR INTEGRATION TEST COMPLETE ===")

if __name__ == "__main__":
    test_fixed_stars()