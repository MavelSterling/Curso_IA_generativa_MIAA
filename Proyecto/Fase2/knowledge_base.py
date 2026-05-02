from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
EMBEDDING_DIMENSION = 256


class HashEmbeddings(Embeddings):
    def __init__(self, dimension: int = EMBEDDING_DIMENSION) -> None:
        self.dimension = dimension

    def _text_to_vector(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = text.lower().split()
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            idx = int(digest, 16) % self.dimension
            vector[idx] += 1.0

        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0.0:
            return vector
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._text_to_vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._text_to_vector(text)


def _load_markdown(path: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [
        Document(
            page_content=text,
            metadata={"source": path.name, "doc_type": "markdown"},
        )
    ]


def _load_csv(path: Path) -> list[Document]:
    documents: list[Document] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for index, row in enumerate(reader, start=1):
            content = "\n".join([f"{key}: {value}" for key, value in row.items()])
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": path.name,
                        "doc_type": "csv",
                        "row": index,
                    },
                )
            )
    return documents


def _load_json(path: Path) -> list[Document]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    records: list[dict] = []
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict):
        for value in raw.values():
            if isinstance(value, list):
                records.extend([item for item in value if isinstance(item, dict)])

    documents: list[Document] = []
    for index, record in enumerate(records, start=1):
        content = json.dumps(record, ensure_ascii=False, indent=2)
        documents.append(
            Document(
                page_content=content,
                metadata={"source": path.name, "doc_type": "json", "record": index},
            )
        )
    return documents


def load_knowledge_documents() -> list[Document]:
    documents: list[Document] = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        documents.extend(_load_markdown(path))
    for path in sorted(KNOWLEDGE_DIR.glob("*.csv")):
        documents.extend(_load_csv(path))
    for path in sorted(KNOWLEDGE_DIR.glob("*.json")):
        documents.extend(_load_json(path))
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " "],
    )
    return splitter.split_documents(documents)


def build_embeddings_model() -> Embeddings:
    return HashEmbeddings()


def _has_indexed_documents(store: Chroma) -> bool:
    try:
        payload = store.get(limit=1)
    except Exception:
        return False
    ids = payload.get("ids") or []
    return len(ids) > 0


def _clear_vectorstore_dir(path: Path) -> None:
    if not path.exists():
        return
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def build_or_load_vectorstore(force_reindex: bool = False) -> Chroma:
    embeddings = build_embeddings_model()
    if force_reindex and VECTORSTORE_DIR.exists():
        _clear_vectorstore_dir(VECTORSTORE_DIR)

    if VECTORSTORE_DIR.exists():
        store = Chroma(
            persist_directory=str(VECTORSTORE_DIR),
            embedding_function=embeddings,
            collection_name="ecomarket_knowledge",
        )
        if _has_indexed_documents(store):
            return store
        _clear_vectorstore_dir(VECTORSTORE_DIR)

    source_documents = load_knowledge_documents()
    if not source_documents:
        raise RuntimeError("No se encontraron documentos en la carpeta knowledge.")

    chunks = split_documents(source_documents)
    store = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
        collection_name="ecomarket_knowledge",
    )
    return store
