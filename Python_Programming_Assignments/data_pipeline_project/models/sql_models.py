from __future__ import annotations

from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    articles: Mapped[List["ScientificArticle"]] = relationship(back_populates="author")

    def __repr__(self) -> str:  # noqa: D401
        return f"Author(id={self.id!r}, full_name={self.full_name!r})"

class ScientificArticle(Base):
    __tablename__ = "scientific_articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(String(2048), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    arxiv_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    author: Mapped[Author] = relationship(back_populates="articles")

    def __repr__(self) -> str:
        return f"ScientificArticle(id={self.id!r}, title={self.title!r})"
