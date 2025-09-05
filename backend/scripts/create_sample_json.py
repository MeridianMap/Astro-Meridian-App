"""
Create Sample ACG JSON Output

Creates a sample JSON payload by calling the API directly to demonstrate
the complete output format including rendering metadata.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app


def create_sample_json():
    """Create sample JSON by calling the API directly."""
    
    print("Creating Sample ACG JSON Output")
    print("=" * 40)
    
    # Create test client
    client = TestClient(app)
    
    # Sample request data (based on test files)
    sample_request = {
        "epoch": "2000-01-01T12:00:00Z",  # J2000.0 epoch
        "bodies": [
            "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
            "LilithMean"  # Include one with rendering metadata
        ],
        "options": {
            "line_types": ["MC", "IC", "AC", "DC"],
            "include_parans": False,
            "aspects": ["sextile", "square", "trine"],
            "orb_deg": 1.0,
            "flags": 2  # SEFLG_SWIEPH
        },
        "natal": {
            "birthplace_lat": 40.7128,  # NYC
            "birthplace_lon": -74.0060
        }
    }
    
    print(f"Location: NYC ({sample_request['natal']['birthplace_lat']}, {sample_request['natal']['birthplace_lon']})")
    print(f"Epoch: {sample_request['epoch']}")
    print(f"Bodies: {', '.join(sample_request['bodies'])}")
    print(f"Line Types: {', '.join(sample_request['options']['line_types'])}")
    print(f"Aspects: {', '.join(sample_request['options']['aspects'])}")
    
    try:
        # Make API call
        print("\nCalling ACG API...")
        response = client.post("/acg/lines", json=sample_request)
        
        if response.status_code == 200:
            result_data = response.json()
            
            # Add metadata about generation
            metadata = {
                "generation_info": {
                    "timestamp": datetime.now().isoformat(),
                    "location": f"NYC ({sample_request['natal']['birthplace_lat']}, {sample_request['natal']['birthplace_lon']})",
                    "epoch": sample_request["epoch"],
                    "bodies_requested": sample_request["bodies"],
                    "total_features": len(result_data.get("features", [])),
                    "status_code": response.status_code,
                    "api_endpoint": "/acg/lines"
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
                }
            }
            
            # Combine with API response
            full_output = {
                **result_data,
                "metadata": metadata
            }
            
            # Save to file
            output_file = Path(__file__).parent.parent / "sample_acg_output.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(full_output, f, indent=2, ensure_ascii=False)
            
            print(f"\nSample output generated successfully!")
            print(f"Saved to: {output_file}")
            print(f"Total features: {len(result_data.get('features', []))}")
            
            # Print summary of feature types and rendering metadata
            features = result_data.get("features", [])
            feature_types = {}
            rendering_metadata_examples = []
            
            for feature in features:
                props = feature.get("properties", {})
                line_info = props.get("line", {})
                line_type = line_info.get("line_type", "unknown")
                body_id = props.get("id", "unknown")
                
                feature_types[line_type] = feature_types.get(line_type, 0) + 1
                
                # Collect examples of rendering metadata
                influence_radius = props.get("influence_radius_miles", 0)
                render_orb_only = props.get("render_orb_only", False)
                
                if influence_radius > 0 or render_orb_only:
                    rendering_metadata_examples.append({
                        "body": body_id,
                        "influence_radius_miles": influence_radius,
                        "render_orb_only": render_orb_only
                    })
            
            print(f"\nFeature Type Summary:")
            for feature_type, count in feature_types.items():
                print(f"  {feature_type}: {count} lines")
            
            if rendering_metadata_examples:
                print(f"\nRendering Metadata Examples:")
                unique_examples = {ex["body"]: ex for ex in rendering_metadata_examples}.values()
                for example in list(unique_examples)[:3]:  # Show first 3 unique
                    print(f"  {example['body']}: {example['influence_radius_miles']}mi radius, orb_only={example['render_orb_only']}")
            else:
                print(f"\nNo rendering metadata found (extended features may be commented out)")
            
            return full_output
            
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error creating sample JSON: {e}")
        raise


if __name__ == "__main__":
    result = create_sample_json()