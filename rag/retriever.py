import os
from rag.gdelt_fetcher import fetch_gdelt_news
from rag.embeddings import get_embedding_generator
from vector_db.index_manager import FAISSIndexManager


class SemanticRetriever:
    """
    Coordinates news fetching, dense vector embedding, FAISS indexing,
    and top-k semantic article retrieval for RAG-augmented market explainability.
    """

    def __init__(self):
        """
        Initializes the Semantic Retriever with shared embedding generator
        and FAISS index manager instances.
        """
        self.embedder = get_embedding_generator()
        self.index_manager = FAISSIndexManager(dim=self.embedder.dimension)

    def index_company_news(self, company_name, max_articles=25):
        """
        Ingests GDELT news for a company, encodes texts into dense vectors,
        builds a FAISS index, and persists binary files to disk.

        Parameters:
            company_name (str): Company ticker or title (e.g. 'AAPL').
            max_articles (int): Maximum news articles to fetch and index.

        Returns:
            int: Number of articles indexed.
        """
        print(f"--- RAG Pipeline: Ingesting & Indexing News for '{company_name}' ---")
        
        # 1. Fetch raw cleaned news records from GDELT
        articles = fetch_gdelt_news(company_name, max_records=max_articles)
        if not articles:
            print(f"No articles retrieved for {company_name}.")
            return 0

        # 2. Convert articles into 384-d dense embedding matrix
        embeddings_matrix, metadata_records = self.embedder.embed_articles(articles)
        if len(metadata_records) == 0:
            print("No valid embeddings generated.")
            return 0

        # 3. Build FAISS index and save to vector_db/
        total_indexed = self.index_manager.create_index(embeddings_matrix, metadata_records)
        self.index_manager.save_index()

        print(f"--- RAG Pipeline: Successfully indexed {total_indexed} articles for {company_name} ---")
        return total_indexed

    def retrieve_relevant_news(self, query_prompt, company_name=None, top_k=5):
        """
        Executes semantic vector search against the FAISS vector database
        to retrieve top-k articles relevant to a query.

        Parameters:
            query_prompt (str): Natural language search query (e.g. 'What affected Apple earnings?').
            company_name (str, optional): Target asset ticker to index if database is empty.
            top_k (int): Number of top semantically ranked articles to return (default 5).

        Returns:
            list of dict: Top-k semantically ranked article metadata records with similarity scores.
        """
        # Auto-index if vector index does not exist or is empty
        if self.index_manager.index is None or self.index_manager.index.ntotal == 0:
            loaded = self.index_manager.load_index()
            if not loaded and company_name:
                self.index_company_news(company_name, max_articles=25)

        if not query_prompt or not isinstance(query_prompt, str):
            query_prompt = f"Market earnings economic developments {company_name or ''}"

        # Convert query string into normalized 384-d query vector
        query_vector = self.embedder.embed_text(query_prompt)

        # Execute vector search in FAISS database
        results = self.index_manager.search(query_vector, top_k=top_k)
        
        print(f"Retrieved {len(results)} top semantically relevant articles for query: '{query_prompt[:40]}...'")
        return results


def retrieve_news_for_asset(company_name, query_prompt=None, top_k=5):
    """
    Convenience functional wrapper to execute full RAG retrieval for an asset ticker.

    Parameters:
        company_name (str): Company/asset ticker (e.g. 'AAPL', 'TSLA', 'BTC').
        query_prompt (str, optional): Custom prompt or default auto-generated asset query.
        top_k (int): Top articles to retrieve (default 5).

    Returns:
        list of dict: Top-k relevant article records.
    """
    retriever = SemanticRetriever()
    
    # Always ensure index is built for requested asset
    retriever.index_company_news(company_name, max_articles=25)
    
    if not query_prompt:
        clean_name = company_name.replace(".csv", "").upper()
        query_prompt = f"What news financial factors and earnings reports affected {clean_name} stock price movement?"

    return retriever.retrieve_relevant_news(query_prompt=query_prompt, company_name=company_name, top_k=top_k)
