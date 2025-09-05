"""
Simple Sample JSON Generator - Basic ACG Output

Creates a sample JSON payload using just the core ephemeris functionality
to demonstrate the basic output format without complex dependencies.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def create_sample_acg_geojson():
    """Create a sample ACG GeoJSON output based on documentation."""
    
    print("Creating Simple ACG Sample JSON...")
    print("=" * 40)
    
    # Sample GeoJSON structure based on the ACG system documentation
    sample_output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-180.0, -23.5],
                        [-90.0, -15.2],
                        [0.0, 0.0],
                        [90.0, 15.2],
                        [180.0, 23.5]
                    ]
                },
                "properties": {
                    "id": "Sun",
                    "type": "body",
                    "kind": "planet",
                    "epoch": "2000-01-01T12:00:00Z",
                    "jd": 2451545.0,
                    "gmst": 280.4606,
                    "obliquity": 23.4392911,
                    "coords": {
                        "ra": 280.1532,
                        "dec": -23.0123,
                        "lambda_": 280.1532,
                        "beta": 0.0001,
                        "distance": 0.98329,
                        "speed": 1.0194
                    },
                    "line": {
                        "angle": "MC",
                        "line_type": "MC",
                        "method": "swiss_ephemeris_v2.10.03",
                        "orb": 1.0
                    },
                    "calculation_time_ms": 12.5,
                    "number": 0,
                    "flags": 2,
                    "se_version": "2.10.03",
                    "source": "Meridian-ACG",
                    "color": "#FFD700",
                    "z_index": 10,
                    "hit_radius": 2.0,
                    "influence_radius_miles": 0.0,
                    "render_orb_only": False
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-180.0, 35.7],
                        [-90.0, 28.3],
                        [0.0, 15.0],
                        [90.0, 28.3],
                        [180.0, 35.7]
                    ]
                },
                "properties": {
                    "id": "Moon",
                    "type": "body", 
                    "kind": "planet",
                    "epoch": "2000-01-01T12:00:00Z",
                    "jd": 2451545.0,
                    "gmst": 280.4606,
                    "obliquity": 23.4392911,
                    "coords": {
                        "ra": 98.2845,
                        "dec": 26.1234,
                        "lambda_": 96.4567,
                        "beta": 4.2341,
                        "distance": 0.00257,
                        "speed": 13.1763
                    },
                    "line": {
                        "angle": "AC",
                        "line_type": "AC", 
                        "method": "swiss_ephemeris_v2.10.03",
                        "orb": 1.0
                    },
                    "calculation_time_ms": 8.3,
                    "number": 1,
                    "flags": 2,
                    "se_version": "2.10.03",
                    "source": "Meridian-ACG",
                    "color": "#C0C0C0",
                    "z_index": 9,
                    "hit_radius": 2.0,
                    "influence_radius_miles": 0.0,
                    "render_orb_only": False
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [-180.0, -45.2],
                        [-90.0, -38.7],
                        [0.0, -25.3],
                        [90.0, -38.7],
                        [180.0, -45.2]
                    ]
                },
                "properties": {
                    "id": "Mars",
                    "type": "body",
                    "kind": "planet", 
                    "epoch": "2000-01-01T12:00:00Z",
                    "jd": 2451545.0,
                    "gmst": 280.4606,
                    "obliquity": 23.4392911,
                    "coords": {
                        "ra": 332.9876,
                        "dec": -12.4567,
                        "lambda_": 333.4821,
                        "beta": -1.3456,
                        "distance": 1.3825,
                        "speed": 0.5234
                    },
                    "line": {
                        "angle": "IC",
                        "line_type": "IC",
                        "method": "swiss_ephemeris_v2.10.03",
                        "orb": 1.0
                    },
                    "calculation_time_ms": 10.1,
                    "number": 4,
                    "flags": 2,
                    "se_version": "2.10.03",
                    "source": "Meridian-ACG",
                    "color": "#FF4500",
                    "z_index": 8,
                    "hit_radius": 2.0,
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
                    "epoch": "2000-01-01T12:00:00Z",
                    "jd": 2451545.0,
                    "gmst": 280.4606,
                    "obliquity": 23.4392911,
                    "coords": {
                        "ra": 125.6789,
                        "dec": 18.9876,
                        "lambda_": 124.3456,
                        "beta": 2.1098,
                        "distance": None,
                        "speed": 0.1111
                    },
                    "line": {
                        "angle": "point",
                        "line_type": "orb_only",
                        "method": "swiss_ephemeris_v2.10.03",
                        "orb": 1.0
                    },
                    "calculation_time_ms": 6.7,
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
            "generation_info": {
                "timestamp": datetime.now().isoformat(),
                "location": "NYC (40.7128, -74.0060)",
                "epoch": "2000-01-01T12:00:00Z",
                "bodies_requested": ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "LilithMean"],
                "total_features": 4,
                "status_code": 200,
                "api_endpoint": "/acg/lines",
                "calculation_type": "ACG Lines"
            },
            "sample_explanation": {
                "type": "ACG (Astrocartography) calculation result",
                "format": "GeoJSON FeatureCollection", 
                "features": "Each feature represents an ACG line or point",
                "properties": {
                    "influence_radius_miles": "Radius for orb rendering (0 = no orb)",
                    "render_orb_only": "true = render orb only, false = render ACG lines + orb if radius > 0",
                    "line_type": "MC/IC/AC/DC for cardinal angles, MC_ASPECT/AC_ASPECT for aspect lines",
                    "coords": "Celestial coordinates (RA, Dec, Ecliptic Lon/Lat)",
                    "natal": "Natal chart context if available"
                }
            },
            "rendering_metadata_examples": [
                {
                    "body": "LilithMean",
                    "influence_radius_miles": 150.0,
                    "render_orb_only": True,
                    "explanation": "Fixed stars and special points render only influence orbs, not ACG lines"
                }
            ],
            "feature_type_summary": {
                "MC": 1,
                "AC": 1, 
                "IC": 1,
                "orb_only": 1
            }
        }
    }
    
    # Save to file
    output_file = Path(__file__).parent.parent / "sample_acg_output.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSample ACG output generated successfully!")
    print(f"Saved to: {output_file}")
    print(f"Total features: {len(sample_output['features'])}")
    
    # Print feature summary
    print(f"\nFeature Type Summary:")
    for feature_type, count in sample_output['metadata']['feature_type_summary'].items():
        print(f"  {feature_type}: {count} lines")
    
    print(f"\nRendering Metadata Examples:")
    for example in sample_output['metadata']['rendering_metadata_examples']:
        print(f"  {example['body']}: {example['influence_radius_miles']}mi radius, orb_only={example['render_orb_only']}")
        print(f"    -> {example['explanation']}")
    
    print(f"\nKey Features Demonstrated:")
    print(f"  - GeoJSON FeatureCollection format")
    print(f"  - Standard ACG lines (MC, AC, IC lines)")
    print(f"  - Extended body with influence radius (LilithMean)")
    print(f"  - Comprehensive metadata structure")
    print(f"  - Three.js-compatible coordinate arrays")
    print(f"  - Professional visualization properties")
    
    return sample_output


if __name__ == "__main__":
    result = create_sample_acg_geojson()