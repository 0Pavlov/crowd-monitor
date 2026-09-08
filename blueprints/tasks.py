from flask import Blueprint, render_template, request, session, redirect, flash, jsonify
import re
from model import db_handler
from helpers import login_required, validate_session, format_sqlite_datetime, apology, RED, RESET
from ai_service import ai_get_answer

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/tasks", methods=["GET", "POST"])
@login_required
@validate_session
def tasks():
    """Tasks"""
    if request.method == "GET":
        if session.get("role") == 'admin':
            db = db_handler.db_connect("crowd.db")
            table_info = db_handler.query(db, "PRAGMA table_info(tasks)")
            column_names = [info[1] for info in table_info]
            tasks = db_handler.query(db, "SELECT * FROM tasks ORDER BY creation_timestamp DESC")
            tasks: list[dict] = [dict(zip(column_names, row)) for row in tasks]
            assignments_info: dict[dict] = {}

            for task in tasks:
                assignments_ids_from_db: list = db_handler.query(db, "SELECT id FROM assignments WHERE task_id = ?", task['id'])
                assignments_ids: list = []
                for assigned_id in assignments_ids_from_db:
                    assignments_ids.append(assigned_id['id'])
                    temp_assignment: dict = dict(db_handler.query(db, "SELECT * FROM assignments WHERE id = ?", assigned_id['id'])[0])
                    try:
                        last_submission: str = db_handler.query(db, "SELECT submitted_answer FROM submissions WHERE assignment_id = ? ORDER BY timestamp DESC LIMIT 1", assigned_id['id'])[0]['submitted_answer']
                        temp_assignment['last_submission'] = last_submission
                    except:
                        temp_assignment['last_submission'] = 'No sumbissions yet'
                    
                    worker_username: str = db_handler.query(db, "SELECT u.username FROM users u JOIN assignments a ON u.id = a.user_id WHERE a.id = ?", assigned_id['id'])[0]['username']
                    temp_assignment['assigned_worker'] = worker_username
                    try:
                        who_submitted: str = db_handler.query(db, "SELECT u.username FROM users u JOIN submissions a ON u.id = a.submitted_by_id WHERE assignment_id = ? ORDER BY timestamp DESC LIMIT 1", assigned_id['id'])[0]['username']
                    except:
                        who_submitted = "Error"
                    temp_assignment['who_last_submitted'] = who_submitted
                    assignments_info[assigned_id['id']] = temp_assignment
                task['assignments_ids'] = assignments_ids

            for task in tasks:
                task['creation_timestamp'] = format_sqlite_datetime(task['creation_timestamp'])
                task['deadline'] = format_sqlite_datetime(task['deadline'])

            db.close()
            return render_template("/tasks/tasks.html", tasks=tasks, assignments_info=assignments_info)
            
        elif session.get("role") == 'worker':
            db = db_handler.db_connect("crowd.db")
            table_info = db_handler.query(db, "PRAGMA table_info(tasks)")
            column_names = [info[1] for info in table_info]
            tasks = db_handler.query(db, "SELECT * FROM tasks WHERE id IN (SELECT task_id FROM assignments WHERE user_id = ?) ORDER BY creation_timestamp DESC", session.get("user_id"))
            tasks: list[dict] = [dict(zip(column_names, row)) for row in tasks]
            assignments_info: dict[dict] = {}

            for task in tasks:
                assignments_ids_from_db: list = db_handler.query(db, "SELECT id FROM assignments WHERE task_id = ? and user_id = ?", task['id'], session.get("user_id"))
                assignments_ids: list = []
                for assigned_id in assignments_ids_from_db:
                    assignments_ids.append(assigned_id['id'])
                    temp_assignment: dict = dict(db_handler.query(db, "SELECT * FROM assignments WHERE id = ?", assigned_id['id'])[0])
                    try:
                        last_submission: str = db_handler.query(db, "SELECT submitted_answer FROM submissions WHERE assignment_id = ? ORDER BY timestamp DESC LIMIT 1", assigned_id['id'])[0]['submitted_answer']
                        temp_assignment['last_submission'] = last_submission
                    except:
                        temp_assignment['last_submission'] = 'No sumbissions yet'
                        
                    worker_username: str = db_handler.query(db, "SELECT u.username FROM users u JOIN assignments a ON u.id = a.user_id WHERE a.id = ?", assigned_id['id'])[0]['username']
                    temp_assignment['assigned_worker'] = worker_username
                    try:
                        who_submitted: str = db_handler.query(db, "SELECT u.username FROM users u JOIN submissions a ON u.id = a.submitted_by_id WHERE assignment_id = ? ORDER BY timestamp DESC LIMIT 1", assigned_id['id'])[0]['username']
                    except:
                        who_submitted = "Error"
                    temp_assignment['who_last_submitted'] = who_submitted
                    assignments_info[assigned_id['id']] = temp_assignment
                task['assignments_ids'] = assignments_ids

            for task in tasks:
                task['creation_timestamp'] = format_sqlite_datetime(task['creation_timestamp'])
                task['deadline'] = format_sqlite_datetime(task['deadline'])

            db.close()
            return render_template("/tasks/tasks.html", tasks=tasks, assignments_info=assignments_info)

    if request.method == "POST":
        if request.form.get("task_creation_form") == "create_task":
            session_role_is_admin: bool = session.get("role") == 'admin'
            if session_role_is_admin:
                content: str = request.form.get('content')
                task_type: str = request.form.get('task_type')
                gsa: str = request.form.get('gsa')
                deadline = request.form.get('deadline')
                worker: str = request.form.get('worker')

                if not content or content.strip() == '':
                    flash("The content field is empty.", "danger")
                    return redirect("/tasks")
                if not gsa or gsa.strip() == '':
                    flash("The gsa isn't specified.", "danger")
                    return redirect("/tasks")
                if not task_type or task_type.strip() == '':
                    flash("The task type isn't specified.", "danger")
                    return redirect("/tasks")
                if not worker or worker.strip() == '':
                    flash("The worker isn't specified.", "danger")
                    return redirect("/tasks")
                if not deadline or deadline.strip() == '':
                    flash("The deadline isn't specified.", "danger")
                    return redirect("/tasks")

                task_type = task_type.lower()
                deadline = deadline.replace('T', ' ') + ':00'
                db = db_handler.db_connect("crowd.db")
                creator_id: int = session['user_id']
                worker_id: int = db_handler.query(db, "SELECT id FROM users WHERE username = ?", worker)[0]['id']

                try:
                    db_handler.query(db, "INSERT INTO tasks (creator_id, task_type, content, gold_standard_answer, deadline) VALUES (?, ?, ?, ?, ?)", creator_id, task_type, content, gsa, deadline)
                except:
                    db.rollback()

                task_id = db_handler.query(db, "SELECT id FROM tasks WHERE (content == ? AND creator_id == ?)", content, creator_id)[0]['id']
                
                try:
                    db_handler.query(db, "INSERT INTO assignments (task_id, user_id, assigned_by_id) VALUES (?, ?, ?)", task_id, worker_id, creator_id)
                except:
                    # FIX: Corrected typo 'task' to 'tasks' table
                    db_handler.query(db, "DELETE FROM tasks WHERE id = ?", task_id)
                    db.rollback()

                db.commit()
                db.close()
                flash("Task successfully created.", "success")
                return redirect("/tasks")
            else:
                return apology("You don't have permission to perform this action.", code=403)

    return render_template("/tasks/tasks.html")

@tasks_bp.route("/get-create-task")
@login_required
@validate_session
def get_create_task():
    session_role_is_admin: bool = session.get("role") == 'admin'
    if session_role_is_admin:
        db = db_handler.db_connect("crowd.db")
        db_users = db_handler.query(db, "SELECT username FROM users")
        users: list = [user['username'] for user in db_users]
        db.close()
        return render_template("/tasks/create-task.html", users=users, color="green")
    else:
        return apology("You don't have permission to perform this action.", code=403)

@tasks_bp.route("/assignment")
@login_required
@validate_session
def get_assignment_details():
    if request.method == "GET":
        db = db_handler.db_connect("crowd.db")
        task_id: int = request.args.get('task_id')
        assignment_id: int = request.args.get('assignment_id')
        
        task: dict = db_handler.query(db, "SELECT * FROM tasks WHERE id = ?", task_id)[0]
        creator_id: int = task['creator_id']
        task_creator_username: str = db_handler.query(db, "SELECT username FROM users WHERE id = ?", creator_id)[0]['username']
        task_type: str = task['task_type']
        task_content: str = task['content']
        gsa: str = task['gold_standard_answer']
        task_creation_timestamp: str = format_sqlite_datetime(task['creation_timestamp'])
        task_deadline: str = format_sqlite_datetime(task['deadline'])
        task_status: str = task['status']

        assignment: dict = db_handler.query(db, "SELECT * FROM assignments WHERE id = ?", assignment_id)[0]
        user_id: int = assignment['user_id']
        assigned_by_id: int = assignment['assigned_by_id']
        assigned_by_name: str = db_handler.query(db, "SELECT username FROM users WHERE id = ?", assigned_by_id)[0]['username']
        assignment_status: str = assignment['status']
        score = assignment['score']
        ai_score = assignment['ai_score']
        feedback = assignment['feedback']
        assigned_at: str = format_sqlite_datetime(assignment['assigned_at'])

        submissions_db = db_handler.query(db, "SELECT submitted_answer, timestamp, submitted_by_id FROM submissions WHERE assignment_id = ? ORDER BY timestamp ASC", assignment_id)
        submissions: list[dict] = []
        for submission in submissions_db:
            sub_dict = dict(submission)
            uid: int = sub_dict['submitted_by_id']
            sub_dict['submitted_by_name'] = db_handler.query(db, "SELECT username FROM users WHERE id = ?", uid)[0]['username']
            del sub_dict['submitted_by_id']
            sub_dict['formatted_timestamp'] = format_sqlite_datetime(sub_dict['timestamp'])
            submissions.append(sub_dict)

        last_submission_formatted: str = "None"
        if len(submissions) > 0:
            last_submission_formatted = submissions[-1]['formatted_timestamp']

        db.close()
        return render_template(
            "/tasks/assignment.html",
            task_id=task_id,
            assignment_id=assignment_id,
            task_creation_timestamp=task_creation_timestamp,
            last_submission=last_submission_formatted,
            assigned_at=assigned_at,
            task_status=task_status,
            assignment_status=assignment_status,
            task_creator_username=task_creator_username,
            task_type=task_type,
            task_deadline=task_deadline,
            task_content=task_content,
            assigned_by_name=assigned_by_name,
            submissions=submissions,
            current_username=session.get('username'),
            score=score,
            ai_score=ai_score,
            feedback=feedback
        )

@tasks_bp.route("/create-submission", methods=["POST"])
@login_required
@validate_session
def create_submission():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Invalid request: missing JSON"}), 400
    
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    submitted_answer = data.get('submitted_answer')

    if not assignment_id or not submitted_answer or submitted_answer.strip() == '':
        return jsonify({"status": "error", "message": "Missing or empty data"}), 400

    db = db_handler.db_connect("crowd.db")
    is_closed = False
    try:
        submitted_by_id = session['user_id']
        is_closed = db_handler.query(db, "SELECT status FROM assignments WHERE id = ?", assignment_id)[0]['status'] == 'closed'

        if not is_closed:
            db_handler.query(db, "INSERT INTO submissions (assignment_id, submitted_by_id, submitted_answer) VALUES (?, ?, ?)", assignment_id, submitted_by_id, submitted_answer)
            db.commit()
            submitted_by_name = session['username']
            timestamp: str = db_handler.query(db, "SELECT timestamp FROM submissions WHERE submitted_by_id == ? AND assignment_id == ? ORDER BY timestamp DESC LIMIT 1", session['user_id'], assignment_id)[0]['timestamp'] 
            formatted_timestamp = format_sqlite_datetime(timestamp)
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": "Could not save message to database."}), 400
    finally:
        db.close()

    if is_closed:
        return jsonify({"status": "error", "message": "Assignment is closed."}), 400

    return jsonify({
        "status": "success",
        "message": "Submission created",
        "new_submission": {
            "submitted_answer": submitted_answer,
            "submitted_by_name": submitted_by_name,
            "timestamp": timestamp,
            "formatted_timestamp": formatted_timestamp
        }
    })

@tasks_bp.route("/get-updates")
@login_required
@validate_session
def get_updates():
    try:
        assignment_id = request.args.get('assignment_id')
        last_timestamp = request.args.get('last_timestamp')

        if not assignment_id or not last_timestamp:
            return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
        db = db_handler.db_connect("crowd.db", silent=True)
        assignment_is_closed: bool = db_handler.query(db, "SELECT status FROM assignments WHERE id = ?", assignment_id)[0]['status'] == 'closed'
        assignment_is_closed = "closed" if assignment_is_closed else "not_closed"

        new_submissions_db = db_handler.query(db, "SELECT submitted_answer, timestamp, submitted_by_id FROM submissions WHERE assignment_id = ? AND timestamp > ? ORDER BY timestamp ASC", assignment_id, last_timestamp, silent=True)

        new_submissions: list = []
        if new_submissions_db:
            for submission in new_submissions_db:
                submission_dict = dict(submission)
                user_id: int = submission_dict['submitted_by_id']
                name = db_handler.query(db, "SELECT username FROM users WHERE id = ?", user_id, silent=True)[0]['username']
                submission_dict['submitted_by_name'] = name
                del submission_dict['submitted_by_id']
                submission_dict['formatted_timestamp'] = format_sqlite_datetime(submission_dict['timestamp'])
                new_submissions.append(submission_dict)
        db.close()
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": "Database error"}), 400

    return jsonify({
        "status": "success",
        "new_submissions": new_submissions,
        "assignment_status": assignment_is_closed
    })

@tasks_bp.route('/close-task', methods=['POST'])
@login_required
@validate_session
def close_task():
    if request.is_json and session['role'] == 'admin':
        data = request.get_json()
        task_id = data.get('task_id')
        db = db_handler.db_connect("crowd.db")
        try:
            status_data = db_handler.query(db, "SELECT status FROM tasks WHERE id = ?", task_id)
            if not status_data or status_data[0]['status'] == 'closed':
                return jsonify({'status': 'success', 'message': 'Task already closed'})

            db_handler.query(db, "UPDATE tasks SET status = 'closed' WHERE id = ?", task_id)
            
            task_info = db_handler.query(db, "SELECT content, gold_standard_answer FROM tasks WHERE id = ?", task_id)[0]
            task_content = task_info['content']
            gsa = task_info['gold_standard_answer']
            
            assignments = db_handler.query(db, "SELECT id FROM assignments WHERE task_id = ?", task_id)

            for asn in assignments:
                asn_id = asn['id']
                db_handler.query(db, "UPDATE assignments SET status = 'closed' WHERE id = ?", asn_id)

                submissions = db_handler.query(db, "SELECT submitted_answer FROM submissions WHERE assignment_id = ? ORDER BY timestamp ASC", asn_id)
                if submissions:
                    final_answer = submissions[-1]['submitted_answer']
                    prompt = f"Task: {task_content}\nGold Standard Answer: {gsa}\nUser Answer: {final_answer}\nEvaluate the user answer out of 10 based on the Gold Standard Answer."
                    system_prompt = "You are a strict grading assistant. Only output a single integer representing the score out of 10. Do not include any other text."
                    score_str = ai_get_answer(prompt, system_prompt)
                    try:
                        match = re.search(r'\d+', str(score_str))
                        ai_score = min(10, max(0, int(match.group()))) if match else 0
                    except Exception:
                        ai_score = 0
                else:
                    ai_score = 0
                
                db_handler.query(db, "UPDATE assignments SET ai_score = ? WHERE id = ?", ai_score, asn_id)

            db.commit()
        except Exception as e:
            db.rollback()
            return jsonify({"status": "error", "message": "Database error"}), 400
        finally:
            db.close()
        return jsonify({'status':'success', 'message': f'Task {task_id} closed and scored by AI'})
    else:
        return jsonify({'status': 'error', 'message': 'request not json or unauthorized'}), 400

@tasks_bp.route("/dashboard")
@login_required
@validate_session
def dashboard():
    return render_template("dashboard.html")

@tasks_bp.route("/review")
@login_required
@validate_session
def review():
    return render_template("review.html")
