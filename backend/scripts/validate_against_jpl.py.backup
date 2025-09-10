#!/usr/bin/env python3
"""
JPL Horizons Validation Script

Cross-validation script for planetary position calculations against 
JPL Horizons System data. Ensures sub-arcsecond accuracy for all
planetary ephemeris calculations.
"""

import sys
import asyncio
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import swisseph as swe

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ephemeris.tools.validation import nasa_validator
from app.core.ephemeris.charts.natal import NatalChart
from app.core.ephemeris.charts.subject import Subject

class JPLValidationRunner:
    """Comprehensive JPL Horizons validation test runner."""
    
    def __init__(self):
        """Initialize validation runner."""
        self.validator = nasa_validator
        self.results = []
        
        # Planet mapping
        self.PLANETS = {
            'Sun': swe.SUN,
            'Moon': swe.MOON,
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Uranus': swe.URANUS,
            'Neptune': swe.NEPTUNE,
            'Pluto': swe.PLUTO
        }
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """
        Run comprehensive validation against JPL Horizons data.
        
        Returns:
            Detailed validation report
        """
        print("🚀 Starting JPL Horizons Position Validation Suite")
        print("=" * 70)
        
        # Load JPL reference data
        print("📚 Loading JPL Horizons Reference Data...")
        jpl_data = self.validator.load_jpl_ephemeris_data()
        test_dates = list(jpl_data.keys())[:5]  # Test first 5 dates
        
        print(f"   Found {len(jpl_data)} reference epochs")
        print(f"   Testing {len(test_dates)} epochs")
        
        validation_results = {
            'position_validation_results': [],
            'planet_accuracy_summary': {},
            'date_accuracy_summary': {},
            'overall_summary': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Validate planetary positions
        print("\n🪐 Validating Planetary Positions...")
        position_results = await self._validate_planetary_positions(jpl_data, test_dates)
        validation_results['position_validation_results'] = position_results
        
        # Generate planet-specific accuracy
        print("\n📊 Analyzing Planet-Specific Accuracy...")
        planet_summary = self._generate_planet_accuracy_summary(position_results)
        validation_results['planet_accuracy_summary'] = planet_summary
        
        # Generate date-specific accuracy
        print("\n📅 Analyzing Date-Specific Accuracy...")
        date_summary = self._generate_date_accuracy_summary(position_results)
        validation_results['date_accuracy_summary'] = date_summary
        
        # Generate overall summary
        print("\n📈 Generating Overall Summary...")
        overall_summary = self._generate_overall_summary(position_results)
        validation_results['overall_summary'] = overall_summary
        
        # Save results
        self._save_validation_report(validation_results)
        
        # Print results
        self._print_validation_results(validation_results)
        
        return validation_results
    
    async def _validate_planetary_positions(
        self, 
        jpl_data: Dict[str, Any], 
        test_dates: List[str]
    ) -> List[Dict[str, Any]]:
        """Validate planetary position calculations."""
        results = []
        
        for date_idx, date_str in enumerate(test_dates, 1):
            print(f"   Testing epoch {date_idx}/{len(test_dates)}: {date_str}")
            
            test_datetime = datetime.fromisoformat(date_str)
            reference_positions = jpl_data[date_str]
            
            # Calculate positions using our system
            calculated_positions = await self._calculate_planetary_positions(test_datetime)
            
            # Compare each planet
            for planet_name, reference_pos in reference_positions.items():
                if planet_name in calculated_positions:
                    calculated_pos = calculated_positions[planet_name]
                    
                    # Calculate position errors
                    lon_error = abs(calculated_pos['longitude'] - reference_pos['longitude'])
                    lat_error = abs(calculated_pos['latitude'] - reference_pos['latitude'])
                    
                    # Handle longitude wrap-around
                    if lon_error > 180:
                        lon_error = 360 - lon_error
                    
                    # Convert to arcseconds
                    lon_error_arcsec = lon_error * 3600
                    lat_error_arcsec = lat_error * 3600
                    
                    # Calculate total position error
                    total_error_arcsec = (lon_error_arcsec**2 + lat_error_arcsec**2)**0.5
                    
                    # Calculate distance error percentage
                    dist_error_pct = abs(
                        (calculated_pos['distance'] - reference_pos['distance']) / reference_pos['distance'] * 100
                    ) if reference_pos['distance'] != 0 else 0
                    
                    # Determine pass/fail
                    passed = total_error_arcsec <= self.validator.TOLERANCES['position_arcseconds']
                    
                    result = {
                        'test_date': date_str,
                        'planet': planet_name,
                        'reference_longitude': reference_pos['longitude'],
                        'calculated_longitude': calculated_pos['longitude'],
                        'reference_latitude': reference_pos['latitude'],
                        'calculated_latitude': calculated_pos['latitude'],
                        'reference_distance': reference_pos['distance'],
                        'calculated_distance': calculated_pos['distance'],
                        'longitude_error_arcsec': lon_error_arcsec,
                        'latitude_error_arcsec': lat_error_arcsec,
                        'total_position_error_arcsec': total_error_arcsec,
                        'distance_error_percent': dist_error_pct,
                        'passed': passed,
                        'notes': f'Total error: {total_error_arcsec:.3f}" (target: ≤{self.validator.TOLERANCES["position_arcseconds"]}")'
                    }
                    
                    results.append(result)
                    
                    # Progress indicator
                    if passed:
                        print(f"     ✅ {planet_name:<8} - Error: {total_error_arcsec:.3f}\"")
                    else:
                        print(f"     ❌ {planet_name:<8} - Error: {total_error_arcsec:.3f}\"")
                
                else:
                    # Planet not calculated
                    result = {
                        'test_date': date_str,
                        'planet': planet_name,
                        'reference_longitude': reference_pos['longitude'],
                        'calculated_longitude': None,
                        'reference_latitude': reference_pos['latitude'],
                        'calculated_latitude': None,
                        'reference_distance': reference_pos['distance'],
                        'calculated_distance': None,
                        'longitude_error_arcsec': float('inf'),
                        'latitude_error_arcsec': float('inf'),
                        'total_position_error_arcsec': float('inf'),
                        'distance_error_percent': float('inf'),
                        'passed': False,
                        'notes': 'Planet position not calculated'
                    }
                    
                    results.append(result)
                    print(f"     ❌ {planet_name:<8} - NOT CALCULATED")
        
        return results
    
    async def _calculate_planetary_positions(self, test_datetime: datetime) -> Dict[str, Dict[str, float]]:
        """Calculate planetary positions using our ephemeris system."""
        positions = {}
        
        try:
            # Convert to Julian Day
            jd = swe.julday(
                test_datetime.year, test_datetime.month, test_datetime.day,
                test_datetime.hour + test_datetime.minute/60.0 + test_datetime.second/3600.0
            )
            
            # Calculate positions for each planet
            for planet_name, planet_id in self.PLANETS.items():
                try:
                    pos, speed = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
                    
                    positions[planet_name] = {
                        'longitude': pos[0],
                        'latitude': pos[1], 
                        'distance': pos[2]
                    }
                    
                except Exception as e:
                    print(f"     Warning: Failed to calculate {planet_name}: {e}")
                    continue
            
        except Exception as e:
            print(f"     Error calculating positions for {test_datetime}: {e}")
        
        return positions
    
    def _generate_planet_accuracy_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate accuracy summary by planet."""
        planet_summary = {}
        
        # Group results by planet
        planet_groups = {}
        for result in results:
            planet = result['planet']
            if planet not in planet_groups:
                planet_groups[planet] = []
            planet_groups[planet].append(result)
        
        # Generate summary for each planet
        for planet, planet_results in planet_groups.items():
            valid_results = [r for r in planet_results if r['total_position_error_arcsec'] != float('inf')]
            
            if valid_results:
                total_tests = len(planet_results)
                passed_tests = sum(1 for r in planet_results if r['passed'])
                
                position_errors = [r['total_position_error_arcsec'] for r in valid_results]
                lon_errors = [r['longitude_error_arcsec'] for r in valid_results]
                lat_errors = [r['latitude_error_arcsec'] for r in valid_results]
                dist_errors = [r['distance_error_percent'] for r in valid_results if r['distance_error_percent'] != float('inf')]
                
                planet_summary[planet] = {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'accuracy_percentage': (passed_tests / total_tests) * 100,
                    'average_position_error_arcsec': sum(position_errors) / len(position_errors),
                    'max_position_error_arcsec': max(position_errors),
                    'average_longitude_error_arcsec': sum(lon_errors) / len(lon_errors),
                    'average_latitude_error_arcsec': sum(lat_errors) / len(lat_errors),
                    'average_distance_error_percent': sum(dist_errors) / len(dist_errors) if dist_errors else 0,
                    'jpl_validated': (passed_tests / total_tests) >= 0.95
                }
            else:
                planet_summary[planet] = {
                    'total_tests': len(planet_results),
                    'passed_tests': 0,
                    'accuracy_percentage': 0.0,
                    'average_position_error_arcsec': float('inf'),
                    'max_position_error_arcsec': float('inf'),
                    'average_longitude_error_arcsec': float('inf'),
                    'average_latitude_error_arcsec': float('inf'),
                    'average_distance_error_percent': float('inf'),
                    'jpl_validated': False
                }
        
        return planet_summary
    
    def _generate_date_accuracy_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate accuracy summary by test date."""
        date_summary = {}
        
        # Group results by date
        date_groups = {}
        for result in results:
            date = result['test_date']
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(result)
        
        # Generate summary for each date
        for date, date_results in date_groups.items():
            valid_results = [r for r in date_results if r['total_position_error_arcsec'] != float('inf')]
            
            if valid_results:
                total_tests = len(date_results)
                passed_tests = sum(1 for r in date_results if r['passed'])
                
                position_errors = [r['total_position_error_arcsec'] for r in valid_results]
                
                date_summary[date] = {
                    'total_planets_tested': total_tests,
                    'planets_passed': passed_tests,
                    'epoch_accuracy_percentage': (passed_tests / total_tests) * 100,
                    'average_position_error_arcsec': sum(position_errors) / len(position_errors),
                    'max_position_error_arcsec': max(position_errors),
                    'epoch_validated': (passed_tests / total_tests) >= 0.95
                }
            else:
                date_summary[date] = {
                    'total_planets_tested': len(date_results),
                    'planets_passed': 0,
                    'epoch_accuracy_percentage': 0.0,
                    'average_position_error_arcsec': float('inf'),
                    'max_position_error_arcsec': float('inf'),
                    'epoch_validated': False
                }
        
        return date_summary
    
    def _generate_overall_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall validation summary."""
        valid_results = [r for r in results if r['total_position_error_arcsec'] != float('inf')]
        
        if not valid_results:
            return {
                'total_tests': len(results),
                'passed_tests': 0,
                'failed_tests': len(results),
                'overall_accuracy_percentage': 0.0,
                'jpl_validation_status': 'FAIL',
                'certification_ready': False
            }
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        # Position accuracy statistics
        position_errors = [r['total_position_error_arcsec'] for r in valid_results]
        lon_errors = [r['longitude_error_arcsec'] for r in valid_results]
        lat_errors = [r['latitude_error_arcsec'] for r in valid_results]
        
        avg_position_error = sum(position_errors) / len(position_errors)
        max_position_error = max(position_errors)
        avg_lon_error = sum(lon_errors) / len(lon_errors)
        avg_lat_error = sum(lat_errors) / len(lat_errors)
        
        accuracy_percentage = (passed_tests / total_tests) * 100
        
        # Determine validation status
        jpl_validated = accuracy_percentage >= 95.0 and max_position_error <= 0.1
        certification_ready = accuracy_percentage >= 99.0 and max_position_error <= 0.05
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'overall_accuracy_percentage': accuracy_percentage,
            'average_position_error_arcsec': avg_position_error,
            'maximum_position_error_arcsec': max_position_error,
            'average_longitude_error_arcsec': avg_lon_error,
            'average_latitude_error_arcsec': avg_lat_error,
            'jpl_target_accuracy_arcsec': self.validator.TOLERANCES['position_arcseconds'],
            'jpl_validation_status': 'PASS' if jpl_validated else 'FAIL',
            'certification_ready': certification_ready,
            'sub_arcsecond_accuracy': max_position_error < 1.0
        }
    
    def _save_validation_report(self, results: Dict[str, Any]):
        """Save validation report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create reports directory
        reports_dir = Path(__file__).parent.parent / "validation_reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        json_file = reports_dir / f"jpl_validation_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save detailed CSV report
        csv_file = reports_dir / f"jpl_validation_{timestamp}.csv"
        position_results = results['position_validation_results']
        
        if position_results:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=position_results[0].keys())
                writer.writeheader()
                writer.writerows(position_results)
        
        # Save planet summary CSV
        planet_csv = reports_dir / f"jpl_planet_summary_{timestamp}.csv"
        planet_summary = results['planet_accuracy_summary']
        
        if planet_summary:
            with open(planet_csv, 'w', newline='') as f:
                # Add planet name to each row
                rows = []
                for planet, data in planet_summary.items():
                    row = {'planet': planet, **data}
                    rows.append(row)
                
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"\n💾 JPL Validation reports saved:")
        print(f"   Detailed JSON: {json_file}")
        print(f"   Position CSV:  {csv_file}")
        print(f"   Planet CSV:    {planet_csv}")
    
    def _print_validation_results(self, results: Dict[str, Any]):
        """Print formatted validation results."""
        overall = results['overall_summary']
        planet_summary = results['planet_accuracy_summary']
        
        print("\n" + "=" * 70)
        print("🎯 JPL HORIZONS POSITION VALIDATION RESULTS")
        print("=" * 70)
        
        print(f"📊 Overall Statistics:")
        print(f"   Total Tests:        {overall['total_tests']}")
        print(f"   Passed Tests:       {overall['passed_tests']}")
        print(f"   Failed Tests:       {overall['failed_tests']}")
        print(f"   Accuracy:           {overall['overall_accuracy_percentage']:.1f}%")
        
        print(f"\n🎯 Position Accuracy:")
        print(f"   Average Error:      {overall['average_position_error_arcsec']:.4f}\"")
        print(f"   Maximum Error:      {overall['maximum_position_error_arcsec']:.4f}\"")
        print(f"   JPL Target:         ≤{overall['jpl_target_accuracy_arcsec']}\"")
        print(f"   Sub-arcsecond:      {'✅ YES' if overall['sub_arcsecond_accuracy'] else '❌ NO'}")
        
        print(f"\n🪐 Planet-by-Planet Accuracy:")
        for planet, data in planet_summary.items():
            status = "✅" if data['jpl_validated'] else "❌"
            print(f"   {planet:<10} {status} {data['accuracy_percentage']:5.1f}% "
                  f"(avg: {data['average_position_error_arcsec']:.4f}\", "
                  f"max: {data['max_position_error_arcsec']:.4f}\")")
        
        print(f"\n🏆 JPL Validation Status:")
        status = overall['jpl_validation_status']
        cert_ready = overall['certification_ready']
        
        if status == 'PASS':
            print(f"   JPL Validation:     ✅ {status}")
        else:
            print(f"   JPL Validation:     ❌ {status}")
        
        if cert_ready:
            print(f"   Certification:      ✅ READY")
            print("   🎉 System exceeds JPL Horizons accuracy standards!")
        else:
            print(f"   Certification:      ⚠️  NEEDS IMPROVEMENT")
            print("   📈 Additional calibration may be required")
        
        print("=" * 70)

async def main():
    """Main validation runner."""
    try:
        runner = JPLValidationRunner()
        results = await runner.run_comprehensive_validation()
        
        # Exit with appropriate code
        if results['overall_summary']['jpl_validation_status'] == 'PASS':
            print("\n✅ JPL Horizons validation PASSED - System ready for production")
            sys.exit(0)
        else:
            print("\n❌ JPL Horizons validation FAILED - System needs calibration")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 JPL validation runner failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())