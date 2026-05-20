from pathlib import Path

from app.rag.chunker import KnowledgeChunk, chunk_text


def read_text(path: Path) -> str:
    encodings = ["utf-8-sig", "utf-8", "cp950", "big5"]
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def load_knowledge_base(path: Path) -> list[KnowledgeChunk]:
    if not path.exists():
        return []

    text = read_text(path)
    return chunk_text(text, source_name=path.name)

