# This file explains the database on both a technical and on a conceptual level

# Technical part:

## Users

```
    CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'worker' CHECK(role IN ('worker', 'admin'))
                );
```

#### This table contains users.
- (id) is a column used to identify the user for
login or for assigning a task to them.
- (username) is just a username and can be used for
identification as well.
- (password_hash) is the hash for the user's password,
used for authentication. It is checked against the
password the user inputs during login.
- (role) helps manage rights for certain project
features. For example, if the user is a worker, they
cannot create a new task.

## Tasks

```
    CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL CHECK(task_type IN ('classification', 'ranking', 'code', 'free')),
                content TEXT NOT NULL,
                gold_standard_answer TEXT,
                creation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                deadline DATETIME,
                status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'in_review', 'completed'))
            );
```

#### This table contains tasks.
- (id) is the particular task's identifier, which can be
used to find the task.
- (task_type) classifies tasks by type. It can be used
to measure a worker's performance on tasks of
a specific type.
- (content) is the content of the task.
- (gold_standard_answer) is defined by the admin or
generated automatically by the AI. A worker's assignment
will be compared to the GSA to give
them an AI score.
- (creation_timestamp) is the time when the task
was created.
- (deadline) is the deadline for the task.
- (status) is the status of the task.

## Assignments

```
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
```

#### This table contains an individual worker's assignment to a particular task. A task can have multiple assignments from multiple users.
- (id) is the assignment ID.
- (task_id) is the ID of the assigned task.
- (user_id) is the ID of the assigned user.
- (status) shows the system and sometimes the
worker the status of their assignment. For example, if
the status is 'revision_requested', this means that
the admin wants the worker to add more submissions
(more on that later).
- (score) is the score given by the reviewer upon
closing the task.
- (ai_score) is the score given by the AI reviewer
upon closing the task.
- (feedback) is the feedback from the reviewer upon
closing the task.
- (assigned_at) is the time when the task was assigned
to this particular worker.

## Submissions

```
    CREATE TABLE submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assignment_id INTEGER NOT NULL,
                submitted_answer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assignment_id) REFERENCES assignments (id) ON DELETE CASCADE
            );
```

#### This table contains individual submissions for the assignments (not for the tasks). An assignment is a hub, created for a particular worker, which aggregates all of that worker's submissions. There can be multiple submissions for one assignment.
- (id) is the ID of a particular submission.
- (assignment_id) specifies to which assignment
this submission is related.
- (submitted_answer) is the submission itself.
- (timestamp) is the time of the submission.

## Metrics Cache
    TODO

# Conceptual Part:

The ultimate goal of the system is to crowdsource solutions for particular tasks.
The concept is analogous to a school assignment.

There is a **teacher** (an `admin` user), who provides a problem, and there are **students**
(the `worker` users), who provide the solutions.

## Workflow
- An admin (the "teacher") creates a `task` and sets its deadline.
- The admin then assigns this single `task` to one or more workers ("students").
- This creates an `assignment` for each worker. The `assignment` acts like a 
personal project folder for that specific task. A worker has exactly one `assignment` 
per task they are assigned.
- As workers progress, they submit their work. Each piece of work is a `submission`. 
A worker can make multiple `submissions` to their single `assignment` for a task. 
All of their work for that task is collected within that assignment.
    - From the worker's perspective, this interaction feels like having an individual chat 
or workspace for each task assigned to them.
- At any point, an admin can view every `submission` for every `assignment`.
- Once a worker believes they have finished, they change their assignment's status to 
`awaiting_review`.
- An admin can review the work. If it is incomplete or incorrect, the admin can request 
a `revision_requested`, prompting the worker to make more submissions.
- An admin can **close** an individual worker's `assignment`. This may happen because 
the worker has successfully completed the task, is no longer working on it, or for any 
other reason.
- An admin can also **close** the entire `task`. When this happens, all related 
assignments are automatically closed, and no one can make further submissions. 
At this point, the task is considered `completed`.

## Implementation

#### User Creation

```
# Admin
admin = query(db, "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 'username', 'hash', 'admin')
# Worker
worker = query(db, "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 'username', 'hash', 'worker')
```

#### Task Creation

```
# Task content should be retrieved from the UI in the actual usecase
task_content = "Solve the equasion: 1 + 3 = x + 1."
# Task type
task_type = 'free'
# Gold standart answer (could be specified by admin or generated by the AI if not specified)
gsa = '3'
# Deadline
deadline = datetime(2025, 7, 12, 10, 30, 0)
# Status (is 'open' by default so there is no need to include it into the query)
status = 'open'

task = query(db, "INSERT INTO tasks (task_type, content, gold_standart_answer, deadline) VALUES (?, ?, ?, ?)", task_type, task_content, gsa, deadline)
```

#### Create Assignment

```
# Admin assigns the task to the worker (this creates their project folder)
assignment = query(db, "INSERT INTO assignments (task_id, user_id) VALUES (?, ?)", task_id, alice_id)
```

#### Make Submission

```
# Workers submit their answers (putting papers in folders)
query(db, "INSERT INTO submissions (assignment_id, submitted_answer) VALUES (?, ?)", worker_assignment_id, "The x is 1")

# Now the assignment status should be changed to 'in_progress' or 'awaiting_review' which depends on what the worker has pressed
query(db, "UPDATE assignments SET status = 'in_progress' WHERE id = ?", worker_assignment_id)

# Puts another answer
query(db, "INSERT INTO submissions (assignment_id, submitted_answer) VALUES (?, ?)", worker_assignment_id, "Nevermind, the x is 3")

# Now status should be changed to awaiting_review
query(db, "UPDATE assignments SET status = 'awaiting_review' WHERE id = ?", worker_assignment_id)
```

#### Work Review

```
# Fetch all submittions for worker's assignment (worker_assignment_id)
worker_submissions = query(db, "SELECT submitted_answer, timestamp FROM submissions WHERE assignment_id = ? ORDER BY timestamp ASC", worker_assignment_id, fetch='all')
# View
for sub in worker_submissions:
    print(f"[{sub['timestamp']}] {sub['submitted_answer']}")
```

#### Score And Provide Feedback

```
query(db, "UPDATE assignments SET score = 10, feedback = ?, status = 'closed' WHERE id = ?", "Excellent work", worker_assignment_id)
```
