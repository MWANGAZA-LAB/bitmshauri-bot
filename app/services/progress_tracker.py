from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.enhanced_database import get_user_stats, track_lesson_completion, track_user_activity
from app.utils.logger import logger

class UserProgressTracker:
    """Comprehensive user progress tracking and gamification"""
    
    def __init__(self):
        self.achievement_definitions = {
            'first_lesson': {
                'name': 'Mwanafunzi wa Kwanza',
                'description': 'Maliza somo lako la kwanza',
                'icon': '🎯',
                'points': 10
            },
            'quiz_master': {
                'name': 'Bingwa wa Maswali',
                'description': 'Pata alama 80% au zaidi katika jaribio',
                'icon': '🏆',
                'points': 25
            },
            'consistent_learner': {
                'name': 'Mwanafunzi Mzuri',
                'description': 'Jifunze kwa siku 3 mfululizo',
                'icon': '📚',
                'points': 30
            },
            'audio_enthusiast': {
                'name': 'Mpenda Sauti',
                'description': 'Sikiliza masomo 5 kwa sauti',
                'icon': '🎵',
                'points': 20
            },
            'bitcoin_expert': {
                'name': 'Mtaalamu wa Bitcoin',
                'description': 'Maliza masomo yote ya msingi',
                'icon': '🚀',
                'points': 50
            },
            'calculator_user': {
                'name': 'Mwenda Kwa Hesabu',
                'description': 'Tumia hesabu marathezo 10',
                'icon': '🧮',
                'points': 15
            }
        }
        
        self.lesson_modules = {
            'basics': [
                'kwa_nini_bitcoin', 'bitcoin_ni_nini', 'p2p_inafanyaje'
            ],
            'security': [
                'kufungua_pochi', 'usalama_pochi', 'kupoteza_ufunguo'
            ],
            'advanced': [
                'blockchain_usalama', 'faida_na_hatari', 'mfano_matumizi'
            ]
        }
    
    async def get_user_progress(self, user_id: int) -> Dict:
        """Get comprehensive user progress report"""
        try:
            stats = get_user_stats(user_id)
            if not stats:
                return self._create_empty_progress()
            
            # Calculate learning streaks
            streak_info = await self._calculate_learning_streak(user_id)
            
            # Get achievements
            achievements = await self._check_achievements(user_id, stats)
            
            # Calculate module progress
            module_progress = await self._calculate_module_progress(user_id)
            
            # Calculate overall progress percentage
            overall_progress = self._calculate_overall_progress(stats, module_progress)
            
            return {
                'user_info': stats.get('user_info', {}),
                'lessons': stats.get('lessons', {}),
                'quizzes': stats.get('quizzes', {}),
                'streak': streak_info,
                'achievements': achievements,
                'modules': module_progress,
                'overall_progress': overall_progress,
                'next_goals': self._get_next_goals(stats, achievements)
            }
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_user_progress", "user_id": user_id})
            return self._create_empty_progress()
    
    def _create_empty_progress(self) -> Dict:
        """Create empty progress for new users"""
        return {
            'user_info': {},
            'lessons': {'completed_lessons': 0, 'audio_lessons': 0},
            'quizzes': {'total_quizzes': 0, 'avg_score': 0, 'best_score': 0},
            'streak': {'current_streak': 0, 'longest_streak': 0},
            'achievements': [],
            'modules': {},
            'overall_progress': 0,
            'next_goals': []
        }
    
    async def _calculate_learning_streak(self, user_id: int) -> Dict:
        """Calculate user's learning streak"""
        try:
            from app.enhanced_database import db_connection
            
            with db_connection() as cursor:
                # Get user activities from last 30 days
                cursor.execute('''
                    SELECT DATE(timestamp) as activity_date
                    FROM user_activities
                    WHERE user_id = ? 
                    AND activity_type IN ('lesson_completed', 'quiz_completed')
                    AND timestamp >= date('now', '-30 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY activity_date DESC
                ''', (user_id,))
                
                activity_dates = [row[0] for row in cursor.fetchall()]
                
                if not activity_dates:
                    return {'current_streak': 0, 'longest_streak': 0, 'last_activity': None}
                
                # Calculate current streak
                current_streak = 0
                today = datetime.now().date()
                
                for i, date_str in enumerate(activity_dates):
                    activity_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    expected_date = today - timedelta(days=i)
                    
                    if activity_date == expected_date:
                        current_streak += 1
                    else:
                        break
                
                # Calculate longest streak
                longest_streak = 0
                temp_streak = 1
                
                for i in range(1, len(activity_dates)):
                    prev_date = datetime.strptime(activity_dates[i-1], '%Y-%m-%d').date()
                    curr_date = datetime.strptime(activity_dates[i], '%Y-%m-%d').date()
                    
                    if (prev_date - curr_date).days == 1:
                        temp_streak += 1
                    else:
                        longest_streak = max(longest_streak, temp_streak)
                        temp_streak = 1
                
                longest_streak = max(longest_streak, temp_streak)
                
                return {
                    'current_streak': current_streak,
                    'longest_streak': longest_streak,
                    'last_activity': activity_dates[0] if activity_dates else None
                }
                
        except Exception as e:
            logger.log_error(e, {"operation": "_calculate_learning_streak", "user_id": user_id})
            return {'current_streak': 0, 'longest_streak': 0, 'last_activity': None}
    
    async def _check_achievements(self, user_id: int, stats: Dict) -> List[Dict]:
        """Check and return user achievements"""
        try:
            from app.enhanced_database import db_connection
            
            achievements = []
            user_info = stats.get('user_info', {})
            lessons = stats.get('lessons', {})
            quizzes = stats.get('quizzes', {})
            
            # First lesson achievement
            if lessons.get('completed_lessons', 0) >= 1:
                achievements.append(self.achievement_definitions['first_lesson'])
            
            # Quiz master achievement
            if quizzes.get('avg_score', 0) >= 80:
                achievements.append(self.achievement_definitions['quiz_master'])
            
            # Audio enthusiast achievement
            if lessons.get('audio_lessons', 0) >= 5:
                achievements.append(self.achievement_definitions['audio_enthusiast'])
            
            # Bitcoin expert achievement
            total_basic_lessons = len(self.lesson_modules['basics'] + 
                                    self.lesson_modules['security'] + 
                                    self.lesson_modules['advanced'])
            if lessons.get('completed_lessons', 0) >= total_basic_lessons:
                achievements.append(self.achievement_definitions['bitcoin_expert'])
            
            # Calculator user achievement
            with db_connection() as cursor:
                cursor.execute('''
                    SELECT COUNT(*) FROM user_activities
                    WHERE user_id = ? AND activity_type = 'calculator_success'
                ''', (user_id,))
                calc_uses = cursor.fetchone()[0]
                
                if calc_uses >= 10:
                    achievements.append(self.achievement_definitions['calculator_user'])
            
            # Consistent learner achievement (check streak)
            streak_info = await self._calculate_learning_streak(user_id)
            if streak_info.get('current_streak', 0) >= 3:
                achievements.append(self.achievement_definitions['consistent_learner'])
            
            return achievements
            
        except Exception as e:
            logger.log_error(e, {"operation": "_check_achievements", "user_id": user_id})
            return []
    
    async def _calculate_module_progress(self, user_id: int) -> Dict:
        """Calculate progress for each learning module"""
        try:
            from app.enhanced_database import db_connection
            
            with db_connection() as cursor:
                cursor.execute('''
                    SELECT lesson_key FROM lesson_progress 
                    WHERE user_id = ?
                ''', (user_id,))
                
                completed_lessons = {row[0] for row in cursor.fetchall()}
                
                module_progress = {}
                
                for module_name, lessons in self.lesson_modules.items():
                    completed_in_module = len([l for l in lessons if l in completed_lessons])
                    total_in_module = len(lessons)
                    progress_percent = (completed_in_module / total_in_module) * 100 if total_in_module > 0 else 0
                    
                    module_progress[module_name] = {
                        'completed': completed_in_module,
                        'total': total_in_module,
                        'percentage': round(progress_percent, 1),
                        'status': 'completed' if progress_percent == 100 else 
                                 'in_progress' if progress_percent > 0 else 'not_started'
                    }
                
                return module_progress
                
        except Exception as e:
            logger.log_error(e, {"operation": "_calculate_module_progress", "user_id": user_id})
            return {}
    
    def _calculate_overall_progress(self, stats: Dict, module_progress: Dict) -> float:
        """Calculate overall progress percentage"""
        try:
            # Weight different aspects of progress
            lesson_weight = 0.4
            quiz_weight = 0.3
            module_weight = 0.3
            
            # Lesson progress (out of total available lessons)
            total_lessons = sum(len(lessons) for lessons in self.lesson_modules.values())
            lesson_progress = min((stats.get('lessons', {}).get('completed_lessons', 0) / total_lessons) * 100, 100)
            
            # Quiz progress (based on average score)
            quiz_progress = min(stats.get('quizzes', {}).get('avg_score', 0), 100)
            
            # Module completion progress
            module_completion = 0
            if module_progress:
                completed_modules = sum(1 for module in module_progress.values() if module['status'] == 'completed')
                module_completion = (completed_modules / len(module_progress)) * 100
            
            overall = (lesson_progress * lesson_weight + 
                      quiz_progress * quiz_weight + 
                      module_completion * module_weight)
            
            return round(overall, 1)
            
        except Exception as e:
            logger.log_error(e, {"operation": "_calculate_overall_progress"})
            return 0.0
    
    def _get_next_goals(self, stats: Dict, achievements: List[Dict]) -> List[str]:
        """Get personalized next goals for the user"""
        goals = []
        
        try:
            lessons = stats.get('lessons', {})
            quizzes = stats.get('quizzes', {})
            
            # Achievement-based goals
            achievement_names = {ach['name'] for ach in achievements}
            
            if 'Mwanafunzi wa Kwanza' not in achievement_names:
                goals.append("📚 Maliza somo lako la kwanza")
            
            if 'Bingwa wa Maswali' not in achievement_names:
                goals.append("🎯 Pata alama 80% katika jaribio")
            
            if 'Mpenda Sauti' not in achievement_names:
                goals.append("🎵 Sikiliza masomo 5 kwa sauti")
            
            # Progress-based goals
            if lessons.get('completed_lessons', 0) < 3:
                goals.append("📖 Maliza masomo 3 ya msingi")
            
            if quizzes.get('total_quizzes', 0) == 0:
                goals.append("❓ Jaribu jaribio lako la kwanza")
            
            # If no specific goals, give general encouragement
            if not goals:
                goals.append("🚀 Endelea kujifunza na kuchunguza!")
            
            return goals[:3]  # Return max 3 goals
            
        except Exception as e:
            logger.log_error(e, {"operation": "_get_next_goals"})
            return ["📚 Endelea kujifunza!"]
    
    def format_progress_report(self, progress: Dict, user_name: str = "Mwanafunzi") -> str:
        """Format progress report into user-friendly message"""
        try:
            if not progress or not progress.get('user_info'):
                return (
                    f"👋 Karibu {user_name}!\n\n"
                    "🎯 Anza safari yako ya kujifunza Bitcoin!\n"
                    "Chagua somo la kwanza kuanza."
                )
            
            lessons = progress.get('lessons', {})
            quizzes = progress.get('quizzes', {})
            streak = progress.get('streak', {})
            achievements = progress.get('achievements', [])
            overall = progress.get('overall_progress', 0)
            
            # Progress bar
            progress_bar = self._create_progress_bar(overall)
            
            message = (
                f"📊 *Ripoti ya Maendeleo ya {user_name}*\n\n"
                f"🎯 *Maendeleo ya Jumla:* {overall}%\n"
                f"{progress_bar}\n\n"
                f"📚 *Masomo:* {lessons.get('completed_lessons', 0)} yamekamilika\n"
                f"🎵 *Sauti:* {lessons.get('audio_lessons', 0)} zimesikilizwa\n"
                f"📝 *Majaribio:* {quizzes.get('total_quizzes', 0)} yamefanywa\n"
                f"📈 *Wastani:* {quizzes.get('avg_score', 0):.1f}%\n"
                f"🔥 *Mfululizo:* siku {streak.get('current_streak', 0)}\n\n"
            )
            
            # Achievements
            if achievements:
                message += "🏆 *Mafanikio Yaliyopatikana:*\n"
                for ach in achievements[:3]:  # Show max 3 achievements
                    message += f"{ach['icon']} {ach['name']}\n"
                if len(achievements) > 3:
                    message += f"... na mengine {len(achievements) - 3}\n"
                message += "\n"
            
            # Next goals
            next_goals = progress.get('next_goals', [])
            if next_goals:
                message += "🎯 *Malengo ya Hivi Karibuni:*\n"
                for goal in next_goals:
                    message += f"• {goal}\n"
                message += "\n"
            
            message += "💪 Endelea hivyo! Umefanya kazi nzuri!"
            
            return message
            
        except Exception as e:
            logger.log_error(e, {"operation": "format_progress_report"})
            return "Kuna tatizo la kuonyesha ripoti ya maendeleo."
    
    def _create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create visual progress bar"""
        filled = int((percentage / 100) * length)
        empty = length - filled
        return "█" * filled + "░" * empty + f" {percentage}%"

# Global progress tracker instance
progress_tracker = UserProgressTracker()
