import streamlit as st
from components.explanation_tab import get_cached_rag_explanation
from components.news_tab import get_cached_market_news
from chatbot.chatbot import StockAIChatbot
from chatbot.memory import ChatbotMemory


def render_chatbot_tab(selected_stock, summary):
    """
    Renders Tab 7: AI Financial Analyst chat interface, quick-ask pill buttons,
    conversation history bubbles, and chat input field.
    """
    memory_mgr = ChatbotMemory()

    with st.container(border=True):
        st.markdown(f'<div class="intercom-title">AI Financial Analyst — Context Assistant ({summary["company_name"]})</div>', unsafe_allow_html=True)
        st.caption("Ask questions about forecasts, model error benchmarks (RMSE/MAPE), news summaries, or RAG explanations. Zero-hallucination context bounds enforced.")
        
        # ---------------------------------------------------------------------
        # 1. QUICK-ASK SUGGESTED QUESTION BUTTONS
        # ---------------------------------------------------------------------
        st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #8f9bba; margin-bottom: 8px;'>Suggested Inquiries</div>", unsafe_allow_html=True)
        q_btn1, q_btn2, q_btn3, q_btn4 = st.columns(4)
        
        selected_quick_q = None
        with q_btn1:
            if st.button("Why is confidence low?"):
                selected_quick_q = f"Why is the RAG alignment confidence score for {selected_stock} at its current level?"
        with q_btn2:
            if st.button("Explain today's forecast"):
                selected_quick_q = f"Explain the active 3-month forecast and projected price target for {selected_stock}."
        with q_btn3:
            if st.button("Compare Prophet & LSTM"):
                selected_quick_q = f"Compare the accuracy error metrics (RMSE, MAE, MAPE) between Prophet, ARIMA, and LSTM for {selected_stock}."
        with q_btn4:
            if st.button("Summarize latest news"):
                selected_quick_q = f"Summarize the major news events and market drivers for {selected_stock}."

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 2. CONVERSATION HISTORY RENDERER
        # ---------------------------------------------------------------------
        history_list = memory_mgr.get_history()

        chat_container = st.container()
        with chat_container:
            if history_list:
                for msg in history_list:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        with st.chat_message("user"):
                            st.write(content)
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(content)
            else:
                st.info(f"Welcome! I am your AI Analyst for **{selected_stock}**. Ask me any question about model error scores, forecasts, news summaries, or market signals.")

        # ---------------------------------------------------------------------
        # 3. CHAT INPUT ENGINE & FAST CACHED EXECUTION
        # ---------------------------------------------------------------------
        user_input = st.chat_input(f"Ask a question about {selected_stock} or dashboard context...")
        
        # Handle prompt submission (via input box or quick-ask button)
        prompt_to_process = selected_quick_q or user_input

        if prompt_to_process:
            # Display user message immediately
            with chat_container:
                with st.chat_message("user"):
                    st.write(prompt_to_process)

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
                with st.chat_message("assistant"):
                    st.markdown(ai_answer)
                    
            st.rerun()

        # Clear Chat History Button
        if history_list:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Clear Chat History", type="secondary"):
                memory_mgr.clear_memory()
                st.rerun()
