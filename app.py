from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from model import db_handler
from helpers import apology

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


@app.route("/login")
def login():
    """Login page"""
    return render_template("login.html")


@app.route("/register")
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
        return render_template("register.html")
    # When the user tries to submit the form
    elif request.method == "POST":
        # Get the data (ensure the datatype of str)
        new_username: str = str(request.form.get("username"))
        new_password: str = str(request.form.get("password"))
        new_password_confirmation: str = str(request.form.get("confirmation"))
        return render_template("register.html", message="Not implemented yet.", color="red")
