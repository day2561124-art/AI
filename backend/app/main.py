from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.rag.loader import load_knowledge_base
from app.rag.retriever import LocalRetriever
from app.rag.safety import build_answer, classify_question
from app.llm import generate_llm_answer, llm_enabled
from app.storage import JsonStore


PROJECT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_DIR / ".env")


def find_knowledge_path() -> Path:
    configured_path = os.getenv("KNOWLEDGE_BASE_PATH")
    if configured_path:
        path = Path(configured_path)
        if not path.is_absolute():
            path = PROJECT_DIR / path
        return path.resolve()

    txt_files = sorted(PROJECT_DIR.glob("*.txt"))
    if not txt_files:
        return PROJECT_DIR / "knowledge.txt"
    return txt_files[0]


KNOWLEDGE_PATH = find_knowledge_path()
store = JsonStore(PROJECT_DIR / "data")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-admin-token")

app = FastAPI(title="AI Customer Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chunks = load_knowledge_base(KNOWLEDGE_PATH)
retriever = LocalRetriever(chunks)


def reload_knowledge() -> dict:
    global chunks, retriever
    chunks = load_knowledge_base(KNOWLEDGE_PATH)
    retriever = LocalRetriever(chunks)
    return {
        "knowledge_path": str(KNOWLEDGE_PATH),
        "chunk_count": len(chunks),
        "retriever": "local-hybrid-tfidf",
    }


class ChatRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    helpful: bool
    comment: str | None = None


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not ADMIN_TOKEN:
        return
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/knowledge/status")
def knowledge_status() -> dict:
    return {
        "knowledge_path": str(KNOWLEDGE_PATH),
        "chunk_count": len(chunks),
        "retriever": "local-hybrid-tfidf",
        "llm_enabled": llm_enabled(),
    }


@app.post("/api/chat")
def chat(payload: ChatRequest) -> dict:
    question = payload.question.strip()
    category = classify_question(question)
    matches = retriever.search(question, top_k=5, category=category)
    response = build_answer(question, category, matches)
    llm_answer = generate_llm_answer(question, category, matches, response["sources"])
    response["llm_used"] = bool(llm_answer)
    if llm_answer:
        response["answer"] = llm_answer
    saved = store.append(
        "chat_logs",
        {
            "question": question,
            "answer": response["answer"],
            "category": response["category"],
            "category_label": response["category_label"],
            "matched": response["matched"],
            "sources": response["sources"],
            "notice": response["notice"],
        },
    )
    response["conversation_id"] = saved["id"]
    if not response["matched"]:
        store.append(
            "unanswered_questions",
            {
                "question": question,
                "category": response["category"],
                "category_label": response["category_label"],
            },
        )
    return response


@app.get("/api/faqs")
def faqs() -> dict:
    return {
        "items": [
            {
                "category": "course",
                "question": "What is the total training duration?",
                "answer": "The knowledge base states that both listed terms are 255 hours. Please verify by term.",
            },
            {
                "category": "subsidy",
                "question": "Is subsidy guaranteed?",
                "answer": "No. The system can only say eligible users may apply. Final approval depends on official review.",
            },
            {
                "category": "contact",
                "question": "What is the contact phone number?",
                "answer": "06-213-0019 or 06-2130019.",
            },
        ]
    }


@app.post("/api/feedback")
def feedback(payload: FeedbackRequest) -> dict:
    saved = store.append(
        "feedback",
        {
            "question": payload.question,
            "answer": payload.answer,
            "helpful": payload.helpful,
            "comment": payload.comment,
        },
    )
    return {
        "status": "received",
        "id": saved["id"],
        "message": "Feedback saved.",
    }


@app.get("/api/admin/stats")
def admin_stats(_: None = Depends(require_admin)) -> dict:
    return store.stats()


@app.get("/api/admin/chat-logs")
def admin_chat_logs(limit: int = 30, _: None = Depends(require_admin)) -> dict:
    return {"items": store.list("chat_logs", limit=limit)}


@app.get("/api/admin/feedback")
def admin_feedback(limit: int = 30, _: None = Depends(require_admin)) -> dict:
    return {"items": store.list("feedback", limit=limit)}


@app.get("/api/admin/unanswered")
def admin_unanswered(limit: int = 30, _: None = Depends(require_admin)) -> dict:
    return {"items": store.list("unanswered_questions", limit=limit)}


@app.post("/api/admin/knowledge/reload")
def admin_reload_knowledge(_: None = Depends(require_admin)) -> dict:
    status = reload_knowledge()
    return {"status": "reloaded", **status}


@app.post("/api/admin/knowledge/upload")
async def admin_upload_knowledge(
    file: UploadFile = File(...),
    _: None = Depends(require_admin),
) -> dict:
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    content = await file.read()
    if not content.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    version_dir = PROJECT_DIR / "data" / "knowledge_versions"
    version_dir.mkdir(parents=True, exist_ok=True)

    if KNOWLEDGE_PATH.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = version_dir / f"{timestamp}_{KNOWLEDGE_PATH.name}"
        backup_path.write_bytes(KNOWLEDGE_PATH.read_bytes())

    KNOWLEDGE_PATH.write_bytes(content)
    status = reload_knowledge()
    store.append(
        "knowledge_versions",
        {
            "filename": file.filename,
            "active_path": str(KNOWLEDGE_PATH),
            "chunk_count": status["chunk_count"],
        },
    )
    return {"status": "uploaded", "filename": file.filename, **status}
