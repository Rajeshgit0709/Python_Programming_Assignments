from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.mongo_models import AuthorEmbedded, ScientificArticleDoc
from models.sql_models import ScientificArticle
from storage.mariadb import get_session
from storage.mongodb import init_mongo


def pdf_to_markdown(pdf_path: Path) -> str:
    """Extract text from PDF (pypdf if available) and wrap as Markdown."""
    try:
        from pypdf import PdfReader  # type: ignore
        body = "\n\n".join(
            (t.strip() for p in PdfReader(str(pdf_path)).pages
             if (t := (p.extract_text() or "")))
        ) or "(No extractable text)"
    except Exception:
        body = "(Extracted text unavailable in this environment)"
    return f"# Extracted Content\n\n{body}\n"


def _tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"\W+", text.lower()) if t]


def compute_embedding(text: str, dim: int = 128) -> list[float]:
    """Deterministic hash-based bag-of-words embedding, L2-normalized."""
    vec = [0.0] * dim
    for tok in _tokenize(text):
        h = hashlib.sha256(tok.encode("utf-8")).digest()
        vec[int.from_bytes(h[:4], "big") % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm else vec


def transfer_mariadb_to_mongodb(papers_root: Path) -> int:
    """Load articles from MariaDB into MongoDB with PDF→Markdown + embedding."""
    init_mongo()
    inserted = 0
    with get_session() as session:
        assert isinstance(session, Session)
        for art in session.scalars(select(ScientificArticle)):
            pdf_path = (papers_root / Path(art.file_path).name).resolve()
            doc = ScientificArticleDoc(
                title=art.title,
                summary=art.summary,
                file_path=str(pdf_path),
                arxiv_id=art.arxiv_id,
                author=AuthorEmbedded(
                    full_name=art.author.full_name, title=art.author.title or ""
                ),
                text=(md := pdf_to_markdown(pdf_path)),
                embedding=compute_embedding(md),
            )
            doc.save()
            inserted += 1
    return inserted
