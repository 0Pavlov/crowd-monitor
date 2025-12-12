from flask import Blueprint, render_template
from helpers import login_required, validate_session

homepage_bp = Blueprint('homepage', __name__)

@homepage_bp.route("/")
@login_required
@validate_session
def index():
    """Homepage"""
    return render_template("index.html")

