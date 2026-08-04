import os
import json
import requests
from datetime import datetime

# Default Ollama REST API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"

# Path to local cache directory and summary archive JSON
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "news_summaries.json")


class OllamaSummarizer:
    """
    Local LLM-based news summarization service using Ollama.
    Features persistent disk caching to prevent redundant LLM inference calls.
    """

    def __init__(self, model_name=DEFAULT_MODEL, cache_file=CACHE_FILE):
        """
        Initializes the Ollama Summarizer.

        Parameters:
            model_name (str): Local Ollama model ('llama3', 'mistral', 'gemma').
            cache_file (str): Filepath for JSON summary cache storage.
        """
        self.model_name = model_name
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        """
        Loads cached news summaries from disk if present.

        Returns:
            dict: Keyed by article URL.
        """
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading news summary cache: {e}")
                return {}
        return {}

    def _save_cache(self):
        """
        Saves active summary cache dictionary to cache/news_summaries.json.
        """
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving news summary cache: {e}")

    def generate_summary(self, title, article_text, article_url="#"):
        """
        Generates a 2-3 sentence financial summary for an article using Ollama.
        Checks cache first to prevent redundant execution.

        Parameters:
            title (str): Article headline.
            article_text (str): Full article body or context snippet.
            article_url (str): Article source URL (used as unique cache key).

        Returns:
            dict: {
                "title": str,
                "summary": str
            }
        """
        clean_url = article_url.strip() if article_url else title.strip()

        # 1. Check if summary already exists in cache
        if clean_url in self.cache:
            cached_data = self.cache[clean_url]
            return {
                "title": title,
                "summary": cached_data.get("summary", "")
            }

        # Combine headline and text for LLM context
        full_context = f"{title}. {article_text}".strip()
        if len(full_context) < 30:
            return {
                "title": title,
                "summary": f"{title} — Financial news update."
            }

        # 2. Build Ollama Prompt
        prompt = f"""Summarize this financial news article in 2-3 concise sentences.

Focus on:
1. What happened.
2. Why it matters.
3. Potential market impact.

Do not add opinions or speculation.

Article:
{full_context[:1500]}"""

        # 3. Call local Ollama API
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "max_tokens": 150
            }
        }

        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=8)
            if response.status_code == 200:
                data = response.json()
                llm_response = data.get("response", "").strip()
                if llm_response:
                    summary_text = llm_response
                else:
                    summary_text = self._fallback_extract_summary(title, article_text)
            else:
                summary_text = self._fallback_extract_summary(title, article_text)
        except Exception:
            # Fallback if Ollama service is not currently running locally
            summary_text = self._fallback_extract_summary(title, article_text)

        # 4. Save to cache
        self.cache[clean_url] = {
            "title": title,
            "summary": summary_text,
            "created_at": datetime.now().isoformat()
        }
        self._save_cache()

        return {
            "title": title,
            "summary": summary_text
        }

    def _fallback_extract_summary(self, title, text):
        """
        Creates a clean 2-sentence summary fallback when Ollama is offline.
        """
        if text and len(text) > 40:
            sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 15]
            if len(sentences) >= 2:
                return f"{sentences[0]}. {sentences[1]}."
            elif len(sentences) == 1:
                return f"{sentences[0]}."
        return f"{title}. Key financial developments indicate ongoing market attention for this asset."

    def summarize_articles(self, articles):
        """
        Processes a list of articles and generates summaries for each.

        Parameters:
            articles (list of dict): Article dicts with 'title', 'content', and 'url'.

        Returns:
            list of dict: Articles enriched with 'summary' field.
        """
        summarized_list = []
        for art in articles:
            t = art.get("title", "")
            c = art.get("content", art.get("title", ""))
            u = art.get("url", "#")

            res = self.generate_summary(title=t, article_text=c, article_url=u)
            
            art_copy = dict(art)
            art_copy["summary"] = res["summary"]
            summarized_list.append(art_copy)

        return summarized_list


def summarize_news_article(title, text, url="#"):
    """
    Convenience functional wrapper to generate a local LLM news summary.
    """
    summarizer = OllamaSummarizer()
    return summarizer.generate_summary(title=title, article_text=text, article_url=url)
