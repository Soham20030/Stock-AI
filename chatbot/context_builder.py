import os
import json
import streamlit as st


class DashboardContextBuilder:
    """
    Collects, structures, and serializes the complete live dashboard state
    (Stock info, forecasts, RMSE/MAE/MAPE metrics, FinBERT sentiment, GDELT/Ollama news, RAG explanations)
    into structured payloads and atomic category-tagged text chunks.
    """

    def collect_dashboard_context(
        self,
        stock_name,
        summary_info=None,
        all_forecasts=None,
        model_history=None,
        sentiment_info=None,
        explanation_report=None,
        summarized_news=None
    ):
        """
        Gathers active dashboard components into a unified context payload dictionary.

        Parameters:
            stock_name (str): Active asset ticker (e.g. 'AAPL.csv').
            summary_info (dict, optional): Stock fundamentals (current_price, high_52w, etc.).
            all_forecasts (dict, optional): Trained forecasting model payloads.
            model_history (dict, optional): RMSE, MAE, MAPE evaluation metrics dict.
            sentiment_info (dict, optional): FinBERT sentiment analysis results.
            explanation_report (dict, optional): RAG explanation report dict.
            summarized_news (list of dict, optional): Ollama summarized news articles.

        Returns:
            dict: Standardized dashboard context dictionary.
        """
        clean_stock = stock_name.replace(".csv", "").strip().upper() if stock_name else "Asset"

        # 1. Fundamentals & Price Action
        current_p = summary_info.get("current_price", 0.0) if summary_info else 0.0

        # 2. Quantitative Forecast Details
        forecast_str = "Pending Model Fit"
        target_p_str = "N/A"
        active_model = "Prophet"

        if all_forecasts and len(all_forecasts) > 0:
            active_model = list(all_forecasts.keys())[-1]
            latest_payload = all_forecasts[active_model]
            fc_df = latest_payload.get("df", None)
            if fc_df is not None and not fc_df.empty:
                pred_mask = fc_df["type"] == "Forecast"
                if pred_mask.any():
                    t_price = float(fc_df.loc[pred_mask, "Price"].iloc[-1])
                    delta_val = t_price - current_p
                    delta_pct = (delta_val / current_p * 100) if current_p > 0 else 0.0
                    forecast_str = f"{delta_pct:+.2f}%"
                    target_p_str = f"${t_price:.2f}"

        # 3. Model Benchmark Metrics (RMSE, MAE, MAPE)
        formatted_metrics = {}
        if model_history:
            for m_name, m_dict in model_history.items():
                formatted_metrics[m_name] = {
                    "rmse": round(m_dict.get("RMSE", 0.0), 2),
                    "mae": round(m_dict.get("MAE", 0.0), 2),
                    "mape": round(m_dict.get("MAPE", 0.0), 2)
                }

        # 4. Sentiment Analysis Breakdown
        sentiment_payload = {
            "overall_label": "neutral",
            "overall_score": 0.0,
            "positive": 0.33,
            "negative": 0.33,
            "neutral": 0.34
        }
        if sentiment_info:
            sentiment_payload = {
                "overall_label": sentiment_info.get("overall_sentiment_label", "neutral"),
                "overall_score": sentiment_info.get("overall_sentiment_score", 0.0),
                "positive": sentiment_info.get("avg_positive", 0.33),
                "negative": sentiment_info.get("avg_negative", 0.33),
                "neutral": sentiment_info.get("avg_neutral", 0.34)
            }

        # 5. RAG Alignment & Explanation
        confidence_str = "N/A"
        narrative_str = "No explanation generated yet."
        pos_signals = []
        neg_signals = []

        if explanation_report:
            confidence_str = f"{explanation_report.get('confidence_pct', 75)}%"
            narrative_str = explanation_report.get("narrative", "")
            pos_signals = explanation_report.get("positive_signals", [])
            neg_signals = explanation_report.get("negative_signals", [])

        # 6. News Headlines & Ollama Summaries
        formatted_news = []
        if summarized_news:
            for item in summarized_news[:6]:
                formatted_news.append({
                    "title": item.get("title", ""),
                    "summary": item.get("summary", item.get("title", "")),
                    "source": item.get("source", "News"),
                    "date": item.get("date", "")
                })

        return {
            "stock": clean_stock,
            "current_price": f"${current_p:.2f}" if current_p else "N/A",
            "active_model": active_model,
            "forecast": forecast_str,
            "target_price": target_p_str,
            "confidence": confidence_str,
            "metrics": formatted_metrics,
            "sentiment": sentiment_payload,
            "news": formatted_news,
            "explanation": narrative_str,
            "positive_signals": pos_signals,
            "negative_signals": neg_signals
        }

    def build_atomic_context_chunks(self, context_dict):
        """
        Converts the context dictionary into category-tagged atomic text chunks
        suitable for dense vector embedding and FAISS top-k semantic retrieval.

        Parameters:
            context_dict (dict): Dashboard context dictionary.

        Returns:
            list of dict: [{ "category": str, "text": str, "metadata": dict }]
        """
        chunks = []
        stock = context_dict.get("stock", "Asset")

        # Chunk 1: Forecast Overview
        chunks.append({
            "category": "FORECAST",
            "text": (
                f"[CATEGORY: FORECAST] Stock: {stock}. Active Model: {context_dict.get('active_model', 'Prophet')}. "
                f"Current Price: {context_dict.get('current_price', 'N/A')}. "
                f"3-Month Forecast Return: {context_dict.get('forecast', 'N/A')}. "
                f"Projected Target Price: {context_dict.get('target_price', 'N/A')}. "
                f"RAG Alignment Confidence Score: {context_dict.get('confidence', 'N/A')}."
            ),
            "metadata": {"type": "forecast", "stock": stock}
        })

        # Chunk 2: Model Performance & Error Metrics
        metrics_dict = context_dict.get("metrics", {})
        if metrics_dict:
            m_lines = []
            for m_name, m_val in metrics_dict.items():
                m_lines.append(
                    f"{m_name} Model Error Scores -> RMSE: {m_val.get('rmse')}, MAE: {m_val.get('mae')}, MAPE: {m_val.get('mape')}%."
                )
            metrics_str = " ".join(m_lines)
            chunks.append({
                "category": "METRICS",
                "text": f"[CATEGORY: METRICS] Model Accuracy Benchmarks for {stock}: {metrics_str}",
                "metadata": {"type": "metrics", "stock": stock}
            })

        # Chunk 3: Sentiment & AI Explanation Layer
        sentiment_info = context_dict.get("sentiment", {})
        pos_sigs = ", ".join(context_dict.get("positive_signals", []))
        neg_sigs = ", ".join(context_dict.get("negative_signals", []))
        
        chunks.append({
            "category": "SENTIMENT_EXPLANATION",
            "text": (
                f"[CATEGORY: SENTIMENT_EXPLANATION] Stock: {stock}. "
                f"Overall Market News Sentiment: {sentiment_info.get('overall_label', 'neutral').upper()} "
                f"(Score: {sentiment_info.get('overall_score', 0.0):+.2f}, Positive: {int(sentiment_info.get('positive', 0)*100)}%, Negative: {int(sentiment_info.get('negative', 0)*100)}%). "
                f"Positive Signals: {pos_sigs if pos_sigs else 'None'}. "
                f"Negative Signals: {neg_sigs if neg_sigs else 'None'}. "
                f"AI Explanation Narrative: {context_dict.get('explanation', '')}"
            ),
            "metadata": {"type": "sentiment", "stock": stock}
        })

        # Chunk 4: News Headlines & Ollama LLM Summaries
        news_list = context_dict.get("news", [])
        for idx, news_item in enumerate(news_list, 1):
            chunks.append({
                "category": "NEWS",
                "text": (
                    f"[CATEGORY: NEWS] Article #{idx} for {stock}: Title: '{news_item.get('title', '')}'. "
                    f"Ollama LLM Summary: {news_item.get('summary', '')}. "
                    f"Source: {news_item.get('source', '')}. Date: {news_item.get('date', '')}."
                ),
                "metadata": {"type": "news", "title": news_item.get("title", ""), "stock": stock}
            })

        return chunks


def get_dashboard_context_snapshot(
    stock_name,
    summary_info=None,
    all_forecasts=None,
    model_history=None,
    sentiment_info=None,
    explanation_report=None,
    summarized_news=None
):
    """
    Convenience functional wrapper to collect context dictionary and atomic chunks.
    """
    builder = DashboardContextBuilder()
    context_dict = builder.collect_dashboard_context(
        stock_name=stock_name,
        summary_info=summary_info,
        all_forecasts=all_forecasts,
        model_history=model_history,
        sentiment_info=sentiment_info,
        explanation_report=explanation_report,
        summarized_news=summarized_news
    )
    chunks = builder.build_atomic_context_chunks(context_dict)
    return context_dict, chunks
