import re


CATEGORY_LABELS = {
    "course": "\u8ab2\u7a0b\u8cc7\u8a0a",
    "registration": "\u5831\u540d\u65b9\u5f0f",
    "subsidy": "\u88dc\u52a9\u8cbb\u7528",
    "exam": "\u7504\u8a66\u8cc7\u8a0a",
    "contact": "\u806f\u7d61\u65b9\u5f0f",
    "on-job-training": "\u975e\u672c\u8ab2\u7a0b\u7bc4\u570d",
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
    "on-job-training": "\u975e\u672c\u8ab2\u7a0b\u7bc4\u570d",
    "pre-job-training": "\u8077\u524d\u8a13\u7df4",
    "faq": "FAQ",
    "admission": "\u9304\u53d6\u8207\u8cc7\u683c",
    "eligibility": "\u5831\u540d\u8cc7\u683c",
}


def classify_question(question: str) -> str:
    rules = [
        ("\u8ab0\u53ef\u4ee5\u5831\u540d", "eligibility"),
        ("\u5831\u540d\u8cc7\u683c", "eligibility"),
        ("\u53c3\u8a13\u8cc7\u683c", "eligibility"),
        ("\u53c3\u8a13\u5c0d\u8c61", "eligibility"),
        ("\u5c0d\u8c61", "eligibility"),
        ("\u5831\u540d\u9023\u7d50", "registration"),
        ("\u5831\u540d\u7db2\u5740", "registration"),
        ("\u5831\u540d", "registration"),
        ("\u622a\u6b62", "registration"),
        ("\u5e73\u53f0", "registration"),
        ("\u9023\u7d50", "registration"),
        ("\u7db2\u5740", "registration"),
        ("\u8ab2\u7a0b\u4ee3\u78bc", "registration"),
        ("\u67e5\u8a62", "registration"),
        ("\u53f0\u7063\u5c31\u696d\u901a", "registration"),
        ("\u4e0a\u8ab2", "course"),
        ("\u5730\u9ede", "course"),
        ("\u8a13\u7df4\u5730\u9ede", "course"),
        ("\u6642\u6578", "course"),
        ("\u7e3d\u6642\u6578", "course"),
        ("\u5728\u8077", "on-job-training"),
        ("\u8077\u524d", "pre-job-training"),
        ("\u88dc\u52a9", "subsidy"),
        ("\u514d\u5b78\u8cbb", "subsidy"),
        ("\u734e\u52f5\u91d1", "subsidy"),
        ("\u6d25\u8cbc", "subsidy"),
        ("\u4e2d\u9ad8\u9f61", "subsidy"),
        ("45 \u6b72", "subsidy"),
        ("45\u6b72", "subsidy"),
        ("\u7279\u5b9a\u5c0d\u8c61", "subsidy"),
        ("8000", "subsidy"),
        ("8,000", "subsidy"),
        ("\u9818", "subsidy"),
        ("\u7504\u8a66", "exam"),
        ("\u8003\u8a66", "exam"),
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
    if category == "on-job-training":
        return (
            "\u672c\u7cfb\u7d71\u805a\u7126\u300cAI\u667a\u6167\u61c9\u7528\u7522\u696d\u4eba\u624d\u57f9\u8a13\u73ed\u300d"
            "\u8077\u524d\u8a13\u7df4\u8cc7\u8a0a\uff0c\u4e0d\u63d0\u4f9b\u5728\u8077\u8a13\u7df4\u6216\u5728\u8077\u88dc\u52a9\u7684\u7d30\u7bc0\u89e3\u7b54\u3002"
        )
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
    topic_key = category if category and category not in {"latest"} else metadata.get("topic", "general")
    topic = TOPIC_LABELS.get(topic_key, topic_key)
    parts = [topic]
    if metadata.get("year"):
        parts.append(f"{metadata['year']} \u5e74")
    if metadata.get("term") == "term-01":
        parts.append("\u7b2c 01 \u671f")
    if metadata.get("term") == "term-02":
        parts.append("\u7b2c 02 \u671f")
    return " / ".join(parts)


def excerpt(content: str, limit: int = 420) -> str:
    compact = " ".join(line.strip() for line in content.splitlines() if line.strip())
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def brief_answer(category: str, matches: list[dict]) -> str:
    label = CATEGORY_LABELS.get(category, category)
    if category == "on-job-training":
        return "\u9019\u9580\u8ab2\u7a0b\u662f\u8077\u524d\u8a13\u7df4\u5594 \U0001f60a\uff0c\u4e0d\u6574\u7406\u5728\u8077\u8a13\u7df4\u6216\u5728\u8077\u88dc\u52a9\u8cc7\u8a0a\u3002\u8acb\u6539\u8a62\u554f\u5831\u540d\u8cc7\u683c\u3001\u8077\u524d\u88dc\u52a9\u3001\u9752\u5e74\u734e\u52f5\u91d1\u6216\u8ab2\u7a0b\u5167\u5bb9\u3002"
    if category == "latest":
        return "\u6211\u53ef\u4ee5\u5e6b\u4f60\u67e5\u5df2\u6574\u7406\u7684\u68af\u6b21\u8cc7\u8a0a \u2728\uff0c\u4f46\u662f\u5426\u4ecd\u70ba\u6700\u65b0\u6216\u4ecd\u53ef\u5831\u540d\uff0c\u5fc5\u9808\u4ee5\u5b98\u65b9\u5e73\u53f0\u70ba\u6e96\u3002"
    if category in {"subsidy", "admission", "eligibility"}:
        return f"\u6211\u5e6b\u4f60\u6574\u7406\u4e00\u4e0b \U0001f60a\uff1a\u9019\u500b\u554f\u984c\u5c6c\u65bc\u300c{label}\u300d\uff1b\u7cfb\u7d71\u53ea\u80fd\u8aaa\u660e\u53ef\u80fd\u689d\u4ef6\u8207\u7533\u8acb\u65b9\u5411\uff0c\u4e0d\u80fd\u4fdd\u8b49\u4e00\u5b9a\u901a\u904e\u6216\u9304\u53d6\u3002"
    return f"\u6211\u5e6b\u4f60\u627e\u5230\u300c{label}\u300d\u7684\u76f8\u95dc\u8cc7\u8a0a\u4e86 \U0001f60a"


def unique_sources(matches: list[dict], category: str) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()
    for match in matches:
        source = source_label(match, category)
        if source not in seen:
            sources.append(source)
            seen.add(source)
    term_sources = [source for source in sources if "\u5e74" in source]
    if len(term_sources) >= 2:
        return term_sources
    return sources


def has_any(question: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in question.lower() for keyword in keywords)


def asks_specific_term(question: str) -> bool:
    return has_any(question, ["114", "115", "\u7b2c01", "\u7b2c 01", "\u7b2c02", "\u7b2c 02"])


def fact_answer(text: str, question: str, category: str) -> str | None:
    if has_any(question, ["\u4e0a\u8ab2", "\u5730\u9ede", "\u8a13\u7df4\u5730\u9ede"]):
        location_matches = re.findall(r"(?:^|\n)-?\s*\u8a13\u7df4\u5730\u9ede[^\uff1a:]*[\uff1a:]\s*([^\n\u3002]+)", text)
        for location in location_matches:
            location = location.strip()
            if "\u6821\u5340" in location or "\u8857" in location:
                return f"\u4e0a\u8ab2\u5730\u9ede\u70ba{location}\u3002"
        if location_matches:
            return f"\u4e0a\u8ab2\u5730\u9ede\u70ba{location_matches[0].strip()}\u3002"

    if has_any(question, ["\u96fb\u8a71", "\u806f\u7d61", "\u6d3d\u8a62"]):
        phone_match = re.search(r"0\d{1,2}-?\d{3}-?\d{4}", text)
        if phone_match:
            return f"\u6d3d\u8a62\u96fb\u8a71\u70ba {phone_match.group(0)}\u3002"

    if has_any(question, ["LINE", "line", "\u5b98\u65b9 line"]):
        line_match = re.search(r"@[\w\d]+", text)
        if line_match:
            return f"\u5b98\u65b9 LINE \u70ba {line_match.group(0)}\u3002"

    if has_any(question, ["\u6642\u6578", "\u7e3d\u6642\u6578", "\u591a\u5c11\u5c0f\u6642"]):
        hours_match = re.search(r"(\d{2,4})\s*\u5c0f\u6642", text)
        if hours_match:
            return f"\u8ab2\u7a0b\u7e3d\u6642\u6578\u70ba {hours_match.group(1)} \u5c0f\u6642\u3002"

    if category == "registration" and has_any(question, ["\u622a\u6b62", "\u5831\u540d\u622a\u6b62", "\u4ec0\u9ebc\u6642\u5019"]):
        deadline_match = re.search(r"\u5831\u540d\u622a\u6b62[^\d]*(\d{3}/\d{2}/\d{2})\s*(\d{1,2}:\d{2})?", text)
        if deadline_match:
            date = deadline_match.group(1)
            time = deadline_match.group(2) or ""
            return f"115 \u5e74\u7b2c 02 \u671f\u7684\u5831\u540d\u622a\u6b62\u6642\u9593\u662f {date}{f' {time}' if time else ''}\u3002"

    if category == "registration" and has_any(question, ["\u5831\u540d\u9023\u7d50", "\u5831\u540d\u7db2\u5740", "\u600e\u9ebc\u5831\u540d", "\u5831\u540d"]):
        if not asks_specific_term(question):
            return (
                "\u5831\u540d\u8cc7\u8a0a\u9700\u5206\u671f\u5225\u67e5\u770b\uff1a"
                "115 \u5e74\u7b2c 02 \u671f\u53ef\u4f7f\u7528\u7acb\u5373\u5831\u540d\u9801\u9762 https://its.taiwanjobs.gov.tw/Course/Detail?ID=161756\uff1b"
                "114 \u5e74\u7b2c 01 \u671f\u516c\u544a\u63d0\u4f9b\u53f0\u7063\u5c31\u696d\u901a\u5831\u540d\u7db2\u5740 https://reurl.cc/eVd7bQ \u8207\u8ab2\u7a0b\u4ee3\u78bc 159386\u3002"
            )
        url_match = re.search(r"https://its\.taiwanjobs\.gov\.tw/Course/Detail\?ID=\d+", text)
        if url_match:
            return f"\u5831\u540d\u9801\u9762\u70ba {url_match.group(0)}\u3002"

    if category == "subsidy" and has_any(question, ["8000", "8,000", "\u734e\u52f5\u91d1"]):
        return "\u77e5\u8b58\u5eab\u63d0\u5230\uff0c15-29 \u6b72\u9752\u5e74\u7b26\u5408\u8cc7\u683c\u8005\u53ef\u7533\u8acb\u6bcf\u6708\u65b0\u81fa\u5e63 8,000 \u5143\u5b78\u7fd2\u734e\u52f5\u91d1\uff1b\u5be6\u969b\u8cc7\u683c\u8207\u6838\u5b9a\u4ecd\u4ee5\u5b98\u65b9\u5be9\u6838\u70ba\u6e96\u3002"

    if category == "eligibility" and has_any(question, ["\u8ab0", "\u8cc7\u683c", "\u5c0d\u8c61", "\u53ef\u4ee5\u5831\u540d", "\u53ef\u4ee5\u53c3\u52a0"]):
        if not asks_specific_term(question):
            return (
                "\u53c3\u8a13\u8cc7\u683c\u9700\u5206\u671f\u5225\u770b\uff1a"
                "114 \u5e74\u7b2c 01 \u671f\u516c\u544a\u5c0d\u8c61\u5305\u542b\u61c9\u5c46\u7562\u696d\u751f\u3001\u5931\u696d\u8005\u3001\u6b32\u8f49\u8077 AI \u7522\u696d\u4e4b\u5f85\u696d\u8005\u7b49\uff1b"
                "115 \u5e74\u7b2c 02 \u671f\u516c\u544a\u63d0\u5230\u5e74\u6eff 15 \u6b72\u4ee5\u4e0a\u5931\u696d\u8005\u7b26\u5408\u653f\u5e9c\u88dc\u52a9\u8cc7\u683c\u3002"
            )

    if category == "subsidy" and has_any(question, ["\u4e2d\u9ad8\u9f61", "45 \u6b72", "45\u6b72", "\u7279\u5b9a\u5c0d\u8c61"]):
        return "\u4e2d\u9ad8\u9f61\u8005\u5c6c\u65bc\u53ef\u80fd\u9069\u7528\u8f03\u9ad8\u88dc\u52a9\u7684\u7279\u5b9a\u5c0d\u8c61\uff1b\u77e5\u8b58\u5eab\u63d0\u5230 45 \u6b72\u4ee5\u4e0a\u4e2d\u9ad8\u9f61\u8005\u53ef\u80fd\u88dc\u52a9 100%\uff0c\u5be6\u969b\u8cc7\u683c\u8207\u88dc\u52a9\u6bd4\u4f8b\u4ecd\u4ee5\u5b98\u65b9\u5be9\u6838\u70ba\u6e96\u3002"

    if category == "subsidy" and has_any(question, ["\u514d\u5b78\u8cbb", "\u5168\u984d", "\u88dc\u52a9"]):
        if not asks_specific_term(question):
            return (
                "\u88dc\u52a9\u8cc7\u8a0a\u9700\u5206\u671f\u5225\u770b\uff1a"
                "115 \u5e74\u7b2c 02 \u671f\u516c\u544a\u63d0\u5230\u7b26\u5408\u8cc7\u683c\u8005\u53ef\u5168\u984d\u514d\u5b78\u8cbb\uff1b"
                "114 \u5e74\u7b2c 01 \u671f\u516c\u544a\u63d0\u5230\u653f\u5e9c\u88dc\u52a9\u5b78\u8cbb 80% \u81f3 100%\uff0c\u5b78\u54e1\u81ea\u4ed8\u7d04 0% \u81f3 20%\u3002"
            )
        if "\u5168\u984d\u514d\u5b78\u8cbb" in text:
            return "\u7b2c 02 \u671f\u516c\u544a\u63d0\u5230\u7b26\u5408\u8cc7\u683c\u8005\u53ef\u5168\u984d\u514d\u5b78\u8cbb\uff1b\u5be6\u969b\u88dc\u52a9\u7d50\u679c\u4ecd\u4ee5\u5b98\u65b9\u5be9\u6838\u70ba\u6e96\u3002"
        return "\u88dc\u52a9\u8cc7\u683c\u8207\u91d1\u984d\u9700\u4f9d\u5b98\u65b9\u5be9\u6838\u8a8d\u5b9a\uff0c\u7cfb\u7d71\u4e0d\u80fd\u4fdd\u8b49\u4e00\u5b9a\u901a\u904e\u6216\u5168\u984d\u88dc\u52a9\u3002"

    if category == "exam" and has_any(question, ["\u7504\u8a66", "\u8003\u8a66"]):
        exam_date = re.search(r"\u7504\u8a66\u65e5\u671f[^\uff1a:]*[\uff1a:]\s*([^\n\u3002]+)", text)
        exam_scope = re.search(r"\u8a66\u984c\u7bc4\u570d[^\uff1a:]*[\uff1a:]\s*([^\n\u3002]+)", text)
        if exam_date or exam_scope:
            parts = []
            if exam_date:
                parts.append(f"\u7504\u8a66\u65e5\u671f\u70ba{exam_date.group(1).strip()}")
            if exam_scope:
                parts.append(f"\u8a66\u984c\u7bc4\u570d\u70ba{exam_scope.group(1).strip()}")
            return "\uff1b".join(parts) + "\u3002"

    return None


def direct_answer(question: str, category: str, matches: list[dict], fallback_text: str = "") -> str | None:
    if category == "on-job-training":
        return (
            "\u7c21\u77ed\u56de\u7b54\uff1a\n"
            "\u9019\u9580\u8ab2\u7a0b\u662f\u8077\u524d\u8a13\u7df4\u5594 \U0001f60a\uff0c\u4e0d\u63d0\u4f9b\u5728\u8077\u88dc\u52a9\u6216\u5728\u8077\u8a13\u7df4\u7684\u7d30\u7bc0\u89e3\u7b54\u3002"
            "\u82e5\u8981\u67e5\u672c\u8ab2\u7a0b\uff0c\u53ef\u8a62\u554f\u300c\u8077\u524d\u88dc\u52a9\u8cc7\u683c\u300d\u3001\u300c\u9752\u5e74\u734e\u52f5\u91d1\u300d\u3001\u300c\u5831\u540d\u8cc7\u683c\u300d\u6216\u300c\u5831\u540d\u65b9\u5f0f\u300d\u3002"
            "\n\n\u6ce8\u610f\u4e8b\u9805\uff1a\n"
            + official_notice(category)
        )

    text = "\n".join(match["content"] for match in matches[:4])
    if fallback_text:
        text = text + "\n" + fallback_text
    fact = fact_answer(text, question, category)
    if fact:
        return (
            "\u7c21\u77ed\u56de\u7b54\uff1a\n"
            "\u6211\u5e6b\u4f60\u67e5\u5230\u4e86 \U0001f60a "
            + fact
            + "\n\n\u6ce8\u610f\u4e8b\u9805\uff1a\n"
            + official_notice(category)
        )
    return None


def build_answer(question: str, category: str, matches: list[dict], fallback_text: str = "") -> dict:
    sources = unique_sources(matches, category) if matches else [CATEGORY_LABELS.get(category, category)]
    direct = direct_answer(question, category, matches, fallback_text=fallback_text)
    if direct:
        if category == "on-job-training":
            sources = ["職前訓練定位"]
        return {
            "answer": direct,
            "category": category,
            "category_label": CATEGORY_LABELS.get(category, category),
            "sources": sources,
            "notice": official_notice(category),
            "matched": True,
            "answer_style": "direct",
        }

    if not matches:
        answer = (
            "\u7c21\u77ed\u56de\u7b54\uff1a\n"
            "\u4e0d\u597d\u610f\u601d\uff0c\u76ee\u524d\u77e5\u8b58\u5eab\u6c92\u6709\u660e\u78ba\u8cc7\u6599 \U0001f64f\n\n"
            "\u8a73\u7d30\u8aaa\u660e\uff1a\n"
            "\u5efa\u8b70\u67e5\u8a62\u53f0\u7063\u5c31\u696d\u901a\u3001\u8077\u524d\u8a13\u7df4\u7db2\u6216\u6d3d\u8a62\u627f\u8fa6\u55ae\u4f4d\u3002\u570b\u7acb\u81fa\u5357\u5927\u5b78 AI \u64da\u9ede\u96fb\u8a71\uff1a06-213-0019\u3002\n\n"
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

    detail_items = [f"- {excerpt(match['content'], limit=180)}" for match in matches[:2]]
    answer = (
        "\u7c21\u77ed\u56de\u7b54\uff1a\n"
        + brief_answer(category, matches)
        + "\n\n\u91cd\u9ede\u8cc7\u8a0a\uff1a\n"
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
