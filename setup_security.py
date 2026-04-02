#!/usr/bin/env python3
"""
DECOYABLE Security Setup Helper

Generates secure configuration values for DECOYABLE deployment.
Run this script to create secure random keys and initial configuration.

Usage:
    python setup_security.py
    
This will create/update your .env file with secure values.
"""

import os
import secrets
import string
from pathlib import Path


def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure random key."""
    return secrets.token_urlsafe(length)


def generate_password(length: int = 32) -> str:
    """Generate a strong random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_api_key() -> str:
    """Generate an API key with a recognizable prefix."""
    return f"dcy_{secrets.token_urlsafe(32)}"


def create_secrets_directory():
    """Create secrets directory if it doesn't exist."""
    secrets_dir = Path("secrets")
    secrets_dir.mkdir(exist_ok=True)
    
    # Set proper permissions (owner read/write only)
    os.chmod(secrets_dir, 0o700)
    
    return secrets_dir


def write_secret_file(filepath: Path, content: str):
    """Write a secret to a file with proper permissions."""
    filepath.write_text(content)
    os.chmod(filepath, 0o600)  # Owner read/write only
    print(f"✅ Created: {filepath}")


def create_env_file():
    """Create .env file with secure values."""
    env_file = Path(".env")
    
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("ℹ️  Skipping .env creation")
            return
    
    # Generate secure values
    secret_key = generate_secret_key()
    jwt_secret_key = generate_secret_key()
    api_key1 = generate_api_key()
    api_key2 = generate_api_key()
    
    # Create .env content
    env_content = f"""# DECOYABLE Environment Configuration
# Generated on {os.popen('date').read().strip()}
# NEVER commit this file to version control!

# ===== APPLICATION =====
APP_ENV=production
APP_NAME=decoyable
APP_VERSION=1.2.2

# ===== SECURITY (REQUIRED) =====
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret_key}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Keys (comma-separated)
VALID_API_KEYS={api_key1},{api_key2}

# ===== API SERVER =====
API_HOST=0.0.0.0
APP_PORT=8000
API_DEBUG=false
API_WORKERS=4
API_RELOAD=false

# ===== CORS & HOST SECURITY =====
# Update these with your actual domains!
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# ===== DATABASE =====
DATABASE_URL=postgresql://app@db:5432/app?sslmode=require
POSTGRES_USER=app
POSTGRES_DB=app

DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_ECHO=false

# ===== REDIS =====
REDIS_URL=redis://:@redis:6379/0
REDIS_DB=0

# ===== CELERY =====
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# ===== KAFKA (Optional) =====
KAFKA_ENABLED=false

# ===== HONEYPOT =====
HONEYPOT_ENABLED=true
DECOY_PORTS=9001,2222
HONEYPOT_LOG_ATTACKS=true
HONEYPOT_BLOCK_IPS=true

# ===== SCANNERS =====
ALLOWED_SCAN_DIRS=/app,/workspace

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_JSON_FORMAT=true
"""
    
    env_file.write_text(env_content)
    os.chmod(env_file, 0o600)
    
    print(f"✅ Created: {env_file}")
    print("\n📋 Generated API Keys:")
    print(f"   API Key 1: {api_key1}")
    print(f"   API Key 2: {api_key2}")
    print("\n⚠️  Save these keys securely - they won't be shown again!")


def create_docker_secrets():
    """Create Docker secret files."""
    secrets_dir = create_secrets_directory()
    
    # Generate passwords
    postgres_password = generate_password()
    redis_password = generate_password()
    
    # Write secret files
    write_secret_file(secrets_dir / "postgres_password.txt", postgres_password)
    write_secret_file(secrets_dir / "redis_password.txt", redis_password)
    
    print("\n📋 Generated Docker Secrets:")
    print(f"   PostgreSQL Password: {postgres_password}")
    print(f"   Redis Password: {redis_password}")
    print("\n⚠️  These passwords are saved in secrets/ directory")


def verify_gitignore():
    """Verify .gitignore includes sensitive files."""
    gitignore = Path(".gitignore")
    
    if not gitignore.exists():
        print("⚠️  .gitignore not found - creating one")
        gitignore.write_text("""# Sensitive files
.env
.env.*
secrets/
*.key
*.pem
*.secret
""")
        print("✅ Created .gitignore")
        return
    
    content = gitignore.read_text()
    
    required_patterns = [".env", "secrets/", "*.key"]
    missing_patterns = [p for p in required_patterns if p not in content]
    
    if missing_patterns:
        print(f"⚠️  .gitignore missing patterns: {missing_patterns}")
        print("   Please add them manually to prevent committing secrets")
    else:
        print("✅ .gitignore looks good")


def print_next_steps():
    """Print next steps for deployment."""
    print("\n" + "="*60)
    print("🎉 Security Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print()
    print("1. Review and update .env file:")
    print("   - Update ALLOWED_ORIGINS with your actual domains")
    print("   - Update ALLOWED_HOSTS with your actual domains")
    print()
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("3. Build Docker images:")
    print("   docker-compose build")
    print()
    print("4. Start services:")
    print("   docker-compose up -d")
    print()
    print("5. Test authentication:")
    print("   curl -H \"X-API-Key: <your_api_key>\" \\")
    print("        http://localhost:8000/api/v1/health")
    print()
    print("6. Check security headers:")
    print("   curl -I http://localhost:8000/health")
    print()
    print("📚 Documentation:")
    print("   - Read SECURITY_FIXES.md for details")
    print("   - Read SECURITY_SUMMARY.md for overview")
    print("   - Read SECURITY_AUDIT_REPORT.md for full audit")
    print()
    print("⚠️  IMPORTANT:")
    print("   - NEVER commit .env to version control")
    print("   - Store production secrets in secure vault")
    print("   - Rotate API keys regularly")
    print("   - Monitor security logs")
    print()


def main():
    """Main setup function."""
    print("="*60)
    print("DECOYABLE Security Setup")
    print("="*60)
    print()
    print("This script will generate secure configuration values.")
    print()
    
    # Verify we're in the right directory
    if not Path("decoyable").exists():
        print("❌ Error: Must run from DECOYABLE project root")
        return 1
    
    # Verify gitignore
    verify_gitignore()
    print()
    
    # Create .env file
    print("Creating .env file...")
    create_env_file()
    print()
    
    # Create Docker secrets
    print("Creating Docker secrets...")
    create_docker_secrets()
    print()
    
    # Print next steps
    print_next_steps()
    
    return 0


if __name__ == "__main__":
    exit(main())
