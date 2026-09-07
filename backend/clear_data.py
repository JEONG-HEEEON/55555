"""
Firestore 'data' 컬렉션의 모든 문서를 삭제합니다.
(seed_data.py를 실수로 여러 번 실행해서 중복이 쌓였을 때 정리용)

실행:
  python clear_data.py
"""
from app.database import get_db, DATA_COLLECTION


def main():
    db = get_db()
    docs = list(db.collection(DATA_COLLECTION).stream())
    count = len(docs)
    for doc in docs:
        doc.reference.delete()
    print(f"{count}개 데이터 삭제 완료.")


if __name__ == "__main__":
    main()