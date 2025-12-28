# Paid API with Authentication & Rate Limits

## 🎯 Overview

Your Decision Intelligence API is now a **paid, authenticated service** with:

✅ **API Key Authentication** (Bearer tokens)  
✅ **Multi-Tier Pricing** (Free, Starter, Pro, Enterprise)  
✅ **Rate Limiting** (per-minute, per-day, per-month)  
✅ **Usage Tracking** (real-time monitoring)  
✅ **Automatic Headers** (rate limit info in every response)

---

## 💰 Pricing Tiers

| Tier | Price/Month | Requests/Min | Requests/Day | Requests/Month |
|------|-------------|--------------|--------------|----------------|
| **Free** | $0 | 10 | 100 | 1,000 |
| **Starter** | $29 | 60 | 5,000 | 100,000 |
| **Professional** | $99 | 300 | 50,000 | 1,000,000 |
| **Enterprise** | $499 | 1,000 | 500,000 | 10,000,000 |

**Overage Pricing**: $0.001 per request beyond monthly limit

---

## 🔑 Getting an API Key

### Option 1: Use Demo Keys (Testing)

We've pre-created test keys for you:

```bash
# Free Tier
sk_test_demo_free_key_12345678901234567890

# Starter Tier  
sk_test_demo_starter_key_1234567890123456

# Professional Tier
sk_test_demo_pro_key_123456789012345678
```

### Option 2: Generate Your Own Key

```bash
curl -X POST http://localhost:8000/v1/keys/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_12345",
    "tier": "professional",
    "email": "you@company.com",
    "name": "Production API Key",
    "is_test": false
  }'
```

**Response:**
```json
{
  "api_key": "sk_live_AbCdEf123456...",
  "tier": "professional",
  "limits": {...},
  "warning": "Save this key securely. It will not be shown again.",
  "usage": "Set header: Authorization: Bearer sk_live_AbCdEf123456..."
}
```

⚠️ **IMPORTANT**: Save the key immediately. It's only shown once!

---

## 🚀 Using Your API Key

### Method 1: Authorization Header (Recommended)

```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk_test_demo_pro_key_123456789012345678" \
  -d '{
    "message": "I will contact my lawyer about this",
    "user_plan": "enterprise",
    "channel": "email"
  }'
```

### Method 2: X-API-Key Header

```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_test_demo_pro_key_123456789012345678" \
  -d '{
    "message": "How do I reset my password?",
    "user_plan": "free",
    "channel": "chat"
  }'
```

### Method 3: Query Parameter (Not Recommended for Production)

```bash
curl -X POST "http://localhost:8000/v1/decision?api_key=sk_test_demo_pro_key_123456789012345678" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message", "user_plan": "free"}'
```

⚠️ Query parameters expose keys in logs. Use headers in production.

---

## 📊 Rate Limit Headers

Every response includes rate limit information:

```http
X-RateLimit-Limit-Minute: 300
X-RateLimit-Remaining-Minute: 287
X-RateLimit-Limit-Day: 50000
X-RateLimit-Remaining-Day: 48234
X-RateLimit-Reset: 1704153600
X-RateLimit-Tier: professional
```

**Header Meanings:**
- `X-RateLimit-Limit-Minute`: Requests allowed per minute
- `X-RateLimit-Remaining-Minute`: Requests left this minute
- `X-RateLimit-Limit-Day`: Requests allowed per day
- `X-RateLimit-Remaining-Day`: Requests left today
- `X-RateLimit-Reset`: Unix timestamp when daily limit resets
- `X-RateLimit-Tier`: Your current subscription tier

---

## ⚠️ Error Responses

### 401 Unauthorized (Missing/Invalid API Key)

```json
{
  "error": "authentication_failed",
  "message": "Missing API key. Provide via 'Authorization: Bearer YOUR_KEY' header.",
  "docs": "https://docs.yourapi.com/authentication"
}
```

**Fix**: Add valid API key to request headers.

### 429 Too Many Requests (Rate Limit Exceeded)

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded (300 requests/minute)",
  "retry_after": "42",
  "docs": "https://docs.yourapi.com/rate-limits"
}
```

**Headers:**
```http
Retry-After: 42
```

**Fix**: Wait `retry_after` seconds before retrying, or upgrade tier.

---

## 📈 Check Your Usage

Get real-time usage statistics:

```bash
curl http://localhost:8000/v1/usage \
  -H "Authorization: Bearer sk_test_demo_pro_key_123456789012345678"
```

**Response:**
```json
{
  "tier": "professional",
  "usage": {
    "requests_today": 1234,
    "requests_this_month": 45678,
    "last_request_at": "2024-01-15T14:23:45.123456"
  },
  "limits": {
    "requests_per_day": 50000,
    "requests_per_month": 1000000
  },
  "remaining": {
    "today": 48766,
    "this_month": 954322
  },
  "estimated_cost_this_month": {
    "included_requests": 1000000,
    "overage_requests": 0,
    "overage_cost_usd": 0.0,
    "total_cost_usd": 99.0
  }
}
```

---

## 🔐 Security Best Practices

### 1. Never Commit Keys to Git

```bash
# Add to .gitignore
echo "*.key" >> .gitignore
echo ".env" >> .gitignore
```

### 2. Use Environment Variables

```bash
export API_KEY="sk_live_your_key_here"

curl -H "Authorization: Bearer $API_KEY" ...
```

### 3. Rotate Keys Regularly

```python
# Deactivate old key
api_key_store.deactivate_key(old_key_hash)

# Generate new key
new_key = api_key_store.create_key(user_id, tier, email)
```

### 4. Use Different Keys for Different Environments

```
sk_test_*  → Development/Staging
sk_live_*  → Production
```

### 5. Monitor for Unauthorized Usage

```python
# Check unusual patterns
if api_key.requests_today > usual_daily_average * 3:
    alert_team()
```

---

## 🧪 Testing Rate Limits

### Test Per-Minute Limit

```bash
# Free tier: 10 req/min
for i in {1..15}; do
  curl -X POST http://localhost:8000/v1/decision \
    -H "Authorization: Bearer sk_test_demo_free_key_12345678901234567890" \
    -H "Content-Type: application/json" \
    -d '{"message":"Test '$i'","user_plan":"free"}' &
done
wait

# Requests 11-15 should return 429
```

### Test Daily Limit

```python
import requests

API_KEY = "sk_test_demo_free_key_12345678901234567890"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Free tier: 100 req/day
for i in range(105):
    response = requests.post(
        "http://localhost:8000/v1/decision",
        headers=headers,
        json={"message": f"Test {i}", "user_plan": "free"}
    )
    
    if response.status_code == 429:
        print(f"Rate limited at request {i}")
        print(f"Retry after: {response.headers.get('Retry-After')} seconds")
        break
```

---

## 💡 Client Implementation Examples

### Python

```python
import requests
import os

class DecisionAPIClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def make_decision(self, message: str, user_plan: str = "free", 
                     channel: str = "email", history: list = None):
        """Make a decision request."""
        payload = {
            "message": message,
            "user_plan": user_plan,
            "channel": channel,
            "history": history or []
        }
        
        response = self.session.post(
            f"{self.base_url}/v1/decision",
            json=payload
        )
        
        # Check rate limits
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(f"Rate limited. Retry after {retry_after}s")
        
        response.raise_for_status()
        return response.json()
    
    def get_usage(self):
        """Get current usage statistics."""
        response = self.session.get(f"{self.base_url}/v1/usage")
        response.raise_for_status()
        return response.json()

# Usage
client = DecisionAPIClient(api_key=os.getenv("API_KEY"))

result = client.make_decision(
    message="I will sue you if this isn't fixed",
    user_plan="enterprise",
    channel="email"
)

print(f"Decision: {result['decision']}")
print(f"Priority: {result['priority']}")
print(f"Confidence: {result['confidence']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

class DecisionAPIClient {
  constructor(apiKey, baseURL = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async makeDecision(message, userPlan = 'free', channel = 'email', history = []) {
    try {
      const response = await this.client.post('/v1/decision', {
        message,
        user_plan: userPlan,
        channel,
        history
      });
      
      // Log rate limit info
      console.log('Remaining requests (minute):', 
        response.headers['x-ratelimit-remaining-minute']);
      
      return response.data;
    } catch (error) {
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'];
        throw new Error(`Rate limited. Retry after ${retryAfter}s`);
      }
      throw error;
    }
  }

  async getUsage() {
    const response = await this.client.get('/v1/usage');
    return response.data;
  }
}

// Usage
const client = new DecisionAPIClient(process.env.API_KEY);

const result = await client.makeDecision(
  'How do I reset my password?',
  'pro',
  'chat'
);

console.log('Decision:', result.decision);
console.log('Confidence:', result.confidence);
```

---

## 🔄 Handling Rate Limits in Production

### Exponential Backoff

```python
import time
import random

def make_decision_with_retry(client, message, max_retries=3):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return client.make_decision(message)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
```

### Request Queuing

```python
from queue import Queue
from threading import Thread
import time

class RateLimitedQueue:
    def __init__(self, client, requests_per_second=5):
        self.client = client
        self.queue = Queue()
        self.delay = 1.0 / requests_per_second
        self.worker = Thread(target=self._process_queue, daemon=True)
        self.worker.start()
    
    def _process_queue(self):
        while True:
            message, callback = self.queue.get()
            try:
                result = self.client.make_decision(message)
                callback(result, None)
            except Exception as error:
                callback(None, error)
            
            time.sleep(self.delay)
    
    def enqueue(self, message, callback):
        self.queue.put((message, callback))

# Usage
queue = RateLimitedQueue(client, requests_per_second=4)

def handle_result(result, error):
    if error:
        print(f"Error: {error}")
    else:
        print(f"Decision: {result['decision']}")

queue.enqueue("Test message", handle_result)
```

---

## 📊 Monitoring & Analytics

### Track Key Metrics

```python
# metrics.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class APIMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    rate_limited_requests: int = 0
    average_response_time: float = 0.0
    last_updated: datetime = None

metrics = APIMetrics()

def track_request(response, duration):
    """Track request metrics."""
    metrics.total_requests += 1
    metrics.last_updated = datetime.utcnow()
    
    if response.status_code == 200:
        metrics.successful_requests += 1
    elif response.status_code == 429:
        metrics.rate_limited_requests += 1
    
    # Update average response time
    metrics.average_response_time = (
        (metrics.average_response_time * (metrics.total_requests - 1) + duration)
        / metrics.total_requests
    )
```

---

## 🚀 Production Deployment

### Environment Variables

```bash
# .env.production
API_KEY=sk_live_your_production_key_here
API_BASE_URL=https://api.yourdomain.com
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

### Docker Compose with Client

```yaml
version: '3.8'
services:
  decision-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
  
  api-client:
    build: ./client
    environment:
      - API_KEY=${API_KEY}
      - API_BASE_URL=http://decision-api:8000
```

---

## 💰 Cost Calculation

### Monthly Cost Estimator

```python
def estimate_monthly_cost(requests_per_day: int, tier: str):
    """Estimate monthly API costs."""
    TIERS = {
        'free': (0, 1000),
        'starter': (29, 100000),
        'professional': (99, 1000000),
        'enterprise': (499, 10000000)
    }
    
    base_price, included = TIERS[tier]
    monthly_requests = requests_per_day * 30
    
    overage = max(0, monthly_requests - included)
    overage_cost = overage * 0.001
    
    total_cost = base_price + overage_cost
    
    return {
        'tier': tier,
        'base_price': base_price,
        'included_requests': included,
        'total_requests': monthly_requests,
        'overage_requests': overage,
        'overage_cost': overage_cost,
        'total_cost': total_cost
    }

# Example
print(estimate_monthly_cost(5000, 'starter'))
# Output: {'total_cost': 79.0, ...} if using 150K requests
```

---

## 🎓 Best Practices Checklist

- [ ] Use environment variables for API keys
- [ ] Implement exponential backoff for retries
- [ ] Monitor rate limit headers in responses
- [ ] Set up alerts for approaching limits
- [ ] Use different keys for dev/staging/prod
- [ ] Rotate keys every 90 days
- [ ] Log all API errors for debugging
- [ ] Cache responses where appropriate
- [ ] Implement circuit breakers for failures
- [ ] Track costs and usage metrics

---

## 🆘 Troubleshooting

### "Authentication failed"
- Check API key is correct
- Verify key is active (not deactivated)
- Ensure using correct header format

### "Rate limit exceeded"
- Check current usage: `GET /v1/usage`
- Wait for `Retry-After` seconds
- Consider upgrading tier

### "Invalid API key format"
- Key must start with `sk_live_` or `sk_test_`
- Key must be 40+ characters
- No spaces or special chars in key

---

**Ready to monetize your API!** 🎉

Start with the demo keys, test the rate limits, then deploy to production with real authentication and billing integration.