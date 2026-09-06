from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.database import get_db, CONVERSATIONS_COLLECTION
from app.models import ChatRequest, ChatResponse
from app.routers.data import _fetch_all_items
from app.services.openai_service import run_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    db = get_db()

    # 1) 기존 대화 불러오기 (있으면 이어서, 없으면 새로 시작)
    history = []
    conv_ref = None
    if req.conversation_id:
        conv_ref = db.collection(CONVERSATIONS_COLLECTION).document(req.conversation_id)
        doc = conv_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
        history = doc.to_dict().get("messages", [])

    history.append({"role": "user", "content": req.message})

    # 2) 데이터 요약 조회 + 3) GPT 호출 (컨텍스트 주입은 openai_service 내부에서 처리)
    all_items = _fetch_all_items()
    try:
        result = run_chat(history, all_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    history.append({"role": "assistant", "content": result["reply"]})

    # 4) 대화 자동 저장
    if conv_ref is None:
        created_at = datetime.now(timezone.utc).isoformat()
        title = req.message[:30]
        _, conv_ref = db.collection(CONVERSATIONS_COLLECTION).add(
            {"title": title, "created_at": created_at, "messages": history}
        )
        conversation_id = conv_ref.id
    else:
        conv_ref.update({"messages": history})
        conversation_id = req.conversation_id

    return ChatResponse(
        conversation_id=conversation_id,
        reply=result["reply"],
        used_tools=result["used_tools"],
    )
