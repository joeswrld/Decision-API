"""
Decision Intelligence API - Main Application

Architecture:
1. Rules run first (catch critical cases)
2. AI analyzes (advisory layer)
3. Validation ensures schema (safety net)
4. Confidence scoring (meta-layer)

This is production-ready: defensive, predictable, and testable.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from models import DecisionRequest, DecisionResponse, Decision, Priority
from rules import apply_rules
from ai_decision import get_ai_decision, get_fallback_decision
from confidence import calculate_confidence, should_apply_confidence_fallback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Decision Intelligence API",
    description="AI-powered customer message triage and decision engine",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "operational",
        "service": "Decision Intelligence API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "api": "online",
        "rules_engine": "online",
        "ai_layer": "online"  # In production, ping AI service here
    }


@app.post("/v1/decision", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest) -> DecisionResponse:
    """
    Main decision endpoint.
    
    Flow:
    1. Validate input (Pydantic does this automatically)
    2. Apply rule engine (terminal rules skip AI)
    3. Call AI for nuanced analysis (if needed)
    4. Merge rule + AI decisions (rules can override)
    5. Calculate confidence score
    6. Apply fallback if confidence too low
    7. Return validated response
    
    Errors:
    - 422: Invalid input schema
    - 500: Internal processing error (with safe fallback)
    """
    
    try:
        logger.info(f"Processing decision request: plan={request.user_plan.value}, channel={request.channel.value}")
        
        # STEP 1: Apply rule engine
        terminal_rule, all_rules = apply_rules(request)
        
        # If we have a terminal rule (legal, spam), return immediately
        if terminal_rule and terminal_rule.is_terminal:
            logger.info(f"Terminal rule matched: {terminal_rule.reason}")
            
            # Build response from rule
            response = DecisionResponse(
                decision=terminal_rule.decision,
                priority=terminal_rule.priority,
                churn_risk=0.0,  # Rules don't estimate churn
                confidence=0.9,  # High confidence in rule-based decisions
                recommended_action=terminal_rule.reason
            )
            
            return response
        
        # STEP 2: Call AI for advisory analysis
        ai_result = await get_ai_decision(request)
        ai_failed = False
        
        if not ai_result:
            logger.warning("AI decision failed, using fallback")
            ai_result = get_fallback_decision(request)
            ai_failed = True
        
        # STEP 3: Merge rule constraints with AI decision
        # Rules can set minimum priority levels
        final_decision = ai_result.decision
        final_priority = ai_result.priority
        
        # Check if any non-terminal rule sets a minimum decision level
        for rule in all_rules:
            if rule.decision:
                # If rule says "priority_response" and AI says "standard_response",
                # upgrade to rule's decision
                decision_hierarchy = [
                    Decision.IGNORE,
                    Decision.STANDARD_RESPONSE,
                    Decision.PRIORITY_RESPONSE,
                    Decision.IMMEDIATE_ESCALATION
                ]
                
                rule_level = decision_hierarchy.index(rule.decision)
                ai_level = decision_hierarchy.index(final_decision)
                
                if rule_level > ai_level:
                    final_decision = rule.decision
                    logger.info(f"Rule upgraded decision: {rule.reason}")
            
            if rule.priority:
                # Similar upgrade logic for priority
                priority_hierarchy = [
                    Priority.LOW,
                    Priority.MEDIUM,
                    Priority.HIGH,
                    Priority.CRITICAL
                ]
                
                rule_priority_level = priority_hierarchy.index(rule.priority)
                current_priority_level = priority_hierarchy.index(final_priority)
                
                if rule_priority_level > current_priority_level:
                    final_priority = rule.priority
        
        # STEP 4: Calculate confidence
        confidence = calculate_confidence(
            request=request,
            rule_results=all_rules,
            ai_result=ai_result,
            ai_failed=ai_failed
        )
        
        # STEP 5: Apply confidence-based fallback
        if should_apply_confidence_fallback(confidence):
            logger.warning(f"Low confidence ({confidence}), applying conservative fallback")
            
            # When uncertain, escalate
            if final_decision == Decision.IGNORE:
                final_decision = Decision.STANDARD_RESPONSE
                final_priority = Priority.MEDIUM
            elif final_decision == Decision.STANDARD_RESPONSE:
                final_decision = Decision.PRIORITY_RESPONSE
                final_priority = Priority.HIGH
            
            ai_result.recommended_action = f"[Low confidence - review required] {ai_result.recommended_action}"
        
        # STEP 6: Build final response
        response = DecisionResponse(
            decision=final_decision,
            priority=final_priority,
            churn_risk=ai_result.churn_risk,
            confidence=confidence,
            recommended_action=ai_result.recommended_action
        )
        
        logger.info(f"Decision complete: {final_decision.value}, priority={final_priority.value}, confidence={confidence}")
        
        return response
    
    except ValidationError as e:
        # This should rarely happen (Pydantic validates input)
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    
    except Exception as e:
        # Unexpected error - return safe fallback
        logger.error(f"Unexpected error: {e}", exc_info=True)
        
        # Emergency fallback: always safe to escalate when broken
        return DecisionResponse(
            decision=Decision.PRIORITY_RESPONSE,
            priority=Priority.HIGH,
            churn_risk=0.5,
            confidence=0.2,
            recommended_action="System error occurred. Manual review required immediately."
        )


# Exception handlers for better error responses
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors gracefully."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Invalid request format",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all handler for unexpected errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Safe fallback applied."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)