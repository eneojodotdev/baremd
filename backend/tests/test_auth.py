import requests
import time

URL = "http://localhost:8001/api/convert"
API_KEY = "default_secret_key_123"
INVALID_KEY = "wrong_key_456"

def test_auth():
    print("=== Testing Authentication ===")
    
    # 1. No API Key
    print("\n1. Testing missing API Key...")
    response = requests.post(URL, files={"file": ("test.txt", "Hello World")})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("✅ Passed: Missing API key was rejected with 401 Unauthorized")
    
    # 2. Invalid API Key
    print("\n2. Testing invalid API Key...")
    response = requests.post(URL, headers={"X-API-Key": INVALID_KEY}, files={"file": ("test.txt", "Hello World")})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("✅ Passed: Invalid API key was rejected with 401 Unauthorized")
    
    # 3. Valid API Key (Success)
    print("\n3. Testing valid API Key...")
    response = requests.post(URL, headers={"X-API-Key": API_KEY}, files={"file": ("test.txt", "Hello World")})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    print("✅ Passed: Valid API key successfully authenticated")
    
    # 4. Rate Limiting (60 requests per minute)
    # We will simulate 61 fast requests to trigger a 429
    # Note: the limit is 60/minute, so the 61st should fail
    print("\n4. Testing Rate Limiting (this might take a few seconds)...")
    for i in range(60):
        # We don't actually need to wait, just hit it fast
        res = requests.post(URL, headers={"X-API-Key": API_KEY}, files={"file": ("test.txt", "Hello World")})
        if res.status_code == 429:
            print(f"✅ Passed: Rate limit kicked in early at request {i+1}!")
            return
            
    # The 61st request should definitely fail
    res = requests.post(URL, headers={"X-API-Key": API_KEY}, files={"file": ("test.txt", "Hello World")})
    assert res.status_code == 429, f"Expected 429 Too Many Requests, got {res.status_code}"
    print("✅ Passed: Rate limit strictly enforced after 60 requests!")

if __name__ == "__main__":
    try:
        test_auth()
        print("\n🎉 ALL AUTH & RATE LIMITING TESTS PASSED!")
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
