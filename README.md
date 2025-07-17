# BitMshauri Bot

BitMshauri is a Telegram bot designed to educate, empower, and assist users in East Africa with Bitcoin knowledge and transactions, all in Swahili. The bot provides lessons, quizzes, daily tips, and interactive features for buying, spending, and saving Bitcoin.

---

## Features

- **Swahili Bitcoin Lessons:** Learn the basics and advanced concepts of Bitcoin in Swahili.
- **Daily Tips:** Receive daily Bitcoin tips to improve your understanding and security.
- **Quizzes:** Test your Bitcoin knowledge with interactive quizzes.
- **Bitcoin Price:** Get the latest Bitcoin price using the `/price` command.
- **Buy Bitcoin:** Purchase Bitcoin via integrated platforms (Bitika, Bitsacco, Fedimint).
- **Spend Bitcoin:** Spend Bitcoin through supported platforms.
- **Group Savings (Chama):** Save Bitcoin as a group using Bitsacco.
- **AI Q&A:** Ask any Bitcoin-related question and get instant answers powered by AI (OpenAI GPT).
- **Donation/Support:** Donate Bitcoin to support further development of BitMshauri.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Telegram account
- OpenAI API key (for AI Q&A)
- Git (for deployment and updates)


## Project Structure

```
bitmshauri-bot/
│
├── app/
│   ├── bot/
│   │   ├── telegram_bot.py
│   │   ├── price_api.py
│   │   └── content_swahili.py
│   └── database/
│       └── ...
├── requirements.txt
├── Procfile
├── .env
└── README.md
```

---

## Future Improvements

- **In-Bot Transaction Interfaces:**  
  Integrate full transaction flows for buying and spending Bitcoin directly within the bot, without redirecting users outside Telegram.
- **Platform Integrations:**  
  Add support for Tando (spending), Bitika (buying), Fedimint (group savings), and advanced Bitsacco features for personal and group savings.
- **Advanced Group Management:**  
  Enable users to create, join, and manage group savings (chama) with invitations and group wallets.
- **Enhanced AI Q&A:**  
  Improve AI moderation, support more languages, and provide fallback to human support for sensitive topics.
- **User Profiles & Analytics:**  
  Track user progress, quiz scores, and provide personalized learning paths.
- **Security Enhancements:**  
  Add more security tips, warnings, and best practices for safe Bitcoin usage.
- **Donation Recognition:**  
  Publicly recognize donors and provide special features for supporters.
- **Mobile/Web Dashboard:**  
  Build a companion dashboard for users to view their progress and manage group savings.

---

## Contributing

We welcome contributions!  
- Fork the repo, make your changes, and submit a pull request.
- For major features, open an issue first to discuss your ideas.

---

## License

MIT License

---

## Contact & Support

- Telegram: [@BitMshauriBot](https://t.me/BitMshauriBot)
- Email: mwanga02717@gmail.com

---

**BitMshauri – Elimu ya Bitcoin kwa Kiswahili, kwa wote!**
