"""
Performance Report Generator Module.

Analyzes telemetry captured by PerformanceLogger and generates performance_report.md
with overall metrics, detailed component timings, function call analysis,
suspicious bottleneck warnings, Streamlit rerun traces, and recommendations.
"""

import os
from typing import List, Dict, Any
from performance.logger import logger_instance


def generate_performance_report(output_file: str = "performance_report.md") -> str:
    """
    Generates a comprehensive Markdown performance report based on profiling telemetry.
    """
    step_logs = logger_instance.step_logs
    func_stats = logger_instance.function_stats
    rerun_logs = logger_instance.rerun_logs

    total_runtime = logger_instance.get_total_runtime()
    peak_memory = logger_instance.get_peak_memory()

    # Calculate startup time if recorded, otherwise derive from initial steps
    startup_time = 0.0
    for log in step_logs:
        if "startup" in log["step"].lower() or "load" in log["step"].lower():
            startup_time += log["time"]
    if startup_time == 0.0 and step_logs:
        startup_time = round(step_logs[0]["time"], 2)

    lines = []
    lines.append("# Performance Report\n")

    # -------------------------------------------------------------------------
    # 1. OVERALL METRICS
    # -------------------------------------------------------------------------
    lines.append("## Overall\n")
    lines.append(f"- **Total startup time**: {startup_time:.2f} s")
    lines.append(f"- **Total runtime**: {total_runtime:.2f} s")
    lines.append(f"- **Peak memory usage**: {peak_memory:.2f} MB\n")
    lines.append("---\n")

    # -------------------------------------------------------------------------
    # 2. DETAILED TIMINGS TABLE
    # -------------------------------------------------------------------------
    lines.append("## Detailed Timings\n")
    lines.append("| Component | Time (s) | Memory (MB) |")
    lines.append("|---|---|---|")

    if step_logs:
        for log in step_logs:
            lines.append(f"| {log['step']} | {log['time']:.2f} | {log['memory_mb']:.2f} |")
    else:
        lines.append("| No component steps recorded | 0.00 | 0.00 |")

    lines.append("\n---\n")

    # -------------------------------------------------------------------------
    # 3. FUNCTION CALL ANALYSIS
    # -------------------------------------------------------------------------
    lines.append("# Function Call Analysis\n")
    lines.append("## Overall Function Call Table\n")
    lines.append("| Function | Calls | Avg Time (s) | Total Time (s) | Min Time (s) | Max Time (s) | Peak Memory (MB) |")
    lines.append("|---|---|---|---|---|---|---|")

    sorted_funcs = sorted(func_stats.items(), key=lambda x: x[1]["total_time"], reverse=True)
    if sorted_funcs:
        for fname, s in sorted_funcs:
            lines.append(
                f"| `{fname}` | {s['calls']} | {s['average_time']:.2f} | {s['total_time']:.2f} | "
                f"{s['min_time']:.2f} | {s['max_time']:.2f} | {s['memory_mb']:.2f} |"
            )
    else:
        lines.append("| N/A | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |")

    lines.append("\n### Most frequently called functions\n")
    lines.append("| Function | Calls |")
    lines.append("|---|---|")
    freq_sorted = sorted(func_stats.items(), key=lambda x: x[1]["calls"], reverse=True)
    if freq_sorted:
        for fname, s in freq_sorted[:5]:
            lines.append(f"| `{fname}` | {s['calls']} |")
    else:
        lines.append("| N/A | 0 |")

    lines.append("\n### Most expensive functions\n")
    lines.append("| Function | Calls | Total Time |")
    lines.append("|---|---|---|")
    if sorted_funcs:
        for fname, s in sorted_funcs[:5]:
            lines.append(f"| `{fname}` | {s['calls']} | {s['total_time']:.2f} s |")
    else:
        lines.append("| N/A | 0 | 0.00 s |")

    lines.append("\n---\n")

    # -------------------------------------------------------------------------
    # 4. SUSPICIOUS FUNCTIONS IDENTIFICATION
    # -------------------------------------------------------------------------
    lines.append("## Suspicious functions\n")
    suspicious_found = False

    for fname, s in func_stats.items():
        is_slow = s["average_time"] > 2.0 or s["max_time"] > 2.0
        is_frequent = s["calls"] > 10
        is_expensive = s["total_time"] > 20.0

        if is_slow or is_frequent or is_expensive:
            suspicious_found = True
            lines.append(f"### ⚠ `{fname}()`\n")
            lines.append(f"- **Called**: {s['calls']} times")
            lines.append(f"- **Average**: {s['average_time']:.2f} seconds")
            lines.append(f"- **Total**: {s['total_time']:.2f} seconds\n")

            possible_issues = []
            if is_frequent:
                possible_issues.append("The function may be rerunning unnecessarily because of Streamlit rerenders.")
            if is_slow or is_expensive:
                possible_issues.append("Execution time is high; operation or network responses may not be cached efficiently.")

            lines.append("**Possible issue:**")
            for issue in possible_issues:
                lines.append(f"- {issue}")
            lines.append("")

    if not suspicious_found:
        lines.append("No suspicious bottlenecks detected matching execution criteria.\n")

    lines.append("---\n")

    # -------------------------------------------------------------------------
    # 5. STREAMLIT RERUN ANALYSIS
    # -------------------------------------------------------------------------
    lines.append("# Streamlit Rerun Analysis\n")
    if rerun_logs:
        for rerun in rerun_logs:
            lines.append(f"### Action: {rerun['action']}\n")
            lines.append("**Functions rerun:**")
            for f_item in rerun.get("functions_rerun", []):
                lines.append(f"- `{f_item}`")
            lines.append(f"\n**Total rerun cost:** {rerun['total_rerun_cost']:.2f} seconds\n")
    else:
        lines.append("No user action rerun events logged during this session.\n")

    lines.append("---\n")

    # -------------------------------------------------------------------------
    # 6. SLOWEST COMPONENTS & RECOMMENDATIONS
    # -------------------------------------------------------------------------
    lines.append("## Slowest components\n")
    if sorted_funcs:
        for idx, (fname, s) in enumerate(sorted_funcs[:3], 1):
            lines.append(f"{idx}. `{fname}` — {s['total_time']:.2f} s")
    else:
        lines.append("1. None recorded\n")

    lines.append("\n---\n")
    lines.append("## Recommendations\n")
    lines.append("- **Cache Prophet/ARIMA/LSTM Models**: Persist trained model payloads in session state to avoid retraining on tab switches.")
    lines.append("- **Cache FinBERT Embeddings**: Avoid re-computing BERT vector embeddings on every stream rerun.")
    lines.append("- **Avoid Rebuilding FAISS Index**: Reuse existing FAISS vector indexes across user queries.")
    lines.append("- **Parallelize GDELT Article Scraping**: Use thread pools for concurrent HTTP requests when fetching market news.")
    lines.append("\n---\n")

    report_content = "\n".join(lines)

    # Save report to performance_report.md
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)
    except Exception:
        pass

    return report_content
