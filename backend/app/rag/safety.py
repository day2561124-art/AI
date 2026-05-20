CATEGORY_LABELS = {
    "course": "\u8ab2\u7a0b\u8cc7\u8a0a",
    "registration": "\u5831\u540d\u65b9\u5f0f",
    "subsidy": "\u88dc\u52a9\u8cbb\u7528",
    "exam": "\u7504\u8a66\u8cc7\u8a0a",
    "contact": "\u806f\u7d61\u65b9\u5f0f",
    "on-job-training": "\u5728\u8077\u8a13\u7df4",
    "pre-job-training": "\u8077\u524d\u8a13\u7df4",
    "latest": "\u6700\u65b0\u8cc7\u8a0a",
    "admission": "\u9304\u53d6\u8207\u8cc7\u683c",
    "eligibility": "\u5831\u540d\u8cc7\u683c",
}


TOPIC_LABELS = {
    "general": "\u4e00\u822c\u8cc7\u8a0a",
    "course": "\u8ab2\u7a0b\u8cc7\u8a0a",
    "registration": "\u5831\u540d\u65b9\u5f0f",
    "subsidy": "\u88dc\u52a9\u8cbb\u7528",
    "exam": "\u7504\u8a66\u8cc7\u8a0a",
    "contact": "\u806f\u7d61\u65b9\u5f0f",
    "on-job-training": "\u5728\u8077\u8a13\u7df4",
    "pre-job-training": "\u8077\u524d\u8a13\u7df4",
    "faq": "FAQ",
}


def classify_question(question: str) -> str:
    rules = [
        ("\u5728\u8077", "on-job-training"),
        ("\u8077\u524d", "pre-job-training"),
        ("\u88dc\u52a9", "subsidy"),
        ("\u514d\u5b78\u8cbb", "subsidy"),
        ("\u734e\u52f5\u91d1", "subsidy"),
        ("\u6d25\u8cbc", "subsidy"),
        ("8000", "subsidy"),
        ("8,000", "subsidy"),
        ("\u9818", "subsidy"),
        ("\u7504\u8a66", "exam"),
        ("\u8003\u8a66", "exam"),
        ("\u5831\u540d", "registration"),
        ("\u622a\u6b62", "registration"),
        ("\u5e73\u53f0", "registration"),
        ("\u67e5\u8a62", "registration"),
        ("\u53f0\u7063\u5c31\u696d\u901a", "registration"),
        ("\u96fb\u8a71", "contact"),
        ("\u806f\u7d61", "contact"),
        ("LINE", "contact"),
        ("line", "contact"),
        ("\u6700\u65b0", "latest"),
        ("\u9084\u80fd\u5831", "latest"),
        ("\u9304\u53d6", "admission"),
        ("\u8cc7\u683c", "eligibility"),
        ("\u53ef\u4ee5\u53c3\u52a0", "eligibility"),
    ]
    for keyword, category in rules:
        if keyword in question:
            return category
    return "course"


def official_notice(category: str) -> str:
    base = "\u5be6\u969b\u8cc7\u8a0a\u4ecd\u4ee5\u5b98\u65b9\u6700\u65b0\u516c\u544a\u8207\u627f\u8fa6\u55ae\u4f4d\u56de\u8986\u70ba\u6e96\u3002"
    if category in {"subsidy", "admission", "eligibility"}:
        return (
            base
            + " \u88dc\u52a9\u8cc7\u683c\u3001\u6d25\u8cbc\u3001\u5b78\u7fd2\u734e\u52f5\u91d1\u8207\u9304\u53d6\u7d50\u679c\u9700\u7531\u5b98\u65b9\u6216\u627f\u8fa6\u55ae\u4f4d\u8a8d\u5b9a\uff0c\u7cfb\u7d71\u4e0d\u53ef\u4fdd\u8b49\u4e00\u5b9a\u901a\u904e\u3002"
        )
    if category == "latest":
        return (
            base
            + " \u6700\u65b0\u68af\u6b21\u3001\u622a\u6b62\u65e5\u671f\u8207\u662f\u5426\u4ecd\u958b\u653e\u5831\u540d\uff0c\u8acb\u67e5\u8a62\u5b98\u65b9\u5e73\u53f0\u6216\u6d3d\u8a62\u627f\u8fa6\u55ae\u4f4d\u3002"
        )
    return base


def source_label(match: dict, category: str | None = None) -> str:
    metadata = match["metadata"]
    topic_key = category if category and category not in {"course", "latest"} else metadata.get("topic", "general")
    topic = TOPIC_LABELS.get(topic_key, topic_key)
    parts = [topic]
    if metadata.get("year"):
        parts.append(f"{metadata['year']} \u5e74")
    if metadata.get("term") == "term-01":
        parts.append("\u7b2c 01 \u671f")
    if metadata.get("term") == "term-02":
        parts.append("\u7b2c 02 \u671f")
    parts.append(f"chunk {metadata.get('chunk_index', match['id'])}")
    return " / ".join(parts)


def excerpt(content: str, limit: int = 420) -> str:
    compact = " ".join(line.strip() for line in content.splitlines() if line.strip())
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def brief_answer(category: str, matches: list[dict]) -> str:
    label = CATEGORY_LABELS.get(category, category)
    if category == "latest":
        return "\u77e5\u8b58\u5eab\u53ef\u63d0\u4f9b\u5df2\u6574\u7406\u7684\u68af\u6b21\u8cc7\u8a0a\uff0c\u4f46\u662f\u5426\u4ecd\u70ba\u6700\u65b0\u6216\u4ecd\u53ef\u5831\u540d\uff0c\u5fc5\u9808\u4ee5\u5b98\u65b9\u5e73\u53f0\u70ba\u6e96\u3002"
    if category in {"subsidy", "admission", "eligibility"}:
        return f"\u6839\u64da\u77e5\u8b58\u5eab\uff0c\u6b64\u554f\u984c\u5c6c\u65bc\u300c{label}\u300d\uff1b\u7cfb\u7d71\u53ea\u80fd\u8aaa\u660e\u53ef\u80fd\u689d\u4ef6\u8207\u7533\u8acb\u65b9\u5411\uff0c\u4e0d\u80fd\u4fdd\u8b49\u4e00\u5b9a\u901a\u904e\u6216\u9304\u53d6\u3002"
    return f"\u6839\u64da\u77e5\u8b58\u5eab\uff0c\u4ee5\u4e0b\u662f\u300c{label}\u300d\u7684\u76f8\u95dc\u8cc7\u8a0a\u3002"


def build_answer(question: str, category: str, matches: list[dict]) -> dict:
    if not matches:
        answer = (
            "\u7c21\u77ed\u56de\u7b54\uff1a\n"
            "\u76ee\u524d\u77e5\u8b58\u5eab\u6c92\u6709\u660e\u78ba\u8cc7\u6599\u3002\n\n"
            "\u8a73\u7d30\u8aaa\u660e\uff1a\n"
            "\u5efa\u8b70\u67e5\u8a62\u53f0\u7063\u5c31\u696d\u901a\u3001\u8077\u524d\u8a13\u7df4\u7db2\u3001\u5728\u8077\u8a13\u7df4\u7db2\u6216\u6d3d\u8a62\u627f\u8fa6\u55ae\u4f4d\u3002\u570b\u7acb\u81fa\u5357\u5927\u5b78 AI \u64da\u9ede\u96fb\u8a71\uff1a06-213-0019\u3002\n\n"
            "\u4f86\u6e90\u4f9d\u64da\uff1a\n"
            "\u672a\u6aa2\u7d22\u5230\u8db3\u5920\u660e\u78ba\u7684\u77e5\u8b58\u5eab\u6bb5\u843d\u3002"
        )
        return {
            "answer": answer,
            "category": category,
            "category_label": CATEGORY_LABELS.get(category, category),
            "sources": [],
            "notice": official_notice(category),
            "matched": False,
        }

    sources = [source_label(match, category) for match in matches]
    detail_items = [f"{index}. {excerpt(match['content'])}" for index, match in enumerate(matches[:3], start=1)]
    answer = (
        "\u7c21\u77ed\u56de\u7b54\uff1a\n"
        + brief_answer(category, matches)
        + "\n\n\u8a73\u7d30\u8aaa\u660e\uff1a\n"
        + "\n\n".join(detail_items)
        + "\n\n\u4f86\u6e90\u4f9d\u64da\uff1a\n"
        + "\n".join(f"- {source}" for source in sources)
        + "\n\n\u6ce8\u610f\u4e8b\u9805\uff1a\n"
        + official_notice(category)
    )

    return {
        "answer": answer,
        "category": category,
        "category_label": CATEGORY_LABELS.get(category, category),
        "sources": sources,
        "notice": official_notice(category),
        "matched": True,
    }
