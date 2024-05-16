"""
Function decorator for Flask routes that require authentication.

Check for valid tokens in the request headers.
"""

from functools import wraps
from flask import request, jsonify

def google_auth_required(func):
    """
    Decorator to go around routes that require google authentication.    
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('google-auth-token')
        if not token:
            return jsonify({"status": 401, "response": "Unauthorized"})
        return func(*args, **kwargs)
    return wrapper

def jira_auth_required(func):
    """
    Decorator to go around routes that require jira authentication.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('jira-auth-token')
        if not token:
            return jsonify({"status": 401, "response": "Unauthorized"})
        return func(*args, **kwargs)
    return wrapper