import json
from typing import Optional, List

import numpy as np
from fastapi import APIRouter, Depends

from controllers import sample_articles_content
from controllers.article_ner import ArticleNer, ArticlePair, \
    get_cosine_similarity
from controllers.parser.mos_ru import clean_text
from controllers.vectorization import get_vector
from db import SuspiciousArticle, VectorArticle, Article
from db.engine import get_session
from db.schemas import Answer

router = APIRouter(tags=['Fake News'])


@router.post("/check-article_ner_sentiment", status_code=200,
             response_model=Answer)
async def check_article_ner_sentiment(
        suspicious_article_text: str = sample_articles_content.article_false_string,
        session=Depends(get_session)):
    suspicious_article_text = clean_text(suspicious_article_text)

    s_article: Optional[SuspiciousArticle] = session.query(
        SuspiciousArticle).filter_by(content=suspicious_article_text).first()
    if s_article:
        return Answer(
            suspicious_content=s_article.content,
            percentage=s_article.percentage,
            article=s_article.article.content,
            result=json.loads(s_article.answer),
        )
    suspicious_vector = get_vector(suspicious_article_text)
    v_articles: List[VectorArticle] = session.query(VectorArticle).all()
    similarities = []
    for v_article in v_articles:
        sim = get_cosine_similarity(np.array(json.loads(v_article.vector)),
                                    suspicious_vector)
        similarities.append((sim, v_article.id))
    article = session.query(Article).filter_by(id=max(similarities,
                                                      key=lambda x: x[1])[
        0]).first()

    article_true = ArticleNer(article.content, type_=True)
    article_false = ArticleNer(suspicious_article_text, type_=False)

    article_pair = ArticlePair(article_true, article_false)
    ngrams = list(
        map(lambda x: round(x['truth'] * 100), article_pair.result['ngrams']))
    percentage = round(article_pair.result['percentage'] * 100)
    session.add(SuspiciousArticle(
        content=suspicious_article_text,
        article_id=article.id,
        flag=percentage > 75,
        percentage=percentage,
        answer=json.dumps(ngrams)
    ))
    session.commit()
    return Answer(
        suspicious_content=s_article.content,
        percentage=percentage,
        article=article.content,
        result=ngrams,
    )
