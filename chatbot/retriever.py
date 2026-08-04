import numpy as np
from rag.embeddings import get_embedding_generator
from vector_db.index_manager import FAISSIndexManager


class ChatbotContextRetriever:
    """
    Executes semantic vector search over category-tagged dashboard context chunks
    to retrieve only the top-k context snippets relevant to a user's question.
    """

    def __init__(self):
        """
        Initializes the Context Retriever with shared SentenceTransformers embedding generator
        and an in-memory FAISS index manager.
        """
        self.embedder = get_embedding_generator()
        self.index_manager = FAISSIndexManager(dim=self.embedder.dimension)
        self.context_chunks = []

    def index_context_chunks(self, chunks):
        """
        Encodes context chunk text strings into 384-d dense vectors and builds
        the active FAISS vector index.

        Parameters:
            chunks (list of dict): List of atomic context chunk dictionaries built by ContextBuilder.

        Returns:
            int: Number of context chunks indexed.
        """
        if not chunks:
            return 0

        self.context_chunks = list(chunks)
        texts_to_encode = [c.get("text", "") for c in self.context_chunks]

        # Generate dense embeddings matrix
        embeddings_matrix, metadata_records = self.embedder.embed_articles(
            [{"title": txt, "content": txt} for txt in texts_to_encode]
        )

        if len(metadata_records) == 0:
            return 0

        # Build in-memory FAISS index
        total_indexed = self.index_manager.create_index(embeddings_matrix, self.context_chunks)
        return total_indexed

    def retrieve_relevant_context(self, user_question, top_k=3):
        """
        Converts the user question into a vector embedding, searches the FAISS index,
        and returns the top-k most semantically relevant context chunks.

        Parameters:
            user_question (str): User prompt/question string.
            top_k (int): Number of top context chunks to retrieve (default 3).

        Returns:
            list of dict: Top-k matching context chunk dictionaries with similarity scores.
        """
        if not user_question or not isinstance(user_question, str):
            return self.context_chunks[:top_k]

        if self.index_manager.index is None or self.index_manager.index.ntotal == 0:
            return self.context_chunks[:top_k]

        # Embed user question string into 384-d vector
        query_vector = self.embedder.embed_text(user_question)

        # Execute vector similarity search in FAISS
        results = self.index_manager.search(query_vector, top_k=top_k)

        # Fallback to initial chunks if search yields no results
        if not results:
            return self.context_chunks[:top_k]

        return results


def retrieve_context_for_question(user_question, context_chunks, top_k=3):
    """
    Convenience functional wrapper to index context chunks and retrieve top-k
    relevant context snippets for a question.
    """
    retriever = ChatbotContextRetriever()
    retriever.index_context_chunks(context_chunks)
    return retriever.retrieve_relevant_context(user_question=user_question, top_k=top_k)
