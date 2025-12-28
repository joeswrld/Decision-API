# Production Deployment Guide

## 🎯 Pre-Deployment Checklist

### Security
- [ ] API key stored in secret manager (AWS/GCP/Azure Secrets)
- [ ] `.env` files added to `.gitignore`
- [ ] No hardcoded credentials in code
- [ ] API authentication implemented (JWT/API keys)
- [ ] Rate limiting configured per user/IP
- [ ] CORS configured for allowed origins only
- [ ] HTTPS/TLS enabled

### Infrastructure
- [ ] Load balancer configured
- [ ] Multiple API instances (horizontal scaling)
- [ ] Health check endpoint tested
- [ ] Database for audit logs (optional)
- [ ] Redis/Memcached for caching (optional)
- [ ] CDN if serving static assets

### Monitoring & Logging
- [ ] Application logging to cloud service (CloudWatch/Stackdriver)
- [ ] Error tracking (Sentry/Rollbar)
- [ ] Performance monitoring (Datadog/New Relic)
- [ ] Gemini API usage tracking
- [ ] Alert on high error rates (>5%)
- [ ] Alert on API latency (>2s)
- [ ] Alert on Gemini API failures (>20%)

### Testing
- [ ] Load test completed (simulate 1000+ concurrent users)
- [ ] Stress test (find breaking point)
- [ ] Gemini failure simulation (disconnect/timeout)
- [ ] Invalid input fuzzing (random/malformed JSON)
- [ ] Edge cases tested (empty messages, huge messages)
- [ ] Fallback behavior verified

### Cost Management
- [ ] Gemini API budget alerts configured
- [ ] Daily cost monitoring dashboard
- [ ] Token usage logged per request
- [ ] Caching strategy for repeated queries
- [ ] Batch processing for non-urgent requests

---

## 🚀 Deployment Options

### Option 1: Docker (Recommended)

**Create `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Build and run:**
```bash
docker build -t decision-api .
docker run -p 8000:8000 -e GOOGLE_API_KEY=$GOOGLE_API_KEY decision-api
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Option 2: Google Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT/decision-api

# Deploy
gcloud run deploy decision-api \
  --image gcr.io/YOUR_PROJECT/decision-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
  --min-instances 1 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1
```

### Option 3: AWS ECS/Fargate

**task-definition.json:**
```json
{
  "family": "decision-api",
  "containerDefinitions": [{
    "name": "decision-api",
    "image": "YOUR_ECR_REPO/decision-api",
    "memory": 512,
    "cpu": 256,
    "essential": true,
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [{
      "name": "GOOGLE_API_KEY",
      "value": "{{resolve:secretsmanager:gemini-api-key:SecretString}}"
    }]
  }]
}
```

### Option 4: Traditional VPS/VM

**systemd service (`/etc/systemd/system/decision-api.service`):**
```ini
[Unit]
Description=Decision Intelligence API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/decision-api
Environment="GOOGLE_API_KEY=your_key"
ExecStart=/opt/decision-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable decision-api
sudo systemctl start decision-api
sudo systemctl status decision-api
```

---

## 📊 Production Configuration

### Uvicorn Settings

**For high traffic:**
```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --limit-concurrency 1000 \
  --timeout-keep-alive 5 \
  --log-level warning
```

**Worker calculation:**
```
Workers = (2 x CPU_CORES) + 1

For 2 CPU cores: 5 workers
For 4 CPU cores: 9 workers
```

### Environment Variables

**Required:**
```bash
GOOGLE_API_KEY=your_api_key
```

**Optional:**
```bash
LOG_LEVEL=INFO              # DEBUG|INFO|WARNING|ERROR
API_HOST=0.0.0.0
API_PORT=8000
MAX_WORKERS=4
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_TOKENS=500
GEMINI_TIMEOUT=10
RATE_LIMIT_PER_MINUTE=60
```

### Nginx Reverse Proxy

**`/etc/nginx/sites-available/decision-api`:**
```nginx
upstream decision_api {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://decision_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

---

## 🔍 Monitoring Setup

### Application Metrics to Track

1. **Request Metrics**
   - Requests per second
   - Response time (p50, p95, p99)
   - Error rate (4xx, 5xx)
   - Decision type distribution

2. **AI Metrics**
   - Gemini API latency
   - Gemini failure rate
   - Tokens consumed per request
   - Fallback trigger rate
   - Confidence score distribution

3. **Business Metrics**
   - Escalations per hour
   - Churn risk distribution
   - Rule vs AI decision ratio
   - Cost per 1000 decisions

### Sample Logging Enhancement

**Add to `main.py`:**
```python
import time
from datetime import datetime

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"path={request.url.path} "
        f"method={request.method} "
        f"status={response.status_code} "
        f"duration={duration:.3f}s "
        f"timestamp={datetime.utcnow().isoformat()}"
    )
    
    return response
```

### Sentry Integration

```bash
pip install sentry-sdk[fastapi]
```

**In `main.py`:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your_sentry_dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # Sample 10% of transactions
    environment="production"
)
```

---

## 💰 Cost Optimization

### Gemini API Costs

**Current setup (Gemini 1.5 Flash):**
- Input: ~200 tokens/request × $0.35/1M = $0.00007/request
- Output: ~150 tokens/request × $1.05/1M = $0.00016/request
- **Total: ~$0.00023 per decision**

**Monthly projections:**
| Daily Requests | Monthly Cost |
|----------------|--------------|
| 1,000          | ~$7          |
| 10,000         | ~$70         |
| 100,000        | ~$700        |
| 1,000,000      | ~$7,000      |

### Cost Reduction Strategies

1. **Aggressive rule filtering** (reduce AI calls by 30-40%)
   ```python
   # Expand spam/noise rules to catch more obvious cases
   # before hitting Gemini API
   ```

2. **Response caching** for similar queries
   ```python
   from functools import lru_cache
   import hashlib
   
   def hash_request(message: str, plan: str) -> str:
       return hashlib.md5(f"{message}{plan}".encode()).hexdigest()
   
   # Cache responses for 1 hour
   ```

3. **Batch processing** for non-urgent requests
   ```python
   # Queue low-priority requests and process in batches
   # during off-peak hours
   ```

4. **Use Flash over Pro** (already configured)
   - 3x cheaper with minimal accuracy loss

---

## 🚨 Incident Response

### Common Issues & Solutions

**1. High Error Rate**
```bash
# Check Gemini API status
curl https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash

# Check logs
tail -f /var/log/decision-api.log | grep ERROR

# Restart service
sudo systemctl restart decision-api
```

**2. High Latency**
```bash
# Check Gemini response times
grep "Gemini API error" /var/log/decision-api.log

# Scale workers
# Increase --workers in uvicorn command

# Check database/cache connections if applicable
```

**3. Gemini API Quota Exceeded**
```python
# Temporary fallback to rules-only mode
# Set environment variable:
export DISABLE_GEMINI=true

# Or add flag in config.py:
USE_AI = os.getenv("DISABLE_GEMINI", "false") == "false"
```

**4. Out of Memory**
```bash
# Check memory usage
top -o %MEM

# Reduce workers
# Check for memory leaks in logs
```

### Rollback Plan

**Quick rollback:**
```bash
# Docker
docker pull previous-version:tag
docker service update --image previous-version:tag decision-api

# Git-based
git checkout stable
sudo systemctl restart decision-api

# Cloud Run
gcloud run services update decision-api --image gcr.io/project/decision-api:previous
```

---

## ✅ Go-Live Checklist

**Day Before:**
- [ ] All tests passing
- [ ] Load test completed successfully
- [ ] Monitoring dashboards ready
- [ ] On-call rotation scheduled
- [ ] Rollback plan documented
- [ ] Stakeholders notified

**Launch Day:**
- [ ] Deploy to production
- [ ] Verify health check endpoint
- [ ] Run smoke tests on production URL
- [ ] Monitor error rates (first 1 hour)
- [ ] Check Gemini API usage/costs
- [ ] Verify logs are flowing to monitoring service

**Day After:**
- [ ] Review error logs
- [ ] Check cost actuals vs projections
- [ ] Analyze decision distribution
- [ ] Gather user feedback
- [ ] Document any issues

**Week After:**
- [ ] Performance review meeting
- [ ] Tune confidence thresholds if needed
- [ ] Optimize rules based on real data
- [ ] Plan iteration 2 features

---

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Production](https://www.uvicorn.org/deployment/)
- [Gemini API Best Practices](https://ai.google.dev/docs/best_practices)
- [Docker Production Guide](https://docs.docker.com/config/containers/resource_constraints/)

---

**Questions? Issues during deployment? Check the logs first, then reach out to the team.**