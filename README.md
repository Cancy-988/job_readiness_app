# Skillify

Skillify is a student skill analyzer and career readiness platform built with Flask, Jinja templates, SQLite/PostgreSQL support, and a Logistic Regression machine learning model. It helps students assess technical skills, track performance, generate learning guidance, and predict whether they are job-ready.

## Live Demo

Production link: [https://skillify-yjbs.onrender.com/](https://skillify-yjbs.onrender.com/)

## Project Overview

This application combines quiz-based evaluation, student profile management, analytics dashboards, and ML-based readiness prediction in a single Flask web app. The backend renders templates directly, stores user and quiz data in a database, and uses a saved model file to predict job readiness from quiz scores.

## Key Features

- Secure student signup and login
- Student profile with branch, projects, internships, skills, and confidence level
- Branch-based quizzes for aptitude, DSA, DBMS, and OS
- Category-wise quiz result summary
- Analytics dashboard with score history and performance insights
- Personalized learning path based on weak areas
- Job readiness prediction using a trained machine learning model
- Optional PostgreSQL support for production deployments
- Optional Cloudinary support for profile image uploads

## Architecture

Skillify uses a simple server-rendered architecture:

1. The browser opens the Flask app and requests a page.
2. Flask routes in [app.py](app.py) validate the session and load data.
3. Jinja templates in [templates/](templates) render the UI.
4. Quiz results, profile details, and user records are stored in the database.
5. The saved model in [job_ready_model.pkl](job_ready_model.pkl) predicts job readiness.
6. Static assets in [static/](static) handle styling, scripts, images, and uploads.

### Main application flow

- User signs up or logs in
- Student fills profile information
- Quiz sections are unlocked based on branch
- Quiz answers are submitted and stored
- Analytics page shows progress and insights
- Machine learning model predicts readiness
- Learning path suggests what to improve next

### Backend design

- Flask handles routing, session management, and page rendering
- SQLite is used locally
- PostgreSQL is supported when `DATABASE_URL` is present
- Cloudinary is used when profile upload credentials are configured
- Gunicorn runs the app in production through [Procfile](Procfile)

## Technology Stack

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2 templates

### Backend

- Python
- Flask
- Gunicorn

### Database

- SQLite for local development
- PostgreSQL for production support

### Machine Learning

- Pandas
- NumPy
- Scikit-learn
- Pickle

### Storage and Media

- Cloudinary for profile images

## Repository Structure

- [app.py](app.py) - Main Flask application
- [init_db.py](init_db.py) - Database initialization script
- [train_model.py](train_model.py) - Model training script
- [job_ready_model.pkl](job_ready_model.pkl) - Trained ML model
- [data/](data) - Questions and dataset files
- [templates/](templates) - HTML templates
- [static/](static) - CSS, JavaScript, images, and uploads
- [requirements.txt](requirements.txt) - Python dependencies
- [Procfile](Procfile) - Production start command

## Database Tables

The app manages these core tables:

- `users` - student account details and profile data
- `student_details` - branch, projects, internships, skills, and confidence
- `quiz_results` - quiz score history
- `admin_users` - admin accounts

## Machine Learning Pipeline

The readiness model is trained with synthetic student performance data using Logistic Regression.

Input features:

- Aptitude score
- DSA score
- DBMS score
- OS score

Output:

- Job ready: Yes / No

The trained estimator is saved as [job_ready_model.pkl](job_ready_model.pkl) and loaded by the Flask app at runtime.

## Local Development Setup

1. Clone the repository.
2. Create a virtual environment.
3. Install dependencies.
4. Initialize the database.
5. Run the Flask app.

### Example commands

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
```

## Environment Variables

For production, configure these variables:

- `SECRET_KEY` - Flask session secret
- `DATABASE_URL` - PostgreSQL connection string
- `CLOUDINARY_CLOUD_NAME` - Cloudinary account name
- `CLOUDINARY_API_KEY` - Cloudinary API key
- `CLOUDINARY_API_SECRET` - Cloudinary API secret

If `DATABASE_URL` is not set, the app falls back to local SQLite.

## Deployment Notes

This project is deployed as a Flask web service on Render.

Production start command:

```bash
gunicorn app:app
```

Recommended Render settings:

- Service type: Web Service
- Environment: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

Important note for the free Render tier:

- Free services sleep after inactivity
- The first request after idle may take about a minute to wake up
- Render free filesystem storage is ephemeral, so local uploads and local SQLite data should not be treated as permanent production storage

## Features in Production

- Student authentication
- Profile management
- Quiz flow
- Results storage
- Analytics dashboard
- Learning path generation
- ML-based readiness prediction

## Future Improvements

- Resume parsing with NLP
- Internship and job recommendations
- More advanced ML models such as Random Forest or XGBoost
- Better dashboard visualizations
- Stronger mobile responsiveness
- Gamification features like badges and levels

## Author

Cancy Khandelwal

B.Tech CSE (Data Science)

## Acknowledgement

This project was developed as part of a B.Tech final year curriculum to demonstrate full-stack development, analytics, and machine learning integration in a student career readiness platform.
