#!/bin/bash

# Decision Intelligence API Test Suite
# Run this after starting the API with: uvicorn main:app --reload

BASE_URL="http://localhost:8000"

echo "========================================="
echo "Decision Intelligence API Test Suite"
echo "========================================="
echo ""

# Health check
echo "1. Health Check"
curl -s $BASE_URL/health | jq '.'
echo -e "\n"

# Test 1: Legal threat (should escalate immediately)
echo "2. Test: Legal Threat (Rule-Based)"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "This is unacceptable. I will contact my lawyer if not resolved today.",
    "user_plan": "pro",
    "channel": "email"
  }' | jq '.'
echo -e "\n"

# Test 2: Enterprise customer with churn signals
echo "3. Test: Enterprise Customer Churn Risk"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "We are very disappointed with the service and considering switching to your competitor.",
    "user_plan": "enterprise",
    "channel": "email",
    "history": ["complaint 1", "complaint 2", "escalation"]
  }' | jq '.'
echo -e "\n"

# Test 3: Normal question
echo "4. Test: Standard Customer Question"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I reset my password? I cannot find the link in settings.",
    "user_plan": "free",
    "channel": "chat"
  }' | jq '.'
echo -e "\n"

# Test 4: Spam detection
echo "5. Test: Spam Detection"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Click here now! Limited offer!",
    "user_plan": "free",
    "channel": "social"
  }' | jq '.'
echo -e "\n"

# Test 5: Very short message (noise)
echo "6. Test: Short Message (Noise)"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ok",
    "user_plan": "free",
    "channel": "chat"
  }' | jq '.'
echo -e "\n"

# Test 6: Pro user with issue
echo "7. Test: Pro User With Issue"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The export feature has been broken for 3 days now and we need this for our business. This is really frustrating.",
    "user_plan": "pro",
    "channel": "email",
    "history": ["initial report"]
  }' | jq '.'
echo -e "\n"

# Test 7: Invalid request (should return 422)
echo "8. Test: Invalid Request (Missing Required Field)"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "user_plan": "pro"
  }' | jq '.'
echo -e "\n"

# Test 8: Edge case - empty message (should fail validation)
echo "9. Test: Empty Message (Should Fail)"
curl -s -X POST $BASE_URL/v1/decision \
  -H "Content-Type: application/json" \
  -d '{
    "message": "   ",
    "user_plan": "free",
    "channel": "email"
  }' | jq '.'
echo -e "\n"

echo "========================================="
echo "Test Suite Complete"
echo "========================================="
echo ""
echo "Expected Results:"
echo "1. Health check: status=healthy"
echo "2. Legal threat: decision=immediate_escalation, priority=critical"
echo "3. Enterprise churn: decision=priority_response, priority=high"
echo "4. Standard question: decision=standard_response, priority=medium"
echo "5. Spam: decision=ignore, priority=low"
echo "6. Short message: decision=ignore, priority=low"
echo "7. Pro issue: decision=priority_response or standard_response"
echo "8. Invalid request: error=422"
echo "9. Empty message: error=422"