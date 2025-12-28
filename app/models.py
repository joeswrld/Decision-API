"""
Pydantic models for strict request/response validation.
All enums are exhaustive - invalid values will fail fast.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from enum import Enum


class UserPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Channel(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    REVIEW = "review"
    SOCIAL = "social"


class Decision(str, Enum):
    IGNORE = "ignore"
    STANDARD_RESPONSE = "standard_response"
    PRIORITY_RESPONSE = "priority_response"
    IMMEDIATE_ESCALATION = "immediate_escalation"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionRequest(BaseModel):
    """Incoming customer message with context."""
    message: str = Field(..., min_length=1, max_length=5000)
    user_plan: Optional[UserPlan] = UserPlan.FREE
    channel: Optional[Channel] = Channel.EMAIL
    history: Optional[list[str]] = Field(default_factory=list, max_length=50)

    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Ensure message isn't just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()


class DecisionResponse(BaseModel):
    """Strict output schema - no deviation allowed."""
    decision: Decision
    priority: Priority
    churn_risk: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommended_action: str = Field(..., min_length=1, max_length=500)

    class Config:
        use_enum_values = True  # Return string values, not enum objects