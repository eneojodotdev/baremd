from markitdown import MarkItDown
import traceback

def run_tests():
    md = MarkItDown()
    
    test_cases = [
        ("Localhost (127.0.0.1)", "http://127.0.0.1:8001/api/convert", True),
        ("Metadata Service (169.254)", "http://169.254.169.254/latest/meta-data/", True),
        ("Localhost Domain (localhost)", "http://localhost:8001/api/convert", True),
        ("File URI", "file:///etc/passwd", True),
        ("Public Domain", "http://example.com", False)
    ]
    
    all_passed = True
    
    for name, uri, should_fail in test_cases:
        print(f"Testing {name}: {uri}")
        try:
            md.convert(uri)
            if should_fail:
                print(f"❌ FAILED: {uri} successfully connected, but it should have been BLOCKED!")
                all_passed = False
            else:
                print(f"✅ PASSED: {uri} successfully connected as expected.")
        except Exception as e:
            if should_fail:
                print(f"✅ PASSED (Blocked): {type(e).__name__} - {e}")
            else:
                print(f"❌ FAILED: {uri} was blocked, but it should have SUCCEEDED! Error: {e}")
                all_passed = False
                
    if all_passed:
        print("\n🎉 ALL SSRF TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED.")

if __name__ == "__main__":
    run_tests()
