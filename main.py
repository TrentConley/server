import os
import httpx
import logging
import urllib.parse
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from jose.exceptions import JWTError

# --- Configuration ---
# Load from environment variables
OIDC_PROVIDER_URL = os.environ.get("OIDC_PROVIDER_URL", "https://accounts.google.com")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
# This is the URL of this server, as seen by the user's browser.
# For Railway, this will be your public app URL (e.g., https://my-app.up.railway.app)
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8000")
# The VSCode extension's custom URI scheme
VSCODE_EXTENSION_ID = os.environ.get("VSCODE_EXTENSION_ID", "saoudrizwan.claude-dev")

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(
    title="Generic OIDC Callback Server",
    description="A generic OIDC callback handler for desktop extensions.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- OIDC Discovery and Token Validation ---
oidc_config = {}
jwks_client = None

@app.on_event("startup")
async def startup_event():
    """
    On startup, fetch the OIDC provider's configuration (discovery document).
    This makes the server adaptable to any OIDC provider.
    """
    global oidc_config, jwks_client
    if not all([CLIENT_ID, CLIENT_SECRET]):
        logger.error("FATAL: CLIENT_ID and CLIENT_SECRET environment variables are not set.")
        # In a real app, you might want to exit here if running in production
        # For now, we'll let it run to allow for health checks.
    
    discovery_url = f"{OIDC_PROVIDER_URL}/.well-known/openid-configuration"
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching OIDC discovery document from: {discovery_url}")
            response = await client.get(discovery_url)
            response.raise_for_status()
            oidc_config = response.json()
            logger.info("Successfully loaded OIDC configuration.")
            
            # Create a client to fetch the JWKS for token signature validation
            jwks_uri = oidc_config.get("jwks_uri")
            if not jwks_uri:
                raise ValueError("jwks_uri not found in OIDC configuration")
            
            jwks_client = jwt.PyJWKClient(jwks_uri)

    except (httpx.RequestError, ValueError, KeyError) as e:
        logger.error(f"Failed to initialize OIDC configuration: {e}")
        # This is a critical failure. The app cannot function without this.
        oidc_config = {}

# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check and information endpoint."""
    return {
        "message": "OIDC Callback Server is running",
        "oidc_provider": OIDC_PROVIDER_URL,
        "oidc_config_loaded": bool(oidc_config)
    }

@app.get("/login")
async def login(request: Request, state: Optional[str] = None):
    """
    Initiates the OIDC login flow.
    Redirects the user to the OIDC provider's authorization endpoint.
    The 'state' parameter is passed through and is essential for security.
    """
    if not oidc_config:
        raise HTTPException(status_code=503, detail="OIDC provider not configured. Check server logs.")
    if not state:
        raise HTTPException(status_code=400, detail="The 'state' parameter is required.")

    redirect_uri = f"{APP_BASE_URL}/oauth/oidc/callback"
    
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "state": state,
    }
    
    auth_url = oidc_config["authorization_endpoint"]
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    logger.info(f"Redirecting user to OIDC provider for login: {auth_url}")
    return RedirectResponse(full_auth_url)

@app.get("/oauth/oidc/callback")
async def oauth_callback(request: Request, code: str, state: str):
    """
    Handles the callback from the OIDC provider after user authentication.
    Exchanges the authorization code for tokens and redirects to the VSCode extension.
    """
    if not oidc_config:
        raise HTTPException(status_code=503, detail="OIDC provider not configured. Check server logs.")

    redirect_uri = f"{APP_BASE_URL}/oauth/oidc/callback"
    token_endpoint = oidc_config["token_endpoint"]

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Exchanging authorization code for tokens at: {token_endpoint}")
            token_response = await client.post(token_endpoint, data=token_data)
            token_response.raise_for_status()
            token_json = token_response.json()
            
            id_token = token_json.get("id_token")
            if not id_token:
                raise ValueError("id_token not found in token response")

            # Validate the ID token (signature, claims, etc.)
            # This is a critical security step.
            signing_key = await jwks_client.get_signing_key_from_jwt(id_token)
            decoded_token = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=CLIENT_ID,
                issuer=oidc_config.get("issuer")
            )
            logger.info(f"Successfully validated ID token for user: {decoded_token.get('email')}")

    except (httpx.RequestError, JWTError, ValueError) as e:
        logger.error(f"Error during token exchange or validation: {e}")
        return _create_error_response(
            "Token Exchange Failed",
            "Could not exchange the authorization code for a valid token. Please try again."
        )

    # Pass the full token response to the extension
    vscode_uri = f"vscode://{VSCODE_EXTENSION_ID}/auth?{urllib.parse.urlencode(token_json)}&state={state}"
    
    logger.info("Redirecting to VSCode extension with tokens.")
    return _create_success_response(vscode_uri)

def _create_success_response(vscode_uri: str):
    """Returns a user-friendly HTML page that redirects to the VSCode extension."""
    return HTMLResponse(content=f'''
        <html>
            <head>
                <title>Redirecting to VSCode...</title>
                <meta http-equiv="refresh" content="1;url={vscode_uri}">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-align: center; padding: 40px; background-color: #f8f9fa; }}
                    .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; }}
                    h1 {{ color: #28a745; }}
                    p {{ color: #495057; }}
                    a {{ color: #007bff; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Authentication Successful!</h1>
                    <p>Redirecting you back to VSCode...</p>
                    <p>If you are not redirected automatically, <a href="{vscode_uri}">click here to continue</a>.</p>
                </div>
                <script>window.location.href = "{vscode_uri}";</script>
            </body>
        </html>
    ''')

def _create_error_response(error_title: str, error_description: str):
    """Returns a user-friendly HTML page for displaying errors."""
    return HTMLResponse(content=f'''
        <html>
            <head><title>Authentication Error</title></head>
            <body style='font-family: sans-serif; text-align: center; padding: 40px;'>
                <div style='background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block;'>
                    <h1 style='color: #dc3545;'>{error_title}</h1>
                    <p>{error_description}</p>
                    <button onclick="window.close()">Close Window</button>
                </div>
            </body>
        </html>
    ''', status_code=400)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "cline-oauth-callback"}

# This part is for local development and won't be used by run_prod.py
if __name__ == "__main__":
    import uvicorn
    # This local run uses the dev script's port for consistency
    print("🚀 Starting server in local development mode (not for production)")
    print("🔑 Make sure to set environment variables (e.g., in a .env file)")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000, # Consistent with run_dev.py
        reload=True
    )
