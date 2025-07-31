import json
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from app.enhanced_database import DatabaseManager
from app.utils.logger import logger
from app.services.multi_language import multi_lang_bot

class CommunityManager:
    """Community features including groups, discussions, and peer learning"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self._init_community_tables()
        
        # Community settings
        self.max_group_size = 50
        self.max_groups_per_user = 5
        self.discussion_retention_days = 30
        
        # Community roles
        self.roles = {
            'member': {'level': 1, 'permissions': ['read', 'post']},
            'moderator': {'level': 2, 'permissions': ['read', 'post', 'moderate']},
            'admin': {'level': 3, 'permissions': ['read', 'post', 'moderate', 'manage']}
        }
    
    def _init_community_tables(self):
        """Initialize community-related database tables"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Study groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    creator_id INTEGER NOT NULL,
                    language TEXT DEFAULT 'sw',
                    max_members INTEGER DEFAULT 20,
                    is_public BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Group memberships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_memberships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (group_id) REFERENCES study_groups (id),
                    UNIQUE(group_id, user_id)
                )
            ''')
            
            # Group discussions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_discussions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    reply_to_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (group_id) REFERENCES study_groups (id),
                    FOREIGN KEY (reply_to_id) REFERENCES group_discussions (id)
                )
            ''')
            
            # Peer achievements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS peer_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_type TEXT NOT NULL,
                    achievement_data TEXT,
                    awarded_by INTEGER,
                    group_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (awarded_by) REFERENCES group_memberships (user_id),
                    FOREIGN KEY (group_id) REFERENCES study_groups (id)
                )
            ''')
            
            # Study challenges table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    challenge_type TEXT NOT NULL,
                    difficulty_level TEXT DEFAULT 'beginner',
                    language TEXT DEFAULT 'sw',
                    challenge_data TEXT,
                    creator_id INTEGER,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Challenge participations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS challenge_participations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    challenge_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    group_id INTEGER,
                    participation_data TEXT,
                    score INTEGER DEFAULT 0,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (challenge_id) REFERENCES study_challenges (id),
                    FOREIGN KEY (group_id) REFERENCES study_groups (id),
                    UNIQUE(challenge_id, user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.logger.info("Community tables initialized successfully")
            
        except Exception as e:
            logger.log_error(e, {"operation": "init_community_tables"})
    
    def create_study_group(self, 
                          creator_id: int, 
                          name: str, 
                          description: str = "",
                          language: str = 'sw',
                          max_members: int = 20,
                          is_public: bool = True) -> Optional[int]:
        """Create a new study group"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Check if user has reached group creation limit
            cursor.execute('''
                SELECT COUNT(*) FROM study_groups 
                WHERE creator_id = ?
            ''', (creator_id,))
            
            group_count = cursor.fetchone()[0]
            if group_count >= self.max_groups_per_user:
                conn.close()
                return None
            
            # Create the group
            cursor.execute('''
                INSERT INTO study_groups 
                (name, description, creator_id, language, max_members, is_public)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, description, creator_id, language, max_members, is_public))
            
            group_id = cursor.lastrowid
            
            # Add creator as admin
            cursor.execute('''
                INSERT INTO group_memberships (group_id, user_id, role)
                VALUES (?, ?, 'admin')
            ''', (group_id, creator_id))
            
            conn.commit()
            conn.close()
            
            logger.log_user_action(creator_id, 'group_created', {
                'group_id': group_id,
                'group_name': name,
                'language': language
            })
            
            return group_id
            
        except Exception as e:
            logger.log_error(e, {"operation": "create_study_group"})
            return None
    
    def join_study_group(self, user_id: int, group_id: int) -> bool:
        """Join a study group"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Check if group exists and is public
            cursor.execute('''
                SELECT name, max_members, is_public 
                FROM study_groups 
                WHERE id = ?
            ''', (group_id,))
            
            group_info = cursor.fetchone()
            if not group_info or not group_info[2]:  # Group doesn't exist or is private
                conn.close()
                return False
            
            # Check current member count
            cursor.execute('''
                SELECT COUNT(*) FROM group_memberships 
                WHERE group_id = ? AND is_active = 1
            ''', (group_id,))
            
            current_members = cursor.fetchone()[0]
            if current_members >= group_info[1]:  # Max members reached
                conn.close()
                return False
            
            # Check if user is already a member
            cursor.execute('''
                SELECT id FROM group_memberships 
                WHERE group_id = ? AND user_id = ?
            ''', (group_id, user_id))
            
            if cursor.fetchone():  # Already a member
                conn.close()
                return False
            
            # Add user to group
            cursor.execute('''
                INSERT INTO group_memberships (group_id, user_id, role)
                VALUES (?, ?, 'member')
            ''', (group_id, user_id))
            
            conn.commit()
            conn.close()
            
            logger.log_user_action(user_id, 'group_joined', {
                'group_id': group_id,
                'group_name': group_info[0]
            })
            
            return True
            
        except Exception as e:
            logger.log_error(e, {"operation": "join_study_group"})
            return False
    
    def leave_study_group(self, user_id: int, group_id: int) -> bool:
        """Leave a study group"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Update membership status
            cursor.execute('''
                UPDATE group_memberships 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE group_id = ? AND user_id = ? AND is_active = 1
            ''', (group_id, user_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            
            logger.log_user_action(user_id, 'group_left', {'group_id': group_id})
            return True
            
        except Exception as e:
            logger.log_error(e, {"operation": "leave_study_group"})
            return False
    
    def post_to_group(self, 
                     user_id: int, 
                     group_id: int, 
                     message: str,
                     message_type: str = 'text',
                     reply_to_id: Optional[int] = None) -> Optional[int]:
        """Post a message to a study group"""
        try:
            # Check if user is a member of the group
            if not self.is_group_member(user_id, group_id):
                return None
            
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO group_discussions 
                (group_id, user_id, message, message_type, reply_to_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (group_id, user_id, message, message_type, reply_to_id))
            
            message_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.log_user_action(user_id, 'group_message_posted', {
                'group_id': group_id,
                'message_id': message_id,
                'message_type': message_type
            })
            
            return message_id
            
        except Exception as e:
            logger.log_error(e, {"operation": "post_to_group"})
            return None
    
    def get_group_messages(self, 
                          group_id: int, 
                          user_id: int,
                          limit: int = 20,
                          offset: int = 0) -> List[Dict]:
        """Get recent messages from a group"""
        try:
            # Check if user is a member
            if not self.is_group_member(user_id, group_id):
                return []
            
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    gd.id, gd.user_id, gd.message, gd.message_type,
                    gd.reply_to_id, gd.created_at,
                    u.username
                FROM group_discussions gd
                LEFT JOIN users u ON gd.user_id = u.user_id
                WHERE gd.group_id = ? AND gd.is_deleted = 0
                ORDER BY gd.created_at DESC
                LIMIT ? OFFSET ?
            ''', (group_id, limit, offset))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'user_id': row[1],
                    'message': row[2],
                    'message_type': row[3],
                    'reply_to_id': row[4],
                    'created_at': row[5],
                    'username': row[6] or f"User {row[1]}"
                })
            
            conn.close()
            return messages
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_group_messages"})
            return []
    
    def is_group_member(self, user_id: int, group_id: int) -> bool:
        """Check if user is an active member of a group"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM group_memberships 
                WHERE group_id = ? AND user_id = ? AND is_active = 1
            ''', (group_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.log_error(e, {"operation": "is_group_member"})
            return False
    
    def get_user_groups(self, user_id: int) -> List[Dict]:
        """Get all groups a user is a member of"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    sg.id, sg.name, sg.description, sg.language,
                    gm.role, gm.joined_at,
                    COUNT(gm2.user_id) as member_count
                FROM study_groups sg
                JOIN group_memberships gm ON sg.id = gm.group_id
                LEFT JOIN group_memberships gm2 ON sg.id = gm2.group_id AND gm2.is_active = 1
                WHERE gm.user_id = ? AND gm.is_active = 1
                GROUP BY sg.id, sg.name, sg.description, sg.language, gm.role, gm.joined_at
                ORDER BY gm.joined_at DESC
            ''', (user_id,))
            
            groups = []
            for row in cursor.fetchall():
                groups.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'language': row[3],
                    'role': row[4],
                    'joined_at': row[5],
                    'member_count': row[6]
                })
            
            conn.close()
            return groups
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_user_groups"})
            return []
    
    def get_public_groups(self, language: str = None, limit: int = 20) -> List[Dict]:
        """Get list of public groups available to join"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    sg.id, sg.name, sg.description, sg.language,
                    sg.max_members, sg.created_at,
                    COUNT(gm.user_id) as member_count
                FROM study_groups sg
                LEFT JOIN group_memberships gm ON sg.id = gm.group_id AND gm.is_active = 1
                WHERE sg.is_public = 1
            '''
            
            params = []
            if language:
                query += ' AND sg.language = ?'
                params.append(language)
            
            query += '''
                GROUP BY sg.id, sg.name, sg.description, sg.language, sg.max_members, sg.created_at
                HAVING member_count < sg.max_members
                ORDER BY sg.created_at DESC
                LIMIT ?
            '''
            params.append(limit)
            
            cursor.execute(query, params)
            
            groups = []
            for row in cursor.fetchall():
                groups.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'language': row[3],
                    'max_members': row[4],
                    'created_at': row[5],
                    'member_count': row[6]
                })
            
            conn.close()
            return groups
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_public_groups"})
            return []
    
    def create_study_challenge(self,
                              title: str,
                              description: str,
                              challenge_type: str,
                              difficulty_level: str = 'beginner',
                              language: str = 'sw',
                              challenge_data: Dict = None,
                              creator_id: int = None,
                              duration_days: int = 7) -> Optional[int]:
        """Create a new study challenge"""
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)
            
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO study_challenges 
                (title, description, challenge_type, difficulty_level, 
                 language, challenge_data, creator_id, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, challenge_type, difficulty_level,
                  language, json.dumps(challenge_data or {}), 
                  creator_id, start_date, end_date))
            
            challenge_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            if creator_id:
                logger.log_user_action(creator_id, 'challenge_created', {
                    'challenge_id': challenge_id,
                    'challenge_type': challenge_type
                })
            
            return challenge_id
            
        except Exception as e:
            logger.log_error(e, {"operation": "create_study_challenge"})
            return None
    
    def join_challenge(self, user_id: int, challenge_id: int, group_id: int = None) -> bool:
        """Join a study challenge"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Check if challenge exists and is active
            cursor.execute('''
                SELECT title FROM study_challenges 
                WHERE id = ? AND is_active = 1 AND end_date > CURRENT_TIMESTAMP
            ''', (challenge_id,))
            
            if not cursor.fetchone():
                conn.close()
                return False
            
            # Check if user already joined
            cursor.execute('''
                SELECT id FROM challenge_participations 
                WHERE challenge_id = ? AND user_id = ?
            ''', (challenge_id, user_id))
            
            if cursor.fetchone():
                conn.close()
                return False
            
            # Join challenge
            cursor.execute('''
                INSERT INTO challenge_participations 
                (challenge_id, user_id, group_id, participation_data)
                VALUES (?, ?, ?, ?)
            ''', (challenge_id, user_id, group_id, json.dumps({})))
            
            conn.commit()
            conn.close()
            
            logger.log_user_action(user_id, 'challenge_joined', {
                'challenge_id': challenge_id,
                'group_id': group_id
            })
            
            return True
            
        except Exception as e:
            logger.log_error(e, {"operation": "join_challenge"})
            return False
    
    def get_active_challenges(self, language: str = None, limit: int = 10) -> List[Dict]:
        """Get active study challenges"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    sc.id, sc.title, sc.description, sc.challenge_type,
                    sc.difficulty_level, sc.language, sc.start_date, sc.end_date,
                    COUNT(cp.user_id) as participant_count
                FROM study_challenges sc
                LEFT JOIN challenge_participations cp ON sc.id = cp.challenge_id
                WHERE sc.is_active = 1 AND sc.end_date > CURRENT_TIMESTAMP
            '''
            
            params = []
            if language:
                query += ' AND sc.language = ?'
                params.append(language)
            
            query += '''
                GROUP BY sc.id
                ORDER BY sc.start_date DESC
                LIMIT ?
            '''
            params.append(limit)
            
            cursor.execute(query, params)
            
            challenges = []
            for row in cursor.fetchall():
                challenges.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'challenge_type': row[3],
                    'difficulty_level': row[4],
                    'language': row[5],
                    'start_date': row[6],
                    'end_date': row[7],
                    'participant_count': row[8]
                })
            
            conn.close()
            return challenges
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_active_challenges"})
            return []
    
    def get_community_stats(self) -> Dict:
        """Get community statistics"""
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            
            # Group statistics
            cursor.execute('SELECT COUNT(*) FROM study_groups WHERE is_public = 1')
            public_groups = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM group_memberships WHERE is_active = 1')
            total_memberships = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM group_discussions WHERE is_deleted = 0')
            total_messages = cursor.fetchone()[0]
            
            # Challenge statistics
            cursor.execute('SELECT COUNT(*) FROM study_challenges WHERE is_active = 1')
            active_challenges = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM challenge_participations')
            challenge_participations = cursor.fetchone()[0]
            
            # Language distribution
            cursor.execute('''
                SELECT language, COUNT(*) 
                FROM study_groups 
                GROUP BY language
            ''')
            language_distribution = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'public_groups': public_groups,
                'total_memberships': total_memberships,
                'total_messages': total_messages,
                'active_challenges': active_challenges,
                'challenge_participations': challenge_participations,
                'language_distribution': language_distribution,
                'max_group_size': self.max_group_size,
                'max_groups_per_user': self.max_groups_per_user
            }
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_community_stats"})
            return {}

# Global community manager instance
community_manager = CommunityManager()

# Helper functions for easy integration
def create_new_study_group(creator_id: int, name: str, description: str = "", language: str = 'sw') -> Optional[int]:
    """Create a new study group"""
    return community_manager.create_study_group(creator_id, name, description, language)

def join_group(user_id: int, group_id: int) -> bool:
    """Join a study group"""
    return community_manager.join_study_group(user_id, group_id)

def post_group_message(user_id: int, group_id: int, message: str) -> Optional[int]:
    """Post message to group"""
    return community_manager.post_to_group(user_id, group_id, message)

def get_user_study_groups(user_id: int) -> List[Dict]:
    """Get user's study groups"""
    return community_manager.get_user_groups(user_id)

def get_available_groups(language: str = None) -> List[Dict]:
    """Get available public groups"""
    return community_manager.get_public_groups(language)
