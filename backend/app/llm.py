from __future__ import annotations

import os

from app.rag.safety import CATEGORY_LABELS, excerpt, official_notice


def llm_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") and os.getenv("LLM_MODEL"))


def build_llm_prompt(question: str, category: str, matches: list[dict], sources: list[str]) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    context_blocks = []
    for index, match in enumerate(matches[:5], start=1):
        context_blocks.append(
            f"[來源 {index}: {sources[index - 1]}]\n{excerpt(match['content'], limit=900)}"
        )

    return (
        "你是「AI智慧應用產業人才培訓班」線上客服系統的回答助手。\n"
        "請只根據下方 RAG 檢索內容回答，不要自行補充知識庫沒有的日期、金額、課程代碼、錄取標準或補助承諾。\n\n"
        f"使用者問題：{question}\n"
        f"問題分類：{category_label}\n\n"
        "回答格式：\n"
        "1. 簡短回答：先直接回答使用者問題。\n"
        "2. 詳細說明：用條列補充條件、日期、費用、流程或限制。\n"
        "3. 來源依據：列出使用到的來源標題。\n"
        "4. 注意事項：提醒實際資訊仍以官方最新公告與承辦單位回覆為準。\n\n"
        "重要規則：\n"
        "- 補助、學習獎勵金、職訓生活津貼只能說「符合資格者可申請」，不可保證一定核定。\n"
        "- 不可保證錄取。\n"
        "- 涉及最新梯次、個人資格、補助核定或錄取結果時，必須提醒查詢官方平台或洽詢承辦單位。\n"
        "- 不可混用 114 年第 01 期與 115 年第 02 期資訊。\n"
        "- 不可把職前訓練規則套用到在職勞工進修，也不可反向套用。\n"
        "- 若檢索內容不足，請明確回答「目前知識庫沒有明確資料」。\n\n"
        "RAG 檢索內容：\n"
        + "\n\n".join(context_blocks)
        + "\n\n預設注意事項：\n"
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
                "你是一位正式、清楚、謹慎的繁體中文客服助理。"
                "請根據 RAG 來源回答，保留來源依據與注意事項，避免保證補助、錄取或最新資訊。"
            ),
            input=build_llm_prompt(question, category, matches, sources),
        )
        return response.output_text.strip()
    except Exception:
        return None
