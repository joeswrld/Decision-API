"""
Rule engine - runs BEFORE AI to catch critical cases.
These rules are non-negotiable business logic.
"""

from typing import Optional, Tuple
from models import DecisionRequest, Decision, Priority
import config
import re


class RuleResult:
    """Result from rule engine evaluation."""
    def __init__(
        self,
        decision: Optional[Decision] = None,
        priority: Optional[Priority] = None,
        confidence_boost: float = 0.0,
        reason: Optional[str] = None,
        is_terminal: bool = False
    ):
        self.decision = decision
        self.priority = priority
        self.confidence_boost = confidence_boost  # Add to final confidence
        self.reason = reason
        self.is_terminal = is_terminal  # If True, skip AI entirely


def check_legal_escalation(message: str) -> Optional[RuleResult]:
    """
    CRITICAL RULE: Legal keywords → immediate escalation.
    This protects the company and must run first.
    """
    message_lower = message.lower()
    
    for keyword in config.LEGAL_KEYWORDS:
        if keyword in message_lower:
            return RuleResult(
                decision=Decision.IMMEDIATE_ESCALATION,
                priority=Priority.CRITICAL,
                confidence_boost=0.3,
                reason=f"Legal keyword detected: '{keyword}'",
                is_terminal=True  # Skip AI, escalate now
            )
    return None


def check_spam_or_noise(message: str) -> Optional[RuleResult]:
    """
    Detect low-signal messages (spam, very short, promotional).
    Save processing costs by filtering these early.
    """
    message_clean = message.strip()
    
    # Too short to be meaningful
    if len(message_clean) < config.MIN_MESSAGE_LENGTH:
        return RuleResult(
            decision=Decision.IGNORE,
            priority=Priority.LOW,
            confidence_boost=0.2,
            reason="Message too short (likely noise)",
            is_terminal=True
        )
    
    # Spam indicators
    message_lower = message_clean.lower()
    for spam_word in config.SPAM_INDICATORS:
        if spam_word in message_lower:
            return RuleResult(
                decision=Decision.IGNORE,
                priority=Priority.LOW,
                confidence_boost=0.15,
                reason=f"Spam indicator detected: '{spam_word}'",
                is_terminal=True
            )
    
    return None


def check_enterprise_sentiment(request: DecisionRequest) -> Optional[RuleResult]:
    """
    Enterprise customers with negative signals get priority treatment.
    This is business logic: we can't afford to lose enterprise accounts.
    """
    if request.user_plan.value != "enterprise":
        return None
    
    message_lower = request.message.lower()
    
    # Check for churn/threat signals
    negative_signals = 0
    for keyword in config.THREAT_KEYWORDS:
        if keyword in message_lower:
            negative_signals += 1
    
    if negative_signals > 0:
        return RuleResult(
            decision=Decision.PRIORITY_RESPONSE,  # Minimum level for enterprise
            priority=Priority.HIGH,
            confidence_boost=0.2,
            reason=f"Enterprise customer with {negative_signals} negative signal(s)",
            is_terminal=False  # Let AI refine, but ensure minimum priority
        )
    
    return None


def check_history_patterns(request: DecisionRequest) -> Optional[RuleResult]:
    """
    If customer has history of issues, boost priority.
    Multiple complaints = higher risk.
    """
    if not request.history or len(request.history) == 0:
        return None
    
    # Simple heuristic: lots of history = engaged user (for better or worse)
    history_count = len(request.history)
    
    if history_count >= 5:
        return RuleResult(
            confidence_boost=0.15,
            reason=f"Customer has {history_count} previous interactions",
            is_terminal=False
        )
    elif history_count >= 3:
        return RuleResult(
            confidence_boost=0.1,
            reason=f"Customer has {history_count} previous interactions",
            is_terminal=False
        )
    
    return None


def apply_rules(request: DecisionRequest) -> Tuple[Optional[RuleResult], list[RuleResult]]:
    """
    Apply all rules in priority order.
    Returns: (terminal_result, all_results)
    
    Terminal result = stop processing, return this decision immediately.
    All results = used for confidence scoring even if not terminal.
    """
    results = []
    
    # Rule 1: Legal (highest priority, terminal)
    legal_result = check_legal_escalation(request.message)
    if legal_result:
        results.append(legal_result)
        if legal_result.is_terminal:
            return legal_result, results
    
    # Rule 2: Spam/noise (terminal if matched)
    spam_result = check_spam_or_noise(request.message)
    if spam_result:
        results.append(spam_result)
        if spam_result.is_terminal:
            return spam_result, results
    
    # Rule 3: Enterprise sentiment (sets minimum priority)
    enterprise_result = check_enterprise_sentiment(request)
    if enterprise_result:
        results.append(enterprise_result)
    
    # Rule 4: History patterns (boost confidence)
    history_result = check_history_patterns(request)
    if history_result:
        results.append(history_result)
    
    # No terminal rule matched - proceed to AI
    return None, results