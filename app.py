from flask import Flask, redirect, render_template, request, session, jsonify, flash
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


@app.route("/")
@login_required
@validate_session
def index():
    """Homepage"""
    return render_template("index.html")


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
        session["role"] = user[0]["role"]

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


@app.route("/logout", methods=["GET", "POST"])
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


@app.route("/tasks", methods=["GET", "POST"])
@login_required
@validate_session
def tasks():
    """Tasks"""
    if request.method == "GET":
        if session.get("role") == 'admin':
            # Connect to the db
            db = db_handler.db_connect("crowd.db")

            # Retrieve the tasks

            # Get the table schema
            table_info = db_handler.query(db, "PRAGMA table_info(tasks)")
            # Get the column names
            column_names = [info[1] for info in table_info]
            # Get the list of sql objects
            tasks = db_handler.query(db, "SELECT * FROM tasks")
            # Combine the column names with values to get the list of dicts
            tasks: list[dict] = [dict(zip(column_names, row)) for row in tasks]

            # This dict stores the full info on each assignment mapped to it's id
            # HIGHLY inefficient (will result in double querying the same table)
            # was added after the template layout was done
            # didn't wanted to refactor the template
            assignments_info: dict[dict] = {}

            # Now for each task construct a list of assignments ids
            for task in tasks:
                assignments_ids_from_db: list = db_handler.query(db, "SELECT id FROM assignments WHERE task_id = ?", task['id'])
                assignments_ids: list = []
                for assigned_id in assignments_ids_from_db:
                    assignments_ids.append(assigned_id['id'])

                    # Query the db for an assignment with this id
                    temp_assignment: dict = dict(db_handler.query(db, "SELECT * FROM assignments WHERE id = ?", assigned_id['id'])[0])
                    # Add last submission info to it
                    last_submission: str = db_handler.query(db, "SELECT submitted_answer FROM submissions WHERE assignment_id = ? ORDER BY timestamp DESC LIMIT 1", assigned_id['id'])[0]['submitted_answer']
                    temp_assignment['last_submission'] = last_submission
                    # Add username of the person to it
                    worker_username: str = db_handler.query(db, "SELECT u.username FROM users u JOIN assignments a ON u.id = a.user_id WHERE a.id = ?", assigned_id['id'])[0]['username']
                    temp_assignment['assigned_worker'] = worker_username
                    # Append the assigments_info
                    assignments_info[assigned_id['id']] = temp_assignment
                # Add this list to the task dict
                task['assignments_ids'] = assignments_ids

            # Close the connection
            db.close()
            return render_template("tasks.html", tasks=tasks, assignments_info=assignments_info)
    if request.method == "POST":
        # Create task section
        if request.form.get("task_creation_form") == "create_task":
            # Check the roles
            session_role_is_admin: bool = session.get("role") == 'admin'
            if session_role_is_admin:
                # Retrieve the data from the forms
                content: str = request.form.get('content')
                task_type: str = request.form.get('task_type')
                gsa: str = request.form.get('gsa')
                deadline = request.form.get('deadline')
                worker: str = request.form.get('worker')

                # Check the data
                if content == None or content.strip() == '':
                    flash("The content field is empty.", "danger")
                    return redirect("/tasks")
                if gsa == None or gsa.strip() == '':
                    flash("The gsa isn't specified.", "danger")
                    return redirect("/tasks")
                if task_type == None or task_type.strip() == '':
                    flash("The task type isn't specified.", "danger")
                    return redirect("/tasks")
                if worker == None or worker.strip() == '':
                    flash("The worker isn't specified.", "danger")
                    return redirect("/tasks")
                if deadline == None or deadline.strip() == '':
                    flash("The deadline isn't specified.", "danger")
                    return redirect("/tasks")

                # Convert the task type to lowercase
                task_type: str = task_type.lower()

                # Convert the deadline to the SQL DATETIME
                deadline = deadline.replace('T', ' ') + ':00'

                # Connect to the db
                db = db_handler.db_connect("crowd.db")

                # Get the id of who creating the task
                creator_id: int = session['user_id']

                # Get the id of the worker
                worker_id: int = db_handler.query(db, "SELECT id FROM users WHERE username = ?", worker)[0]['id']

                # Create the task
                try:
                    db_handler.query(db, "INSERT INTO tasks (creator_id, task_type, content, gold_standard_answer, deadline) VALUES (?, ?, ?, ?, ?)", creator_id, task_type, content, gsa, deadline)
                    print("Successfully created task")
                except:
                    print("ERROOOOOOOOOOORRRRRRR")
                    db.rollback()

                # Find out the task id
                task_id = db_handler.query(db, "SELECT id FROM tasks WHERE (content == ? AND creator_id == ?)", content, creator_id)[0]['id']

                # Assign the task to worker
                try:
                    db_handler.query(db, "INSERT INTO assignments (task_id, user_id, assigned_by_id) VALUES (?, ?, ?)", task_id, worker_id, creator_id)
                    print("SUCCEEEESSSSSSSSS")
                except:
                    # Delete the task
                    db_handler.query(db, "DELETE FROM task WHERE id = ?", task_id)
                    print("LOOOOOOOOOOL")
                    db.rollback()

                # Commit changes
                db.commit()

                # Close the connection
                db.close()

                # Show the success flash
                flash("Task successfully created.", "success")
                return redirect("/tasks")
            else:
                return apology("You don't have permission to perform this action.", code=403)

    return render_template("tasks.html")


# TEST TEST TEST #
# Try to use AJAX for the dynamic HTML return
# Called by the JavaScript from the tasks.html
# It only returns the HTML for the create-task
@app.route("/get-create-task")
@login_required
@validate_session
def get_create_task():
    # Check the roles
    session_role_is_admin: bool = session.get("role") == 'admin'

    if session_role_is_admin:
        # Connect to the db
        db = db_handler.db_connect("crowd.db")

        # Query the db for the usernames
        db_users: str = db_handler.query(db, "SELECT username FROM users")
        # Initialize users list
        users: list = []
        # Populate the users list with usernames
        for user in db_users:
            users.append(user['username'])

        # Render the template and return it
        # This sends the HTML back to the JavaScript fetch() call
        return render_template("create-task.html", users=users, color="green")
        db.close()
    else:
        db.close()
        return apology("You don't have permission to perform this action.", code=403)


# AJAX part for the assignment
@app.route("/assignment")
@login_required
@validate_session
def get_assignment_details():
    """Fetch and return HTML for a single assignment."""
    if request.method == "GET":
        if session.get("role") == 'admin':
            # Connect to the db
            db = db_handler.db_connect("crowd.db")

            # Get the info about the task with this id

            # Get the id's
            task_id: int = request.args.get('task_id')
            assignment_id: int = request.args.get('assignment_id')

            # Fetch the db for task
            task: dict = db_handler.query(db, "SELECT * FROM tasks WHERE id = ?", task_id)[0]

            task_id: int = task['id']
            creator_id: int = task['creator_id']
            task_creator_username: str = db_handler.query(db, "SELECT username FROM users WHERE id = ?", creator_id)[0]['username']
            task_type: str = task['task_type']
            task_content: str = task['content']
            gsa: str = task['gold_standard_answer']
            task_creation_timestamp: str = task['creation_timestamp']
            task_deadline: str = task['deadline']
            task_status: str = task['status']

            # Fetch the db for an assignment
            assignment: dict = db_handler.query(db, "SELECT * FROM assignments WHERE id = ?", assignment_id)[0]

            user_id: int = assignment['user_id']
            assigned_to_name: str = db_handler.query(db, "SELECT username FROM users WHERE id = ?", user_id)[0]['username']
            assigned_by_id: int = assignment['assigned_by_id']
            assigned_by_name: str = db_handler.query(db, "SELECT username FROM users WHERE id = ?", assigned_by_id)[0]['username']
            assignment_status: str = assignment['status']
            score: int = assignment['score']
            ai_score: int = assignment['ai_score']
            feedback: str = assignment['feedback']
            assigned_at: str = assignment['assigned_at']

            # Fetch all of the submissions
            submissions_db = db_handler.query(db, "SELECT submitted_answer, timestamp, submitted_by_id FROM submissions WHERE assignment_id = ? ORDER BY timestamp ASC", assignment_id)
            # Convert to a list of dicts
            submissions: list[dict] = []
            for submission in submissions_db:
                submissions.append(dict(submission))
            # Replace the submitted_by_id with the name
            if len(submissions) > 0:
                for submission in submissions:
                    id: int = submission['submitted_by_id']
                    name: str = db_handler.query(db, "SELECT username FROM users WHERE id = ?", id)[0]['username']
                    # Delete the key-value pair from the dict
                    del submission['submitted_by_id']
                    # Create a new one with the name
                    submission['submitted_by_name'] = name

            # Calculate at which time the last submission was made
            last_submission: str = "None"
            if len(submissions) > 0:
                last_submission: str = submissions[-1]['timestamp']

            # Close the connection
            db.close()
            return render_template(
                "assignment.html",
                task_id=task_id,
                assignment_id=assignment_id,
                task_creation_timestamp=task_creation_timestamp,
                last_submission=last_submission,
                assigned_at=assigned_at,
                task_status=task_status,
                assignment_status=assignment_status,
                task_creator_username=task_creator_username,
                task_type=task_type,
                task_deadline=task_deadline,
                task_content=task_content,
                assigned_by_name=assigned_by_name,
                submissions=submissions
            )


# API route to handle the chat messages within assignments
@app.route("/create-submission", methods=["POST"])
@login_required
@validate_session
def create_submission():
    """Handles AJAX request to create a new submission.
    
    Creates the submission, and displays it to the user as the new chat message,
    without reloading the entire page.
    """

    # Expect JSON data, not form date
    if not request.is_json:
        return jsonify(
            {
                "status": "error",
                "message": "Invalid request: missing JSON"
            }
        ), 400
    
    data = request.get_json()

    # Get the data sent by the JavaScript
    assignment_id = data.get('assignment_id')
    submitted_answer = data.get('submitted_answer')

    # Validate the data
    if not assignment_id or not submitted_answer or submitted_answer.strip() == '':
        return jsonify(
            {
                "status": "error",
                "message": "Missing or empty data"
            }
        ), 400

    # Create the submission
    db = db_handler.db_connect("crowd.db")
    try:
        submitted_by_id = session['user_id']

        # Create new submission
        db_handler.query(db, "INSERT INTO submissions (assignment_id, submitted_by_id, submitted_answer) VALUES (?, ?, ?)", assignment_id, submitted_by_id, submitted_answer)

        # Commit changes
        db.commit()

        # Username to send back to the client for message displaying
        submitted_by_name = session['username']

        # Get the timestamp
        timestamp: str = db_handler.query(db, "SELECT timestamp FROM submissions WHERE submitted_by_id == ? AND assignment_id == ? ORDER BY timestamp DESC LIMIT 1", session['user_id'], assignment_id)[0]['timestamp'] 
    except Exception as e:
        # Rollback the changes
        db.rollback()
        print(f"{RED}DATABASE ERROR in /create-submission: {e}{RESET}")
        return jsonify(
            {
                "status": "error",
                "message": "Could not save message to database."
            }
        ), 400
    finally:
        # Close the connection
        db.close()

    # Instead of redirecting, return a JSON response
    # with data JavaScript needs to update the UI
    return jsonify(
        {
            "status": "success",
            "message": "Submission created",
            "new_submission": {
                "submitted_answer": submitted_answer,
                "submitted_by_name": submitted_by_name,
                "timestamp": timestamp
            }
        }
    )


# API route to poll for new messages
@app.route("/get-updates")
@login_required
@validate_session
def get_updates():
    """Handles polling requests from clients to check for new submissions."""
    try:
        # Get assignment_id and the last timestamp the client knows about
        assignment_id = request.args.get('assignment_id')
        last_timestamp = request.args.get('last_timestamp')

        if not assignment_id or not last_timestamp:
            return jsonify(
                {
                    "status": "error",
                    "message": "Missing parameters"
                }
            ), 400
        
        # Connect to the db
        db = db_handler.db_connect("crowd.db", silent=True)

        # Query for submissions newer than the last one the client has
        new_submissions_db = db_handler.query(db, "SELECT submitted_answer, timestamp, submitted_by_id FROM submissions WHERE assignment_id = ? AND timestamp > ? ORDER BY timestamp ASC", assignment_id, last_timestamp, silent=True)

        new_submissions: list = []
        if new_submissions_db:
            for submission in new_submissions_db:
                submission_dict = dict(submission)

                # Get the username for the Id to display it on the client
                user_id: int = submission_dict['submitted_by_id']
                name = db_handler.query(db, "SELECT username FROM users WHERE id = ?", user_id, silent=True)[0]['username']

                submission_dict['submitted_by_name'] = name
                del submission_dict['submitted_by_id']
                new_submissions.append(submission_dict)
    except Exception as e:
        db.rollback()
        print(f"{RED}DATABASE ERROR in /get-updates: {e}{RESET}")
        return jsonify(
            {
                "status": "error",
                "message": "Database error"
            }
        ), 400
    finally:
        db.close()

    return jsonify(
        {
            "status": "success",
            "new_submissions": new_submissions
        }
    )
