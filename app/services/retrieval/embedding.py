from sentence_transformers import SentenceTransformer


class SentenceEmbedder:

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None

    def get_model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model


    def embed_query(self, query: str) -> list[float]:
        model = self.get_model()
        embeddings = model.encode(query)
        return embeddings.tolist()


    def embed_texts(self, texts: list[str]) -> list[list[str]]:
        model = self.get_model()
        embeddings = model.encode(texts, batch_size=self.batch_size)
        return embeddings.tolist()