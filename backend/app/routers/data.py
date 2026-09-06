from fastapi import APIRouter, HTTPException
from app.database import get_db, DATA_COLLECTION
from app.models import DataItemCreate, DataItemUpdate, DataItemOut, DataSummary, DataStatistics
from app.services.analysis import compute_summary, compute_statistics

router = APIRouter(prefix="/api/data", tags=["data"])


def _fetch_all_items():
    db = get_db()
    docs = db.collection(DATA_COLLECTION).stream()
    items = []
    for doc in docs:
        d = doc.to_dict()
        items.append({"id": doc.id, "date": d["date"], "value": d["value"], "memo": d.get("memo")})
    return items


@router.post("", response_model=DataItemOut)
def create_data(item: DataItemCreate):
    db = get_db()
    payload = {
        "date": item.date.isoformat(),
        "value": item.value,
        "memo": item.memo,
    }
    _, doc_ref = db.collection(DATA_COLLECTION).add(payload)
    return DataItemOut(id=doc_ref.id, **payload)


@router.get("", response_model=list[DataItemOut])
def list_data():
    items = _fetch_all_items()
    items.sort(key=lambda x: x["date"])
    return items


@router.put("/{item_id}", response_model=DataItemOut)
def update_data(item_id: str, item: DataItemUpdate):
    db = get_db()
    doc_ref = db.collection(DATA_COLLECTION).document(item_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")

    update_data = {k: v for k, v in item.model_dump(exclude_unset=True).items() if v is not None}
    if "date" in update_data:
        update_data["date"] = update_data["date"].isoformat()
    if update_data:
        doc_ref.update(update_data)

    updated = doc_ref.get().to_dict()
    return DataItemOut(id=item_id, date=updated["date"], value=updated["value"], memo=updated.get("memo"))


@router.delete("/{item_id}")
def delete_data(item_id: str):
    db = get_db()
    doc_ref = db.collection(DATA_COLLECTION).document(item_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    doc_ref.delete()
    return {"status": "deleted", "id": item_id}


@router.get("/summary", response_model=DataSummary)
def get_summary():
    items = _fetch_all_items()
    return compute_summary(items)


@router.get("/statistics", response_model=DataStatistics)
def get_statistics():
    """보너스: 요약 확장 (표준편차, 최근 7개 이동평균)"""
    items = _fetch_all_items()
    return compute_statistics(items)
