from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import json
import pickle
import random
from werkzeug.utils import secure_filename

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:
    cloudinary = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass



app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key_change_me")
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)

CLOUDINARY_ENABLED = all([
    os.getenv("CLOUDINARY_CLOUD_NAME"),
    os.getenv("CLOUDINARY_API_KEY"),
    os.getenv("CLOUDINARY_API_SECRET"),
]) and cloudinary is not None

if CLOUDINARY_ENABLED:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

model = pickle.load(open("job_ready_model.pkl", "rb"))

def get_db_connection(db_path="data/users.db"):
    """Get database connection for Postgres in production and SQLite locally."""
    if USE_POSTGRES:
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary is required when DATABASE_URL is set.")
        conn = psycopg2.connect(DATABASE_URL)
        return conn

    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def db_execute(cursor, query, params=()):
    if USE_POSTGRES:
        query = query.replace("?", "%s")
    cursor.execute(query, params)


def build_profile_pic_url(profile_pic_value):
    if not profile_pic_value:
        return None

    if profile_pic_value.startswith("http://") or profile_pic_value.startswith("https://"):
        return profile_pic_value

    return url_for("static", filename=f"uploads/{profile_pic_value}")

def load_questions():
    with open("data/questions.json", "r") as file:
        questions = json.load(file)
    return questions

BRANCH_CATEGORIES = {
    "CSE": ["aptitude", "dsa", "dbms", "os"],
    "OTHER": ["aptitude"] 
}


@app.route("/")
def home():
    """Main landing page for Skillify"""
    return render_template("home.html")

@app.route("/home")
def home_page():
    """Alias for the home page"""
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
       


        conn = get_db_connection()
        cursor = conn.cursor()

        db_execute(cursor, "SELECT name, password FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            message = "Email not found."
            return render_template("login.html", message=message)

        elif user[1] != password:
            message = "Incorrect password."
            return render_template("login.html", message=message)
        

        session.clear()
        session["user_name"] = user[0]
        session["user_email"] = email
        return redirect("/dashboard")

    return render_template("login.html", message=message)



@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        db_execute(cursor, "SELECT * FROM users WHERE email=?", (email,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            message = "Email already exists. Please use another email or login."
            return render_template("signup.html", message=message)

        db_execute(cursor, "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
               (name, email, password))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html", message=message)

@app.route("/dashboard")
def dashboard():
    if "user_name" not in session:
        return redirect("/login")
    
    return render_template("dashboard.html", name=session["user_name"])


@app.route("/form", methods=["GET", "POST"])
def student():
    if "user_name" not in session:
        return redirect("/login")

    if request.method == "POST":
        branch = request.form["branch"]
        projects = request.form["projects"]
        internships = request.form["internships"]
        skills = request.form["skills"]
        confidence = request.form["confidence"]

        email = session.get("user_email")

        conn = get_db_connection()
        cursor = conn.cursor()

        db_execute(cursor, "INSERT INTO student_details (user_email, branch, projects, internships, skills, confidence) VALUES (?, ?, ?, ?, ?, ?)",
               (email, branch, projects, internships, skills, confidence))

        conn.commit()
        conn.close()

   
        return redirect("/quiz_sections")

    return render_template("form.html")
@app.route("/quiz/<category>", methods=["GET", "POST"])
def quiz_category(category):
    if "user_name" not in session:
        return redirect("/login")

    all_questions = load_questions()

    if category not in all_questions:
        return "Quiz category not found!"

    if request.method == "POST":
        # Get the questions that were shown to the user from session
        quiz_questions = session.get("current_quiz_questions", [])
        answers = []
        for i in range(1, len(quiz_questions) + 1):
            user_ans = request.form.get(f"q{i}")
            answers.append(user_ans)

        session["quiz_answers"] = answers
        session["quiz_category"] = category

        return redirect("/results")

    # Randomly select 5 questions from the pool for this quiz attempt
    question_pool = all_questions[category]
    quiz_questions = random.sample(question_pool, min(5, len(question_pool)))
    
    # Store selected questions in session for answer verification
    session["current_quiz_questions"] = quiz_questions
    
    return render_template("quiz.html", questions=quiz_questions, category=category)




@app.route("/profile")
def profile():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        db_execute(cursor, "SELECT name, email, profile_pic FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        db_execute(cursor, "SELECT branch, projects, internships, skills, confidence FROM student_details WHERE user_email=?", (email,))
        details = cursor.fetchone()
    finally:
        if conn:
            conn.close()

    profile_pic_url = build_profile_pic_url(user[2]) if user else None
    return render_template("profile.html", user=user, details=details, profile_pic_url=profile_pic_url)


@app.route("/edit_profile", methods=["GET"])
def edit_profile():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        db_execute(cursor, "SELECT name, email, profile_pic FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        db_execute(cursor, "SELECT branch, projects, internships, skills, confidence FROM student_details WHERE user_email=?", (email,))
        details = cursor.fetchone()
    finally:
        if conn:
            conn.close()

    profile_pic_url = build_profile_pic_url(user[2]) if user else None
    return render_template("edit_profile.html", user=user, details=details, profile_pic_url=profile_pic_url)

@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]
    name = request.form["name"]
    branch = request.form["branch"]
    skills = request.form["skills"]
    projects = request.form["projects"]
    internships = request.form["internships"]
    confidence = request.form["confidence"]

    file = request.files.get("profile_pic")
    profile_pic_value = None

    if file and file.filename:
        if CLOUDINARY_ENABLED:
            upload_result = cloudinary.uploader.upload(
                file,
                folder="skillify/profile_pics",
                public_id=email.replace("@", "_").replace(".", "_"),
                overwrite=True,
                resource_type="image",
            )
            profile_pic_value = upload_result.get("secure_url")
        else:
            ext = file.filename.rsplit(".", 1)[-1]
            safe_email = secure_filename(email.replace("@", "_"))
            filename = f"{safe_email}.{ext}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            profile_pic_value = filename

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if profile_pic_value:
            db_execute(cursor, "UPDATE users SET name=?, profile_pic=? WHERE email=?", (name, profile_pic_value, email))
        else:
            db_execute(cursor, "UPDATE users SET name=? WHERE email=?", (name, email))

        db_execute(cursor, "UPDATE student_details SET branch=?, skills=?, projects=?, internships=?, confidence=? WHERE user_email=?", (branch, skills, projects, internships, confidence, email))

        conn.commit()
    finally:
        if conn:
            conn.close()

    session["user_name"] = name

    return redirect("/profile")

@app.route("/quiz_sections")
def quiz_sections():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]

    conn = get_db_connection()
    cursor = conn.cursor()

    db_execute(cursor,
        "SELECT branch FROM student_details WHERE user_email=? ORDER BY id DESC LIMIT 1",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        branch = row[0].strip().upper()
    else:
        branch = "OTHER"

    categories = BRANCH_CATEGORIES.get(branch, ["aptitude"])

    return render_template(
        "quiz_sections.html",
        categories=categories,
        branch=branch.title()
    )



from datetime import datetime
@app.route("/submit_quiz/<category>", methods=["GET", "POST"])
def submit_quiz(category):
    if request.method == "GET":
        return redirect(f"/quiz/{category}")
    
    # Get the randomly selected questions from session (not all questions)
    questions = session.get("current_quiz_questions", [])
    if not questions:
        # Fallback in case session expired
        return redirect(f"/quiz/{category}")
    
    score = 0

    for i, q in enumerate(questions, start=1):
        user_ans = request.form.get(f"q{i}")
        if user_ans == q["answer"]:
            score += 1

    total = len(questions)

   
    conn = get_db_connection()
    cursor = conn.cursor()

    db_execute(cursor, """
        INSERT INTO quiz_results (user_email, category, score, total, taken_on)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session["user_email"],
        category,
        score,
        total,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    

    conn = get_db_connection()
    cursor = conn.cursor()

    db_execute(cursor, """
        SELECT category, score FROM quiz_results 
        WHERE user_email=?
    """, (session["user_email"],))

    all_scores = cursor.fetchall()
    conn.close()

    score_map = {"aptitude": 0, "dsa": 0, "dbms": 0, "os": 0}
    for cat, s in all_scores:
        score_map[cat] = s

    import pandas as pd
    X_test = pd.DataFrame([[
        score_map["aptitude"],
        score_map["dsa"],
        score_map["dbms"],
        score_map["os"]
    ]])

    prediction = model.predict(X_test)[0]  

    session["job_ready_prediction"] = int(prediction)
    
                                          

    
    session["quiz_score"] = score
    session["quiz_category"] = category

    return redirect("/results")


def generate_insight(scores, categories):
    if not scores:
        return "No quiz taken yet."

    from collections import defaultdict

   
    cat_scores = defaultdict(list)

    for cat, score in zip(categories, scores):
        cat_scores[cat].append(score)


    avg_scores = {}
    for cat in cat_scores:
        avg_scores[cat] = sum(cat_scores[cat]) / len(cat_scores[cat])

    if len(avg_scores) == 1:
        only_skill = list(avg_scores.keys())[0].upper()
        return f"Your performance in **{only_skill}** is consistent. Try attempting more quizzes for deeper insights."

    
    sorted_skills = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)

    strong_skills = [sorted_skills[0][0].upper()]
    weak_skills = [sorted_skills[-1][0].upper()]

    insight = (
        f"🌟 Your strongest skill is  {strong_skills[0]}.\n\n"
        f"⚠️ You need to improve your  {weak_skills[0]} skill.\n\n"
        "🎯 **Recommended Actions:**\n"
    )

    if "APTITUDE" in weak_skills:
        insight += "• Practice aptitude daily using IndiaBix or PrepInsta.\n"

    if "DSA" in weak_skills:
        insight += "• Solve 1–2 DSA problems daily on LeetCode.\n"

    if "DBMS" in weak_skills:
        insight += "• Revise SQL queries, joins, and normalization.\n"

    if "OS" in weak_skills:
        insight += "• Focus on CPU scheduling, deadlocks, and memory management.\n"

    return insight


@app.route("/results")
def results():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]

    conn = get_db_connection()
    cursor = conn.cursor()

    db_execute(cursor, """
        SELECT category, score, total, taken_on 
        FROM quiz_results 
        WHERE user_email=? 
        ORDER BY taken_on DESC
    """, (email,))
    
    records = cursor.fetchall()
    conn.close()

    categories = [r[0].upper() for r in records]
    scores = [r[1] for r in records]
    totals = [r[2] for r in records]

    
    if totals and sum(totals) > 0:
        overall_percent = round((sum(scores) / sum(totals)) * 100)
    else:
        overall_percent = 0

    insight_text = generate_insight(scores, categories)
    job_pred = session.get("job_ready_prediction")

    return render_template(
        "results.html",
        results=records,
        categories=categories,
        scores=scores,
        totals=totals,
        insight=insight_text,
        overall_percent=overall_percent,
        job_pred=job_pred
    )


@app.route("/learning_path")
def learning_path():
    if "user_email" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    db_execute(cursor, """
        SELECT category, score, total
        FROM quiz_results
        WHERE user_email=?
        ORDER BY taken_on DESC
    """, (session["user_email"],))

    records = cursor.fetchall()
    conn.close()

    # 🔹 Case 1: NEW USER (no quiz taken)
    if not records:
        return render_template(
            "learning_path.html",
            message="Please attempt at least one quiz to generate your learning path.",
            readiness=0,
            weak=[],
            best=[],
            score_map={}
        )

    # 🔹 Case 2: Quiz data exists - Deduplicate by taking latest score per category
    category_data = {}
    for cat, score, total in records:
        cat_upper = cat.upper()
        if cat_upper not in category_data:
            category_data[cat_upper] = {"score": score, "total": total}

    # Extract unique categories, scores, totals
    categories = list(category_data.keys())
    scores = [category_data[cat]["score"] for cat in categories]
    totals = [category_data[cat]["total"] for cat in categories]

    readiness = round((sum(scores) / sum(totals)) * 100, 1) if sum(totals) > 0 else 0

    # Find weak and strong skills (unique)
    min_score = min(scores)
    max_score = max(scores)

    weak = list(set([categories[i] for i, s in enumerate(scores) if s == min_score]))
    best = list(set([categories[i] for i, s in enumerate(scores) if s == max_score]))

    score_map = {cat: category_data[cat]["score"] for cat in categories}

    return render_template(
        "learning_path.html",
        readiness=readiness,
        weak=weak,
        best=best,
        score_map=score_map,
        message=None
    )




from collections import defaultdict

@app.route("/analytics")
def analytics():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]
    conn = get_db_connection()
    cursor = conn.cursor()

    db_execute(cursor, """
        SELECT category, score, total, taken_on 
        FROM quiz_results 
        WHERE user_email=?
    """, (email,))
    
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return render_template("analytics.html", no_data=True)

   
    category_scores = defaultdict(list)
    category_totals = defaultdict(list)
    history = defaultdict(list)
    date_labels = set()

    for cat, score, total, date in rows:
        category_scores[cat].append(score)
        category_totals[cat].append(total)
        history[cat].append(round((score / total) * 100, 2))
        date_labels.add(date)

   
    categories = []
    scores = []
    totals = []
    category_percent = {}

    for cat in category_scores:
        avg_score = sum(category_scores[cat]) / len(category_scores[cat])
        avg_total = sum(category_totals[cat]) / len(category_totals[cat])

        categories.append(cat)
        scores.append(round(avg_score, 2))
        totals.append(round(avg_total, 2))

        if avg_total > 0:
            category_percent[cat] = round((avg_score / avg_total) * 100, 2)
        else:
            category_percent[cat] = 0

    dates = sorted(list(date_labels))

  
    sorted_skills = sorted(category_percent.items(), key=lambda x: x[1], reverse=True)

    strong_skills = [s[0].upper() for s in sorted_skills[:2]]
    weak_skills = [s[0].upper() for s in sorted_skills[-2:]]

    insight = (
        f"🌟 Your strongest skills are: **{', '.join(strong_skills)}**.\n\n"
        f"⚠️ You need to improve these skills: **{', '.join(weak_skills)}**."
    )

    return render_template(
        "analytics.html",
        categories=categories,
        scores=scores,
        totals=totals,
        dates=dates,
        history=history,
        insight=insight,
        no_data=False
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
