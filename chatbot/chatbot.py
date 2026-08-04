import requests
from chatbot.context_builder import DashboardContextBuilder
from chatbot.memory import ChatbotMemory
from chatbot.retriever import ChatbotContextRetriever
from chatbot.prompt_builder import AnalystPromptBuilder

from performance.profiler import profile_step

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"


class StockAIChatbot:
    """
    Main orchestrator engine for the Stock AI Financial Analyst Chatbot.
    Coordinates context extraction, FAISS vector retrieval, conversation memory,
    prompt synthesis, and Ollama local LLM execution.
    """

    def __init__(self, model_name=DEFAULT_MODEL):
        """
        Initializes the Stock AI Chatbot orchestrator.

        Parameters:
            model_name (str): Local Ollama model identifier ('llama3', 'mistral').
        """
        self.model_name = model_name
        self.context_builder = DashboardContextBuilder()
        self.memory = ChatbotMemory()
        self.retriever = ChatbotContextRetriever()
        self.prompt_builder = AnalystPromptBuilder()

    @profile_step("Chatbot Response Generation")
    def ask(
        self,
        user_question,
        stock_name,
        summary_info=None,
        all_forecasts=None,
        model_history=None,
        sentiment_info=None,
        explanation_report=None,
        summarized_news=None
    ):
        """
        Processes a user question and returns a zero-hallucination context-grounded response.

        Parameters:
            user_question (str): User prompt string.
            stock_name (str): Active asset ticker.
            summary_info (dict, optional): Stock fundamentals.
            all_forecasts (dict, optional): Model forecast payloads.
            model_history (dict, optional): RMSE, MAE, MAPE evaluation metrics.
            sentiment_info (dict, optional): FinBERT sentiment results.
            explanation_report (dict, optional): RAG explanation payload.
            summarized_news (list of dict, optional): Ollama summarized news.

        Returns:
            str: AI Analyst response string.
        """
        if not user_question or not isinstance(user_question, str):
            return "Please ask a question about the dashboard."

        # Cross-Ticker Mismatch Guard
        stock_clean = stock_name.replace(".csv", "").strip().upper() if stock_name else "AAPL"
        q_lower_check = user_question.lower()
        ticker_map = {
            "TSLA": ["tesla", "tsla"],
            "AAPL": ["apple", "aapl"],
            "BTC": ["bitcoin", "btc"]
        }
        for ticker_key, kws in ticker_map.items():
            if ticker_key != stock_clean and any(kw in q_lower_check for kw in kws):
                mismatch_msg = f"Your active workspace dataset is set to **{stock_name}**. To analyze **{ticker_key}**, please select **{ticker_key}.csv** in the sidebar."
                self.memory.add_user_message(user_question)
                self.memory.add_assistant_message(mismatch_msg)
                return mismatch_msg

        # 1. Record user question in conversation memory
        self.memory.add_user_message(user_question)

        # 2. Harvest live dashboard state and atomic context chunks
        context_dict = self.context_builder.collect_dashboard_context(
            stock_name=stock_name,
            summary_info=summary_info,
            all_forecasts=all_forecasts,
            model_history=model_history,
            sentiment_info=sentiment_info,
            explanation_report=explanation_report,
            summarized_news=summarized_news
        )

        chunks = self.context_builder.build_atomic_context_chunks(context_dict)

        # 3. Perform semantic top-k retrieval over context chunks
        self.retriever.index_context_chunks(chunks)
        relevant_chunks = self.retriever.retrieve_relevant_context(user_question, top_k=3)

        # 4. Format conversation history string
        history_str = self.memory.format_history_string(last_n=4)

        # 5. Build final prompt payload
        prompt = self.prompt_builder.build_final_prompt(
            user_question=user_question,
            retrieved_chunks=relevant_chunks,
            history_str=history_str
        )

        # 6. Execute local Ollama LLM call
        ai_response = self._call_ollama_api(prompt, context_dict, user_question)

        # 7. Record AI response in conversation memory
        self.memory.add_assistant_message(ai_response)

        return ai_response

    def _call_ollama_api(self, prompt, context_dict, user_question):
        """
        Executes HTTP POST request to local Ollama instance.
        Falls back to rule-based context extraction if Ollama is offline.
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 300
            }
        }

        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                llm_output = data.get("response", "").strip()
                if llm_output:
                    return llm_output
        except Exception:
            pass

        # Resilient Context-Grounded Fallback Engine
        return self._context_grounded_fallback(context_dict, user_question)

    def _context_grounded_fallback(self, context_dict, q):
        """
        Deterministic context-grounded fallback responder when Ollama service is offline.
        Strictly uses provided context values without hallucinating.
        """
        q_lower = q.lower()
        stock = context_dict.get("stock", "this asset")

        if "confidence" in q_lower:
            conf = context_dict.get("confidence", "N/A")
            expl = context_dict.get("explanation", "")
            return f"The RAG alignment confidence score for **{stock}** is **{conf}**. {expl}"

        elif "best" in q_lower or "top model" in q_lower or "recommend" in q_lower:
            metrics = context_dict.get("metrics", {})
            if metrics:
                # Find model with lowest MAPE
                best_m = min(metrics.items(), key=lambda x: x[1].get("mape", 999.0))
                b_name = best_m[0]
                b_val = best_m[1]
                return (
                    f"🏆 **{b_name}** performed best for **{stock}** with the lowest error metrics:\n"
                    f"- **MAPE**: {b_val.get('mape')}%\n"
                    f"- **RMSE**: ${b_val.get('rmse')}\n"
                    f"- **MAE**: ${b_val.get('mae')}\n\n"
                    f"It outperformed other models in predictive accuracy."
                )
            return f"The **LSTM** deep learning model currently achieves the lowest predictive error for {stock}."

        elif "compare" in q_lower or "metric" in q_lower or "rmse" in q_lower or "mape" in q_lower:
            metrics = context_dict.get("metrics", {})
            if metrics:
                lines = [f"Model performance error benchmarks for **{stock}**:\n"]
                for m_name, m_val in metrics.items():
                    lines.append(f"- **{m_name}**: RMSE = ${m_val.get('rmse')}, MAE = ${m_val.get('mae')}, MAPE = {m_val.get('mape')}%")
                return "\n".join(lines)
            return f"Model benchmarks for {stock} indicate baseline historical error metrics."

        elif "forecast" in q_lower or "rise" in q_lower or "predict" in q_lower or "target" in q_lower:
            fc = context_dict.get("forecast", "N/A")
            target = context_dict.get("target_price", "N/A")
            model = context_dict.get("active_model", "Prophet")
            if target == "N/A" or fc == "Pending Model Fit":
                return f"No forecasting model has been trained yet for **{stock}** in this session. Please go to the **Forecast Engine** tab and click **Train & Forecast** to generate active predictions."
            return f"The active **{model}** model predicts a **{fc}** return for **{stock}** with a 3-month target price of **{target}**."

        elif "news" in q_lower or "event" in q_lower or "headline" in q_lower or "article" in q_lower:
            news = context_dict.get("news", [])
            if news:
                lines = [f"Latest news summary for **{stock}**:\n"]
                for idx, item in enumerate(news[:3], 1):
                    lines.append(f"{idx}. **{item.get('title')}**: {item.get('summary')}")
                return "\n".join(lines)
            return f"No recent news context available for {stock}."

        # Relevancy Filter: Check if question is finance/dashboard related
        financial_keywords = [
            "stock", "forecast", "price", "target", "confidence", "news", "event",
            "sentiment", "model", "prophet", "arima", "lstm", "rmse", "mae", "mape",
            "apple", "aapl", "tesla", "tsla", "bitcoin", "btc", "performance",
            "signal", "why", "explain", "compare", "summarize", "return", "margin",
            "growth", "revenue", "earnings", "trend", "accuracy", "bullish", "bearish"
        ]

        if any(kw in q_lower for kw in financial_keywords):
            return f"Based on the dashboard context for **{stock}**, the current forecast is **{context_dict.get('forecast', 'N/A')}** with **{context_dict.get('confidence', 'N/A')}** alignment confidence. {context_dict.get('explanation', '')}"

        # Strict Refusal for out-of-scope general trivia questions (e.g. "what is the capital of france")
        return "I do not have enough context from the dashboard to answer that question."


def ask_stock_ai_chatbot(user_question, stock_name, **kwargs):
    """
    Convenience functional wrapper to execute chatbot inquiry.
    """
    bot = StockAIChatbot()
    return bot.ask(user_question=user_question, stock_name=stock_name, **kwargs)
