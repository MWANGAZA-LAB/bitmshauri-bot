import sqlite3
from contextlib import contextmanager

# --- Configuration ---
DB_NAME = "bitmshauri.db"


# --- Database Connection Management ---
@contextmanager
def db_connection():
    """
    A context manager to handle database connections, ensuring they are
    properly opened, committed, and closed. It also handles rollbacks on error.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# --- Database Initialization ---
def init_db():
    """
    Initializes the database and creates the 'users' table if it doesn't exist.
    This function should be called once when the application starts.
    """
    with db_connection() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      chat_id INTEGER UNIQUE,
                      first_name TEXT,
                      last_name TEXT,
                      username TEXT,
                      progress INTEGER DEFAULT 0,
                      last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_tip TIMESTAMP)"""
        )
    print("💾 Database initialized")


# --- User Management Functions ---
def update_user(user, chat_id):
    """
    Inserts a new user or updates an existing one using an efficient
    'INSERT ... ON CONFLICT' statement. This captures the user's chat_id,
    which is essential for sending proactive messages.
    """
    sql = """INSERT INTO users (user_id, chat_id, first_name, last_name, username, last_active)
             VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
             ON CONFLICT(user_id) DO UPDATE SET
                chat_id=excluded.chat_id,
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                username=excluded.username,
                last_active=CURRENT_TIMESTAMP;"""
    with db_connection() as c:
        c.execute(
            sql,
            (user.id, chat_id, user.first_name, user.last_name, user.username),
        )


def update_last_tip(user_id):
    """Updates the timestamp of the last tip sent to a specific user."""
    with db_connection() as c:
        c.execute(
            "UPDATE users SET last_tip=CURRENT_TIMESTAMP WHERE user_id=?",
            (user_id,),
        )


def get_all_users():
    """Retrieves the user_id and chat_id for all users in the database."""
    with db_connection() as c:
        c.execute("SELECT user_id, chat_id FROM users")
        return c.fetchall()


def get_user_by_id(user_id):
    """Retrieve a user's record by their user_id."""
    with db_connection() as c:
        c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return c.fetchone()


def create_feedback_table():
    with db_connection() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )


def save_feedback(user_id, username, feedback):
    with db_connection() as c:
        c.execute(
            "INSERT INTO feedback (user_id, username, feedback) VALUES (?, ?, ?)",
            (user_id, username, feedback),
        )


create_feedback_table()
init_db()
