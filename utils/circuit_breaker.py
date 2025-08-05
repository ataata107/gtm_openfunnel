import asyncio
import time
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass
import logging

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit is open, requests fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5        # Number of failures before opening circuit
    recovery_timeout: float = 60.0    # Seconds to wait before trying again
    expected_exception: type = Exception  # Type of exception to count as failure
    success_threshold: int = 2        # Number of successes to close circuit

class CircuitBreaker:
    """
    Circuit breaker pattern implementation for API failure handling.
    
    States:
    - CLOSED: Normal operation, requests go through
    - OPEN: Circuit is open, requests fail fast
    - HALF_OPEN: Testing if service is back
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = time.time()
        
        print(f"🔌 Circuit Breaker '{name}' initialized")
    
    def _can_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful request"""
        self.failure_count = 0
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN and self.success_count >= self.config.success_threshold:
            self.state = CircuitState.CLOSED
            self.success_count = 0
            print(f"🔌 Circuit Breaker '{self.name}': CLOSED (recovered)")
    
    def _on_failure(self):
        """Handle failed request"""
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"🔌 Circuit Breaker '{self.name}': OPEN (too many failures)")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            print(f"🔌 Circuit Breaker '{self.name}': OPEN (still failing)")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from function
        """
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._can_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.failure_count = 0
                print(f"🔌 Circuit Breaker '{self.name}': HALF_OPEN (testing)")
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        # Execute the function
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold
            }
        }

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass

# Global circuit breakers for different APIs
serper_circuit_breaker = CircuitBreaker("serper_api", CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30.0,
    expected_exception=Exception
))

openai_circuit_breaker = CircuitBreaker("openai_api", CircuitBreakerConfig(
    failure_threshold=2,
    recovery_timeout=60.0,
    expected_exception=Exception
))

news_api_circuit_breaker = CircuitBreaker("news_api", CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=45.0,
    expected_exception=Exception
))

def get_circuit_breaker_status() -> dict:
    """Get status of all circuit breakers"""
    return {
        "serper": serper_circuit_breaker.get_status(),
        "openai": openai_circuit_breaker.get_status(),
        "news": news_api_circuit_breaker.get_status()
    } 