import os
import json
import streamlit as st

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
CHAT_HISTORY_FILE = os.path.join(CACHE_DIR, "chat_history.json")


class ChatbotMemory:
    """
    Manages persistent session-based conversation memory for the AI Analyst chatbot,
    saving dialogue history to disk (cache/chat_history.json) so chat turns persist across page refreshes.
    """

    def __init__(self, max_history=10, history_file=CHAT_HISTORY_FILE):
        """
        Initializes conversation memory with persistent disk backing.

        Parameters:
            max_history (int): Maximum conversation turns (user + assistant pairs) to retain.
            history_file (str): Filepath for JSON chat history persistence.
        """
        self.max_history = max_history
        self.history_file = history_file

        # Initialize session state storage if not present
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = self._load_disk_history()

    def _load_disk_history(self):
        """
        Loads cached conversation history from disk if present.

        Returns:
            list: List of message dicts.
        """
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                print(f"Error loading chat history disk cache: {e}")
                return []
        return []

    def _save_disk_history(self):
        """
        Saves current chat history to cache/chat_history.json on disk.
        """
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(st.session_state["chat_history"], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chat history to disk cache: {e}")

    def add_user_message(self, content):
        """
        Appends a user question to conversation history and saves to disk.

        Parameters:
            content (str): User query string.
        """
        if content and isinstance(content, str):
            st.session_state["chat_history"].append({
                "role": "user",
                "content": content.strip()
            })
            self._trim_history()
            self._save_disk_history()

    def add_assistant_message(self, content):
        """
        Appends an AI assistant response to conversation history and saves to disk.

        Parameters:
            content (str): AI response string.
        """
        if content and isinstance(content, str):
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": content.strip()
            })
            self._trim_history()
            self._save_disk_history()

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
        Clears active session conversation memory and removes disk cache.
        """
        st.session_state["chat_history"] = []
        self._save_disk_history()

    def _trim_history(self):
        """
        Private helper to enforce maximum conversation history bounds.
        """
        max_messages = self.max_history * 2  # 2 messages per turn (user + assistant)
        if len(st.session_state["chat_history"]) > max_messages:
            st.session_state["chat_history"] = st.session_state["chat_history"][-max_messages:]
