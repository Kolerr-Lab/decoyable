"""
Rate Limiting Middleware for DECOYABLE API

Provides rate limiting to prevent abuse and DoS attacks.
Uses in-memory storage with Redis backend support.
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional, Tuple

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from decoyable.core.logging import get_logger

logger = get_logger("api.ratelimit")


class RateLimitStore:
    """
    In-memory rate limit store with automatic cleanup.
    
    Stores request counts per IP address with expiration.
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self):
        # Structure: {ip_address: {window_start: request_count}}
        self._store: Dict[str, Dict[float, int]] = defaultdict(dict)
        self._last_cleanup = time.time()
    
    def _cleanup_expired(self, current_time: float, window_seconds: int):
        """Remove expired entries to prevent memory growth."""
        # Only cleanup every minute to reduce overhead
        if current_time - self._last_cleanup < 60:
            return
        
        cutoff_time = current_time - (window_seconds * 2)  # Keep 2 windows worth
        
        for ip in list(self._store.keys()):
            # Remove expired windows for this IP
            expired_windows = [
                window for window in self._store[ip].keys() 
                if window < cutoff_time
            ]
            for window in expired_windows:
                del self._store[ip][window]
            
            # Remove IP if no windows left
            if not self._store[ip]:
                del self._store[ip]
        
        self._last_cleanup = current_time
        logger.debug(f"Cleaned up rate limit store. Active IPs: {len(self._store)}")
    
    def get_request_count(self, ip: str, window_seconds: int) -> Tuple[int, float]:
        """
        Get request count for IP in current window.
        
        Args:
            ip: Client IP address
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (request_count, window_reset_time)
        """
        current_time = time.time()
        window_start = current_time - (current_time % window_seconds)
        
        # Cleanup old entries
        self._cleanup_expired(current_time, window_seconds)
        
        # Get count for current window
        count = self._store.get(ip, {}).get(window_start, 0)
        reset_time = window_start + window_seconds
        
        return count, reset_time
    
    def increment(self, ip: str, window_seconds: int) -> int:
        """
        Increment request count for IP in current window.
        
        Args:
            ip: Client IP address
            window_seconds: Time window in seconds
            
        Returns:
            New request count
        """
        current_time = time.time()
        window_start = current_time - (current_time % window_seconds)
        
        if ip not in self._store:
            self._store[ip] = {}
        
        if window_start not in self._store[ip]:
            self._store[ip][window_start] = 0
        
        self._store[ip][window_start] += 1
        
        return self._store[ip][window_start]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with configurable limits per endpoint.
    
    Features:
    - Per-IP rate limiting
    - Configurable limits per endpoint pattern
    - Automatic cleanup of expired entries
    - Rate limit headers in responses
    """
    
    def __init__(
        self,
        app,
        default_limit: int = 100,
        default_window: int = 60,
        endpoint_limits: Optional[Dict[str, Tuple[int, int]]] = None
    ):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: FastAPI application
            default_limit: Default requests per window (default: 100)
            default_window: Default window in seconds (default: 60)
            endpoint_limits: Dict mapping endpoint patterns to (limit, window) tuples
                Example: {"/api/v1/scan/": (10, 60), "/api/v1/health": (1000, 60)}
        """
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self.endpoint_limits = endpoint_limits or {}
        self.store = RateLimitStore()
        
        logger.info(
            f"Rate limiting initialized: default={default_limit}/{default_window}s, "
            f"custom_endpoints={len(self.endpoint_limits)}"
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, respecting proxy headers."""
        # Check X-Forwarded-For header (from proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # X-Forwarded-For can contain multiple IPs, use the first one
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _get_rate_limit(self, path: str) -> Tuple[int, int]:
        """
        Get rate limit for a specific endpoint.
        
        Args:
            path: Request path
            
        Returns:
            Tuple of (limit, window_seconds)
        """
        # Check for exact match first
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]
        
        # Check for prefix match
        for pattern, (limit, window) in self.endpoint_limits.items():
            if path.startswith(pattern):
                return limit, window
        
        # Return default
        return self.default_limit, self.default_window
    
    def _is_whitelisted(self, path: str) -> bool:
        """Check if path should bypass rate limiting."""
        whitelist = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health/live",  # Kubernetes liveness probe
        ]
        return any(path.startswith(p) for p in whitelist)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        path = request.url.path
        
        # Skip rate limiting for whitelisted paths
        if self._is_whitelisted(path):
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Get rate limit for this endpoint
        limit, window = self._get_rate_limit(path)
        
        # Check current request count
        current_count, reset_time = self.store.get_request_count(client_ip, window)
        
        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, limit - current_count - 1)),
            "X-RateLimit-Reset": str(int(reset_time)),
            "X-RateLimit-Window": str(window),
        }
        
        # Check if rate limit exceeded
        if current_count >= limit:
            retry_after = int(reset_time - time.time())
            headers["Retry-After"] = str(retry_after)
            
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {path}: "
                f"{current_count}/{limit} in {window}s window"
            )
            
            return Response(
                content='{"detail":"Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers=headers,
                media_type="application/json"
            )
        
        # Increment counter
        new_count = self.store.increment(client_ip, window)
        headers["X-RateLimit-Remaining"] = str(max(0, limit - new_count))
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header, value in headers.items():
            response.headers[header] = value
        
        return response


def create_rate_limit_middleware(
    default_limit: int = 100,
    default_window: int = 60
) -> RateLimitMiddleware:
    """
    Factory function to create rate limiting middleware with DECOYABLE defaults.
    
    Args:
        default_limit: Default requests per window
        default_window: Default window in seconds
        
    Returns:
        Configured RateLimitMiddleware
    """
    # Define custom limits for different endpoint patterns
    endpoint_limits = {
        # Security scanning endpoints - strict limits
        "/api/v1/scan/": (10, 60),  # 10 requests per minute
        "/api/v1/scan/all": (5, 60),  # 5 comprehensive scans per minute
        
        # Attack endpoints - moderate limits
        "/api/v1/attacks": (30, 60),  # 30 requests per minute
        
        # Health checks - generous limits
        "/api/v1/health": (1000, 60),  # 1000 requests per minute
        "/health": (1000, 60),
        
        # Honeypot endpoints - moderate limits
        "/decoy/": (50, 60),  # 50 requests per minute
        
        # Metrics - moderate limits
        "/api/v1/metrics": (100, 60),  # 100 requests per minute
    }
    
    return lambda app: RateLimitMiddleware(
        app,
        default_limit=default_limit,
        default_window=default_window,
        endpoint_limits=endpoint_limits
    )
