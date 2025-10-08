# Test Case 2: SQL Injection Detection
# app/api.py
from flask import request

def get_user():
    uid = request.args.get("id")
    query = "SELECT * FROM users WHERE id = %s" % uid   # vulnerable
    db.execute(query)
