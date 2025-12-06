from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import json
import pickle



app = Flask(__name__)
app.secret_key = "my_secret_key_12345"
app.config["UPLOAD_FOLDER"] = "static/uploads"

model = pickle.load(open("job_ready_model.pkl", "rb"))

def load_questions():
    with open("data/questions.json", "r") as file:
        questions = json.load(file)
    return questions

BRANCH_CATEGORIES = {
    "CSE": ["aptitude", "dsa", "dbms", "os"],
    "OTHER": ["aptitude"] 
}

ADMIN_EMAIL = "admin@skillify.com"
ADMIN_PASSWORD = "admin123"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("data/users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name, password FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            message = "Email not found."
            return render_template("login.html", message=message)

        elif user[1] != password:
            message = "Incorrect password."
            return render_template("login.html", message=message)

        # Login success
        session["user_name"] = user[0]
        session["user_email"] = email
        return redirect("/dashboard")

    return render_template("login.html", message=message)

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin_dashboard")
        else:
            return render_template("admin_login.html", error="❌ Invalid login")

    return render_template("admin_login.html")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("data/users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            message = "Email already exists. Please use another email or login."
            return render_template("signup.html", message=message)

        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
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

        conn = sqlite3.connect("data/users.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO student_details (user_email, branch, projects, internships, skills, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                       (email, branch, projects, internships, skills, confidence))

        conn.commit()
        conn.close()

   
        return redirect("/quiz_sections")

    return render_template("form.html")
@app.route("/quiz/<category>", methods=["GET", "POST"])
def quiz_category(category):
    if "user_name" not in session:
        return redirect("/login")

    questions = load_questions()

    if category not in questions:
        return "Quiz category not found!"

    if request.method == "POST":
        answers = []
        for i in range(1, 6):
            user_ans = request.form.get(f"q{i}")
            answers.append(user_ans)

  
        session["quiz_answers"] = answers
        session["quiz_category"] = category

        return redirect("/result")


    quiz_questions = questions[category]
    return render_template("quiz.html", questions=quiz_questions, category=category)




# ------------------- PROFILE -------------------
@app.route("/profile")
def profile():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, email, profile_pic FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    cursor.execute("SELECT branch, projects, internships, skills, confidence FROM student_details WHERE user_email=?", (email,))
    details = cursor.fetchone()

    conn.close()

    return render_template("profile.html", user=user, details=details)

# ------------------- EDIT PROFILE -------------------
@app.route("/edit_profile", methods=["GET"])
def edit_profile():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, email, profile_pic FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    cursor.execute("SELECT branch, projects, internships, skills, confidence FROM student_details WHERE user_email=?", (email,))
    details = cursor.fetchone()

    conn.close()

    return render_template("edit_profile.html", user=user, details=details)

@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]
    name = request.form["name"]
    branch = request.form["branch"]
    skills = request.form["skills"]

    file = request.files.get("profile_pic")
    filename = None

    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1]
        filename = email.replace("@", "_") + "." + ext
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    if filename:
        cursor.execute("UPDATE users SET name=?, profile_pic=? WHERE email=?", (name, filename, email))
    else:
        cursor.execute("UPDATE users SET name=? WHERE email=?", (name, email))

    cursor.execute("UPDATE student_details SET branch=?, skills=? WHERE user_email=?", (branch, skills, email))

    conn.commit()
    conn.close()

    session["user_name"] = name

    return redirect("/profile")

@app.route("/quiz_sections")
def quiz_sections():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT branch FROM student_details WHERE user_email=? ORDER BY rowid DESC LIMIT 1",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        branch = row[0].strip().upper()
    else:
        branch = "OTHER"

    # fetch categories for the branch
    categories = BRANCH_CATEGORIES.get(branch, ["aptitude"])

    return render_template(
        "quiz_sections.html",
        categories=categories,
        branch=branch.title()
    )



from datetime import datetime
@app.route("/submit_quiz/<category>", methods=["POST"])
def submit_quiz(category):
    questions = load_questions()[category]
    score = 0

 
    for i, q in enumerate(questions, start=1):
        user_ans = request.form.get(f"q{i}")
        if user_ans == q["answer"]:
            score += 1

    total = len(questions)

   
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("""
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

    

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("""
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

    unique_scores = set(scores)

   
    if len(unique_scores) == 1:
        return "Your performance is balanced across all skills. Try attempting more quizzes to get detailed insights."

    max_score = max(scores)
    min_score = min(scores)

    best_cats = [categories[i].upper() for i, s in enumerate(scores) if s == max_score]


    weak_cats = [categories[i].upper() for i, s in enumerate(scores) if s == min_score]

    insight = ""

    
    if len(best_cats) == 1:
        insight += f"🌟 Your strongest skill is **{best_cats[0]}**.\n"
    else:
        insight += f"🌟 Your strongest skills are: **{', '.join(best_cats)}**.\n"

   
    if len(weak_cats) == 1:
        insight += f"⚠️ You need to improve your **{weak_cats[0]}** skill.\n\n"
    else:
        insight += f"⚠️ You need to improve these skills: **{', '.join(weak_cats)}**.\n\n"

 
    insight += "🎯 **Recommended Actions:**\n"

    if "APTITUDE" in weak_cats:
        insight += "• Practice aptitude daily using IndiaBix or PrepInsta.\n"

    if "DSA" in weak_cats:
        insight += "• Solve 1–2 DSA problems daily on LeetCode or CodeStudio.\n"

    if "DBMS" in weak_cats:
        insight += "• Revise SQL queries, Joins & ER models.\n"

    if "OS" in weak_cats:
        insight += "• Focus on CPU Scheduling, Deadlocks & Memory Management.\n"

    if len(weak_cats) == 0:
        insight += "• Awesome! All your skills look great! Keep it up 🚀\n"

    return insight

@app.route("/results")
def results():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, score, total, taken_on 
        FROM quiz_results 
        WHERE user_email=? 
        ORDER BY taken_on DESC
    """, (email,))
    
    records = cursor.fetchall()
    conn.close()

    categories = [row[0] for row in records]
    scores = [row[1] for row in records]
    totals = [row[2] for row in records]

    # ✅ overall percentage (for UI)
    if totals and sum(totals) > 0:
        overall_percent = round(sum(scores) / sum(totals) * 100)
    else:
        overall_percent = 0

    # ✅ AI insight text (you already had this)
    insight_text = generate_insight(scores, categories)

    # ✅ ML prediction from session (0/1 or None)
    job_pred = session.get("job_ready_prediction")  # 0 = not ready, 1 = ready

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

    email = session["user_email"]

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    # fetch last quiz scores
    cursor.execute("""
        SELECT category, score, total 
        FROM quiz_results 
        WHERE user_email=? 
        ORDER BY taken_on DESC
    """, (email,))
    
    records = cursor.fetchall()
    conn.close()

    if not records:
        return render_template("learning_path.html", 
                               message="Please attempt at least one quiz to get your learning path.")

    # Build score dictionary

    categories = [r[0].upper() for r in records]
    scores = [r[1] for r in records]
    totals = [r[2] for r in records]
    score_map = {r[0].upper(): r[1] for r in records}

    # Best & Weak Areas
    min_score = min(scores)

    # List of all weak skills
    weak_skills = [categories[i].upper() for i, s in enumerate(scores) if s == min_score]

    # Find best skills
    max_score = max(scores)
    best_skills = [categories[i].upper() for i, s in enumerate(scores) if s == max_score]

    readiness = round((sum(scores) / sum(totals)) * 100, 1)


    return render_template(
        "learning_path.html",
        best=best_skills,
        weak=weak_skills,
        readiness=readiness,
        score_map=score_map
    )



from collections import defaultdict

@app.route("/analytics")
def analytics():
    if "user_email" not in session:
        return redirect("/login")

    email = session["user_email"]
    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT category, score, total, taken_on FROM quiz_results WHERE user_email=?", (email,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return render_template("analytics.html", no_data=True)

    # --- Prepare data ---
    categories = []
    scores = []
    totals = []
    dates = []
    
    # For line chart (attempt history)
    history = defaultdict(list)

    for row in rows:
        cat, score, total, date = row
        categories.append(cat)
        scores.append(score)
        totals.append(total)
        dates.append(date)
        history[cat].append(score)

    return render_template("analytics.html",
                           categories=categories,
                           scores=scores,
                           totals=totals,
                           dates=dates,
                           history=history,
                           no_data=False)

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT id, user_email, category, score, total, taken_on FROM quiz_results")
    results = cursor.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", users=users, results=results)



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin_login")

if __name__ == "__main__":
    app.run(debug=True)
