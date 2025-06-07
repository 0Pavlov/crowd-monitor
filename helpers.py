from flask import render_template
from functools import wraps
from flask import redirect, session


def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, message=message)

def login_required(f):
    """
    Require login in order to access the route.

    This decorator wraps the route and ensures that only logged in users
    can access the route.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated
