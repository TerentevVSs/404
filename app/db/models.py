from sqlalchemy import Column, String, ForeignKey, Boolean, Float, Integer, \
    UniqueConstraint
from sqlalchemy.orm import relationship

from db.base import Base


class Source(Base):
    """Источник данных - Элемент white list"""
    title = Column(String(128), index=True, nullable=False)
    description = Column(String(512), nullable=True)
    base_url = Column(String, index=True, nullable=True)

    articles = relationship('Article', back_populates='source')


class Article(Base):
    """Статья (содержимое)"""
    __table_args__ = (UniqueConstraint('source_id', 'external_id', name='_source_external_uc'),)
    content = Column(String, nullable=False, index=True)
    source_id = Column(ForeignKey('source.id'))
    external_id = Column(Integer, nullable=False, index=True)

    source = relationship("Source", back_populates="articles")
    vector = relationship("VectorArticle", back_populates="article",
                          uselist=False)
    f = Column(Boolean, default=True)
    suspicious_articles = relationship("SuspiciousArticle", back_populates="article",)


class SuspiciousArticle(Base):
    """Подозрительная статья (для проверки)"""
    content = Column(String)
    article_id = Column(ForeignKey('article.id'), index=True, nullable=True,
                        unique=True)
    flag = Column(Boolean)  # True - Truth, False - Fake
    percentage = Column(Float)
    answer = Column(String)  # json.dumps

    article = relationship("Article", back_populates="suspicious_articles")


class VectorArticle(Base):
    """Статья (токенизированная)"""
    vector = Column(String, nullable=False, index=True)  # json.dumps
    article_id = Column(ForeignKey('article.id'), index=True, nullable=False,
                        unique=True)

    article = relationship("Article", back_populates="vector")
