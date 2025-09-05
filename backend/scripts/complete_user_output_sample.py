"""
Complete User Output Sample Generator

Creates the COMPLETE dataset that a user would receive when they input their 
birth information and request both natal chart + ACG lines. This demonstrates
the full system capabilities and data structure.

This shows what happens when user hits "GO" with complete birth data:
- Birth: June 15, 1990, 2:30 PM, New York City
- House System: Placidus (default)
- Request: Complete natal chart + ACG lines with natal context
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def create_complete_user_output():
    """Create complete user output showing both natal chart + ACG with natal context."""
    
    print("Creating Complete User Output Sample...")
    print("=" * 50)
    print("User Input:")
    print("- Name: John Doe")
    print("- Birth: June 15, 1990, 2:30 PM")
    print("- Location: New York City (40.7128°N, 74.0060°W)")
    print("- House System: Placidus")
    print("- Request: Complete natal chart + ACG lines")
    print("=" * 50)
    
    # This represents what the user gets: TWO separate but related datasets
    
    # PART 1: Enhanced Natal Chart Response (/ephemeris/v2/natal-enhanced)
    natal_chart_response = {
        "success": True,
        "chart_type": "natal_enhanced",
        "subject": {
            "name": "John Doe",
            "datetime": {
                "iso_string": "1990-06-15T14:30:00-04:00",
                "utc_string": "1990-06-15T18:30:00Z",
                "jd": 2448068.27083,
                "timezone": "America/New_York"
            },
            "coordinates": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "altitude": 10.0
            }
        },
        "planets": [
            {
                "name": "Sun",
                "symbol": "☉",
                "longitude": 93.4567,
                "latitude": 0.0003,
                "distance": 1.0156,
                "longitude_speed": 0.9582,
                "retrograde": False,
                "sign": "Cancer",
                "sign_longitude": 3.4567,
                "house": 4,
                "dignity": {
                    "essential": "fall",
                    "accidental": "angular"
                },
                "element": "Water",
                "modality": "Cardinal",
                "decanate": 1,
                "dwad": "Cancer"
            },
            {
                "name": "Moon",
                "symbol": "☽",
                "longitude": 156.2341,
                "latitude": 2.1456,
                "distance": 0.00256,
                "longitude_speed": 13.1763,
                "retrograde": False,
                "sign": "Virgo",
                "sign_longitude": 6.2341,
                "house": 7,
                "dignity": {
                    "essential": "neutral",
                    "accidental": "angular"
                },
                "element": "Earth",
                "modality": "Mutable",
                "decanate": 1,
                "dwad": "Virgo"
            },
            {
                "name": "Mercury",
                "symbol": "☿",
                "longitude": 78.9876,
                "latitude": 1.2345,
                "distance": 0.6789,
                "longitude_speed": 1.2345,
                "retrograde": True,
                "sign": "Gemini",
                "sign_longitude": 18.9876,
                "house": 3,
                "dignity": {
                    "essential": "domicile",
                    "accidental": "cadent"
                },
                "element": "Air",
                "modality": "Mutable",
                "decanate": 2,
                "dwad": "Libra"
            },
            {
                "name": "Venus",
                "symbol": "♀",
                "longitude": 45.6789,
                "latitude": 0.8901,
                "distance": 0.7234,
                "longitude_speed": 0.9876,
                "retrograde": False,
                "sign": "Taurus",
                "sign_longitude": 15.6789,
                "house": 2,
                "dignity": {
                    "essential": "domicile",
                    "accidental": "succeedent"
                },
                "element": "Earth",
                "modality": "Fixed",
                "decanate": 2,
                "dwad": "Virgo"
            }
        ],
        "houses": {
            "system": "placidus",
            "cusps": [
                15.2345,   # House 1 (Ascendant)
                45.6789,   # House 2
                75.9012,   # House 3
                105.2345,  # House 4 (IC)
                135.6789,  # House 5
                165.9012,  # House 6
                195.2345,  # House 7 (Descendant)
                225.6789,  # House 8
                255.9012,  # House 9
                285.2345,  # House 10 (MC)
                315.6789,  # House 11
                345.9012   # House 12
            ],
            "angles": {
                "asc": 15.2345,
                "ic": 105.2345,
                "dc": 195.2345,
                "mc": 285.2345
            }
        },
        "aspects": [
            {
                "object1": "Sun",
                "object2": "Moon",
                "aspect": "sextile",
                "angle": 62.78,
                "orb": 2.78,
                "exact_angle": 60.0,
                "applying": False,
                "strength": 0.652,
                "orb_percentage": 46.3
            },
            {
                "object1": "Sun",
                "object2": "Venus",
                "aspect": "trine",
                "angle": 122.22,
                "orb": 2.22,
                "exact_angle": 120.0,
                "applying": True,
                "strength": 0.722,
                "orb_percentage": 37.0
            },
            {
                "object1": "Mercury",
                "object2": "Venus",
                "aspect": "square",
                "angle": 86.7,
                "orb": 3.3,
                "exact_angle": 90.0,
                "applying": False,
                "strength": 0.45,
                "orb_percentage": 55.0
            }
        ],
        "aspect_matrix": {
            "total_aspects": 3,
            "major_aspects": 3,
            "minor_aspects": 0,
            "orb_config_used": "Traditional",
            "calculation_time_ms": 47.2
        },
        "arabic_parts": {
            "parts": [
                {
                    "name": "Part of Fortune",
                    "symbol": "⊗",
                    "longitude": 234.5678,
                    "sign": "Scorpio",
                    "sign_longitude": 24.5678,
                    "house": 11,
                    "formula": "day_formula",
                    "calculation": "Asc + Moon - Sun",
                    "traditional": True
                },
                {
                    "name": "Part of Spirit",
                    "symbol": "⊙",
                    "longitude": 198.7654,
                    "sign": "Libra",
                    "sign_longitude": 18.7654,
                    "house": 8,
                    "formula": "day_formula",
                    "calculation": "Asc + Sun - Moon",
                    "traditional": True
                }
            ],
            "sect_determination": {
                "sect": "day",
                "sun_above_horizon": True,
                "calculation_method": "traditional"
            },
            "calculation_time_ms": 23.4
        },
        "calculation_metadata": {
            "calculation_time_ms": 156.7,
            "ephemeris_version": "2.10.03",
            "features_included": ["aspects", "arabic_parts", "retrograde_analysis"],
            "house_system_used": "placidus",
            "aspect_orb_preset": "traditional",
            "coordinate_system": "geocentric",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # PART 2: ACG Lines with Full Natal Context (/acg/lines with natal integration)
    acg_with_natal_response = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-180.0, -12.8],
                        [-120.0, -8.4],
                        [-60.0, -3.2],
                        [0.0, 2.1],
                        [60.0, 7.8],
                        [120.0, 13.5],
                        [180.0, 18.9]
                    ]
                },
                "properties": {
                    "id": "Sun",
                    "type": "body",
                    "kind": "planet",
                    "epoch": "1990-06-15T18:30:00Z",
                    "jd": 2448068.27083,
                    "gmst": 267.4521,
                    "obliquity": 23.4392911,
                    "coords": {
                        "ra": 91.2345,
                        "dec": 23.4567,
                        "lambda_": 93.4567,
                        "beta": 0.0003,
                        "distance": 1.0156,
                        "speed": 0.9582
                    },
                    "line": {
                        "angle": "MC",
                        "line_type": "MC",
                        "method": "swiss_ephemeris_v2.10.03",
                        "orb": 1.0
                    },
                    "natal": {
                        "dignity": "fall",
                        "house": 4,
                        "retrograde": False,
                        "sign": "Cancer",
                        "element": "Water",
                        "modality": "Cardinal",
                        "aspects": [
                            {
                                "planet": "Moon",
                                "aspect": "sextile",
                                "orb": 2.78,
                                "applying": False,
                                "strength": 0.652
                            },
                            {
                                "planet": "Venus", 
                                "aspect": "trine",
                                "orb": 2.22,
                                "applying": True,
                                "strength": 0.722
                            }
                        ]
                    },
                    "calculation_time_ms": 18.4,
                    "number": 0,
                    "flags": 2,
                    "se_version": "2.10.03",
                    "source": "Meridian-ACG",
                    "color": "#FFD700",
                    "z_index": 10,
                    "hit_radius": 2.5,
                    "influence_radius_miles": 0.0,
                    "render_orb_only": False
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-180.0, 45.2],
                        [-120.0, 38.7],
                        [-60.0, 31.4],
                        [0.0, 23.8],
                        [60.0, 15.9],
                        [120.0, 8.2],
                        [180.0, 0.3]
                    ]
                },
                "properties": {
                    "id": "Moon",
                    "type": "body",
                    "kind": "planet",
                    "epoch": "1990-06-15T18:30:00Z",
                    "jd": 2448068.27083,
                    "gmst": 267.4521,
                    "obliquity": 23.4392911,
                    "coords": {
                        "ra": 154.1234,
                        "dec": 11.2345,
                        "lambda_": 156.2341,
                        "beta": 2.1456,
                        "distance": 0.00256,
                        "speed": 13.1763
                    },
                    "line": {
                        "angle": "AC",
                        "line_type": "AC",
                        "method": "swiss_ephemeris_v2.10.03",
                        "orb": 1.0
                    },
                    "natal": {
                        "dignity": "neutral",
                        "house": 7,
                        "retrograde": False,
                        "sign": "Virgo",
                        "element": "Earth",
                        "modality": "Mutable",
                        "aspects": [
                            {
                                "planet": "Sun",
                                "aspect": "sextile",
                                "orb": 2.78,
                                "applying": False,
                                "strength": 0.652
                            }
                        ]
                    },
                    "calculation_time_ms": 14.7,
                    "number": 1,
                    "flags": 2,
                    "se_version": "2.10.03",
                    "source": "Meridian-ACG",
                    "color": "#C0C0C0",
                    "z_index": 9,
                    "hit_radius": 2.5,
                    "influence_radius_miles": 0.0,
                    "render_orb_only": False
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [40.7128, -74.0060]
                },
                "properties": {
                    "id": "LilithMean",
                    "type": "body",
                    "kind": "point",
                    "epoch": "1990-06-15T18:30:00Z",
                    "jd": 2448068.27083,
                    "gmst": 267.4521,
                    "obliquity": 23.4392911,
                    "coords": {
                        "ra": 278.9876,
                        "dec": -8.1234,
                        "lambda_": 280.1234,
                        "beta": 1.5678,
                        "distance": None,
                        "speed": 0.1111
                    },
                    "line": {
                        "angle": "point",
                        "line_type": "orb_only",
                        "method": "swiss_ephemeris_v2.10.03",
                        "orb": 1.0
                    },
                    "natal": {
                        "dignity": None,
                        "house": 10,
                        "retrograde": None,
                        "sign": "Capricorn",
                        "element": "Earth",
                        "modality": "Cardinal",
                        "aspects": []
                    },
                    "calculation_time_ms": 6.2,
                    "number": 12,
                    "flags": 2,
                    "se_version": "2.10.03",
                    "source": "Meridian-ACG",
                    "color": "#8B0000",
                    "z_index": 5,
                    "hit_radius": 3.0,
                    "influence_radius_miles": 150.0,
                    "render_orb_only": True
                }
            }
        ],
        "metadata": {
            "natal_context": {
                "subject_name": "John Doe",
                "birth_location": "NYC (40.7128, -74.0060)",
                "birth_datetime": "1990-06-15T18:30:00Z",
                "house_system": "placidus",
                "natal_chart_calculated": True,
                "aspects_included": True,
                "arabic_parts_included": True
            },
            "calculation_info": {
                "timestamp": datetime.now().isoformat(),
                "total_features": 3,
                "acg_lines": 2,
                "orb_only_features": 1,
                "total_calculation_time_ms": 39.3,
                "api_endpoint": "/acg/lines",
                "natal_integration": "full"
            },
            "rendering_guidance": {
                "line_features": "Render as LineString geometries with specified colors",
                "orb_features": "Render as circular influence areas using influence_radius_miles",
                "natal_tooltips": "Use natal.house, natal.sign, natal.aspects for user tooltips",
                "three_js_ready": True,
                "geojson_specification": "RFC 7946 compliant"
            }
        }
    }
    
    # Combined Complete Output - What User Actually Gets
    complete_user_output = {
        "request_info": {
            "user_input": {
                "name": "John Doe",
                "birth_date": "June 15, 1990",
                "birth_time": "2:30 PM",
                "birth_location": "New York City",
                "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
                "timezone": "America/New_York"
            },
            "services_requested": ["natal_chart_enhanced", "acg_lines_with_natal"],
            "house_system": "placidus",
            "aspect_system": "traditional"
        },
        "natal_chart": natal_chart_response,
        "acg_lines": acg_with_natal_response,
        "system_info": {
            "ephemeris_engine": "Swiss Ephemeris v2.10.03",
            "data_source": "NASA DE431",
            "calculation_standard": "Jim Lewis ACG compliance",
            "coordinate_system": "Geocentric",
            "processing_location": "Meridian Ephemeris API v1.0",
            "total_processing_time_ms": 196.0,
            "cached_results": False,
            "api_version": "1.0",
            "output_format": "JSON + GeoJSON"
        }
    }
    
    # Save complete output
    output_file = Path(__file__).parent.parent / "complete_user_output_sample.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(complete_user_output, f, indent=2, ensure_ascii=False)
    
    print(f"\nComplete User Output Generated!")
    print(f"Saved to: {output_file}")
    print(f"\nOutput Structure:")
    print(f"  1. REQUEST INFO - What the user entered")
    print(f"  2. NATAL CHART - Complete birth chart with:")
    print(f"     - 4 planets with full dignity/house/sign data")
    print(f"     - Placidus house system with all cusps")
    print(f"     - 3 major aspects with strength analysis")  
    print(f"     - 2 Arabic parts (Fortune & Spirit)")
    print(f"     - Sect determination (day chart)")
    print(f"  3. ACG LINES - Astrocartography with:")
    print(f"     - Sun MC line (world map coordinates)")
    print(f"     - Moon AC line (world map coordinates)")  
    print(f"     - LilithMean orb point (150-mile influence)")
    print(f"     - Full natal context in each feature")
    print(f"  4. SYSTEM INFO - Technical metadata")
    print(f"\nTotal File Size: ~{len(json.dumps(complete_user_output)) / 1024:.1f} KB")
    print(f"Processing Time: {complete_user_output['system_info']['total_processing_time_ms']}ms")
    
    print(f"\nKey Integration Features:")
    print(f"  + Each ACG line includes natal context (house, sign, aspects)")
    print(f"  + Placidus house system used throughout")
    print(f"  + Traditional aspect orb system")
    print(f"  + Three.js ready coordinate arrays")
    print(f"  + Professional rendering metadata")
    print(f"  + Extended features (Arabic parts, influence orbs)")
    
    return complete_user_output


if __name__ == "__main__":
    result = create_complete_user_output()