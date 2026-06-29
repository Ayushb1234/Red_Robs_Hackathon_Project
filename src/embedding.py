from sentence_transformers import SentenceTransformer

class EmbeddingEngine:

    def __init__(self):

        self.model=SentenceTransformer(

            "all-MiniLM-L6-v2"

        )

    def encode(self,texts):

        return self.model.encode(

            texts,

            normalize_embeddings=True,

            show_progress_bar=True

        )