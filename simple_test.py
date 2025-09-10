#!/usr/bin/env python3
"""
Simple API Test Script - Generate JSON Output
"""

import json
import requests
from datetime import datetime

def test_api_simple():
    """Simple API test to generate JSON output."""
    
    # Define the request payload
    request_payload = {
        "subject": {
            "name": "Test Person - 1987-07-15 09:01",
            "datetime": {"iso_string": "1987-07-15T09:01:00"},
            "latitude": {"decimal": 32.7833333333},
            "longitude": {"decimal": -96.8},
            "timezone": {"name": "America/Chicago"}
        },
        "configuration": {
            "house_system": "P",
            "include_asteroids": True,
            "include_nodes": True,
            "include_lilith": True
        },
        "include_aspects": True,
        "aspect_orb_preset": "traditional",
        "metadata_level": "audit"
    }
    
    # Test the API
    url = "http://127.0.0.1:8000/ephemeris/natal"
    
    print("=== MERIDIAN API TEST ===")
    print(f"Testing URL: {url}")
    print("Request payload:")
    print(json.dumps(request_payload, indent=2))
    print("-" * 60)
    
    try:
        print("Making API request...")
        response = requests.post(url, json=request_payload, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            
            # Get JSON response
            data = response.model_dump_json()
            
            # Create output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_output_{timestamp}.json"
            
            # Save complete output
            output_data = {
                "test_info": {
                    "endpoint": url,
                    "timestamp": datetime.now().isoformat(),
                    "status_code": response.status_code
                },
                "request": request_payload,
                "response": data
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Output saved to: {filename}")
            
            # Print summary
            if data.get("success"):
                print("\n=== CHART SUMMARY ===")
                planets = data.get("planets", {})
                aspects = data.get("aspects", [])
                
                print(f"Planets found: {len(planets)}")
                print(f"Aspects found: {len(aspects)}")
                
                # Show some planets
                print("\nSample planets:")
                for planet_name, planet_data in list(planets.items())[:5]:
                    sign = planet_data.get("sign", "Unknown")
                    house = planet_data.get("house", "Unknown")
                    longitude = planet_data.get("longitude", 0)
                    print(f"  {planet_name}: {longitude:.2f}° in {sign}, House {house}")
                
                # Show calculation metadata
                if "calculation_metadata" in data:
                    calc_time = data["calculation_metadata"].get("calculation_time", "N/A")
                    print(f"\nCalculation time: {calc_time}s")
            
            return filename
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print("Response:", response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot connect to API server")
        print("Make sure the server is running on http://127.0.0.1:8000")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    result = test_api_simple()
    
    if result:
        print(f"\n🎉 SUCCESS! API output saved to: {result}")
    else:
        print("\n💥 FAILED: Could not generate API output")
        print("Check that the API server is running")
