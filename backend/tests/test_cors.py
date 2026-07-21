import requests

URL = "http://localhost:8001/api/convert"

def test_cors():
    print("=== Testing CORS Middleware ===")
    
    # 1. Valid Origin (localhost:3000)
    print("\n1. Testing valid origin: http://localhost:3000")
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    response = requests.options(URL, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000", "Missing or incorrect CORS header for valid origin"
    print("✅ Passed: Valid origin accepted correctly.")
    
    # 2. Another Valid Origin (https://baremd.example.com)
    print("\n2. Testing valid origin: https://baremd.example.com")
    headers = {
        "Origin": "https://baremd.example.com",
        "Access-Control-Request-Method": "POST",
    }
    response = requests.options(URL, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers.get("access-control-allow-origin") == "https://baremd.example.com", "Missing or incorrect CORS header for valid origin"
    print("✅ Passed: Second valid origin accepted correctly.")

    # 3. Malicious Origin (https://evil.com)
    print("\n3. Testing malicious origin: https://evil.com")
    headers = {
        "Origin": "https://evil.com",
        "Access-Control-Request-Method": "POST",
    }
    response = requests.options(URL, headers=headers)
    # FastAPI's CORSMiddleware returns 400 Bad Request for invalid origins
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert "access-control-allow-origin" not in response.headers, "CORS header leaked to malicious origin!"
    print("✅ Passed: Malicious origin strictly rejected (400 Bad Request).")

if __name__ == "__main__":
    try:
        test_cors()
        print("\n🎉 ALL CORS TESTS PASSED!")
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
