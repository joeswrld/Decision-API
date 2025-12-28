# Decision Intelligence API

A production-ready customer message triage system using **rules-first, AI-assisted** decision making.

**AI Provider**: Google Gemini 1.5 Flash

## 🚀 Quick Start

```bash
# 1. Get Gemini API key from https://makersuite.google.com/app/apikey
# 2. Set environment variable
export GOOGLE_API_KEY="your_key_here"

# 3. Install and run
pip install -r requirements.txt
uvicorn main:app --reload

# 4. Test
./test_api.sh
```

**See [GEMINI_SETUP.md](GEMINI_SETUP.md) for detailed setup guide.**

```
Request → Rules Engine → AI Layer → Validation → Response
          (critical)     (advisory)   (safety)
```

### Core Principles

1. **Rules First**: Critical cases (legal threats, spam) handled deterministically
2. **AI Advisory**: Nuanced analysis for edge cases and churn prediction
3. **Safe Degradation**: AI failure → intelligent fallback, never crash
4. **Confidence Scoring**: Every decision includes reliability metric

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the API

```bash
# Development mode
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API will be available at:
- **Local**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **Health**: http://localhost:8000/health

## API Usage

### Endpoint: `POST /v1/decision`

**Request Body:**
```json
{
  "message": "I'm extremely disappointed and considering legal action",
  "user_plan": "enterprise",
  "channel": "email",
  "history": ["previous complaint", "unresolved issue"]
}
```

**Response:**
```json
{
  "decision": "immediate_escalation",
  "priority": "critical",
  "churn_risk": 0.95,
  "confidence": 0.92,
  "recommended_action": "Escalate to legal team immediately. Customer threatening legal action."
}
```

### Example cURL Requests

**1. Legal Threat (Rule-Based Escalation)**
```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "This is unacceptable. I will contact my lawyer if not resolved.",
    "user_plan": "pro",
    "channel": "email"
  }'
```

**2. Enterprise Customer Issue**
```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "We are considering switching to a competitor. Service has been unreliable.",
    "user_plan": "enterprise",
    "channel": "email",
    "history": ["complaint 1", "complaint 2", "complaint 3"]
  }'
```

**3. Standard Question**
```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I reset my password?",
    "user_plan": "free",
    "channel": "chat"
  }'
```

**4. Spam/Noise**
```bash
curl -X POST http://localhost:8000/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Click here now!",
    "user_plan": "free",
    "channel": "social"
  }'
```

## Decision Logic

### Decision Types (in escalation order)

1. **ignore**: Spam, noise, very low-signal messages
2. **standard_response**: Normal customer inquiries
3. **priority_response**: Paying customers with issues, multiple complaints
4. **immediate_escalation**: Legal threats, critical issues

### Priority Levels

- **low**: Routine, no urgency
- **medium**: Standard customer service queue
- **high**: Paying customer issues, churn risk
- **critical**: Legal/compliance, severe customer issues

## Rule Engine

### Critical Rules (Terminal)

1. **Legal Keywords**: `lawsuit`, `lawyer`, `attorney`, `sue` → Immediate escalation
2. **Spam Detection**: Very short messages, promotional language → Ignore
3. **Length Check**: < 10 characters → Ignore (likely noise)

### Advisory Rules (Boost Priority)

1. **Enterprise + Negative**: Enterprise customer with threat keywords → Priority minimum
2. **History Patterns**: 5+ previous interactions → Confidence boost

## Confidence Scoring

Combines multiple signals:

- ✅ Rule matches (+0.15 to +0.3)
- ✅ Message quality (+0.1 for detailed, -0.1 for vague)
- ✅ Question marks (+0.05)
- ✅ History context (+0.03 per interaction, max +0.15)
- ✅ Enterprise plan (+0.1)
- ✅ AI alignment with churn risk (+0.05 to +0.1)
- ❌ AI failure (-0.2)

### Low Confidence Fallback

If confidence < 0.4:
- `ignore` → `standard_response`
- `standard_response` → `priority_response`
- Message flagged for manual review

## AI Integration - Google Gemini

### Setup

1. **Get API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key

2. **Set Environment Variable**
   ```bash
   # Linux/Mac
   export GOOGLE_API_KEY="your_api_key_here"
   
   # Windows (PowerShell)
   $env:GOOGLE_API_KEY="your_api_key_here"
   
   # Or add to .env file
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Model Used: Gemini 1.5 Flash

**Why Flash?**
- ⚡ **Fast**: ~200ms response time
- 💰 **Cheap**: $0.35 per 1M tokens (input), $1.05 per 1M tokens (output)
- 🎯 **Accurate**: Good enough for decision logic
- 📊 **Long Context**: 1M token window (not needed here, but available)

**Alternative: Gemini 1.5 Pro**
If you need higher accuracy, change in `ai_decision.py`:
```python
model = genai.GenerativeModel(model_name='gemini-1.5-pro')
```
- More accurate but slower and 3x more expensive
- Use for complex edge cases or if Flash quality isn't sufficient

### Configuration

Edit `config.py` to tune Gemini behavior:

```python
AI_TEMPERATURE = 0.2      # 0.0-1.0 (lower = more deterministic)
AI_MAX_TOKENS = 500       # Response length limit
AI_TIMEOUT_SECONDS = 10   # API timeout
```

### Testing Without API Key

The API will gracefully fallback to rule-based decisions if:
- `GOOGLE_API_KEY` not set
- Gemini API is down
- Rate limits hit
- Any other error

**Test fallback behavior:**
```bash
# Don't set API key
unset GOOGLE_API_KEY

# Run API - will use fallback logic
uvicorn main:app --reload
```

## Error Handling

### Graceful Degradation

1. **AI Fails**: Falls back to rule-based + conservative escalation
2. **Schema Invalid**: AI returns bad JSON → Fallback decision
3. **Timeout**: 10 second limit → Fallback
4. **Unexpected Error**: Emergency escalation + manual review flag

### No Silent Failures

- All errors logged
- All failures trigger safe fallback
- Low confidence scores flag uncertain decisions

## Testing

### Run the API

```bash
# Terminal 1: Start server
uvicorn main:app --reload

# Terminal 2: Test endpoints
bash test_api.sh  # Create this with curl commands above
```

### Test Cases to Try

1. ✅ Legal keyword → Should escalate immediately
2. ✅ Spam message → Should ignore
3. ✅ Enterprise + negative → Should prioritize
4. ✅ Short message → Should ignore
5. ✅ Normal question → Standard response
6. ❌ Invalid JSON → Should return 422
7. ❌ Empty message → Should return 422

## Configuration

Edit `config.py` to tune behavior:

```python
# Add more legal keywords
LEGAL_KEYWORDS.add("injunction")

# Adjust confidence thresholds
LOW_CONFIDENCE_THRESHOLD = 0.5  # More conservative

# Change AI temperature
AI_TEMPERATURE = 0.1  # Even more deterministic
```

## Production Checklist

- [ ] Replace mock AI with real API client
- [ ] Add API key management (env vars, secrets)
- [ ] Set up logging/monitoring (Datadog, Sentry)
- [ ] Add rate limiting (per user/IP)
- [ ] Configure CORS if needed
- [ ] Add authentication/authorization
- [ ] Set up CI/CD pipeline
- [ ] Load test with realistic traffic
- [ ] Monitor AI costs and latency
- [ ] Set up alerting for AI failures

## File Structure

```
decision_api/
├── main.py              # FastAPI app + endpoint
├── models.py            # Pydantic schemas (request/response)
├── rules.py             # Rule engine logic
├── ai_decision.py       # AI integration layer
├── confidence.py        # Confidence scoring
├── config.py            # Constants and settings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Key Design Decisions

### Why Rules First?

- **Legal compliance**: Can't afford to miss legal threats
- **Cost efficiency**: Filtering spam before AI saves $$
- **Predictability**: Rules are debuggable, AI is not

### Why Low Temperature?

- Decisions need consistency
- We're not doing creative writing
- 0.2-0.3 gives good balance of reasoning + determinism

### Why Confidence Scores?

- Honest about uncertainty
- Enables human-in-the-loop for edge cases
- Improves over time (feedback loop)

### Why Fallback Everything?

- AI is advisory, not critical path
- Network/API failures happen
- Better to escalate than miss important messages

## License

MIT

## Support

Questions? Issues? Feedback?
- Check `/docs` endpoint for interactive API docs
- Review logs for debugging
- Adjust `config.py` for tuning