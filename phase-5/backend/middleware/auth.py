"""JWT authentication middleware for FastAPI."""

import os
from typing import Annotated

import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Load environment variables
load_dotenv()

# Frontend URL where Better Auth is running (for JWKS endpoint)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
JWKS_URL = f"{FRONTEND_URL}/api/auth/jwks"

# HTTP Bearer scheme for extracting token from Authorization header
security = HTTPBearer()

# Cache for JWKS client
_jwks_client = None


def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client for fetching public keys."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(JWKS_URL)
    return _jwks_client


class AuthenticatedUser:
    """Represents an authenticated user extracted from JWT."""

    def __init__(self, user_id: str, email: str | None = None):
        self.user_id = user_id
        self.email = email


def verify_token(token: str) -> dict:
    """
    Verify JWT token using public key from JWKS endpoint.
    Also supports demo tokens for development/testing.

    Args:
        token: JWT token string

    Returns:
        Decoded JWT payload

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    import base64
    import json
    import time

    # Check if this is a demo token (format: demo.{base64_payload}.signature)
    parts = token.split(".")
    if len(parts) == 3 and parts[0] == "demo":
        try:
            # Decode the demo token payload
            payload = json.loads(base64.b64decode(parts[1]))

            # Check expiration
            if payload.get("exp") and payload["exp"] < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload
        except (json.JSONDecodeError, base64.binascii.Error) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid demo token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Otherwise, verify as a real JWT using JWKS
    try:
        # Get the signing key from JWKS
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256", "EdDSA"],
            options={
                "verify_aud": False,
                "verify_iss": False,
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> AuthenticatedUser:
    """
    FastAPI dependency to extract and verify user from JWT token.

    Args:
        credentials: HTTP Bearer credentials extracted by FastAPI

    Returns:
        AuthenticatedUser object with user_id and optional email

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    token = credentials.credentials
    payload = verify_token(token)

    # Extract user_id from payload
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("email")

    return AuthenticatedUser(user_id=str(user_id), email=email)


# Type alias for dependency injection
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
