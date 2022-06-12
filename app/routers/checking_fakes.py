from typing import Optional

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.orm import Session

from db import SuspiciousArticle
from db.engine import get_session
from db.schemas import SuspiciousArticleBase, \
    SuspiciousArticle as SuspiciousArticleSchema

router = APIRouter(tags=['checking fakes'])


@router.post(path='/check-article', status_code=201,
             response_model=SuspiciousArticleBase)
def check_article(suspicious_article: SuspiciousArticleBase,
                  session: Session = Depends(get_session)) -> object:
    logger.info(suspicious_article)
    sa: Optional[SuspiciousArticle] = session.query(SuspiciousArticle).filter(SuspiciousArticle.content == suspicious_article.content).first()
    if sa:
        article = SuspiciousArticleSchema.from_orm(**sa)
        return article
    session.add(SuspiciousArticle(**suspicious_article.dict()))
    session.commit()
    suspicious_article.flag = True
    suspicious_article.percentage = 0.3
    suspicious_article.answer = 'библия'
    return suspicious_article



