import streamlit as st
from datetime import datetime
from rag.gdelt_fetcher import fetch_gdelt_news
from rag.summarizer import OllamaSummarizer
from rag.sentiment import FinBERTSentimentAnalyzer
from components.helpers import render_news_card


from cache.cache_manager import (
    get_news_cache_path,
    get_summary_cache_path,
    get_explanation_cache_path,
    invalidate_cache
)


@st.cache_data(ttl=600, show_spinner=False)
def get_cached_market_news(company_name, timeline_range="3 Months"):
    """
    Retrieves GDELT news and Ollama summaries using cache-first disk & memory architecture.
    """
    raw_items = fetch_gdelt_news(
        company_name=company_name,
        max_records=25,
        timeline_range=timeline_range
    )
    summarizer = OllamaSummarizer()
    summarized = summarizer.summarize_articles(
        articles=raw_items,
        company_name=company_name,
        timeline_range=timeline_range
    )
    return summarized


@st.cache_resource
def get_finbert_analyzer():
    """
    Caches the heavy FinBERT Transformer model in RAM so it loads only ONCE per session.
    """
    return FinBERTSentimentAnalyzer()


from performance.profiler import profile_step


@profile_step("Market News Tab Rendering")
def render_news_tab(selected_stock, company_name):
    """
    Renders Tab 3: Market News timeline filters, Ollama LLM summaries,
    FinBERT sentiment badges, and executive news cards.
    """
    with st.container(border=True):
        st.markdown(f'<div class="intercom-title">Market News & LLM Summaries — {company_name}</div>', unsafe_allow_html=True)
        
        c_select, c_btn = st.columns([3.5, 1.2])
        
        with c_select:
            # Timeline Selector (3 Months, 6 Months, 1 Year)
            timeline_selection = st.selectbox(
                "News Horizon Range:",
                options=["3 Months", "6 Months", "1 Year"],
                index=0,
                key="market_news_timeline_selector",
                help="Filters GDELT financial news coverage within the selected historical date range."
            )
            
        with c_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Refresh News", key="btn_refresh_news_cache", help="Invalidates disk cache and refetches fresh GDELT news and summaries"):
                # Invalidate news cache
                invalidate_cache(get_news_cache_path(selected_stock, timeline_selection))
                # Invalidate summary cache
                invalidate_cache(get_summary_cache_path(selected_stock, timeline_selection))
                # Invalidate explanation cache
                invalidate_cache(get_explanation_cache_path(selected_stock, timeline_selection))
                # Clear Streamlit cache_data & session state
                st.cache_data.clear()
                if "news_cache" in st.session_state:
                    st.session_state["news_cache"].pop(f"{selected_stock}_{timeline_selection}", None)
                st.rerun()

    # SESSION STATE CACHE MANAGER: Prevents re-fetching GDELT when returning to Market News
    if "news_cache" not in st.session_state:
        st.session_state["news_cache"] = {}

    cache_key = f"{selected_stock}_{timeline_selection}"

    if cache_key in st.session_state["news_cache"]:
        summarized_news = st.session_state["news_cache"][cache_key]
        finbert_analyzer = get_finbert_analyzer()
    else:
        with st.spinner(f"Loading GDELT news and Ollama summaries ({timeline_selection})..."):
            summarized_news = get_cached_market_news(
                company_name=selected_stock,
                timeline_range=timeline_selection
            )
            finbert_analyzer = get_finbert_analyzer()
            st.session_state["news_cache"][cache_key] = summarized_news

    if summarized_news:
        st.markdown("<br>", unsafe_allow_html=True)
        for item in summarized_news[:6]:
                title_str = item.get("title", "Headline")
                summary_str = item.get("summary", "Summary pending.")
                source_str = item.get("source", "Financial News")
                date_str = item.get("date", datetime.now().strftime("%d %B %Y"))
                url_str = item.get("url", "#")

                # FinBERT Sentiment
                s_res = finbert_analyzer.analyze_article(headline=title_str, content=summary_str)
                pos_p = s_res.get("positive", 0.33)
                neg_p = s_res.get("negative", 0.33)

                if pos_p >= 0.5 and pos_p > neg_p:
                    s_badge = f'<span class="badge-positive">Positive ({int(pos_p*100)}%)</span>'
                    s_type = "positive"
                elif neg_p >= 0.5 and neg_p > pos_p:
                    s_badge = f'<span class="badge-negative">Negative ({int(neg_p*100)}%)</span>'
                    s_type = "negative"
                else:
                    s_badge = f'<span class="badge-neutral">Neutral ({int(s_res.get("neutral", 0.34)*100)}%)</span>'
                    s_type = "neutral"

                # Render Executive News Card
                render_news_card(
                    title=title_str,
                    summary=summary_str,
                    source=source_str,
                    date=date_str,
                    url=url_str,
                    sentiment_badge=s_badge,
                    sentiment_type=s_type
                )
        else:
            st.write("No recent news articles found for this ticker in the selected range.")
