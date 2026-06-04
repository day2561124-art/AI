from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

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
        if path.is_absolute():
            return path.resolve()

        candidates = [
            PROJECT_DIR / path,
            Path.cwd() / path,
            Path(__file__).resolve().parents[1] / path,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()

    fallback_candidates = [
        Path.cwd() / "knowledge_base.txt",
        PROJECT_DIR / "knowledge_base.txt",
        Path(__file__).resolve().parents[1] / "knowledge_base.txt",
    ]
    for candidate in fallback_candidates:
        if candidate.exists():
            return candidate.resolve()

    txt_files = sorted({*PROJECT_DIR.glob("*.txt"), *Path.cwd().glob("*.txt")})
    if not txt_files:
        return PROJECT_DIR / "knowledge.txt"
    return txt_files[0]


KNOWLEDGE_PATH = find_knowledge_path()
store = JsonStore(PROJECT_DIR / "data")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-admin-token")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://ai-project-frontend-mrm9.onrender.com")

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


DUAL_TERM_CATEGORIES = {
    "course",
    "registration",
    "subsidy",
    "exam",
    "eligibility",
    "admission",
    "latest",
}


def mentions_specific_term(question: str) -> bool:
    return any(
        keyword in question
        for keyword in ["114", "115", "\u7b2c01", "\u7b2c 01", "\u7b2c02", "\u7b2c 02"]
    )


def include_both_terms(question: str, category: str, matches: list[dict]) -> list[dict]:
    if category not in DUAL_TERM_CATEGORIES or mentions_specific_term(question):
        return matches

    enriched = list(matches)
    seen_ids = {match["id"] for match in enriched}
    years = {match["metadata"].get("year") for match in enriched if match["metadata"].get("year")}

    for year in ["114", "115"]:
        if year in years:
            continue
        for candidate in retriever.search(f"{question} {year}", top_k=3, category=category):
            if candidate["id"] in seen_ids:
                continue
            enriched.append(candidate)
            seen_ids.add(candidate["id"])
            years.add(year)
            break

    return enriched[:7]


def is_casual_chat(question: str) -> bool:
    compact = question.strip().lower().replace(" ", "")
    course_terms = [
        "\u5831\u540d",
        "\u88dc\u52a9",
        "\u734e\u52f5\u91d1",
        "\u7504\u8a66",
        "\u8ab2\u7a0b",
        "\u4e0a\u8ab2",
        "\u6642\u6578",
        "\u5730\u9ede",
        "\u806f\u7d61",
        "\u96fb\u8a71",
        "line",
        "114",
        "115",
        "\u8cc7\u683c",
        "\u8077\u524d",
    ]
    if any(term in compact for term in course_terms):
        return False

    casual_terms = [
        "hi",
        "hello",
        "hey",
        "ok",
        "\u4f60\u597d",
        "\u55e8",
        "\u65e9\u5b89",
        "\u5348\u5b89",
        "\u665a\u5b89",
        "\u8b1d\u8b1d",
        "\u611f\u8b1d",
        "\u8b1d\u5566",
        "\u4f60\u662f\u8ab0",
        "\u4f60\u53ef\u4ee5\u505a\u4ec0\u9ebc",
        "\u53ef\u4ee5\u5e6b\u6211",
        "\u6211\u60f3\u554f",
        "\u597d\u7684",
        "\u597d\u5594",
        "\u597d\u55ce",
    ]
    return len(compact) <= 40 and any(term in compact for term in casual_terms)


def casual_fallback_answer(question: str) -> str:
    compact = question.strip().lower().replace(" ", "")
    if any(term in compact for term in ["\u8b1d\u8b1d", "\u611f\u8b1d", "\u8b1d\u5566"]):
        return "\u4e0d\u5ba2\u6c23\uff5e\u5f88\u958b\u5fc3\u80fd\u5e6b\u4e0a\u5fd9 😊 \u5982\u679c\u4f60\u9084\u60f3\u67e5\u5831\u540d\u3001\u88dc\u52a9\u3001\u7504\u8a66\u6216\u806f\u7d61\u65b9\u5f0f\uff0c\u90fd\u53ef\u4ee5\u76f4\u63a5\u554f\u6211\u3002"
    if "\u4f60\u662f\u8ab0" in compact or "\u53ef\u4ee5\u505a\u4ec0\u9ebc" in compact:
        return "\u6211\u662f AI\u667a\u6167\u61c9\u7528\u7522\u696d\u4eba\u624d\u57f9\u8a13\u73ed\u7684\u5ba2\u670d\u52a9\u7406 😊 \u53ef\u4ee5\u5e6b\u4f60\u67e5\u8ab2\u7a0b\u5167\u5bb9\u3001\u5831\u540d\u65b9\u5f0f\u3001\u88dc\u52a9\u8cc7\u683c\u3001\u9752\u5e74\u734e\u52f5\u91d1\u3001\u7504\u8a66\u8cc7\u8a0a\u548c\u806f\u7d61\u7ba1\u9053\u3002"
    return "\u4f60\u597d\uff5e\u6211\u5728\u9019\u88e1 😊 \u4f60\u53ef\u4ee5\u76f4\u63a5\u554f\u6211\u95dc\u65bc AI\u667a\u6167\u61c9\u7528\u7522\u696d\u4eba\u624d\u57f9\u8a13\u73ed\u7684\u8ab2\u7a0b\u3001\u5831\u540d\u3001\u88dc\u52a9\u3001\u7504\u8a66\u6216\u806f\u7d61\u8cc7\u8a0a\u3002"


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
    visitor_id: str | None = None
    history: list[dict] = Field(default_factory=list)


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    helpful: bool
    comment: str | None = None
    visitor_id: str | None = None
    conversation_id: str | None = None


class VisitRequest(BaseModel):
    visitor_id: str
    page: str
    path: str | None = None
    referrer: str | None = None


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not ADMIN_TOKEN:
        return
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
@app.get("/admin", response_class=HTMLResponse)
def staff_entry() -> str:
    admin_url = f"{FRONTEND_URL.rstrip('/')}/admin"
    public_url = FRONTEND_URL.rstrip("/")
    return f"""
<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>工作人員入口｜AI智慧客服問答系統</title>
    <style>
      :root {{
        color: #172033;
        background: #eef6f6;
        font-family: "Noto Sans TC", "Microsoft JhengHei", system-ui, sans-serif;
      }}
      body {{
        min-height: 100vh;
        margin: 0;
        display: grid;
        place-items: center;
        background:
          linear-gradient(135deg, rgba(15,118,110,.11), transparent 34%),
          repeating-linear-gradient(0deg, rgba(15,118,110,.055) 0 1px, transparent 1px 12px),
          #f6fafb;
      }}
      main {{
        width: min(860px, calc(100% - 32px));
        border: 1px solid rgba(15,118,110,.18);
        border-radius: 12px;
        padding: clamp(28px, 5vw, 52px);
        background: rgba(255,255,255,.92);
        box-shadow: 0 24px 70px rgba(15, 23, 42, .12);
      }}
      .eyebrow {{
        color: #0f766e;
        font-size: 14px;
        font-weight: 900;
        letter-spacing: .08em;
      }}
      h1 {{
        margin: 10px 0 14px;
        font-size: clamp(34px, 6vw, 56px);
        line-height: 1.08;
      }}
      p {{
        max-width: 680px;
        color: #46566f;
        font-size: 17px;
        line-height: 1.9;
      }}
      .actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 28px;
      }}
      a {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 46px;
        border-radius: 8px;
        padding: 0 18px;
        color: #fff;
        background: #0f766e;
        font-weight: 800;
        text-decoration: none;
        box-shadow: 0 12px 24px rgba(15,118,110,.18);
      }}
      a.secondary {{
        color: #0f514c;
        border: 1px solid rgba(15,118,110,.22);
        background: #e7f5f2;
        box-shadow: none;
      }}
      .meta {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 34px;
      }}
      .meta div {{
        border: 1px solid rgba(148,163,184,.32);
        border-radius: 8px;
        padding: 14px;
        background: rgba(248,250,252,.8);
      }}
      .meta span {{
        display: block;
        color: #64748b;
        font-size: 13px;
        font-weight: 800;
      }}
      .meta strong {{
        display: block;
        margin-top: 8px;
        color: #172033;
      }}
      @media (max-width: 720px) {{
        .meta {{
          grid-template-columns: 1fr;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <div class="eyebrow">STAFF PORTAL</div>
      <h1>AI智慧客服工作人員入口</h1>
      <p>
        後端服務已正常運行。工作人員可從這裡進入管理後台，查看瀏覽統計、
        問答紀錄、使用者回饋、無法回答問題，並管理知識庫。
      </p>
      <div class="actions">
        <a href="{admin_url}">進入管理後台</a>
        <a class="secondary" href="{public_url}">前往使用者網站</a>
        <a class="secondary" href="/docs">API 文件</a>
      </div>
      <section class="meta" aria-label="服務狀態">
        <div><span>API</span><strong>Online</strong></div>
        <div><span>Knowledge Chunks</span><strong>{len(chunks)}</strong></div>
        <div><span>LLM</span><strong>{"Enabled" if llm_enabled() else "Disabled"}</strong></div>
      </section>
    </main>
  </body>
</html>
"""


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
    conversation = [
        {
            "role": item.get("role", "user"),
            "text": str(item.get("text", ""))[:500],
        }
        for item in payload.history[-8:]
        if isinstance(item, dict) and item.get("text")
    ]

    if is_casual_chat(question):
        llm_answer = generate_llm_answer(
            question,
            "casual",
            [],
            [],
            full_knowledge="\n".join(chunk.content for chunk in chunks),
            conversation=conversation,
        )
        response = {
            "answer": llm_answer or casual_fallback_answer(question),
            "category": "casual",
            "category_label": "\u4e00\u822c\u804a\u5929",
            "sources": [],
            "notice": "\u82e5\u8981\u67e5\u8ab2\u7a0b\u3001\u5831\u540d\u3001\u88dc\u52a9\u6216\u7504\u8a66\u8cc7\u8a0a\uff0c\u6211\u6703\u4ee5\u77e5\u8b58\u5eab\u8207\u5b98\u65b9\u516c\u544a\u70ba\u4f9d\u64da\u5354\u52a9\u4f60\u3002",
            "matched": True,
            "answer_style": "chat",
            "llm_used": bool(llm_answer),
        }
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
                "visitor_id": payload.visitor_id,
            },
        )
        response["conversation_id"] = saved["id"]
        return response

    category = classify_question(question)
    matches = retriever.search(question, top_k=5, category=category)
    matches = include_both_terms(question, category, matches)
    fallback_text = "\n".join(chunk.content for chunk in chunks)
    response = build_answer(question, category, matches, fallback_text=fallback_text)
    asks_deadline = category == "registration" and any(
        keyword in question for keyword in ["\u622a\u6b62", "\u5831\u540d\u622a\u6b62", "\u4ec0\u9ebc\u6642\u5019"]
    )
    asks_hard_fact = asks_deadline or any(
        keyword in question
        for keyword in [
            "\u96fb\u8a71",
            "\u806f\u7d61",
            "LINE",
            "line",
            "\u5730\u9ede",
            "\u8a13\u7df4\u5730\u9ede",
            "\u4e0a\u8ab2",
            "\u6642\u6578",
            "\u7e3d\u6642\u6578",
            "\u591a\u5c11\u5c0f\u6642",
        ]
    )
    use_llm = category != "on-job-training" and not asks_hard_fact
    llm_answer = (
        generate_llm_answer(
            question,
            category,
            matches,
            response["sources"],
            full_knowledge=fallback_text,
            conversation=conversation,
        )
        if use_llm
        else None
    )
    response["llm_used"] = bool(llm_answer)
    if llm_answer:
        response["answer"] = llm_answer
        response["matched"] = True
        if not response["sources"]:
            response["sources"] = ["整合知識庫"]
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
            "visitor_id": payload.visitor_id,
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


@app.get("/api/chat-history")
def public_chat_history(limit: int = 30) -> dict:
    safe_limit = min(max(limit, 1), 100)
    items = []
    for row in store.list("chat_logs", limit=safe_limit):
        items.append(
            {
                "id": row.get("id"),
                "created_at": row.get("created_at"),
                "question": row.get("question"),
                "category_label": row.get("category_label"),
                "matched": row.get("matched"),
            }
        )
    return {"items": items}


@app.post("/api/feedback")
def feedback(payload: FeedbackRequest) -> dict:
    saved = store.append(
        "feedback",
        {
            "question": payload.question,
            "answer": payload.answer,
            "helpful": payload.helpful,
            "comment": payload.comment,
            "visitor_id": payload.visitor_id,
            "conversation_id": payload.conversation_id,
        },
    )
    return {
        "status": "received",
        "id": saved["id"],
        "message": "Feedback saved.",
    }


@app.post("/api/analytics/visit")
def analytics_visit(payload: VisitRequest) -> dict:
    saved = store.append(
        "visits",
        {
            "visitor_id": payload.visitor_id,
            "page": payload.page,
            "path": payload.path,
            "referrer": payload.referrer,
        },
    )
    return {
        "status": "tracked",
        "id": saved["id"],
        "visitor_visit_count": store.visitor_visit_count(payload.visitor_id),
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


@app.get("/api/admin/visits")
def admin_visits(limit: int = 50, _: None = Depends(require_admin)) -> dict:
    return {"items": store.list("visits", limit=limit)}


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
