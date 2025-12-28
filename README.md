🎓 Skillify – Student Skill Analyzer & Career Readiness Platform

Skillify is a data-driven student skill assessment and analytics platform designed to help students evaluate their technical and aptitude skills, monitor progress, receive personalized learning guidance, and predict career readiness using Machine Learning.

This project is developed as a Final Year B.Tech CSE (Data Science) project, focusing on real-world application, usability, and analytics-driven decision-making for students and academic institutions.

📌 Problem Statement

Many students are unsure about:

Their actual skill level

Which areas they need to improve

Whether they are job-ready or not

What learning path they should follow

Traditional systems only provide marks, not insights.

Skillify solves this problem by:

Analyzing student performance

Visualizing progress through dashboards

Providing personalized learning paths

Predicting job readiness using ML

🚀 Key Features
👤 Student Module

Secure login and signup system

Student profile with branch, skills, internships, projects, and confidence level

Branch-based quiz system (Aptitude, DSA, DBMS, OS)

Quiz result summary with category-wise analysis

📊 Analytics dashboard to track performance and progress

🧭 Personalized learning path based on weak skills

🤖 Job readiness prediction using Machine Learning

🛠 Admin Module

Role-based admin authentication

Admin dashboard with platform overview

View total students, quizzes attempted, and performance trends

Branch-wise and category-wise analytics

Helps institutions identify skill gaps across students

📊 Analytics & Visualization

Skillify uses interactive charts to make data easy to understand:

📈 Line charts for performance trends over time

📊 Bar charts for category-wise and branch-wise scores

📌 Overall readiness percentage

📉 Skill gap identification

These visualizations help students and admins interpret data clearly and take informed actions.

🤖 Machine Learning Integration

A Logistic Regression model is trained using synthetic student performance data

Input features include:

Aptitude score

DSA score

DBMS score

OS score

Output:

Job Ready (Yes / No)

The trained model is saved using pickle and integrated into the Flask application to provide real-time predictions after quiz completion.

🧠 Personalized Learning Path

Based on quiz performance:

Weak skill areas are identified

Best-performing skills are highlighted

Students receive targeted improvement suggestions

Helps students follow a structured and focused learning roadmap

This makes the platform action-oriented, not just analytical.

🧰 Technology Stack
Frontend

HTML

CSS

JavaScript

Backend

Python

Flask

Database

SQLite

Machine Learning

Pandas

NumPy

Scikit-learn

Pickle

Visualization

Chart.js

⚙️ How the System Works

Student registers and logs in

Student fills profile details

Branch-wise quizzes are unlocked

Quiz results are stored in database

Analytics dashboard visualizes performance

ML model predicts job readiness

Learning path is generated based on weak skills

Admin can monitor overall performance and trends

🎯 Outcome

Enabled students to understand their strengths and weaknesses clearly

Improved career awareness through analytics and ML predictions

Provided structured learning guidance for skill improvement

🔮 Future Enhancements

Resume analysis using NLP

Internship and job recommendation system

Advanced ML models (Random Forest, XGBoost)

Cloud deployment (AWS / Render)

Mobile-responsive UI

Gamification (badges, levels, challenges)

Integration with online learning platforms

👨‍💻 Author

Cancy Khandelwal
B.Tech CSE (Data Science)


📚 Acknowledgement

This project was developed as part of the B.Tech Final Year Curriculum to demonstrate practical implementation of Data Science, Machine Learning, Analytics, and Full-Stack Development concepts.

⭐ Conclusion

Skillify is a practical, analytics-driven, and scalable platform that bridges the gap between student performance data and career readiness, making it useful for students, educators, and institutions.
