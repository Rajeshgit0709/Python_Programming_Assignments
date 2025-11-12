from __future__ import annotations
from typing import List, Tuple
from models.mongo_models import ScientificArticleDoc
from storage.mongodb import init_mongo

def search_text(query: str, limit: int = 5) -> List[Tuple[str, float]]:
    init_mongo()
    cursor = ScientificArticleDoc.objects.search_text(query).order_by("$text_score").limit(limit)
    results: List[Tuple[str, float]] = []
    for doc in cursor:
        score = float(getattr(doc, "_text_score", 0.0))  # type: ignore[attr-defined]
        results.append((doc.title, score))
    return results
