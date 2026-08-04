"""
Explanation Cache Module.

Provides persistent caching for RAG alignment explanations, avoiding unnecessary
re-computation of confidence scores, market signals, and narratives during simple UI rerenders.
"""

from typing import Dict, Any, Optional
from cache.cache_manager import (
    get_explanation_cache_path,
    is_cache_fresh,
    load_cache,
    save_cache
)
from rag.explainer import generate_explanation


def get_cached_explanation(company_name: str, timeline_range: str = "3 Months") -> Optional[Dict[str, Any]]:
    """
    Checks persistent explanation cache (cache/explanations/{ticker}_{timeline}.json).
    Returns cached explanation dict if valid and fresh.
    """
    cache_path = get_explanation_cache_path(company_name, timeline_range)
    if is_cache_fresh(cache_path, timeline_range):
        cached_payload = load_cache(cache_path)
        if cached_payload and isinstance(cached_payload, dict) and "data" in cached_payload:
            print(f"--- Cache Hit: Loaded RAG Explanation for '{company_name}' ({timeline_range}) from disk ---")
            return cached_payload["data"]
    return None


def save_explanation_to_cache(company_name: str, timeline_range: str, explanation_data: Dict[str, Any]) -> None:
    """
    Persists RAG explanation payload to cache/explanations/{ticker}_{timeline}.json.
    """
    cache_path = get_explanation_cache_path(company_name, timeline_range)
    save_cache(cache_path, explanation_data)


def get_or_generate_explanation(
    company_name: str,
    timeline_range: str = "3 Months",
    forecast_delta_pct: float = 0.0,
    target_price: float = 0.0,
    sentiment_info: Optional[Dict[str, Any]] = None,
    model_name: str = "Prophet"
) -> Dict[str, Any]:
    """
    Loads explanation report from persistent cache if fresh.
    Otherwise generates new report via ForecastExplainer and caches to disk.
    """
    cached_report = get_cached_explanation(company_name, timeline_range)
    if cached_report is not None:
        return cached_report

    # Generate fresh explanation payload
    fresh_report = generate_explanation(
        forecast_delta_pct=forecast_delta_pct,
        target_price=target_price,
        sentiment_info=sentiment_info or {},
        company_name=company_name,
        model_name=model_name
    )

    # Save fresh report to disk cache
    save_explanation_to_cache(company_name, timeline_range, fresh_report)
    return fresh_report
