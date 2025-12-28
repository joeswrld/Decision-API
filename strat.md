# 🚀 Launch Your API in Browser (30 Seconds)

## Quick Start

### Option 1: One-Command Launch (Recommended)

```bash
# Make the script executable
chmod +x start.sh

# Run it
./start.sh
```

**This will:**
- ✅ Start the API server
- ✅ Launch browser test UI automatically
- ✅ Give you demo API keys

---

### Option 2: Manual Launch (2 Steps)

**Step 1: Start API**
```bash
uvicorn main:app --reload
```

**Step 2: Open Browser**
- Double-click `browser_test.html`
- OR visit: http://localhost:8000/docs (Swagger UI)

---

## 🎯 What You'll See

### Browser Test UI
A beautiful interface where you can:
- 📝 Type customer messages
- 🔑 Select API tier (Free/Starter/Pro)
- 🎯 Click "Make Decision" 
- 📊 See results instantly
- 📈 Track usage in real-time

### Example Test
1. Click "Legal Threat" example
2. Click "Make Decision"
3. Watch it escalate immediately!

---

## 🔑 Demo API Keys (Pre-configured)

```bash
# Free Tier (10 req/min)
sk_test_demo_free_key_12345678901234567890

# Starter Tier (60 req/min)
sk_test_demo_starter_key_1234567890123456

# Pro Tier (300 req/min)
sk_test_demo_pro_key_123456789012345678
```

**These work immediately - no setup needed!**

---

## 🧪 Try These Tests

### Test 1: Legal Threat
```
Message: "I will contact my lawyer"
Result: IMMEDIATE_ESCALATION 🔴
```

### Test 2: Rate Limit
```
1. Select Free tier
2. Click "Make Decision" 15 times fast
3. Request 11+ will fail with 429
```

### Test 3: Usage Tracking
```
1. Make 5 decisions
2. Click "Refresh Usage"
3. See your request count
```

---

## 🐛 Troubleshooting

### API Not Starting?
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9

# Start again
uvicorn main:app --reload
```

### Browser Says "Failed to Fetch"?
```bash
# 1. Make sure API is running
curl http://localhost:8000/health

# Should return: {"status": "healthy"}

# 2. Check the URL in browser console
# Should be: http://localhost:8000
```

### CORS Error?
```bash
# Already fixed in main.py!
# CORS is enabled for browser testing
```

---

## 📚 Alternative Testing Methods

### 1. Swagger UI (Built-in)
```
Open: http://localhost:8000/docs
- Interactive API documentation
- Test all endpoints
- See request/response schemas
```

### 2. cURL (Command Line)
```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Authorization: Bearer sk_test_demo_pro_key_123456789012345678" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "user_plan": "pro"}'
```

### 3. Python Script
```python
import requests

response = requests.post(
    "http://localhost:8000/v1/decision",
    headers={"Authorization": "Bearer sk_test_demo_pro_key_123456789012345678"},
    json={"message": "Test", "user_plan": "pro"}
)

print(response.json())
```

---

## 🎨 Browser UI Features

### Beautiful Interface
- 🎯 Clean, modern design
- 📱 Mobile-friendly
- 🌈 Color-coded decisions
- 📊 Real-time metrics

### Smart Examples
- Legal Threat
- Churn Risk  
- Simple Question
- Spam Detection

### Live Metrics
- Rate limits (per minute/day)
- Usage tracking
- Cost estimation
- Request counters

---

## 🚀 What's Next?

After testing in browser:

1. **Share with team** → They can test without code
2. **Gather feedback** → What works? What doesn't?
3. **Tune settings** → Adjust rules in `config.py`
4. **Deploy** → See `DEPLOYMENT.md` when ready

---

## 💡 Pro Tips

1. **Keep API running** while using browser UI
2. **Open DevTools** (F12) to see network requests
3. **Try all tiers** to understand rate limits
4. **Test edge cases** (empty messages, long text, etc.)
5. **Watch the headers** tab for rate limit info

---

## 📞 Need Help?

**Quick Checks:**
```bash
# Is API running?
curl http://localhost:8000/health

# Test API directly
curl -X POST http://localhost:8000/v1/decision \
  -H "Authorization: Bearer sk_test_demo_pro_key_123456789012345678" \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_plan": "free"}'

# Check logs
# Look at terminal where uvicorn is running
```

**Still stuck?**
- Check `BROWSER_TESTING.md` for detailed guide
- Try Swagger UI at `/docs` instead
- Review `QUICK_REFERENCE.md` for commands

---

## 🎉 You're Ready!

**Just run:**
```bash
./start.sh
```

**And start testing!** 🚀

The browser will open automatically with a beautiful UI where you can test everything without writing any code.
