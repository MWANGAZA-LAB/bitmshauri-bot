import unittest
import asyncio
import os
import tempfile
import sqlite3
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import sys

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.enhanced_database import DatabaseManager
from app.utils.logger import logger
from app.utils.rate_limiter import rate_limiter
from app.services.price_service import BitcoinPriceMonitor
from app.services.calculator import BitcoinCalculator
from app.services.progress_tracker import UserProgressTracker
from app.services.content_manager import content_manager
from app.services.multi_language import multi_lang_bot
from app.services.community import community_manager


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown"""

    def setUp(self):
        """Set up test environment"""
        self.test_db_path = os.path.join(
            tempfile.gettempdir(), "test_bitmshauri.db"
        )
        self.test_user_id = 12345
        self.test_username = "test_user"

        # Clean up any existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except:
                pass


class TestDatabaseManager(BaseTestCase):
    """Test database operations"""

    def test_database_initialization(self):
        """Test database creation and initialization"""
        db_manager = DatabaseManager(self.test_db_path)

        # Check if database file was created
        self.assertTrue(os.path.exists(self.test_db_path))

        # Check if tables were created
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = [
            "users",
            "user_activities",
            "lesson_progress",
            "quiz_results",
            "price_alerts",
        ]
        for table in expected_tables:
            self.assertIn(table, tables)

        conn.close()

    def test_add_user(self):
        """Test adding a new user"""
        db_manager = DatabaseManager(self.test_db_path)

        result = db_manager.add_user(self.test_user_id, self.test_username)
        self.assertTrue(result)

        # Check if user was added
        user = db_manager.get_user(self.test_user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], self.test_username)

    def test_duplicate_user(self):
        """Test handling of duplicate user addition"""
        db_manager = DatabaseManager(self.test_db_path)

        # Add user first time
        result1 = db_manager.add_user(self.test_user_id, self.test_username)
        self.assertTrue(result1)

        # Try to add same user again
        result2 = db_manager.add_user(self.test_user_id, self.test_username)
        self.assertFalse(result2)

    def test_lesson_progress(self):
        """Test lesson progress tracking"""
        db_manager = DatabaseManager(self.test_db_path)
        db_manager.add_user(self.test_user_id, self.test_username)

        lesson_key = "test_lesson"
        result = db_manager.update_lesson_progress(
            self.test_user_id, lesson_key, True
        )
        self.assertTrue(result)

        # Check progress
        progress = db_manager.get_user_progress(self.test_user_id)
        self.assertIsNotNone(progress)
        self.assertIn(
            lesson_key, [p["lesson_key"] for p in progress.get("lessons", [])]
        )


class TestRateLimiter(BaseTestCase):
    """Test rate limiting functionality"""

    def test_rate_limiting_basic(self):
        """Test basic rate limiting"""
        # Reset rate limiter
        rate_limiter.user_actions.clear()

        # Should allow first few actions
        for i in range(5):
            result = rate_limiter.check_rate_limit(
                self.test_user_id, "message"
            )
            self.assertTrue(result)

        # Should start blocking after limit
        result = rate_limiter.check_rate_limit(self.test_user_id, "message")
        # This depends on the configured limits, adjust as needed

    def test_rate_limiting_different_actions(self):
        """Test rate limiting for different action types"""
        rate_limiter.user_actions.clear()

        # Different actions should have separate limits
        message_result = rate_limiter.check_rate_limit(
            self.test_user_id, "message"
        )
        quiz_result = rate_limiter.check_rate_limit(self.test_user_id, "quiz")

        self.assertTrue(message_result)
        self.assertTrue(quiz_result)

    def test_penalty_system(self):
        """Test penalty system for rate limiting"""
        rate_limiter.user_actions.clear()
        rate_limiter.user_penalties.clear()

        # Apply penalty
        rate_limiter.apply_penalty(self.test_user_id, 60)  # 1 minute penalty

        # Check if action is blocked due to penalty
        result = rate_limiter.check_rate_limit(self.test_user_id, "message")
        self.assertFalse(result)


class TestBitcoinCalculator(BaseTestCase):
    """Test Bitcoin calculator functionality"""

    def setUp(self):
        super().setUp()
        self.calculator = BitcoinCalculator()

    @patch("app.services.calculator.BitcoinCalculator._get_current_price")
    def test_usd_to_btc_calculation(self, mock_price):
        """Test USD to BTC conversion"""
        mock_price.return_value = 50000  # Mock Bitcoin price

        result = self.calculator.calculate("100 usd to btc")

        self.assertIsNotNone(result)
        self.assertEqual(result["from_currency"], "usd")
        self.assertEqual(result["to_currency"], "btc")
        self.assertEqual(result["original_amount"], 100)
        self.assertAlmostEqual(
            result["converted_amount"], 0.002, places=6
        )  # 100/50000

    @patch("app.services.calculator.BitcoinCalculator._get_current_price")
    def test_btc_to_usd_calculation(self, mock_price):
        """Test BTC to USD conversion"""
        mock_price.return_value = 50000

        result = self.calculator.calculate("0.1 btc to usd")

        self.assertIsNotNone(result)
        self.assertEqual(result["from_currency"], "btc")
        self.assertEqual(result["to_currency"], "usd")
        self.assertEqual(result["original_amount"], 0.1)
        self.assertEqual(result["converted_amount"], 5000)  # 0.1 * 50000

    def test_invalid_calculation(self):
        """Test handling of invalid calculations"""
        result = self.calculator.calculate("invalid input")
        self.assertIsNone(result)


class TestProgressTracker(BaseTestCase):
    """Test user progress tracking"""

    def setUp(self):
        super().setUp()
        self.tracker = UserProgressTracker(self.test_db_path)

        # Initialize database
        db_manager = DatabaseManager(self.test_db_path)
        db_manager.add_user(self.test_user_id, self.test_username)

    def test_lesson_completion(self):
        """Test lesson completion tracking"""
        lesson_key = "test_lesson"
        result = self.tracker.complete_lesson(self.test_user_id, lesson_key)
        self.assertTrue(result)

        # Check if lesson is marked as completed
        progress = self.tracker.get_user_progress(self.test_user_id)
        completed_lessons = [
            l["lesson_key"] for l in progress.get("completed_lessons", [])
        ]
        self.assertIn(lesson_key, completed_lessons)

    def test_quiz_completion(self):
        """Test quiz completion tracking"""
        quiz_name = "test_quiz"
        score = 85

        result = self.tracker.complete_quiz(
            self.test_user_id, quiz_name, score
        )
        self.assertTrue(result)

        # Check quiz results
        progress = self.tracker.get_user_progress(self.test_user_id)
        quiz_results = progress.get("quiz_results", [])

        test_quiz_result = next(
            (q for q in quiz_results if q["quiz_name"] == quiz_name), None
        )
        self.assertIsNotNone(test_quiz_result)
        self.assertEqual(test_quiz_result["score"], score)

    def test_achievement_unlocking(self):
        """Test achievement system"""
        # Complete multiple lessons to unlock achievement
        for i in range(5):
            self.tracker.complete_lesson(self.test_user_id, f"lesson_{i}")

        achievements = self.tracker.check_achievements(self.test_user_id)
        self.assertIsInstance(achievements, list)

        # Should have some achievements unlocked
        progress = self.tracker.get_user_progress(self.test_user_id)
        self.assertGreater(len(progress.get("achievements", [])), 0)


class TestContentManager(BaseTestCase):
    """Test content management system"""

    def test_get_lesson_content(self):
        """Test retrieving lesson content"""
        lesson = content_manager.get_lesson("intro", "sw")
        self.assertIsNotNone(lesson)
        self.assertIn("content", lesson)
        self.assertIn("title", lesson)

    def test_get_lesson_english(self):
        """Test retrieving English lesson content"""
        lesson = content_manager.get_lesson("intro", "en")
        self.assertIsNotNone(lesson)
        self.assertIn("content", lesson)

    def test_get_quiz_content(self):
        """Test retrieving quiz content"""
        quiz = content_manager.get_quiz("msingi", "sw")
        self.assertIsNotNone(quiz)
        self.assertIsInstance(quiz, list)

        if quiz:  # If quiz has questions
            question = quiz[0]
            self.assertIn("question", question)
            self.assertIn("options", question)
            self.assertIn("answer", question)

    def test_content_validation(self):
        """Test content validation"""
        validation_result = content_manager.validate_content("sw")
        self.assertIn("sw", validation_result)
        self.assertIn("status", validation_result["sw"])


class TestMultiLanguageBot(BaseTestCase):
    """Test multi-language functionality"""

    def test_language_detection_swahili(self):
        """Test Swahili language detection"""
        swahili_text = "Habari za asubuhi, ninahitaji msaada wa Bitcoin"
        language = multi_lang_bot.language_detector.detect_language(
            swahili_text
        )
        self.assertEqual(language, "sw")

    def test_language_detection_english(self):
        """Test English language detection"""
        english_text = "Hello, I need help with Bitcoin"
        language = multi_lang_bot.language_detector.detect_language(
            english_text
        )
        self.assertEqual(language, "en")

    def test_user_language_preference(self):
        """Test user language preference setting"""
        result = multi_lang_bot.set_user_language(self.test_user_id, "en")
        self.assertTrue(result)

        language = multi_lang_bot.get_user_language(self.test_user_id)
        self.assertEqual(language, "en")

    def test_localized_response(self):
        """Test getting localized responses"""
        # Set user language to English
        multi_lang_bot.set_user_language(self.test_user_id, "en")

        response = multi_lang_bot.get_response(self.test_user_id, "welcome")
        self.assertIn("Hello", response)

        # Set to Swahili
        multi_lang_bot.set_user_language(self.test_user_id, "sw")

        response = multi_lang_bot.get_response(self.test_user_id, "welcome")
        self.assertIn("Habari", response)


class TestCommunityFeatures(BaseTestCase):
    """Test community functionality"""

    def setUp(self):
        super().setUp()
        # Initialize community manager with test database
        community_manager.db_manager = DatabaseManager(self.test_db_path)
        community_manager._init_community_tables()

        # Add test user
        community_manager.db_manager.add_user(
            self.test_user_id, self.test_username
        )

    def test_create_study_group(self):
        """Test creating a study group"""
        group_id = community_manager.create_study_group(
            creator_id=self.test_user_id,
            name="Test Bitcoin Group",
            description="Learning Bitcoin together",
            language="sw",
        )

        self.assertIsNotNone(group_id)
        self.assertIsInstance(group_id, int)

    def test_join_study_group(self):
        """Test joining a study group"""
        # Create a group first
        group_id = community_manager.create_study_group(
            creator_id=self.test_user_id, name="Test Group", language="sw"
        )

        # Add another user and try to join
        other_user_id = 67890
        community_manager.db_manager.add_user(other_user_id, "other_user")

        result = community_manager.join_study_group(other_user_id, group_id)
        self.assertTrue(result)

        # Check if user is now a member
        is_member = community_manager.is_group_member(other_user_id, group_id)
        self.assertTrue(is_member)

    def test_group_messaging(self):
        """Test group messaging functionality"""
        # Create group and join
        group_id = community_manager.create_study_group(
            creator_id=self.test_user_id, name="Test Group", language="sw"
        )

        # Post a message
        message_id = community_manager.post_to_group(
            user_id=self.test_user_id,
            group_id=group_id,
            message="Hello everyone!",
        )

        self.assertIsNotNone(message_id)

        # Get messages
        messages = community_manager.get_group_messages(
            group_id, self.test_user_id
        )
        self.assertGreater(len(messages), 0)
        self.assertEqual(messages[0]["message"], "Hello everyone!")


class TestIntegration(BaseTestCase):
    """Integration tests combining multiple components"""

    def setUp(self):
        super().setUp()
        self.db_manager = DatabaseManager(self.test_db_path)
        self.tracker = UserProgressTracker(self.test_db_path)

        # Add test user
        self.db_manager.add_user(self.test_user_id, self.test_username)

    def test_complete_learning_flow(self):
        """Test complete user learning flow"""
        # Set user language
        multi_lang_bot.set_user_language(self.test_user_id, "sw")

        # Complete a lesson
        lesson_result = self.tracker.complete_lesson(
            self.test_user_id, "intro"
        )
        self.assertTrue(lesson_result)

        # Take a quiz
        quiz_result = self.tracker.complete_quiz(
            self.test_user_id, "msingi", 90
        )
        self.assertTrue(quiz_result)

        # Check overall progress
        progress = self.tracker.get_user_progress(self.test_user_id)
        self.assertGreater(len(progress.get("completed_lessons", [])), 0)
        self.assertGreater(len(progress.get("quiz_results", [])), 0)

        # Check achievements
        achievements = self.tracker.check_achievements(self.test_user_id)
        self.assertIsInstance(achievements, list)


class TestAsyncComponents(unittest.IsolatedAsyncioTestCase):
    """Test asynchronous components"""

    async def test_price_service_initialization(self):
        """Test price service initialization"""
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "bitcoin": {
                    "usd": 50000,
                    "usd_24h_change": 2.5,
                    "last_updated": "2024-01-01T00:00:00Z",
                }
            }
            mock_get.return_value.__aenter__.return_value = mock_response

            price_monitor = BitcoinPriceMonitor()
            price_data = await price_monitor.get_current_price()

            self.assertIsNotNone(price_data)
            self.assertIn("usd", price_data)


def run_all_tests():
    """Run all tests and return results"""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_cases = [
        TestDatabaseManager,
        TestRateLimiter,
        TestBitcoinCalculator,
        TestProgressTracker,
        TestContentManager,
        TestMultiLanguageBot,
        TestCommunityFeatures,
        TestIntegration,
    ]

    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)

    # Add async tests
    async_tests = unittest.TestLoader().loadTestsFromTestCase(
        TestAsyncComponents
    )
    test_suite.addTests(async_tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result


def run_specific_test(test_class_name: str):
    """Run a specific test class"""
    test_classes = {
        "database": TestDatabaseManager,
        "rate_limiter": TestRateLimiter,
        "calculator": TestBitcoinCalculator,
        "progress": TestProgressTracker,
        "content": TestContentManager,
        "multilang": TestMultiLanguageBot,
        "community": TestCommunityFeatures,
        "integration": TestIntegration,
        "async": TestAsyncComponents,
    }

    if test_class_name.lower() in test_classes:
        test_class = test_classes[test_class_name.lower()]
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)
    else:
        print(f"Test class '{test_class_name}' not found.")
        print(f"Available test classes: {', '.join(test_classes.keys())}")
        return None


if __name__ == "__main__":
    # Run all tests if script is executed directly
    print("Running BitMshauri Bot Test Suite...")
    print("=" * 50)

    result = run_all_tests()

    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
