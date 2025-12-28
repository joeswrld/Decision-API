"""
Rate limiting logic for API keys.
Tracks requests per minute, per day, and per month.
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from collections import defaultdict
import logging

from auth import APIKey, TIER_LIMITS

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter.
    
    In production, replace with:
    - Redis for distributed rate limiting
    - Sliding window algorithm for better accuracy
    - Background job to reset counters at midnight
    """
    
    def __init__(self):
        # Track requests per minute (key_hash -> {timestamp: count})
        self.minute_requests: Dict[str, Dict[datetime, int]] = defaultdict(dict)
        
        # Daily and monthly counters are in APIKey object
        # This class just validates against limits
    
    def _get_current_minute(self) -> datetime:
        """Get current minute (truncated to minute precision)."""
        now = datetime.utcnow()
        return now.replace(second=0, microsecond=0)
    
    def _cleanup_old_minute_data(self, key_hash: str):
        """Remove minute data older than 2 minutes (cleanup)."""
        if key_hash not in self.minute_requests:
            return
        
        current_minute = self._get_current_minute()
        cutoff = current_minute - timedelta(minutes=2)
        
        # Remove old entries
        self.minute_requests[key_hash] = {
            timestamp: count
            for timestamp, count in self.minute_requests[key_hash].items()
            if timestamp > cutoff
        }
    
    def check_rate_limit(self, api_key: APIKey) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if request is allowed under rate limits.
        
        Returns:
            (allowed, error_message, retry_after_seconds)
        """
        limits = TIER_LIMITS[api_key.tier]
        current_minute = self._get_current_minute()
        
        # Clean up old data
        self._cleanup_old_minute_data(api_key.key_hash)
        
        # Check per-minute limit
        minute_count = self.minute_requests[api_key.key_hash].get(current_minute, 0)
        if minute_count >= limits.requests_per_minute:
            return (
                False,
                f"Rate limit exceeded ({limits.requests_per_minute} requests/minute)",
                60  # Retry after 60 seconds
            )
        
        # Check daily limit
        if api_key.requests_today >= limits.requests_per_day:
            # Calculate seconds until midnight UTC
            now = datetime.utcnow()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            retry_after = int((midnight - now).total_seconds())
            
            return (
                False,
                f"Daily rate limit exceeded ({limits.requests_per_day} requests/day)",
                retry_after
            )
        
        # Check monthly limit
        if api_key.requests_this_month >= limits.requests_per_month:
            # Calculate seconds until next month
            now = datetime.utcnow()
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            retry_after = int((next_month - now).total_seconds())
            
            return (
                False,
                f"Monthly rate limit exceeded ({limits.requests_per_month} requests/month)",
                retry_after
            )
        
        # All checks passed - increment counter
        self.minute_requests[api_key.key_hash][current_minute] = minute_count + 1
        
        return (True, None, None)
    
    def get_rate_limit_headers(self, api_key: APIKey) -> Dict[str, str]:
        """
        Generate rate limit headers for response.
        Follows standard X-RateLimit-* header format.
        """
        limits = TIER_LIMITS[api_key.tier]
        current_minute = self._get_current_minute()
        
        # Get current minute usage
        minute_count = self.minute_requests[api_key.key_hash].get(current_minute, 0)
        
        # Calculate daily reset time (midnight UTC)
        now = datetime.utcnow()
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        reset_timestamp = int(midnight.timestamp())
        
        return {
            "X-RateLimit-Limit-Minute": str(limits.requests_per_minute),
            "X-RateLimit-Remaining-Minute": str(max(0, limits.requests_per_minute - minute_count)),
            "X-RateLimit-Limit-Day": str(limits.requests_per_day),
            "X-RateLimit-Remaining-Day": str(max(0, limits.requests_per_day - api_key.requests_today)),
            "X-RateLimit-Reset": str(reset_timestamp),
            "X-RateLimit-Tier": api_key.tier.value
        }


# Global rate limiter instance
rate_limiter = RateLimiter()