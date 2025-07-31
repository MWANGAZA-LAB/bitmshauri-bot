"""
BitMshauri Bot Setup and Installation Script
Automated setup for the enhanced Bitcoin education bot
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_step(message):
    """Print setup step with formatting"""
    print(f"\n🔧 {message}")
    print("=" * 50)

def check_python_version():
    """Check Python version compatibility"""
    print_step("Checking Python Version")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages"""
    print_step("Installing Requirements")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)

def setup_directories():
    """Create necessary directories"""
    print_step("Setting up Directories")
    
    directories = [
        "app/content",
        "app/utils", 
        "app/services",
        "tests",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created: {directory}")
    
    print("✅ Directories created successfully")

def initialize_database():
    """Initialize the enhanced database"""
    print_step("Initializing Database")
    
    try:
        # Import after ensuring the module path is correct
        sys.path.insert(0, os.path.join(os.getcwd(), '.'))
        from app.enhanced_database import DatabaseManager
        
        db_manager = DatabaseManager()
        print("✅ Database initialized successfully")
        
        # Test database connection
        test_user_id = 999999
        if db_manager.add_user(test_user_id, "setup_test"):
            print("✅ Database connection test passed")
            # Clean up test user
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (test_user_id,))
            conn.commit()
            conn.close()
        else:
            print("⚠️ Database connection test failed, but database exists")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("This might be due to missing dependencies. Database will be created on first run.")

def setup_environment():
    """Setup environment variables"""
    print_step("Setting up Environment")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ Found existing {env_file}")
        return
    
    print(f"📝 Creating {env_file} template")
    
    env_template = """# BitMshauri Bot Configuration
# Copy this file to .env and fill in your values

# Telegram Bot Token (Required)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Optional: OpenAI API Key for advanced features
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (Optional - uses SQLite by default)
DATABASE_PATH=bitmshauri.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bitmshauri.log

# Price Monitoring
PRICE_UPDATE_INTERVAL=300
PRICE_ALERT_THRESHOLD=5.0

# Rate Limiting
RATE_LIMIT_MESSAGES=10
RATE_LIMIT_WINDOW=60

# Audio Settings
AUDIO_TEMP_DIR=temp/audio
AUDIO_CLEANUP_HOURS=24

# Community Features
MAX_GROUP_SIZE=50
MAX_GROUPS_PER_USER=5
"""
    
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print(f"✅ Created {env_file} template")
    print("📝 Please edit .env file with your actual configuration values")

def create_run_scripts():
    """Create convenient run scripts"""
    print_step("Creating Run Scripts")
    
    # Windows batch script
    bat_content = """@echo off
echo Starting BitMshauri Bot...
python app/enhanced_telegram_bot.py
pause
"""
    
    with open("run_bot.bat", 'w') as f:
        f.write(bat_content)
    
    # Unix shell script
    sh_content = """#!/bin/bash
echo "Starting BitMshauri Bot..."
python3 app/enhanced_telegram_bot.py
"""
    
    with open("run_bot.sh", 'w') as f:
        f.write(sh_content)
    
    # Make shell script executable on Unix systems
    if os.name != 'nt':
        os.chmod("run_bot.sh", 0o755)
    
    # Test runner script
    test_content = """@echo off
echo Running BitMshauri Bot Tests...
python tests/test_suite.py
pause
"""
    
    with open("run_tests.bat", 'w') as f:
        f.write(test_content)
    
    print("✅ Created run scripts: run_bot.bat, run_bot.sh, run_tests.bat")

def validate_setup():
    """Validate the setup"""
    print_step("Validating Setup")
    
    # Check critical files
    critical_files = [
        "app/enhanced_telegram_bot.py",
        "app/enhanced_database.py",
        "app/utils/logger.py",
        "app/services/content_manager.py",
        "requirements.txt",
        ".env"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    # Test imports
    print("\n🔍 Testing imports...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), '.'))
        
        import app.enhanced_database
        print("✅ Enhanced database module")
        
        import app.utils.logger
        print("✅ Logger module")
        
        import app.services.content_manager
        print("✅ Content manager module")
        
        import app.services.multi_language
        print("✅ Multi-language module")
        
        print("\n✅ All critical modules imported successfully")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Some modules may not be available until dependencies are installed")

def print_next_steps():
    """Print next steps for the user"""
    print_step("Setup Complete!")
    
    next_steps = """
🎉 BitMshauri Bot setup is complete!

📋 NEXT STEPS:

1. 🔑 Configure your bot:
   - Edit the .env file with your Telegram Bot Token
   - Get a bot token from @BotFather on Telegram
   - Optionally add OpenAI API key for advanced features

2. 🧪 Test the installation:
   - Run: python tests/test_suite.py
   - Or use: run_tests.bat (Windows)

3. 🚀 Start the bot:
   - Run: python app/enhanced_telegram_bot.py
   - Or use: run_bot.bat (Windows) / ./run_bot.sh (Linux/Mac)

4. 📱 Test your bot:
   - Message your bot on Telegram
   - Try commands like /start, /help, /language

⚠️  IMPORTANT:
   - Make sure to install any additional audio dependencies if needed
   - Check logs/bitmshauri.log for any issues
   - The bot will create its database automatically on first run

🆘 NEED HELP?
   - Check the README.md file
   - Review the logs for error messages
   - Ensure all environment variables are set correctly

Happy learning with BitMshauri! 🚀
"""
    
    print(next_steps)

def main():
    """Main setup function"""
    print("🚀 BitMshauri Bot Enhanced Setup")
    print("=" * 50)
    print("Setting up your professional Bitcoin education bot...")
    
    try:
        check_python_version()
        setup_directories()
        setup_environment()
        install_requirements()
        initialize_database()
        create_run_scripts()
        validate_setup()
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
