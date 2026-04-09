"""
main.py
FastAPI server cho Vinmec Maternity Chatbot.
"""

import os
import uuid
import json
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent import VinmecAgent
from tools import append_feedback_log

load_dotenv()

# ---------------------------------------------------------------------------
# Config – đọc từ .env, không yêu cầu frontend gửi key
# ---------------------------------------------------------------------------

SESSIONS: dict[str, VinmecAgent] = {}

SERVER_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not SERVER_API_KEY:
    print("⚠️  OPENAI_API_KEY chưa được đặt trong .env")


def get_or_create_session(session_id: str, model: str) -> VinmecAgent:
    """Lấy hoặc tạo mới session agent dùng server API key."""
    if session_id not in SESSIONS:
        SESSIONS[session_id] = VinmecAgent(api_key=SERVER_API_KEY, model=model)
    return SESSIONS[session_id]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Vinmec Chatbot server started.")
    yield
    SESSIONS.clear()
    print("🛑 Server stopped. Sessions cleared.")


app = FastAPI(
    title="Vinmec Maternity Chatbot API",
    description="AI chatbot tư vấn gói thai sản Vinmec",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str
    model: str = DEFAULT_MODEL


class ResetRequest(BaseModel):
    session_id: str
    model: str = DEFAULT_MODEL


class WelcomeRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str = DEFAULT_MODEL


class BookingRequest(BaseModel):
    session_id: str
    name: str
    dob: str           # ngày sinh, VD: "01/01/1995"
    phone: str
    facility: str      # cơ sở chọn
    note: str = ""     # chủ đề tư vấn (tuỳ chọn)


class FeedbackRequest(BaseModel):
    session_id: str
    feedback_type: str = "bad"
    feedback_text: str = ""
    user_question: str = ""
    assistant_answer: str = ""
    policy_tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    model: str = DEFAULT_MODEL


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "Vinmec Chatbot API", "docs": "/docs"}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "sessions_active": len(SESSIONS),
        "default_model": DEFAULT_MODEL,
    }


@app.post("/api/welcome")
async def welcome(req: WelcomeRequest):
    """Trả về tin nhắn chào hỏi khi mở chat."""
    session_id = req.session_id or str(uuid.uuid4())
    temp_agent = VinmecAgent(api_key=SERVER_API_KEY or "placeholder", model=req.model)
    return {
        "session_id": session_id,
        "response": temp_agent.get_welcome_message(),
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Gửi tin nhắn và nhận phản hồi từ agent."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if not SERVER_API_KEY:
        raise HTTPException(status_code=500, detail="Server chưa cấu hình OPENAI_API_KEY trong .env")

    agent = get_or_create_session(req.session_id, req.model)

    try:
        response = agent.chat(req.message)
    except Exception as e:
        err_msg = str(e)
        if "401" in err_msg or "authentication" in err_msg.lower():
            raise HTTPException(status_code=401, detail="OpenAI API key không hợp lệ hoặc đã hết hạn.")
        if "429" in err_msg:
            raise HTTPException(status_code=429, detail="Vượt quá giới hạn request OpenAI. Vui lòng thử lại sau.")
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {err_msg[:200]}")

    return {
        "session_id": req.session_id,
        "response": response,
    }


@app.post("/api/reset")
async def reset_session(req: ResetRequest):
    """Xoá lịch sử hội thoại của một session."""
    if req.session_id in SESSIONS:
        SESSIONS[req.session_id].reset()
    return {"status": "ok", "session_id": req.session_id}


@app.post("/api/feedback")
async def log_feedback(req: FeedbackRequest):
    """Lưu feedback người dùng vào feedback_log.jsonl."""
    agent = SESSIONS.get(req.session_id)

    user_question = req.user_question.strip()
    if not user_question and agent:
        user_question = agent.last_user_message

    assistant_answer = req.assistant_answer.strip()
    if not assistant_answer and agent:
        assistant_answer = str(agent.last_response_payload.get("text", "")).strip()

    policy_tags = req.policy_tags
    if not policy_tags and agent:
        policy_tags = list(agent.last_response_payload.get("policy_tags", []) or [])

    metadata = dict(req.metadata)
    if agent:
        metadata.setdefault("assistant_type", agent.last_response_payload.get("type", ""))

    feedback_text = req.feedback_text.strip()
    if not feedback_text:
        feedback_text = (
            "Người dùng xác nhận câu trả lời hữu ích."
            if req.feedback_type == "good"
            else "Người dùng báo thông tin sai, thiếu hoặc cần kiểm tra lại."
        )

    if not user_question and not assistant_answer:
        raise HTTPException(status_code=400, detail="Không có đủ context để ghi feedback.")

    record = append_feedback_log(
        session_id=req.session_id,
        user_question=user_question,
        assistant_answer=assistant_answer,
        feedback_text=feedback_text,
        feedback_type=req.feedback_type,
        policy_tags=policy_tags,
        model=agent.model if agent else req.model,
        source="api",
        metadata=metadata,
    )

    return {
        "status": "ok",
        "feedback_type": record["feedback_type"],
        "timestamp": record["timestamp"],
    }


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Xoá hoàn toàn một session."""
    SESSIONS.pop(session_id, None)
    return {"status": "ok"}


@app.post("/api/booking")
async def create_booking(req: BookingRequest):
    """Lưu lịch tư vấn vào file bookings.json."""
    record = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_id": req.session_id,
        "name": req.name,
        "dob": req.dob,
        "phone": req.phone,
        "facility": req.facility,
        "note": req.note,
        "status": "pending",
    }

    bookings_file = Path(__file__).parent / "bookings.json"
    bookings: list = []
    if bookings_file.exists():
        try:
            bookings = json.loads(bookings_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            bookings = []

    bookings.append(record)
    bookings_file.write_text(
        json.dumps(bookings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"📅 Booking mới: {record['name']} | {record['facility']} | {record['phone']}")
    return {"status": "ok", "booking_id": record["id"]}


@app.get("/api/bookings")
async def list_bookings():
    """Xem danh sách lịch đặt (admin)."""
    bookings_file = Path(__file__).parent / "bookings.json"
    if not bookings_file.exists():
        return {"count": 0, "bookings": []}
    bookings = json.loads(bookings_file.read_text(encoding="utf-8"))
    return {"count": len(bookings), "bookings": bookings}


@app.get("/api/sessions")
async def list_sessions():
    """Debug: liệt kê sessions đang active."""
    return {
        "count": len(SESSIONS),
        "session_ids": list(SESSIONS.keys()),
    }
