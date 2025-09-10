#!/usr/bin/env python3
"""
Swiss Ephemeris Validator - Comprehensive validation for extracted systems
"""

import os
import sys
from pathlib import Path
import swisseph as swe

class SwissEphemerisValidator:
    """Validates Swiss Ephemeris setup for extracted systems"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            # Auto-detect project root
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "Swiss Eph Library Files").exists():
                    project_root = str(parent)
                    break
            else:
                project_root = str(Path.cwd())
                
        self.project_root = project_root
        self.swiss_eph_path = None
        
    def validate_data_files(self) -> bool:
        """Validate all required Swiss Ephemeris data files exist"""
        required_files = {
            "sefstars.txt": "Fixed star catalog (CRITICAL for fixed stars)",
            "seas_18.se1": "Asteroid ephemeris",
            "semo_18.se1": "Moon ephemeris", 
            "sepl_18.se1": "Planet ephemeris"
        }
        
        swiss_path = os.path.join(self.project_root, "Swiss Eph Library Files")
        
        print(f"🔍 Checking Swiss Ephemeris data files in: {swiss_path}")
        
        if not os.path.exists(swiss_path):
            print(f"❌ Swiss Ephemeris directory not found: {swiss_path}")
            return False
            
        missing_files = []
        for filename, description in required_files.items():
            file_path = os.path.join(swiss_path, filename)
            if not os.path.exists(file_path):
                missing_files.append(f"{filename} - {description}")
            else:
                file_size = os.path.getsize(file_path)
                print(f"✅ {filename}: {file_size:,} bytes - {description}")
        
        if missing_files:
            print(f"❌ Missing critical Swiss Ephemeris files:")
            for missing in missing_files:
                print(f"   - {missing}")
            return False
            
        self.swiss_eph_path = swiss_path
        return True
        
    def setup_swiss_ephemeris(self) -> bool:
        """Setup Swiss Ephemeris path for calculations"""
        if not self.swiss_eph_path:
            if not self.validate_data_files():
                return False
                
        try:
            print(f"🔧 Setting Swiss Ephemeris path...")
            swe.set_ephe_path(self.swiss_eph_path)
            os.environ['SE_EPHE_PATH'] = self.swiss_eph_path
            print(f"✅ Swiss Ephemeris path configured: {self.swiss_eph_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to set Swiss Ephemeris path: {e}")
            return False
            
    def test_fixed_star_calculation(self) -> bool:
        """Test fixed star calculation functionality with Royal Stars"""
        print(f"🌟 Testing fixed star calculations...")
        
        if not self.setup_swiss_ephemeris():
            return False
            
        # Test with the 4 Royal Stars (most important in astrology)
        royal_stars = {
            "Regulus": "Leo - The Royal Star",
            "Aldebaran": "Taurus - Watcher of the East", 
            "Antares": "Scorpius - Watcher of the West",
            "Fomalhaut": "Piscis Austrinus - Watcher of the South"
        }
        
        test_jd = 2460000.5  # Reference Julian Day (approx Sept 2023)
        
        working_stars = []
        for star_name, description in royal_stars.items():
            try:
                result = swe.fixstar(star_name, test_jd)
                if len(result) >= 2 and isinstance(result[0], (list, tuple)):
                    longitude = result[0][0]
                    latitude = result[0][1]
                    if 0 <= longitude <= 360 and -90 <= latitude <= 90:
                        working_stars.append(star_name)
                        print(f"✅ {star_name}: {longitude:.4f}° longitude - {description}")
                    else:
                        print(f"❌ {star_name}: Invalid coordinates (lon: {longitude}, lat: {latitude})")
                else:
                    print(f"❌ {star_name}: Invalid result format - {result}")
            except Exception as e:
                print(f"❌ {star_name}: Calculation failed - {e}")
                
        success_rate = len(working_stars) / len(royal_stars)
        print(f"📊 Fixed star success rate: {success_rate:.1%} ({len(working_stars)}/{len(royal_stars)})")
        
        if success_rate < 1.0:
            print(f"⚠️  Some fixed stars failed - extraction may have limited star support")
        
        return success_rate >= 0.75  # At least 75% success rate acceptable
        
    def test_planetary_calculation(self) -> bool:
        """Test planetary position calculation for all major bodies"""
        print(f"🪐 Testing planetary calculations...")
        
        if not self.setup_swiss_ephemeris():
            return False
            
        # Test traditional 7 planets + modern planets
        test_bodies = [
            (0, "Sun"), (1, "Moon"), (2, "Mercury"), (3, "Venus"), 
            (4, "Mars"), (5, "Jupiter"), (6, "Saturn"),
            (7, "Uranus"), (8, "Neptune"), (9, "Pluto")
        ]
        test_jd = 2460000.5
        
        working_bodies = []
        for body_id, body_name in test_bodies:
            try:
                result = swe.calc_ut(test_jd, body_id)
                if len(result) >= 2 and isinstance(result[0], (list, tuple)):
                    longitude = result[0][0]
                    latitude = result[0][1]
                    distance = result[0][2]
                    if 0 <= longitude <= 360 and -90 <= latitude <= 90 and distance > 0:
                        working_bodies.append(body_name)
                        print(f"✅ {body_name}: {longitude:.4f}° (dist: {distance:.6f} AU)")
                    else:
                        print(f"❌ {body_name}: Invalid data (lon: {longitude}, lat: {latitude}, dist: {distance})")
                else:
                    print(f"❌ {body_name}: Invalid result format - {result}")
            except Exception as e:
                print(f"❌ {body_name}: Calculation failed - {e}")
                
        success_rate = len(working_bodies) / len(test_bodies)
        print(f"📊 Planetary calculation success rate: {success_rate:.1%} ({len(working_bodies)}/{len(test_bodies)})")
        
        return success_rate >= 0.9  # At least 90% success rate for planets
        
    def test_house_calculation(self) -> bool:
        """Test house calculation functionality"""
        print(f"🏠 Testing house calculations...")
        
        if not self.setup_swiss_ephemeris():
            return False
            
        # Test coordinates (New York City)
        latitude = 40.7128
        longitude = -74.0060
        test_jd = 2460000.5
        
        try:
            # Test Placidus house system (most common)
            houses = swe.houses(test_jd, latitude, longitude, b'P')
            
            # Swiss Ephemeris returns (cusps, ascmc) tuple
            if len(houses) >= 2:
                cusps = houses[0]  # House cusps 
                ascmc = houses[1]  # Ascendant, MC, ARMC, Vertex, etc.
                
                # Swiss Ephemeris house format: cusps has 12 or 13 elements, ascmc has 8+ elements
                if len(cusps) >= 12 and len(ascmc) >= 4:
                    # Check house cusps - use available cusps
                    if len(cusps) == 13:
                        # Format with unused index 0, check cusps 1-12
                        valid_cusps = all(0 <= cusps[i] <= 360 for i in range(1, 13))
                        house1 = cusps[1]
                        house7 = cusps[7]
                    else:
                        # Format with 12 cusps starting from index 0
                        valid_cusps = all(0 <= cusps[i] <= 360 for i in range(12))
                        house1 = cusps[0]
                        house7 = cusps[6]
                    
                    # Check angles (ASC, MC, ARMC, Vertex)
                    valid_angles = all(0 <= ascmc[i] <= 360 for i in range(4))
                    
                    if valid_cusps and valid_angles:
                        print(f"✅ Houses calculated successfully")
                        print(f"   ASC: {ascmc[0]:.4f}°, MC: {ascmc[1]:.4f}°")
                        print(f"   House 1: {house1:.4f}°, House 7: {house7:.4f}°")
                        return True
                    else:
                        print(f"❌ Invalid house calculations - cusps or angles out of range")
                        print(f"   Cusps valid: {valid_cusps}, Angles valid: {valid_angles}")
                        return False
                else:
                    print(f"❌ Invalid house calculation result format - cusps: {len(cusps)}, ascmc: {len(ascmc)}")
                    return False
            else:
                print(f"❌ Invalid house calculation result format - expected 2 elements, got {len(houses)}")
                return False
                
        except Exception as e:
            print(f"❌ House calculation failed: {e}")
            return False
    
    def validate_all(self) -> bool:
        """Run complete Swiss Ephemeris validation suite"""
        print("=" * 60)
        print("🔍 SWISS EPHEMERIS COMPREHENSIVE VALIDATION")
        print("=" * 60)
        
        results = {
            "data_files": self.validate_data_files(),
            "setup": self.setup_swiss_ephemeris(),
            "fixed_stars": self.test_fixed_star_calculation(),
            "planets": self.test_planetary_calculation(),
            "houses": self.test_house_calculation()
        }
        
        all_passed = all(results.values())
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
            
        print("=" * 60)
        
        if all_passed:
            print("🎉 SWISS EPHEMERIS FULLY VALIDATED AND READY FOR EXTRACTION!")
            print(f"   Data path: {self.swiss_eph_path}")
            print("   All calculation systems operational")
        else:
            print("⚠️  SWISS EPHEMERIS VALIDATION FAILED")
            print("   Extraction may encounter issues")
            print("   Review errors above and fix before proceeding")
            
        return all_passed

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Swiss Ephemeris setup')
    parser.add_argument('--project-root', help='Project root directory')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    try:
        validator = SwissEphemerisValidator(args.project_root)
        success = validator.validate_all()
        
        if not args.quiet:
            if success:
                print("\n✨ Ready for PRP execution!")
            else:
                print("\n🚨 Fix Swiss Ephemeris issues before extraction")
                
        return 0 if success else 1
        
    except Exception as e:
        print(f"💥 Validation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
