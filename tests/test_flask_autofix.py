
"""
Test file for v1.1.1 auto-fix features.
NOTE: This file contains intentional use of dangerous patterns (os.system, subprocess with shell=True, etc.)
for the purpose of testing, demonstration, and validation of security scanners. These are NOT used in production code.
Flask app with SQL injection and command injection vulnerabilities
"""

from flask import Flask, request
import os

app = Flask(__name__)

# SQL Injection Test Case 1: % string formatting
@app.route('/user/<user_id>')
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s" % user_id
    result = db.execute(query)
    return result

# SQL Injection Test Case 2: String concatenation
@app.route('/search')
def search():
    term = request.args.get('q')
    query = "SELECT * FROM products WHERE name LIKE '%" + term + "%'"
    results = db.execute(query)
    return results

# SQL Injection Test Case 3: Multiple parameters
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    query = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password)
    user = db.execute(query)
    return user

# Command Injection Test Case 1: os.system with concatenation
@app.route('/ping')
def ping_host():
    host = request.args.get('host')
    os.system("ping -c 1 " + host)
    return "Pinged"

# Command Injection Test Case 2: os.system with f-string
@app.route('/traceroute')
def traceroute():
    target = request.args.get('target')
    os.system(f"traceroute {target}")
    return "Done"

if __name__ == '__main__':
    app.run(debug=True)
