from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime
from model import db_handler

# Constants for console output
GREEN = '\033[92m'
RED = '\033[31m'
RESET = '\033[0m'


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
    Converts a SQLite DATETIME string to a short, relative format with time.

    Uses abbreviated month names (e.g., "Aug").
    If the date is today, it returns only the time in AM/PM format (e.g., "2:30 PM").
    If the date is in the current year, it returns the abbreviated month, day, and time (e.g., "Aug 26, 2:30 PM").
    If the date is in a past year, it returns the abbreviated month, day, year, and time (e.g., "Aug 26, 2024, 2:30 PM").

    Args:
        datetime_str: The DATETIME string from SQLite (e.g., '2025-08-26 14:30:00').

    Returns:
        A formatted and relative date/time string.
        Returns an error message if the input string is not in the expected format.
    """
    try:
        now = datetime.now()
        input_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

        # Create the formatted time string. 
        # .lstrip('0') removes a leading zero from the hour (e.g., "02:30 PM" -> "2:30 PM")
        time_str = input_datetime.strftime('%I:%M %p').lstrip('0').replace(' 0', ' ')

        # If the date is today, return only the time
        if input_datetime.date() == now.date():
            return time_str

        # If the date is in the current year
        elif input_datetime.year == now.year:
            # Format with abbreviated month (%b), day, and the time
            return input_datetime.strftime(f'%b %d, {time_str}')
        
        # Otherwise, the date is in a past year
        else:
            # Format with abbreviated month (%b), day, year, and the time
            return input_datetime.strftime(f'%b %d, %Y, {time_str}')

    except (ValueError, TypeError):
        return "Invalid DATETIME format"


def validate_session(f):
    @wraps(f)
    def validate_user_session(*args, **kwargs):
        """Validates user session.
        
        Handles case where the user already has previous session saved in their browser.
        Or tries to push custom cookies to the server in order to gain access to the other user's account.
        Or the current session is no longer valid because the user was deleted internally (users table entry).
        Checks if the user id is present in the users table.
        Checks if the username is stored in the session corresponds to that same id.
        Checks if user's role matches the user's role in the db (prevent role manipulation).
        """
        # Get the session data
        try:
            user_id: int = session['user_id']
            username: str = session['username']
            role: str = session['role']
        except:
            return apology("Invalid session. Unable to retrieve data from the session, session is corrupted.", code=400)
        
        # Compare it to the data from the users table

        # Connect to the db
        db = db_handler.db_connect("crowd.db", silent=True)

        # Get the data for this username
        try:
            data = db_handler.query(db, "SELECT username, id, role FROM users WHERE id = ?", user_id, silent=True)
        except:
            db.close()
            return apology("Invalid session. User no longer exists or the session is corrupted.", code=400)

        # Additional checks
        if not data or len(data) == 0:
            db.close()
            return apology("Invalid session. User with this username doesn't exists or the session is corrupted.", code=400)

        # Compare the data
        valid: bool = username == data[0]['username']

        if not valid:
            db.close()
            return apology("Invalid session. User's username doesn't match the internal user id. Session is corrupted.", code=400)

        # Check if the user's session role is same as in the db
        valid_role: bool = role == data[0]['role']
        if not valid_role:
            db.close()
            return apology("Invalid session. Role mismatch.")
        
        db.close()
        return f(*args, **kwargs)
    return validate_user_session
