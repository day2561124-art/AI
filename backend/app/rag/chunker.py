from dataclasses import dataclass
import re


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    title: str
    content: str
    metadata: dict[str, str]


KW_SUBSIDY = "\u88dc\u52a9"
KW_REWARD = "\u734e\u52f5\u91d1"
KW_ALLOWANCE = "\u6d25\u8cbc"
KW_EXAM = "\u7504\u8a66"
KW_REGISTER = "\u5831\u540d"
KW_PHONE = "\u96fb\u8a71"
KW_ON_JOB = "\u5728\u8077"
KW_PRE_JOB = "\u8077\u524d"


def infer_metadata(title: str, content: str, source_name: str, index: int) -> dict[str, str]:
    text = f"{title}\n{content}"
    year = ""
    term = ""
    topic = "general"

    if "114" in text or "第01" in text or "第 01" in text or "term-01" in text:
        year = "114"
        term = "term-01"
    if "115" in text or "第02" in text or "第 02" in text or "term-02" in text:
        year = "115"
        term = "term-02"

    title_topic_rules = [
        (KW_ON_JOB, "on-job-training"),
        (KW_PRE_JOB, "pre-job-training"),
    ]
    for keyword, value in title_topic_rules:
        if keyword in title:
            topic = value
            break

    topic_rules = [
        (KW_SUBSIDY, "subsidy"),
        (KW_REWARD, "subsidy"),
        (KW_ALLOWANCE, "subsidy"),
        (KW_EXAM, "exam"),
        (KW_REGISTER, "registration"),
        (KW_PHONE, "contact"),
        ("LINE", "contact"),
        ("FAQ", "faq"),
    ]
    if topic == "general":
        for keyword, value in topic_rules:
            if keyword in text:
                topic = value
                break

    return {
        "source": source_name,
        "chunk_index": str(index),
        "year": year,
        "term": term,
        "topic": topic,
        "requires_official_confirmation": "true",
    }


def chunk_text(text: str, source_name: str) -> list[KnowledgeChunk]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    parts = re.split(r"\n={8,}\n|\n#{1,4}\s+", cleaned)
    chunks: list[KnowledgeChunk] = []

    for index, part in enumerate(parts, start=1):
        part = part.strip()
        if len(part) < 30:
            continue

        lines = [line.strip() for line in part.splitlines() if line.strip()]
        title = lines[0][:80] if lines else f"Chunk {index}"
        content = "\n".join(lines)
        metadata = infer_metadata(title, content, source_name, len(chunks) + 1)

        chunks.append(
            KnowledgeChunk(
                id=f"chunk-{len(chunks) + 1:03d}",
                title=title,
                content=content,
                metadata=metadata,
            )
        )

    return chunks
