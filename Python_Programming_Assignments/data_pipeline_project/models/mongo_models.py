from __future__ import annotations

from typing import Optional

from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    FloatField,
    ListField,
    StringField,
)

class AuthorEmbedded(EmbeddedDocument):
    full_name: StringField = StringField(required=True, max_length=255)
    title: StringField = StringField(required=False, max_length=255)

class ScientificArticleDoc(Document):
    title: StringField = StringField(required=True, max_length=512)
    summary: StringField = StringField(required=True, max_length=2048)
    file_path: StringField = StringField(required=True, max_length=512)
    arxiv_id: StringField = StringField(required=True, max_length=64)
    author: EmbeddedDocumentField = EmbeddedDocumentField(AuthorEmbedded, required=True)
    text: StringField = StringField(required=True)
    embedding: ListField = ListField(FloatField(), required=False, default=list)

    meta = {
        "collection": "scientific_articles",
        # Text index on the 'text' field:
        "indexes": [{"fields": ["$text"]}],  # MongoDB text index
    }
