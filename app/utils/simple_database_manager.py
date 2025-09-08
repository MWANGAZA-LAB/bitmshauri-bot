"""Simple database manager with fallback support.

Works with or without aiosqlite.
"""

import asyncio
import json
import sqlite3
from typing import List

from app.utils.logger import logger

# Try to import aiosqlite, fallback to regular sqlite3 if not available
try:
    import aiosqlite
    ASYNC_SQLITE_AVAILABLE = True
except ImportError:
    ASYNC_SQLITE_AVAILABLE = False
    logger.logger.warning("aiosqlite not available, using regular sqlite3")


class SimpleDatabaseManager:
    """Simple database manager with async/sync fallback."""

    def __init__(self, db_path: str = "bitmshauri_bot.db"):
        """Initialize the database manager."""
        self.db_path = db_path
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize database tables."""
        try:
            if ASYNC_SQLITE_AVAILABLE:
                await self._init_async()
            else:
                await self._init_sync()
            self._initialized = True
            logger.logger.info("Database initialized successfully")
        except Exception as e:
            logger.log_error(e, {"operation": "database_initialize"})
            raise

    async def _init_async(self) -> None:
        """Initialize with aiosqlite."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    chat_id INTEGER,
                    language TEXT DEFAULT 'sw',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS lesson_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    lesson_key TEXT,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    quiz_name TEXT,
                    score INTEGER,
                    total_questions INTEGER,
                    answers TEXT,
                    time_taken INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    feedback_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            await db.commit()

    async def _init_sync(self) -> None:
        """Initialize with regular sqlite3 (run in thread)."""
        def init_db():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    chat_id INTEGER,
                    language TEXT DEFAULT 'sw',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lesson_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    lesson_key TEXT,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    quiz_name TEXT,
                    score INTEGER,
                    total_questions INTEGER,
                    answers TEXT,
                    time_taken INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    feedback_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            conn.commit()
            conn.close()

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, init_db)

    async def add_user(
        self,
        user_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        chat_id: int = None,
    ) -> None:
        """Add or update user."""
        try:
            if ASYNC_SQLITE_AVAILABLE:
                await self._add_user_async(
                    user_id, username, first_name, last_name, chat_id
                )
            else:
                await self._add_user_sync(
                    user_id, username, first_name, last_name, chat_id
                )
        except Exception as e:
            logger.log_error(e, {"operation": "add_user", "user_id": user_id})

    async def _add_user_async(
        self,
        user_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        chat_id: int = None,
    ) -> None:
        """Add user with aiosqlite."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users
                (user_id, username, first_name, last_name, chat_id, last_active)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, username, first_name, last_name, chat_id))
            await db.commit()

    async def _add_user_sync(
        self,
        user_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        chat_id: int = None,
    ) -> None:
        """Add user with regular sqlite3."""
        def add_user():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users
                (user_id, username, first_name, last_name, chat_id, last_active)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, username, first_name, last_name, chat_id))
            conn.commit()
            conn.close()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, add_user)

    async def save_lesson_progress(self, user_id: int, lesson_key: str) -> None:
        """Save lesson progress."""
        try:
            if ASYNC_SQLITE_AVAILABLE:
                await self._save_lesson_progress_async(user_id, lesson_key)
            else:
                await self._save_lesson_progress_sync(user_id, lesson_key)
        except Exception as e:
            logger.log_error(
                e, {"operation": "save_lesson_progress", "user_id": user_id}
            )

    async def _save_lesson_progress_async(
        self, user_id: int, lesson_key: str
    ) -> None:
        """Save lesson progress with aiosqlite."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO lesson_progress (user_id, lesson_key)
                VALUES (?, ?)
            """, (user_id, lesson_key))
            await db.commit()

    async def _save_lesson_progress_sync(
        self, user_id: int, lesson_key: str
    ) -> None:
        """Save lesson progress with regular sqlite3."""
        def save_progress():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lesson_progress (user_id, lesson_key)
                VALUES (?, ?)
            """, (user_id, lesson_key))
            conn.commit()
            conn.close()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, save_progress)

    async def save_quiz_result(
        self,
        user_id: int,
        quiz_name: str,
        score: int,
        total_questions: int,
        answers: List,
        time_taken: int,
    ) -> None:
        """Save quiz result."""
        try:
            answers_json = json.dumps(answers)
            if ASYNC_SQLITE_AVAILABLE:
                await self._save_quiz_result_async(
                    user_id, quiz_name, score, total_questions, answers_json, time_taken
                )
            else:
                await self._save_quiz_result_sync(
                    user_id, quiz_name, score, total_questions, answers_json, time_taken
                )
        except Exception as e:
            logger.log_error(
                e, {"operation": "save_quiz_result", "user_id": user_id}
            )

    async def _save_quiz_result_async(
        self,
        user_id: int,
        quiz_name: str,
        score: int,
        total_questions: int,
        answers_json: str,
        time_taken: int,
    ) -> None:
        """Save quiz result with aiosqlite."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO quiz_results
                (user_id, quiz_name, score, total_questions, answers, time_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, quiz_name, score, total_questions, answers_json, time_taken))
            await db.commit()

    async def _save_quiz_result_sync(
        self,
        user_id: int,
        quiz_name: str,
        score: int,
        total_questions: int,
        answers_json: str,
        time_taken: int,
    ) -> None:
        """Save quiz result with regular sqlite3."""
        def save_result():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quiz_results
                (user_id, quiz_name, score, total_questions, answers, time_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, quiz_name, score, total_questions, answers_json, time_taken))
            conn.commit()
            conn.close()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, save_result)

    async def save_feedback(self, user_id: int, feedback_text: str) -> None:
        """Save user feedback."""
        try:
            if ASYNC_SQLITE_AVAILABLE:
                await self._save_feedback_async(user_id, feedback_text)
            else:
                await self._save_feedback_sync(user_id, feedback_text)
        except Exception as e:
            logger.log_error(
                e, {"operation": "save_feedback", "user_id": user_id}
            )

    async def _save_feedback_async(
        self, user_id: int, feedback_text: str
    ) -> None:
        """Save feedback with aiosqlite."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO feedback (user_id, feedback_text)
                VALUES (?, ?)
            """, (user_id, feedback_text))
            await db.commit()

    async def _save_feedback_sync(
        self, user_id: int, feedback_text: str
    ) -> None:
        """Save feedback with regular sqlite3."""
        def save_feedback():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (user_id, feedback_text)
                VALUES (?, ?)
            """, (user_id, feedback_text))
            conn.commit()
            conn.close()

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, save_feedback)

    async def close(self) -> None:
        """Close database connections."""
        # For simple implementation, nothing to close
        pass


# Global database manager instance
async_db_manager = SimpleDatabaseManager()