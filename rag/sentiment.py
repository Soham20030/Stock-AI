import numpy as np

# FinBERT HuggingFace model identifier
FINBERT_MODEL_NAME = "ProsusAI/finbert"

# Global cached analyzer instance
_GLOBAL_FINBERT_ANALYZER = None


from performance.profiler import profile_step


class FinBERTSentimentAnalyzer:
    """
    Executes domain-specific financial sentiment analysis using FinBERT
    (ProsusAI/finbert) to assign positive, negative, and neutral probability scores.
    """

    def __init__(self, model_name=FINBERT_MODEL_NAME):
        """
        Initializes the FinBERT tokenizer and sequence classification pipeline.

        Parameters:
            model_name (str): HuggingFace model path.
        """
        self.model_name = model_name
        self.pipeline = None
        self._init_model()

    def _init_model(self):
        """
        Private helper to load HuggingFace FinBERT pipeline lazily.
        """
        try:
            from transformers import pipeline
            print(f"Loading FinBERT sentiment model ({self.model_name})...")
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                return_all_scores=True
            )
            print("FinBERT model loaded successfully.")
        except Exception as e:
            print(f"FinBERT pipeline initialization warning ({e}). Falling back to Financial NLP lexicon engine.")
            self.pipeline = None

    @profile_step("Sentiment Analysis")
    def analyze_article(self, headline, content=""):
        """
        Analyzes a single news article and generates positive, negative, 
        and neutral probability scores.

        Parameters:
            headline (str): Article title.
            content (str): Optional article body text.

        Returns:
            dict: {
                "headline": str,
                "positive": float,
                "negative": float,
                "neutral": float
            }
        """
        text = f"{headline}. {content}".strip() if content else headline.strip()
        if not text:
            return {
                "headline": headline or "N/A",
                "positive": 0.33,
                "negative": 0.33,
                "neutral": 0.34
            }

        # 1. Primary: Use Transformer FinBERT Pipeline
        if self.pipeline is not None:
            try:
                # Truncate text to 512 tokens max for BERT
                truncated_text = text[:500]
                raw_outputs = self.pipeline(truncated_text)
                
                # Handle pipeline nested output list formats
                if isinstance(raw_outputs, list) and len(raw_outputs) > 0:
                    if isinstance(raw_outputs[0], list):
                        raw_outputs = raw_outputs[0]
                    
                    scores = {}
                    for item in raw_outputs:
                        if isinstance(item, dict) and "label" in item and "score" in item:
                            label = item["label"].lower()
                            scores[label] = round(float(item["score"]), 4)

                    return {
                        "headline": headline,
                        "positive": scores.get("positive", 0.0),
                        "negative": scores.get("negative", 0.0),
                        "neutral": scores.get("neutral", 0.0)
                    }
            except Exception as e:
                print(f"FinBERT inference execution note ({e}). Utilizing financial rule-based scoring.")

        # 2. Resilient Fallback: Domain-Specific Financial Sentiment Scoring
        return self._rule_based_financial_sentiment(headline, text)

    def _rule_based_financial_sentiment(self, headline, text):
        """
        Rule-based financial sentiment scoring engine based on market keywords.
        """
        text_lower = text.lower()

        positive_keywords = [
            "record revenue", "earnings beat", "surge", "surpass", "profit growth",
            "upgrade", "bullish", "rally", "outperform", "dividend increase",
            "strong demand", "expansion", "all-time high", "gain", "buy rating"
        ]
        
        negative_keywords = [
            "decline", "missed expectations", "plunge", "loss", "lawsuit",
            "downgrade", "bearish", "drop", "underperform", "margin squeeze",
            "regulatory scrutiny", "antitrust", "recall", "probe", "investigation",
            "sell rating", "slump", "bankruptcy", "debt default"
        ]

        pos_count = sum(1 for kw in positive_keywords if kw in text_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in text_lower)

        total_matches = pos_count + neg_count

        if total_matches == 0:
            pos_prob, neg_prob, neu_prob = 0.15, 0.15, 0.70
        else:
            pos_prob = round(0.1 + (pos_count / (total_matches + 1)) * 0.8, 4)
            neg_prob = round(0.1 + (neg_count / (total_matches + 1)) * 0.8, 4)
            neu_prob = round(max(0.0, 1.0 - (pos_prob + neg_prob)), 4)

        return {
            "headline": headline,
            "positive": pos_prob,
            "negative": neg_prob,
            "neutral": neu_prob
        }

    def analyze_corpus(self, articles):
        """
        Analyzes a corpus of retrieved news articles and computes per-article probabilities
        alongside overall aggregated sentiment score and label.

        Parameters:
            articles (list of dict): List of article dicts with 'title' and optional 'content'.

        Returns:
            dict: {
                "article_sentiments": list of article score dicts,
                "overall_sentiment_score": float (-1.0 to +1.0),
                "overall_sentiment_label": str ('positive', 'neutral', 'negative'),
                "avg_positive": float,
                "avg_negative": float,
                "avg_neutral": float
            }
        """
        if not articles:
            return {
                "article_sentiments": [],
                "overall_sentiment_score": 0.0,
                "overall_sentiment_label": "neutral",
                "avg_positive": 0.33,
                "avg_negative": 0.33,
                "avg_neutral": 0.34
            }

        per_article_results = []
        pos_scores = []
        neg_scores = []
        neu_scores = []

        for art in articles:
            title = art.get("title", "")
            content = art.get("content", "")
            
            res = self.analyze_article(headline=title, content=content)
            
            # Preserve original article metadata (date, url, source)
            res["date"] = art.get("date", "N/A")
            res["url"] = art.get("url", "#")
            res["source"] = art.get("source", "News")
            
            per_article_results.append(res)
            
            pos_scores.append(res["positive"])
            neg_scores.append(res["negative"])
            neu_scores.append(res["neutral"])

        # Calculate average probability distributions across retrieved corpus
        avg_pos = float(np.mean(pos_scores)) if pos_scores else 0.33
        avg_neg = float(np.mean(neg_scores)) if neg_scores else 0.33
        avg_neu = float(np.mean(neu_scores)) if neu_scores else 0.34

        # Continuous overall sentiment score: Range -1.0 (Negative) to +1.0 (Positive)
        overall_score = float(avg_pos - avg_neg)
        overall_score = round(max(-1.0, min(1.0, overall_score)), 4)

        # Categorical overall label
        if overall_score >= 0.15:
            overall_label = "positive"
        elif overall_score <= -0.15:
            overall_label = "negative"
        else:
            overall_label = "neutral"

        return {
            "article_sentiments": per_article_results,
            "overall_sentiment_score": overall_score,
            "overall_sentiment_label": overall_label,
            "avg_positive": round(avg_pos, 4),
            "avg_negative": round(avg_neg, 4),
            "avg_neutral": round(avg_neu, 4)
        }


def analyze_news_sentiment(articles):
    """
    Convenience functional wrapper to run FinBERT sentiment scoring on a list of articles.

    Parameters:
        articles (list of dict): Retrieved article records.

    Returns:
        dict: Aggregated sentiment scores, article breakdowns, and overall label.
    """
    global _GLOBAL_FINBERT_ANALYZER
    if _GLOBAL_FINBERT_ANALYZER is None:
        _GLOBAL_FINBERT_ANALYZER = FinBERTSentimentAnalyzer()
    return _GLOBAL_FINBERT_ANALYZER.analyze_corpus(articles)
