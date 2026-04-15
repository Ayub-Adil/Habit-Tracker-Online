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

    cur.execute(
        "SELECT date FROM records WHERE habit_id=? ORDER BY date DESC",
        (habit_id,)
    )

    dates = [r[0] for r in cur.fetchall()]

    streak = 0
    today = datetime.now()

    for i in range(len(dates)):

        expected = (
            today - timedelta(days=i)
        ).strftime("%Y-%m-%d")

        if expected in dates:
            streak += 1
        else:
            break

    return streak


# ---------------- PROGRESS ----------------

def get_progress(habit_id, goal):

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM records WHERE habit_id=?",
        (habit_id,)
    )

    completed = cur.fetchone()[0]

    percent = int(
        (completed / goal) * 100
    ) if goal > 0 else 0

    if percent > 100:
        percent = 100

    return percent


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

    else:
        return "No Badge Yet"


# ---------------- REGISTER ----------------

@app.route("/", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username=request.form["username"]
        password=request.form["password"]

        con=connect()
        cur=con.cursor()

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )

        con.commit()
        con.close()

        return redirect("/login")

    return render_template_string("""

<h2>Register</h2>

<form method="POST">

<input name="username" required>
<input name="password" type="password" required>

<button>Register</button>

</form>

<a href="/login">Login</a>

""")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        con=connect()
        cur=con.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user=cur.fetchone()

        if user:
            session["user"]=user[0]
            return redirect("/dashboard")

    return render_template_string("""

<h2>Login</h2>

<form method="POST">

<input name="username" required>
<input name="password" type="password" required>

<button>Login</button>

</form>

""")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    con=connect()
    cur=con.cursor()

    cur.execute(
        "SELECT * FROM habits WHERE user_id=?",
        (session["user"],)
    )

    habits=cur.fetchall()

    return render_template_string("""

<style>

.progress-bar {
width:100%;
background:#ddd;
border-radius:10px;
overflow:hidden;
margin-top:5px;
}

.progress-fill {
height:15px;
background:#28a745;
}

.badge {
background:gold;
padding:5px 10px;
border-radius:8px;
margin-left:10px;
font-weight:bold;
}

.streak {
background:orange;
padding:4px 8px;
border-radius:6px;
margin-left:10px;
}

button {
padding:6px 10px;
border:none;
background:#007bff;
color:white;
border-radius:6px;
cursor:pointer;
}

.card {
background:white;
padding:20px;
margin-bottom:20px;
border-radius:10px;
box-shadow:0 5px 10px rgba(0,0,0,0.1);
}

body {
font-family:Arial;
background:#f5f6fa;
padding:20px;
}

</style>

<h1>🔥 Habit Dashboard</h1>

<div class="card">

<h2>Add Habit</h2>

<form method="POST" action="/add">

<input name="name"
placeholder="Habit name"
required>

<input name="goal"
type="number"
placeholder="Goal days"
required>

<button>Add</button>

</form>

</div>

<div class="card">

<h2>Your Habits</h2>

{% for h in habits %}

<div style="margin-bottom:20px;">

<b>{{h[2]}}</b>

<span class="streak">
🔥 {{ get_streak(h[0]) }} days
</span>

<span class="badge">
🏆 {{ get_achievement(get_streak(h[0])) }}
</span>

<div class="progress-bar">

<div class="progress-fill"
style="width:{{ get_progress(h[0],h[3]) }}%">
</div>

</div>

<small>

Progress:
{{ get_progress(h[0],h[3]) }}%

</small>

<br><br>

<a href="/calendar/{{h[0]}}">
<button>📅 Track</button>
</a>

</div>

{% endfor %}

</div>

<a href="/charts">
<button>📊 View Analytics</button>
</a>

""",
habits=habits,
get_streak=get_streak,
get_progress=get_progress,
get_achievement=get_achievement)


# ---------------- ADD HABIT ----------------

@app.route("/add",methods=["POST"])
def add():

    name=request.form["name"]
    goal=request.form["goal"]

    con=connect()
    cur=con.cursor()

    cur.execute(
        "INSERT INTO habits(user_id,name,goal) VALUES(?,?,?)",
        (session["user"],name,goal)
    )

    con.commit()
    con.close()

    return redirect("/dashboard")


# ---------------- CALENDAR ----------------

@app.route("/calendar/<int:habit_id>")
def habit_calendar(habit_id):

    now=datetime.now()

    cal=calendar.monthcalendar(
        now.year,
        now.month
    )

    con=connect()
    cur=con.cursor()

    cur.execute(
        "SELECT date FROM records WHERE habit_id=?",
        (habit_id,)
    )

    records=[
        int(r[0].split("-")[2])
        for r in cur.fetchall()
        if r[0].startswith(
            now.strftime("%Y-%m")
        )
    ]

    streak=get_streak(habit_id)

    return render_template_string("""

<style>

.calendar {
display:grid;
grid-template-columns:repeat(7,1fr);
gap:5px;
}

.day {
padding:15px;
text-align:center;
border-radius:6px;
cursor:pointer;
background:#eee;
}

.completed {
background:#28a745;
color:white;
font-weight:bold;
}

.day:hover {
background:#007bff;
color:white;
}

.streak-box {
background:orange;
padding:10px;
border-radius:8px;
margin-bottom:15px;
font-weight:bold;
}

button {
padding:6px 10px;
border:none;
background:#007bff;
color:white;
border-radius:6px;
cursor:pointer;
}

</style>

<h2>📅 Daily Tracking</h2>

<div class="streak-box">

🔥 Current Streak: {{streak}} days

</div>

<div class="calendar">

{% for week in cal %}
{% for day in week %}

{% if day!=0 %}

<a href="/mark/{{habit_id}}/{{day}}">

<div class="day
{% if day in records %}
completed
{% endif %}
">

{{day}}

</div>

</a>

{% else %}

<div></div>

{% endif %}

{% endfor %}
{% endfor %}

</div>

<br>

<a href="/dashboard">
<button>⬅ Back</button>
</a>

""",
cal=cal,
habit_id=habit_id,
records=records,
streak=streak)


# ---------------- MARK DAY ----------------

@app.route("/mark/<int:habit_id>/<int:day>")
def mark_day(habit_id, day):

    date=datetime.now().strftime("%Y-%m-")+str(day)

    con=connect()
    cur=con.cursor()

    cur.execute(
        "SELECT * FROM records WHERE habit_id=? AND date=?",
        (habit_id,date)
    )

    exists=cur.fetchone()

    if not exists:

        cur.execute(
            "INSERT INTO records(habit_id,date) VALUES(?,?)",
            (habit_id,date)
        )

        con.commit()

    con.close()

    return redirect("/calendar/"+str(habit_id))


# ---------------- WEEKLY DATA ----------------

@app.route("/weekly")
def weekly():

    con=connect()
    cur=con.cursor()

    today=datetime.now()

    data={}

    for i in range(7):

        day=(today-timedelta(days=i)).strftime("%Y-%m-%d")

        cur.execute(
            "SELECT COUNT(*) FROM records WHERE date=?",
            (day,)
        )

        data[day]=cur.fetchone()[0]

    return jsonify(data)


# ---------------- MONTHLY DATA ----------------

@app.route("/monthly")
def monthly():

    con=connect()
    cur=con.cursor()

    today=datetime.now()

    data={}

    for i in range(30):

        day=(today-timedelta(days=i)).strftime("%Y-%m-%d")

        cur.execute(
            "SELECT COUNT(*) FROM records WHERE date=?",
            (day,)
        )

        data[day]=cur.fetchone()[0]

    return jsonify(data)


# ---------------- CHART PAGE ----------------

@app.route("/charts")
def charts():

    return render_template_string("""

<h1>📊 Analytics</h1>

<canvas id="weekly"></canvas>
<canvas id="monthly"></canvas>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>

fetch("/weekly")
.then(res=>res.json())
.then(data=>{

new Chart(
document.getElementById("weekly"),
{
type:"line",
data:{
labels:Object.keys(data),
datasets:[{
label:"Weekly",
data:Object.values(data)
}]
}
})

})

fetch("/monthly")
.then(res=>res.json())
.then(data=>{

new Chart(
document.getElementById("monthly"),
{
type:"bar",
data:{
labels:Object.keys(data),
datasets:[{
label:"Monthly",
data:Object.values(data)
}]
}
})

})

</script>

""")


# ---------------- RUN ----------------

if __name__=="__main__":
    app.run(debug=True)
