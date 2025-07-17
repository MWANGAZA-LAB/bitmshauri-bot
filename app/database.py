import sqlite3
from app import app
import logging

logger = logging.getLogger(__name__)

def init_db():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  chat_id INTEGER,
                  first_name TEXT,
                  last_name TEXT,
                  username TEXT,
                  progress INTEGER DEFAULT 0,
                  last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_tip TIMESTAMP)''')
    
    
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'last_active' not in columns:
        logger.info("Adding last_active column to users table")
        c.execute("ALTER TABLE users ADD COLUMN last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    
    if 'last_tip' not in columns:
        logger.info("Adding last_tip column to users table")
        c.execute("ALTER TABLE users ADD COLUMN last_tip TIMESTAMP")
    
    conn.commit()
    conn.close()
    logger.info(f"💾 Database initialized at {db_path}")

def update_user(user):
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, first_name, last_name, username) 
                 VALUES (?, ?, ?, ?)''',
              (user.id, user.first_name, user.last_name, user.username))
    
    c.execute('''UPDATE users SET 
                 first_name=?, last_name=?, username=?, 
                 last_active=CURRENT_TIMESTAMP 
                 WHERE user_id=?''',
              (user.first_name, user.last_name, user.username, user.id))
    
    conn.commit()
    conn.close()

def update_last_tip(user_id):
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE users SET last_tip=CURRENT_TIMESTAMP WHERE user_id=?''', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT user_id, chat_id FROM users''')
    users = c.fetchall()
    conn.close()
    return users


init_db()