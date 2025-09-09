#!/usr/bin/env python3
"""
Generate Comprehensive Ephemeris JSON Output

This script generates a complete JSON output with all available ephemeris features:
- All planets, asteroids, nodes, and Lilith points
- Houses, angles, and fixed stars  
- Complete aspect analysis
- 16 traditional hermetic lots with sect determination
- Jim Lewis style astrocartography data
- Essential dignities analysis
- Comprehensive metadata

Usage:
    python generate_comprehensive_output.py

Output will be written to:
    COMPREHENSIVE_EPHEMERIS_OUTPUT_[timestamp].json
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app


def generate_comprehensive_chart():
    """Generate comprehensive chart with all features."""
    client = TestClient(app)
    
    # Comprehensive request with all features enabled
    request_payload = {
        "subject": {
            "name": "Dallas Comprehensive Demo 1987-07-15 09:01",
            "datetime": {"iso_string": "1987-07-15T09:01:00"},
            "latitude": {"decimal": 32.7833333333},
            "longitude": {"decimal": -96.8},
            "timezone": {"name": "America/Chicago"},
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
    }
    
    print("🌟 Generating Comprehensive Ephemeris Output...")
    print("Features: Planets, Asteroids, Nodes, Lilith, Houses, Angles, Fixed Stars,")
    print("         Aspects, Hermetic Lots, Astrocartography, Essential Dignities")
    print("-" * 70)
    
    # Try comprehensive endpoint first, fallback to enhanced
    endpoints = [
        "/ephemeris/v3/comprehensive",
        "/ephemeris/v2/natal-enhanced", 
        "/ephemeris/natal"
    ]
    
    response = None
    endpoint_used = None
    
    for endpoint in endpoints:
        try:
            response = client.post(endpoint, json=request_payload)
            if response.status_code in [200, 201]:
                endpoint_used = endpoint
                break
            elif response.status_code == 404:
                continue
            else:
                print(f"⚠️  Endpoint {endpoint} returned status {response.status_code}")
                continue
        except Exception as e:
            print(f"⚠️  Error trying {endpoint}: {e}")
            continue
    
    if not response or response.status_code not in [200, 201]:
        print("❌ Failed to generate chart from any endpoint")
        return None
        
    print(f"✅ Successfully generated chart using: {endpoint_used}")
    print(f"📊 HTTP Status: {response.status_code}")
    
    try:
        body = response.json()
    except Exception as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return None
    
    # Create output structure
    output_data = {
        "generation_info": {
            "timestamp": datetime.now().isoformat(),
            "endpoint_used": endpoint_used,
            "status_code": response.status_code,
            "features_requested": [
                "planets", "asteroids", "nodes", "lilith_points", 
                "houses", "angles", "fixed_stars", "aspects", 
                "hermetic_lots", "astrocartography", "essential_dignities"
            ]
        },
        "request_payload": request_payload,
        "response": body
    }
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"COMPREHENSIVE_EPHEMERIS_OUTPUT_{timestamp}.json"
    
    # Write output
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Output written to: {filename}")
    
    # Print summary stats
    if body.get("success"):
        planets = len(body.get("planets", {}))
        asteroids = len(body.get("asteroids", {}))
        aspects = len(body.get("aspects", []))
        lots = len(body.get("hermetic_lots", []))
        
        print("\n📈 Chart Summary:")
        print(f"   • Planets: {planets}")
        print(f"   • Asteroids: {asteroids}")
        print(f"   • Aspects: {aspects}")
        print(f"   • Hermetic Lots: {lots}")
        
        if body.get("astrocartography"):
            acg_lines = len(body.get("astrocartography", {}).get("geojson", {}).get("features", []))
            print(f"   • ACG Lines: {acg_lines}")
            
        if body.get("calculation_metadata"):
            calc_time = body["calculation_metadata"].get("calculation_time", 0)
            print(f"   • Calculation Time: {calc_time:.3f}s")
    else:
        print("⚠️  Chart calculation reported success=False")
        if body.get("errors"):
            print(f"   Errors: {body['errors']}")
    
    print("\n🎉 Comprehensive ephemeris generation complete!")
    return filename


if __name__ == "__main__":
    try:
        output_file = generate_comprehensive_chart()
        if output_file:
            print(f"\n✨ Use this file to review the complete JSON structure: {output_file}")
    except KeyboardInterrupt:
        print("\n⏹️  Generation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()