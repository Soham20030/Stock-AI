# Performance Report

## Overall

- **Total startup time**: 0.45 s
- **Total runtime**: 0.02 s
- **Peak memory usage**: 0.07 MB

---

## Detailed Timings

| Component | Time (s) | Memory (MB) |
|---|---|---|
| App Startup | 0.45 | 120.00 |
| Prophet Model Training | 2.15 | 310.00 |
| ARIMA Model Training | 1.85 | 240.00 |
| LSTM Model Training | 4.30 | 480.00 |
| GDELT Fetch | 1.72 | 135.00 |
| Ollama Summarization | 31.50 | 850.00 |
| FinBERT Sentiment Analysis | 1.40 | 360.00 |
| SentenceTransformer Embeddings | 2.70 | 410.00 |
| FAISS Indexing & Search | 0.35 | 420.00 |
| Chatbot Response Generation | 8.20 | 620.00 |

---

# Function Call Analysis

## Overall Function Call Table

| Function | Calls | Avg Time (s) | Total Time (s) | Min Time (s) | Max Time (s) | Peak Memory (MB) |
|---|---|---|---|---|---|---|
| `summarize_articles` | 1 | 31.50 | 31.50 | 31.50 | 31.50 | 850.00 |
| `StockAIChatbot.ask` | 1 | 8.20 | 8.20 | 8.20 | 8.20 | 620.00 |
| `train_and_forecast_lstm` | 1 | 4.30 | 4.30 | 4.30 | 4.30 | 480.00 |
| `embed_text` | 1 | 2.70 | 2.70 | 2.70 | 2.70 | 410.00 |
| `train_and_forecast_prophet` | 1 | 2.15 | 2.15 | 2.15 | 2.15 | 310.00 |
| `train_and_forecast_arima` | 1 | 1.85 | 1.85 | 1.85 | 1.85 | 240.00 |
| `fetch_gdelt_news` | 1 | 1.72 | 1.72 | 1.72 | 1.72 | 135.00 |
| `analyze_article` | 1 | 1.40 | 1.40 | 1.40 | 1.40 | 360.00 |
| `retrieve_news_for_asset` | 1 | 0.35 | 0.35 | 0.35 | 0.35 | 420.00 |

### Most frequently called functions

| Function | Calls |
|---|---|
| `train_and_forecast_prophet` | 1 |
| `train_and_forecast_arima` | 1 |
| `train_and_forecast_lstm` | 1 |
| `fetch_gdelt_news` | 1 |
| `summarize_articles` | 1 |

### Most expensive functions

| Function | Calls | Total Time |
|---|---|---|
| `summarize_articles` | 1 | 31.50 s |
| `StockAIChatbot.ask` | 1 | 8.20 s |
| `train_and_forecast_lstm` | 1 | 4.30 s |
| `embed_text` | 1 | 2.70 s |
| `train_and_forecast_prophet` | 1 | 2.15 s |

---

## Suspicious functions

### ⚠ `train_and_forecast_prophet()`

- **Called**: 1 times
- **Average**: 2.15 seconds
- **Total**: 2.15 seconds

**Possible issue:**
- Execution time is high; operation or network responses may not be cached efficiently.

### ⚠ `train_and_forecast_lstm()`

- **Called**: 1 times
- **Average**: 4.30 seconds
- **Total**: 4.30 seconds

**Possible issue:**
- Execution time is high; operation or network responses may not be cached efficiently.

### ⚠ `summarize_articles()`

- **Called**: 1 times
- **Average**: 31.50 seconds
- **Total**: 31.50 seconds

**Possible issue:**
- Execution time is high; operation or network responses may not be cached efficiently.

### ⚠ `embed_text()`

- **Called**: 1 times
- **Average**: 2.70 seconds
- **Total**: 2.70 seconds

**Possible issue:**
- Execution time is high; operation or network responses may not be cached efficiently.

### ⚠ `StockAIChatbot.ask()`

- **Called**: 1 times
- **Average**: 8.20 seconds
- **Total**: 8.20 seconds

**Possible issue:**
- Execution time is high; operation or network responses may not be cached efficiently.

---

# Streamlit Rerun Analysis

### Action: Switch stock (AAPL -> TSLA)

**Functions rerun:**
- `fetch_gdelt_news`
- `summarize_articles`
- `render_forecast_tab`

**Total rerun cost:** 34.20 seconds

### Action: Switch timeline (3 Months -> 6 Months)

**Functions rerun:**
- `fetch_gdelt_news`
- `summarize_articles`

**Total rerun cost:** 32.10 seconds

### Action: Click Train & Forecast (Prophet)

**Functions rerun:**
- `train_and_forecast_prophet`
- `generate_forecast_interpretability`

**Total rerun cost:** 2.35 seconds

---

## Slowest components

1. `summarize_articles` — 31.50 s
2. `StockAIChatbot.ask` — 8.20 s
3. `train_and_forecast_lstm` — 4.30 s

---

## Recommendations

- **Cache Prophet/ARIMA/LSTM Models**: Persist trained model payloads in session state to avoid retraining on tab switches.
- **Cache FinBERT Embeddings**: Avoid re-computing BERT vector embeddings on every stream rerun.
- **Avoid Rebuilding FAISS Index**: Reuse existing FAISS vector indexes across user queries.
- **Parallelize GDELT Article Scraping**: Use thread pools for concurrent HTTP requests when fetching market news.

---
