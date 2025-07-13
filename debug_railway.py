#!/usr/bin/env python3
"""
Debug script to help identify Railway startup issues
"""
import os
import sys

print("=== Railway Debug Info ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"HOST: {os.environ.get('HOST', 'not set')}")
print(f"PORT: {os.environ.get('PORT', 'not set')}")
print(f"CLIENT_ID: {'set' if os.environ.get('CLIENT_ID') else 'NOT SET'}")
print(f"CLIENT_SECRET: {'set' if os.environ.get('CLIENT_SECRET') else 'NOT SET'}")
print(f"APP_BASE_URL: {os.environ.get('APP_BASE_URL', 'not set')}")
print(f"OIDC_PROVIDER_URL: {os.environ.get('OIDC_PROVIDER_URL', 'not set')}")
print(f"VSCODE_EXTENSION_ID: {os.environ.get('VSCODE_EXTENSION_ID', 'not set')}")

print("\n=== Testing imports ===")
try:
    import fastapi
    print(f"✅ FastAPI: {fastapi.__version__}")
except Exception as e:
    print(f"❌ FastAPI import error: {e}")

try:
    import uvicorn
    print(f"✅ Uvicorn: {uvicorn.__version__}")
except Exception as e:
    print(f"❌ Uvicorn import error: {e}")

try:
    import httpx
    print(f"✅ HTTPX: {httpx.__version__}")
except Exception as e:
    print(f"❌ HTTPX import error: {e}")

try:
    import jwt
    print(f"✅ PyJWT: {jwt.__version__}")
except Exception as e:
    print(f"❌ PyJWT import error: {e}")

print("\n=== Testing main.py import ===")
try:
    from main import app
    print("✅ Main app imported successfully")
except Exception as e:
    print(f"❌ Main app import error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Testing startup event ===")
try:
    import asyncio
    from main import startup_event
    asyncio.run(startup_event())
    print("✅ Startup event completed")
except Exception as e:
    print(f"❌ Startup event error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Debug complete ===") 