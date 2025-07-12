#!/usr/bin/env python3
"""
Production server runner - generates SSL certificates and runs with HTTPS
"""

import uvicorn
import subprocess
import os
import sys
from main import app

def generate_ssl_certificates():
    """Generate self-signed SSL certificates if they don't exist"""
    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        print("✅ SSL certificates already exist")
        return True
    
    print("🔐 Generating self-signed SSL certificates...")
    try:
        # Generate private key
        subprocess.run([
            "openssl", "genrsa", "-out", "key.pem", "2048"
        ], check=True)
        
        # Generate certificate
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", "key.pem", "-out", "cert.pem",
            "-days", "365", "-subj", "/CN=localhost"
        ], check=True)
        
        print("✅ SSL certificates generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating SSL certificates: {e}")
        print("📋 Make sure OpenSSL is installed on your system")
        return False
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL first.")
        print("📋 On macOS: brew install openssl")
        print("📋 On Ubuntu/Debian: sudo apt-get install openssl")
        return False

if __name__ == "__main__":
    print("🚀 Starting Cline OAuth Callback Server (Production Mode)")
    print()
    
    # Generate SSL certificates if needed
    if not generate_ssl_certificates():
        print("❌ Failed to generate SSL certificates")
        print("🔄 Falling back to HTTP mode...")
        print()
        
        # Run in HTTP mode
        print("📋 Server will run on: http://localhost:8000")
        print("🔗 Callback endpoint: http://localhost:8000/oauth/oidc/callback")
        print("⚠️  Running in HTTP mode - OAuth providers may reject this!")
        print()
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    else:
        # Run in HTTPS mode
        print("📋 Server will run on: https://localhost:8000")
        print("🔗 Callback endpoint: https://localhost:8000/oauth/oidc/callback")
        print("🔐 Running with SSL certificates")
        print()
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            ssl_keyfile="key.pem",
            ssl_certfile="cert.pem",
            log_level="info"
        )
