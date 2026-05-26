"""知识库检索——被工具调用"""
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeChunk
from openai import OpenAI
from app.core.config import settings


def search_all_kbs(query: str, top_k: int = 3) -> list[dict]:
    """跨所有知识库搜索"""
    db = SessionLocal()
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        resp = client.embeddings.create(model="text-embedding-ada-002", input=query)
        query_emb = resp.data[0].embedding

        results = (
            db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.embedding.isnot(None))
            .order_by(KnowledgeChunk.embedding.cosine_distance(query_emb))
            .limit(top_k)
            .all()
        )

        return [
            {"content": r.content, "source": r.source, "chunk_index": r.chunk_index}
            for r in results
        ]
    finally:
        db.close()
