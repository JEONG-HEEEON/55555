from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS
from app.routers import data, conversations, chat

app = FastAPI(
    title="시계열 데이터 AI 분석 챗봇 API",
    description="시계열 데이터를 저장/분석하고, 요약을 컨텍스트로 주입해 GPT와 대화하는 서비스",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
def health_check():
    # Render 무료 티어 콜드스타트 확인용 헬스체크 엔드포인트
    return {"status": "ok", "message": "API가 정상 동작 중입니다."}
