from __future__ import annotations

from collections import Counter
from math import log, sqrt
import re

from app.rag.chunker import KnowledgeChunk


KEYWORDS = [
    "114",
    "115",
    "01",
    "02",
    "\u8ab2\u7a0b",
    "\u5831\u540d",
    "\u88dc\u52a9",
    "\u7504\u8a66",
    "\u96fb\u8a71",
    "line",
    "\u8077\u524d",
    "\u5728\u8077",
    "\u9752\u5e74",
    "\u5931\u696d",
    "\u8cc7\u683c",
    "\u734e\u52f5\u91d1",
    "\u6d25\u8cbc",
    "\u5728\u8077\u8a13\u7df4",
    "\u8077\u524d\u8a13\u7df4",
    "\u5e73\u53f0",
    "\u67e5\u8a62",
    "\u5b98\u65b9",
    "\u53f0\u7063\u5c31\u696d\u901a",
    "\u5728\u8077\u8a13\u7df4\u7db2",
    "\u8077\u524d\u8a13\u7df4\u7db2",
]


def infer_query_filters(question: str, category: str | None = None) -> dict[str, str]:
    filters: dict[str, str] = {}
    if "114" in question or "\u7b2c01" in question or "\u7b2c 01" in question:
        filters["year"] = "114"
        filters["term"] = "term-01"
    if "115" in question or "\u7b2c02" in question or "\u7b2c 02" in question:
        filters["year"] = "115"
        filters["term"] = "term-02"
    if category in {"on-job-training", "pre-job-training"}:
        filters["topic"] = category
    return filters


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    tokens = re.findall(r"[a-z0-9@._/-]+|[\u4e00-\u9fff]{2,}", lowered)
    for keyword in KEYWORDS:
        if keyword.lower() in lowered:
            tokens.append(keyword.lower())
    return tokens


def token_set(text: str) -> set[str]:
    return set(tokenize(text))


class TfidfIndex:
    def __init__(self, chunks: list[KnowledgeChunk]):
        self.documents = [tokenize(chunk.title + "\n" + chunk.content) for chunk in chunks]
        self.idf = self._build_idf()
        self.vectors = [self._vectorize(tokens) for tokens in self.documents]

    def _build_idf(self) -> dict[str, float]:
        doc_count = len(self.documents)
        document_frequency: Counter[str] = Counter()
        for tokens in self.documents:
            document_frequency.update(set(tokens))
        return {
            token: log((1 + doc_count) / (1 + frequency)) + 1
            for token, frequency in document_frequency.items()
        }

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        if not counts:
            return {}
        max_count = max(counts.values())
        return {
            token: (count / max_count) * self.idf.get(token, 1.0)
            for token, count in counts.items()
        }

    @staticmethod
    def cosine(left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        common = set(left).intersection(right)
        dot = sum(left[token] * right[token] for token in common)
        left_norm = sqrt(sum(value * value for value in left.values()))
        right_norm = sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    def score(self, question: str, index: int) -> float:
        query_vector = self._vectorize(tokenize(question))
        return self.cosine(query_vector, self.vectors[index])


class LocalRetriever:
    def __init__(self, chunks: list[KnowledgeChunk]):
        self.chunks = chunks
        self.keyword_index = [
            (chunk, token_set(chunk.title + "\n" + chunk.content))
            for chunk in chunks
        ]
        self.vector_index = TfidfIndex(chunks)

    def search(self, question: str, top_k: int = 4, category: str | None = None) -> list[dict]:
        question_tokens = token_set(question)
        filters = infer_query_filters(question, category)
        scored = []

        for index, (chunk, tokens) in enumerate(self.keyword_index):
            metadata = chunk.metadata
            if filters.get("year") and metadata.get("year") and metadata["year"] != filters["year"]:
                continue
            if filters.get("topic") and metadata.get("topic") and metadata["topic"] != filters["topic"]:
                continue

            keyword_score = len(question_tokens.intersection(tokens))
            vector_score = self.vector_index.score(question, index)
            score = keyword_score + (vector_score * 8)

            if metadata.get("year") and metadata["year"] in question:
                score += 3
            if metadata.get("topic") and metadata["topic"] == category:
                score += 2
            if filters.get("term") and metadata.get("term") == filters["term"]:
                score += 2

            if score > 0:
                scored.append((score, keyword_score, vector_score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "score": round(score, 4),
                "keyword_score": keyword_score,
                "vector_score": round(vector_score, 4),
                "id": chunk.id,
                "title": chunk.title,
                "content": chunk.content[:900],
                "metadata": chunk.metadata,
            }
            for score, keyword_score, vector_score, chunk in scored[:top_k]
        ]
