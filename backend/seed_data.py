"""
샘플 CSV(sample_data/daejeon_temperature.csv)를 Firestore 'data' 컬렉션에 업로드.

실행 전:
  1) .env 파일에 FIREBASE_SERVICE_ACCOUNT_JSON 설정 완료
  2) pip install -r requirements.txt

실행:
  python seed_data.py
"""
import csv
from app.database import get_db, DATA_COLLECTION

CSV_PATH = "sample_data/daejeon_temperature.csv"


def main():
    db = get_db()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            db.collection(DATA_COLLECTION).add(
                {
                    "date": row["date"],
                    "value": float(row["value"]),
                    "memo": row.get("memo") or None,
                }
            )
            count += 1
    print(f"{count}개 데이터 업로드 완료.")


if __name__ == "__main__":
    main()
