from __future__ import annotations

import importlib
import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def mariadb_url_from_env() -> str:
    # Prefer full DSN if provided
    dsn = os.getenv("MARIADB_DSN")
    if dsn:
        return dsn
    user = os.getenv("MARIADB_USER", "root")
    pwd = os.getenv("MARIADB_PASSWORD", "password")
    host = os.getenv("MARIADB_HOST", "localhost")
    port = os.getenv("MARIADB_PORT", "3306")
    db = os.getenv("MARIADB_DATABASE", "articles_db")
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"

def get_engine(echo: bool = False) -> Engine:
    engine = create_engine(mariadb_url_from_env(), echo=echo, pool_pre_ping=True)
    return engine

def init_db() -> None:
    models_module = importlib.import_module("models.sql_models")
    Base = models_module.Base
    engine = get_engine()
    Base.metadata.create_all(engine)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        yield session
