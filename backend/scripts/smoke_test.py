from pathlib import Path

from app.rag.loader import load_knowledge_base
from app.rag.retriever import LocalRetriever
from app.rag.safety import build_answer, classify_question


PROJECT_DIR = Path(__file__).resolve().parents[2]


def main() -> None:
    knowledge_path = next(PROJECT_DIR.glob("*.txt"))
    chunks = load_knowledge_base(knowledge_path)
    retriever = LocalRetriever(chunks)

    questions = [
        "115 年第 02 期報名截止時間是什麼時候？",
        "114 年第 01 期甄試資訊是什麼？",
        "15-29 歲青年一定可以領 8000 元嗎？",
        "在職勞工進修補助要去哪裡查？",
        "我一定會錄取嗎？",
        "這個系統可以查詢哪些官方平台？",
    ]

    print(f"knowledge_path={knowledge_path}")
    print(f"chunk_count={len(chunks)}")

    for question in questions:
        category = classify_question(question)
        matches = retriever.search(question, top_k=5, category=category)
        answer = build_answer(question, category, matches)
        print("=" * 72)
        print(f"question={question}")
        print(f"category={answer['category']} label={answer['category_label']}")
        print(f"matched={answer['matched']} sources={len(answer['sources'])}")
        if matches:
            print(
                "top_score="
                f"{matches[0]['score']} keyword={matches[0]['keyword_score']} "
                f"vector={matches[0]['vector_score']}"
            )
        print(answer["notice"])


if __name__ == "__main__":
    main()

