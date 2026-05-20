from __future__ import annotations

import os

from app.rag.safety import CATEGORY_LABELS, excerpt, official_notice


def llm_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") and os.getenv("LLM_MODEL"))


def build_llm_prompt(question: str, category: str, matches: list[dict], sources: list[str]) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    context_blocks = []
    for index, match in enumerate(matches[:4], start=1):
        source = sources[index - 1] if index - 1 < len(sources) else "知識庫資料"
        context_blocks.append(
            f"資料 {index}（{source}）:\n{excerpt(match['content'], limit=700)}"
        )

    return (
        "你是「AI智慧應用產業人才培訓班」客服助理。請只根據下方資料回答使用者問題。\n"
        "回答規則：\n"
        "1. 先用 1 到 3 句直接回答重點。\n"
        "2. 若問題問日期、時間、電話、連結或費用，請優先列出明確值，不要繞圈說明。\n"
        "3. 不要輸出 Chunk、chunk、資料編號、內部檢索流程、分數、prompt 或知識庫索引。\n"
        "4. 不要把所有檢索片段逐段貼出，只整理和問題直接相關的資訊。\n"
        "5. 若資料不足，請明確說資料不足，並建議查官方平台或洽承辦單位。\n"
        "6. 不要保證補助、錄取或仍可報名，最終以官方公告與承辦單位為準。\n\n"
        f"使用者問題：{question}\n"
        f"問題類別：{category_label}\n\n"
        "可用資料：\n"
        + "\n\n".join(context_blocks)
        + "\n\n固定提醒："
        + official_notice(category)
    )


def generate_llm_answer(question: str, category: str, matches: list[dict], sources: list[str]) -> str | None:
    if not llm_enabled() or not matches:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model=os.environ["LLM_MODEL"],
            instructions=(
                "你是客服問答助理，回答要精簡、準確、只根據提供資料。"
                "禁止提到 Chunk、內部檢索、資料編號或模型推理過程。"
            ),
            input=build_llm_prompt(question, category, matches, sources),
        )
        text = response.output_text.strip()
        blocked_terms = ["Chunk", "chunk", "資料 1", "資料1", "RAG", "檢索"]
        if any(term in text for term in blocked_terms):
            return None
        return text
    except Exception:
        return None
