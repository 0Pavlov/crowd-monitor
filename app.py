from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from model import db_handler

# Create/check the database
created: bool = db_handler.create_database("crowd.db")
# Check success
if not created:
    exit("Database error.")


# Configure application
app = Flask(__name__)


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
    return render_template("index.html")


@app.route("/login")
def login():
    """Login page"""
    return render_template("login.html")
