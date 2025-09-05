#!/usr/bin/env python3
"""
NASA Validation Script

Comprehensive validation script for eclipse predictions against NASA's
Five Millennium Canon. Generates detailed accuracy reports and validation
certificates for production deployment.
"""

import sys
import asyncio
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ephemeris.tools.validation import nasa_validator, ValidationResult
from app.core.ephemeris.tools.eclipse_calculator import EclipseCalculator
from app.core.ephemeris.tools.predictive_models import SolarEclipse, LunarEclipse

class NASAValidationRunner:
    """Comprehensive NASA validation test runner."""
    
    def __init__(self):
        """Initialize validation runner."""
        self.validator = nasa_validator
        self.eclipse_calculator = EclipseCalculator()
        self.results = []
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """
        Run comprehensive validation against NASA data.
        
        Returns:
            Detailed validation report
        """
        print("🚀 Starting NASA Eclipse Validation Suite")
        print("=" * 60)
        
        # Load NASA eclipse catalog
        print("📚 Loading NASA Eclipse Catalog...")
        eclipse_catalog = self.validator.load_nasa_eclipse_catalog()
        solar_eclipses = eclipse_catalog.get('solar_eclipses', [])
        lunar_eclipses = eclipse_catalog.get('lunar_eclipses', [])
        
        print(f"   Found {len(solar_eclipses)} solar eclipses in catalog")
        print(f"   Found {len(lunar_eclipses)} lunar eclipses in catalog")
        
        validation_results = {
            'solar_eclipse_results': [],
            'lunar_eclipse_results': [],
            'summary': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Validate solar eclipses
        print("\n☀️  Validating Solar Eclipses...")
        solar_results = await self._validate_solar_eclipses(solar_eclipses[:10])  # Test first 10
        validation_results['solar_eclipse_results'] = solar_results
        
        # Validate lunar eclipses  
        print("\n🌙 Validating Lunar Eclipses...")
        lunar_results = await self._validate_lunar_eclipses(lunar_eclipses[:10])  # Test first 10
        validation_results['lunar_eclipse_results'] = lunar_results
        
        # Generate summary
        print("\n📊 Generating Validation Summary...")
        summary = self._generate_summary(solar_results, lunar_results)
        validation_results['summary'] = summary
        
        # Save results
        self._save_validation_report(validation_results)
        
        # Print results
        self._print_validation_results(summary)
        
        return validation_results
    
    async def _validate_solar_eclipses(self, reference_eclipses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate solar eclipse calculations."""
        results = []
        
        for i, ref_eclipse in enumerate(reference_eclipses, 1):
            print(f"   Testing solar eclipse {i}/{len(reference_eclipses)}: {ref_eclipse['catalog_id']}")
            
            try:
                # Parse reference data
                ref_time = datetime.fromisoformat(ref_eclipse['date'])
                
                # Calculate eclipse using our engine
                calculated_eclipse = self.eclipse_calculator.find_next_solar_eclipse(
                    ref_time - timedelta(days=1),  # Start search 1 day before
                    eclipse_type=ref_eclipse.get('type')
                )
                
                if calculated_eclipse:
                    # Validate against NASA data
                    validation = self.validator.validate_eclipse_against_canon(calculated_eclipse)
                    
                    result = {
                        'reference_id': ref_eclipse['catalog_id'],
                        'reference_time': ref_eclipse['date'],
                        'calculated_time': calculated_eclipse.maximum_eclipse_time.isoformat(),
                        'timing_error_seconds': validation.timing_error_seconds,
                        'magnitude_error': validation.magnitude_error,
                        'passed': validation.is_valid,
                        'notes': validation.notes
                    }
                else:
                    result = {
                        'reference_id': ref_eclipse['catalog_id'],
                        'reference_time': ref_eclipse['date'],
                        'calculated_time': None,
                        'timing_error_seconds': float('inf'),
                        'magnitude_error': None,
                        'passed': False,
                        'notes': 'Eclipse not found by calculator'
                    }
                
                results.append(result)
                
                # Progress indicator
                if validation.is_valid if calculated_eclipse else False:
                    print(f"     ✅ PASS - Error: {validation.timing_error_seconds:.1f}s")
                else:
                    print(f"     ❌ FAIL - Error: {validation.timing_error_seconds:.1f}s")
                
            except Exception as e:
                result = {
                    'reference_id': ref_eclipse['catalog_id'],
                    'reference_time': ref_eclipse['date'],
                    'calculated_time': None,
                    'timing_error_seconds': float('inf'),
                    'magnitude_error': None,
                    'passed': False,
                    'notes': f'Validation error: {e}'
                }
                results.append(result)
                print(f"     ❌ ERROR - {e}")
        
        return results
    
    async def _validate_lunar_eclipses(self, reference_eclipses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate lunar eclipse calculations."""
        results = []
        
        for i, ref_eclipse in enumerate(reference_eclipses, 1):
            print(f"   Testing lunar eclipse {i}/{len(reference_eclipses)}: {ref_eclipse['catalog_id']}")
            
            try:
                # Parse reference data
                ref_time = datetime.fromisoformat(ref_eclipse['date'])
                
                # Calculate eclipse using our engine
                calculated_eclipse = self.eclipse_calculator.find_next_lunar_eclipse(
                    ref_time - timedelta(days=1),  # Start search 1 day before
                    eclipse_type=ref_eclipse.get('type')
                )
                
                if calculated_eclipse:
                    # Validate against NASA data
                    validation = self.validator.validate_eclipse_against_canon(calculated_eclipse)
                    
                    result = {
                        'reference_id': ref_eclipse['catalog_id'],
                        'reference_time': ref_eclipse['date'],
                        'calculated_time': calculated_eclipse.maximum_eclipse_time.isoformat(),
                        'timing_error_seconds': validation.timing_error_seconds,
                        'magnitude_error': validation.magnitude_error,
                        'passed': validation.is_valid,
                        'notes': validation.notes
                    }
                else:
                    result = {
                        'reference_id': ref_eclipse['catalog_id'],
                        'reference_time': ref_eclipse['date'],
                        'calculated_time': None,
                        'timing_error_seconds': float('inf'),
                        'magnitude_error': None,
                        'passed': False,
                        'notes': 'Eclipse not found by calculator'
                    }
                
                results.append(result)
                
                # Progress indicator
                if validation.is_valid if calculated_eclipse else False:
                    print(f"     ✅ PASS - Error: {validation.timing_error_seconds:.1f}s")
                else:
                    print(f"     ❌ FAIL - Error: {validation.timing_error_seconds:.1f}s")
                
            except Exception as e:
                result = {
                    'reference_id': ref_eclipse['catalog_id'],
                    'reference_time': ref_eclipse['date'],
                    'calculated_time': None,
                    'timing_error_seconds': float('inf'),
                    'magnitude_error': None,
                    'passed': False,
                    'notes': f'Validation error: {e}'
                }
                results.append(result)
                print(f"     ❌ ERROR - {e}")
        
        return results
    
    def _generate_summary(self, solar_results: List[Dict], lunar_results: List[Dict]) -> Dict[str, Any]:
        """Generate validation summary statistics."""
        all_results = solar_results + lunar_results
        
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        # Calculate timing statistics
        timing_errors = [r['timing_error_seconds'] for r in all_results if r['timing_error_seconds'] != float('inf')]
        avg_timing_error = sum(timing_errors) / len(timing_errors) if timing_errors else 0
        max_timing_error = max(timing_errors) if timing_errors else 0
        
        # Calculate magnitude statistics
        magnitude_errors = [r['magnitude_error'] for r in all_results if r['magnitude_error'] is not None]
        avg_magnitude_error = sum(magnitude_errors) / len(magnitude_errors) if magnitude_errors else 0
        max_magnitude_error = max(magnitude_errors) if magnitude_errors else 0
        
        accuracy_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'accuracy_percentage': accuracy_percentage,
            'solar_eclipse_accuracy': (sum(1 for r in solar_results if r['passed']) / len(solar_results)) * 100 if solar_results else 0,
            'lunar_eclipse_accuracy': (sum(1 for r in lunar_results if r['passed']) / len(lunar_results)) * 100 if lunar_results else 0,
            'average_timing_error_seconds': avg_timing_error,
            'maximum_timing_error_seconds': max_timing_error,
            'average_magnitude_error': avg_magnitude_error,
            'maximum_magnitude_error': max_magnitude_error,
            'nasa_validation_status': 'PASS' if accuracy_percentage >= 95.0 else 'FAIL',
            'certification_ready': accuracy_percentage >= 99.0 and max_timing_error <= 60.0
        }
    
    def _save_validation_report(self, results: Dict[str, Any]):
        """Save validation report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON report
        json_file = Path(__file__).parent.parent / f"validation_reports/nasa_validation_{timestamp}.json"
        json_file.parent.mkdir(exist_ok=True)
        
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save CSV report
        csv_file = Path(__file__).parent.parent / f"validation_reports/nasa_validation_{timestamp}.csv"
        
        all_results = results['solar_eclipse_results'] + results['lunar_eclipse_results']
        
        with open(csv_file, 'w', newline='') as f:
            if all_results:
                writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
                writer.writeheader()
                writer.writerows(all_results)
        
        print(f"\n💾 Validation reports saved:")
        print(f"   JSON: {json_file}")
        print(f"   CSV:  {csv_file}")
    
    def _print_validation_results(self, summary: Dict[str, Any]):
        """Print formatted validation results."""
        print("\n" + "=" * 60)
        print("🎯 NASA ECLIPSE VALIDATION RESULTS")
        print("=" * 60)
        
        print(f"📊 Overall Statistics:")
        print(f"   Total Tests:        {summary['total_tests']}")
        print(f"   Passed Tests:       {summary['passed_tests']}")
        print(f"   Failed Tests:       {summary['failed_tests']}")
        print(f"   Accuracy:           {summary['accuracy_percentage']:.1f}%")
        
        print(f"\n🌟 Eclipse Type Breakdown:")
        print(f"   Solar Eclipses:     {summary['solar_eclipse_accuracy']:.1f}%")
        print(f"   Lunar Eclipses:     {summary['lunar_eclipse_accuracy']:.1f}%")
        
        print(f"\n⏱️  Timing Accuracy:")
        print(f"   Average Error:      {summary['average_timing_error_seconds']:.2f} seconds")
        print(f"   Maximum Error:      {summary['maximum_timing_error_seconds']:.2f} seconds")
        print(f"   NASA Target:        ≤60 seconds")
        
        print(f"\n📏 Magnitude Accuracy:")
        print(f"   Average Error:      {summary['average_magnitude_error']:.4f}")
        print(f"   Maximum Error:      {summary['maximum_magnitude_error']:.4f}")
        print(f"   NASA Target:        ≤0.01")
        
        print(f"\n🏆 Validation Status:")
        status = summary['nasa_validation_status']
        cert_ready = summary['certification_ready']
        
        if status == 'PASS':
            print(f"   NASA Validation:    ✅ {status}")
        else:
            print(f"   NASA Validation:    ❌ {status}")
        
        if cert_ready:
            print(f"   Certification:      ✅ READY")
            print("   🎉 System meets NASA accuracy standards!")
        else:
            print(f"   Certification:      ⚠️  NEEDS IMPROVEMENT")
            print("   📈 Additional calibration may be required")
        
        print("=" * 60)

async def main():
    """Main validation runner."""
    try:
        runner = NASAValidationRunner()
        results = await runner.run_comprehensive_validation()
        
        # Exit with appropriate code
        if results['summary']['nasa_validation_status'] == 'PASS':
            print("\n✅ NASA validation PASSED - System ready for production")
            sys.exit(0)
        else:
            print("\n❌ NASA validation FAILED - System needs calibration")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Validation runner failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())