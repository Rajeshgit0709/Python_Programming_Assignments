from __future__ import annotations

import importlib


def search_text(query: str, limit: int = 5) -> list[tuple[str, float]]:
    """Search the MongoDB text index and return [(title, score)]."""
    mongo_storage = importlib.import_module("storage.mongodb")
    init_mongo = mongo_storage.init_mongo
    mongo_models = importlib.import_module("models.mongo_models")
    ScientificArticleDoc = mongo_models.ScientificArticleDoc

    init_mongo()
    cursor = ScientificArticleDoc.objects.search_text(query).order_by("$text_score").limit(limit)
    results: list[tuple[str, float]] = []
    for doc in cursor:
        score = float(getattr(doc, "_text_score", 0.0))
        results.append((doc.title, score))
    return results
