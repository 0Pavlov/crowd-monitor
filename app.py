from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from model import db_handler
from helpers import apology, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Store the colors for the colored console output
GREEN = '\033[92m'
RED = '\033[31m'
RESET = '\033[0m'

# Create/check the database
created: bool = db_handler.create_database("crowd.db")
# Check success
if not created:
    exit("Database error.")

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def validate_session(f):
    @wraps(f)
    def validate_user_session(*args, **kwargs):
        """Validates user session.
        
        Handles case where the user already has previous session saved in their browser.
        Or tries to push custom cookies to the server in order to gain access to the other user's account.
        Or the current session is no longer valid because the user was deleted internally (users table entry).
        Checks if the user id is present in the users table.
        Checks if the username is stored in the session corresponds to that same id.
        """
        # Get the session data
        try:
            user_id: int = session['user_id']
            username: str = session['username']
        except:
            return apology("Invalid session. Unable to retrieve data from the session, session is corrupted.", code=400)
        
        # Compare it to the data from the users table

        # Connect to the db
        db = db_handler.db_connect("crowd.db")

        # Get the data for this username
        try:
            data = db_handler.query(db, "SELECT username, id FROM users WHERE id = ?", user_id)
        except:
            return apology("Invalid session. User no longer exists or the session is corrupted.", code=400)

        # Additional checks
        if not data or len(data) == 0:
            return apology("Invalid session. User with this username doesn't exists or the session is corrupted.", code=400)

        # Compare the data
        valid: bool = username == data[0]['username']

        if not valid:
            return apology("Invalid session. User's username doesn't match the internal user id. Session is corrupted.", code=400)
        
        return f(*args, **kwargs)
    return validate_user_session


@app.route("/")
@login_required
def index():
    """Homepage"""
    return apology("Test error occured", code=666)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""

    # Clear any previous session
    session.clear()

    # User reached route via GET
    if request.method == "GET":
        return render_template("login.html")
    # User reached route via POST
    elif request.method == "POST":

        # Get the name and password
        username: str = request.form.get("username")
        password: str = request.form.get("password")

        # Check if blank
        bl: str = ""
        if username == bl or password == bl:
            return render_template("login.html", message="You must fill in all of the forms.", color="red")
        # Set of the unappropriate chars in the name
        chars: str = "!?*$#@%^&()-+=`~\"\'.<>/,"
        name_has_chars: bool = False
        for char in username:
            if char in chars:
                name_has_chars = True
        # Single space
        space: str = " "

        if name_has_chars or space in username:
            return render_template("login.html", message=f"Do not submit name which contains spaces or special characters: {chars}", color="red")

        # Connect to the db
        db = db_handler.db_connect("crowd.db")

        # Query the db for this userdata
        user = db_handler.query(db, "SELECT * FROM users WHERE username = ?", username)

        # Check if not found
        if len(user) == 0:
            return render_template("login.html", message=f"No user with the name: \"{username}\".", color="red")

        # Check the password
        password_is_correct: bool = check_password_hash(user[0]["password_hash"], password)
        
        if not password_is_correct:
            return render_template("login.html", message="Incorrect password.", color="red")

        # Remember the user in the session
        session["user_id"] = user[0]["id"]
        session["username"] = user[0]["username"]

        # Close the db connection
        db.close()

        # Redirect the user to the homepage
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register page

    The register template takes arguments.
    Uses Jinja to place the arguments to the page.

    Args:
        message (str): A message shown to a user on the page.
        color (str): Color of the message in the format, that html can understand (red | #000000).
    """
    # When the user just visits the page
    if request.method == "GET":
        # Return the page
        return render_template("register.html", color="red")
    # When the user tries to submit the form
    elif request.method == "POST":

        # Connect to the db
        db = db_handler.db_connect("crowd.db")

        # Get the data (ensure the datatype of str)
        new_username: str = str(request.form.get("username"))
        new_password: str = str(request.form.get("password"))
        new_password_confirmation: str = str(request.form.get("confirmation"))

        # Check if inputs are blank
        bl: str = ""
        if new_username == bl or new_password == bl or new_password_confirmation == bl:
            return render_template("register.html", message=f"You should fill in all of the forms.", color="red")

        # Set of the unappropriate chars in the name
        chars: str = "!?*$#@%^&()-+=`~\"\'.<>/,"
        name_has_chars: bool = False
        for char in new_username:
            if char in chars:
                name_has_chars = True
        # Single space
        space: str = " "

        # Check
        if name_has_chars or space in new_username:
            # Notify user
            return render_template("register.html", message=f"Your name contains spaces or {chars}.", color="red")

        # Check if the user with this name already exists
        query = db_handler.query(db, "SELECT username FROM users WHERE username = ?", new_username)
        # Check if returned the empty list
        if query != []:
            # Notify user
            return render_template("register.html", message=f"This username is taken.", color="red")

        # Compare the passwords
        passwords_match: bool = new_password == new_password_confirmation
        if not passwords_match:
            return render_template("register.html", message=f"Passwords don't match.", color="red")

        # Disallow spaces in the password
        if space in new_password:
            return render_template("register.html", message="Password shouldn't containd spaces.", color="red")

        # Generate password hash
        password_hash: str = generate_password_hash(new_password)

        try:
            # Add the user to the db
            db_handler.query(db, "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", new_username, password_hash, "worker")
        except:
            db.rollback()
            print(f"{RED}Performed rollback.{RESET}")
            return apology("db fktup sorry")
        db.commit()
        print(f"{GREEN}Successfully commited.{RESET}")

        # Close the db connection
        db.close()

        return render_template("register.html", message="Successfully registered.", color="green")
