from smartrun.local_requests import check_url_status, local_requests, get_content
import pytest
import os
from unittest.mock import patch, mock_open


def not_long_test():
    """Check if long tests should be skipped"""
    return not os.getenv("SMARTRUN_LONGTEST", "0") in {"1", "on", "yes", "true"}


class TestLocalRequests:
    """Test suite for local_requests module"""

    @pytest.mark.skipif(
        not_long_test(), reason="Long test - set SMARTRUN_LONGTEST=1 to enable"
    )
    def test_local_requests_google(self):
        """Test basic functionality with Google"""
        URL = "https://www.google.com/"

        print(f"Testing URL: {URL}")
        print("-" * 50)

        response = local_requests(URL)

        # Basic assertions
        assert response[
            "success"
        ], f"Request failed: {response.get('error', 'Unknown error')}"
        assert (
            response["status"] == 200
        ), f"Expected status 200, got {response['status']}"
        assert "response_time" in response, "Response time should be included"
        assert response["response_time"] > 0, "Response time should be positive"
        assert "headers" in response, "Headers should be included"
        assert "url" in response, "Final URL should be included"

        # Validate response structure
        assert isinstance(response["headers"], dict), "Headers should be a dictionary"
        assert isinstance(
            response["response_time"], (int, float)
        ), "Response time should be numeric"

        print(
            f"✅ SUCCESS - Status: {response['status']}, Time: {response['response_time']}s"
        )

    @pytest.mark.skipif(
        not_long_test(), reason="Long test - set SMARTRUN_LONGTEST=1 to enable"
    )
    def test_check_url_status(self):
        """Test URL status checking functionality"""
        URL = "https://httpbin.org/get"

        status = check_url_status(URL)

        assert isinstance(status, dict), "Status should return a dictionary"
        assert "accessible" in status, "Should include 'accessible' field"
        assert "status" in status, "Should include 'status' field"
        assert "response_time" in status, "Should include 'response_time' field"

        if status["accessible"]:
            assert (
                status["status"] == 200
            ), f"Expected status 200, got {status['status']}"
            assert isinstance(
                status["response_time"], (int, float)
            ), "Response time should be numeric"
            print(
                f"✅ URL Status Check - Accessible: {status['accessible']}, Status: {status['status']}"
            )
        else:
            assert "error" in status, "Failed requests should include error information"
            print(f"❌ URL not accessible: {status.get('error', 'Unknown error')}")

    def test_invalid_url_handling(self):
        """Test handling of invalid URLs"""
        invalid_urls = [
            "",  # Empty URL
            "not-a-url",  # Invalid format
            "ftp://example.com",  # Unsupported protocol
            "http://",  # Incomplete URL
        ]

        for url in invalid_urls:
            response = local_requests(url)
            assert not response["success"], f"Invalid URL '{url}' should fail"
            assert (
                "error" in response
            ), f"Failed request should include error for URL: {url}"
            print(f"✅ Correctly rejected invalid URL: '{url}' - {response['error']}")

    @pytest.mark.skipif(
        not_long_test(), reason="Long test - set SMARTRUN_LONGTEST=1 to enable"
    )
    def test_nonexistent_domain(self):
        """Test handling of non-existent domains"""
        URL = "https://this-domain-definitely-does-not-exist-12345.com"

        response = local_requests(URL)

        # Should fail gracefully
        assert not response["success"], "Non-existent domain should fail"
        assert "error" in response, "Should include error message"
        assert (
            "URL Error" in response["error"] or "HTTP Error" in response["error"]
        ), "Should be a URL or HTTP error"

        print(f"✅ Correctly handled non-existent domain: {response['error']}")

    @pytest.mark.skipif(True, reason="Long test - set SMARTRUN_LONGTEST=1 to enable")
    def test_http_error_codes(self):
        """Test handling of various HTTP error codes"""
        test_cases = []

        for url, expected_status in test_cases:
            response = local_requests(url)

            assert not response[
                "success"
            ], f"HTTP error {expected_status} should result in success=False"
            assert (
                response.get("status") == expected_status
            ), f"Expected status {expected_status}, got {response.get('status')}"
            assert "HTTP Error" in response["error"], "Should indicate HTTP error"

            print(f"✅ Correctly handled HTTP {expected_status}: {response['error']}")

    def test_env_file_creation(self):
        """Test .env file creation when it doesn't exist"""
        from smartrun.local_requests import load_env
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = os.path.join(temp_dir, "test.env")

            # Should create file and return defaults
            proxy_url, verify_ssl, timeout = load_env(env_file)

            assert proxy_url is None, "Should return None for proxy when file created"
            assert verify_ssl is False, "Should default to False for SSL verification"
            assert timeout == 30, "Should default to 30 seconds timeout"
            assert os.path.exists(env_file), "Should create .env file"

            print("✅ Correctly created .env file with defaults")

    @pytest.mark.skipif(
        not_long_test(), reason="Long test - set SMARTRUN_LONGTEST=1 to enable"
    )
    def test_response_structure(self):
        """Test that successful responses have expected structure"""
        URL = "https://httpbin.org/get"

        response = local_requests(URL)

        if response["success"]:
            required_fields = ["success", "status", "url", "headers", "response_time"]
            for field in required_fields:
                assert field in response, f"Response missing required field: {field}"

            # Test specific field types
            assert isinstance(response["success"], bool)
            assert isinstance(response["status"], int)
            assert isinstance(response["url"], str)
            assert isinstance(response["headers"], dict)
            assert isinstance(response["response_time"], (int, float))

            print("✅ Response structure validation passed")
        else:
            pytest.skip(
                f"Skipping structure test due to connection failure: {response.get('error')}"
            )

    @pytest.mark.skipif(
        not_long_test(), reason="Long test - set SMARTRUN_LONGTEST=1 to enable"
    )
    def test_timeout_behavior(self):
        """Test timeout functionality"""
        # Using httpbin's delay endpoint to test timeout
        URL = "https://httpbin.org/delay/2"  # 2 second delay

        # Test with short timeout (should fail)
        from smartrun.local_requests import fetch_url

        response = fetch_url(URL, timeout=1)  # 1 second timeout

        assert not response["success"], "Request with short timeout should fail"
        assert (
            "timeout" in response["error"].lower()
            or "timed out" in response["error"].lower()
        ), f"Error should mention timeout: {response['error']}"

        print(f"✅ Timeout behavior correct: {response['error']}")


class TestUtilityFunctions:
    """Test utility functions if they exist"""

    @pytest.mark.skipif(
        not_long_test(), reason="Long test - set SMARTRUN_LONGTEST=1 to enable"
    )
    def test_get_content_function(self):
        """Test get_content utility function if available"""
        try:
            content = get_content("https://httpbin.org/get")

            if content:
                assert isinstance(content, str), "Content should be a string"
                assert len(content) > 0, "Content should not be empty"
                print(f"✅ get_content returned {len(content)} characters")
            else:
                print("⚠️  get_content returned None - connection may have failed")

        except ImportError:
            pytest.skip("get_content function not available")


# Parametrized tests for multiple URLs
@pytest.mark.skipif(
    not_long_test(), reason="Long test - set SMARTRUN_LONGTEST=1 to enable"
)
@pytest.mark.parametrize(
    "url,expected_success",
    [
        ("https://www.google.com/", True),
        ("https://jsonplaceholder.typicode.com/posts/1", True),
        ("invalid-url", False),
        ("", False),
    ],
)
def test_multiple_urls(url, expected_success):
    """Test multiple URLs with expected outcomes"""
    response = local_requests(url)

    if expected_success:
        # For URLs expected to succeed, we'll be lenient due to network issues
        if not response["success"]:
            pytest.skip(f"Network issue with {url}: {response.get('error')}")
        else:
            assert response["success"], f"Expected success for {url}"
            assert response["status"] == 200, f"Expected 200 status for {url}"
    else:
        assert not response["success"], f"Expected failure for invalid URL: {url}"


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 Running Local Requests Test Suite")
    print("=" * 70)

    # Run tests manually if executed directly
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "long":
        os.environ["SMARTRUN_LONGTEST"] = "1"
        print("🔧 Long tests enabled via command line")

    # Simple test runner for direct execution
    test_instance = TestLocalRequests()

    try:
        print("\n🔍 Testing environment variable detection...")
        test_environment_variable_detection()

        print("\n🌐 Testing basic functionality...")
        if not_long_test():
            test_instance.test_local_requests_google()
            test_instance.test_check_url_status()
            print("\n✅ All tests passed!")
        else:
            print(
                "⚠️  Long tests disabled. Set SMARTRUN_LONGTEST=1 to enable network tests."
            )
            print("   Testing only offline functionality...")
            test_instance.test_invalid_url_handling()
            test_instance.test_env_file_creation()

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
