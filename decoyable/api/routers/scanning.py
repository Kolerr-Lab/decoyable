"""
Scanning router for security scanning operations.
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field, validator

from decoyable.core.logging import get_logger
from decoyable.core.registry import get_service_registry
from decoyable.scanners.service import ScannerService

router = APIRouter()
logger = get_logger("api.scanning")


def validate_scan_path(path: str) -> Path:
    """
    Validate and sanitize scan path to prevent path traversal attacks.
    
    Args:
        path: The path to validate
        
    Returns:
        Resolved Path object
        
    Raises:
        ValueError: If path is invalid or outside allowed directories
    """
    try:
        # Resolve the path to absolute path
        resolved_path = Path(path).resolve()
        
        # Get allowed directories from environment or use defaults
        allowed_dirs_str = os.getenv("ALLOWED_SCAN_DIRS", "/app,/workspace,/tmp")
        allowed_dirs = [Path(d.strip()).resolve() for d in allowed_dirs_str.split(",") if d.strip()]
        
        # Add current working directory in development
        if os.getenv("APP_ENV", "development") == "development":
            allowed_dirs.append(Path.cwd())
        
        # Check if resolved path starts with any allowed directory
        is_allowed = any(
            str(resolved_path).startswith(str(allowed_dir)) 
            for allowed_dir in allowed_dirs
        )
        
        if not is_allowed:
            raise ValueError(
                f"Path {path} is outside allowed directories. "
                f"Allowed: {', '.join(str(d) for d in allowed_dirs)}"
            )
        
        # Check if path exists
        if not resolved_path.exists():
            raise ValueError(f"Path {path} does not exist")
        
        # Additional security: Check for symbolic links that might escape allowed dirs
        if resolved_path.is_symlink():
            raise ValueError("Symbolic links are not allowed for security reasons")
        
        return resolved_path
        
    except Exception as e:
        logger.error(f"Path validation failed for {path}: {e}")
        raise ValueError(f"Invalid scan path: {str(e)}")


class ScanRequest(BaseModel):
    """Request model for scan endpoints."""

    path: str = Field(
        ..., 
        min_length=1, 
        max_length=4096, 
        description="Path to scan (must be within allowed directories)"
    )
    scan_types: Optional[list[str]] = Field(
        None, 
        description="Types of scans to perform"
    )
    async_scan: bool = Field(
        False, 
        description="Whether to perform scan asynchronously"
    )

    @validator('path')
    def validate_path_security(cls, v):
        """Validate path for security before processing."""
        # Basic validation - full validation happens in validate_scan_path()
        if '..' in v:
            raise ValueError("Path cannot contain '..' for security reasons")
        if v.startswith('/etc') or v.startswith('/root') or v.startswith('/sys'):
            raise ValueError("Scanning system directories is not allowed")
        return v

    @validator('scan_types')
    def validate_scan_types(cls, v):
        """Validate scan types are supported."""
        if v is not None:
            allowed_types = ['secrets', 'dependencies', 'sast']
            for scan_type in v:
                if scan_type not in allowed_types:
                    raise ValueError(f"Invalid scan type: {scan_type}. Allowed: {allowed_types}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "path": "/workspace/myproject", 
                "scan_types": ["secrets", "dependencies", "sast"], 
                "async_scan": False
            }
        }


class ScanResponse(BaseModel):
    """Response model for scan operations."""

    status: str
    scan_id: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    scan_duration: Optional[float] = None


def get_scanner_service() -> ScannerService:
    """Dependency injection for scanner service."""
    try:
        registry = get_service_registry()
        config = registry.get_by_name("config")
        logging_service = registry.get_by_name("logging")
        return ScannerService(config, logging_service)
    except Exception as e:
        logger.error(f"Failed to get scanner service: {e}")
        raise HTTPException(status_code=500, detail="Scanner service unavailable")


@router.post("/scan/secrets", summary="Scan for exposed secrets", response_model=ScanResponse)
async def scan_secrets(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    scanner_service: ScannerService = Depends(get_scanner_service),
) -> ScanResponse:
    """
    Scan a directory for exposed secrets and sensitive information.

    Performs comprehensive secret detection including:
    - API keys and tokens
    - Database credentials
    - Private keys and certificates
    - Cloud service credentials
    - Authentication tokens
    """
    start_time = time.time()

    try:
        if request.async_scan:
            # Async processing
            background_tasks.add_task(_perform_secrets_scan_async, request.path, scanner_service)
            return ScanResponse(
                status="accepted", message="Scan started asynchronously", scan_id=f"secrets_{int(time.time())}"
            )

        # Synchronous processing
        report = await scanner_service.scan_secrets(request.path)
        scan_duration = time.time() - start_time

        return ScanResponse(
            status="success",
            results={
                "findings": [finding.__dict__ for finding in report.results],
                "count": len(report.results),
                "summary": report.summary.__dict__,
            },
            scan_duration=scan_duration,
        )

    except Exception as e:
        logger.error(f"Error scanning for secrets: {e}")
        scan_duration = time.time() - start_time
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/scan/dependencies", summary="Scan for dependency issues", response_model=ScanResponse)
async def scan_dependencies(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    scanner_service: ScannerService = Depends(get_scanner_service),
) -> ScanResponse:
    """Scan a project for dependency issues and missing imports."""
    start_time = time.time()

    try:
        if request.async_scan:
            background_tasks.add_task(_perform_deps_scan_async, request.path, scanner_service)
            return ScanResponse(
                status="accepted", message="Dependency scan started asynchronously", scan_id=f"deps_{int(time.time())}"
            )

        report = await scanner_service.scan_dependencies(request.path)
        scan_duration = time.time() - start_time

        return ScanResponse(
            status="success",
            results={
                "issues": [issue.__dict__ for issue in report.results],
                "count": len(report.results),
                "summary": report.summary.__dict__,
            },
            scan_duration=scan_duration,
        )

    except Exception as e:
        logger.error(f"Error scanning dependencies: {e}")
        raise HTTPException(status_code=500, detail=f"Dependency scan failed: {str(e)}")


@router.post("/scan/sast", summary="Scan for security vulnerabilities", response_model=ScanResponse)
async def scan_sast(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    scanner_service: ScannerService = Depends(get_scanner_service),
) -> ScanResponse:
    """Perform Static Application Security Testing (SAST)."""
    start_time = time.time()

    try:
        if request.async_scan:
            background_tasks.add_task(_perform_sast_scan_async, request.path, scanner_service)
            return ScanResponse(
                status="accepted", message="SAST scan started asynchronously", scan_id=f"sast_{int(time.time())}"
            )

        report = await scanner_service.scan_sast(request.path)
        scan_duration = time.time() - start_time

        return ScanResponse(
            status="success",
            results={
                "vulnerabilities": [vuln.__dict__ for vuln in report.results],
                "count": len(report.results),
                "summary": report.summary.__dict__,
            },
            scan_duration=scan_duration,
        )

    except Exception as e:
        logger.error(f"Error performing SAST scan: {e}")
        raise HTTPException(status_code=500, detail=f"SAST scan failed: {str(e)}")


@router.post("/scan/all", summary="Comprehensive security scan", response_model=ScanResponse)
async def scan_all(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    scanner_service: ScannerService = Depends(get_scanner_service),
) -> ScanResponse:
    """Perform comprehensive security scanning (secrets, dependencies, SAST)."""
    start_time = time.time()

    try:
        if request.async_scan:
            background_tasks.add_task(_perform_comprehensive_scan_async, request.path, scanner_service)
            return ScanResponse(
                status="accepted",
                message="Comprehensive scan started asynchronously",
                scan_id=f"comprehensive_{int(time.time())}",
            )

        # Run all scans concurrently
        scan_types = request.scan_types or ["secrets", "dependencies", "sast"]
        scan_tasks = {}

        if "secrets" in scan_types:
            scan_tasks["secrets"] = scanner_service.scan_secrets(request.path)
        if "dependencies" in scan_types:
            scan_tasks["dependencies"] = scanner_service.scan_dependencies(request.path)
        if "sast" in scan_types:
            scan_tasks["sast"] = scanner_service.scan_sast(request.path)

        # Wait for all scans to complete
        results = {}
        for scan_type, task in scan_tasks.items():
            report = await task
            results[scan_type] = {
                "findings": [finding.__dict__ for finding in report.results],
                "count": len(report.results),
                "summary": report.summary.__dict__,
            }

        scan_duration = time.time() - start_time
        total_issues = sum(result["count"] for result in results.values())

        return ScanResponse(
            status="success",
            results=results,
            message=f"Comprehensive scan completed: {total_issues} total issues found",
            scan_duration=scan_duration,
        )

    except Exception as e:
        logger.error(f"Error performing comprehensive scan: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive scan failed: {str(e)}")


# Background task functions
async def _perform_secrets_scan_async(path: str, scanner_service: ScannerService) -> None:
    """Background task for secrets scanning."""
    try:
        report = await scanner_service.scan_secrets(path)
        logger.info(f"Async secrets scan completed for {path}: {len(report.results)} findings")
    except Exception as e:
        logger.error(f"Async secrets scan failed for {path}: {e}")


async def _perform_deps_scan_async(path: str, scanner_service: ScannerService) -> None:
    """Background task for dependency scanning."""
    try:
        report = await scanner_service.scan_dependencies(path)
        logger.info(f"Async dependency scan completed for {path}: {len(report.results)} issues")
    except Exception as e:
        logger.error(f"Async dependency scan failed for {path}: {e}")


async def _perform_sast_scan_async(path: str, scanner_service: ScannerService) -> None:
    """Background task for SAST scanning."""
    try:
        report = await scanner_service.scan_sast(path)
        logger.info(f"Async SAST scan completed for {path}: {len(report.results)} vulnerabilities")
    except Exception as e:
        logger.error(f"Async SAST scan failed for {path}: {e}")


async def _perform_comprehensive_scan_async(path: str, scanner_service: ScannerService) -> None:
    """Background task for comprehensive scanning."""
    try:
        results = await scanner_service.scan_all(path)
        total_issues = sum(len(report.results) for report in results.values())
        logger.info(f"Async comprehensive scan completed for {path}: {total_issues} total issues")
    except Exception as e:
        logger.error(f"Async comprehensive scan failed for {path}: {e}")
