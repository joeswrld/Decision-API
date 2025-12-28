# Migration Guide: Free → Paid API

## 🎯 What Changed?

Your Decision Intelligence API now requires **authentication** and includes **rate limiting**.

### Before (v1.0)
```bash
# Anyone could call it
curl -X POST http://localhost:8000/v1/decision \
  -d '{"message": "test"}'
```

### After (v2.0)
```bash
# Requires API key
curl -X POST http://localhost:8000/v1/decision \
  -H "Authorization: Bearer sk_live_xxx" \
  -d '{"message": "test"}'
```

---

## 📦 New Files Added

```
decision_api/
├── auth.py              # ✨ NEW: API key management
├── rate_limit.py        # ✨ NEW: Rate limiting logic
├── middleware.py        # ✨ NEW: Authentication middleware
├── main.py              # 🔄 UPDATED: Added auth middleware
└── requirements.txt     # 🔄 UPDATED: No new dependencies needed
```

**Total new code**: ~500 lines  
**Breaking changes**: All `/v1/*` endpoints now require auth

---

## 🚀 Migration Steps

### Step 1: Update Your Code

**Pull the new files:**
```bash
git pull origin main
# Or download: auth.py, rate_limit.py, middleware.py
# And updated: main.py
```

### Step 2: Restart the API

```bash
# No new dependencies to install!
uvicorn main:app --reload
```

### Step 3: Get an API Key

**Option A: Use demo keys (testing)**
```bash
# Pre-configured test keys
FREE_KEY="sk_test_demo_free_key_12345678901234567890"
STARTER_KEY="sk_test_demo_starter_key_1234567890123456"
PRO_KEY="sk_test_demo_pro_key_123456789012345678"
```

**Option B: Generate your own**
```bash
curl -X POST http://localhost:8000/v1/keys/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your_user_id",
    "tier": "professional",
    "email": "you@company.com",
    "name": "Production Key"
  }'

# Save the returned key immediately!
```

### Step 4: Update Your Clients

**Python:**
```python
# OLD
response = requests.post(
    "http://localhost:8000/v1/decision",
    json={"message": "test"}
)

# NEW
response = requests.post(
    "http://localhost:8000/v1/decision",
    headers={"Authorization": f"Bearer {API_KEY}"},  # Add this
    json={"message": "test"}
)
```

**JavaScript:**
```javascript
// OLD
fetch('http://localhost:8000/v1/decision', {
  method: 'POST',
  body: JSON.stringify({message: 'test'})
})

// NEW
fetch('http://localhost:8000/v1/decision', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,  // Add this
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({message: 'test'})
})
```

**cURL:**
```bash
# OLD
curl -X POST http://localhost:8000/v1/decision \
  -d '{"message": "test"}'

# NEW
curl -X POST http://localhost:8000/v1/decision \
  -H "Authorization: Bearer $API_KEY" \  # Add this
  -d '{"message": "test"}'
```

### Step 5: Test It

```bash
# Run the updated test suite
chmod +x test_api.sh
./test_api.sh
```

---

## 📊 What Stayed the Same

✅ **Request format**: Exact same JSON structure  
✅ **Response format**: Exact same JSON structure  
✅ **Decision logic**: Rules + AI flow unchanged  
✅ **Gemini integration**: Still uses same AI layer  
✅ **Performance**: Same latency (~200-500ms)

**The only change**: You now need to include an API key.

---

## 🔄 Backward Compatibility

### Public Endpoints (No Auth Required)

These endpoints still work without authentication:

- `GET /` - Root/welcome
- `GET /health` - Health check
- `GET /docs` - API documentation
- `GET /v1/pricing` - Pricing info

### Protected Endpoints (Auth Required)

These now require an API key:

- `POST /v1/decision` - Make decision
- `GET /v1/usage` - Check usage stats

---

## 💰 Rate Limits by Tier

| Tier | Cost | Requests/Min | Requests/Day | Requests/Month |
|------|------|--------------|--------------|----------------|
| Free | $0 | 10 | 100 | 1,000 |
| Starter | $29 | 60 | 5,000 | 100,000 |
| Pro | $99 | 300 | 50,000 | 1,000,000 |
| Enterprise | $499 | 1,000 | 500,000 | 10,000,000 |

**Start with Free tier** to test, then upgrade as needed.

---

## 🐛 Troubleshooting Migration

### Error: "Missing API key"

**Problem:** Not sending API key in request.

**Fix:**
```bash
# Make sure you include Authorization header
curl -H "Authorization: Bearer YOUR_KEY" ...
```

### Error: "Invalid API key format"

**Problem:** API key doesn't match expected format.

**Fix:**
- Keys must start with `sk_live_` or `sk_test_`
- Use one of the demo keys or generate a new one
- Check for typos or extra spaces

### Error: "Rate limit exceeded"

**Problem:** Hit your tier's rate limit.

**Fix:**
```bash
# Check your usage
curl http://localhost:8000/v1/usage \
  -H "Authorization: Bearer YOUR_KEY"

# Wait for rate limit to reset, or upgrade tier
```

### Old Clients Breaking

**Problem:** Existing clients don't send API key.

**Temporary workaround** (development only):
```python
# In middleware.py, temporarily skip auth for testing
public_paths = ["/", "/health", "/docs", "/openapi.json", "/redoc", 
                "/v1/decision"]  # Add this temporarily

# Remove after clients are updated!
```

---

## 📈 Monitoring After Migration

### Check Usage Regularly

```bash
# Get current usage
curl http://localhost:8000/v1/usage \
  -H "Authorization: Bearer YOUR_KEY" | jq '.'
```

### Watch Rate Limit Headers

```python
response = requests.post(url, headers=headers, json=data)

# Check how many requests you have left
remaining = response.headers.get('X-RateLimit-Remaining-Day')
print(f"Requests remaining today: {remaining}")
```

### Set Up Alerts

```python
def check_usage_alert(usage_data):
    """Alert if approaching limits."""
    remaining_pct = (
        usage_data['remaining']['this_month'] / 
        usage_data['limits']['requests_per_month']
    )
    
    if remaining_pct < 0.2:  # Less than 20% remaining
        send_alert("Approaching monthly API limit!")
```

---

## 🎯 Next Steps

1. **Test locally**: Use demo keys to verify everything works
2. **Update all clients**: Add authentication headers
3. **Monitor usage**: Check `/v1/usage` endpoint regularly
4. **Choose tier**: Based on your actual usage patterns
5. **Set up billing**: Integrate Stripe/payment system

---

## 💡 Pro Tips

### 1. Use Environment Variables

```bash
# Don't hardcode keys!
export API_KEY="sk_live_xxx"

curl -H "Authorization: Bearer $API_KEY" ...
```

### 2. Different Keys for Different Environments

```
Development:  sk_test_dev_xxx
Staging:      sk_test_staging_xxx
Production:   sk_live_prod_xxx
```

### 3. Implement Retry Logic

```python
def make_request_with_retry(url, data, api_key, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                json=data
            )
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue
            
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

### 4. Cache Responses (When Appropriate)

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_decision(message_hash):
    """Cache decisions for identical messages."""
    # Only cache for stable, non-time-sensitive decisions
    pass
```

---

## 🔐 Security Checklist

After migration:

- [ ] API keys stored in environment variables
- [ ] No keys committed to Git
- [ ] Different keys for dev/staging/prod
- [ ] Keys rotated every 90 days
- [ ] Usage monitoring set up
- [ ] Rate limit alerts configured
- [ ] Error logging enabled

---

## 📞 Need Help?

**Common issues:**
1. Check logs: `tail -f /var/log/decision-api.log`
2. Verify API key format: `sk_test_*` or `sk_live_*`
3. Test with demo keys first
4. Review `PAID_API_GUIDE.md` for full docs

**Still stuck?**
- Run `./test_api.sh` to verify setup
- Check `/health` endpoint is responding
- Confirm middleware is loaded: check startup logs

---

**Migration complete!** 🎉

Your API is now production-ready with authentication and rate limiting.