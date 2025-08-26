from flask import render_template
from functools import wraps
from flask import redirect, session
from datetime import datetime


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


def format_sqlite_datetime(datetime_str: str) -> str:
    """
    Converts a SQLite DATETIME string to a more readable and relative format.

    If the date is today, it returns the time in AM/PM format (e.g., "02:30 PM").
    If the date is in the current year but not today, it returns the month and day (e.g., "August 26").
    If the date is in a past year, it returns the month, day, and year (e.g., "August 26, 2024").

    Args:
        datetime_str: The DATETIME string from SQLite (e.g., '2025-08-26 14:30:00').

    Returns:
        A formatted and relative date/time string.
        Returns an error message if the input string is not in the expected format.
    """
    try:
        # The current date and time
        now = datetime.now()
        # The input string converted to a datetime object
        input_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

        # Check if the date is today
        if input_datetime.date() == now.date():
            # Format for time only
            return input_datetime.strftime('%I:%M %p').lstrip('0').replace(' 0', ' ')
        
        # Check if the date is in the current year (but not today)
        elif input_datetime.year == now.year:
            # Format for month and day
            return input_datetime.strftime('%B %d')
        
        # Otherwise, the date is in a past year
        else:
            # Format for month, day, and year
            return input_datetime.strftime('%B %d, %Y')

    except (ValueError, TypeError):
        return "Invalid DATETIME format"
