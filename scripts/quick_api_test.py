#!/usr/bin/env python3
"""
Quick API Test to Generate Real JSON Output

This bypasses import issues and directly calls the working API endpoint.
"""

import json
import requests
import subprocess
import time
import sys
from datetime import datetime

def start_api_server():
    """Start the FastAPI server in the background."""
    print("Starting FastAPI server...")
    try:
        # Start the server using uvicorn
        proc = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1",
            "--port", "8000"
        ], cwd="backend", capture_output=True, text=True)
        
        # Give the server time to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print("✓ Server started successfully")
                return proc
            else:
                print("✗ Server health check failed")
                return None
        except requests.exceptions.RequestException:
            try:
                # Try the root endpoint instead
                response = requests.get("http://127.0.0.1:8000/", timeout=5)
                print("✓ Server started (root endpoint accessible)")
                return proc
            except:
                print("✗ Server not responding")
                return None
                
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return None

def test_api_endpoint():
    """Test the API endpoint and capture JSON output."""
    
    request_payload = {
        "subject": {
            "name": "Dallas API Test 1987-07-15 09:01",
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
    
    # Try different endpoints in order
    endpoints = [
        "http://127.0.0.1:8000/ephemeris/v2/natal-enhanced",
        "http://127.0.0.1:8000/ephemeris/natal"
    ]
    
    for endpoint in endpoints:
        print(f"Testing endpoint: {endpoint}")
        try:
            response = requests.post(
                endpoint, 
                json=request_payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Success! Got JSON response")
                
                # Parse response
                try:
                    data = response.model_dump_json()
                    
                    # Create output
                    output_data = {
                        "endpoint_used": endpoint,
                        "status_code": response.status_code,
                        "timestamp": datetime.now().isoformat(),
                        "request_payload": request_payload,
                        "response": data
                    }
                    
                    # Save to file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"REAL_API_OUTPUT_{timestamp}.json"
                    
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"✓ Real API output saved to: {filename}")
                    
                    # Print summary
                    if data.get("success"):
                        planets = len(data.get("planets", {}))
                        aspects = len(data.get("aspects", []))
                        print(f"  - Chart Success: {data.get('success')}")
                        print(f"  - Planets: {planets}")
                        print(f"  - Aspects: {aspects}")
                        if "calculation_metadata" in data:
                            calc_time = data["calculation_metadata"].get("calculation_time", "N/A")
                            print(f"  - Calculation Time: {calc_time}s")
                    
                    return filename
                    
                except json.JSONDecodeError as e:
                    print(f"✗ JSON decode error: {e}")
                    print("Raw response:", response.text[:500])
                    
            elif response.status_code == 404:
                print(f"✗ Endpoint not found: {endpoint}")
                continue
            elif response.status_code == 422:
                print(f"✗ Validation error")
                try:
                    error_data = response.model_dump_json()
                    print(f"  Error details: {error_data}")
                except:
                    print(f"  Raw error: {response.text[:500]}")
            else:
                print(f"✗ HTTP {response.status_code}")
                print(f"  Response: {response.text[:500]}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            continue
    
    return None

def main():
    """Main function to test API and generate output."""
    print("Real API Output Generator")
    print("=" * 40)
    
    # Start server
    server_proc = start_api_server()
    
    if not server_proc:
        print("Failed to start server. Try running manually:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
        return
    
    try:
        # Test API
        output_file = test_api_endpoint()
        
        if output_file:
            print(f"\n✓ SUCCESS: Real API output generated")
            print(f"  File: {output_file}")
        else:
            print(f"\n✗ FAILED: Could not generate API output")
            print("Check server logs for errors")
            
    finally:
        # Clean up server
        if server_proc:
            print("\nStopping server...")
            server_proc.terminate()
            server_proc.wait()

if __name__ == "__main__":
    main()