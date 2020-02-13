from functools import wraps
from flask import redirect, session

def login_required(f):
    """
    A function to make sure the user logged in to the system before granted access to use the web application.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        else:
            return f(*args, **kwargs)
    return wrap
