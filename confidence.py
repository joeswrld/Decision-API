"""
Confidence scoring - combines rule signals and AI certainty.
Higher confidence = more reliable decision.
"""

from typing import List
from models import DecisionRequest
from rules import RuleResult
from ai_decision import AIDecisionResult
import config


def calculate_confidence(
    request: DecisionRequest,
    rule_results: List[RuleResult],
    ai_result: AIDecisionResult,
    ai_failed: bool = False
) -> float:
    """
    Calculate confidence score (0.0 - 1.0) based on multiple signals.
    
    Factors:
    1. Rule matches (strong signal)
    2. Message clarity (length, structure)
    3. AI availability (penalty if failed)
    4. History (more context = higher confidence)
    """
    
    confidence = 0.5  # Base confidence
    
    # Factor 1: Rule boost
    for rule in rule_results:
        confidence += rule.confidence_boost
    
    # Factor 2: Message quality
    message_length = len(request.message.strip())
    if message_length > 100:
        confidence += 0.1  # Detailed message = clearer intent
    elif message_length < 30:
        confidence -= 0.1  # Very short = ambiguous
    
    # Check for question marks (questions are clearer intent)
    if "?" in request.message:
        confidence += 0.05
    
    # Factor 3: AI availability penalty
    if ai_failed:
        confidence -= 0.2  # Significant penalty for AI failure
    
    # Factor 4: History context
    if request.history and len(request.history) > 0:
        history_boost = min(0.15, len(request.history) * 0.03)
        confidence += history_boost
    
    # Factor 5: Enterprise customers (more context assumed)
    if request.user_plan.value == "enterprise":
        confidence += 0.1
    
    # Factor 6: Churn risk alignment
    # High churn risk with escalation decision = good alignment
    if ai_result.churn_risk > 0.7 and ai_result.decision.value in ["priority_response", "immediate_escalation"]:
        confidence += 0.1
    elif ai_result.churn_risk < 0.3 and ai_result.decision.value in ["ignore", "standard_response"]:
        confidence += 0.05
    
    # Clamp to valid range
    confidence = max(0.0, min(1.0, confidence))
    
    return round(confidence, 2)


def should_apply_confidence_fallback(confidence: float) -> bool:
    """
    If confidence is too low, we should escalate conservatively.
    Better to over-respond than under-respond when uncertain.
    """
    return confidence < config.LOW_CONFIDENCE_THRESHOLD