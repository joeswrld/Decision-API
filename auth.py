"""
API Key Authentication System
Manages API keys, user tiers, and authentication.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from enum import Enum
from pydantic import BaseModel


class Tier(str, Enum):
    """Subscription tiers with different rate limits."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class APIKey(BaseModel):
    """API key model with tier and usage tracking."""
    key_hash: str
    user_id: str
    tier: Tier
    created_at: datetime
    requests_today: int = 0
    requests_this_month: int = 0
    last_request_at: Optional[datetime] = None
    is_active: bool = True
    
    # Metadata
    name: Optional[str] = None  # e.g., "Production API", "Development"
    email: Optional[str] = None


class TierLimits(BaseModel):
    """Rate limits per tier."""
    requests_per_minute: int
    requests_per_day: int
    requests_per_month: int
    price_usd: float


# Tier configuration
TIER_LIMITS: Dict[Tier, TierLimits] = {
    Tier.FREE: TierLimits(
        requests_per_minute=10,
        requests_per_day=100,
        requests_per_month=1000,
        price_usd=0.0
    ),
    Tier.STARTER: TierLimits(
        requests_per_minute=60,
        requests_per_day=5000,
        requests_per_month=100000,
        price_usd=29.0
    ),
    Tier.PROFESSIONAL: TierLimits(
        requests_per_minute=300,
        requests_per_day=50000,
        requests_per_month=1000000,
        price_usd=99.0
    ),
    Tier.ENTERPRISE: TierLimits(
        requests_per_minute=1000,
        requests_per_day=500000,
        requests_per_month=10000000,
        price_usd=499.0
    )
}


def generate_api_key() -> str:
    """
    Generate a secure API key.
    Format: sk_live_<32_chars> or sk_test_<32_chars>
    """
    random_part = secrets.token_urlsafe(32)
    return f"sk_live_{random_part}"


def generate_test_api_key() -> str:
    """Generate a test/sandbox API key."""
    random_part = secrets.token_urlsafe(32)
    return f"sk_test_{random_part}"


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for secure storage.
    Never store raw keys in database.
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key_format(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key:
        return False
    
    # Must start with sk_live_ or sk_test_
    if not (api_key.startswith("sk_live_") or api_key.startswith("sk_test_")):
        return False
    
    # Must have the random part
    parts = api_key.split("_")
    if len(parts) != 3:
        return False
    
    # Random part should be long enough
    if len(parts[2]) < 32:
        return False
    
    return True


class APIKeyStore:
    """
    In-memory store for API keys.
    
    In production, replace with:
    - PostgreSQL/MySQL for persistent storage
    - Redis for fast lookups and rate limiting
    - Add indexes on key_hash for performance
    """
    
    def __init__(self):
        self.keys: Dict[str, APIKey] = {}
        self._initialize_demo_keys()
    
    def _initialize_demo_keys(self):
        """Create demo API keys for testing."""
        demo_keys = [
            ("sk_test_demo_free_key_12345678901234567890", "demo-free", Tier.FREE, "demo-free@example.com"),
            ("sk_test_demo_starter_key_1234567890123456", "demo-starter", Tier.STARTER, "demo-starter@example.com"),
            ("sk_test_demo_pro_key_123456789012345678", "demo-pro", Tier.PROFESSIONAL, "demo-pro@example.com"),
        ]
        
        for key, user_id, tier, email in demo_keys:
            key_hash = hash_api_key(key)
            self.keys[key_hash] = APIKey(
                key_hash=key_hash,
                user_id=user_id,
                tier=tier,
                created_at=datetime.utcnow(),
                email=email,
                name=f"Demo {tier.value.title()} Key"
            )
    
    def create_key(
        self,
        user_id: str,
        tier: Tier,
        email: Optional[str] = None,
        name: Optional[str] = None,
        is_test: bool = False
    ) -> str:
        """
        Create a new API key.
        Returns the raw key (only time it's visible to user).
        """
        # Generate key
        raw_key = generate_test_api_key() if is_test else generate_api_key()
        key_hash = hash_api_key(raw_key)
        
        # Store hashed version
        self.keys[key_hash] = APIKey(
            key_hash=key_hash,
            user_id=user_id,
            tier=tier,
            created_at=datetime.utcnow(),
            email=email,
            name=name
        )
        
        return raw_key  # Return only once
    
    def get_key(self, raw_key: str) -> Optional[APIKey]:
        """Retrieve API key by raw key value."""
        if not verify_api_key_format(raw_key):
            return None
        
        key_hash = hash_api_key(raw_key)
        return self.keys.get(key_hash)
    
    def get_key_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Retrieve API key by hash (for internal use)."""
        return self.keys.get(key_hash)
    
    def update_usage(self, key_hash: str):
        """Increment usage counters."""
        if key_hash in self.keys:
            key = self.keys[key_hash]
            key.requests_today += 1
            key.requests_this_month += 1
            key.last_request_at = datetime.utcnow()
    
    def reset_daily_counters(self):
        """Reset daily request counters (run via cron at midnight)."""
        for key in self.keys.values():
            key.requests_today = 0
    
    def reset_monthly_counters(self):
        """Reset monthly request counters (run via cron on 1st)."""
        for key in self.keys.values():
            key.requests_this_month = 0
    
    def deactivate_key(self, key_hash: str):
        """Deactivate an API key."""
        if key_hash in self.keys:
            self.keys[key_hash].is_active = False
    
    def list_keys_by_user(self, user_id: str) -> list[APIKey]:
        """Get all keys for a user."""
        return [k for k in self.keys.values() if k.user_id == user_id]


# Global key store instance
api_key_store = APIKeyStore()