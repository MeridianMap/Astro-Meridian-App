#!/usr/bin/env python3
"""
Simple JSON Generator for Comprehensive Ephemeris Output

This script generates a JSON structure that demonstrates the comprehensive ephemeris format
without relying on the full backend API stack.
"""

import json
from datetime import datetime


def generate_sample_comprehensive_output():
    """Generate a sample comprehensive ephemeris output structure."""
    
    output_data = {
        "generation_info": {
            "timestamp": datetime.now().isoformat(),
            "chart_type": "comprehensive_natal",
            "features_included": [
                "planets", "asteroids", "lunar_nodes", "lilith_points",
                "houses", "angles", "fixed_stars", "aspects",
                "hermetic_lots", "astrocartography", "essential_dignities"
            ],
            "description": "Complete comprehensive ephemeris structure based on architectural restructure"
        },
        
        "request_payload": {
            "subject": {
                "name": "Dallas Comprehensive Demo 1987-07-15 09:01",
                "datetime": {"iso_string": "1987-07-15T09:01:00"},
                "latitude": {"decimal": 32.7833333333},
                "longitude": {"decimal": -96.8},
                "timezone": {"name": "America/Chicago"}
            },
            "configuration": {
                "house_system": "P",
                "include_asteroids": True,
                "include_nodes": True,
                "include_lilith": True,
                "include_fixed_stars": True,
                "fixed_star_magnitude_limit": 2.5
            },
            "include_aspects": True,
            "aspect_orb_preset": "traditional",
            "metadata_level": "audit",
            "include_arabic_parts": True,
            "include_all_traditional_parts": True,
            "include_dignities": True,
            "include_astrocartography": True,
            "include_hermetic_lots": True
        },
        
        "response": {
            "success": True,
            
            "subject": {
                "name": "Dallas Comprehensive Demo 1987-07-15 09:01",
                "datetime": "1987-07-15T09:01:00-05:00",
                "latitude": 32.7833333333,
                "longitude": -96.8,
                "timezone": "America/Chicago",
                "julian_day": 2447012.0625,
                "calculation_metadata": {
                    "coordinate_system": "geocentric",
                    "reference_frame": "tropical",
                    "calculation_flags": ["SPEED", "SIDEREAL"]
                }
            },
            
            "planets": {
                "Sun": {
                    "name": "Sun",
                    "longitude": 293.4567,
                    "latitude": 0.0002,
                    "distance": 1.0154,
                    "longitude_speed": 0.9563,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Capricorn",
                    "sign_longitude": 23.4567,
                    "house_number": 8,
                    "element": "Earth",
                    "modality": "Cardinal"
                },
                "Moon": {
                    "name": "Moon",
                    "longitude": 156.7890,
                    "latitude": 2.1234,
                    "distance": 0.00257,
                    "longitude_speed": 13.2345,
                    "is_retrograde": False,
                    "motion_type": "direct", 
                    "sign_name": "Virgo",
                    "sign_longitude": 6.7890,
                    "house_number": 4,
                    "element": "Earth",
                    "modality": "Mutable"
                },
                "Mercury": {
                    "name": "Mercury",
                    "longitude": 310.1234,
                    "latitude": -1.5678,
                    "distance": 0.3456,
                    "longitude_speed": -0.5432,
                    "is_retrograde": True,
                    "motion_type": "retrograde",
                    "sign_name": "Aquarius", 
                    "sign_longitude": 10.1234,
                    "house_number": 9,
                    "element": "Air",
                    "modality": "Fixed"
                },
                "Venus": {
                    "name": "Venus",
                    "longitude": 275.8901,
                    "latitude": 1.2345,
                    "distance": 0.7234,
                    "longitude_speed": 1.2345,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Capricorn",
                    "sign_longitude": 5.8901,
                    "house_number": 7,
                    "element": "Earth", 
                    "modality": "Cardinal"
                },
                "Mars": {
                    "name": "Mars",
                    "longitude": 89.5678,
                    "latitude": -0.8901,
                    "distance": 1.4567,
                    "longitude_speed": 0.4567,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Gemini",
                    "sign_longitude": 29.5678,
                    "house_number": 3,
                    "element": "Air",
                    "modality": "Mutable"
                },
                "Jupiter": {
                    "name": "Jupiter",
                    "longitude": 45.2345,
                    "latitude": 0.3456,
                    "distance": 5.1234,
                    "longitude_speed": 0.0834,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Taurus",
                    "sign_longitude": 15.2345,
                    "house_number": 2,
                    "element": "Earth",
                    "modality": "Fixed"
                },
                "Saturn": {
                    "name": "Saturn",
                    "longitude": 225.6789,
                    "latitude": -1.2345,
                    "distance": 9.8765,
                    "longitude_speed": 0.0334,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Scorpio",
                    "sign_longitude": 15.6789,
                    "house_number": 6,
                    "element": "Water",
                    "modality": "Fixed"
                },
                "Uranus": {
                    "name": "Uranus",
                    "longitude": 342.3456,
                    "latitude": 0.5678,
                    "distance": 19.2345,
                    "longitude_speed": 0.0042,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Pisces",
                    "sign_longitude": 12.3456,
                    "house_number": 11,
                    "element": "Water",
                    "modality": "Mutable"
                },
                "Neptune": {
                    "name": "Neptune", 
                    "longitude": 67.8901,
                    "latitude": 1.0123,
                    "distance": 30.1234,
                    "longitude_speed": 0.0024,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Gemini",
                    "sign_longitude": 7.8901,
                    "house_number": 3,
                    "element": "Air",
                    "modality": "Mutable"
                },
                "Pluto": {
                    "name": "Pluto",
                    "longitude": 102.4567,
                    "latitude": -2.3456,
                    "distance": 39.4567,
                    "longitude_speed": 0.0016,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Cancer",
                    "sign_longitude": 12.4567,
                    "house_number": 4,
                    "element": "Water",
                    "modality": "Cardinal"
                }
            },
            
            "asteroids": {
                "Chiron": {
                    "name": "Chiron",
                    "longitude": 198.7654,
                    "latitude": 3.2109,
                    "distance": 18.9876,
                    "longitude_speed": 0.0456,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Libra",
                    "sign_longitude": 18.7654,
                    "house_number": 5,
                    "element": "Air",
                    "modality": "Cardinal"
                },
                "Ceres": {
                    "name": "Ceres",
                    "longitude": 123.4567,
                    "latitude": -1.8765,
                    "distance": 2.7654,
                    "longitude_speed": 0.2109,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Leo",
                    "sign_longitude": 3.4567,
                    "house_number": 4,
                    "element": "Fire",
                    "modality": "Fixed"
                },
                "Pallas": {
                    "name": "Pallas",
                    "longitude": 256.8901,
                    "latitude": 5.4321,
                    "distance": 2.1234,
                    "longitude_speed": 0.1876,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Sagittarius",
                    "sign_longitude": 16.8901,
                    "house_number": 7,
                    "element": "Fire",
                    "modality": "Mutable"
                },
                "Juno": {
                    "name": "Juno",
                    "longitude": 78.9012,
                    "latitude": -2.6789,
                    "distance": 1.9876,
                    "longitude_speed": 0.2345,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Gemini",
                    "sign_longitude": 18.9012,
                    "house_number": 3,
                    "element": "Air",
                    "modality": "Mutable"
                },
                "Vesta": {
                    "name": "Vesta",
                    "longitude": 345.6789,
                    "latitude": 1.2345,
                    "distance": 2.3456,
                    "longitude_speed": 0.1567,
                    "is_retrograde": False,
                    "motion_type": "direct",
                    "sign_name": "Pisces",
                    "sign_longitude": 15.6789,
                    "house_number": 11,
                    "element": "Water",
                    "modality": "Mutable"
                }
            },
            
            "lunar_nodes": {
                "True Node": {
                    "name": "True Node",
                    "longitude": 167.8901,
                    "latitude": 0.0,
                    "distance": 0.0,
                    "longitude_speed": -0.0529,
                    "is_retrograde": True,
                    "motion_type": "retrograde",
                    "sign_name": "Virgo",
                    "sign_longitude": 17.8901,
                    "house_number": 4,
                    "element": "Earth",
                    "modality": "Mutable"
                },
                "Mean Node": {
                    "name": "Mean Node",
                    "longitude": 167.5432,
                    "latitude": 0.0,
                    "distance": 0.0,
                    "longitude_speed": -0.0529,
                    "is_retrograde": True,
                    "motion_type": "retrograde",
                    "sign_name": "Virgo", 
                    "sign_longitude": 17.5432,
                    "house_number": 4,
                    "element": "Earth",
                    "modality": "Mutable"
                }
            },
            
            "lilith_points": {
                "Lilith (Mean)": {
                    "name": "Lilith (Mean)",
                    "longitude": 234.5678,
                    "latitude": 0.0,
                    "distance": 0.0,
                    "longitude_speed": -0.1107,
                    "is_retrograde": True,
                    "motion_type": "retrograde",
                    "sign_name": "Scorpio",
                    "sign_longitude": 24.5678,
                    "house_number": 6,
                    "element": "Water",
                    "modality": "Fixed"
                },
                "Lilith (True)": {
                    "name": "Lilith (True)",
                    "longitude": 235.1234,
                    "latitude": 0.0,
                    "distance": 0.0,
                    "longitude_speed": -0.1089,
                    "is_retrograde": True,
                    "motion_type": "retrograde",
                    "sign_name": "Scorpio",
                    "sign_longitude": 25.1234,
                    "house_number": 6,
                    "element": "Water",
                    "modality": "Fixed"
                }
            },
            
            "houses": {
                "system": "Placidus",
                "house_cusps": [
                    17.89, 48.23, 78.45, 108.67, 138.89, 169.12,
                    197.89, 228.23, 258.45, 288.67, 318.89, 349.12
                ],
                "houses": {
                    "house_1": 17.89,
                    "house_2": 48.23,
                    "house_3": 78.45,
                    "house_4": 108.67,
                    "house_5": 138.89,
                    "house_6": 169.12,
                    "house_7": 197.89,
                    "house_8": 228.23,
                    "house_9": 258.45,
                    "house_10": 288.67,
                    "house_11": 318.89,
                    "house_12": 349.12
                }
            },
            
            "angles": {
                "ASC": 17.89,
                "MC": 288.67,
                "DSC": 197.89,
                "IC": 108.67,
                "ARMC": 292.34,
                "Vertex": 234.56
            },
            
            "fixed_stars": [
                {
                    "name": "Regulus",
                    "longitude": 149.8901,
                    "latitude": 0.4567,
                    "magnitude": 1.36,
                    "right_ascension": 152.0123,
                    "declination": 11.9678,
                    "spectral_type": "B7V",
                    "constellation": "Leo"
                },
                {
                    "name": "Spica",
                    "longitude": 203.6789,
                    "latitude": -2.0987,
                    "magnitude": 0.97,
                    "right_ascension": 201.2987,
                    "declination": -11.1612,
                    "spectral_type": "B1III-IV",
                    "constellation": "Virgo"
                },
                {
                    "name": "Arcturus",
                    "longitude": 184.0543,
                    "latitude": 30.7123,
                    "magnitude": -0.05,
                    "right_ascension": 213.9154,
                    "declination": 19.1823,
                    "spectral_type": "K0III",
                    "constellation": "Boötes"
                }
            ],
            
            "aspects": [
                {
                    "object1": "Sun",
                    "object2": "Moon",
                    "aspect": "Square",
                    "angle": 86.7123,
                    "exact_angle": 90.0,
                    "orb": 3.2877,
                    "orb_percentage": 0.366,
                    "applying": False,
                    "strength": 0.634,
                    "aspect_type": "major"
                },
                {
                    "object1": "Mercury",
                    "object2": "Venus",
                    "aspect": "Conjunction",
                    "angle": 5.7667,
                    "exact_angle": 0.0,
                    "orb": 5.7667,
                    "orb_percentage": 0.577,
                    "applying": True,
                    "strength": 0.423,
                    "aspect_type": "major"
                },
                {
                    "object1": "Mars",
                    "object2": "Jupiter",
                    "aspect": "Sextile",
                    "angle": 62.3333,
                    "exact_angle": 60.0,
                    "orb": 2.3333,
                    "orb_percentage": 0.389,
                    "applying": False,
                    "strength": 0.611,
                    "aspect_type": "major"
                },
                {
                    "object1": "Saturn",
                    "object2": "Uranus",
                    "aspect": "Trine",
                    "angle": 117.0213,
                    "exact_angle": 120.0,
                    "orb": 2.9787,
                    "orb_percentage": 0.372,
                    "applying": True,
                    "strength": 0.628,
                    "aspect_type": "major"
                }
            ],
            
            "aspect_matrix": {
                "total_aspects": 15,
                "major_aspects": 12,
                "minor_aspects": 3,
                "orb_config_used": "traditional",
                "calculation_time_ms": 45.7
            },
            
            "hermetic_lots": [
                {
                    "name": "Part of Fortune",
                    "longitude": 45.6789,
                    "sign_name": "Taurus",
                    "sign_longitude": 15.6789,
                    "house_number": 2,
                    "formula_used": "day",
                    "element": "Earth",
                    "modality": "Fixed"
                },
                {
                    "name": "Part of Spirit",
                    "longitude": 213.4567,
                    "sign_name": "Scorpio",
                    "sign_longitude": 3.4567,
                    "house_number": 6,
                    "formula_used": "day",
                    "element": "Water",
                    "modality": "Fixed"
                },
                {
                    "name": "Part of Basis",
                    "longitude": 156.7890,
                    "sign_name": "Virgo",
                    "sign_longitude": 6.7890,
                    "house_number": 4,
                    "formula_used": "day",
                    "element": "Earth",
                    "modality": "Mutable"
                },
                {
                    "name": "Part of Love",
                    "longitude": 298.1234,
                    "sign_name": "Capricorn",
                    "sign_longitude": 28.1234,
                    "house_number": 8,
                    "formula_used": "day",
                    "element": "Earth",
                    "modality": "Cardinal"
                }
            ],
            
            "astrocartography": {
                "geojson": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [-96.8, 89.0],
                                    [-96.8, -89.0]
                                ]
                            },
                            "properties": {
                                "planet": "Sun",
                                "line_type": "AC",
                                "feature_id": "ACG_Sun_AC",
                                "line_category": "primary",
                                "intensity": 0.95
                            }
                        },
                        {
                            "type": "Feature", 
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [83.2, 89.0],
                                    [83.2, -89.0]
                                ]
                            },
                            "properties": {
                                "planet": "Sun",
                                "line_type": "MC",
                                "feature_id": "ACG_Sun_MC",
                                "line_category": "primary",
                                "intensity": 0.98
                            }
                        }
                    ]
                },
                "calculation_metadata": {
                    "total_lines": 84,
                    "primary_lines": 40,
                    "aspect_lines": 32,
                    "paran_lines": 12,
                    "coordinate_system": "geographical",
                    "projection": "cylindrical_equidistant"
                }
            },
            
            "essential_dignities": {
                "Sun": {
                    "total_score": 4,
                    "rulership_score": 0,
                    "exaltation_score": 0,
                    "triplicity_score": 3,
                    "term_score": 2,
                    "face_score": 0,
                    "dignities_held": ["triplicity", "term"]
                },
                "Moon": {
                    "total_score": -1,
                    "rulership_score": 0,
                    "exaltation_score": -5,
                    "triplicity_score": 0,
                    "term_score": 2,
                    "face_score": 1,
                    "dignities_held": ["fall", "term", "face"]
                },
                "Mercury": {
                    "total_score": 7,
                    "rulership_score": 5,
                    "exaltation_score": 0,
                    "triplicity_score": 0,
                    "term_score": 2,
                    "face_score": 0,
                    "dignities_held": ["rulership", "term"]
                }
            },
            
            "calculation_metadata": {
                "julian_day": 2447012.0625,
                "calculation_time": 0.285,
                "total_objects_calculated": 19,
                "features_included": [
                    "planets", "asteroids", "lunar_nodes", "lilith_points",
                    "houses", "angles", "fixed_stars", "aspects", 
                    "hermetic_lots", "astrocartography", "essential_dignities"
                ],
                "house_system": "P",
                "coordinate_system": "geocentric",
                "reference_frame": "tropical",
                "calculation_flags": ["SPEED", "SIDEREAL"],
                "swiss_ephemeris_version": "2.10.03",
                "performance_metrics": {
                    "planet_calculation_time": 0.045,
                    "house_calculation_time": 0.012,
                    "aspect_calculation_time": 0.089,
                    "hermetic_lots_calculation_time": 0.034,
                    "acg_calculation_time": 0.156,
                    "dignity_calculation_time": 0.023
                },
                "orb_system_used": "traditional",
                "sect_determination": "day_chart"
            },
            
            "warnings": [
                "Fixed star Spica slightly below specified magnitude limit",
                "Some aspect calculations may have precision variations due to high-speed objects"
            ],
            
            "chart_type": "comprehensive_natal"
        }
    }
    
    return output_data


def main():
    """Generate and save comprehensive JSON output."""
    print("Generating Comprehensive Ephemeris JSON Structure...")
    print("This demonstrates the complete API response format after architectural restructure")
    print("-" * 70)
    
    output_data = generate_sample_comprehensive_output()
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"COMPREHENSIVE_EPHEMERIS_STRUCTURE_{timestamp}.json"
    
    # Write output
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated comprehensive JSON structure: {filename}")
    print("\nStructure Summary:")
    print(f"   - Traditional Planets: 10")
    print(f"   - Major Asteroids: 5") 
    print(f"   - Lunar Nodes: 2")
    print(f"   - Lilith Points: 2")
    print(f"   - House System: Placidus")
    print(f"   - Chart Angles: 6")
    print(f"   - Fixed Stars: 3 (magnitude <= 2.0)")
    print(f"   - Major Aspects: 4 sample")
    print(f"   - Hermetic Lots: 4 traditional")
    print(f"   - ACG Lines: 2 sample (Sun AC/MC)")
    print(f"   - Essential Dignities: 3 planets")
    print(f"   - Performance Metrics: Complete")
    
    print("\nThis JSON structure represents the unified ComprehensiveChartResponse model")
    print("that consolidates all ephemeris features into a single, comprehensive format.")
    
    return filename


if __name__ == "__main__":
    try:
        output_file = main()
        print(f"\nUse this file to review the complete JSON structure: {output_file}")
    except KeyboardInterrupt:
        print("\nGeneration cancelled by user")
    except Exception as e:
        print(f"\nError generating JSON: {e}")