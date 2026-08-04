import numpy as np


class ForecastExplainer:
    """
    Synthesizes quantitative model predictions with qualitative FinBERT news sentiment
    to compute alignment confidence scores, extract market signals, and generate
    contextual explanations.
    """

    def calculate_confidence_score(self, forecast_delta_pct, sentiment_score, model_name="Model"):
        """
        Computes an Alignment Confidence Score reflecting how strongly historical trend
        momentum aligns with current public news sentiment.

        IMPORTANT: Confidence does NOT change the prediction itself. It only reflects
        how aligned the quantitative trend is with the qualitative information environment.

        Parameters:
            forecast_delta_pct (float): Forecasted 3-month return percentage (e.g., +6.2%).
            sentiment_score (float): FinBERT overall sentiment score (-1.0 to +1.0).
            model_name (str): Name of the forecasting model.

        Returns:
            dict: {
                "confidence_pct": int (35% to 95%),
                "base_confidence": int,
                "sentiment_factor": float,
                "reason": str
            }
        """
        base_confidence = 75  # Baseline model historical confidence

        # Determine directional agreement between quantitative forecast and news sentiment
        forecast_direction = 1.0 if forecast_delta_pct >= 0 else -1.0
        
        # Alignment score: +1.0 if full agreement, -1.0 if full conflict
        alignment = forecast_direction * sentiment_score
        
        # Sentiment adjustment factor: Adds or subtracts up to +-20%
        sentiment_adjustment = alignment * 20.0
        
        # Final calculated confidence percentage bounded between 35% and 95%
        final_confidence = int(np.clip(base_confidence + sentiment_adjustment, 35, 95))

        # Generate human-readable reason
        if alignment > 0.3:
            reason = f"Strong agreement between {model_name} historical trend momentum and positive public news sentiment."
        elif alignment < -0.3:
            reason = f"Historical trend momentum shows growth, but conflicting negative news sentiment reduces alignment confidence."
        else:
            reason = f"Moderate alignment between quantitative trajectory and neutral market news sentiment."

        return {
            "confidence_pct": final_confidence,
            "base_confidence": base_confidence,
            "sentiment_factor": round(alignment, 2),
            "reason": reason
        }

    def extract_market_signals(self, article_sentiments):
        """
        Categorizes retrieved article headlines into Positive and Negative signals.

        Parameters:
            article_sentiments (list of dict): List of article sentiment breakdown dicts.

        Returns:
            dict: {
                "positive_signals": list of str,
                "negative_signals": list of str
            }
        """
        positive_signals = []
        negative_signals = []

        for item in article_sentiments:
            headline = item.get("headline", "").strip()
            pos_p = item.get("positive", 0.0)
            neg_p = item.get("negative", 0.0)

            if not headline:
                continue

            if pos_p > 0.5 and pos_p > neg_p:
                positive_signals.append(f"✓ {headline}")
            elif neg_p > 0.5 and neg_p > pos_p:
                negative_signals.append(f"⚠ {headline}")

        # Fallback signals if specific probability thresholds were neutral
        if not positive_signals and not negative_signals:
            for item in article_sentiments[:3]:
                headline = item.get("headline", "")
                if headline:
                    positive_signals.append(f"✓ Market coverage: {headline}")

        return {
            "positive_signals": positive_signals[:4],  # Top 4 positive
            "negative_signals": negative_signals[:4]   # Top 4 negative
        }

    def generate_explanation_narrative(self, forecast_delta_pct, sentiment_info, signals, company_name):
        """
        Generates a natural-language contextual narrative explaining the surrounding
        information environment.

        CRITICAL RULE: Never claim causation. Only describe contextual signals surrounding the forecast.
        """
        clean_name = company_name.replace(".csv", "").strip().upper()
        sentiment_label = sentiment_info.get("overall_sentiment_label", "neutral")
        sentiment_score = sentiment_info.get("overall_sentiment_score", 0.0)
        
        pos_cnt = len(signals.get("positive_signals", []))
        neg_cnt = len(signals.get("negative_signals", []))

        trend_text = "growth" if forecast_delta_pct >= 0 else "decline"

        if sentiment_label == "positive" and forecast_delta_pct >= 0:
            narrative = (
                f"The projected {forecast_delta_pct:+.1f}% {trend_text} for {clean_name} is supported by a strong "
                f"information environment featuring {pos_cnt} positive news signals and overall Bullish market sentiment "
                f"(score: {sentiment_score:+.2f})."
            )
        elif sentiment_label == "negative" and forecast_delta_pct >= 0:
            narrative = (
                f"The quantitative model forecasts a {forecast_delta_pct:+.1f}% {trend_text} based on historical momentum, "
                f"although the surrounding information environment presents {neg_cnt} negative contextual signals "
                f"(score: {sentiment_score:+.2f}) that indicate potential headwind uncertainty."
            )
        elif sentiment_label == "negative" and forecast_delta_pct < 0:
            narrative = (
                f"The projected {forecast_delta_pct:+.1f}% downward trajectory for {clean_name} aligns with a cautious "
                f"information environment marked by negative market coverage and regulatory/margin scrutiny "
                f"(score: {sentiment_score:+.2f})."
            )
        else:
            narrative = (
                f"The quantitative forecast ({forecast_delta_pct:+.1f}%) reflects baseline price action, "
                f"surrounded by a balanced news environment with mixed positive ({pos_cnt}) and negative ({neg_cnt}) contextual signals."
            )

        return narrative

    def build_explanation_report(self, forecast_delta_pct, target_price, sentiment_info, company_name, model_name="Prophet"):
        """
        Builds the complete structured explanation report payload for the UI dashboard.

        Parameters:
            forecast_delta_pct (float): 3-month forecast return %.
            target_price (float): 90-day target predicted price.
            sentiment_info (dict): FinBERT sentiment analysis results dict.
            company_name (str): Asset name (e.g. 'AAPL.csv').
            model_name (str): Name of the forecasting model.

        Returns:
            dict: Complete report payload for Tab 6 (🧠 AI Explanation).
        """
        article_sentiments = sentiment_info.get("article_sentiments", [])
        sentiment_score = sentiment_info.get("overall_sentiment_score", 0.0)

        # 1. Calculate Confidence Score
        confidence_data = self.calculate_confidence_score(
            forecast_delta_pct=forecast_delta_pct,
            sentiment_score=sentiment_score,
            model_name=model_name
        )

        # 2. Extract Positive & Negative Market Signals
        signals = self.extract_market_signals(article_sentiments)

        # 3. Generate Natural Language Narrative
        narrative = self.generate_explanation_narrative(
            forecast_delta_pct=forecast_delta_pct,
            sentiment_info=sentiment_info,
            signals=signals,
            company_name=company_name
        )

        return {
            "forecast_delta_pct": round(forecast_delta_pct, 2),
            "target_price": round(target_price, 2),
            "confidence_pct": confidence_data["confidence_pct"],
            "confidence_reason": confidence_data["reason"],
            "overall_sentiment_score": sentiment_score,
            "overall_sentiment_label": sentiment_info.get("overall_sentiment_label", "neutral"),
            "positive_signals": signals["positive_signals"],
            "negative_signals": signals["negative_signals"],
            "narrative": narrative,
            "retrieved_articles": article_sentiments
        }


def generate_explanation(forecast_delta_pct, target_price, sentiment_info, company_name, model_name="Prophet"):
    """
    Convenience functional wrapper to generate a full RAG explanation report.

    Parameters:
        forecast_delta_pct (float): Forecasted return %.
        target_price (float): 90-day target predicted price.
        sentiment_info (dict): FinBERT sentiment analysis output dict.
        company_name (str): Asset ticker name.
        model_name (str): Active model name.

    Returns:
        dict: Complete structured explanation payload for Tab 6.
    """
    explainer = ForecastExplainer()
    return explainer.build_explanation_report(
        forecast_delta_pct=forecast_delta_pct,
        target_price=target_price,
        sentiment_info=sentiment_info,
        company_name=company_name,
        model_name=model_name
    )
