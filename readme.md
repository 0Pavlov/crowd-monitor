# How to use

* **Clone:**
```bash
git clone "https://github.com/0Pavlov/crowd-monitor/
```
* **CD:**
```bash
cd crowd-monitor
```
* **Venv:**
```bash
python -m venv venv
```
* **Activate:**
```bash
platform specific (research)
```
* **Dependencies:**
```bash
pip install -r requirements.txt
```
* **Run:**
```bash
Flask run
```
* **Open:** Open the link in the browser and register a new user.
* **Rights:** In the /model/ folder there is a script
```bash
python change_role.py name admin\worker
```

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

## Technologies:

- Python Flask for the UI.
- SQLite3 for the db.
- AI API's for the project's AI features.


### 📌 Project Update (08.09.2026)

I am making this repository public today. While I have decided to pivot to a new tech stack, I am wrapping this project up to serve as a portfolio piece.

* **The Journey:** Building this app taught me a lot about Flask routing, templating, authentication, databases, polling, responsive UI, JavaScript, and building custom modules and tools.
* **The Pivot:** At some point, I reached the limits of vanilla CSS and JavaScript for the frontend (or at least it became unreasonable to continue scaling with this stack). I then discovered modern frontend frameworks like Svelte and backend frameworks like FastAPI. I've decided to focus my learning there, meaning active development on this version is ending.
* **AI Assistance:** All of the core backend logic in this project was handwritten by me prior to this date. Moving forward from today, any final commits (mostly UI polishing and chat improvements) will be heavily assisted by AI to help me quickly reach a "finished" state.
