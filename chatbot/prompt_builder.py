import json


class AnalystPromptBuilder:
    """
    Constructs high-precision, zero-hallucination system prompts for local LLMs
    by combining analyst persona rules, retrieved dashboard context snippets,
    and recent session conversation history.
    """

    def format_context_block(self, retrieved_chunks):
        """
        Formats retrieved context chunks into a clean, numbered context section.

        Parameters:
            retrieved_chunks (list of dict): Retrieved context chunks from ChatbotContextRetriever.

        Returns:
            str: Formatted context string.
        """
        if not retrieved_chunks:
            return "No specific dashboard context available for this query."

        formatted_snippets = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            text = chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
            formatted_snippets.append(f"{idx}. {text}")

        return "\n".join(formatted_snippets)

    def build_final_prompt(self, user_question, retrieved_chunks, history_str=""):
        """
        Synthesizes the complete prompt payload for Ollama LLM execution.

        Parameters:
            user_question (str): Active user query.
            retrieved_chunks (list of dict): Top-k relevant context chunks.
            history_str (str): Formatted conversation history string.

        Returns:
            str: Full zero-hallucination prompt string.
        """
        context_block = self.format_context_block(retrieved_chunks)
        clean_history = history_str.strip() if history_str else "No previous history."

        prompt = f"""You are an expert Senior Financial Analyst assistant integrated into the Stock AI Dashboard.

CRITICAL INSTRUCTIONS & ANTI-HALLUCINATION RULES:
1. Answer the user's question using ONLY the provided Dashboard Context and Conversation History below.
2. Do NOT invent, assume, or pull in external market information outside the provided context.
3. Be concise, professional, clear, and quantitative when discussing metrics (RMSE, MAE, MAPE, %, $ targets).
4. If no model has been trained yet (target price is N/A or Pending Model Fit), state: "No forecasting model has been trained yet for this asset in this session. Please go to the 'Forecast Engine' tab and click 'Train & Forecast'."
5. If the user asks about a different company/ticker (e.g., Tesla when current asset is AAPL), clarify that the active workspace dataset is set to the current asset and instruct them to select the requested asset in the sidebar.
6. If the question is about general trivia/knowledge (e.g. geography, sports, history, non-dashboard topics) OR if the required information is NOT present in the context, respond strictly with:
   "I do not have enough context from the dashboard to answer that question."

CURRENT DASHBOARD CONTEXT:
{context_block}

RECENT CONVERSATION HISTORY:
{clean_history}

USER QUESTION:
{user_question}

FINANCIAL ANALYST RESPONSE:"""

        return prompt


def build_analyst_prompt(user_question, retrieved_chunks, history_str=""):
    """
    Convenience functional wrapper to build the analyst prompt.
    """
    builder = AnalystPromptBuilder()
    return builder.build_final_prompt(
        user_question=user_question,
        retrieved_chunks=retrieved_chunks,
        history_str=history_str
    )
