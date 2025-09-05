"""
Generate Sample ACG JSON Output

Creates a sample JSON payload using the ACG engine with test data
to demonstrate the complete output format including rendering metadata.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.core.acg.acg_core import ACGCalculationEngine
from app.core.acg.acg_types import (
    ACGRequest, ACGOptions, ACGBodyType, ACGLineType, ACGNatalInfo, ACGAspectType
)


def create_sample_request():
    """Create a sample ACG request using test data."""
    
    # Test location: New York City (from test files)
    # Test date: January 1, 2000, 12:00 UTC (J2000.0 epoch)
    
    return ACGRequest(
        epoch="2000-01-01T12:00:00Z",
        bodies=[
            "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
            "LilithMean"  # Include one with rendering metadata
        ],
        options=ACGOptions(
            line_types=[ACGLineType.MC, ACGLineType.IC, ACGLineType.AC, ACGLineType.DC],
            include_parans=False,
            aspects=[ACGAspectType.SEXTILE, ACGAspectType.SQUARE, ACGAspectType.TRINE],  # Sample aspects
            flags=2,  # SEFLG_SWIEPH
            orb_deg=1.0
        ),
        natal=ACGNatalInfo(
            birthplace_lat=40.7128,  # NYC latitude
            birthplace_lon=-74.0060  # NYC longitude  
        )
    )


def generate_sample_output():
    """Generate sample ACG output and save as JSON."""
    
    print("Generating Sample ACG Output...")
    print("=" * 40)
    
    try:
        # Initialize ACG engine
        engine = ACGCalculationEngine()
        
        # Create sample request
        request = create_sample_request()
        
        print(f"Request Location: NYC ({request.natal.birthplace_lat}, {request.natal.birthplace_lon})")
        print(f"Request Epoch: {request.epoch}")
        print(f"Request Bodies: {', '.join(request.bodies)}")
        print(f"Line Types: {', '.join([lt.value for lt in request.options.line_types])}")
        print(f"Include Aspects: {[asp.value for asp in request.options.aspects] if request.options.aspects else 'None'}")
        
        # Calculate ACG lines
        print("\nCalculating ACG lines...")
        result = engine.calculate_acg_lines(request)
        
        # Convert to GeoJSON format (this is what the API returns)
        geojson_output = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # Add each ACG line as a GeoJSON feature
        for line_data in result.lines:
            feature = {
                "type": "Feature",
                "geometry": line_data.geometry,
                "properties": line_data.properties
            }
            geojson_output["features"].append(feature)
        
        # Add metadata
        metadata = {
            "generation_info": {
                "timestamp": datetime.now().isoformat(),
                "location": f"NYC ({request.natal.birthplace_lat}, {request.natal.birthplace_lon})",
                "epoch": request.epoch,
                "bodies_requested": request.bodies,
                "total_features": len(geojson_output["features"]),
                "calculation_time_ms": result.total_calculation_time_ms if hasattr(result, 'total_calculation_time_ms') else 0
            },
            "sample_properties_explanation": {
                "influence_radius_miles": "Radius for orb rendering (0 = no orb)",
                "render_orb_only": "true = render orb only, false = render ACG lines + orb if radius > 0",
                "line_type": "MC/IC/AC/DC for cardinal angles, MC_ASPECT/AC_ASPECT for aspect lines", 
                "coords": "Celestial coordinates (RA, Dec, Ecliptic Lon/Lat)",
                "natal": "Natal chart context if available"
            }
        }
        
        # Combine output
        full_output = {
            **geojson_output,
            "metadata": metadata
        }
        
        # Save to file
        output_file = Path(__file__).parent.parent / "sample_acg_output.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(full_output, f, indent=2, ensure_ascii=False)
        
        print(f"\nSample output generated successfully!")
        print(f"Saved to: {output_file}")
        print(f"Total features: {len(geojson_output['features'])}")
        
        # Print summary of feature types
        feature_types = {}
        rendering_metadata_examples = []
        
        for feature in geojson_output["features"]:
            props = feature["properties"]
            line_type = props.get("line", {}).get("line_type", "unknown")
            body_id = props.get("id", "unknown")
            
            feature_types[line_type] = feature_types.get(line_type, 0) + 1
            
            # Collect examples of rendering metadata
            if props.get("influence_radius_miles", 0) > 0 or props.get("render_orb_only", False):
                rendering_metadata_examples.append({
                    "body": body_id,
                    "influence_radius_miles": props.get("influence_radius_miles", 0),
                    "render_orb_only": props.get("render_orb_only", False)
                })
        
        print(f"\nFeature Type Summary:")
        for feature_type, count in feature_types.items():
            print(f"  {feature_type}: {count} lines")
        
        if rendering_metadata_examples:
            print(f"\nRendering Metadata Examples:")
            for example in rendering_metadata_examples[:3]:  # Show first 3
                print(f"  {example['body']}: {example['influence_radius_miles']}mi radius, orb_only={example['render_orb_only']}")
        
        return full_output
        
    except Exception as e:
        print(f"Error generating sample output: {e}")
        raise


if __name__ == "__main__":
    sample_output = generate_sample_output()