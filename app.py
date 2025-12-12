from flask import Flask
from flask_session import Session
from model import db_handler

from blueprints.auth import auth_bp
from blueprints.homepage import homepage_bp
from blueprints.tasks import tasks_bp

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

# Register Blueprints
app.register_blueprint(auth_bp) 
app.register_blueprint(homepage_bp)
app.register_blueprint(tasks_bp)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
