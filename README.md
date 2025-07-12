# Cline OAuth Callback Server

A FastAPI-based HTTPS server that handles OAuth callbacks for the Cline VSCode extension.

## 🎯 Purpose

This server acts as a bridge between OAuth providers that only support HTTP(S) redirect URIs and the Cline VSCode extension that needs to receive OAuth callbacks via custom URI schemes.

## 🔄 Flow

1. **User clicks "Sign In"** in VSCode extension
2. **Browser opens** OAuth provider login page
3. **User authenticates** with OAuth provider
4. **OAuth provider redirects** to `https://your-server.com/oauth/oidc/callback`
5. **This server receives** the authorization code
6. **Server redirects** to `vscode://saoudrizwan.claude-dev/auth` with the code
7. **VSCode extension** completes the token exchange

## 📋 Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- OpenSSL (for HTTPS certificates)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Development Server (HTTP)

For testing purposes:

```bash
python run_dev.py
```

This runs on `http://localhost:8000` (⚠️ OAuth providers may reject HTTP callbacks)

### 3. Run Production Server (HTTPS)

For production use:

```bash
python run_prod.py
```

This automatically generates SSL certificates and runs on `https://localhost:8000`

## 🔧 Configuration

### Update Your OAuth Provider

Configure your OAuth provider to use this callback URL:

```
https://your-server.com:8000/oauth/oidc/callback
```

### Update Cline Extension

In your Cline extension's `src/services/auth/AuthService.ts`, set the redirect URI:

```typescript
redirectUri: "https://your-server.com:8000/oauth/oidc/callback"
```

## 🔍 Testing

Test the callback endpoint:

```bash
curl "http://localhost:8000/oauth/oidc/callback?code=test123&state=test456"
```

Should redirect to VSCode with the test parameters.

## 🚨 Security Notes

1. **HTTPS Required**: OAuth providers typically require HTTPS callbacks
2. **State Validation**: The server passes through the state parameter for CSRF protection
3. **Error Handling**: Proper error responses for failed authentication
4. **Logging**: All attempts are logged for debugging

## 📡 API Endpoints

- `GET /`: Health check
- `GET /oauth/oidc/callback`: OAuth callback handler
- `GET /health`: Health check for monitoring

## 🐛 Troubleshooting

- **"OAuth provider rejected redirect URI"**: Ensure HTTPS and exact URL match
- **"VSCode doesn't open"**: Check extension is installed and URI scheme is correct
- **"Missing authorization code"**: Verify OAuth provider configuration
- **"SSL certificate errors"**: Use real certificates for production

## 🔗 Integration

1. **Fill in your OAuth details** in Cline extension
2. **Deploy this server** with HTTPS
3. **Configure OAuth provider** to use this server's callback URL
4. **Test the complete flow**

Your OAuth provider will send JWTs (JSON Web Tokens) including:
- `access_token`: For API access
- `id_token`: User identity information
- `refresh_token`: For token renewal

The server acts as a bridge - it doesn't process the JWTs, just passes the authorization code to VSCode.
