#!/usr/bin/env python3
"""
Development server runner - runs without SSL for testing
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Cline OAuth Callback Server (Development Mode)")
    print("📋 Server will run on: http://localhost:8000")
    print("🔗 Callback endpoint: http://localhost:8000/oauth/oidc/callback")
    print("⚠️  This is for development only - use HTTPS in production!")
    print()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
