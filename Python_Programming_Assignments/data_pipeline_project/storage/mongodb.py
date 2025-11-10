from __future__ import annotations

import os

from mongoengine import connect


def mongo_url_from_env() -> str:
    dsn = os.getenv("MONGODB_DSN")
    if dsn:
        return dsn
    user = os.getenv("MONGODB_USER")
    pwd = os.getenv("MONGODB_PASSWORD")
    host = os.getenv("MONGODB_HOST", "localhost")
    port = os.getenv("MONGODB_PORT", "27017")
    db = os.getenv("MONGODB_DATABASE", "articles_db")

    if user and pwd:
        return f"mongodb://{user}:{pwd}@{host}:{port}/{db}"
    return f"mongodb://{host}:{port}/{db}"

def init_mongo() -> None:
    url = mongo_url_from_env()
    connect(host=url, uuidRepresentation="standard")
