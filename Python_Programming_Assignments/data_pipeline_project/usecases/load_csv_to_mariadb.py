from __future__ import annotations

import csv
import importlib
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session


def load_csv_to_mariadb(csv_path: Path) -> tuple[int, int]:
    """Load rows from CSV into MariaDB.
    Returns (authors_created, articles_created).
    """
    storage_module = importlib.import_module("storage.mariadb")
    init_db = storage_module.init_db
    get_session = storage_module.get_session

    init_db()
    authors_created = 0
    articles_created = 0

    models_module = importlib.import_module("models.sql_models")
    Author = models_module.Author
    ScientificArticle = models_module.ScientificArticle

    with get_session() as session:
        assert isinstance(session, Session)
        existing_authors: dict[str, Any] = {}

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                full_name = row["author_full_name"].strip()
                title = row.get("author_title") or None

                author = existing_authors.get(full_name)
                if author is None:
                    # Try fetch from DB
                    author = session.scalar(select(Author).where(Author.full_name == full_name))
                    if author is None:
                        author = Author(full_name=full_name, title=title)
                        session.add(author)
                        session.flush()
                        authors_created += 1
                    existing_authors[full_name] = author

                article = ScientificArticle(
                    title=row["title"].strip(),
                    summary=row["summary"].strip(),
                    file_path=row["file_path"].strip(),
                    arxiv_id=row["arxiv_id"].strip(),
                    author=author,
                )
                session.add(article)
                articles_created += 1

        session.commit()

    return authors_created, articles_created
