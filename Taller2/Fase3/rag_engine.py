from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

import model as llm
from knowledge_base import build_or_load_vectorstore
from prompts import FALLBACK_MESSAGE, build_rag_prompt


@dataclass
class RetrievedChunk:
    source: str
    score: float
    content: str


class RAGEngine:
    def __init__(
        self, min_score: float = 0.25, top_k: int = 4, force_reindex: bool = False
    ) -> None:
        self.min_score = min_score
        self.top_k = top_k
        self.vectorstore = build_or_load_vectorstore(force_reindex=force_reindex)

    @staticmethod
    def _query_terms(question: str) -> list[str]:
        terms = re.findall(r"[a-zA-Z0-9-]{4,}", question.lower())
        return [term for term in terms if term not in {"cual", "como", "para", "donde"}]

    def _keyword_retrieve(self, question: str) -> list[RetrievedChunk]:
        payload = self.vectorstore.get(include=["documents", "metadatas"])
        documents = payload.get("documents") or []
        metadatas = payload.get("metadatas") or []
        terms = self._query_terms(question)
        if not terms:
            return []

        identifier_terms = re.findall(r"\b[A-Z]{2,4}-\d+\b", question.upper())
        hits: list[RetrievedChunk] = []
        for doc_text, metadata in zip(documents, metadatas):
            text = str(doc_text or "")
            text_lower = text.lower()
            if identifier_terms:
                if not any(identifier.lower() in text_lower for identifier in identifier_terms):
                    continue
                lexical_score = 1.0
            else:
                match_count = sum(1 for term in terms if term in text_lower)
                if match_count == 0:
                    continue
                lexical_score = min(1.0, match_count / max(1, len(terms)))

            hits.append(
                RetrievedChunk(
                    source=str((metadata or {}).get("source", "desconocido")),
                    score=lexical_score,
                    content=text.strip(),
                )
            )

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[: self.top_k]

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()

    def retrieve(self, question: str) -> list[RetrievedChunk]:
        docs_scores = self.vectorstore.similarity_search_with_score(
            question,
            k=self.top_k,
        )
        chunks: list[RetrievedChunk] = []
        for doc, distance in docs_scores:
            safe_distance = max(float(distance), 0.0)
            score = 1.0 / (1.0 + safe_distance)
            if score < self.min_score:
                continue
            source = str(doc.metadata.get("source", "desconocido"))
            chunks.append(
                RetrievedChunk(
                    source=source,
                    score=float(score),
                    content=doc.page_content.strip(),
                )
            )
        lexical_hits = self._keyword_retrieve(question)
        if not lexical_hits:
            return []

        merged: list[RetrievedChunk] = []
        seen: set[tuple[str, str]] = set()
        for item in lexical_hits + chunks:
            key = (item.source, item.content)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
            if len(merged) >= self.top_k:
                break
        return merged

    @staticmethod
    def _build_context_block(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "(sin contexto recuperado)"
        lines: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            lines.append(
                f"[{idx}] fuente={chunk.source} score={chunk.score:.4f}\n{chunk.content}"
            )
        return "\n\n".join(lines)

    @staticmethod
    def _extract_sources(chunks: list[RetrievedChunk]) -> list[str]:
        unique: list[str] = []
        for chunk in chunks:
            if chunk.source not in unique:
                unique.append(chunk.source)
        return unique

    def answer(self, question: str) -> str:
        chunks = self.retrieve(question)
        if not chunks:
            return FALLBACK_MESSAGE

        context_block = self._build_context_block(chunks)
        prompt = build_rag_prompt(question, context_block)
        answer = llm.run_model(prompt).strip()
        if not answer:
            return FALLBACK_MESSAGE
        normalized_answer = self._normalize_text(answer)
        normalized_fallback = self._normalize_text(FALLBACK_MESSAGE)
        if normalized_fallback in normalized_answer or "no cuento con informacion suficiente" in normalized_answer:
            return FALLBACK_MESSAGE

        sources = self._extract_sources(chunks)
        if "Fuentes:" not in answer:
            citations = ", ".join([f"[{source}]" for source in sources])
            answer = f"{answer}\n\nFuentes: {citations}"
        return answer
