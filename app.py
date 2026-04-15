# ===============================
# Habit Tracker Web App (Flask) - BEAUTIFIED UI
# ===============================

from flask import Flask, render_template_string, request, redirect, session, jsonify
import sqlite3
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)
app.secret_key = "secret"

DB = "habit.db"

# ---------------- DATABASE ----------------

def connect():
    return sqlite3.connect(DB)


def create_tables():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS habits(
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        goal INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY,
        habit_id INTEGER,
        date TEXT
    )
    """)

    con.commit()
    con.close()

create_tables()

# ---------------- STREAK ----------------

def get_streak(habit_id):
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT date FROM records WHERE habit_id=? ORDER BY date DESC", (habit_id,))
    dates = [r[0] for r in cur.fetchall()]

    streak = 0
    today = datetime.now()

    for i in range(len(dates)):
        expected = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if expected in dates:
            streak += 1
        else:
            break

    return streak

# ---------------- PROGRESS ----------------

def get_progress(habit_id, goal):
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM records WHERE habit_id=?", (habit_id,))
    completed = cur.fetchone()[0]

    percent = int((completed / goal) * 100) if goal > 0 else 0
    return min(percent, 100)

# ---------------- ACHIEVEMENTS ----------------

def get_achievement(streak):
    if streak >= 30:
        return "👑 Master"
    elif streak >= 14:
        return "🥇 Dedicated"
    elif streak >= 7:
        return "🥈 Consistent"
    elif streak >= 3:
        return "🥉 Beginner"
    return "No Badge"

# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    con = connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM habits WHERE user_id=?", (session["user"],))
    habits = cur.fetchall()

    return render_template_string("""

<style>
body {
    font-family: 'Segoe UI';
    background: linear-gradient(135deg, #1d2671, #c33764);
    color: white;
    padding: 20px;
}

h1 {
    text-align: center;
}

.card {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    padding: 20px;
    margin: 15px auto;
    border-radius: 15px;
    width: 80%;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}

button {
    padding: 8px 14px;
    border: none;
    border-radius: 8px;
    margin: 5px;
    cursor: pointer;
    background: #00c6ff;
    color: black;
    font-weight: bold;
}

.progress-bar {
    width: 100%;
    background: #333;
    border-radius: 10px;
    margin-top: 10px;
}

.progress-fill {
    height: 12px;
    background: lime;
    border-radius: 10px;
}

.badge {
    background: gold;
    padding: 4px 10px;
    border-radius: 10px;
}

.streak {
    background: orange;
    padding: 4px 10px;
    border-radius: 10px;
}

input {
    padding: 8px;
    border-radius: 8px;
    border: none;
    margin: 5px;
}

</style>

<h1>🔥 Habit Tracker</h1>

<div class="card">
<h2>Add Habit</h2>
<form method="POST" action="/add">
<input name="name" placeholder="Habit name" required>
<input name="goal" type="number" placeholder="Goal" required>
<button>Add</button>
</form>
</div>

{% for h in habits %}
<div class="card">

<h2>{{h[2]}}</h2>

<span class="streak">🔥 {{ get_streak(h[0]) }} days</span>
<span class="badge">{{ get_achievement(get_streak(h[0])) }}</span>

<div class="progress-bar">
<div class="progress-fill" style="width:{{ get_progress(h[0],h[3]) }}%"></div>
</div>

<p>{{ get_progress(h[0],h[3]) }}% completed</p>

<a href="/calendar/{{h[0]}}"><button>📅 Track</button></a>
<a href="/charts"><button>📊 Charts</button></a>

</div>
{% endfor %}

""", habits=habits, get_streak=get_streak, get_progress=get_progress, get_achievement=get_achievement)

# باقي routes same (no change needed)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
