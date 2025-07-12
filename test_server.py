#!/usr/bin/env python3
"""
Test script to verify the OAuth callback server
"""

import requests
import sys
import time
import subprocess
import signal
import os
from urllib.parse import urlparse

def test_server(base_url="http://localhost:8000"):
    """Test the OAuth callback server endpoints"""
    print(f"🧪 Testing OAuth callback server at {base_url}")
    print()
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 3: OAuth callback with valid parameters
    print("\n3. Testing OAuth callback with valid parameters...")
    try:
        response = requests.get(
            f"{base_url}/oauth/oidc/callback",
            params={"code": "test123", "state": "test456"},
            timeout=5,
            allow_redirects=False
        )
        if response.status_code == 200:
            print("✅ OAuth callback passed")
            print("   Response contains HTML with VSCode redirect")
            # Check if response contains the expected VSCode URI
            if "vscode://saoudrizwan.claude-dev/auth" in response.text:
                print("   ✅ VSCode URI found in response")
            else:
                print("   ⚠️  VSCode URI not found in response")
        else:
            print(f"❌ OAuth callback failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OAuth callback failed: {e}")
        return False
    
    # Test 4: OAuth callback with error
    print("\n4. Testing OAuth callback with error...")
    try:
        response = requests.get(
            f"{base_url}/oauth/oidc/callback",
            params={"error": "access_denied", "error_description": "User denied access"},
            timeout=5,
            allow_redirects=False
        )
        if response.status_code == 400:
            print("✅ OAuth error handling passed")
            print("   Server correctly returned 400 for OAuth error")
        else:
            print(f"❌ OAuth error handling failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OAuth error handling failed: {e}")
        return False
    
    # Test 5: OAuth callback with missing parameters
    print("\n5. Testing OAuth callback with missing parameters...")
    try:
        response = requests.get(
            f"{base_url}/oauth/oidc/callback",
            timeout=5,
            allow_redirects=False
        )
        if response.status_code == 400:
            print("✅ Parameter validation passed")
            print("   Server correctly returned 400 for missing parameters")
        else:
            print(f"❌ Parameter validation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Parameter validation failed: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

def start_test_server():
    """Start the development server for testing"""
    print("🚀 Starting test server...")
    try:
        process = subprocess.Popen(
            [sys.executable, "run_dev.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ Test server started successfully")
            return process
        else:
            print("❌ Test server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start test server: {e}")
        return None

def stop_test_server(process):
    """Stop the test server"""
    if process:
        try:
            # Kill the process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            process.wait(timeout=5)
            print("✅ Test server stopped")
        except Exception as e:
            print(f"⚠️  Error stopping test server: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test against provided URL
        base_url = sys.argv[1]
        success = test_server(base_url)
    else:
        # Start our own test server
        server_process = start_test_server()
        if server_process:
            try:
                success = test_server()
            finally:
                stop_test_server(server_process)
        else:
            success = False
    
    sys.exit(0 if success else 1)
