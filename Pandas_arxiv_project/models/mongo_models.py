from __future__ import annotations
from mongoengine import (
    Document, EmbeddedDocument, EmbeddedDocumentField, StringField,
    ListField, FloatField, IntField
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
    embedding: ListField = ListField(FloatField(), default=list)
    author_id: IntField = IntField()
    article_id: IntField = IntField()

    meta = { "collection": "scientific_articles", "indexes": [{"fields": ["$text"]}] }
