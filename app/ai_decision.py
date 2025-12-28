"""
AI decision layer - uses LLM to analyze intent and risk.
This is advisory only; rules can override it.
"""

import json
import logging
from typing import Optional
from models import DecisionRequest, DecisionResponse, Decision, Priority
import config

logger = logging.getLogger(__name__)


class AIDecisionResult:
    """Structured AI output (or None if AI fails)."""
    def __init__(
        self,
        decision: Decision,
        priority: Priority,
        churn_risk: float,
        recommended_action: str,
        raw_response: Optional[str] = None
    ):
        self.decision = decision
        self.priority = priority
        self.churn_risk = max(0.0, min(1.0, churn_risk))  # Clamp
        self.recommended_action = recommended_action
        self.raw_response = raw_response


def build_ai_prompt(request: DecisionRequest) -> str:
    """
    Construct a prompt that forces structured JSON output.
    We use few-shot examples to guide the model.
    """
    history_context = ""
    if request.history:
        history_context = f"\n- Previous interactions: {len(request.history)} messages"
    
    prompt = f"""You are a customer service decision AI. Analyze the message and return ONLY valid JSON.

Customer Context:
- Plan: {request.user_plan.value}
- Channel: {request.channel.value}{history_context}

Message: "{request.message}"

Return this exact JSON structure:
{{
  "decision": "ignore | standard_response | priority_response | immediate_escalation",
  "priority": "low | medium | high | critical",
  "churn_risk": <float 0.0-1.0>,
  "recommended_action": "<concise action for support team>"
}}

Rules:
- Use "immediate_escalation" for urgent, angry, or legal threats
- Use "priority_response" for paying customers with issues
- Use "standard_response" for normal questions/feedback
- Use "ignore" only for spam/noise (rare)
- churn_risk: 0.0 = happy, 1.0 = about to leave
- recommended_action: 1-2 sentences max

Return ONLY the JSON, no markdown, no explanation."""

    return prompt


async def call_ai_api(prompt: str) -> Optional[str]:
    """
    Call Google Gemini API for decision analysis.
    Uses gemini-1.5-flash for speed and cost-efficiency.
    
    Setup:
    1. pip install google-generativeai
    2. Set environment variable: GOOGLE_API_KEY=your_key_here
    3. Or pass API key in code (not recommended for production)
    
    Note: The Gemini SDK doesn't have native async support yet,
    so we run the synchronous call in an executor to avoid blocking.
    """
    try:
        import google.generativeai as genai
        import os
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        # Configure API key (from environment variable)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set")
            return None
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Flash for fast, cost-effective inference
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={
                'temperature': config.AI_TEMPERATURE,
                'max_output_tokens': config.AI_MAX_TOKENS,
            }
        )
        
        # Run synchronous Gemini call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            response = await loop.run_in_executor(
                executor,
                model.generate_content,
                prompt
            )
        
        if not response or not response.text:
            logger.error("Gemini returned empty response")
            return None
        
        return response.text
        
    except ImportError:
        logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        return None
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


async def get_ai_decision(request: DecisionRequest) -> Optional[AIDecisionResult]:
    """
    Main AI decision function.
    Returns None if AI fails (triggers fallback in main logic).
    """
    try:
        # Build prompt
        prompt = build_ai_prompt(request)
        
        # Call AI (with timeout)
        raw_response = await call_ai_api(prompt)
        
        if not raw_response:
            return None
        
        # Parse JSON
        # Handle markdown code blocks if present (some models add them)
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```"):
            # Extract JSON from markdown block
            lines = cleaned_response.split("\n")
            json_lines = [l for l in lines if not l.startswith("```")]
            cleaned_response = "\n".join(json_lines).strip()
        
        parsed = json.loads(cleaned_response)
        
        # Validate and extract fields
        decision = Decision(parsed["decision"])
        priority = Priority(parsed["priority"])
        churn_risk = float(parsed["churn_risk"])
        recommended_action = str(parsed["recommended_action"])
        
        # Sanity checks
        if not (0.0 <= churn_risk <= 1.0):
            churn_risk = max(0.0, min(1.0, churn_risk))
        
        if len(recommended_action) > 500:
            recommended_action = recommended_action[:497] + "..."
        
        return AIDecisionResult(
            decision=decision,
            priority=priority,
            churn_risk=churn_risk,
            recommended_action=recommended_action,
            raw_response=raw_response
        )
        
    except json.JSONDecodeError as e:
        # AI returned invalid JSON
        print(f"AI JSON parse error: {e}")
        return None
    except (KeyError, ValueError) as e:
        # AI returned JSON but wrong schema
        print(f"AI schema validation error: {e}")
        return None
    except Exception as e:
        # Network timeout, API error, etc.
        print(f"AI call failed: {e}")
        return None


def get_fallback_decision(request: DecisionRequest) -> AIDecisionResult:
    """
    If AI fails, return a safe conservative decision.
    Enterprise customers get priority, others get standard response.
    """
    if request.user_plan.value == "enterprise":
        return AIDecisionResult(
            decision=Decision.PRIORITY_RESPONSE,
            priority=Priority.HIGH,
            churn_risk=0.5,  # Uncertain, assume medium risk
            recommended_action="AI unavailable. Review manually and respond within 2 hours (enterprise SLA)."
        )
    else:
        return AIDecisionResult(
            decision=Decision.STANDARD_RESPONSE,
            priority=Priority.MEDIUM,
            churn_risk=0.3,
            recommended_action="AI unavailable. Review and respond using standard workflow."
        )