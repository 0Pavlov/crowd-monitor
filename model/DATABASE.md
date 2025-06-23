# This file explains the database both on technical and on a conceptional level

# Technical part

    ## Users

    CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'worker' CHECK(role IN ('worker', 'admin'))
                );

    This table contains users
        - (id) column is used to identify the user for the
        login, or for assigning a task to them.
        - (username) just a username, can be used for
        identification as well.
        - (password_hash) the hash for the user password,
        used for autentification, checked against the
        password user inputs during the login.
        - (role) helps manage rights for sertain project
        features, for example if the user is worker, they
        cannot create a new task.

    ## Tasks

    CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL CHECK(task_type IN ('classification', 'ranking', 'code', 'free')),
                content TEXT NOT NULL,
                gold_standard_answer TEXT,
                creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                deadline DATETIME,
                status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'in_review', 'completed'))
            );

    This table contains tasks
        - (id) is the particular task's identifier, can be
        used to find the task.
        - (task_type) classifies tasks by type, can be used
        to measure worker's performance on the tasks with
        the specific type.
        - (content) is the content of the task.
        - (gold_standard_answer) is defined by the admin or
        generated automatically by the AI. Worker's assignment
        would be later compared to the gsa in order to give
        them an AI score.
        - (creation_timestamp) is the time when the task
        was created.
        - (deadline) is the deadline of the task.
        - (status) is the status of the task.

    ## Assignments

    CREATE TABLE assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'assigned' CHECK(status IN ('assigned', 'in_progress', 'awaiting_review', 'revision_requested', 'closed')),
                score INTEGER,
                ai_score INTEGER,
                feedback TEXT,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE (task_id, user_id)
                );

    This table contains individual worker's assignment to a
    particular task. There is only one task, but there is
    multiple assignments to this task from multiple users.
        - (id) assignment id.
        - (task_id) assignment to which task.
        - (user_id) assignment from who.
        - (status) shows to the system and sometimes to the
        worker the status of their assignment. For example if
        the status is 'revision_requested' this means that
        the admin wants the worker to add more submissions
        (more on that later).
        - (score) is the score given by the reviewer upon
        closing the task.
        - (ai_score) is the score given by the AI reviewer
        upon closing the task.
        - (feedback) is the feedback from the reviewer upon
        closing the task.
        - (assigned_at) is the time when the task is assigned
        to this particular worker.

    ## Submissions

    CREATE TABLE submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                submitted_answer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id) ON DELETE CASCADE
            );

    This table contains individual submissions to the
    assignments (not for the tasks). Assignment is the
    hub, created for particular worker, which agregates 
    all of the worker's submissions. There is can be
    multiple submissions for the one assignment.
        - (id) is particular submission id.
        - (assignment_id) specifies to which assignment
        this submission is related.
        - (submitted_answer) is the submittion itself.
        - (timestamp) is the time of the submittion.

    ## Metrics Cache
    TODO

# Conceptional part
TODO
