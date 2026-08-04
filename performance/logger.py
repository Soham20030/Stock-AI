"""
Performance Logger Module.

Provides in-memory telemetry storage, memory tracking via psutil/tracemalloc,
function statistics aggregation, and JSON persistence for application profiling.
"""

import os
import json
import time
import tracemalloc
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional

# Track process memory using psutil
_PROCESS = psutil.Process(os.getpid())


def get_current_memory_mb() -> float:
    """
    Returns current RSS process memory in Megabytes (MB).
    """
    try:
        return _PROCESS.memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0


class PerformanceLogger:
    """
    In-memory singleton storage for performance profiling measurements.
    """
    _instance: Optional["PerformanceLogger"] = None

    def __new__(cls) -> "PerformanceLogger":
        if cls._instance is None:
            cls._instance = super(PerformanceLogger, cls).__new__(cls)
            cls._instance._init_storage()
        return cls._instance

    def _init_storage(self) -> None:
        self.enabled: bool = False
        self.start_time: float = time.perf_counter()
        self.step_logs: List[Dict[str, Any]] = []
        self.function_stats: Dict[str, Dict[str, Any]] = {}
        self.rerun_logs: List[Dict[str, Any]] = []
        self.session_events: List[Dict[str, Any]] = []
        
        # Start tracemalloc memory tracing
        if not tracemalloc.is_tracing():
            try:
                tracemalloc.start()
            except Exception:
                pass

    def enable_profiling(self) -> None:
        """Enables performance profiling trace collection."""
        self.enabled = True
        self.start_time = time.perf_counter()

    def disable_profiling(self) -> None:
        """Disables performance profiling trace collection."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Returns True if performance profiling is currently enabled."""
        return self.enabled

    def record_step(
        self,
        step_name: str,
        duration: float,
        start_t: float,
        end_t: float,
        memory_mb: float,
        peak_memory_mb: float
    ) -> None:
        """
        Records a completed execution step timing and memory snapshot.
        """
        if not self.enabled:
            return

        log_entry = {
            "step": step_name,
            "time": round(duration, 4),
            "start_time": round(start_t, 4),
            "end_time": round(end_t, 4),
            "memory_mb": round(memory_mb, 2),
            "peak_memory_mb": round(peak_memory_mb, 2)
        }
        self.step_logs.append(log_entry)

    def update_function_stats(
        self,
        func_name: str,
        duration: float,
        memory_mb: float
    ) -> None:
        """
        Updates cumulative statistics for a profiled function.
        """
        if not self.enabled:
            return

        if func_name not in self.function_stats:
            self.function_stats[func_name] = {
                "calls": 0,
                "total_time": 0.0,
                "average_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
                "memory_mb": round(memory_mb, 2)
            }

        stats = self.function_stats[func_name]
        stats["calls"] += 1
        stats["total_time"] = round(stats["total_time"] + duration, 4)
        stats["min_time"] = round(min(stats["min_time"], duration), 4)
        stats["max_time"] = round(max(stats["max_time"], duration), 4)
        stats["average_time"] = round(stats["total_time"] / stats["calls"], 4)
        stats["memory_mb"] = max(stats["memory_mb"], round(memory_mb, 2))

        # Save updated JSON stats to disk
        self.save_function_stats_json()

    def log_rerun_action(self, action_name: str, functions_rerun: List[str], total_rerun_cost: float) -> None:
        """
        Records a Streamlit user action rerun event.
        """
        if not self.enabled:
            return

        self.rerun_logs.append({
            "action": action_name,
            "functions_rerun": functions_rerun,
            "total_rerun_cost": round(total_rerun_cost, 4)
        })

    def record_session_action(
        self,
        action: str,
        from_val: Any = None,
        to_val: Any = None,
        widget_id: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Records a user session interaction event and saves to performance/session_log.json.
        """
        if not self.enabled:
            return

        timestamp_str = datetime.now().isoformat()
        entry = {
            "action": action,
            "from": from_val,
            "to": to_val,
            "timestamp": timestamp_str,
            "widget": widget_id,
            "functions": functions or []
        }
        self.session_events.append(entry)
        self.save_session_log_json()

    def save_session_log_json(self, filepath: str = "performance/session_log.json") -> None:
        """
        Persists recorded session interaction events to performance/session_log.json.
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.session_events, f, indent=4)
        except Exception:
            pass

    def save_function_stats_json(self, filepath: str = "performance/function_stats.json") -> None:
        """
        Persists current function statistics to performance/function_stats.json.
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.function_stats, f, indent=4)
        except Exception:
            pass

    def get_peak_memory(self) -> float:
        """
        Returns peak memory allocated during profiling.
        """
        try:
            if tracemalloc.is_tracing():
                _, peak = tracemalloc.get_traced_memory()
                return round(peak / (1024 * 1024), 2)
        except Exception:
            pass
        return round(get_current_memory_mb(), 2)

    def get_total_runtime(self) -> float:
        """
        Returns total runtime since profiling started.
        """
        return round(time.perf_counter() - self.start_time, 4)

    def clear(self) -> None:
        """Resets all collected logs."""
        self.step_logs.clear()
        self.function_stats.clear()
        self.rerun_logs.clear()
        self.start_time = time.perf_counter()


# Singleton Instance
logger_instance = PerformanceLogger()
