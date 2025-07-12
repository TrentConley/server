from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import urllib.parse
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cline OAuth Callback Server",
    description="OAuth callback handler for Cline VSCode extension",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Cline OAuth Callback Server is running"}

@app.get("/oauth/oidc/callback")
async def oauth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
):
    """
    Handle OAuth callback from OIDC provider and redirect to VSCode extension.
    
    This endpoint receives the authorization code from the OAuth provider
    and redirects to the VSCode extension with the code and state parameters.
    """
    logger.info(f"OAuth callback received: code={code is not None}, state={state}, error={error}")
    
    # Handle OAuth errors
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        error_message = f"OAuth Error: {error}"
        if error_description:
            error_message += f" - {error_description}"
        
        # Return error page with option to retry
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <title>OAuth Error</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; text-align: center; }}
                        .error {{ color: red; margin: 20px 0; }}
                        .retry {{ margin: 20px 0; }}
                        button {{ padding: 10px 20px; font-size: 16px; cursor: pointer; }}
                    </style>
                </head>
                <body>
                    <h1>OAuth Authentication Error</h1>
                    <div class="error">{error_message}</div>
                    <div class="retry">
                        <button onclick="window.close()">Close Window</button>
                    </div>
                </body>
            </html>
            """,
            status_code=400
        )
    
    # Validate required parameters
    if not code:
        logger.error("Missing authorization code in OAuth callback")
        raise HTTPException(
            status_code=400, 
            detail="Missing authorization code. Please try the authentication process again."
        )
    
    if not state:
        logger.error("Missing state parameter in OAuth callback")
        raise HTTPException(
            status_code=400,
            detail="Missing state parameter. Please try the authentication process again."
        )
    
    # Create VSCode extension URI with the authorization code and state
    vscode_uri = f"vscode://saoudrizwan.claude-dev/auth?code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}"
    
    logger.info(f"Redirecting to VSCode extension: {vscode_uri}")
    
    # Return an HTML page that redirects to VSCode
    # This is more reliable than a direct redirect for custom URI schemes
    return HTMLResponse(
        content=f"""
        <html>
            <head>
                <title>Redirecting to VSCode...</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        padding: 20px; 
                        text-align: center; 
                        background-color: #f5f5f5; 
                    }}
                    .container {{ 
                        max-width: 500px; 
                        margin: 50px auto; 
                        padding: 30px; 
                        background: white; 
                        border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                    }}
                    .spinner {{ 
                        border: 4px solid #f3f3f3; 
                        border-top: 4px solid #3498db; 
                        border-radius: 50%; 
                        width: 40px; 
                        height: 40px; 
                        animation: spin 1s linear infinite; 
                        margin: 20px auto; 
                    }}
                    @keyframes spin {{ 
                        0% {{ transform: rotate(0deg); }} 
                        100% {{ transform: rotate(360deg); }} 
                    }}
                    .manual-link {{ 
                        margin-top: 20px; 
                        padding: 10px 20px; 
                        background-color: #007acc; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 5px; 
                        display: inline-block; 
                    }}
                    .manual-link:hover {{ 
                        background-color: #005a9e; 
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Authentication Successful!</h1>
                    <div class="spinner"></div>
                    <p>Redirecting to VSCode...</p>
                    <p>If the redirect doesn't work automatically, click the button below:</p>
                    <a href="{vscode_uri}" class="manual-link">Open in VSCode</a>
                    <p style="margin-top: 20px; font-size: 12px; color: #666;">
                        You can close this window once VSCode opens.
                    </p>
                </div>
                <script>
                    // Automatic redirect after a short delay
                    setTimeout(function() {{
                        window.location.href = "{vscode_uri}";
                    }}, 2000);
                </script>
            </body>
        </html>
        """
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "cline-oauth-callback"}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="key.pem",  # You'll need to generate these
        ssl_certfile="cert.pem"
    )
