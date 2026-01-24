from flask import Blueprint, render_template, session
from helpers import login_required, validate_session

homepage_bp = Blueprint('homepage', __name__)

@homepage_bp.route("/")
@login_required
@validate_session
def index():
    """Homepage"""
    # User info that will be handed to the template
    user: dict = {
        'username' : session['username'],
        'role' : session['role'],
        'role_starts_with_vowel' : False
    }
    # The template will use it for defining which article
    # to use while greeting the user
    # I'm doing it on the server because I don't care
    vowels: list = ['e','y','u','i','o','a',]
    if user['role'].lower()[0] in vowels:
        user['role_starts_with_vowel'] = True

    return render_template("index.html", user=user)

