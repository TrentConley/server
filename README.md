# Generic OIDC Callback Server

This is a production-ready, containerized FastAPI server that acts as a secure and configurable middleware for handling OIDC (OpenID Connect) callbacks. It is designed to bridge the gap between cloud-based OIDC providers (like Google, Okta, Auth0) and desktop applications (like a VSCode extension) that need to perform an OAuth2 Authorization Code Flow.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

---

## 🎯 How It Works

The OAuth2 Authorization Code Flow, when initiated from a desktop application, requires a web server to receive the redirect from the authentication provider. This server fulfills that role.

1.  **Initiation**: The VSCode extension generates a `state` parameter and opens a browser window to this server's `/login` endpoint.
2.  **Redirect to Provider**: The server constructs the full authorization URL for the configured OIDC provider and redirects the user's browser to it.
3.  **User Authentication**: The user signs in and grants consent on the provider's platform.
4.  **Callback to Server**: The provider redirects the user back to this server's `/oauth/oidc/callback` endpoint with an authorization `code` and the original `state`.
5.  **Token Exchange**: The server securely exchanges the `code` for an `id_token`, `access_token`, and `refresh_token` by making a direct, server-to-server request to the provider's token endpoint.
6.  **Token Validation**: The server validates the received `id_token` to ensure it is authentic and has not been tampered with.
7.  **Redirect to Application**: The server redirects the browser one last time to a custom URI scheme (e.g., `vscode://...`), passing all tokens and the `state` parameter back to the VSCode extension.
8.  **Completion**: The VSCode extension receives the tokens, validates the `state`, and completes the login process.

## ✨ Features

- **OIDC Compliant**: Works with any OpenID Connect provider (Google, Okta, Auth0, etc.).
- **Dynamic Configuration**: Fetches provider endpoints from the `.well-known/openid-configuration` discovery document on startup.
- **Secure**: Validates JWT signatures, audience, and issuer. Uses `state` parameter to prevent CSRF.
- **Containerized**: Comes with a multi-stage `Dockerfile` for building a small and secure production image.
- **Flexible Deployment**: Can be deployed to cloud platforms (like Railway) or as a standalone server with custom SSL.
- **Environment-Driven Configuration**: All settings are controlled via environment variables.

## 🔧 Configuration

Configuration is managed entirely through environment variables. Create a `.env` file for local development (you can copy `.env.example`).

| Variable              | Description                                                                                                | Default Value                  |
| --------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `OIDC_PROVIDER_URL`   | The base URL of the OIDC provider.                                                                         | `https://accounts.google.com`  |
| `CLIENT_ID`           | The OAuth2 Client ID for your application.                                                                 | **(Required)**                 |
| `CLIENT_SECRET`       | The OAuth2 Client Secret for your application.                                                             | **(Required)**                 |
| `APP_BASE_URL`        | The public URL of this server. For Railway, this is your `*.up.railway.app` URL.                           | `http://localhost:8000`        |
| `VSCODE_EXTENSION_ID` | The unique ID of your VSCode extension (e.g., `your-publisher.your-extension`).                            | `saoudrizwan.claude-dev`       |
| `HOST`                | The host address for the server to bind to.                                                                | `0.0.0.0`                      |
| `PORT`                | The port for the server to listen on.                                                                      | `8000`                         |
| `SSL_KEYFILE`         | (Optional) Path to the SSL private key file for standalone HTTPS mode.                                     | `""`                           |
| `SSL_CERTFILE`        | (Optional) Path to the SSL certificate file for standalone HTTPS mode.                                     | `""`                           |

## 🚀 Running the Server

### Local Development (HTTP)

This is the easiest way to run the server locally.

1.  **Install Dependencies**: `pip install -r requirements.txt`
2.  **Configure**: Create a `.env` file and fill in your `CLIENT_ID` and `CLIENT_SECRET`.
3.  **Run**: `python run_dev.py`

The server will be available at `http://localhost:8000`.

### Docker

Build and run the application in a container.

1.  **Build the image**:
    ```bash
    docker build -t oidc-callback-server .
    ```
2.  **Run the container**:
    ```bash
    docker run -p 8000:8000 --env-file .env oidc-callback-server
    ```

## ☁️ Deployment

### Deploying to Railway

Railway can deploy this application using the provided `Dockerfile`.

1.  **Push to GitHub**: Ensure your repository is on GitHub.
2.  **Create a New Railway Project**: Connect it to your GitHub repository.
3.  **Configure Build**: In your service settings under the "Build" tab, select **`Dockerfile`** as the build method.
4.  **Add Environment Variables**: In the "Variables" tab, add all the required variables from the configuration table above. **Crucially, set `APP_BASE_URL` to your public Railway URL** (e.g., `https://my-app-name.up.railway.app`).
5.  **Deploy**: Railway will automatically build the Docker image and deploy it.

### Standalone Deployment (with Custom SSL)

To run this server on your own infrastructure with your own SSL certificates:

1.  **Place SSL Files**: Put your private key and certificate on the server.
2.  **Set Environment Variables**: Configure all the required variables, and additionally set:
    - `SSL_KEYFILE=/path/to/your/private.key`
    - `SSL_CERTFILE=/path/to/your/certificate.crt`
3.  **Run**: Execute `python run_prod.py` or use the Docker container. The server will automatically detect the SSL settings and start in HTTPS mode.

## 🤝 Integration with Your VSCode Extension

1.  **Set Redirect URI**: In your Google Cloud Console (or other provider), set the **Authorized redirect URI** to: `YOUR_APP_BASE_URL/oauth/oidc/callback`.
2.  **Initiate Login**: In your extension, generate a `state` string and open the following URL:
    `YOUR_APP_BASE_URL/login?state=YOUR_UNIQUE_STATE`
3.  **Handle Callback**: Register a `UriHandler` in your extension for the scheme `vscode://YOUR_VSCODE_EXTENSION_ID/`. It will receive the final redirect containing the tokens.
