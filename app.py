from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from model import db_handler

# Create/check the database
created: bool = db_handler.create_database("crowd.db")
# Check success
if not created:
    exit("Database error.")


app = Flask(__name__)
