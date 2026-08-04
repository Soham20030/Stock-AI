import streamlit as st


class ChatbotMemory:
    """
    Manages session-based conversation memory for the AI Analyst chatbot,
    supporting message tracking, context sliding windows, and prompt formatting.
    """

    def __init__(self, max_history=10):
        """
        Initializes conversation memory.

        Parameters:
            max_history (int): Maximum conversation turns (user + assistant pairs) to retain.
        """
        self.max_history = max_history

        # Initialize session state storage if not present
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

    def add_user_message(self, content):
        """
        Appends a user question to conversation history.

        Parameters:
            content (str): User query string.
        """
        if content and isinstance(content, str):
            st.session_state["chat_history"].append({
                "role": "user",
                "content": content.strip()
            })
            self._trim_history()

    def add_assistant_message(self, content):
        """
        Appends an AI assistant response to conversation history.

        Parameters:
            content (str): AI response string.
        """
        if content and isinstance(content, str):
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": content.strip()
            })
            self._trim_history()

    def get_history(self):
        """
        Returns the raw list of conversation message dictionaries.

        Returns:
            list of dict: List of {"role": str, "content": str} objects.
        """
        return st.session_state.get("chat_history", [])

    def format_history_string(self, last_n=6):
        """
        Formats recent conversation turns into a clean text string for prompt injection.

        Parameters:
            last_n (int): Number of recent messages to include.

        Returns:
            str: Formatted dialogue string.
        """
        history = self.get_history()
        if not history:
            return "No previous conversation history."

        recent_messages = history[-last_n:]
        formatted_lines = []

        for msg in recent_messages:
            role_label = "User" if msg["role"] == "user" else "AI Analyst"
            formatted_lines.append(f"{role_label}: {msg['content']}")

        return "\n".join(formatted_lines)

    def clear_memory(self):
        """
        Clears all active session conversation memory.
        """
        st.session_state["chat_history"] = []

    def _trim_history(self):
        """
        Private helper to enforce maximum conversation history bounds.
        """
        max_messages = self.max_history * 2  # 2 messages per turn (user + assistant)
        if len(st.session_state["chat_history"]) > max_messages:
            st.session_state["chat_history"] = st.session_state["chat_history"][-max_messages:]
