# DECOYABLE - Security Audit Report
**Date:** April 2, 2026  
**Auditor:** GitHub Copilot Security Analysis  
**Severity Levels:** 🔴 Critical | 🟠 High | 🟡 Medium | 🔵 Low

---

## Executive Summary

This comprehensive security audit identified **24 security vulnerabilities** across the DECOYABLE application. The most critical issues include:
- **Missing authentication/authorization** on all API endpoints
- **CORS misconfiguration** allowing any origin
- **No input validation** leading to path traversal
- **Missing rate limiting** enabling DoS attacks
- **Insecure secret management** with hardcoded defaults
- **SQL injection vulnerabilities** in test files
- **Missing security headers** (HSTS, CSP, X-Frame-Options)
- **Subprocess execution** with potential command injection risks

---

## Critical Vulnerabilities (🔴)

### 1. Missing Authentication & Authorization on All API Endpoints
**File:** `decoyable/api/routers/scanning.py`, `decoyable/api/routers/attacks.py`, `decoyable/api/honeypot_router.py`  
**Severity:** 🔴 CRITICAL  
**CWE:** CWE-306 (Missing Authentication for Critical Function)

**Description:**  
All API endpoints are publicly accessible without any authentication. Anyone can:
- Execute security scans (`/api/v1/scan/*`)
- Access attack logs (`/api/v1/attacks`)
- Block IPs (`/decoy/block/{ip}`)
- Retrieve sensitive metrics

**Impact:**
- Unauthorized access to sensitive security data
- Resource exhaustion through unlimited scans
- Data exfiltration
- DoS attacks

**Proof of Concept:**
```bash
curl -X POST http://localhost:8000/api/v1/scan/all \
  -H "Content-Type: application/json" \
  -d '{"path": "/etc/passwd"}'
```

**Recommendation:**
- Implement OAuth2/JWT authentication
- Add API key validation
- Implement role-based access control (RBAC)

---

### 2. CORS Misconfiguration - Wildcard Origin
**File:** `decoyable/api/service.py:82`  
**Severity:** 🔴 CRITICAL  
**CWE:** CWE-942 (Permissive Cross-domain Policy)

**Description:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔴 CRITICAL: Allows ANY origin!
    allow_credentials=True,
)
```

**Impact:**
- Cross-Site Request Forgery (CSRF) attacks
- Credential theft
- Session hijacking

**Recommendation:**
```python
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

---

### 3. Missing Rate Limiting on All Endpoints
**File:** All API routers  
**Severity:** 🔴 CRITICAL  
**CWE:** CWE-770 (Allocation of Resources Without Limits)

**Description:**  
No rate limiting implemented on any endpoint. Attackers can:
- Spam scan requests causing resource exhaustion
- Brute force attacks
- DDoS the application

**Proof of Concept:**
```bash
for i in {1..10000}; do
  curl -X POST http://localhost:8000/api/v1/scan/all \
    -H "Content-Type: application/json" \
    -d '{"path": "/tmp"}' &
done
```

**Recommendation:**
- Implement slowapi or fastapi-limiter
- Set limits: 10 requests/minute per IP for scan endpoints
- Set limits: 100 requests/minute per IP for read endpoints

---

### 4. Path Traversal Vulnerability in Scan Endpoints
**File:** `decoyable/api/routers/scanning.py:21`  
**Severity:** 🔴 CRITICAL  
**CWE:** CWE-22 (Path Traversal)

**Description:**
```python
class ScanRequest(BaseModel):
    path: str = Field(..., min_length=1, max_length=4096)
```

No validation that the path is within allowed directories. Attackers can scan:
- `/etc/passwd`
- `/root/.ssh/`
- System configuration files

**Proof of Concept:**
```bash
curl -X POST http://localhost:8000/api/v1/scan/secrets \
  -H "Content-Type: application/json" \
  -d '{"path": "/etc/shadow"}'
```

**Recommendation:**
```python
import os
from pathlib import Path

def validate_scan_path(path: str) -> Path:
    # Resolve path and check if it's within allowed directories
    resolved = Path(path).resolve()
    allowed_dirs = [Path("/app"), Path("/workspace")]
    
    if not any(str(resolved).startswith(str(d)) for d in allowed_dirs):
        raise ValueError("Path outside allowed directories")
    
    return resolved
```

---

### 5. Hardcoded Secret Keys in Configuration
**File:** `decoyable/core/config.py:97-99`  
**Severity:** 🔴 CRITICAL  
**CWE:** CWE-798 (Hardcoded Credentials)

**Description:**
```python
secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
jwt_secret_key: str = Field(default="jwt-secret-key", env="JWT_SECRET_KEY")
```

**Impact:**
- If deployed without changing defaults, attackers can:
  - Forge JWT tokens
  - Decrypt session data
  - Bypass authentication

**Recommendation:**
```python
secret_key: str = Field(..., env="SECRET_KEY")  # No default, must be set
jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")

@validator('secret_key', 'jwt_secret_key')
def validate_secret_not_default(cls, v):
    if v in ["dev-secret-key-change-in-production", "jwt-secret-key"]:
        raise ValueError("Must not use default secret key in production")
    if len(v) < 32:
        raise ValueError("Secret key must be at least 32 characters")
    return v
```

---

### 6. SQL Injection Vulnerabilities in Test Files
**File:** `support/debug_patterns.py:11`, multiple test files  
**Severity:** 🔴 CRITICAL  
**CWE:** CWE-89 (SQL Injection)

**Description:**
```python
query = "SELECT * FROM users WHERE id = " + user_id  # Vulnerable
```

While these are in test files, they could be copied by developers into production code.

**Recommendation:**
- Use parameterized queries
- Add linter rules to prevent SQL injection patterns
- Update all examples to use safe practices

---

## High Severity Vulnerabilities (🟠)

### 7. Missing CSRF Protection
**File:** API middleware configuration  
**Severity:** 🟠 HIGH  
**CWE:** CWE-352 (Cross-Site Request Forgery)

**Description:**  
No CSRF tokens implemented. Combined with CORS misconfiguration, allows CSRF attacks.

**Recommendation:**
- Implement CSRF tokens for state-changing operations
- Use SameSite cookie attribute
- Add CSRF middleware

---

### 8. Missing Security Headers
**File:** `decoyable/api/service.py`  
**Severity:** 🟠 HIGH  
**CWE:** CWE-693 (Protection Mechanism Failure)

**Missing Headers:**
- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy`
- `X-XSS-Protection`
- `Permissions-Policy`

**Recommendation:**
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response
```

---

### 9. Sensitive Error Information Disclosure
**File:** Multiple API endpoints  
**Severity:** 🟠 HIGH  
**CWE:** CWE-209 (Information Exposure Through Error Message)

**Description:**
```python
raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
```

Full exception details exposed to users, revealing internal structure.

**Recommendation:**
- Log detailed errors server-side
- Return generic error messages to clients
- Implement custom exception handlers

---

### 10. Missing Input Size Validation
**File:** `decoyable/api/routers/scanning.py`  
**Severity:** 🟠 HIGH  
**CWE:** CWE-400 (Uncontrolled Resource Consumption)

**Description:**  
No limits on request body size or file upload sizes.

**Recommendation:**
```python
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(
    RequestValidationMiddleware,
    max_body_size=10 * 1024 * 1024  # 10MB
)
```

---

### 11. Insecure Docker Configuration
**File:** `Dockerfile:43`, `docker-compose.yml`  
**Severity:** 🟠 HIGH  
**CWE:** CWE-732 (Incorrect Permission Assignment)

**Issues:**
- User created but potentially running with elevated privileges in some contexts
- Exposed ports without network isolation
- Secrets in environment variables (better than hardcoded, but not ideal)

**Recommendation:**
- Use Docker secrets properly
- Implement network segmentation
- Run with minimum required capabilities
- Use read-only filesystems where possible

---

### 12. Subprocess Execution with Command Injection Risk
**File:** `decoyable/defense/honeypot.py:82-97`  
**Severity:** 🟠 HIGH  
**CWE:** CWE-78 (OS Command Injection)

**Description:**
While IP address is validated, subprocess execution should still be minimized:
```python
proc = await asyncio.create_subprocess_exec(
    "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP",
    ...
)
```

**Recommendation:**
- Use Python libraries (python-iptables) instead of subprocess
- Implement strict input validation
- Use whitelisting for allowed commands
- Log all subprocess executions

---

## Medium Severity Vulnerabilities (🟡)

### 13. Missing Request Logging for Security Events
**File:** API endpoints  
**Severity:** 🟡 MEDIUM  
**CWE:** CWE-778 (Insufficient Logging)

**Recommendation:**
- Log all authentication attempts
- Log all authorization failures
- Log all scan operations with user/IP
- Implement audit trail

---

### 14. No Session Timeout Configuration
**File:** Authentication (when implemented)  
**Severity:** 🟡 MEDIUM  
**CWE:** CWE-613 (Insufficient Session Expiration)

**Recommendation:**
- Implement JWT token expiration (1 hour)
- Implement refresh token rotation
- Force re-authentication for sensitive operations

---

### 15. Trusted Host Middleware Misconfigured
**File:** `decoyable/api/service.py:89`  
**Severity:** 🟡 MEDIUM

**Description:**
```python
TrustedHostMiddleware,
allowed_hosts=["*"],  # 🟡 Should be restricted
```

**Recommendation:**
```python
allowed_hosts=["yourdomain.com", "api.yourdomain.com"]
```

---

### 16. Missing Database Connection Encryption
**File:** `docker-compose.yml:18`  
**Severity:** 🟡 MEDIUM  
**CWE:** CWE-319 (Cleartext Transmission of Sensitive Information)

**Description:**
```yaml
DATABASE_URL=postgresql://user:password@db:5432/app
```

No SSL/TLS enforcement for PostgreSQL connections.

**Recommendation:**
```yaml
DATABASE_URL=postgresql://user:password@db:5432/app?sslmode=require
```

---

### 17. Redis Password in Command Line
**File:** `docker-compose.yml:75`  
**Severity:** 🟡 MEDIUM  
**CWE:** CWE-214 (Information Exposure Through Process Environment)

**Description:**
```yaml
command: ["redis-server", "--requirepass", "$REDIS_PASSWORD"]
```

Password visible in `docker ps` and process list.

**Recommendation:**
- Use Redis ACL configuration file
- Mount config file as secret
- Use environment variable in config, not command line

---

### 18. Weak Database Password Defaults
**File:** `docker-compose.yml:52`  
**Severity:** 🟡 MEDIUM

**Description:**
```yaml
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}  # Weak default
```

**Recommendation:**
- No defaults for production
- Enforce strong password policy
- Use secret management service

---

### 19. Missing Content-Type Validation
**File:** API endpoints  
**Severity:** 🟡 MEDIUM  
**CWE:** CWE-20 (Improper Input Validation)

**Recommendation:**
```python
@app.middleware("http")
async def validate_content_type(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        if request.headers.get("content-type") != "application/json":
            return JSONResponse(
                status_code=415,
                content={"detail": "Content-Type must be application/json"}
            )
    return await call_next(request)
```

---

### 20. No Health Check Authentication
**File:** `decoyable/api/routers/health.py`  
**Severity:** 🟡 MEDIUM

**Description:**  
Health endpoints expose internal system information without authentication.

**Recommendation:**
- Require authentication for `/health` endpoint
- Keep `/health/live` public for load balancer
- Add `/health/ready` with authentication

---

## Low Severity Issues (🔵)

### 21. Missing API Versioning Strategy
**File:** API routes  
**Severity:** 🔵 LOW

**Description:**  
API uses `/api/v1/` but no clear deprecation strategy documented.

**Recommendation:**
- Document API versioning policy
- Implement version deprecation warnings
- Support multiple API versions during transition

---

### 22. Debug Mode Can Be Enabled in Production
**File:** `decoyable/core/config.py:96`  
**Severity:** 🔵 LOW

**Description:**
```python
debug: bool = Field(default=False, env="API_DEBUG")
```

Should enforce debug=False in production.

**Recommendation:**
```python
@validator('debug')
def validate_no_debug_in_production(cls, v, values):
    if v and values.get('environment') == 'production':
        raise ValueError("Debug mode not allowed in production")
    return v
```

---

### 23. Missing Response Compression
**File:** API middleware  
**Severity:** 🔵 LOW

**Recommendation:**
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

### 24. No API Documentation Authentication
**File:** `decoyable/api/service.py:68`  
**Severity:** 🔵 LOW

**Description:**  
Swagger UI (`/docs`) and ReDoc (`/redoc`) are publicly accessible.

**Recommendation:**
- Require authentication for API documentation in production
- Or disable in production, serve separately

---

## Summary Statistics

| Severity | Count | Fixed |
|----------|-------|-------|
| 🔴 Critical | 6 | 0 |
| 🟠 High | 6 | 0 |
| 🟡 Medium | 8 | 0 |
| 🔵 Low | 4 | 0 |
| **Total** | **24** | **0** |

---

## Compliance Impact

### OWASP Top 10 2021 Violations:
1. **A01:2021 – Broken Access Control** (Issues #1, #4, #7)
2. **A02:2021 – Cryptographic Failures** (Issues #5, #16)
3. **A03:2021 – Injection** (Issue #6)
4. **A05:2021 – Security Misconfiguration** (Issues #2, #8, #11, #15, #22)
5. **A07:2021 – Identification and Authentication Failures** (Issues #1, #14)
6. **A09:2021 – Security Logging and Monitoring Failures** (Issue #13)

### Recommended Priority

**Immediate (This Week):**
1. Add authentication/authorization (Issue #1)
2. Fix CORS configuration (Issue #2)
3. Implement rate limiting (Issue #3)
4. Add path validation (Issue #4)
5. Change default secrets (Issue #5)

**Short Term (This Month):**
6. Add security headers (Issue #8)
7. Implement CSRF protection (Issue #7)
8. Fix error disclosure (Issue #9)
9. Add input size limits (Issue #10)
10. Improve Docker security (Issue #11)

**Long Term (This Quarter):**
- All remaining issues
- Security testing automation
- Penetration testing
- Security training for developers

---

## Next Steps

1. ✅ Create GitHub issues for each vulnerability
2. ⬜ Assign severity labels and owners
3. ⬜ Create fix PRs for critical issues
4. ⬜ Update security documentation
5. ⬜ Schedule follow-up security audit
6. ⬜ Implement security testing in CI/CD

---

**Report Generated:** April 2, 2026  
**Tools Used:** Manual code review, static analysis, security best practices  
**Reviewer:** GitHub Copilot Security Analysis
