"""
Enhanced database manager with connection pooling and async support
"""

import asyncio
import sqlite3
import aiosqlite
from contextlib import asynccontextmanager, contextmanager
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
from app.utils.logger import logger


class DatabaseConnectionPool:
    """Connection pool for database operations"""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections = asyncio.Queue(maxsize=max_connections)
        self._created_connections = 0
        self._lock = asyncio.Lock()
    
    async def get_connection(self) -> aiosqlite.Connection:
        """Get a database connection from the pool"""
        try:
            # Try to get existing connection
            connection = self._connections.get_nowait()
            return connection
        except asyncio.QueueEmpty:
            # Create new connection if pool is not full
            async with self._lock:
                if self._created_connections < self.max_connections:
                    connection = await aiosqlite.connect(self.db_path)
                    connection.row_factory = aiosqlite.Row
                    self._created_connections += 1
                    return connection
                else:
                    # Wait for available connection
                    return await self._connections.get()
    
    async def return_connection(self, connection: aiosqlite.Connection):
        """Return connection to the pool"""
        try:
            self._connections.put_nowait(connection)
        except asyncio.QueueFull:
            # Close connection if pool is full
            await connection.close()
            async with self._lock:
                self._created_connections -= 1
    
    async def close_all(self):
        """Close all connections in the pool"""
        while not self._connections.empty():
            connection = await self._connections.get()
            await connection.close()
        self._created_connections = 0


class AsyncDatabaseManager:
    """Async database manager with connection pooling"""
    
    def __init__(self, db_path: str = "bitmshauri.db"):
        self.db_path = db_path
        self.pool = DatabaseConnectionPool(db_path)
        self._initialized = False
    
    async def initialize(self):
        """Initialize database tables"""
        if self._initialized:
            return
        
        async with self.get_connection() as conn:
            await self._create_tables(conn)
        self._initialized = True
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with automatic cleanup"""
        connection = await self.pool.get_connection()
        try:
            yield connection
        finally:
            await self.pool.return_connection(connection)
    
    async def _create_tables(self, conn: aiosqlite.Connection):
        """Create database tables"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                chat_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                language_preference TEXT DEFAULT 'sw',
                total_lessons_completed INTEGER DEFAULT 0,
                total_quizzes_taken INTEGER DEFAULT 0,
                quiz_score_average REAL DEFAULT 0.0,
                streak_days INTEGER DEFAULT 0,
                last_tip_date TEXT,
                is_premium BOOLEAN DEFAULT FALSE,
                settings TEXT DEFAULT '{}'
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                activity_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS lesson_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_key TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_time_seconds INTEGER,
                audio_listened BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quiz_name TEXT,
                score INTEGER,
                total_questions INTEGER,
                answers TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                time_taken_seconds INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                target_price REAL,
                currency TEXT DEFAULT 'USD',
                condition TEXT DEFAULT 'above',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                triggered_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                feedback_text TEXT,
                feedback_type TEXT DEFAULT 'general',
                rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """
        ]
        
        for table_sql in tables:
            await conn.execute(table_sql)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active)",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_activities_timestamp ON user_activities(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_progress_user_id ON lesson_progress(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_quiz_results_user_id ON quiz_results(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status)",
        ]
        
        for index_sql in indexes:
            await conn.execute(index_sql)
        
        await conn.commit()
    
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None, 
                      chat_id: int = None) -> bool:
        """Add or update user"""
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, chat_id, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, username, first_name, last_name, chat_id, datetime.now())
                )
                await conn.commit()
                
                # Log activity
                await self._log_activity(conn, user_id, "user_registered", {
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                })
                
                return True
        except Exception as e:
            logger.log_error(e, {"operation": "add_user", "user_id": user_id})
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            async with self.get_connection() as conn:
                cursor = await conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.log_error(e, {"operation": "get_user", "user_id": user_id})
            return None
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get comprehensive user statistics with single query"""
        try:
            async with self.get_connection() as conn:
                # Single query with JOINs to get all stats
                cursor = await conn.execute(
                    """
                    SELECT 
                        u.*,
                        COUNT(DISTINCT lp.id) as completed_lessons,
                        COUNT(DISTINCT CASE WHEN lp.audio_listened = 1 THEN lp.id END) as audio_lessons,
                        COUNT(DISTINCT qr.id) as total_quizzes,
                        COALESCE(AVG(CAST(qr.score AS FLOAT) / qr.total_questions * 100), 0) as avg_quiz_score,
                        MAX(qr.score) as best_quiz_score
                    FROM users u
                    LEFT JOIN lesson_progress lp ON u.user_id = lp.user_id
                    LEFT JOIN quiz_results qr ON u.user_id = qr.user_id
                    WHERE u.user_id = ?
                    GROUP BY u.user_id
                    """,
                    (user_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return dict(row)
                return {}
        except Exception as e:
            logger.log_error(e, {"operation": "get_user_stats", "user_id": user_id})
            return {}
    
    async def save_lesson_progress(self, user_id: int, lesson_key: str, 
                                 completion_time: int = None, 
                                 audio_listened: bool = False) -> bool:
        """Save lesson completion"""
        try:
            async with self.get_connection() as conn:
                # Save lesson progress
                await conn.execute(
                    """
                    INSERT INTO lesson_progress 
                    (user_id, lesson_key, completion_time_seconds, audio_listened)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, lesson_key, completion_time, audio_listened)
                )
                
                # Update user stats
                await conn.execute(
                    """
                    UPDATE users SET 
                        total_lessons_completed = total_lessons_completed + 1,
                        last_active = ?
                    WHERE user_id = ?
                    """,
                    (datetime.now(), user_id)
                )
                
                await conn.commit()
                
                # Log activity
                await self._log_activity(conn, user_id, "lesson_completed", {
                    "lesson_key": lesson_key,
                    "completion_time": completion_time,
                    "audio_listened": audio_listened
                })
                
                return True
        except Exception as e:
            logger.log_error(e, {"operation": "save_lesson_progress", "user_id": user_id})
            return False
    
    async def save_quiz_result(self, user_id: int, quiz_name: str, 
                             score: int, total_questions: int, 
                             answers: List = None, time_taken: int = None) -> bool:
        """Save quiz result"""
        try:
            async with self.get_connection() as conn:
                # Save quiz result
                await conn.execute(
                    """
                    INSERT INTO quiz_results 
                    (user_id, quiz_name, score, total_questions, answers, time_taken_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, quiz_name, score, total_questions, 
                     json.dumps(answers) if answers else None, time_taken)
                )
                
                # Update user stats
                await conn.execute(
                    """
                    UPDATE users SET 
                        total_quizzes_taken = total_quizzes_taken + 1,
                        last_active = ?
                    WHERE user_id = ?
                    """,
                    (datetime.now(), user_id)
                )
                
                await conn.commit()
                
                # Log activity
                await self._log_activity(conn, user_id, "quiz_completed", {
                    "quiz_name": quiz_name,
                    "score": score,
                    "total_questions": total_questions,
                    "percentage": (score / total_questions) * 100 if total_questions > 0 else 0
                })
                
                return True
        except Exception as e:
            logger.log_error(e, {"operation": "save_quiz_result", "user_id": user_id})
            return False
    
    async def create_price_alert(self, user_id: int, target_price: float, 
                               currency: str = "USD", condition: str = "above") -> Optional[int]:
        """Create price alert"""
        try:
            async with self.get_connection() as conn:
                cursor = await conn.execute(
                    """
                    INSERT INTO price_alerts (user_id, target_price, currency, condition)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, target_price, currency, condition)
                )
                await conn.commit()
                
                alert_id = cursor.lastrowid
                
                # Log activity
                await self._log_activity(conn, user_id, "price_alert_created", {
                    "alert_id": alert_id,
                    "target_price": target_price,
                    "currency": currency,
                    "condition": condition
                })
                
                return alert_id
        except Exception as e:
            logger.log_error(e, {"operation": "create_price_alert", "user_id": user_id})
            return None
    
    async def get_active_price_alerts(self) -> List[Dict]:
        """Get all active price alerts"""
        try:
            async with self.get_connection() as conn:
                cursor = await conn.execute(
                    """
                    SELECT pa.*, u.chat_id, u.first_name 
                    FROM price_alerts pa
                    JOIN users u ON pa.user_id = u.user_id
                    WHERE pa.is_active = 1 AND pa.triggered_at IS NULL
                    """
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.log_error(e, {"operation": "get_active_price_alerts"})
            return []
    
    async def trigger_price_alert(self, alert_id: int) -> bool:
        """Mark price alert as triggered"""
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    UPDATE price_alerts 
                    SET triggered_at = ?, is_active = 0
                    WHERE id = ?
                    """,
                    (datetime.now(), alert_id)
                )
                await conn.commit()
                return True
        except Exception as e:
            logger.log_error(e, {"operation": "trigger_price_alert", "alert_id": alert_id})
            return False
    
    async def get_analytics(self, days: int = 7) -> Dict:
        """Get system analytics"""
        try:
            async with self.get_connection() as conn:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                start_date = start_date.replace(day=start_date.day - days)
                
                # User analytics
                cursor = await conn.execute(
                    """
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(CASE WHEN created_at >= ? THEN 1 END) as new_users,
                        COUNT(CASE WHEN last_active >= ? THEN 1 END) as active_users
                    FROM users
                    """,
                    (start_date, start_date)
                )
                user_stats = await cursor.fetchone()
                
                # Activity analytics
                cursor = await conn.execute(
                    """
                    SELECT activity_type, COUNT(*) as count
                    FROM user_activities
                    WHERE timestamp >= ?
                    GROUP BY activity_type
                    ORDER BY count DESC
                    """,
                    (start_date,)
                )
                activity_stats = await cursor.fetchall()
                
                # Lesson analytics
                cursor = await conn.execute(
                    """
                    SELECT 
                        lesson_key, 
                        COUNT(*) as completions,
                        AVG(completion_time_seconds) as avg_time
                    FROM lesson_progress
                    WHERE completed_at >= ?
                    GROUP BY lesson_key
                    ORDER BY completions DESC
                    """,
                    (start_date,)
                )
                lesson_stats = await cursor.fetchall()
                
                return {
                    "users": dict(user_stats) if user_stats else {},
                    "activities": [dict(row) for row in activity_stats],
                    "lessons": [dict(row) for row in lesson_stats],
                    "period_days": days
                }
        except Exception as e:
            logger.log_error(e, {"operation": "get_analytics"})
            return {}
    
    async def _log_activity(self, conn: aiosqlite.Connection, user_id: int, 
                          activity_type: str, activity_data: Dict = None):
        """Log user activity"""
        try:
            await conn.execute(
                """
                INSERT INTO user_activities (user_id, activity_type, activity_data)
                VALUES (?, ?, ?)
                """,
                (user_id, activity_type, json.dumps(activity_data or {}))
            )
        except Exception as e:
            logger.log_error(e, {"operation": "_log_activity", "user_id": user_id})
    
    async def close(self):
        """Close database connections"""
        await self.pool.close_all()


# Global async database manager instance
async_db_manager = AsyncDatabaseManager()


# Legacy synchronous database manager for backward compatibility
class LegacyDatabaseManager:
    """Legacy synchronous database manager"""
    
    def __init__(self, db_path: str = "bitmshauri.db"):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Get synchronous database connection"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.log_error(e, {"operation": "legacy_db_connection"})
            raise
        finally:
            if conn:
                conn.close()
    
    def add_user(self, user_id: int, username: str = None, 
                first_name: str = None, last_name: str = None, 
                chat_id: int = None) -> bool:
        """Add user (synchronous)"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, chat_id, last_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, username, first_name, last_name, chat_id, datetime.now())
                )
                return True
        except Exception as e:
            logger.log_error(e, {"operation": "legacy_add_user", "user_id": user_id})
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user (synchronous)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE user_id = ?", (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.log_error(e, {"operation": "legacy_get_user", "user_id": user_id})
            return None


# Global legacy database manager instance
legacy_db_manager = LegacyDatabaseManager()
