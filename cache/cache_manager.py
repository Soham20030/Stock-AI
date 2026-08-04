"""
Cache Manager Module.

Provides persistent multi-tiered disk caching utilities, TTL freshness validation,
and cache invalidation for GDELT news, Ollama summaries, and RAG explanations.
"""

import os
import json
import time
import hashlib
from typing import Any, Optional, Dict

# Base cache directory path relative to project root
CACHE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
NEWS_CACHE_DIR = os.path.join(CACHE_BASE_DIR, "news")
SUMMARIES_CACHE_DIR = os.path.join(CACHE_BASE_DIR, "summaries")
EXPLANATIONS_CACHE_DIR = os.path.join(CACHE_BASE_DIR, "explanations")

# Freshness Rules (TTL in seconds)
# - 3 Months -> refresh every 24 hours (86,400s)
# - 6 Months -> refresh every 24 hours (86,400s)
# - 1 Year -> refresh every 48 hours (172,800s)
TTL_RULES = {
    "3 Months": 86400,
    "6 Months": 86400,
    "1 Year": 172800
}
DEFAULT_TTL = 86400


def ensure_cache_directories() -> None:
    """
    Creates necessary cache subdirectories automatically if they do not exist.
    """
    for dir_path in [NEWS_CACHE_DIR, SUMMARIES_CACHE_DIR, EXPLANATIONS_CACHE_DIR]:
        os.makedirs(dir_path, exist_ok=True)


def format_cache_key(ticker: str, timeline: str) -> str:
    """
    Generates a clean cache key filename from asset ticker and timeline selection.
    Example: 'AAPL_3months.json'
    """
    clean_ticker = ticker.replace(".csv", "").strip().upper()
    clean_timeline = timeline.lower().replace(" ", "")
    return f"{clean_ticker}_{clean_timeline}.json"


def get_news_cache_path(ticker: str, timeline: str) -> str:
    """Returns absolute file path for news cache."""
    ensure_cache_directories()
    return os.path.join(NEWS_CACHE_DIR, format_cache_key(ticker, timeline))


def get_summary_cache_path(ticker: str, timeline: str) -> str:
    """Returns absolute file path for summary cache."""
    ensure_cache_directories()
    return os.path.join(SUMMARIES_CACHE_DIR, format_cache_key(ticker, timeline))


def get_explanation_cache_path(ticker: str, timeline: str) -> str:
    """Returns absolute file path for explanation cache."""
    ensure_cache_directories()
    return os.path.join(EXPLANATIONS_CACHE_DIR, format_cache_key(ticker, timeline))


def get_article_hash(url: str) -> str:
    """Generates a unique SHA-256 hash string for an article URL."""
    clean_url = url.strip().lower()
    return hashlib.sha256(clean_url.encode("utf-8")).hexdigest()


def load_cache(filepath: str) -> Optional[Any]:
    """
    Loads JSON cache payload from disk if present and readable.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_cache(filepath: str, data: Any) -> None:
    """
    Saves JSON payload to disk, injecting timestamp for TTL freshness tracking.
    """
    ensure_cache_directories()
    payload = {
        "cached_at": time.time(),
        "data": data
    }
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def is_cache_fresh(filepath: str, timeline: str) -> bool:
    """
    Validates whether a cache file exists and its age is within the TTL freshness threshold.
    """
    if not os.path.exists(filepath):
        return False

    raw_cache = load_cache(filepath)
    if not raw_cache or not isinstance(raw_cache, dict):
        return False

    cached_at = raw_cache.get("cached_at", 0)
    max_age = TTL_RULES.get(timeline, DEFAULT_TTL)
    age = time.time() - cached_at

    return age < max_age


def invalidate_cache(filepath: str) -> None:
    """
    Deletes a specific cache file from disk.
    """
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass
