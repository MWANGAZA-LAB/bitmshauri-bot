#!/usr/bin/env python3
"""Setup webhook for BitMshauri Bot."""

import requests
import os

# Bot configuration
BOT_TOKEN = "8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_webhook_info():
    """Get current webhook information."""
    try:
        response = requests.get(f"{BOT_URL}/getWebhookInfo")
        if response.status_code == 200:
            webhook_info = response.json()
            print("📡 Current Webhook Info:")
            print(f"  URL: {webhook_info['result'].get('url', 'Not set')}")
            print(f"  Pending Updates: {webhook_info['result'].get('pending_update_count', 0)}")
            return webhook_info['result']
        else:
            print(f"❌ Failed to get webhook info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
        return None

def set_webhook(webhook_url):
    """Set webhook URL."""
    try:
        print(f"🔗 Setting webhook to: {webhook_url}")
        
        # Set webhook
        response = requests.post(f"{BOT_URL}/setWebhook", data={'url': webhook_url})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook set successfully!")
                return True
            else:
                print(f"❌ Webhook setup failed: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def delete_webhook():
    """Delete webhook (for testing)."""
    try:
        print("🗑️ Deleting webhook...")
        response = requests.post(f"{BOT_URL}/deleteWebhook")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook deleted successfully!")
                return True
            else:
                print(f"❌ Webhook deletion failed: {result.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False

def main():
    """Main function."""
    print("🔧 BitMshauri Bot Webhook Setup")
    print("=" * 40)
    
    # Get current webhook info
    webhook_info = get_webhook_info()
    
    print("\n📋 Options:")
    print("1. Set webhook URL")
    print("2. Delete webhook (for testing)")
    print("3. Get webhook info")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        webhook_url = input("Enter webhook URL (e.g., https://your-app.railway.app/webhook): ").strip()
        if webhook_url:
            set_webhook(webhook_url)
        else:
            print("❌ No URL provided")
    
    elif choice == "2":
        delete_webhook()
    
    elif choice == "3":
        get_webhook_info()
    
    elif choice == "4":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
