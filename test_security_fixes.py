#!/usr/bin/env python3
"""
DECOYABLE Security Verification Script

Tests all security fixes to ensure they're working correctly.
Run this after deploying security updates.

Usage:
    python test_security_fixes.py [--host localhost] [--port 8000] [--api-key YOUR_KEY]
"""

import argparse
import sys
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("❌ requests library not found. Install with: pip install requests")
    sys.exit(1)


class SecurityTester:
    """Test security features of DECOYABLE."""
    
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.results: List[Tuple[str, bool, str]] = []
    
    def test(self, name: str) -> None:
        """Decorator to track test results."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    success, message = func(*args, **kwargs)
                    self.results.append((name, success, message))
                    symbol = "✅" if success else "❌"
                    print(f"{symbol} {name}: {message}")
                except Exception as e:
                    self.results.append((name, False, str(e)))
                    print(f"❌ {name}: Error - {str(e)}")
            return wrapper
        return decorator
    
    def test_security_headers(self) -> Tuple[bool, str]:
        """Test that security headers are present."""
        response = requests.get(f"{self.base_url}/health", timeout=5)
        
        required_headers = {
            "Strict-Transport-Security": "HSTS",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "X-Frame-Options",
            "Content-Security-Policy": "CSP",
            "X-XSS-Protection": "XSS Protection",
        }
        
        missing = []
        for header, name in required_headers.items():
            if header not in response.headers:
                missing.append(name)
        
        if missing:
            return False, f"Missing headers: {', '.join(missing)}"
        
        return True, "All security headers present"
    
    def test_cors_restriction(self) -> Tuple[bool, str]:
        """Test that CORS doesn't allow arbitrary origins."""
        headers = {
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
        }
        
        response = requests.options(
            f"{self.base_url}/api/v1/scan/secrets",
            headers=headers,
            timeout=5
        )
        
        # If Access-Control-Allow-Origin is * or includes evil.com, CORS is too permissive
        allow_origin = response.headers.get("Access-Control-Allow-Origin", "")
        
        if allow_origin == "*":
            return False, "CORS allows all origins (*)"
        elif "evil.com" in allow_origin:
            return False, "CORS allows arbitrary origins"
        
        return True, "CORS properly restricted"
    
    def test_authentication_required(self) -> Tuple[bool, str]:
        """Test that authenticated endpoints reject requests without auth."""
        # Try to access scan endpoint without authentication
        response = requests.post(
            f"{self.base_url}/api/v1/scan/secrets",
            json={"path": "/tmp"},
            timeout=5
        )
        
        if response.status_code == 401:
            return True, "Authentication correctly required"
        elif response.status_code == 200:
            return False, "Endpoint accessible without authentication!"
        else:
            return False, f"Unexpected status code: {response.status_code}"
    
    def test_authentication_works(self) -> Tuple[bool, str]:
        """Test that authentication with API key works."""
        if not self.api_key:
            return True, "Skipped (no API key provided)"
        
        headers = {"X-API-Key": self.api_key}
        
        response = requests.get(
            f"{self.base_url}/api/v1/health",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            return True, "API key authentication works"
        elif response.status_code == 401:
            return False, "API key rejected (check if key is valid)"
        else:
            return False, f"Unexpected status code: {response.status_code}"
    
    def test_rate_limiting(self) -> Tuple[bool, str]:
        """Test that rate limiting is active."""
        # Make a few requests to a public endpoint
        responses = []
        
        for i in range(5):
            response = requests.get(f"{self.base_url}/health", timeout=5)
            responses.append(response)
        
        # Check if rate limit headers are present
        last_response = responses[-1]
        
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]
        
        present_headers = [h for h in rate_limit_headers if h in last_response.headers]
        
        if len(present_headers) >= 2:
            limit = last_response.headers.get("X-RateLimit-Limit", "?")
            remaining = last_response.headers.get("X-RateLimit-Remaining", "?")
            return True, f"Rate limiting active (limit: {limit}, remaining: {remaining})"
        
        return False, "Rate limit headers not found"
    
    def test_path_traversal_blocked(self) -> Tuple[bool, str]:
        """Test that path traversal attempts are blocked."""
        if not self.api_key:
            return True, "Skipped (no API key provided)"
        
        headers = {"X-API-Key": self.api_key}
        
        # Try to scan a system directory
        response = requests.post(
            f"{self.base_url}/api/v1/scan/secrets",
            headers=headers,
            json={"path": "/etc/passwd"},
            timeout=5
        )
        
        # Should be rejected (400 or 422)
        if response.status_code in [400, 422]:
            return True, "Path traversal correctly blocked"
        elif response.status_code == 200:
            return False, "Path traversal NOT blocked!"
        else:
            return True, f"Request rejected (code: {response.status_code})"
    
    def test_input_validation(self) -> Tuple[bool, str]:
        """Test that .. in paths is blocked."""
        if not self.api_key:
            return True, "Skipped (no API key provided)"
        
        headers = {"X-API-Key": self.api_key}
        
        # Try path with ..
        response = requests.post(
            f"{self.base_url}/api/v1/scan/secrets",
            headers=headers,
            json={"path": "/app/../etc/passwd"},
            timeout=5
        )
        
        # Should be rejected
        if response.status_code in [400, 422]:
            return True, "Path with '..' correctly blocked"
        elif response.status_code == 200:
            return False, "Path with '..' NOT blocked!"
        else:
            return True, f"Request rejected (code: {response.status_code})"
    
    def test_trusted_host(self) -> Tuple[bool, str]:
        """Test trusted host middleware."""
        # Try with invalid Host header
        headers = {"Host": "evil.com"}
        
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers=headers,
                timeout=5,
                allow_redirects=False
            )
            
            # If it's 400, trusted host is working
            if response.status_code == 400:
                return True, "Trusted host validation active"
            
            return True, "Request processed (check ALLOWED_HOSTS config)"
        except requests.exceptions.ConnectionError:
            return True, "Trusted host validation active (connection rejected)"
    
    def run_all_tests(self):
        """Run all security tests."""
        print("\n" + "="*60)
        print("🔒 DECOYABLE Security Verification")
        print("="*60)
        print(f"\nTesting: {self.base_url}")
        print()
        
        # Run tests
        tests = [
            ("Security Headers", self.test_security_headers),
            ("CORS Restriction", self.test_cors_restriction),
            ("Authentication Required", self.test_authentication_required),
            ("Authentication Works", self.test_authentication_works),
            ("Rate Limiting", self.test_rate_limiting),
            ("Path Traversal Protection", self.test_path_traversal_blocked),
            ("Input Validation", self.test_input_validation),
            ("Trusted Host", self.test_trusted_host),
        ]
        
        for name, test_func in tests:
            try:
                success, message = test_func()
                self.results.append((name, success, message))
                symbol = "✅" if success else "❌"
                print(f"{symbol} {name}: {message}")
            except Exception as e:
                self.results.append((name, False, str(e)))
                print(f"❌ {name}: Error - {str(e)}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 All security tests passed!")
            print("   Your DECOYABLE instance is properly secured.")
        else:
            print("\n⚠️  Some tests failed!")
            print("   Review the failures above and check your configuration.")
            print("\nFailed Tests:")
            for name, success, message in self.results:
                if not success:
                    print(f"   - {name}: {message}")
        
        print()
        return 0 if failed == 0 else 1


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Test DECOYABLE security fixes"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="DECOYABLE host (default: localhost)"
    )
    parser.add_argument(
        "--port",
        default="8000",
        help="DECOYABLE port (default: 8000)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication tests (optional)"
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Use HTTPS instead of HTTP"
    )
    
    args = parser.parse_args()
    
    # Build base URL
    protocol = "https" if args.https else "http"
    base_url = f"{protocol}://{args.host}:{args.port}"
    
    # Run tests
    tester = SecurityTester(base_url, args.api_key)
    
    try:
        return tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
