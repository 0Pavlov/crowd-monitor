from flask import Blueprint, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from model import db_handler
from helpers import apology, login_required, GREEN, RED, RESET

# Define the blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page"""

    # Clear any previous session
    session.clear()

    # User reached route via GET
    if request.method == "GET":
        return render_template("/auth/login.html")
    # User reached route via POST
    elif request.method == "POST":

        # Get the name and password
        username: str = request.form.get("username")
        password: str = request.form.get("password")

        # Check if blank
        bl: str = ""
        if username == bl or password == bl:
            return render_template("/auth/login.html", message="You must fill in all of the forms.", color="#721c24")
        # Set of the unappropriate chars in the name
        chars: str = "!?*$#@%^&()-+=`~\"\'.<>/,"
        name_has_chars: bool = False
        for char in username:
            if char in chars:
                name_has_chars = True
        # Single space
        space: str = " "

        if name_has_chars or space in username:
            return render_template("/auth/login.html", message=f"Do not submit name which contains spaces or special characters: {chars}", color="#721c24")

        # Connect to the db
        db = db_handler.db_connect("crowd.db")

        # Query the db for this userdata
        user = db_handler.query(db, "SELECT * FROM users WHERE username = ?", username)

        # Check if not found
        if len(user) == 0:
            return render_template("/auth/login.html", message=f"No user with the name: \"{username}\".", color="#721c24")

        # Check the password
        password_is_correct: bool = check_password_hash(user[0]["password_hash"], password)
        
        if not password_is_correct:
            return render_template("/auth/login.html", message="Incorrect password.", color="#721c24")

        # Remember the user in the session
        session["user_id"] = user[0]["id"]
        session["username"] = user[0]["username"]
        session["role"] = user[0]["role"]

        # Close the db connection
        db.close()

        # Redirect the user to the homepage
        return redirect("/")


@auth_bp.route("/register", methods=["GET", "POST"])
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
        return render_template("/auth/register.html", color="#721c24")
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
            return render_template("/auth/register.html", message=f"You should fill in all of the forms.", color="#721c24")

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
            return render_template("/auth/register.html", message=f"Your name contains spaces or {chars}.", color="#721c24")

        # Check if the user with this name already exists
        query = db_handler.query(db, "SELECT username FROM users WHERE username = ?", new_username)
        # Check if returned the empty list
        if query != []:
            # Notify user
            return render_template("/auth/register.html", message=f"This username is taken.", color="#721c24")

        # Compare the passwords
        passwords_match: bool = new_password == new_password_confirmation
        if not passwords_match:
            return render_template("/auth/register.html", message=f"Passwords don't match.", color="#721c24")

        # Disallow spaces in the password
        if space in new_password:
            return render_template("/auth/register.html", message="Password shouldn't containd spaces.", color="#721c24")

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

        return render_template("/auth/register.html", message="Successfully registered.", color="green")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logs the user out.

    Login is required because the user shouldn't access this route in other scenario.
    """
    if request.method == "GET":
        # Clear the user session
        session.clear()
        # Redirect the user to the main page
        return redirect("/")
