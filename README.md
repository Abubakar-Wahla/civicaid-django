# CivicAid (Django)

A civic help platform: requests → volunteer claim → timeline updates → completed impact.

## Features
- HelpRequest workflow: OPEN → IN_PROGRESS → COMPLETED
- Claim / complete (owner cannot claim/complete own request)
- Timeline updates with permissions
- Search / filter / pagination
- Volunteer profiles + directory + matching volunteers on request detail
- Impact page for completed outcomes
- Premium UI (custom CSS)

## Tech
Django 5.2.10, SQLite (dev), Postgres (prod), WhiteNoise, Gunicorn

## Local Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
