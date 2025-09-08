# 🚂 Railway Deployment Guide - BitMshauri Bot

## ✅ **Railway Setup Complete**

Your BitMshauri bot is now configured for Railway deployment with persistent containers.

---

## 📋 **Prerequisites**

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install globally
3. **Git Repository**: Your code is already on GitHub

---

## 🛠️ **Installation Steps**

### **Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

### **Step 2: Login to Railway**
```bash
railway login
```

### **Step 3: Initialize Railway Project**
```bash
railway init
```

### **Step 4: Set Environment Variables**
```bash
railway variables set TELEGRAM_BOT_TOKEN=8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno
railway variables set GECKO_API_URL=https://api.coingecko.com/api/v3
railway variables set SECRET_KEY=bitmshauri_secure_key_2024_production
railway variables set LOG_LEVEL=INFO
railway variables set DATABASE_PATH=bitmshauri.db
```

### **Step 5: Deploy to Railway**
```bash
railway up
```

---

## 🔧 **Configuration Files**

### **railway.json**
- ✅ Railway deployment configuration
- ✅ Health check settings
- ✅ Restart policy configuration

### **Procfile**
- ✅ Process definition for Railway
- ✅ Web process specification

### **nixpacks.toml**
- ✅ Build configuration
- ✅ Python environment setup
- ✅ Dependency installation

---

## 🌐 **Deployment URLs**

After deployment, you'll get:
- **Production URL**: `https://your-project.railway.app`
- **Health Check**: `https://your-project.railway.app/health`
- **Webhook URL**: `https://your-project.railway.app/webhook`

---

## 🔗 **Set Telegram Webhook**

Once deployed, set your Telegram webhook:

```bash
curl -X POST "https://api.telegram.org/bot8057866774:AAEMaLJKIyVVqyKn6hEt7tqVt3EzHXzUWno/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-project.railway.app/webhook"}'
```

---

## 📊 **Monitoring**

### **Railway Dashboard**
- Visit [railway.app/dashboard](https://railway.app/dashboard)
- Monitor container logs
- Check resource usage
- View deployment history

### **Health Check**
```bash
curl https://your-project.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "BitMshauri Bot is running",
  "version": "1.0.0",
  "uptime": "2h 30m 15s"
}
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility

#### **Environment Variables**
- Verify all variables are set in Railway dashboard
- Check variable names match exactly

#### **Webhook Issues**
- Ensure webhook URL is correct
- Check bot token is valid
- Verify HTTPS is enabled

#### **Container Issues**
- Check logs in Railway dashboard
- Verify start command is correct
- Check resource limits

---

## 🎯 **Benefits of Railway**

### **✅ Advantages**
- **Persistent Containers**: No cold starts
- **Auto-scaling**: Handles traffic automatically
- **Simple Deployment**: Git integration
- **Built-in Monitoring**: Container logs and metrics
- **Database Integration**: Easy PostgreSQL setup
- **Custom Domains**: Professional URLs

### **⚠️ Considerations**
- **Resource Limits**: Based on your plan
- **Container Restarts**: On failure or updates
- **Environment Variables**: Must be set manually

---

## 🔄 **Continuous Deployment**

### **Automatic Deployments**
- Push to `main` branch → Auto-deploy to production
- Push to other branches → Preview deployments
- Pull requests → Preview deployments

### **Manual Deployments**
```bash
railway up --detach  # Deploy in background
railway logs         # View logs
railway status       # Check status
```

---

## 📱 **Testing Your Bot**

### **After Deployment**
1. **Set webhook** with your Railway URL
2. **Send message** to your bot on Telegram
3. **Check logs** in Railway dashboard
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
- ✅ No errors in Railway logs
- ✅ Fast response times (< 1 second)
- ✅ Container runs continuously

---

## 📞 **Support**

### **Railway Support**
- [Railway Documentation](https://docs.railway.app)
- [Railway Community](https://discord.gg/railway)

### **Bot Support**
- **Email**: mwanga02717@gmail.com
- **GitHub**: https://github.com/MWANGAZA-LAB/bitmshauri-bot

---

## 🚀 **Ready to Deploy!**

Your BitMshauri bot is now fully configured for Railway deployment. Follow the steps above to get your bot running on Railway's infrastructure!

**Next Step**: Run `railway up` in your project directory to start deployment.
