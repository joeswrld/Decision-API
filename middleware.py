"""
FastAPI middleware for authentication and rate limiting.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from auth import APIKey, api_key_store, verify_api_key_format
from rate_limit import rate_limiter

logger = logging.getLogger(__name__)


class AuthenticationError(HTTPException):
    """Custom exception for authentication failures."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class RateLimitError(HTTPException):
    """Custom exception for rate limit exceeded."""
    def __init__(self, detail: str, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)}
        )


def extract_api_key(request: Request) -> Optional[str]:
    """
    Extract API key from request.
    Supports multiple formats:
    1. Authorization header: Bearer sk_live_xxx
    2. X-API-Key header: sk_live_xxx
    3. Query parameter: ?api_key=sk_live_xxx (not recommended for production)
    """
    # Try Authorization header (preferred)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "").strip()
    
    # Try X-API-Key header
    api_key_header = request.headers.get("X-API-Key")
    if api_key_header:
        return api_key_header.strip()
    
    # Try query parameter (least secure, but convenient for testing)
    api_key_query = request.query_params.get("api_key")
    if api_key_query:
        logger.warning("API key passed in query parameter (insecure)")
        return api_key_query.strip()
    
    return None


async def authenticate_request(request: Request) -> APIKey:
    """
    Authenticate the request using API key.
    
    Raises:
        AuthenticationError: If authentication fails
    
    Returns:
        APIKey: The authenticated API key object
    """
    # Extract API key
    raw_key = extract_api_key(request)
    
    if not raw_key:
        raise AuthenticationError(
            "Missing API key. Provide via 'Authorization: Bearer YOUR_KEY' header."
        )
    
    # Validate format
    if not verify_api_key_format(raw_key):
        raise AuthenticationError(
            "Invalid API key format. Expected: sk_live_xxx or sk_test_xxx"
        )
    
    # Retrieve key from store
    api_key = api_key_store.get_key(raw_key)
    
    if not api_key:
        raise AuthenticationError(
            "Invalid API key. Key not found or has been revoked."
        )
    
    # Check if key is active
    if not api_key.is_active:
        raise AuthenticationError(
            "API key has been deactivated. Contact support or generate a new key."
        )
    
    return api_key


async def check_rate_limits(api_key: APIKey) -> None:
    """
    Check rate limits for the API key.
    
    Raises:
        RateLimitError: If rate limit is exceeded
    """
    allowed, error_message, retry_after = rate_limiter.check_rate_limit(api_key)
    
    if not allowed:
        logger.warning(
            f"Rate limit exceeded for key {api_key.key_hash[:8]}... "
            f"(tier={api_key.tier.value})"
        )
        raise RateLimitError(error_message, retry_after or 60)


async def auth_middleware(request: Request, call_next):
    """
    Middleware to authenticate requests and enforce rate limits.
    
    Workflow:
    1. Check if endpoint requires authentication
    2. Extract and validate API key
    3. Check rate limits
    4. Update usage counters
    5. Add rate limit headers to response
    6. Call next middleware/endpoint
    """
    # Skip authentication for public endpoints
    public_paths = ["/", "/health", "/docs", "/openapi.json", "/redoc"]
    if request.url.path in public_paths:
        return await call_next(request)
    
    try:
        # Authenticate
        api_key = await authenticate_request(request)
        
        # Check rate limits
        await check_rate_limits(api_key)
        
        # Update usage counters
        api_key_store.update_usage(api_key.key_hash)
        
        # Store API key in request state for endpoint access
        request.state.api_key = api_key
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        headers = rate_limiter.get_rate_limit_headers(api_key)
        for key, value in headers.items():
            response.headers[key] = value
        
        return response
        
    except AuthenticationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": "authentication_failed",
                "message": e.detail,
                "docs": "https://docs.yourapi.com/authentication"
            },
            headers=e.headers
        )
    
    except RateLimitError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": "rate_limit_exceeded",
                "message": e.detail,
                "retry_after": e.headers.get("Retry-After"),
                "docs": "https://docs.yourapi.com/rate-limits"
            },
            headers=e.headers
        )
    
    except Exception as e:
        logger.error(f"Unexpected error in auth middleware: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred during authentication"
            }
        )