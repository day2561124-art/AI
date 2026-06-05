from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
import re


def normalize_question(text: str) -> str:
    return re.sub(r"[\W_]+", "", text.lower(), flags=re.UNICODE)


def similarity(left: str, right: str) -> float:
    left_key = normalize_question(left)
    right_key = normalize_question(right)
    if not left_key or not right_key:
        return 0.0
    if left_key == right_key:
        return 1.0
    return SequenceMatcher(None, left_key, right_key).ratio()


def find_cag_answer(question: str, category: str, feedback_rows: list[dict]) -> dict | None:
    candidates: list[tuple[float, dict]] = []
    for row in feedback_rows:
        if row.get("helpful") is not True:
            continue
        answer = str(row.get("answer") or "").strip()
        source_question = str(row.get("question") or "").strip()
        if not answer or not source_question:
            continue
        score = similarity(question, source_question)
        if score >= 0.92:
            candidates.append((score, row))

    if not candidates:
        return None

    score, row = sorted(candidates, key=lambda item: item[0], reverse=True)[0]
    return {
        "answer": row["answer"],
        "category": category,
        "category_label": "已驗證快取",
        "sources": ["CAG：使用者回饋確認答案"],
        "notice": "此答案來自曾被標記為有幫助的相似問答；最新資訊仍以官方公告與承辦單位回覆為準。",
        "matched": True,
        "answer_style": "cag",
        "llm_used": False,
        "answer_mode": "CAG",
        "cag_score": round(score, 3),
    }


def build_feedback_context(question: str, feedback_rows: list[dict], limit: int = 4) -> str:
    scored: list[tuple[float, dict]] = []
    for row in feedback_rows:
        source_question = str(row.get("question") or "")
        score = similarity(question, source_question)
        if score >= 0.45:
            scored.append((score, row))

    if not scored:
        return ""

    lines: list[str] = []
    for score, row in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]:
        label = "有幫助" if row.get("helpful") is True else "沒幫助"
        lines.append(
            f"- {label}範例（相似度 {score:.2f}）：問題「{row.get('question', '')}」；回答「{str(row.get('answer', ''))[:160]}」"
        )
    return "\n".join(lines)


def build_visitor_memory(visitor_id: str | None, chat_rows: list[dict], limit: int = 6) -> dict:
    if not visitor_id:
        return {"summary": "", "items": []}

    user_rows = [row for row in chat_rows if row.get("visitor_id") == visitor_id]
    recent = list(reversed(user_rows))[:limit]
    if not recent:
        return {"summary": "", "items": []}

    category_counts = Counter(row.get("category_label") or row.get("category") or "一般" for row in user_rows)
    topics = "、".join(label for label, _ in category_counts.most_common(3))
    items = [
        {
            "role": "user",
            "text": str(row.get("question") or "")[:240],
        }
        for row in reversed(recent)
    ]
    return {
        "summary": f"這位使用者近期常問：{topics}。最近共有 {len(user_rows)} 次問答紀錄。",
        "items": items,
    }
