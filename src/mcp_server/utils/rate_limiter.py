import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API protection"""
    
    def __init__(self):
        # Track requests per endpoint per minute
        self.request_history = defaultdict(lambda: deque(maxlen=100))
        
        # Default rate limits (requests per minute)
        self.default_limits = {
            "openai": 50,      # Conservative for testing
            "google_gemini": 50,
            "weather_api": 60,  # OpenWeatherMap allows 60/min free
            "nyc_open_data": 100,  # NYC Open Data is generous
            "rag_query": 100,   # Local operations
            "general": 200      # Overall system limit
        }
        
        # Custom limits can be set per endpoint
        self.custom_limits = {}
        
        # Blocked endpoints (temporarily disabled)
        self.blocked_endpoints = set()
        
        # Block duration in seconds
        self.block_duration = 300  # 5 minutes
    
    def set_custom_limit(self, endpoint: str, requests_per_minute: int):
        """Set custom rate limit for specific endpoint"""
        self.custom_limits[endpoint] = requests_per_minute
        logger.info(f"Set custom rate limit for {endpoint}: {requests_per_minute} requests/minute")
    
    def get_limit(self, endpoint: str) -> int:
        """Get rate limit for endpoint"""
        return self.custom_limits.get(endpoint, self.default_limits.get(endpoint, 100))
    
    def is_allowed(self, endpoint: str, user_id: Optional[str] = None) -> bool:
        """Check if request is allowed based on rate limits"""
        try:
            # Check if endpoint is blocked
            if endpoint in self.blocked_endpoints:
                logger.warning(f"Endpoint {endpoint} is currently blocked due to rate limit violations")
                return False
            
            current_time = time.time()
            limit = self.get_limit(endpoint)
            
            # Get request history for this endpoint
            history_key = f"{endpoint}_{user_id}" if user_id else endpoint
            requests = self.request_history[history_key]
            
            # Remove old requests (older than 1 minute)
            cutoff_time = current_time - 60
            while requests and requests[0] < cutoff_time:
                requests.popleft()
            
            # Check if we're under the limit
            if len(requests) < limit:
                # Add current request
                requests.append(current_time)
                return True
            else:
                logger.warning(f"Rate limit exceeded for {endpoint}: {len(requests)} requests in last minute (limit: {limit})")
                
                # Block endpoint temporarily if significantly over limit
                if len(requests) > limit * 2:
                    self.blocked_endpoints.add(endpoint)
                    logger.error(f"Endpoint {endpoint} blocked for {self.block_duration} seconds due to excessive rate limit violations")
                    
                    # Schedule unblocking
                    asyncio.create_task(self._unblock_endpoint(endpoint))
                
                return False
                
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open - allow request if rate limiter fails
            return True
    
    async def _unblock_endpoint(self, endpoint: str):
        """Unblock endpoint after block duration"""
        await asyncio.sleep(self.block_duration)
        self.blocked_endpoints.discard(endpoint)
        logger.info(f"Endpoint {endpoint} unblocked after rate limit cooldown")
    
    def get_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        current_time = time.time()
        cutoff_time = current_time - 60
        
        if endpoint:
            # Stats for specific endpoint
            history_key = endpoint
            requests = self.request_history[history_key]
            
            # Count recent requests
            recent_requests = sum(1 for req_time in requests if req_time > cutoff_time)
            limit = self.get_limit(endpoint)
            
            return {
                "endpoint": endpoint,
                "recent_requests": recent_requests,
                "limit": limit,
                "remaining": max(0, limit - recent_requests),
                "is_blocked": endpoint in self.blocked_endpoints,
                "block_remaining": self._get_block_remaining(endpoint) if endpoint in self.blocked_endpoints else 0
            }
        else:
            # Overall stats
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "endpoints": {},
                "blocked_endpoints": list(self.blocked_endpoints),
                "total_requests": sum(len(requests) for requests in self.request_history.values())
            }
            
            for endpoint in self.default_limits.keys():
                stats["endpoints"][endpoint] = self.get_stats(endpoint)
            
            return stats
    
    def _get_block_remaining(self, endpoint: str) -> int:
        """Get remaining block time for endpoint"""
        # This is a simplified version - in production you'd track block start times
        return self.block_duration
    
    def reset_limits(self, endpoint: Optional[str] = None):
        """Reset rate limits for endpoint or all endpoints"""
        if endpoint:
            self.request_history[endpoint].clear()
            self.blocked_endpoints.discard(endpoint)
            logger.info(f"Reset rate limits for {endpoint}")
        else:
            self.request_history.clear()
            self.blocked_endpoints.clear()
            logger.info("Reset all rate limits")
    
    def emergency_override(self, endpoint: str, allow: bool = True):
        """Emergency override for rate limits (use with caution)"""
        if allow:
            self.blocked_endpoints.discard(endpoint)
            logger.warning(f"Emergency override: {endpoint} rate limits disabled")
        else:
            self.blocked_endpoints.add(endpoint)
            logger.warning(f"Emergency override: {endpoint} blocked")

# Global rate limiter instance
rate_limiter = RateLimiter()

# Decorator for easy rate limiting
def rate_limited(endpoint: str, user_id: Optional[str] = None):
    """Decorator to apply rate limiting to functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not rate_limiter.is_allowed(endpoint, user_id):
                raise Exception(f"Rate limit exceeded for {endpoint}. Please wait before making another request.")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
