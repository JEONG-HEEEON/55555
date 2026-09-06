import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from app.config import FIREBASE_SERVICE_ACCOUNT_JSON

_db = None


def get_db():
    """Firestore 클라이언트를 초기화 후 반환 (싱글턴)."""
    global _db
    if _db is not None:
        return _db

    if not firebase_admin._apps:
        if not FIREBASE_SERVICE_ACCOUNT_JSON:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON 환경변수가 설정되지 않았습니다."
            )
        value = FIREBASE_SERVICE_ACCOUNT_JSON.strip()

        # 1) 값이 실제 존재하는 파일 경로인 경우 -> 파일을 직접 로드 (로컬 개발 시 추천)
        if os.path.isfile(value):
            cred = credentials.Certificate(value)
        else:
            # 2) 값이 JSON 문자열 전체인 경우 -> 파싱 (Render 등 배포 환경에서 추천)
            try:
                service_account_info = json.loads(value)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    "FIREBASE_SERVICE_ACCOUNT_JSON 값을 해석할 수 없습니다. "
                    "존재하는 파일 경로이거나, 올바른 한 줄 JSON 문자열이어야 합니다. "
                    f"(원인: {e})"
                )
            cred = credentials.Certificate(service_account_info)

        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


# 컬렉션 이름 상수
DATA_COLLECTION = "data"
CONVERSATIONS_COLLECTION = "conversations"
