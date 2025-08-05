import ssl
from urllib.request import urlopen, Request, ProxyHandler, build_opener, HTTPSHandler
from urllib.error import URLError, HTTPError
from pprint import pprint
from pathlib import Path
import time
from typing import Dict, Tuple, Optional, Union


def local_requests(url: str) -> Dict[str, Union[bool, str, int, float, dict]]:
    """
    Simplified interface to fetch URLs with automatic configuration loading.

    Args:
        url: URL to fetch

    Returns:
        Dict containing response data or error information
    """
    proxy_url, verify_ssl, timeout = load_env()
    result = fetch_url(url, proxy_url, verify_ssl, timeout)
    return result


def load_env(env_file: str = ".env") -> Tuple[Optional[str], bool, int]:
    """
    Load proxy URL from .env file with improved parsing.

    Args:
        env_file: Path to environment file

    Returns:
        Tuple of (proxy_url, verify_ssl, timeout)
    """
    env_path = Path(env_file)
    if not env_path.exists():
        # Create sample .env file
        sample_content = """# Proxy Configuration
http_proxy=http://proxy.example.com:8080
# For authenticated proxy:
# http_proxy=http://username:password@proxy.example.com:8080
# SSL verification (false to disable certificate checking)
verify_ssl=false
# Request timeout in seconds
timeout=30
# Optional: User-Agent override
# user_agent=Custom User Agent String
"""
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(sample_content)
            print(f"✓ Created sample {env_file} - please configure your settings")
        except Exception as e:
            print(f"Warning: Could not create {env_file}: {e}")
        return None, False, 30
    try:
        with open(env_path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        env_vars = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.count("=") != 1:
                continue
            key, value = line.split("=", 1)
            env_vars[key.strip().lower()] = value.strip().strip("\"'")
        proxy_url = env_vars.get("http_proxy") or env_vars.get("proxy_url")
        verify_ssl = env_vars.get("verify_ssl", "false").lower() == "true"

        # Add validation for timeout
        try:
            timeout = int(env_vars.get("timeout", "30"))
            if timeout <= 0:
                print("Warning: Invalid timeout value, using default 30 seconds")
                timeout = 30
        except ValueError:
            print("Warning: Non-numeric timeout value, using default 30 seconds")
            timeout = 30
        return proxy_url, verify_ssl, timeout
    except Exception as e:
        print(f"Error loading {env_file}: {e}")
        return None, False, 30


def create_browser_request(
    url: str, custom_headers: Optional[Dict[str, str]] = None
) -> Request:
    """
    Create request with browser-like headers to avoid blocking.

    Args:
        url: URL to request
        custom_headers: Optional custom headers to override defaults

    Returns:
        urllib Request object
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }

    # Merge custom headers if provided
    if custom_headers:
        default_headers.update(custom_headers)
    return Request(url, headers=default_headers)


def create_secure_opener(
    proxy_url: Optional[str] = None, verify_ssl: bool = False
) -> build_opener:
    """
    Create URL opener with SSL and proxy configuration.

    Args:
        proxy_url: Optional proxy URL
        verify_ssl: Whether to verify SSL certificates

    Returns:
        urllib opener object
    """
    handlers = []
    # SSL Configuration
    ssl_context = ssl.create_default_context()
    if not verify_ssl:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        print("⚠️  SSL verification disabled")
    else:
        print("✓ SSL verification enabled")
    https_handler = HTTPSHandler(context=ssl_context)
    handlers.append(https_handler)
    # Proxy Configuration
    if proxy_url:
        proxy_handler = ProxyHandler({"http": proxy_url, "https": proxy_url})
        handlers.append(proxy_handler)
        print(f"✓ Using proxy: {proxy_url}")
    else:
        print("ℹ️  No proxy configured")
    return build_opener(*handlers)


def fetch_url(
    url: str,
    proxy_url: Optional[str] = None,
    verify_ssl: bool = False,
    timeout: int = 30,
    custom_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Union[bool, str, int, float, dict]]:
    """
    Fetch URL with all configurations applied.

    Args:
        url: URL to fetch
        proxy_url: Optional proxy URL
        verify_ssl: Whether to verify SSL certificates
        timeout: Request timeout in seconds
        custom_headers: Optional custom headers

    Returns:
        Dict containing response data or error information
    """
    # Input validation
    if not url:
        return {"success": False, "error": "URL cannot be empty"}

    if not url.startswith(("http://", "https://")):
        return {"success": False, "error": "URL must start with http:// or https://"}
    # Create opener and request
    opener = create_secure_opener(proxy_url, verify_ssl)
    request = create_browser_request(url, custom_headers)
    try:
        start_time = time.time()
        with opener.open(request, timeout=timeout) as response:
            end_time = time.time()
            return {
                "success": True,
                "response": response,
                "status": response.status,
                "url": response.url,
                "headers": dict(response.headers),
                "response_time": round(end_time - start_time, 2),
                "content_length": response.headers.get("content-length", "unknown"),
            }
    except HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error {e.code}: {e.reason}",
            "status": e.code,
        }
    except URLError as e:
        return {
            "success": False,
            "error": f"URL Error: {e.reason}",
            "details": "Check network connection, proxy settings, or URL validity",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "type": type(e).__name__,
        }


# Convenience functions for common use cases
def get_content(url: str) -> Optional[str]:
    """
    Simple function to get content from URL.

    Args:
        url: URL to fetch

    Returns:
        Content as string or None if failed
    """
    result = local_requests(url)

    if result["success"]:
        try:
            return result["response"].read().decode("utf-8")
        except Exception as e:
            print(f"Error reading content: {e}")
            return None
    else:
        print(f"Failed to fetch {url}: {result['error']}")
        return None


def check_url_status(url: str) -> Dict[str, Union[bool, int, str]]:
    """
    Quick function to check if URL is accessible.

    Args:
        url: URL to check

    Returns:
        Dict with status information
    """
    result = local_requests(url)

    return {
        "accessible": result["success"],
        "status": result.get("status", "unknown"),
        "response_time": result.get("response_time", "unknown"),
        "error": result.get("error", None),
    }


"""
    # Test URL
    test_url = "https://httpbin.org/get"
    
    print(f"Testing URL: {test_url}")
    print("-" * 50)
"""
