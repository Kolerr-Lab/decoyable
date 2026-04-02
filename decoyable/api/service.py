"""
API service layer with dependency injection and clean architecture.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from decoyable.core.config import Settings
from decoyable.core.logging import LoggingService, get_logger
from decoyable.core.registry import ServiceRegistry, get_service_registry
from decoyable.api.ratelimit import create_rate_limit_middleware


class APIService:
    """API service that manages FastAPI application lifecycle and dependencies."""

    def __init__(self, config: Settings, registry: ServiceRegistry, logging_service: LoggingService):
        self.config = config
        self.registry = registry
        self.logging_service = logging_service
        self.logger = get_logger("api.service")
        self.app: Optional[FastAPI] = None

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan context manager."""
        # Startup
        self.logger.info("Starting DECOYABLE API service")
        await self._startup()
        yield
        # Shutdown
        self.logger.info("Shutting down DECOYABLE API service")
        await self._shutdown()

    async def _startup(self) -> None:
        """Initialize services on startup."""
        # Register API service in both registries
        self.registry.register_instance("api", self)
        global_registry = get_service_registry()
        global_registry.register_instance("config", self.config)
        global_registry.register_instance("logging", self.logging_service)
        global_registry.register_instance("api", self)

        # Initialize database connections, caches, etc.
        self.logger.info("API service startup complete")

    async def _shutdown(self) -> None:
        """Cleanup services on shutdown."""
        # Close connections, cleanup resources
        self.logger.info("API service shutdown complete")

    def create_application(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        app = FastAPI(
            title="DECOYABLE API",
            description=self._get_api_description(),
            version=self.config.version,
            lifespan=self.lifespan,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            openapi_tags=self._get_openapi_tags(),
        )

        # Add middleware
        self._add_middleware(app)

        # Register routers
        self._register_routers(app)

        self.app = app
        return app

    def _add_middleware(self, app: FastAPI) -> None:
        """Add middleware to the FastAPI application."""
        # Security headers middleware (add first to apply to all responses)
        @app.middleware("http")
        async def add_security_headers(request, call_next):
            response = await call_next(request)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            return response

        # CORS middleware - FIXED: Only allow specific origins in production
        import os
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
        if self.config.environment == "production":
            # In production, only allow explicitly configured origins
            allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
        else:
            # In development, allow localhost variants
            allowed_origins = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"]
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "X-API-Key"],
            max_age=3600,
        )

        # Trusted host middleware - FIXED: Only allow specific hosts
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
        if self.config.environment != "production":
            allowed_hosts.append("*")  # Only allow wildcard in development
        
        app.add_middleware(
            TrustedHostMiddleware,
         
        
        # Rate limiting middleware - ADDED for DoS protection
        rate_limit_factory = create_rate_limit_middleware(
            default_limit=100,  # 100 requests per minute by default
            default_window=60   # 60 second window
        )
        app.add_middleware(rate_limit_factory(app).__class__, app=app)   allowed_hosts=[host.strip() for host in allowed_hosts],
        )

    def _register_routers(self, app: FastAPI) -> None:
        """Register API routers."""
        # Import routers here to avoid circular imports
        from .honeypot_router import router as honeypot_router
        from .routers.attacks import router as attacks_router
        from .routers.health import router as health_router
        from .routers.metrics import router as metrics_router
        from .routers.scanning import router as scanning_router
        from decoyable.defense.analysis import router as analysis_router

        # Register routers with prefixes
        app.include_router(health_router, prefix="/api/v1", tags=["health"])
        app.include_router(scanning_router, prefix="/api/v1", tags=["scanning"])
        app.include_router(metrics_router, prefix="/api/v1", tags=["metrics"])
        app.include_router(attacks_router, prefix="/api/v1", tags=["attacks"])
        app.include_router(analysis_router, tags=["analysis"])
        app.include_router(honeypot_router, tags=["honeypot"])

    def _get_api_description(self) -> str:
        """Get the API description."""
        return """
        # DECOYABLE - Enterprise Cybersecurity Scanning Platform

        DECOYABLE is an AI-powered cybersecurity scanning platform that combines traditional security tools with advanced machine learning to provide comprehensive threat detection and analysis.

        ## Features

        * **Multi-Modal Scanning**: Secrets, dependencies, vulnerabilities, and behavioral analysis
        * **AI-Powered Analysis**: LLM integration for intelligent threat assessment
        * **Honeypot Technology**: Active defense mechanisms
        * **Enterprise Ready**: Scalable, secure, and compliant
        * **Developer Friendly**: Easy integration with CI/CD pipelines

        ## Authentication

        Some endpoints require authentication. Use API keys or OAuth2 tokens as specified in endpoint documentation.

        ## Rate Limiting

        API requests are rate-limited. Check the `X-RateLimit-*` headers in responses.

        ## Support

        - Documentation: [GitHub Repository](https://github.com/Kolerr-Lab/supper-decoyable)
        - Issues: [GitHub Issues](https://github.com/Kolerr-Lab/supper-decoyable/issues)
        - Security: [Security Policy](https://github.com/Kolerr-Lab/supper-decoyable/security/policy)
        """

    def _get_openapi_tags(self) -> list:
        """Get OpenAPI tags for documentation."""
        return [
            {
                "name": "health",
                "description": "Health check and monitoring endpoints",
            },
            {
                "name": "scanning",
                "description": "Security scanning operations",
            },
            {
                "name": "analysis",
                "description": "Threat analysis and intelligence",
            },
            {
                "name": "honeypot",
                "description": "Honeypot management and active defense",
            },
            {
                "name": "metrics",
                "description": "Prometheus metrics and monitoring",
            },
            {
                "name": "attacks",
                "description": "Attack event monitoring and management",
            },
        ]


def create_api_app(config: Settings, registry: ServiceRegistry, logging_service: LoggingService) -> FastAPI:
    """Factory function to create the API application."""
    api_service = APIService(config, registry, logging_service)
    return api_service.create_application()
