from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, HttpUrl


class SourceBase(BaseModel):
    title: str
    description: Optional[str]
    base_url: HttpUrl


class Source(SourceBase):
    id: int

    articles: list[Article] = []

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    content: str


class Article(ArticleBase):
    source_id: int

    source: Source
    vector: VectorArticle
    suspicious_articles: list[SuspiciousArticleBase] = []

    class Config:
        orm_mode = True


class SuspiciousArticleBase(BaseModel):
    content: str
    flag: Optional[bool]
    percentage: Optional[float]
    answer: Optional[str]


class SuspiciousArticle(SuspiciousArticleBase):
    article_id: Optional[int]

    article: Optional[Article]

    class Config:
        orm_mode = True


class VectorArticleBase(BaseModel):
    vector: str


class VectorArticleOutput(BaseModel):
    vector: list[float]


class VectorArticle(VectorArticleBase):
    article_id: int

    article: Article

    class Config:
        orm_mode = True


Source.update_forward_refs()
Article.update_forward_refs()
SuspiciousArticle.update_forward_refs()
VectorArticle.update_forward_refs()
