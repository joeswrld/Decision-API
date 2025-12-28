"""
Configuration and constants for the decision API.
Centralized for easy tuning without touching core logic.
"""

from typing import Set

# Rule engine keywords (case-insensitive matching)
LEGAL_KEYWORDS: Set[str] = {
    "lawsuit", "lawyer", "attorney", "legal action", "sue", "court",
    "litigation", "subpoena", "defamation", "breach of contract"
}

THREAT_KEYWORDS: Set[str] = {
    "cancel", "canceling", "cancelling", "unsubscribe", "refund",
    "switching to", "competitor", "leaving", "disappointed"
}

SPAM_INDICATORS: Set[str] = {
    "click here", "buy now", "limited offer", "act fast", "congratulations"
}

# Message length thresholds
MIN_MESSAGE_LENGTH = 10  # Characters (after strip)
SPAM_MAX_LENGTH = 20  # Very short messages are likely spam/noise

# Confidence thresholds
LOW_CONFIDENCE_THRESHOLD = 0.4
MEDIUM_CONFIDENCE_THRESHOLD = 0.7

# AI settings
AI_TEMPERATURE = 0.2  # Low temperature for deterministic output
AI_TIMEOUT_SECONDS = 10
AI_MAX_TOKENS = 500

# Priority mapping based on plan
PLAN_BASE_PRIORITY = {
    "free": "low",
    "pro": "medium",
    "enterprise": "high"
}