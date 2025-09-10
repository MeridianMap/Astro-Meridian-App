"""
Swiss Ephemeris Celestial Body Validation Script

Validates all celestial bodies in the ACG registry against Swiss Ephemeris
to ensure exact naming conventions and ID numbers are correct.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import swisseph as swe
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Import ACG components
from extracted.systems.acg_engine.acg_core import ACGCalculationEngine
from extracted.systems.acg_engine.acg_types import ACGBodyType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
if not logger.handlers: logging.basicConfig(level=logging.INFO)


class CelestialBodyValidator:
    """Validates celestial bodies against Swiss Ephemeris."""
    
    def __init__(self):
        self.engine = ACGCalculationEngine()
        self.test_jd = 2451545.0  # J2000.0 epoch
        self.validation_results = {
            "planets": [],
            "asteroids": [],
            "fixed_stars": [],
            "nodes_points": []
        }
    
    def validate_all_bodies(self) -> Dict[str, Any]:
        """
        Validate all registered celestial bodies.
        
        Returns:
            Dictionary with validation results and recommendations
        """
        logger.info("Starting comprehensive celestial body validation...")
        
        # Get all registered bodies
        bodies = self.engine.body_registry
        
        for body_def in bodies:
            body_type = body_def.get("type")
            
            if body_type == ACGBodyType.PLANET:
                self._validate_planet(body_def)
            elif body_type in [ACGBodyType.ASTEROID, ACGBodyType.DWARF]:
                self._validate_asteroid(body_def)
            elif body_type == ACGBodyType.FIXED_STAR:
                self._validate_fixed_star(body_def)
            elif body_type in [ACGBodyType.NODE, ACGBodyType.POINT]:
                self._validate_node_point(body_def)
        
        return self._generate_report()
    
    def _validate_planet(self, body_def: Dict[str, Any]) -> None:
        """Validate a planetary body."""
        body_id = body_def["id"]
        se_id = body_def.get("se_id")
        
        try:
            result = swe.calc_ut(self.test_jd, se_id, swe.FLG_SWIEPH)
            self.validation_results["planets"].append({
                "id": body_id,
                "se_id": se_id,
                "status": "valid",
                "coordinates": result[0][:3]  # lon, lat, distance
            })
            logger.info(f"✅ Planet {body_id} (SE ID: {se_id}) - Valid")
            
        except Exception as e:
            self.validation_results["planets"].append({
                "id": body_id,
                "se_id": se_id,
                "status": "error",
                "error": str(e)
            })
            logger.error(f"❌ Planet {body_id} (SE ID: {se_id}) - Error: {e}")
    
    def _validate_asteroid(self, body_def: Dict[str, Any]) -> None:
        """Validate an asteroid/dwarf planet."""
        body_id = body_def["id"]
        se_id = body_def.get("se_id")
        
        try:
            result = swe.calc_ut(self.test_jd, se_id, swe.FLG_SWIEPH)
            self.validation_results["asteroids"].append({
                "id": body_id,
                "se_id": se_id,
                "status": "valid",
                "coordinates": result[0][:3]
            })
            logger.info(f"✅ Asteroid {body_id} (SE ID: {se_id}) - Valid")
            
        except Exception as e:
            self.validation_results["asteroids"].append({
                "id": body_id,
                "se_id": se_id,
                "status": "error",
                "error": str(e)
            })
            logger.error(f"❌ Asteroid {body_id} (SE ID: {se_id}) - Error: {e}")
    
    def _validate_fixed_star(self, body_def: Dict[str, Any]) -> None:
        """Validate a fixed star."""
        body_id = body_def["id"]
        se_name = body_def.get("se_name")
        
        try:
            result = swe.fixstar_ut(se_name, self.test_jd, swe.FLG_SWIEPH)
            
            if len(result) >= 2 and result[1] == "":  # No error message
                self.validation_results["fixed_stars"].append({
                    "id": body_id,
                    "se_name": se_name,
                    "status": "valid",
                    "coordinates": result[0][:3],
                    "star_info": result[1] if len(result) > 1 else ""
                })
                logger.info(f"✅ Fixed Star {body_id} ('{se_name}') - Valid")
            else:
                error_msg = result[1] if len(result) > 1 else "Unknown error"
                self.validation_results["fixed_stars"].append({
                    "id": body_id,
                    "se_name": se_name,
                    "status": "error",
                    "error": error_msg
                })
                logger.error(f"❌ Fixed Star {body_id} ('{se_name}') - Error: {error_msg}")
                
        except Exception as e:
            self.validation_results["fixed_stars"].append({
                "id": body_id,
                "se_name": se_name,
                "status": "error",
                "error": str(e)
            })
            logger.error(f"❌ Fixed Star {body_id} ('{se_name}') - Exception: {e}")
    
    def _validate_node_point(self, body_def: Dict[str, Any]) -> None:
        """Validate lunar nodes and calculated points."""
        body_id = body_def["id"]
        se_id = body_def.get("se_id")
        
        try:
            result = swe.calc_ut(self.test_jd, se_id, swe.FLG_SWIEPH)
            self.validation_results["nodes_points"].append({
                "id": body_id,
                "se_id": se_id,
                "status": "valid",
                "coordinates": result[0][:3]
            })
            logger.info(f"✅ Node/Point {body_id} (SE ID: {se_id}) - Valid")
            
        except Exception as e:
            self.validation_results["nodes_points"].append({
                "id": body_id,
                "se_id": se_id,
                "status": "error", 
                "error": str(e)
            })
            logger.error(f"❌ Node/Point {body_id} (SE ID: {se_id}) - Error: {e}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "swiss_ephemeris_version": swe.version,
            "test_julian_day": self.test_jd,
            "results": self.validation_results,
            "summary": {},
            "recommendations": []
        }
        
        # Generate summary statistics
        for category, results in self.validation_results.items():
            valid_count = sum(1 for r in results if r["status"] == "valid")
            total_count = len(results)
            error_count = total_count - valid_count
            
            report["summary"][category] = {
                "total": total_count,
                "valid": valid_count,
                "errors": error_count,
                "success_rate": f"{(valid_count/total_count*100):.1f}%" if total_count > 0 else "N/A"
            }
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Check for fixed star naming issues
        star_errors = [r for r in self.validation_results["fixed_stars"] if r["status"] == "error"]
        if star_errors:
            recommendations.append(
                f"Fixed Star Naming Issues: {len(star_errors)} stars failed validation. "
                "Consider using Swiss Ephemeris star catalog names or alternative spellings."
            )
        
        # Check for asteroid ID issues
        asteroid_errors = [r for r in self.validation_results["asteroids"] if r["status"] == "error"]
        if asteroid_errors:
            recommendations.append(
                f"Asteroid ID Issues: {len(asteroid_errors)} asteroids failed validation. "
                "Verify minor planet numbers against MPC catalog."
            )
        
        # Check for planet issues (should be rare)
        planet_errors = [r for r in self.validation_results["planets"] if r["status"] == "error"]
        if planet_errors:
            recommendations.append(
                f"Planet Issues: {len(planet_errors)} planets failed validation. "
                "Check Swiss Ephemeris constants and installation."
            )
        
        return recommendations
    
    def get_corrected_star_names(self) -> Dict[str, str]:
        """
        Get corrected star names based on Swiss Ephemeris catalog.
        
        Returns:
            Dictionary mapping current names to corrected names
        """
        corrections = {}
        
        # Common Swiss Ephemeris star name variations
        se_star_catalog = {
            # Our name -> Correct SE name
            "Fomalhaut": "Fomalhaut",
            "Deneb": "Deneb Cygni", 
            "Alcyone": "Alcyone",
            "Achernar": "Achernar",
            "Acrux": "Acrux", 
            "Alphecca": "Alphecca",
            "Rasalhague": "Rasalhague",
            "Denebola": "Denebola",
            "Markab": "Markab",
            "Alpheratz": "Alpheratz",
            "Scheat": "Scheat",
            "Pollux": "Pollux",
            "Castor": "Castor", 
            "Hamal": "Hamal"
        }
        
        # Test each name
        for our_name, se_name in se_star_catalog.items():
            try:
                swe.fixstar_ut(se_name, self.test_jd, swe.FLG_SWIEPH)
                if our_name != se_name:
                    corrections[our_name] = se_name
            except:
                # Try alternative naming patterns
                alternatives = [
                    f"alpha {se_name.split()[0] if ' ' in se_name else se_name}",
                    f"{se_name} alpha",
                    se_name.replace(" ", ""),
                    se_name.lower(),
                    se_name.capitalize()
                ]
                
                for alt_name in alternatives:
                    try:
                        swe.fixstar_ut(alt_name, self.test_jd, swe.FLG_SWIEPH)
                        corrections[our_name] = alt_name
                        break
                    except:
                        continue
        
        return corrections


def main():
    """Main validation function."""
    print("Swiss Ephemeris Celestial Body Validation")
    print("=" * 50)
    
    validator = CelestialBodyValidator()
    report = validator.validate_all_bodies()
    
    # Print summary
    print(f"\nValidation Summary (SE Version: {report['swiss_ephemeris_version']})")
    print("-" * 40)
    
    for category, summary in report["summary"].items():
        print(f"{category.replace('_', ' ').title()}: {summary['valid']}/{summary['total']} valid ({summary['success_rate']})")
    
    # Print errors
    print(f"\nValidation Errors")
    print("-" * 20)
    
    total_errors = 0
    for category, results in report["results"].items():
        errors = [r for r in results if r["status"] == "error"]
        if errors:
            print(f"\n{category.replace('_', ' ').title()}:")
            for error in errors:
                print(f"  - {error['id']}: {error.get('error', 'Unknown error')}")
                total_errors += 1
    
    if total_errors == 0:
        print("  No errors found!")
    
    # Print recommendations
    if report["recommendations"]:
        print(f"\nRecommendations")
        print("-" * 20)
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")
    
    # Generate star name corrections
    print(f"\nStar Name Corrections")
    print("-" * 25)
    corrections = validator.get_corrected_star_names()
    if corrections:
        for old_name, new_name in corrections.items():
            print(f"  '{old_name}' -> '{new_name}'")
    else:
        print("  No corrections needed or found.")
    
    return report


if __name__ == "__main__":
    report = main()