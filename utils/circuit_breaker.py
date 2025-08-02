import asyncio
import time
from enum import Enum
from typing import Callable, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back

class CircuitBreaker:
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED
        
    def _can_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _record_failure(self):
        """Record a failure and potentially open the circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"🔴 Circuit breaker OPEN after {self.failure_count} failures")
    
    def _record_success(self):
        """Record a success and close the circuit"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        print(f"🟢 Circuit breaker CLOSED after success")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._can_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                print(f"🟡 Circuit breaker HALF_OPEN - testing service")
            else:
                raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record success
            self._record_success()
            return result
            
        except self.expected_exception as e:
            # Record failure
            self._record_failure()
            raise e

class APICircuitBreaker:
    """Circuit breaker specifically for API calls"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=Exception
        )
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute API call with circuit breaker and retry logic"""
        return await self.circuit_breaker.call(func, *args, **kwargs)

# Global circuit breakers for different services
serper_circuit_breaker = APICircuitBreaker("serper")
firecrawl_circuit_breaker = APICircuitBreaker("firecrawl")
openai_circuit_breaker = APICircuitBreaker("openai") 