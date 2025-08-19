from __future__ import annotations

import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class EmbeddingIndex:
    """Optional FAISS + Sentence-Transformers index over Manim snippets.

    If dependencies are missing, the index is disabled and .search() returns [].
    """

    def __init__(self, snippets: List[Dict[str, str]]) -> None:
        self._enabled = False
        self._snippets = snippets
        self._model = None
        self._index = None
        self._vectors = None
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            import faiss  # type: ignore

            # Lazy init model to reduce cold start cost
            self._model = SentenceTransformer("BAAI/bge-small-en-v1.5")
            texts = [self._snippet_text(s) for s in snippets]
            self._vectors = self._model.encode(texts, normalize_embeddings=True)

            dim = self._vectors.shape[1]
            self._index = faiss.IndexFlatIP(dim)
            self._index.add(self._vectors)
            self._enabled = True
            logger.info("✅ Embedding index initialized (BAAI/bge-small-en-v1.5 + FAISS)")
        except Exception as e:
            logger.warning(f"Embedding index disabled (missing deps or init failed): {e}")
            self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        if not self._enabled or not query:
            return []
        try:
            import numpy as np  # type: ignore
            q_vec = self._model.encode([query], normalize_embeddings=True)
            scores, idx = self._index.search(q_vec, top_k)
            idx_list = idx[0].tolist()
            results: List[Tuple[float, Dict[str, str]]] = []
            for i, score in zip(idx_list, scores[0].tolist()):
                if 0 <= i < len(self._snippets):
                    results.append((score, self._snippets[i]))
            results.sort(key=lambda x: x[0], reverse=True)
            return [s for _, s in results]
        except Exception as e:
            logger.warning(f"Embedding search failed, falling back to none: {e}")
            return []

    @staticmethod
    def _snippet_text(s: Dict[str, str]) -> str:
        title = s.get("title", "")
        desc = s.get("description", "")
        tags = s.get("tags", "")
        code = s.get("code", "")
        return f"{title}\n{desc}\n{tags}\n{code}"


