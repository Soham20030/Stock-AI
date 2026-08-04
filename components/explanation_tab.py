import streamlit as st
from rag.gdelt_fetcher import fetch_gdelt_news
from rag.retriever import retrieve_news_for_asset
from rag.sentiment import analyze_news_sentiment
from rag.explainer import generate_explanation
from components.helpers import render_signal_box
from components.sentiment_charts import render_sentiment_timeline_chart


@st.cache_data(ttl=600)
def get_cached_rag_explanation(company_name, active_model_name, forecast_delta, target_p):
    """
    Caches FAISS vector retrieval, FinBERT sentiment scoring, and RAG explanation reports
    for 10 minutes per stock, making UI interactions and button clicks instant (< 0.01s).
    """
    retrieved = retrieve_news_for_asset(company_name, top_k=5)
    sentiment_data = analyze_news_sentiment(retrieved)
    explanation_report = generate_explanation(
        forecast_delta_pct=forecast_delta,
        target_price=target_p,
        sentiment_info=sentiment_data,
        company_name=company_name,
        model_name=active_model_name
    )
    return retrieved, sentiment_data, explanation_report


def render_explanation_tab(selected_stock, summary, raw_df):
    """
    Renders Tab 6: RAG Explainability, alignment confidence scores,
    narrative explanations, market signals grid, sentiment timeline, and retrieved articles.

    Parameters:
        selected_stock (str): Selected asset identifier (e.g. 'AAPL.csv').
        summary (dict): Stock summary fundamentals.
        raw_df (DataFrame): Historical price dataframe.
    """
    with st.container(border=True):
        st.markdown(f'<div class="vesper-title">🧠 RAG Explainability & Market Information Environment — {summary["company_name"]}</div>', unsafe_allow_html=True)
        
        # Determine active quantitative model prediction parameters
        active_model_name = "Prophet"
        forecast_delta = 5.2  # default placeholder return
        target_p = summary["current_price"] * 1.052

        if st.session_state.get("current_forecast") is not None:
            active_model_name = st.session_state["current_forecast"]["model"]
            fc_df = st.session_state["current_forecast"]["df"]
            pred_m = fc_df["type"] == "Forecast"
            if pred_m.any():
                target_p = float(fc_df.loc[pred_m, "Price"].iloc[-1])
                forecast_delta = ((target_p - summary["current_price"]) / summary["current_price"]) * 100

        with st.spinner(f"Loading RAG Vector Search & FinBERT Sentiment Analysis for {selected_stock}..."):
            # FAST CACHED RAG EXPLANATION LOADER (< 0.01s during reruns and button clicks)
            retrieved_articles, sentiment_analysis, explanation_report = get_cached_rag_explanation(
                company_name=selected_stock,
                active_model_name=active_model_name,
                forecast_delta=forecast_delta,
                target_p=target_p
            )

        # ---------------------------------------------------------------------
        # 1. SUMMARY METRICS ROW (FORECAST + CONFIDENCE + SENTIMENT)
        # ---------------------------------------------------------------------
        rc1, rc2, rc3 = st.columns(3)
        
        with rc1:
            st.metric(
                label=f"3M Quantitative Forecast ({active_model_name})",
                value=f"{forecast_delta:+.2f}%",
                delta=f"${target_p:.2f} Target Price"
            )

        with rc2:
            conf_val = explanation_report["confidence_pct"]
            st.metric(
                label="RAG Alignment Confidence",
                value=f"{conf_val}%",
                delta=f"{explanation_report['overall_sentiment_label'].capitalize()} Sentiment",
                help="Reflects alignment between quantitative trend and current news sentiment environment."
            )

        with rc3:
            s_score = explanation_report["overall_sentiment_score"]
            s_label = explanation_report["overall_sentiment_label"].upper()
            st.metric(
                label="Overall News Sentiment Score",
                value=f"{s_score:+.2f}",
                delta=f"{s_label} Context"
            )

        st.caption(f"💡 **Alignment Reason**: {explanation_report['confidence_reason']}")
        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 2. NATURAL LANGUAGE EXPLANATION NARRATIVE CARD
        # ---------------------------------------------------------------------
        st.subheader("💬 Contextual Natural-Language Explanation")
        st.markdown(f"""
            <div class="narrative-box">
                "{explanation_report['narrative']}"
            </div>
        """, unsafe_allow_html=True)
        
        st.caption("⚠️ **Zero-Causation Rule**: News signals describe the surrounding information environment and do not alter the quantitative prediction.")
        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 3. MARKET SIGNALS GRID (POSITIVE vs NEGATIVE)
        # ---------------------------------------------------------------------
        sig_left, sig_right = st.columns(2)
        
        with sig_left:
            st.subheader("✓ Positive Market Signals")
            pos_sigs = explanation_report.get("positive_signals", [])
            if pos_sigs:
                for sig in pos_sigs:
                    render_signal_box(sig, "positive")
            else:
                st.write("No strong bullish drivers detected in recent news.")

        with sig_right:
            st.subheader("⚠ Negative Market Signals")
            neg_sigs = explanation_report.get("negative_signals", [])
            if neg_sigs:
                for sig in neg_sigs:
                    render_signal_box(sig, "negative")
            else:
                st.write("No major bearish headwinds detected in recent news.")

        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 4. SENTIMENT TIMELINE VISUALIZATION
        # ---------------------------------------------------------------------
        render_sentiment_timeline_chart(raw_df)

        st.markdown("<hr style='border-color: #232936;'>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 5. RETRIEVED ARTICLES (FAISS SEMANTIC SEARCH TOP-5 RANKING)
        # ---------------------------------------------------------------------
        st.subheader("📰 Top-5 Semantically Retrieved Articles (FAISS Vector Store)")
        
        articles_list = explanation_report.get("retrieved_articles", [])
        if articles_list:
            for idx, art in enumerate(articles_list[:5], 1):
                p_pos = art.get("positive", 0.33)
                p_neg = art.get("negative", 0.33)
                s_lbl = "Positive 🟢" if p_pos > p_neg else ("Negative 🔴" if p_neg > p_pos else "Neutral 🟡")
                
                st.markdown(f"""
                    <div class="news-item">
                        <div><strong>#{idx}. <a class="news-title" href="{art.get('url', '#')}" target="_blank">{art.get('headline', 'Headline')}</a></strong></div>
                        <div class="news-meta">
                            Source: <strong>{art.get('source', 'GDELT')}</strong> • Date: {art.get('date', 'Recent')} • 
                            FinBERT: <strong>{s_lbl}</strong> (Pos: {p_pos:.2f}, Neg: {p_neg:.2f})
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No news articles retrieved for this query.")
