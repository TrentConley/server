#!/usr/bin/env python3
"""
Production server runner for cloud environments like Railway.
This script runs the server on HTTP, as SSL is handled by the provider.
"""

import uvicorn
import os
from main import app

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting Cline OAuth Callback Server (Production Mode)")
    print(f"📋 Server will run on: http://0.0.0.0:{port}")
    print(f"🔗 Callback endpoint will be determined by your Railway URL.")
    print("🔐 SSL/TLS is handled by the Railway proxy.")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
