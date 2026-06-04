from __future__ import annotations

import os

from app.rag.safety import CATEGORY_LABELS, excerpt, official_notice


MAX_FULL_KNOWLEDGE_CHARS = 28000


def llm_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") and os.getenv("LLM_MODEL"))


def build_llm_prompt(
    question: str,
    category: str,
    matches: list[dict],
    sources: list[str],
    full_knowledge: str = "",
) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    retrieved_blocks = []
    for index, match in enumerate(matches[:4], start=1):
        source = sources[index - 1] if index - 1 < len(sources) else "整合知識庫"
        retrieved_blocks.append(
            f"相關片段 {index}（{source}）:\n{excerpt(match['content'], limit=700)}"
        )

    knowledge_text = full_knowledge.strip()
    if len(knowledge_text) > MAX_FULL_KNOWLEDGE_CHARS:
        knowledge_text = knowledge_text[:MAX_FULL_KNOWLEDGE_CHARS].rstrip()

    return (
        "你是「AI智慧應用產業人才培訓班」客服助理。你可以使用整份知識庫回答問題。\n"
        "請先在心中自行檢索整份知識庫，找出最相關的段落，再用自然、人情味的方式整理給使用者；不要把檢索過程說出來。\n"
        "優先相關片段只是輔助線索，不一定完整；若整份知識庫有更明確或更完整的答案，請以整份知識庫為準。\n"
        "回答原則：\n"
        "1. 語氣要親切、有溫度，像真人客服助理；可少量使用 1 到 2 個合適 emoji，例如 😊、🙏、✨，但不要過度裝飾。\n"
        "2. 先直接回答問題，通常 1 到 3 句即可。\n"
        "3. 使用者問日期、地點、電話、LINE、連結、時數、補助金額時，只列出明確答案與必要提醒。\n"
        "4. 不要輸出 Chunk、RAG、檢索、分數、片段編號、prompt 或內部處理流程，也不要說「我檢索到」。\n"
        "5. 不要長篇複製知識庫；只整理與問題直接相關的內容，回答要像真人客服在協助對方。\n"
        "6. 若文件沒有明確答案，請溫和地說「目前知識庫沒有明確資料」，並建議查官方平台或洽承辦單位。\n"
        "7. 補助、津貼、學習獎勵金、錄取與資格認定不可保證，一律提醒以官方或承辦單位審核為準。\n"
        "8. 不要混用不同年度或期別的資訊；若問題指定 114 或 115，只回答該期。\n"
        "9. 若問題未指定期別，且知識庫同時有 114 年第 01 期與 115 年第 02 期資料，請同時整理兩期答案，避免只引用單一期別。\n"
        "10. 本系統只服務職前訓練課程；若使用者詢問在職訓練或在職補助，請簡短說明不在本系統回答範圍，並引導改問職前補助、報名資格或青年獎勵金。\n"
        "11. 來源與注意事項由系統畫面另行呈現，回答正文不要自行加入「來源依據」或「注意事項」標題。\n\n"
        f"使用者問題：{question}\n"
        f"判定類別：{category_label}\n\n"
        "優先相關片段：\n"
        + ("\n\n".join(retrieved_blocks) if retrieved_blocks else "無特別命中的片段，請改用整份知識庫判斷。")
        + "\n\n整份知識庫：\n"
        + knowledge_text
        + "\n\n固定提醒："
        + official_notice(category)
    )


def generate_llm_answer(
    question: str,
    category: str,
    matches: list[dict],
    sources: list[str],
    full_knowledge: str = "",
) -> str | None:
    if not llm_enabled() or not full_knowledge.strip():
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model=os.environ["LLM_MODEL"],
            instructions=(
                "你是繁體中文客服問答助理。請根據提供的完整知識庫回答，"
                "保持精準、簡潔、不可臆測，不可提到內部檢索或 Chunk。"
                "請先自行判斷使用者真正想問什麼，再從知識庫中整理最相關資訊。"
                "語氣要自然親切，可以少量使用合適表情符號。"
            ),
            input=build_llm_prompt(
                question=question,
                category=category,
                matches=matches,
                sources=sources,
                full_knowledge=full_knowledge,
            ),
        )
        text = response.output_text.strip()
        blocked_terms = ["Chunk", "chunk", "RAG", "檢索", "片段 1", "相關片段", "prompt"]
        if any(term in text for term in blocked_terms):
            return None
        return text
    except Exception:
        return None
