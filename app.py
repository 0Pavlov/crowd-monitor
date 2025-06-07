from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from model import db_handler
from helpers import apology
from werkzeug.security import generate_password_hash, check_password_hash

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


@app.route("/")
def index():
    """Homepage"""
    return apology("Test error occured", code=666)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("login.html")
    # User reached route via POST
    elif request.method == "POST":
        # Clear any previous session
        session.clear()

        # Get the name and password
        username: str = request.form.get("username")
        password: str = request.form.get("password")

        # Check if blank
        bl: str = ""
        if username == bl or password == bl:
            return render_template("login.html", message="You must fill in all of the forms.", color="red")
        return render_template("login.html")


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
        chars: str = "!?*$#@%^&()_-+=`~\"\'.<>/,"
        name_has_chars: bool = False
        for char in new_username:
            if char in chars:
                name_has_chars = True

        # Check
        if name_has_chars:
            # Notify user
            return render_template("register.html", message=f"Your name contains {chars}.", color="red")

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

        return render_template("register.html", message="Successfully registered.", color="green")
