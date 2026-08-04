import streamlit as st
from datetime import datetime
from rag.gdelt_fetcher import fetch_gdelt_news
from rag.summarizer import OllamaSummarizer
from rag.sentiment import FinBERTSentimentAnalyzer
from components.helpers import render_news_card


@st.cache_data(ttl=600)
def get_cached_market_news(company_name, timeline_range="3 Months"):
    """
    Caches GDELT news fetching and Ollama summaries for 10 minutes per stock/timeline selection,
    eliminating redundant network wait times during tab reruns or button clicks.
    """
    raw_items = fetch_gdelt_news(
        company_name=company_name,
        max_records=25,
        timeline_range=timeline_range
    )
    summarizer = OllamaSummarizer()
    summarized = summarizer.summarize_articles(raw_items)
    return summarized


@st.cache_resource
def get_finbert_analyzer():
    """
    Caches the heavy FinBERT Transformer model in RAM so it loads only ONCE per session.
    """
    return FinBERTSentimentAnalyzer()


def render_news_tab(selected_stock, company_name):
    """
    Renders Tab 3: Market News timeline filters, Ollama LLM summaries,
    FinBERT sentiment badges, and executive news cards.
    """
    with st.container(border=True):
        st.markdown(f'<div class="intercom-title">Market News & LLM Summaries — {company_name}</div>', unsafe_allow_html=True)
        
        # Timeline Selector (3 Months, 6 Months, 1 Year)
        timeline_selection = st.selectbox(
            "News Horizon Range:",
            options=["3 Months", "6 Months", "1 Year"],
            index=0,
            key="market_news_timeline_selector",
            help="Filters GDELT financial news coverage within the selected historical date range."
        )

        with st.spinner(f"Loading GDELT news and Ollama summaries ({timeline_selection})..."):
            summarized_news = get_cached_market_news(
                company_name=selected_stock,
                timeline_range=timeline_selection
            )
            finbert_analyzer = get_finbert_analyzer()

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
                elif neg_p >= 0.5 and neg_p > pos_p:
                    s_badge = f'<span class="badge-negative">Negative ({int(neg_p*100)}%)</span>'
                else:
                    s_badge = f'<span class="badge-neutral">Neutral ({int(s_res.get("neutral", 0.34)*100)}%)</span>'

                # Render Executive News Card
                render_news_card(
                    title=title_str,
                    summary=summary_str,
                    source=source_str,
                    date=date_str,
                    url=url_str,
                    sentiment_badge=s_badge
                )
        else:
            st.write("No recent news articles found for this ticker in the selected range.")
