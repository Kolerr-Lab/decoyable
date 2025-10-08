# Comprehensive test file for engineer's test cases
# This file contains all 4 test cases

import os
import hashlib
import random
from flask import request

# Case 1: Hardcoded API key (Secret Detection) - WORKING
API_KEY = "sk-proj-1234567890abcdef"  # hardcoded secret
SECRET_TOKEN = "ghp_1234567890abcdefghijklmnop"

# Case 2: SQL Injection - NOW FIXED
def get_user():
    uid = request.args.get("id")
    query = "SELECT * FROM users WHERE id = %s" % uid   # vulnerable
    # Should be: query = "SELECT * FROM users WHERE id = ?", (uid,)
    return query

# Case 3: Command Injection via os.system - NOW FIXED
def run_ping(host):
    os.system("ping -c 1 " + host)  # vulnerable
    # Should use: subprocess.run(['ping', '-c', '1', host], check=True)

# Case 4: Auto-Fix validation patterns
def weak_crypto_example():
    # Weak cryptography - MD5
    password = "secret123"
    hashed = hashlib.md5(password.encode()).hexdigest()  # vulnerable
    # Should use: hashlib.sha256()
    return hashed

def insecure_random_example():
    # Insecure random for token generation
    token = str(random.random())  # vulnerable
    # Should use: secrets.token_hex(16)
    return token

def another_sql_injection():
    user_input = "malicious"
    query = "DELETE FROM users WHERE name = '%s'" % user_input  # vulnerable
    return query

if __name__ == "__main__":
    print("Test file with multiple vulnerabilities")
