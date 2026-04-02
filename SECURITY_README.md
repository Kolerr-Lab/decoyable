# 🔒 DECOYABLE Security Update v1.2.2

## 🎯 Quick Start

**TL;DR:** We fixed **24 security vulnerabilities**. Run these commands to get secured:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate secure configuration
python setup_security.py

# 3. Update environment variables
# Edit .env and set your actual domains for ALLOWED_ORIGINS and ALLOWED_HOSTS

# 4. Deploy
docker-compose build
docker-compose up -d

# 5. Test security
python test_security_fixes.py --api-key YOUR_GENERATED_API_KEY
```

---

## 📋 What Was Fixed?

### Critical (🔴) - **6 Issues**
1. ✅ **No Authentication** → Added API Key + JWT authentication
2. ✅ **CORS Wildcard** → Restricted to configured origins only  
3. ✅ **No Rate Limiting** → Added per-IP rate limiting
4. ✅ **Path Traversal** → Added path validation
5. ✅ **Hardcoded Secrets** → Removed defaults, added validation
6. ✅ **Missing Security Headers** → Added 7 security headers

### High (🟠) - **6 Issues**
7. ✅ CSRF Protection → Proper CORS + SameSite cookies
8. ✅ Error Disclosure → Generic error messages
9. ✅ Input Size Limits → Request validation
10. ✅ Docker Security → Secrets, SSL, hardening
11. ✅ Subprocess Safety → Input validation
12. ✅ Trusted Host → Configured validation

### Medium (🟡) - **8 Issues**
13-20. ✅ Logging, sessions, database encryption, Redis hardening, etc.

### Low (🔵) - **4 Issues**
21-24. ✅ API versioning, debug mode, compression, docs auth

**Total: 24/24 Fixed ✅**

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `SECURITY_AUDIT_REPORT.md` | Full security audit with 24 issues |
| `SECURITY_FIXES.md` | Detailed implementation guide |
| `SECURITY_SUMMARY.md` | Executive summary |
| `SECURITY_README.md` | This file - quick start guide |
| `decoyable/api/auth.py` | Authentication system |
| `decoyable/api/ratelimit.py` | Rate limiting middleware |
| `.env.template` | Secure config template |
| `redis.conf` | Hardened Redis config |
| `setup_security.py` | Setup automation script |
| `test_security_fixes.py` | Security verification tests |

---

## 🚀 Setup Guide

### Step 1: Install Dependencies

```bash
# Install updated dependencies (includes security packages)
pip install -r requirements.txt

# New packages:
# - python-jose[cryptography] (JWT)
# - passlib[bcrypt] (password hashing)
# - bcrypt (hashing backend)
# - cryptography (encryption)
```

### Step 2: Generate Secure Configuration

```bash
# Run the automated setup script
python setup_security.py

# This will:
# 1. Generate secure random keys (SECRET_KEY, JWT_SECRET_KEY)
# 2. Generate API keys for authentication
# 3. Create .env file with secure defaults
# 4. Create Docker secrets (postgres, redis passwords)
# 5. Verify .gitignore includes sensitive files
```

**Output:**
```
✅ Created: .env
✅ Created: secrets/postgres_password.txt
✅ Created: secrets/redis_password.txt

📋 Generated API Keys:
   API Key 1: dcy_xxxxxxxxxxxxxxxxxxxxxxxxxxx
   API Key 2: dcy_xxxxxxxxxxxxxxxxxxxxxxxxxxx

⚠️  Save these keys securely!
```

### Step 3: Configure Your Environment

Edit `.env` and update these required values:

```bash
# Replace with your actual domains (NO WILDCARDS!)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Optional: Customize allowed scan directories
ALLOWED_SCAN_DIRS=/app,/workspace,/tmp
```

### Step 4: Deploy

```bash
# Build Docker images with security updates
docker-compose build

# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### Step 5: Verify Security

```bash
# Run security verification tests
python test_security_fixes.py --api-key YOUR_API_KEY_FROM_STEP2

# Expected output:
# ✅ Security Headers: All security headers present
# ✅ CORS Restriction: CORS properly restricted
# ✅ Authentication Required: Authentication correctly required
# ✅ Authentication Works: API key authentication works
# ✅ Rate Limiting: Rate limiting active (limit: 100, remaining: 95)
# ✅ Path Traversal Protection: Path traversal correctly blocked
# ✅ Input Validation: Path with '..' correctly blocked
# ✅ Trusted Host: Trusted host validation active
#
# 🎉 All security tests passed!
```

---

## 🔐 Using Authentication

### Method 1: API Key (Recommended for services)

```bash
# Include X-API-Key header
curl -H "X-API-Key: dcy_your_api_key_here" \
     -H "Content-Type: application/json" \
     -d '{"path": "/workspace/myproject"}' \
     http://localhost:8000/api/v1/scan/secrets
```

### Method 2: JWT Token (Recommended for users)

```python
# Python example
import requests

# 1. Get JWT token (you'll need to implement your login endpoint)
response = requests.post("http://localhost:8000/api/v1/auth/login", 
                        json={"username": "user", "password": "pass"})
token = response.json()["access_token"]

# 2. Use token in requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.post("http://localhost:8000/api/v1/scan/secrets",
                        headers=headers,
                        json={"path": "/workspace"})
```

---

## 📊 Rate Limits

Default rate limits per 60 seconds:

| Endpoint | Limit |
|----------|-------|
| `/api/v1/scan/all` | 5 requests |
| `/api/v1/scan/*` | 10 requests |
| `/api/v1/attacks` | 30 requests |
| `/api/v1/health` | 1000 requests |
| `/decoy/*` | 50 requests |
| Other endpoints | 100 requests |

**Rate limit headers in response:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1234567890
X-RateLimit-Window: 60
```

**When limit exceeded:**
```
HTTP 429 Too Many Requests
Retry-After: 45
```

---

## 🛡️ Security Headers

All responses now include:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Permissions-Policy: geolocation=(), microphone=(), camera=()
Referrer-Policy: strict-origin-when-cross-origin
```

These protect against:
- **HSTS**: Forces HTTPS
- **X-Content-Type**: Prevents MIME sniffing
- **X-Frame-Options**: Prevents clickjacking
- **CSP**: Prevents XSS attacks
- **Permissions**: Restricts browser APIs

---

## 🔍 Path Validation

Scanning is restricted to configured directories:

```bash
# ✅ Allowed (in ALLOWED_SCAN_DIRS)
curl -H "X-API-Key: key" -d '{"path": "/app/myproject"}' /api/v1/scan/secrets

# ❌ Blocked (not in ALLOWED_SCAN_DIRS)
curl -H "X-API-Key: key" -d '{"path": "/etc/passwd"}' /api/v1/scan/secrets
# Response: "Path outside allowed directories"

# ❌ Blocked (path traversal attempt)
curl -H "X-API-Key: key" -d '{"path": "/app/../etc/passwd"}' /api/v1/scan/secrets
# Response: "Path cannot contain '..'"

# ❌ Blocked (symbolic link)
curl -H "X-API-Key: key" -d '{"path": "/app/symlink"}' /api/v1/scan/secrets
# Response: "Symbolic links not allowed"
```

---

## 🧪 Testing Checklist

Before going to production, verify:

- [ ] **Authentication**
  ```bash
  # Should fail
  curl http://localhost:8000/api/v1/scan/secrets
  
  # Should succeed
  curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/v1/scan/secrets
  ```

- [ ] **Rate Limiting**
  ```bash
  # Make 11 requests quickly - 11th should be rate limited
  for i in {1..11}; do curl http://localhost:8000/api/v1/scan/all; done
  ```

- [ ] **Path Validation**
  ```bash
  # Should be blocked
  curl -H "X-API-Key: KEY" -d '{"path": "/etc/passwd"}' /api/v1/scan/secrets
  ```

- [ ] **Security Headers**
  ```bash
  # Check for security headers
  curl -I http://localhost:8000/health | grep -E "Strict-Transport|X-Frame|X-Content"
  ```

- [ ] **CORS**
  ```bash
  # Should not allow arbitrary origins
  curl -H "Origin: https://evil.com" -X OPTIONS /api/v1/scan/secrets
  ```

---

## 🆘 Troubleshooting

### Issue: "JWT_SECRET_KEY not configured"
**Solution:** Make sure .env file has `JWT_SECRET_KEY` set (minimum 32 chars)

### Issue: "API key authentication not configured"
**Solution:** Set `VALID_API_KEYS` in .env (comma-separated keys)

### Issue: "Path outside allowed directories"
**Solution:** Add the directory to `ALLOWED_SCAN_DIRS` in .env

### Issue: "Rate limit exceeded"
**Solution:** Wait for the window to reset (check `X-RateLimit-Reset` header)

### Issue: CORS errors in browser
**Solution:** Add your domain to `ALLOWED_ORIGINS` in .env

### Issue: Docker secrets not working
**Solution:** Ensure secrets/ directory exists with proper permissions:
```bash
chmod 600 secrets/*.txt
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `SECURITY_AUDIT_REPORT.md` | **Full audit** - All 24 issues with technical details |
| `SECURITY_FIXES.md` | **Implementation guide** - How each fix works |
| `SECURITY_SUMMARY.md` | **Executive summary** - High-level overview |
| `SECURITY_README.md` | **This file** - Quick start and usage guide |

---

## 🔄 Migration from v1.2.1 to v1.2.2

If you have an existing DECOYABLE installation:

1. **Backup your data**
   ```bash
   docker-compose exec db pg_dump -U app app > backup.sql
   ```

2. **Update code**
   ```bash
   git pull origin main
   ```

3. **Install new dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate new secrets** (DON'T SKIP THIS!)
   ```bash
   python setup_security.py
   ```

5. **Migrate configuration**
   - Copy settings from old .env to new .env
   - Update ALLOWED_ORIGINS and ALLOWED_HOSTS
   - Add new VALID_API_KEYS

6. **Rebuild and restart**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

7. **Test security**
   ```bash
   python test_security_fixes.py --api-key YOUR_KEY
   ```

---

## 🎓 Best Practices

1. **Rotate API Keys Regularly**
   - Generate new keys monthly
   - Invalidate old keys
   - Use different keys for different environments

2. **Monitor Security Logs**
   - Check for failed authentication attempts
   - Monitor rate limit violations
   - Alert on path traversal attempts

3. **Keep Dependencies Updated**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

4. **Use HTTPS in Production**
   - Configure SSL/TLS certificates
   - Set `Strict-Transport-Security` header
   - Redirect HTTP to HTTPS

5. **Principle of Least Privilege**
   - Only scan directories you need
   - Use read-only API keys where possible
   - Limit rate limits for public endpoints

---

## 📞 Support

- **Security Issues:** Use GitHub Security Advisories
- **Bug Reports:** GitHub Issues
- **Documentation:** [GitHub Wiki](https://github.com/Kolerr-Lab/supper-decoyable/wiki)
- **General Questions:** GitHub Discussions

---

## ✅ Security Checklist

Before deploying to production:

- [ ] Generated secure SECRET_KEY (32+ characters)
- [ ] Generated secure JWT_SECRET_KEY (32+ characters)
- [ ] Generated secure API keys
- [ ] Set ALLOWED_ORIGINS to actual domains (no wildcards)
- [ ] Set ALLOWED_HOSTS to actual domains (no wildcards)
- [ ] Set APP_ENV=production
- [ ] Created PostgreSQL and Redis passwords
- [ ] Configured ALLOWED_SCAN_DIRS appropriately
- [ ] Disabled API_DEBUG
- [ ] Tested authentication
- [ ] Tested rate limiting
- [ ] Tested path validation
- [ ] Verified security headers
- [ ] Verified .env not in git
- [ ] Backed up secrets securely
- [ ] Set up monitoring and alerts
- [ ] Reviewed Docker security settings
- [ ] Tested in staging environment

---

## 📈 What's Next?

Future security enhancements (planned):

- [ ] OAuth2 provider integration
- [ ] Multi-factor authentication (MFA)
- [ ] Advanced threat detection
- [ ] Security audit logs
- [ ] Automated vulnerability scanning
- [ ] Bug bounty program
- [ ] SOC 2 / ISO 27001 compliance

---

**Version:** 1.2.2  
**Date:** April 2, 2026  
**Status:** ✅ Production-Ready  

🔒 **Your DECOYABLE instance is now secure!**
