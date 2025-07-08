# app/infrastructure/external/circuit_breaker.py
import time
import logging
from typing import Optional, Callable, Any
from functools import wraps
import redis

logger = logging.getLogger(__name__)

class CircuitBreakerError(Exception):
    """Exception raised when circuit is open"""
    pass

class CircuitBreaker:
    """
    Redis-backed circuit breaker implementation with:
    - Failure threshold tracking
    - Automatic reset after timeout
    - State persistence
    - Decorator support
    """

    def __init__(
        self,
        redis_client: redis.Redis,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        namespace: str = "circuit_breaker"
    ):
        """
        Initialize circuit breaker
        
        Args:
            redis_client: Connected Redis client
            failure_threshold: Number of failures before opening circuit
            reset_timeout: Time in seconds before attempting to close circuit
            namespace: Prefix for Redis keys
        """
        self.redis = redis_client
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.namespace = namespace

    def _get_state_key(self, service_name: str) -> str:
        """Generate Redis key for service state"""
        return f"{self.namespace}:{service_name}"

    def record_failure(self, service_name: str) -> None:
        """
        Record a failed service call
        
        Args:
            service_name: Name of the service that failed
        """
        try:
            state_key = self._get_state_key(service_name)
            with self.redis.pipeline() as pipe:
                pipe.hincrby(state_key, "failures", 1)
                pipe.hset(state_key, "last_failure", time.time())
                pipe.expire(state_key, self.reset_timeout * 2)
                pipe.execute()
            logger.warning("Recorded failure for service: %s", service_name)
        except redis.RedisError as e:
            logger.error("Failed to record failure for %s: %s", service_name, str(e))
            raise

    def is_open(self, service_name: str) -> bool:
        """
        Check if circuit is open for service
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            bool: True if circuit is open, False otherwise
        """
        try:
            state_key = self._get_state_key(service_name)
            failures, last_failure = self.redis.hmget(
                state_key, ["failures", "last_failure"]
            )
            
            failures = int(failures or 0)
            last_failure = float(last_failure or 0)
            
            if failures >= self.failure_threshold:
                if (time.time() - last_failure) < self.reset_timeout:
                    logger.warning("Circuit OPEN for %s (%s failures)", service_name, failures)
                    return True
                # Reset circuit if timeout has passed
                self.reset(service_name)
            return False
        except redis.RedisError as e:
            logger.error("Error checking circuit state for %s: %s", service_name, str(e))
            # Fail open (assume service is unavailable)
            return True

    def reset(self, service_name: str) -> None:
        """
        Reset circuit for service
        
        Args:
            service_name: Name of the service to reset
        """
        try:
            state_key = self._get_state_key(service_name)
            self.redis.hset(state_key, "failures", 0)
            logger.info("Reset circuit for service: %s", service_name)
        except redis.RedisError as e:
            logger.error("Failed to reset circuit for %s: %s", service_name, str(e))
            raise

    def __call__(self, service_name: str) -> Callable:
        """
        Decorator factory for circuit breaker
        
        Args:
            service_name: Name of the service to protect
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if self.is_open(service_name):
                    raise CircuitBreakerError(f"Service {service_name} unavailable (circuit open)")
                
                try:
                    result = func(*args, **kwargs)
                    # Reset on success
                    self.reset(service_name)
                    return result
                except Exception as e:
                    self.record_failure(service_name)
                    raise
            return wrapper
        return decorator