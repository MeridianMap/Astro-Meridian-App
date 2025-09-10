#!/usr/bin/env python3
"""
Simple API Tester - Get Real JSON Output

Run this AFTER starting the API server with START_API_SERVER.bat
"""

import json
import requests
from datetime import datetime

def test_api():
    """Test the API and get real JSON output."""
    
    request_payload = {
        "subject": {
            "name": "Dallas Real API Test 1987-07-15 09:01",
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
    
    # Test the natal endpoint
    url = "http://127.0.0.1:8000/ephemeris/natal"
    
    print("Testing API endpoint...")
    print(f"URL: {url}")
    print("Payload:", json.dumps(request_payload, indent=2))
    print("-" * 50)
    
    try:
        response = requests.post(url, json=request_payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS! Got response")
            
            # Parse and save response
            data = response.model_dump_json()
            
            output_data = {
                "test_info": {
                    "endpoint": url,
                    "timestamp": datetime.now().isoformat(),
                    "status_code": response.status_code
                },
                "request_payload": request_payload,
                "response": data
            }
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"REAL_API_OUTPUT_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"Output saved to: {filename}")
            
            # Print summary
            if data.get("success"):
                print("Chart calculation: SUCCESS")
                planets = len(data.get("planets", {}))
                aspects = len(data.get("aspects", []))
                print(f"Planets: {planets}")
                print(f"Aspects: {aspects}")
                
                if "calculation_metadata" in data:
                    calc_time = data["calculation_metadata"].get("calculation_time", "N/A")
                    print(f"Calculation time: {calc_time}s")
            else:
                print("Chart calculation: FAILED")
                if "errors" in data:
                    print("Errors:", data["errors"])
            
            return filename
            
        else:
            print(f"FAILED with status {response.status_code}")
            print("Response:", response.text[:500])
            return None
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API server")
        print("Make sure to run START_API_SERVER.bat first!")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    print("=== Meridian API Real Output Tester ===")
    print("")
    print("INSTRUCTIONS:")
    print("1. First run: START_API_SERVER.bat") 
    print("2. Wait for 'Application startup complete'")
    print("3. Then run this script")
    print("")
    
    result = test_api()
    
    if result:
        print(f"\nSUCCESS: Real API output saved to {result}")
    else:
        print("\nFAILED: Could not get API output")
        print("Check that the API server is running and accessible")