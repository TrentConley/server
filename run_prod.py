#!/usr/bin/env python3
"""
Production server runner with conditional SSL support.

This script runs the server in one of two modes:
- HTTPS mode: If SSL_KEYFILE and SSL_CERTFILE environment variables are set and point
  to valid files. This is for standalone deployments.
- HTTP mode: If the SSL variables are not set. This is for environments like
  Railway where a proxy handles SSL termination.
"""

import uvicorn
import os
from main import app

if __name__ == "__main__":
    # Get host and port from environment variables, with defaults
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    # Get SSL configuration from environment variables
    ssl_keyfile = os.environ.get("SSL_KEYFILE")
    ssl_certfile = os.environ.get("SSL_CERTFILE")

    uvicorn_kwargs = {
        "host": host,
        "port": port,
        "reload": False,
        "log_level": "info"
    }

    print("🚀 Starting Cline OAuth Callback Server (Production Mode)")

    # Check if SSL is configured and files exist
    if ssl_keyfile and ssl_certfile:
        if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
            uvicorn_kwargs["ssl_keyfile"] = ssl_keyfile
            uvicorn_kwargs["ssl_certfile"] = ssl_certfile
            print(f"🔐 Running in HTTPS mode.")
            print(f"📋 Server will run on: https://{host}:{port}")
        else:
            print(f"❌ SSL files not found: key='{ssl_keyfile}', cert='{ssl_certfile}'")
            print("⚠️  Defaulting to HTTP mode.")
            print(f"📋 Server will run on: http://{host}:{port}")
    else:
        print("🔐 Running in HTTP mode (SSL not configured).")
        print(f"📋 Server will run on: http://{host}:{port}")

    print()
    uvicorn.run("main:app", **uvicorn_kwargs)
