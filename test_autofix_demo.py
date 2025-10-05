"""
Demo file to test DECOYABLE auto-fix feature
This file intentionally contains security issues for demonstration
"""
import hashlib
import random
import subprocess

# Issue 1: Hardcoded secret (will be fixed to use environment variable)
API_KEY = "sk-1234567890abcdef"
SECRET_TOKEN = "my_secret_token_123"

# Issue 2: Weak cryptography - MD5 (will be fixed to SHA-256)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Issue 3: Insecure random (will be fixed to use secrets module)
def generate_session_token():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for _ in range(32))

# Issue 4: Command injection risk (will add IP validation)
def block_ip(ip_addr):
    cmd = f"iptables -A INPUT -s {ip_addr} -j DROP"
    subprocess.run(cmd, shell=True)

# Issue 5: SQL injection risk (example)
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return query

print("This is a demo file with intentional security issues")
print(f"API Key: {API_KEY}")
print(f"MD5 Hash: {hash_password('test')}")
print(f"Session Token: {generate_session_token()}")
