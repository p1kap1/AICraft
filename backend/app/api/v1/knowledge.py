"""RAG 知识库 API"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.knowledge import KnowledgeBase, KnowledgeChunk
from app.schemas.common import ApiResponse
from app.services.embedding import get_embedding
import uuid

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])
CHUNK_SIZE = 500


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


@router.post("")
def create_kb(name: str = "", description: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    kb = KnowledgeBase(name=name, description=description, user_id=user.id)
    db.add(kb); db.commit(); db.refresh(kb)
    return ApiResponse(data={"id": kb.id, "name": kb.name})


@router.get("/user")
def list_kbs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": k.id, "name": k.name, "description": k.description} for k in db.query(KnowledgeBase).filter(KnowledgeBase.user_id == user.id).all()]


@router.get("/{kb_id}/chunks")
def get_chunks(kb_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id).first()
    if not kb: raise HTTPException(404, "Not found")
    return [{"id": c.id, "content": c.content, "index": c.chunk_index, "source": c.source} for c in db.query(KnowledgeChunk).filter(KnowledgeChunk.kb_id == kb_id).order_by(KnowledgeChunk.chunk_index).limit(50).all()]


@router.post("/{kb_id}/upload")
async def upload_document(kb_id: str, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id).first()
    if not kb: raise HTTPException(404, "Not found")

    filename = file.filename or ""
    content = ""
    if filename.endswith(".pdf"):
        import pypdf, io
        content = "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(await file.read())).pages)
    elif filename.endswith(".docx"):
        import docx, io
        content = "\n".join(p.text for p in docx.Document(io.BytesIO(await file.read())).paragraphs)
    else:
        content = (await file.read()).decode("utf-8", errors="ignore")

    count = 0
    for i, text in enumerate(chunk_text(content)):
        db.add(KnowledgeChunk(kb_id=kb_id, content=text, source=filename, chunk_index=i, embedding=get_embedding(text)))
        count += 1
    db.commit()
    return ApiResponse(data={"chunks": count, "filename": filename})


@router.post("/{kb_id}/search")
def search_kb(kb_id: str, query: str = "", top_k: int = 5, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id).first()
    if not kb: raise HTTPException(404, "知识库不存在")

    # 1. 关键词检索（ILIKE 模糊匹配）
    keyword_results = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.kb_id == kb_id,
        KnowledgeChunk.content.ilike(f"%{query}%")
    ).limit(top_k).all()

    # 2. 向量检索（cosine 相似度）
    try:
        q_emb = get_embedding(query)
        vector_results = db.query(KnowledgeChunk).filter(
            KnowledgeChunk.kb_id == kb_id,
            KnowledgeChunk.embedding.isnot(None)
        ).order_by(KnowledgeChunk.embedding.cosine_distance(q_emb)).limit(top_k).all()
    except:
        vector_results = []

    # 3. 合并去重（关键词优先，向量补充）
    seen = {c.id: c for c in keyword_results}
    for c in vector_results:
        if c.id not in seen and len(seen) < top_k * 2:
            seen[c.id] = c

    return {"query": query, "results": [{"content": c.content, "source": c.source} for c in list(seen.values())[:top_k]]}


@router.delete("/{kb_id}")
def delete_kb(kb_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id, KnowledgeBase.user_id == user.id).first()
    if not kb: raise HTTPException(404, "Not found")
    db.query(KnowledgeChunk).filter(KnowledgeChunk.kb_id == kb_id).delete()
    db.delete(kb); db.commit()
    return ApiResponse(message="已删除")
