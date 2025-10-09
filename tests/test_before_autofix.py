# Simple test file for auto-fix demonstration
# This file will be automatically fixed

import os
import subprocess

# Test 1: SQL Injection with % formatting
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = %s" % user_id
    return query

# Test 2: Command Injection with os.system
def ping_server(host):
    subprocess.run(['ping', '-c', '1', host], check=True)
    return "Done"

# Test 3: Multiple SQL injections
def search_data(term):
    query = "SELECT * FROM products WHERE name = '%s'" % term
    return query

def update_user(user_id, name):
    query = "UPDATE users SET name = '%s' WHERE id = %s" % (name, user_id)
    return query