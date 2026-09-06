from datetime import date as date_type
from typing import List, Optional
from pydantic import BaseModel, Field


class DataItemCreate(BaseModel):
    date: date_type = Field(..., description="관측 날짜 (YYYY-MM-DD)")
    value: float = Field(..., description="관측 값 (예: 평균기온)")
    memo: Optional[str] = Field(None, max_length=200, description="메모")


class DataItemUpdate(BaseModel):
    date: Optional[date_type] = None
    value: Optional[float] = None
    memo: Optional[str] = Field(None, max_length=200)


class DataItemOut(BaseModel):
    id: str
    date: str
    value: float
    memo: Optional[str] = None


class Metrics(BaseModel):
    total: float
    average: float
    max: float
    min: float


class DataSummary(BaseModel):
    period: str
    count: int
    metrics: Metrics
    trend: str


class DataStatistics(DataSummary):
    std_dev: float
    moving_average_7: Optional[float] = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    used_tools: List[str] = []


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    messages: List[ChatMessage] = []


class ConversationSummaryOut(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int


class ConversationDetailOut(BaseModel):
    id: str
    title: str
    created_at: str
    messages: List[ChatMessage]
