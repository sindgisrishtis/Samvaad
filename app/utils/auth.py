import streamlit as st
import sqlite3
import bcrypt
import random
from datetime import datetime, timedelta
from pathlib import Path

# ===========================
# DATABASE SETUP
# ===========================

DB_PATH = Path(__file__).parent.parent / "app_data" / "users.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


# ===========================
# AUTHENTICATION FUNCTIONS
# ===========================

def register_user(name, email, username, password):
    """Register a new user with hashed password."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO users (name, email, username, password_hash) VALUES (?, ?, ?, ?)",
                    (name, email, username, password_hash))
        conn.commit()
        conn.close()
        return True, "✅ Registration successful!"
    except sqlite3.IntegrityError:
        return False, "⚠️ Username or Email already exists."
    except Exception as e:
        return False, f"❌ Error: {e}"


def login_user(username_or_email, password):
    """Authenticate user login."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? OR email=?", (username_or_email, username_or_email))
        user = cur.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4]):
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user[0]
            st.session_state["username"] = user[3]
            return True, f"Welcome back, {user[1]}!"
        else:
            return False, "Invalid credentials."
    except Exception as e:
        return False, f"Error: {e}"


def check_login():
    """Check if user is logged in."""
    return st.session_state.get("logged_in", False)


def logout_user():
    """Logout current user."""
    st.session_state.clear()


def get_user_info():
    """Get user info from session."""
    if st.session_state.get("logged_in", False):
        return {
            "user_id": st.session_state["user_id"],
            "username": st.session_state["username"]
        }
    return None


# ===========================
# ANALYTICS MOCK DATA
# ===========================

def get_user_stats(user_id):
    """
    Temporary mock function to provide sample analytics data.
    Replace with real DB fetch when activity tracking is implemented.
    """
    # Simulate action categories
    actions = [
        ("Sign → Text", random.randint(10, 30), random.uniform(0.7, 0.95)),
        ("Text → Sign", random.randint(5, 25), random.uniform(0.6, 0.9)),
        ("Speech → Sign", random.randint(5, 15), random.uniform(0.75, 0.95))
    ]

    # Practice data
    practice = []
    for i in range(10):
        sign = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        score = random.uniform(0.6, 1.0)
        timestamp = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        practice.append((sign, score, timestamp))

    # History (recent activity)
    history = []
    for i in range(20):
        action_type = random.choice(["Sign → Text", "Text → Sign", "Speech → Sign"])
        output = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        confidence = random.uniform(0.6, 0.95)
        timestamp = (datetime.now() - timedelta(hours=i * 5)).strftime("%Y-%m-%d %H:%M:%S")
        history.append((action_type, output, confidence, timestamp))

    return {
        "actions": actions,
        "practice": practice,
        "history": history
    }
