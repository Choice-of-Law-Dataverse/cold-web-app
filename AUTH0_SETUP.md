# Auth0 Integration Guide

This guide explains how to configure Auth0 for the CoLD web application.

## Overview

The CoLD web application now supports Auth0 authentication for both the backend and frontend. This integration:

- Allows users to log in via Auth0 on the frontend
- Passes user tokens to the backend for API authentication
- Maintains backward compatibility with legacy JWT tokens
- Automatically falls back to the backend token if the user is not logged in

## Backend Configuration

### 1. Install Dependencies

The backend requires `python-jose[cryptography]` for Auth0 JWT verification. This has been added to `pyproject.toml`.

If using `uv`:
```bash
cd backend
uv sync
```

If using `pip`:
```bash
cd backend
pip install python-jose[cryptography]
```

### 2. Configure Environment Variables

Add the following environment variables to your backend `.env` file:

```bash
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=https://your-api-identifier
```

- **AUTH0_DOMAIN**: Your Auth0 tenant domain (e.g., `cold.us.auth0.com`)
- **AUTH0_AUDIENCE**: The API identifier configured in your Auth0 dashboard

### 3. How It Works

The backend authentication (`app/auth.py`) now:

1. **Tries Auth0 verification first** if Auth0 is configured
   - Fetches JWKS from Auth0 (with 1-hour caching)
   - Verifies RS256 tokens from Auth0
   - Validates audience and issuer claims

2. **Falls back to legacy JWT** if Auth0 verification fails
   - Uses HS256 algorithm with `JWT_SECRET`
   - Maintains backward compatibility with existing tokens

3. **Returns 401** if both verifications fail

### 4. Testing

Run the Auth0 integration tests:

```bash
cd backend
pytest tests/test_auth0_integration.py -v
```

## Frontend Configuration

### 1. Install Dependencies

The Auth0 Nuxt module has been installed:

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Add the following environment variables to your frontend `.env` file:

```bash
# Auth0 Configuration
AUTH0_SECRET=use-a-long-random-string-at-least-32-characters
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-tenant.auth0.com
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_CLIENT_SECRET=your-auth0-client-secret
AUTH0_AUDIENCE=https://your-api-identifier
```

- **AUTH0_SECRET**: A random string for session encryption (at least 32 characters)
- **AUTH0_BASE_URL**: Your application URL (e.g., `http://localhost:3000` for development)
- **AUTH0_ISSUER_BASE_URL**: Your Auth0 tenant URL (e.g., `https://cold.us.auth0.com`)
- **AUTH0_CLIENT_ID**: Your Auth0 application client ID
- **AUTH0_CLIENT_SECRET**: Your Auth0 application client secret
- **AUTH0_AUDIENCE**: The same API identifier used in the backend

### 3. How It Works

#### Login/Logout

The frontend includes an `AuthButton` component that:
- Shows "Login" when the user is not authenticated
- Shows "Logout" when the user is authenticated
- Redirects to `/api/auth/login` for login
- Redirects to `/api/auth/logout` for logout

#### API Proxy

The API proxy (`server/api/proxy/[...].ts`) now:

1. **Checks for user session** using Auth0
2. **Uses user's access token** if they're logged in
3. **Falls back to backend token** if not logged in
4. **Proxies requests** to the backend API with the appropriate token

This ensures that:
- Anonymous requests still work (using the backend token)
- Authenticated user requests use their own token
- The backend can identify and authorize individual users

## Auth0 Setup

### 1. Create Auth0 Account

1. Go to [auth0.com](https://auth0.com) and sign up
2. Create a new tenant (e.g., `cold`)

### 2. Create API

1. Go to Applications → APIs
2. Click "Create API"
3. Name: `CoLD API`
4. Identifier: `https://api.cold.global` (or your API URL)
5. Signing Algorithm: `RS256`

### 3. Create Application

1. Go to Applications → Applications
2. Click "Create Application"
3. Name: `CoLD Web App`
4. Type: `Regular Web Application`
5. Configure settings:
   - **Allowed Callback URLs**: `http://localhost:3000/api/auth/callback`, `https://cold.global/api/auth/callback`
   - **Allowed Logout URLs**: `http://localhost:3000`, `https://cold.global`
   - **Allowed Web Origins**: `http://localhost:3000`, `https://cold.global`

### 4. Get Credentials

From the application settings:
- Copy the **Domain** → Use for `AUTH0_DOMAIN` and `AUTH0_ISSUER_BASE_URL`
- Copy the **Client ID** → Use for `AUTH0_CLIENT_ID`
- Copy the **Client Secret** → Use for `AUTH0_CLIENT_SECRET`

## Testing the Integration

### 1. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

### 3. Test the Flow

1. **Visit the application**: `http://localhost:3000`
2. **Click "Login"**: You should be redirected to Auth0
3. **Sign in/Sign up**: Use Auth0's authentication
4. **Return to app**: You should see "Logout" instead of "Login"
5. **Make API calls**: Your user token should be used automatically

## Backward Compatibility

The implementation maintains full backward compatibility:

- **Existing JWT tokens** continue to work
- **Anonymous requests** use the backend token
- **No breaking changes** to existing API endpoints
- **Gradual migration** path for users

## Security Considerations

1. **Token Validation**: Both Auth0 tokens (RS256) and legacy tokens (HS256) are properly validated
2. **JWKS Caching**: Auth0 JWKS is cached for 1 hour to prevent rate limiting
3. **Error Handling**: Comprehensive error handling for Auth0 service failures
4. **Session Security**: Frontend sessions are encrypted with `AUTH0_SECRET`

## Troubleshooting

### Backend Issues

**"Auth0 configuration missing"**
- Ensure `AUTH0_DOMAIN` and `AUTH0_AUDIENCE` are set in backend `.env`

**"Unable to fetch JWKS from Auth0"**
- Check internet connectivity
- Verify `AUTH0_DOMAIN` is correct
- Check Auth0 service status

### Frontend Issues

**Login redirects to error page**
- Verify all Auth0 environment variables are set
- Check that callback URLs are configured in Auth0
- Ensure `AUTH0_BASE_URL` matches your application URL

**User token not being used**
- Check that Auth0 session is properly configured
- Verify `AUTH0_AUDIENCE` matches between frontend and backend
- Check browser console for session errors

## Additional Resources

- [Auth0 FastAPI Guide](https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/)
- [Auth0 Nuxt Module](https://www.npmjs.com/package/@auth0/auth0-nuxt)
- [Auth0 Documentation](https://auth0.com/docs)
