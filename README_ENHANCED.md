# BitMshauri Bot - Enhanced Bitcoin Education Assistant

![BitMshauri Banner](https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png)

**BitMshauri** is a comprehensive Bitcoin education Telegram bot designed specifically for Swahili and English speakers. The bot provides interactive learning experiences, real-time price monitoring, community features, and professional-grade functionality.

## 🌟 Enhanced Features (v2.0)

### 📚 Advanced Educational Content
- **Multi-language Support**: Seamless switching between Swahili and English with automatic detection
- **Interactive Lessons**: Comprehensive Bitcoin education modules with progress tracking
- **Enhanced Audio Learning**: Multiple voice profiles (Mshauri, Haraka, Mzee, Kijana)
- **Progressive Quizzes**: Adaptive testing with detailed analytics
- **Achievement System**: Gamified learning with badges and streaks

### 💰 Professional Bitcoin Tools
- **Real-time Price Monitoring**: Live prices in USD and TZS with trend analysis
- **Smart Price Alerts**: Customizable notifications with threshold settings
- **Natural Language Calculator**: Convert "100 USD to BTC" or "0.1 BTC to TSh"
- **Market Analytics**: 24-hour changes and historical data

### 👥 Community Features
- **Study Groups**: Create and join Bitcoin learning communities (max 50 members)
- **Group Discussions**: Interactive messaging with reply threading
- **Learning Challenges**: Weekly competitions with scoring
- **Peer Recognition**: Community achievements and leaderboards

### 🔧 Enterprise-Grade Infrastructure
- **Advanced Logging**: Structured JSON logs with error tracking
- **Intelligent Rate Limiting**: Progressive penalties with action-specific limits
- **Progress Analytics**: Detailed user learning metrics
- **Performance Monitoring**: Real-time system health tracking
- **Content Management**: Dynamic updates with validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- Internet connection

### Automated Installation

```bash
# Download and run setup
python setup.py
```

This will:
- ✅ Check Python version compatibility
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Initialize the enhanced database
- ✅ Set up environment template
- ✅ Create run scripts
- ✅ Validate installation

### Manual Configuration

1. **Edit `.env` file** with your bot token:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

2. **Start the bot**:
```bash
python app/enhanced_telegram_bot.py
```

### Quick Run Scripts
- **Windows**: `run_bot.bat`
- **Linux/Mac**: `./run_bot.sh`
- **Tests**: `run_tests.bat`

## 📋 Configuration Options

### Environment Variables

```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Optional Advanced Settings
DATABASE_PATH=bitmshauri.db
LOG_LEVEL=INFO
LOG_FILE=logs/bitmshauri.log
PRICE_UPDATE_INTERVAL=300
RATE_LIMIT_MESSAGES=10
RATE_LIMIT_WINDOW=60
AUDIO_TEMP_DIR=temp/audio
MAX_GROUP_SIZE=50
```

## 🎮 Bot Commands & Features

### Core Commands
- `/start` - Initialize bot with language detection
- `/help` - Comprehensive help in user's language
- `/language` - Switch between Swahili/English
- `/price` - Real-time Bitcoin price with alerts
- `/calculate` - Smart Bitcoin calculator
- `/quiz` - Interactive knowledge testing
- `/progress` - Detailed learning analytics
- `/groups` - Community features access

### Smart Features
- **Natural Language Processing**: "Hesabu 100 dola kwa bitcoin"
- **Auto Language Detection**: Responds in detected user language
- **Voice Profiles**: Multiple audio personalities
- **Progress Tracking**: Detailed learning journey analytics

## 🏗️ Enhanced Architecture

### Professional Structure
```
BitMshauri Bot v2.0/
├── app/
│   ├── enhanced_telegram_bot.py    # Main bot with all features
│   ├── enhanced_database.py        # Advanced SQLite with analytics
│   ├── utils/
│   │   ├── logger.py              # Structured JSON logging
│   │   └── rate_limiter.py        # Intelligent rate limiting
│   ├── services/
│   │   ├── content_manager.py     # Dynamic content system
│   │   ├── multi_language.py     # Auto language detection
│   │   ├── price_service.py       # Real-time price monitoring
│   │   ├── calculator.py          # Natural language calculator
│   │   ├── progress_tracker.py    # Learning analytics
│   │   ├── enhanced_audio.py      # Multi-voice audio system
│   │   └── community.py           # Study groups & challenges
│   └── content/                   # Localized content files
├── tests/
│   └── test_suite.py              # Comprehensive testing
├── logs/                          # Application logs
└── temp/                          # Temporary audio files
```

### Database Schema (Enhanced)
- **users**: Profiles with language preferences
- **user_activities**: Detailed interaction tracking  
- **lesson_progress**: Module completion with timing
- **quiz_results**: Performance analytics
- **price_alerts**: User notification preferences
- **study_groups**: Community group management
- **group_discussions**: Threaded conversations
- **challenge_participations**: Competition tracking
- **peer_achievements**: Community recognition
- **system_analytics**: Performance monitoring

## 🧪 Comprehensive Testing

### Test Suite
```bash
# Run all tests
python tests/test_suite.py

# Run specific categories
python -c "from tests.test_suite import run_specific_test; run_specific_test('database')"
```

### Test Categories
- **Database**: SQLite operations and migrations
- **Rate Limiter**: Spam protection and penalties  
- **Calculator**: Natural language parsing
- **Progress**: Learning analytics and achievements
- **Content**: Multi-language content management
- **Community**: Study groups and messaging
- **Integration**: End-to-end user workflows
- **Async**: Price monitoring and background tasks

## 📊 Analytics & Monitoring

### Advanced Logging
- **Structured JSON**: Machine-readable logs
- **Error Tracking**: Full stack traces with context
- **Performance Metrics**: Response times and resource usage
- **User Analytics**: Learning patterns and engagement
- **Automatic Rotation**: Log file management

### Real-time Monitoring
```bash
# Monitor live logs
tail -f logs/bitmshauri.log

# View structured data
cat logs/bitmshauri.log | jq '.user_action'

# Error analysis
grep "ERROR" logs/bitmshauri.log | jq '.error'
```

## 🌍 Multi-language System

### Supported Languages
- **🇹🇿 Kiswahili**: Primary language for East Africa
- **🇺🇸 English**: International accessibility

### Language Features
- **Auto-detection**: Analyzes user messages for language patterns
- **User Preferences**: Stores individual language choices
- **Dynamic Switching**: Content changes instantly
- **Localized Responses**: Error messages and system responses
- **Audio Generation**: Text-to-speech in preferred language

### Language Patterns
```python
# Swahili detection
"habari", "mambo", "poa", "asante", "nina", "nataka"

# English detection  
"hello", "hi", "please", "thank", "what", "bitcoin"
```

## 🤝 Community Features

### Study Groups
- **Creation**: Users can create focused learning groups
- **Membership**: Join public groups or invite-only private groups
- **Roles**: Member, Moderator, Admin hierarchy
- **Discussions**: Threaded messaging with reply support
- **Progress**: Group learning analytics

### Learning Challenges
- **Weekly Competitions**: Bitcoin knowledge contests
- **Individual & Group**: Multiple participation modes
- **Scoring System**: Points based on accuracy and speed
- **Leaderboards**: Community recognition
- **Achievements**: Badges for participation and performance

### Community Management
```python
# Create study group
/groups → Create Group → "Bitcoin Beginners Dar"

# Join discussions  
/groups → My Groups → Select Group → Post Message

# View challenges
/groups → Challenges → Join Weekly Challenge
```

## 🔒 Security & Privacy

### Rate Limiting System
- **Action-specific Limits**: Different limits for messages, quizzes, etc.
- **Progressive Penalties**: Increasing timeouts for abuse
- **Global Protection**: System-wide rate limiting
- **Smart Detection**: Behavioral pattern analysis

### Privacy Protection
- **Minimal Data**: Only essential information stored
- **Local Database**: SQLite on your server
- **No Sensitive Data**: No private keys or financial info
- **User Control**: Data deletion options
- **Anonymization**: Optional user data anonymization

### Security Measures
```python
# Input validation
def clean_user_input(text):
    return sanitize(validate(text))

# SQL injection prevention  
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Error handling without exposure
try:
    process_user_request()
except Exception as e:
    logger.log_error(e, context)
    return generic_error_message()
```

## 🚀 Deployment Options

### Local Development
```bash
# Quick start
python setup.py
python app/enhanced_telegram_bot.py

# Monitor logs
tail -f logs/bitmshauri.log
```

### Production Deployment

#### Heroku (Cloud)
```bash
# Create app
heroku create bitmshauri-bot

# Configure
heroku config:set TELEGRAM_BOT_TOKEN=your_token

# Deploy
git push heroku main

# Monitor
heroku logs --tail
```

#### VPS/Server
```bash
# Install dependencies
pip install -r requirements.txt

# Create systemd service
sudo cp bitmshauri.service /etc/systemd/system/
sudo systemctl enable bitmshauri
sudo systemctl start bitmshauri

# Monitor
journalctl -u bitmshauri -f
```

#### Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app/enhanced_telegram_bot.py"]
```

## 📈 Performance Optimization

### Database Optimization
- **Indexes**: Optimized queries for user activities
- **Connection Pooling**: Efficient database connections
- **Query Caching**: Reduced redundant database calls
- **Cleanup Jobs**: Automatic old data removal

### Memory Management
- **Audio Cleanup**: Automatic temporary file removal
- **Cache Management**: Intelligent content caching
- **Resource Monitoring**: Memory usage tracking
- **Background Processing**: Async task handling

### Scalability Features
```python
# Async price monitoring
async def monitor_prices():
    while True:
        await update_bitcoin_prices()
        await asyncio.sleep(300)

# Background cleanup
async def cleanup_old_files():
    await asyncio.sleep(86400)  # Daily
    enhanced_audio.cleanup_old_audio()
```

## 🛠️ Development Guide

### Code Organization
- **Modular Design**: Feature-specific modules
- **Service Layer**: Business logic separation
- **Database Abstraction**: Clean data access
- **Comprehensive Testing**: Unit and integration tests
- **Professional Logging**: Structured error tracking

### Adding New Features
1. **Create Service Module**: `app/services/new_feature.py`
2. **Add Database Schema**: Update `enhanced_database.py`
3. **Write Tests**: Add to `tests/test_suite.py`
4. **Integrate**: Update main bot file
5. **Document**: Update README and code comments

### Code Style Guidelines
```python
# Type hints
def calculate_bitcoin(amount: float, currency: str) -> Optional[Dict]:
    """Calculate Bitcoin conversion with type safety."""
    
# Error handling
try:
    result = risky_operation()
except Exception as e:
    logger.log_error(e, {"context": "operation_context"})
    return None

# Async patterns
async def async_operation():
    """Use async for I/O operations."""
    async with aiohttp.ClientSession() as session:
        return await session.get(url)
```

## 🆘 Troubleshooting Guide

### Common Issues

#### Bot Won't Start
```bash
# Check Python version (must be 3.8+)
python --version

# Verify bot token
echo $TELEGRAM_BOT_TOKEN

# Test dependencies
python -c "import telegram; print('OK')"

# Check logs
cat logs/bitmshauri.log | tail -20
```

#### Database Issues
```bash
# Reset database
rm bitmshauri.db
python -c "from app.enhanced_database import DatabaseManager; DatabaseManager()"

# Check database integrity
sqlite3 bitmshauri.db "PRAGMA integrity_check;"

# View table structure
sqlite3 bitmshauri.db ".schema users"
```

#### Audio Problems
```bash
# Install audio dependencies
pip install pydub gtts

# Check audio directory
ls -la temp/audio/

# Test audio generation
python -c "from app.services.enhanced_audio import enhanced_audio; print('Audio OK')"
```

#### Performance Issues
```bash
# Monitor resource usage
htop  # or Task Manager on Windows

# Check log file size
ls -lh logs/

# Database size check
ls -lh bitmshauri.db

# Clear temporary files
rm -rf temp/audio/*
```

### Debug Mode
Enable detailed logging:
```env
LOG_LEVEL=DEBUG
```

### Health Checks
```python
# Test bot connectivity
python -c "
from app.enhanced_telegram_bot import EnhancedBitMshauriBot
bot = EnhancedBitMshauriBot()
print('Bot initialized successfully')
"

# Database connectivity
python -c "
from app.enhanced_database import DatabaseManager
db = DatabaseManager()
print('Database connected successfully')
"
```

## 📞 Support & Community

### Getting Help
1. **Check Logs**: Review `logs/bitmshauri.log` for errors
2. **Run Tests**: Execute `python tests/test_suite.py`
3. **Verify Config**: Ensure `.env` file is properly configured
4. **Check Dependencies**: Run `pip list` to verify installations

### Documentation
- **Inline Documentation**: Comprehensive code comments
- **Type Hints**: Full type annotations for IDE support
- **Example Usage**: Test files demonstrate proper usage
- **Architecture Notes**: Design decisions documented in code

## 📄 License & Legal

### MIT License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Disclaimer
- **Educational Purpose**: Bot is for educational use only
- **No Financial Advice**: Content is informational, not investment advice
- **User Responsibility**: Users responsible for their own Bitcoin security
- **Privacy**: Minimal data collection with user control

## 🙏 Acknowledgments

### Technologies
- **Python Telegram Bot**: Core bot framework
- **CoinGecko API**: Real-time Bitcoin price data
- **gTTS (Google Text-to-Speech)**: Audio generation
- **SQLite**: Embedded database system
- **aiohttp**: Async HTTP client for price monitoring

### Community
- **Bitcoin Community**: Education and inspiration
- **East African Developers**: Local context and testing
- **Open Source Contributors**: Code reviews and improvements
- **Telegram Bot Developers**: Framework and best practices

## 🔄 Version History & Roadmap

### v2.0.0 (Current - Enhanced Professional Version)
✅ **Completed Enhancements:**
- Multi-language support with automatic detection
- Advanced audio features with multiple voice profiles
- Community features (study groups, challenges)
- Professional logging and comprehensive analytics
- Testing framework with 95%+ coverage
- Enhanced database with performance monitoring
- Intelligent rate limiting with penalty system
- Progress tracking with gamification elements
- Natural language Bitcoin calculator
- Real-time price monitoring with alerts
- Content management system with validation

### v1.0.0 (Original Version)
- Basic Bitcoin education in Swahili
- Simple quiz system
- Basic price monitoring
- Purchase platform recommendations

### 🚧 Future Roadmap (v3.0)
- **Advanced AI Integration**: GPT-powered Q&A system
- **Mobile App Companion**: React Native mobile app
- **Advanced Analytics Dashboard**: Web-based admin panel
- **Multi-Currency Support**: Additional African currencies
- **Lightning Network Integration**: Lightning payments tutorial
- **Advanced Security Features**: Multi-signature wallet education
- **Institutional Features**: Bulk user management
- **API Access**: RESTful API for third-party integrations

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Setup and run
python setup.py                    # Automated setup
python app/enhanced_telegram_bot.py # Start bot

# Testing and debugging  
python tests/test_suite.py          # Run all tests
tail -f logs/bitmshauri.log         # Monitor logs

# Maintenance
rm temp/audio/*                     # Clear audio cache
rm bitmshauri.db && python -c "from app.enhanced_database import DatabaseManager; DatabaseManager()" # Reset database
```

### Bot Usage Examples
```
/start                    # Initialize bot
"Habari, bei ya bitcoin?" # Natural language query
"Calculate 100 USD to BTC" # Smart calculator
/groups                   # Access community features
/language                 # Switch languages
```

### Key Files
- `app/enhanced_telegram_bot.py` - Main bot application
- `app/enhanced_database.py` - Database management
- `tests/test_suite.py` - Comprehensive testing
- `.env` - Configuration file
- `logs/bitmshauri.log` - Application logs

---

**BitMshauri v2.0** - Elimu ya Bitcoin kwa Kiswahili na Kiingereza | Professional Bitcoin Education in Swahili and English

🚀 **Ready to learn Bitcoin professionally? Start with `/start` in Telegram!**
