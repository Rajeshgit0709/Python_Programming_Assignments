from __future__ import annotations

import hashlib, math, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import unescape

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.sql_models import Author, ScientificArticle
from models.mongo_models import AuthorEmbedded, ScientificArticleDoc
from storage.mariadb import get_session, init_db
from storage.mongodb import init_mongo


# ---------- helpers ----------
def _ensure_string_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.astype({c: "string" for c in df.columns})

def _html_to_text(html: str) -> str:
    t = re.sub(r"<script.*?>.*?</script>|<style.*?>.*?</style>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", unescape(t)).strip()

def _embed(text: str, dim: int = 128) -> list[float]:
    vec = [0.0] * dim
    for tok in re.findall(r"\w+", text.lower()):
        vec[int.from_bytes(hashlib.sha256(tok.encode()).digest()[:4], "big") % dim] += 1.0
    n = math.sqrt(sum(v * v for v in vec))
    return [v / n for v in vec] if n else vec


# ---------- arXiv API -> DataFrame ----------
def fetch_arxiv(query: str, max_results: int = 10) -> pd.DataFrame:
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": f"all:{query}", "start": 0, "max_results": max_results, "sortBy": "relevance"}
    )
    with urllib.request.urlopen(url) as r:
        root = ET.fromstring(r.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    rows: list[dict[str, str]] = []
    for e in root.findall("a:entry", ns):
        rows.append({
            "title":   (e.findtext("a:title", default="", namespaces=ns) or "").strip(),
            "summary": (e.findtext("a:summary", default="", namespaces=ns) or "").strip(),
            "file_path": "",
            "arxiv_id": (e.findtext("a:id", default="", namespaces=ns) or "").rsplit("/", 1)[-1].strip(),
            "author_full_name": (e.find("a:author", ns).findtext("a:name", default="", namespaces=ns) or "").strip()
                if e.find("a:author", ns) is not None else "",
            "author_title": "",
        })
    df = pd.DataFrame.from_records(
        rows,
        columns=["title", "summary", "file_path", "arxiv_id", "author_full_name", "author_title"],
    )
    return _ensure_string_df(df)

def add_html_content(df: pd.DataFrame) -> pd.DataFrame:
    def _fetch_html(arxiv_id: str) -> str:
        try:
            with urllib.request.urlopen(f"https://arxiv.org/abs/{arxiv_id}", timeout=20) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception:
            return ""
    out = df.copy()
    out["html_content"] = out["arxiv_id"].apply(_fetch_html).astype("string")
    return out


# ---------- MariaDB: DataFrame -> rows (apply) ----------
def _upsert_author(s: Session, name: str, title: str) -> int:
    a = s.scalar(select(Author).where(Author.full_name == name.strip()))
    if a:
        return int(a.id)
    a = Author(full_name=name.strip(), title=title or None)
    s.add(a); s.flush()
    return int(a.id)

def _insert_article(s: Session, row: pd.Series, author_id: int) -> int:
    art = ScientificArticle(
        title=str(row["title"]),
        summary=str(row["summary"]),
        file_path=str(row.get("file_path", "") or ""),
        arxiv_id=str(row["arxiv_id"]),
        author_id=author_id,
    )
    s.add(art); s.flush()
    return int(art.id)

def load_df_to_mariadb(df: pd.DataFrame) -> pd.DataFrame:
    init_db()
    df = _ensure_string_df(df).copy()
    author_ids: list[int] = []
    article_ids: list[int] = []
    with get_session() as s:
        assert isinstance(s, Session)
        def proc(row: pd.Series) -> tuple[int, int]:
            aid = _upsert_author(s, str(row["author_full_name"]), str(row.get("author_title", "") or ""))
            rid = _insert_article(s, row, aid)
            return aid, rid
        for aid, rid in df.apply(proc, axis=1, result_type="reduce").tolist():
            author_ids.append(int(aid)); article_ids.append(int(rid))
        s.commit()
    df["author_id"] = pd.Series(author_ids, dtype="Int64")
    df["article_id"] = pd.Series(article_ids, dtype="Int64")
    return df


# ---------- MongoDB: DataFrame -> docs (apply; HTML->text; embedding) ----------
def load_df_to_mongodb(df: pd.DataFrame) -> int:
    init_mongo()
    df = _ensure_string_df(df)
    def proc(row: pd.Series) -> int:
        html = str(row.get("html_content", "") or "")
        text = _html_to_text(html) if html else str(row.get("summary", "") or "")
        doc = ScientificArticleDoc(
            title=str(row["title"]),
            summary=str(row["summary"]),
            file_path=str(row.get("file_path", "") or ""),
            arxiv_id=str(row["arxiv_id"]),
            author=AuthorEmbedded(
                full_name=str(row.get("author_full_name", "") or ""),
                title=str(row.get("author_title", "") or ""),
            ),
            text=text,
            embedding=_embed(text),
        )
        if "author_id" in row and pd.notna(row["author_id"]): doc.author_id = int(row["author_id"])
        if "article_id" in row and pd.notna(row["article_id"]): doc.article_id = int(row["article_id"])
        doc.save()
        return 1
    return int(df.apply(proc, axis=1).sum())


# ---------- Orchestrator ----------
@dataclass
class PipelineResult:
    df: pd.DataFrame
    inserted_mongo: int

def run_arxiv_pipeline(query: str, max_results: int = 10) -> PipelineResult:
    df = fetch_arxiv(query, max_results)
    df = add_html_content(df)
    df = load_df_to_mariadb(df)
    return PipelineResult(df=df, inserted_mongo=load_df_to_mongodb(df))
