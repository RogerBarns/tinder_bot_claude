"""
Test script to verify the Flask app is running correctly
"""
import requests
import json

BASE_URL = "http://localhost:5000"


def test_endpoints():
    """Test various endpoints"""

    endpoints = [
        ("/", "GET"),
        ("/config", "GET"),
        ("/stats", "GET"),
        ("/debug-routes", "GET"),
        ("/start-browser", "POST"),
        ("/browser-status", "GET"),
        ("/debug-api-client", "GET"),
    ]

    print("Testing endpoints...")
    print("-" * 50)

    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)

            status = "✅" if response.status_code < 400 else "❌"
            print(f"{status} {method:4} {endpoint:30} - Status: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"❌ {method:4} {endpoint:30} - Connection Error")
        except Exception as e:
            print(f"❌ {method:4} {endpoint:30} - Error: {e}")

    print("-" * 50)

    # Try to get the routes list
    try:
        response = requests.get(f"{BASE_URL}/debug-routes", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\nTotal registered routes: {data.get('total', 0)}")
            print("\nAvailable routes:")
            for route in data.get('routes', [])[:20]:  # Show first 20 routes
                print(f"  - {route}")
    except:
        print("\nCouldn't fetch routes list")


if __name__ == "__main__":
    test_endpoints()