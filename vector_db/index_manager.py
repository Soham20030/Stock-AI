import os
import json
import numpy as np
import faiss

# Default directory for storing FAISS binary index and metadata JSON
VECTOR_DB_DIR = os.path.dirname(__file__)
DEFAULT_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "faiss_index.bin")
DEFAULT_META_PATH = os.path.join(VECTOR_DB_DIR, "metadata.json")


class FAISSIndexManager:
    """
    Manages building, saving, loading, and searching FAISS vector indices
    for high-speed semantic retrieval over embedded news articles.
    """

    def __init__(self, dim=384, index_path=DEFAULT_INDEX_PATH, metadata_path=DEFAULT_META_PATH):
        """
        Initializes the FAISS Index Manager.

        Parameters:
            dim (int): Vector dimension (default 384 for all-MiniLM-L6-v2).
            index_path (str): Filepath for binary FAISS index storage.
            metadata_path (str): Filepath for article metadata JSON storage.
        """
        self.dim = dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []

        # Ensure vector_db directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

    def create_index(self, embeddings, metadata_list):
        """
        Builds a new FAISS index from an embedding matrix and metadata records.

        Parameters:
            embeddings (list or np.ndarray): Matrix of shape (N, dim).
            metadata_list (list of dict): List of N article metadata dictionaries.

        Returns:
            int: Number of vectors added to the index.
        """
        if len(embeddings) == 0:
            print("Warning: Empty embeddings provided to create_index.")
            return 0

        # Convert embeddings matrix to contiguous float32 numpy array
        matrix = np.array(embeddings, dtype=np.float32)
        if matrix.ndim == 1:
            matrix = np.expand_dims(matrix, axis=0)

        # L2 normalize vectors for Cosine Similarity matching via Inner Product
        faiss.normalize_L2(matrix)

        # Instantiate FAISS Inner Product Index (Cosine Similarity after L2 norm)
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(matrix)
        self.metadata = list(metadata_list)

        print(f"Successfully created FAISS index with {self.index.ntotal} vectors.")
        return self.index.ntotal

    def save_index(self):
        """
        Serializes the active FAISS index to binary disk storage and 
        saves article metadata mappings to JSON.

        Returns:
            bool: True if successfully saved, False otherwise.
        """
        if self.index is None or self.index.ntotal == 0:
            print("No active index to save.")
            return False

        try:
            # Write binary FAISS index
            faiss.write_index(self.index, self.index_path)

            # Write sidecar metadata JSON file
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)

            print(f"Index saved to {self.index_path} and metadata to {self.metadata_path}.")
            return True
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
            return False

    def load_index(self):
        """
        Loads binary FAISS index and JSON metadata from disk into memory.

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            print("Index or metadata file does not exist on disk.")
            return False

        try:
            # Read binary FAISS index
            self.index = faiss.read_index(self.index_path)

            # Read metadata JSON mapping
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            print(f"Successfully loaded FAISS index with {self.index.ntotal} vectors.")
            return True
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return False

    def search(self, query_embedding, top_k=5):
        """
        Executes semantic nearest-neighbor search against the FAISS index.

        Parameters:
            query_embedding (list or np.ndarray): Query vector of shape (1, dim) or (dim,).
            top_k (int): Number of top relevant articles to retrieve.

        Returns:
            list of dict: Top-k matching article metadata records with similarity scores.
        """
        if self.index is None or self.index.ntotal == 0:
            # Attempt to auto-load from disk if available
            if not self.load_index():
                return []

        # Format query array
        q_matrix = np.array(query_embedding, dtype=np.float32)
        if q_matrix.ndim == 1:
            q_matrix = np.expand_dims(q_matrix, axis=0)

        # Normalize query vector for Cosine Similarity search
        faiss.normalize_L2(q_matrix)

        # Cap k to total available vectors in index
        k_search = min(top_k, self.index.ntotal)
        if k_search == 0:
            return []

        # Execute FAISS search
        distances, indices = self.index.search(q_matrix, k_search)

        results = []
        for rank, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                item = dict(self.metadata[idx])
                item["score"] = float(distances[0][rank])  # Cosine similarity score
                results.append(item)

        return results
