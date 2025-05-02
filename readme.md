# Initial project plan

Build an application, which purpose in life is to create/manage/evaluate tasks.
This is should be a mix of the crowdsourcing apps, used for the data classification (labeling data for the nerual networks) and the team management ticket systems,
used in IT.

## Target workflow:
- Different roles within the system (Admin/Worker).
- Tasks have different types (e.g. code, classification, transcription)
- Admins create tasks and assign workers to them.
- Admins review submitted tasks, score them, then close the tasks or assign a different worker to them (or the task choose the worker automatically).
- Admins can view the task performance of the team/particular worker on each type of tasks via Dashboard and different charts.
- An AI is integrated into the system, it provides it's own metric on the submitted task (ai evaluates the ai_score based on the golden standart answer).
- Inter-Annotator Agreement (Cohen's/Fleiss' Kappa) is implemented for the tasks completed by multiple workers.
- Task troughput is calculated to measure the overall performance of the team.
- Workers have their own scores on each type of the tasks.
- All of the metrics are cached and calculated only on Admin's demand for the performance reasons.
- Workers have their history of the submitted tasks and their score.

## Technologies

- Python Flask for the UI.
- SQLite3 for the db.
- AI API's for the project's AI features.
