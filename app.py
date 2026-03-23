from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# ---------------- DATABASE ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bmi.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            weight REAL,
            height REAL,
            bmi REAL,
            category TEXT,
            calories REAL
        )
    """)
    conn.commit()
    conn.close()

# RUN ON START
init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    age = int(request.form["age"])
    weight = float(request.form["weight"])
    height_cm = float(request.form["height"])
    activity = request.form["activity"]

    height_m = height_cm / 100

    # BMI CALCULATION
    bmi = round(weight / (height_m ** 2), 2)

    # CATEGORY + COLOR + MESSAGE
    if bmi < 18.5:
        category = "Underweight"
        color = "blue"
        message = "You should improve your diet "

    elif bmi < 25:
        category = "Normal"
        color = "green"
        message = "You are healthy "

    elif bmi < 30:
        category = "Overweight"
        color = "orange"
        message = "Try to exercise more "

    else:
        category = "Obese"
        color = "red"
        message = "Health risk! Take care "

    # CALORIES (BMR)
    bmr = 10 * weight + 6.25 * height_cm - 5 * age + 5

    # ACTIVITY MULTIPLIER
    if activity == "no":
        calories = bmr * 1.2
    elif activity == "light":
        calories = bmr * 1.375
    elif activity == "medium":
        calories = bmr * 1.55
    else:
        calories = bmr * 1.725

    # SAVE DATA
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO records (age, weight, height, bmi, category, calories) VALUES (?, ?, ?, ?, ?, ?)",
        (age, weight, height_cm, bmi, category, calories)
    )
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        bmi=bmi,
        category=category,
        calories=round(calories, 2),
        color=color,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)