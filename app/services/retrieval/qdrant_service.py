import logfire
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
import uuid
from app.services.retrieval.embedding import SentenceEmbedder


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_CLUSTER_ENDPOINT.get_secret_value(),
            api_key=settings.QDRANT_API_KEY.get_secret_value(),
            cloud_inference=True
        )
        self.collection_name: str = settings.QDRANT_COLLECITON
        self.embedder = None


    def _load_embedder(self):
        if self.embedder is None:
            self.embedder = SentenceEmbedder()
        return self.embedder


    def ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logfire.info(f"Create Qdrant collection '{self.collection_name}'")


    def clean_collection(self):
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
            logfire.info(f"Colleciton '{self.collection_name}' deleted")


    def insert_enterpirse_knowledge(self, filename: str, source_type: str, chunks: list[str]):
        with logfire.span("Vectorzing and Indexing"):
            embedder = self._load_embedder()
            embeddings = embedder.embed_texts(chunks)

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk,
                        "source": filename,
                        "source_type": source_type,
                        "raw_gsc_path": f"./artifacts/{settings.RAW_BUCKET}/{source_type}/{filename}"
                    }
                )
                for chunk, vector in zip(chunks, embeddings)
            ]

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                timeout=120
                )

            logfire.info(f"Indexed {len(points)} points to Qdrant from '{filename}'")


    def search_enterpirse_knowledge(self, query: str, limit: int = 8):
        try:
            embedder = self._load_embedder()

            response = self.client.query_points(
                collection_name=settings.QDRANT_COLLECITON,
                query=embedder.embed_query(query),
                with_payload=True,
                limit=limit
            )

            results = []
            for result in response.points:
                results.append(
                    {
                        "content": result.payload.get("text", ""),
                        "source": result.payload.get("source", "Unknown"),
                        "score": result.score    
                    }
                )

            return results

        except Exception as e:
            logfire.error(f"Qdrant Search Failed: {e}")
            raise e