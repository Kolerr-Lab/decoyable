# Test file for v1.1.1 auto-fix features
# Django app with SQL injection vulnerabilities

from django.http import HttpResponse
from django.db import connection

def get_user_view(request, user_id):
    """SQL Injection via % formatting"""
    query = "SELECT * FROM users WHERE id = %s" % user_id
    cursor = connection.cursor()
    cursor.execute(query)
    return HttpResponse("User data")

def search_products(request):
    """SQL Injection via string concatenation"""
    term = request.GET.get('q', '')
    query = "SELECT * FROM products WHERE name = '" + term + "'"
    cursor = connection.cursor()
    cursor.execute(query)
    return HttpResponse("Search results")

def delete_user(request):
    """SQL Injection with DELETE statement"""
    user_id = request.GET.get('id')
    query = "DELETE FROM users WHERE id = %s" % user_id
    cursor = connection.cursor()
    cursor.execute(query)
    return HttpResponse("User deleted")
