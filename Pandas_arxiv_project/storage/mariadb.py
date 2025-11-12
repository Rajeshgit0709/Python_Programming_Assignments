from __future__ import annotations
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models.sql_models import Base

def mariadb_url_from_env() -> str:
    dsn = os.getenv("MARIADB_DSN")
    if dsn:
        return dsn
    user = os.getenv("MARIADB_USER", "app")
    pwd = os.getenv("MARIADB_PASSWORD", "password")
    host = os.getenv("MARIADB_HOST", "localhost")
    port = os.getenv("MARIADB_PORT", "3306")
    db = os.getenv("MARIADB_DATABASE", "articles_db")
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"

def get_engine(echo: bool = False):
    return create_engine(mariadb_url_from_env(), echo=echo, pool_pre_ping=True)

def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    with SessionLocal() as session:
        yield session
