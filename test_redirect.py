#!/usr/bin/env python3
"""
Test script to verify the redirect behavior of the OAuth callback server
"""

import requests
import sys

def test_redirect_behavior(base_url="http://localhost:8000", use_direct_redirect=False):
    """Test how the server handles redirects to vscode:// URIs"""
    
    print(f"Testing OAuth callback server at {base_url}")
    print(f"Direct redirect mode: {use_direct_redirect}")
    print("-" * 50)
    
    # Test successful OAuth callback
    test_params = {
        "code": "test_auth_code_123",
        "state": "test_state_456"
    }
    
    try:
        # Make request without following redirects
        response = requests.get(
            f"{base_url}/oauth/oidc/callback",
            params=test_params,
            allow_redirects=False,
            timeout=5
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"Redirect location: {response.headers.get('Location')}")
        elif response.status_code == 200:
            print("Response is HTML (not a redirect)")
            if "vscode://" in response.text:
                print("✓ HTML contains vscode:// URI")
                # Extract the URI from the HTML
                import re
                uri_match = re.search(r'href="(vscode://[^"]+)"', response.text)
                if uri_match:
                    print(f"Found URI in HTML: {uri_match.group(1)[:100]}...")
            else:
                print("✗ HTML does not contain vscode:// URI")
                
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print("Testing with HTML response (default)...")
    test_redirect_behavior(base_url, use_direct_redirect=False)
    
    print("\n\nTo test with direct redirect, set USE_DIRECT_REDIRECT=true in your environment")
    print("and restart the server.") 