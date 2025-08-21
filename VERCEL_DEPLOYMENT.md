# 🚀 Vercel Deployment Guide - BitMshauri Bot

## ✅ **Vercel Setup Complete**

Your BitMshauri bot is now configured for Vercel deployment with serverless functions.

---

## 📋 **Prerequisites**

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally
3. **Git Repository**: Your code is already on GitHub

---

## 🛠️ **Installation Steps**

### **Step 1: Install Vercel CLI**
```bash
npm install -g vercel
```

### **Step 2: Login to Vercel**
```bash
vercel login
```

### **Step 3: Deploy to Vercel**
```bash
vercel
```

### **Step 4: Set Environment Variables**
```bash
vercel env add TELEGRAM_BOT_TOKEN
# Enter your token: 8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno

vercel env add GECKO_API_URL
# Enter: https://api.coingecko.com/api/v3

vercel env add SECRET_KEY
# Enter: bitmshauri_bot_secret_key_2024
```

### **Step 5: Deploy to Production**
```bash
vercel --prod
```

---

## 🔧 **Configuration Files**

### **vercel.json**
- ✅ Serverless function configuration
- ✅ Python runtime setup
- ✅ Route handling for webhooks

### **api/bot.py**
- ✅ Telegram webhook handler
- ✅ Serverless function entry point
- ✅ Health check endpoint

---

## 🌐 **Deployment URLs**

After deployment, you'll get:
- **Production URL**: `https://your-project.vercel.app`
- **Webhook URL**: `https://your-project.vercel.app/api/bot`
- **Health Check**: `https://your-project.vercel.app/api/bot` (GET)

---

## 🔗 **Set Telegram Webhook**

Once deployed, set your Telegram webhook:

```bash
curl -X POST "https://api.telegram.org/bot8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-project.vercel.app/api/bot"}'
```

---

## 📊 **Monitoring**

### **Vercel Dashboard**
- Visit [vercel.com/dashboard](https://vercel.com/dashboard)
- Monitor function executions
- Check logs and performance

### **Health Check**
```bash
curl https://your-project.vercel.app/api/bot
```

Expected response:
```json
{
  "status": "ok",
  "message": "BitMshauri Bot is running",
  "version": "1.0.0"
}
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
- Ensure all dependencies are in `requirements.txt`
- Check Python path configuration

#### **Environment Variables**
- Verify all variables are set in Vercel dashboard
- Check variable names match exactly

#### **Webhook Issues**
- Ensure webhook URL is correct
- Check bot token is valid
- Verify HTTPS is enabled

---

## 🎯 **Benefits of Vercel**

### **✅ Advantages**
- **Global CDN**: Fast response times worldwide
- **Auto-scaling**: Handles traffic spikes automatically
- **Serverless**: Pay only for what you use
- **Easy deployment**: Git integration
- **Built-in monitoring**: Function logs and metrics

### **⚠️ Limitations**
- **Cold starts**: First request may be slower
- **Function timeout**: 30 seconds max
- **Memory limits**: 1024MB per function

---

## 🔄 **Continuous Deployment**

### **Automatic Deployments**
- Push to `main` branch → Auto-deploy to production
- Push to other branches → Preview deployments
- Pull requests → Preview deployments

### **Manual Deployments**
```bash
vercel --prod  # Deploy to production
vercel         # Deploy to preview
```

---

## 📱 **Testing Your Bot**

### **After Deployment**
1. **Set webhook** with your Vercel URL
2. **Send message** to your bot on Telegram
3. **Check logs** in Vercel dashboard
4. **Verify responses** from bot

### **Test Commands**
```
/start - Initialize bot
/help - Show commands
/price - Get Bitcoin price
/language - Switch languages
```

---

## 🎉 **Success Indicators**

### **When Everything Works:**
- ✅ Bot responds to messages
- ✅ Webhook receives updates
- ✅ No errors in Vercel logs
- ✅ Fast response times (< 2 seconds)
- ✅ Functions execute successfully

---

## 📞 **Support**

### **Vercel Support**
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

### **Bot Support**
- **Email**: mwanga02717@gmail.com
- **GitHub**: https://github.com/MWANGAZA-LAB/bitmshauri-bot

---

## 🚀 **Ready to Deploy!**

Your BitMshauri bot is now fully configured for Vercel deployment. Follow the steps above to get your bot running on Vercel's global infrastructure!

**Next Step**: Run `vercel` in your project directory to start deployment.
