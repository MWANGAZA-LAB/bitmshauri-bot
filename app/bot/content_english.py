#!/usr/bin/env python3
"""Comprehensive English content for BitMshauri Bot."""

LESSONS = {
    "intro": {
        "content": "Hello! I'm BitMshauri, your Bitcoin education assistant in English. Choose one of the options below:"
    },
    "what_is_bitcoin": {
        "content": (
            "💰 *What is Bitcoin?*\n\n"
            "Bitcoin is a decentralized digital currency created in 2009 by an individual or group using the pseudonym Satoshi Nakamoto. "
            "It uses blockchain technology, which is a public ledger with blocks distributed across many computers worldwide. "
            "Every transaction is recorded securely, immutably, and quickly. The network operates without a single authority - no bank or government controls it.\n\n"
            "🔑 *Key Features:*\n"
            "• Decentralized - No central authority\n"
            "• Limited Supply - Only 21 million will ever exist\n"
            "• Transparent - All transactions are public\n"
            "• Secure - Cryptographically protected\n"
            "• Global - Works anywhere with internet"
        )
    },
    "how_p2p_works": {
        "content": (
            "🔗 *How does P2P (peer-to-peer) work?*\n\n"
            "Bitcoin transactions are P2P, meaning each user sends money directly to another through a computer network:\n\n"
            "1. User uses a wallet to send bitcoin\n"
            "2. Transaction is signed with a 'private key'\n"
            "3. Transaction enters the mempool\n"
            "4. Miners verify and add to a block\n"
            "5. Block is created every 10 minutes and distributed on the blockchain\n\n"
            "🌐 *Benefits of P2P:*\n"
            "• No intermediaries (banks, payment processors)\n"
            "• Lower fees\n"
            "• Faster transactions\n"
            "• Global accessibility\n"
            "• Censorship resistance"
        )
    },
    "wallet_types": {
        "content": (
            "👛 *Bitcoin Wallet Types and Examples:*\n\n"
            "Choose a wallet type:\n\n"
            "🔥 *Hot Wallet* (online): Easy to use but more risky\n"
            "   - Examples: Exodus, Electrum, Blockchain.com, Coinbase\n"
            "   - Best for: Small amounts, frequent trading\n\n"
            "❄️ *Cold Wallet* (offline): Much more secure\n"
            "   - Examples: Ledger Nano S/X, Trezor, Bitkey, Coldcard\n"
            "   - Best for: Large amounts, long-term storage\n\n"
            "📱 *Mobile Wallets:*\n"
            "   - Examples: BlueWallet, Muun, Phoenix\n"
            "   - Best for: Daily spending, Lightning payments\n\n"
            "🖥️ *Desktop Wallets:*\n"
            "   - Examples: Bitcoin Core, Electrum, Sparrow\n"
            "   - Best for: Full node, advanced users"
        )
    },
    "wallet_security": {
        "content": (
            "🔒 *Bitcoin Wallet Security:*\n\n"
            "1. *Store seed phrase securely:*\n"
            "   - Never store it online\n"
            "   - Use paper or metal backup\n"
            "   - Store in multiple secure locations\n\n"
            "2. *Avoid scams:*\n"
            "   - Don't click suspicious links\n"
            "   - Verify official websites before downloading\n"
            "   - Never share your private keys\n\n"
            "3. *Keep software updated:*\n"
            "   - Update your wallet software regularly\n"
            "   - Use only legitimate, verified software\n"
            "   - Enable 2FA where possible\n\n"
            "4. *Use hardware wallets for large amounts:*\n"
            "   - Keep most Bitcoin in cold storage\n"
            "   - Only keep spending money in hot wallets\n"
            "   - Test recovery process before storing large amounts"
        )
    },
    "losing_private_key": {
        "content": (
            "⚠️ *What happens when you lose your private key?*\n\n"
            "If you lose your seed phrase or private key:\n"
            "1. *You cannot access your wallet again*\n"
            "2. *Your Bitcoin is lost forever*\n"
            "3. *There is no recovery system* 🚫\n\n"
            "Approximately 20% of all Bitcoin has been lost this way. "
            "Lack of proper backup is the main reason - your Bitcoin is like water spilled without the ability to recover it!\n\n"
            "💡 *Prevention Tips:*\n"
            "• Create multiple backups\n"
            "• Test your recovery process\n"
            "• Store backups in different locations\n"
            "• Use metal backup for fire/water protection"
        )
    },
    "wallet_usage": {
        "content": (
            "📱 *How to use a Bitcoin wallet:*\n\n"
            "1. Open your wallet app (Exodus, Electrum, etc.)\n"
            "2. Choose 'Send'\n"
            "3. Enter recipient's address\n"
            "4. Enter amount to send\n"
            "5. Confirm using your PIN or key\n"
            "6. Wait for confirmation (usually under 20 minutes)\n\n"
            "For hardware wallets (Ledger/Trezor):\n"
            "1. Connect your device\n"
            "2. Follow on-screen instructions\n"
            "3. Confirm transaction on device\n\n"
            "💡 *Pro Tips:*\n"
            "• Always verify the address before sending\n"
            "• Start with small amounts to test\n"
            "• Check transaction fees before confirming\n"
            "• Keep transaction receipts for records"
        )
    },
    "pros_and_cons": {
        "content": (
            "⚖️ *Bitcoin: Pros, Cons, and Recovery:*\n\n"
            "✅ *Advantages:*\n"
            "   - Complete financial freedom without intermediaries\n"
            "   - Accessible to unbanked populations\n"
            "   - No discrimination, works internationally\n"
            "   - Limited supply (deflationary)\n"
            "   - Transparent and auditable\n\n"
            "❌ *Risks:*\n"
            "   - Price can change rapidly (volatility)\n"
            "   - Risk of losing private keys\n"
            "   - Scams and malware threats\n"
            "   - Regulatory uncertainty\n"
            "   - Technical complexity for beginners\n\n"
            "🔄 *Recovery:*\n"
            "   - With hardware wallets, you can recover on a new device using seed phrase\n"
            "   - *There is NO way to recover if you lose your seed phrase!*"
        )
    },
    "blockchain_technology": {
        "content": (
            "🔐 *Blockchain Technology & Security:*\n\n"
            "1. *Blockchain is an immutable ledger:*\n"
            "   - Each block contains hash of previous block\n"
            "   - Cannot be easily modified\n"
            "   - Creates permanent transaction history\n\n"
            "2. *Uses proof-of-work (PoW):*\n"
            "   - Miners must solve complex mathematical problems\n"
            "   - Prevents tampering without massive computing power (>51%)\n"
            "   - Secures the network through economic incentives\n\n"
            "3. *Advanced technologies:*\n"
            "   - Lightning Network enables fast, cheap transactions\n"
            "   - Uses smart contracts off-chain to increase capacity\n"
            "   - Taproot improves privacy and efficiency\n\n"
            "4. *Security features:*\n"
            "   - Cryptographic signatures\n"
            "   - Merkle trees for data integrity\n"
            "   - Distributed consensus mechanism"
        )
    },
    "frequently_asked": {
        "content": (
            "❓ *Frequently Asked Questions:*\n\n"
            "1. *How can I buy Bitcoin with M-Pesa?*\n"
            "   - Use Paxful.com or LocalBitcoins.com\n"
            "   - Choose a seller with good ratings\n"
            "   - Follow the P2P trading process\n\n"
            "2. *Is Bitcoin legal in Kenya?*\n"
            "   - Yes, but it's not official currency\n"
            "   - No government protection like regular money\n"
            "   - Use at your own risk\n\n"
            "3. *What's the minimum amount I can buy?*\n"
            "   - You can buy as little as 500 KSh (0.00001 BTC)\n"
            "   - No minimum limit required\n"
            "   - Bitcoin is divisible to 8 decimal places\n\n"
            "4. *How do I store Bitcoin safely?*\n"
            "   - Use hardware wallets for large amounts\n"
            "   - Keep seed phrase offline and secure\n"
            "   - Never share private keys with anyone"
        )
    },
    "buying_guide": {
        "content": (
            "📱 *How to Buy Bitcoin with M-Pesa:*\n\n"
            "1. Go to Paxful.com or LocalBitcoins.com\n"
            "2. Find a seller with good ratings\n"
            "3. Choose 'Buy with M-Pesa'\n"
            "4. Follow on-screen instructions\n"
            "5. Send money to seller's number\n"
            "6. Confirm receiving Bitcoin in your wallet\n\n"
            "💡 *Important Tips:*\n"
            "   - Make sure wallet address is correct\n"
            "   - Never send money before receiving Bitcoin\n"
            "   - Use 2FA for security\n"
            "   - Start with small amounts\n"
            "   - Check seller's reputation and reviews\n\n"
            "🔗 *Alternative Methods:*\n"
            "   - Local Bitcoin ATMs\n"
            "   - Peer-to-peer exchanges\n"
            "   - Bitcoin exchanges (Binance, Coinbase)\n\n"
            "Complete guide: https://bitmshauri.co.ke/buying-guide"
        )
    },
    "about_bitmshauri": {
        "content": (
            "ℹ️ *About BitMshauri:*\n\n"
            "BitMshauri is an educational Bitcoin system in Swahili and English. "
            "Our goal is to spread Bitcoin knowledge to everyone, especially those in rural areas. "
            "We want to bring Bitcoin education to everyone for free.\n\n"
            "🎯 *Our Mission:*\n"
            "• Democratize Bitcoin education\n"
            "• Support Swahili-speaking communities\n"
            "• Provide reliable, unbiased information\n"
            "• Bridge the digital divide\n\n"
            "📞 *Contact us:* msaada@bitmshauri.co.ke\n"
            "🌐 *Website:* https://bitmshauri.co.ke"
        )
    }
}

# Quiz questions in English
QUIZZES = {
    "basic": [
        {
            "question": "When was Bitcoin created?",
            "options": ["2008", "2009", "2010", "2011"],
            "answer": 1,
            "explanation": "Bitcoin was launched in 2009 by Satoshi Nakamoto."
        },
        {
            "question": "Why does Bitcoin use blockchain technology?",
            "options": [
                "To increase transaction speed",
                "To ensure security and transparency",
                "To reduce bank costs",
                "To enable government control"
            ],
            "answer": 1,
            "explanation": "Blockchain ensures transactions are secure, transparent, and immutable."
        },
        {
            "question": "What makes Bitcoin 'decentralized'?",
            "options": [
                "It's controlled by central banks",
                "It's controlled by governments",
                "It's run by a network of computers worldwide",
                "It's controlled by a single company"
            ],
            "answer": 2,
            "explanation": "Bitcoin has no central authority; it's run by a network of computers worldwide."
        }
    ],
    "security": [
        {
            "question": "What should you do to store Bitcoin securely?",
            "options": [
                "Store seed phrase online",
                "Share seed phrase with friends",
                "Store seed phrase on paper or metal backup",
                "Don't have any backup"
            ],
            "answer": 2,
            "explanation": "Seed phrase is the most important thing. Store it on paper or metal backup, not online."
        },
        {
            "question": "What happens if you lose your private key?",
            "options": [
                "You can recover it from the blockchain",
                "You can contact Bitcoin support",
                "Your Bitcoin is lost forever",
                "You can get it back from your wallet provider"
            ],
            "answer": 2,
            "explanation": "If you lose your private key, your Bitcoin is lost forever. There's no recovery system."
        }
    ]
}

# Daily Bitcoin tips in English
DAILY_TIPS = [
    "💡 Tip: Never share your seed phrase with anyone!",
    "💡 Tip: Bitcoin has a limited supply - only 21 million will ever exist!",
    "💡 Tip: Buy Bitcoin little by little each month (dollar cost averaging)",
    "💡 Tip: Make sure you use 2FA on your Bitcoin accounts",
    "💡 Tip: Never send money before receiving Bitcoin in P2P transactions",
    "💡 Tip: Verify wallet address before sending Bitcoin",
    "💡 Tip: Backup your wallet regularly",
    "💡 Tip: Understand the risks before investing",
    "💡 Tip: Bitcoin is not gambling - it's a long-term value system",
    "💡 Tip: Start with small amounts to learn",
    "💡 Tip: Use hardware wallets for large amounts",
    "💡 Tip: Keep your software updated"
]

# Menu keyboard in English
MENU_KEYBOARD = [
    ["💰 Bitcoin Price", "📚 What is Bitcoin?", "🔗 How P2P Works"],
    ["👛 Wallet Types", "🔒 Wallet Security", "⚠️ Losing Private Key"],
    ["📱 Wallet Usage", "📱 Buy with M-Pesa", "⚖️ Pros and Cons"],
    ["🔐 Blockchain Technology", "❓ FAQ", "ℹ️ About BitMshauri"],
    ["📝 Bitcoin Quiz", "💡 Daily Tip"]
]
