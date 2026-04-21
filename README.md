# 🔥 Habit Tracker Web App

A simple and powerful **Habit Tracking Web Application** built using **Flask, SQLite, and Chart.js**.
Track your daily habits, monitor streaks, and visualize your progress with analytics.

---

## 🚀 Features

* 👤 User Registration & Login (Session-based authentication)
* 📌 Add and manage habits
* 🔥 Streak tracking (daily consistency)
* 🏆 Achievement badges
* 📊 Progress bar based on goals
* 📅 Interactive calendar tracking
* 📈 Weekly & Monthly analytics (Chart.js)
* 💾 SQLite database (lightweight & easy)

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite
* **Frontend:** HTML, CSS, JavaScript
* **Charts:** Chart.js

---

## 📂 Project Structure

```
project/
│── app.py
│── habit.db
│── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/habit-tracker.git
cd habit-tracker
```

### 2. Install Dependencies

```bash
pip install flask
```

### 3. Run the App

```bash
python app.py
```

### 4. Open in Browser

```
http://127.0.0.1:5000/
```

---

## 📊 How It Works

### ➤ Streak System

* Calculates consecutive days of habit completion
* Breaks if a day is missed

### ➤ Progress Tracking

* Based on total completions vs goal
* Capped at 100%

### ➤ Achievements

| Streak   | Badge         |
| -------- | ------------- |
| 3+ days  | 🥉 Beginner   |
| 7+ days  | 🥈 Consistent |
| 14+ days | 🥇 Dedicated  |
| 30+ days | 👑 Master     |

---

## 📅 Calendar Tracking

* Click on any day to mark completion
* Completed days are highlighted
* Displays current streak

---

## 📈 Analytics

* **Weekly Graph** → Last 7 days activity
* **Monthly Graph** → Last 30 days activity

---

## 🔐 Security Note

⚠️ This project uses **plain-text passwords** (for learning purposes).
For production use:

* Hash passwords using `bcrypt`
* Add proper authentication system

---

## 💡 Future Improvements

* 🔒 Password hashing & authentication
* 🌐 Deploy online (Render / Railway / Vercel)
* 📱 Responsive UI
* 🔔 Reminder notifications
* 📊 Advanced analytics

---

## 🤝 Contributing

Feel free to fork this project and improve it!

---

## 📜 License

This project is open-source and free to use.

---

## ❤️ Made With

* Python 🐍
* Flask 🚀
* Hard work 💪

---
