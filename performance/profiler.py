"""
Performance Profiler Decorator Module.

Provides the @profile_step decorator to measure execution time, memory usage,
and function call statistics for any major component or function.
"""

import time
import functools
from typing import Callable, Any, Optional
from performance.logger import logger_instance, get_current_memory_mb


def profile_step(step_name: Optional[str] = None):
    """
    Decorator to profile execution time, start/end timestamps, memory usage,
    and call statistics of a target function or application component.

    Usage:
        @profile_step("GDELT Fetch")
        def fetch_news(...):
            ...

        @profile_step
        def train_prophet(...):
            ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # If profiling is disabled, execute immediately with zero overhead
            if not logger_instance.is_enabled():
                return func(*args, **kwargs)

            name = step_name or func.__name__
            func_identifier = func.__name__

            start_t = time.perf_counter()
            start_mem = get_current_memory_mb()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_t = time.perf_counter()
                end_mem = get_current_memory_mb()
                duration = end_t - start_t
                memory_consumed = max(0.0, end_mem - start_mem)
                peak_mem = logger_instance.get_peak_memory()

                # Record step timing and memory snapshot in logger
                logger_instance.record_step(
                    step_name=name,
                    duration=duration,
                    start_t=start_t,
                    end_t=end_t,
                    memory_mb=end_mem,
                    peak_memory_mb=peak_mem
                )

                # Update cumulative function stats & export to function_stats.json
                logger_instance.update_function_stats(
                    func_name=func_identifier,
                    duration=duration,
                    memory_mb=end_mem
                )

        return wrapper

    # Handle both @profile_step and @profile_step("Custom Name") syntax
    if callable(step_name):
        actual_func = step_name
        step_name = None
        return decorator(actual_func)

    return decorator
