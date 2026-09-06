from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.database import get_db, CONVERSATIONS_COLLECTION
from app.models import ConversationCreate, ConversationSummaryOut, ConversationDetailOut

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationDetailOut)
def create_conversation(conv: ConversationCreate):
    db = get_db()
    created_at = datetime.now(timezone.utc).isoformat()
    title = conv.title or (conv.messages[0].content[:30] if conv.messages else "새 대화")
    payload = {
        "title": title,
        "created_at": created_at,
        "messages": [m.model_dump() for m in conv.messages],
    }
    _, doc_ref = db.collection(CONVERSATIONS_COLLECTION).add(payload)
    return ConversationDetailOut(id=doc_ref.id, **payload)


@router.get("", response_model=list[ConversationSummaryOut])
def list_conversations():
    db = get_db()
    docs = db.collection(CONVERSATIONS_COLLECTION).stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        result.append(
            ConversationSummaryOut(
                id=doc.id,
                title=d.get("title", "대화"),
                created_at=d.get("created_at", ""),
                message_count=len(d.get("messages", [])),
            )
        )
    result.sort(key=lambda x: x.created_at, reverse=True)
    return result


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(conversation_id: str):
    db = get_db()
    doc = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    d = doc.to_dict()
    return ConversationDetailOut(
        id=doc.id, title=d.get("title", "대화"), created_at=d.get("created_at", ""),
        messages=d.get("messages", []),
    )


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    db = get_db()
    doc_ref = db.collection(CONVERSATIONS_COLLECTION).document(conversation_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    doc_ref.delete()
    return {"status": "deleted", "id": conversation_id}
