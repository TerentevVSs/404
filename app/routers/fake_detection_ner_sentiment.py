import json
from typing import Optional, List

import numpy as np
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from markupsafe import Markup
from sqlalchemy.orm import Session

from controllers.article_ner import ArticleNer, ArticlePair, \
    get_cosine_similarity
from controllers.parser.mos_ru import clean_text
from controllers.vectorization import get_vector
from db import SuspiciousArticle, VectorArticle, Article
from db.engine import get_session
from db.schemas import Answer, ArticleBase

router = APIRouter(tags=['Fake News'])

templates = Jinja2Templates(directory="frontend/templates")


@router.post("/check-article_ner_sentiment", status_code=200,
             response_model=Answer)
async def check_article_ner_sentiment(
        suspicious_article: ArticleBase,
        session=Depends(get_session)):
    suspicious_article_text = clean_text(suspicious_article.content)

    s_article: Optional[SuspiciousArticle] = session.query(
        SuspiciousArticle).filter_by(content=suspicious_article_text).first()
    if s_article:
        logger.info(json.loads(s_article.answer))
        return Answer(
            suspicious_content=s_article.content,
            percentage=s_article.percentage,
            article=s_article.article.content,
            result=json.loads(s_article.answer),
            source=s_article.article.source.title,
        )
    suspicious_vector = get_vector(suspicious_article_text)
    v_articles: List[VectorArticle] = session.query(VectorArticle).all()
    similarities = []
    for v_article in v_articles:
        sim = get_cosine_similarity(np.array(json.loads(v_article.vector)),
                                    suspicious_vector)
        similarities.append((sim, v_article.article_id))
    # logger.info()
    id_ = max(similarities, key=lambda x: x[0])[1]
    article = session.query(Article).filter_by(id=id_).first()

    article_true = ArticleNer(article.content, type_=True)
    article_false = ArticleNer(suspicious_article_text, type_=False)

    article_pair = ArticlePair(article_true, article_false)
    ngrams = list(
        map(lambda x: {
            'truth': round(x['truth'] * 100),
            'text_true': x['text_true'],
            'text_false': x['text_false'],
        }, article_pair.result['ngrams']))
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
        suspicious_content=suspicious_article_text,
        percentage=percentage,
        article=article.content,
        result=ngrams,
        source=article.source.title,
    )


@router.get("/", response_class=HTMLResponse)
async def check_fake(request: Request):
    return templates.TemplateResponse("index.html", {
        'request': request, })


def get_color(percentage: int):
    if percentage > 75:
        return "light-green"
    if percentage > 50:
        return "yellow"
    if percentage > 25:
        return "orange"
    return "red"


def colorize(text: str, ngrams):
    for ngram in ngrams:
        part = ngram['text_false']
        if part and part in text:
            ind = text.find(part)
            text = text[:ind] + Markup(
                f'<span class="{get_color(ngram["truth"])}" title="{ngram["truth"]} {ngram["text_true"]}">') + text[


                                                                 ind:ind + len(
                                                                     part)] + Markup(
                '</span>') + text[ind + len(part):]

    return text


@router.post("/", response_class=HTMLResponse)
async def check_fake(request: Request, session: Session = Depends(get_session)):
    form = await request.form()
    text = form.get('input_text')

    text = clean_text(text)

    s_article: Optional[SuspiciousArticle] = session.query(
        SuspiciousArticle).filter_by(content=text).first()
    if s_article:
        logger.info(json.loads(s_article.answer))
        text = colorize(text, json.loads(s_article.answer))
        return templates.TemplateResponse("index.html", {
            'request': request, 'answer': Answer(
                suspicious_content=text,
                percentage=s_article.percentage,
                article=s_article.article.content,
                result=json.loads(s_article.answer),
                source=s_article.article.source.title,
            ).dict()
        })
    suspicious_vector = get_vector(text)
    v_articles: List[VectorArticle] = session.query(VectorArticle).all()
    similarities = []
    for v_article in v_articles:
        sim = get_cosine_similarity(np.array(json.loads(v_article.vector)),
                                    suspicious_vector)
        similarities.append((sim, v_article.article_id))
    id_ = max(similarities, key=lambda x: x[0])[1]
    article = session.query(Article).filter_by(id=id_).first()

    article_true = ArticleNer(article.content, type_=True)
    article_false = ArticleNer(text, type_=False)

    article_pair = ArticlePair(article_true, article_false)
    ngrams = list(
        map(lambda x: {
            'truth': round(x['truth'] * 100),
            'text_true': x['text_true'],
            'text_false': x['text_false'],
        }, article_pair.result['ngrams']))
    percentage = int(round(article_pair.result['percentage'] * 100))
    session.add(SuspiciousArticle(
        content=text,
        article_id=article.id,
        flag=percentage > 75,
        percentage=percentage,
        answer=json.dumps(ngrams)
    ))
    session.commit()

    return templates.TemplateResponse("index.html", {
        'request': request,
        'answer': Answer(
            suspicious_content=colorize(text,ngrams),
            percentage=percentage,
            article=article.content,
            source=article.source.title,
            result=ngrams,
        ).dict()
    })
