# Quick Reference - Decision Intelligence API

## 🚀 One-Minute Setup

```bash
export GOOGLE_API_KEY="your_gemini_key"
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🔑 Demo API Keys

```bash
FREE="sk_test_demo_free_key_12345678901234567890"
STARTER="sk_test_demo_starter_key_1234567890123456"
PRO="sk_test_demo_pro_key_123456789012345678"
```

---

## 📡 API Endpoints

### Make Decision (Authenticated)
```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Authorization: Bearer $PRO" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I will sue you",
    "user_plan": "enterprise",
    "channel": "email"
  }'
```

### Check Usage
```bash
curl http://localhost:8000/v1/usage \
  -H "Authorization: Bearer $PRO"
```

### Get Pricing
```bash
curl http://localhost:8000/v1/pricing
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## 💰 Pricing

| Tier | $/mo | req/min | req/day | req/month |
|------|------|---------|---------|-----------|
| Free | $0 | 10 | 100 | 1K |
| Starter | $29 | 60 | 5K | 100K |
| Pro | $99 | 300 | 50K | 1M |
| Enterprise | $499 | 1K | 500K | 10M |

---

## 📊 Response Structure

```json
{
  "decision": "immediate_escalation",
  "priority": "critical",
  "churn_risk": 0.95,
  "confidence": 0.92,
  "recommended_action": "Escalate to legal..."
}
```

**Decisions:** `ignore | standard_response | priority_response | immediate_escalation`  
**Priorities:** `low | medium | high | critical`

---

## 🔒 Authentication

### Method 1: Authorization Header
```bash
Authorization: Bearer sk_live_xxx
```

### Method 2: X-API-Key Header
```bash
X-API-Key: sk_live_xxx
```

---

## ⚠️ Error Codes

| Code | Error | Fix |
|------|-------|-----|
| 401 | Authentication failed | Add valid API key |
| 429 | Rate limit exceeded | Wait or upgrade tier |
| 422 | Invalid input | Check JSON schema |
| 500 | Internal error | Check logs |

---

## 📈 Rate Limit Headers

```http
X-RateLimit-Remaining-Minute: 287
X-RateLimit-Remaining-Day: 48234
X-RateLimit-Reset: 1704153600
Retry-After: 42
```

---

## 🧪 Quick Test

```bash
./test_api.sh
```

---

## 🐍 Python Client

```python
import requests

API_KEY = "sk_test_demo_pro_key_123456789012345678"

response = requests.post(
    "http://localhost:8000/v1/decision",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"message": "I will sue", "user_plan": "pro"}
)

print(response.json()["decision"])
```

---

## 🔧 Common Commands

```bash
# Start API
uvicorn main:app --reload

# Start with workers
uvicorn main:app --workers 4

# Check logs
tail -f /var/log/decision-api.log

# Test authentication
curl -H "Authorization: Bearer $FREE" \
  http://localhost:8000/v1/usage
```

---

## 📚 Full Documentation

- **Setup**: `GEMINI_SETUP.md`
- **Authentication**: `PAID_API_GUIDE.md`
- **Migration**: `MIGRATION.md`
- **Deployment**: `DEPLOYMENT.md`
- **Overview**: `PROJECT_SUMMARY.md`

---

## 💡 Pro Tips

1. **Start with demo keys** for testing
2. **Monitor `/v1/usage`** regularly
3. **Check rate limit headers** in responses
4. **Use different keys** for dev/prod
5. **Implement retry logic** with exponential backoff

---

## 🚨 Emergency Commands

```bash
# Restart API
sudo systemctl restart decision-api

# Check if API is running
curl http://localhost:8000/health

# View recent errors
tail -100 /var/log/decision-api.log | grep ERROR

# Check Gemini API status
curl https://generativelanguage.googleapis.com/
```

---

**Need help?** Check docs or run `./test_api.sh`