#!/usr/bin/env python3
"""
Debug Swiss Ephemeris Setup
"""
import os
import swisseph as swe

def test_swisseph():
    """Test Swiss Ephemeris directly."""
    
    print("=== SWISS EPHEMERIS DEBUG ===")
    
    # Test different ephemeris paths
    paths_to_test = [
        "backend/ephemeris",
        "Swiss Eph Library Files",
        "backend\\ephemeris",
        "Swiss Eph Library Files"
    ]
    
    for path in paths_to_test:
        print(f"\nTesting path: {path}")
        
        if os.path.exists(path):
            print(f"✅ Path exists")
            files = os.listdir(path)
            print(f"Files found: {files}")
            
            # Try setting the path
            try:
                swe.set_ephe_path(path)
                print(f"✅ Path set successfully")
                
                # Try a simple calculation - Sun position for Jan 1, 2000
                jd = swe.julday(2000, 1, 1, 12.0)
                result = swe.calc(jd, swe.SUN)
                longitude = result[0][0] if isinstance(result[0], (list, tuple)) else result[0]
                print(f"✅ Sun calculation successful: {longitude:.2f}°")
                return True
                
            except Exception as e:
                print(f"❌ Calculation failed: {e}")
        else:
            print(f"❌ Path does not exist")
    
    print("\n❌ All paths failed")
    return False

if __name__ == "__main__":
    success = test_swisseph()
    if success:
        print("\n🎉 Swiss Ephemeris is working!")
    else:
        print("\n💥 Swiss Ephemeris setup needs fixing")
