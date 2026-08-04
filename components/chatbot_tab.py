import streamlit as st
from components.explanation_tab import get_cached_rag_explanation
from components.news_tab import get_cached_market_news
from chatbot.chatbot import StockAIChatbot
from chatbot.memory import ChatbotMemory


def render_chat_bubble(role, content):
    """
    Renders custom Intercom-styled chat bubbles without tacky default icons.
    """
    if role == "user":
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: flex-end; margin-bottom: 12px;">
                <div class="chat-user-meta">You</div>
                <div class="chat-user-bubble">{content}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="margin-bottom: 16px;">
                <div class="chat-assistant-bubble">
                    <div class="chat-assistant-header">
                        <span class="chat-assistant-badge">ANALYST</span>
                        <span class="chat-assistant-sub">Context AI Assistant</span>
                    </div>
                    <div>{content}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_chatbot_tab(selected_stock, summary):
    """
    Renders Tab 7: AI Financial Analyst chat interface with clean Intercom-styled
    conversation bubbles and zero tacky default icons.
    """
    memory_mgr = ChatbotMemory()

    with st.container(border=True):
        st.markdown(f'<div class="intercom-title">AI Financial Analyst — Context Assistant ({summary["company_name"]})</div>', unsafe_allow_html=True)
        st.caption("Ask questions about forecasts, model error benchmarks (RMSE/MAPE), news summaries, or RAG explanations. Zero-hallucination context bounds enforced.")
        
        # ---------------------------------------------------------------------
        # 1. CONVERSATION HISTORY RENDERER (INTERCOM CUSTOM BUBBLES)
        # ---------------------------------------------------------------------
        history_list = memory_mgr.get_history()

        chat_container = st.container()
        with chat_container:
            if history_list:
                for msg in history_list:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    render_chat_bubble(role, content)
            else:
                st.info(f"Welcome! I am your AI Analyst for **{selected_stock}**. Ask me any question about model error scores, forecasts, news summaries, or market signals.")

        # ---------------------------------------------------------------------
        # 2. CHAT INPUT ENGINE & FAST CACHED EXECUTION
        # ---------------------------------------------------------------------
        user_input = st.chat_input(f"Ask a question about {selected_stock} or dashboard context...")
        
        # Handle prompt submission
        prompt_to_process = user_input

        if prompt_to_process:
            # Display user message immediately
            with chat_container:
                render_chat_bubble("user", prompt_to_process)

            with st.spinner(f"Analyst inspecting dashboard context for {selected_stock}..."):
                # Fast Cached Context Harvester (< 0.01s)
                retrieved_news, sentiment_data, explanation_payload = get_cached_rag_explanation(
                    company_name=selected_stock,
                    active_model_name="Prophet" if st.session_state.get("current_forecast") is None else st.session_state["current_forecast"]["model"],
                    forecast_delta=5.2 if st.session_state.get("current_forecast") is None else 0.0,
                    target_p=summary["current_price"]
                )
                summarized_news_items = get_cached_market_news(selected_stock, timeline_range="3 Months")

                # Query chatbot engine
                chatbot_engine = StockAIChatbot()
                ai_answer = chatbot_engine.ask(
                    user_question=prompt_to_process,
                    stock_name=selected_stock,
                    summary_info=summary,
                    all_forecasts=st.session_state.get("all_forecasts", {}),
                    model_history=st.session_state.get("model_history", {}),
                    sentiment_info=sentiment_data,
                    explanation_report=explanation_payload,
                    summarized_news=summarized_news_items
                )

            # Display AI response bubble
            with chat_container:
                render_chat_bubble("assistant", ai_answer)
                    
            st.rerun()

        # Clear Chat History Button
        if history_list:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Clear Chat History", type="secondary"):
                memory_mgr.clear_memory()
                st.rerun()
