import numpy as np
from sentence_transformers import SentenceTransformer

# Default lightweight model producing 384-dimensional dense vectors
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

# Global cached model instance to prevent redundant re-initialization
_GLOBAL_EMBEDDING_GENERATOR = None


class EmbeddingGenerator:
    """
    Encapsulates SentenceTransformers dense vector encoding for financial news
    and user search queries.
    """

    def __init__(self, model_name=DEFAULT_MODEL_NAME):
        """
        Initializes the SentenceTransformer encoder model.

        Parameters:
            model_name (str): HuggingFace model identifier.
        """
        self.model_name = model_name
        print(f"Loading SentenceTransformer model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"SentenceTransformer loaded successfully. Dimension: {self.dimension}")

    def embed_text(self, text):
        """
        Encodes a single text string into a 384-dimensional float32 numpy vector.

        Parameters:
            text (str): Input text string.

        Returns:
            np.ndarray: 1D vector of shape (384,).
        """
        if not text or not isinstance(text, str):
            return np.zeros((self.dimension,), dtype=np.float32)

        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.astype(np.float32)

    def embed_articles(self, articles):
        """
        Encodes a list of GDELT article dictionaries into a 2D numpy matrix 
        and extracts standardized metadata records.

        Parameters:
            articles (list of dict): List of article objects with 'title', 'content', 'url', etc.

        Returns:
            tuple: (embeddings_matrix, metadata_records)
                - embeddings_matrix (np.ndarray): Shape (N, 384) float32 array.
                - metadata_records (list of dict): Article metadata mapped 1-to-1 to matrix rows.
        """
        if not articles:
            return np.empty((0, self.dimension), dtype=np.float32), []

        texts_to_encode = []
        metadata_records = []

        for art in articles:
            title = art.get("title", "").strip()
            content = art.get("content", "").strip()

            # Combine title and content snippet for rich semantic representation
            if title and content and title != content:
                combined_text = f"{title}. {content}"
            else:
                combined_text = title or content or "Financial market news article"

            texts_to_encode.append(combined_text)
            
            # Format clean metadata object
            metadata_records.append({
                "title": title,
                "date": art.get("date", "N/A"),
                "url": art.get("url", "#"),
                "source": art.get("source", "GDELT"),
                "content": content
            })

        # Batch encode all article strings into dense matrix
        embeddings_matrix = self.model.encode(
            texts_to_encode,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype(np.float32)

        return embeddings_matrix, metadata_records


def get_embedding_generator():
    """
    Singleton getter to access a shared global instance of EmbeddingGenerator.

    Returns:
        EmbeddingGenerator: Cached global embedding generator instance.
    """
    global _GLOBAL_EMBEDDING_GENERATOR
    if _GLOBAL_EMBEDDING_GENERATOR is None:
        _GLOBAL_EMBEDDING_GENERATOR = EmbeddingGenerator()
    return _GLOBAL_EMBEDDING_GENERATOR
