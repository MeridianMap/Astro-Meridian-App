#!/usr/bin/env python3
"""
Working API Test - Minimal Valid Request
"""

import json
import requests
from datetime import datetime

def test_working_api():
    """Test with minimal valid payload."""
    
    # Minimal valid request based on schema
    request_payload = {
        "subject": {
            "name": "Dallas Test - July 15, 1987",
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
        }
    }
    
    url = "http://127.0.0.1:8000/ephemeris/natal"
    
    print("=== WORKING API TEST ===")
    print(f"URL: {url}")
    print("Valid payload:")
    print(json.dumps(request_payload, indent=2))
    print("-" * 60)
    
    try:
        print("Making API request...")
        response = requests.post(url, json=request_payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS!")
            
            data = response.model_dump_json()
            
            # Save the complete output
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"WORKING_API_OUTPUT_{timestamp}.json"
            
            output_data = {
                "test_info": {
                    "endpoint": url,
                    "timestamp": datetime.now().isoformat(),
                    "status_code": response.status_code,
                    "success": True
                },
                "request": request_payload,
                "response": data
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Complete output saved to: {filename}")
            print()
            
            # Print summary
            if data.get("success"):
                print("=== CHART SUMMARY ===")
                print(f"Subject: {data.get('subject', {}).get('name', 'N/A')}")
                print(f"Date: {data.get('subject', {}).get('datetime', 'N/A')}")
                
                planets = data.get("planets", {})
                houses = data.get("houses", {})
                
                print(f"Planets calculated: {len(planets)}")
                print(f"Houses calculated: {len(houses)}")
                
                if planets:
                    print("\n--- Sample Planets ---")
                    for planet_name, planet_data in list(planets.items())[:5]:
                        sign = planet_data.get("sign", "Unknown")
                        house = planet_data.get("house", "Unknown")
                        longitude = planet_data.get("longitude", 0)
                        print(f"  {planet_name}: {longitude:.2f}° in {sign} (House {house})")
                
                if "calculation_metadata" in data:
                    calc_time = data["calculation_metadata"].get("calculation_time", "N/A")
                    print(f"\nCalculation time: {calc_time} seconds")
                
                print(f"\n✨ Full astrological chart data available in: {filename}")
                return filename
            else:
                print("❌ Chart calculation failed")
                print("Error:", data.get("error", "Unknown"))
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print("Response:", response.text[:500])
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot connect to server")
        print("Make sure the API server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        
    return None

if __name__ == "__main__":
    result = test_working_api()
    
    if result:
        print(f"\n🏆 SUCCESS! Real astrology API output saved to: {result}")
        print("You can now examine the complete JSON chart data!")
    else:
        print("\n💥 No luck this time. Check the API server and try again.")
