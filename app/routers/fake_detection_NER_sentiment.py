from fastapi import APIRouter, Form
from loguru import logger

from controllers.vectorization import get_vector
from db.schemas import VectorArticleOutput

router = APIRouter(tags=['vectors'])

from controllers.article import Article, ArticlePair
from controllers import sample_article_content


@router.post("/check-article_ner_sentiment", status_code=200,
             response_model=VectorArticleOutput)
async def check_article_ner_sentiment(article_true_text: str=sample_article_content.article_true_string,
                                      article_false_text: str=sample_article_content.article_false_string):

    article_true = Article(article_true_text, type_=True)
    article_false = Article(article_false_text, type_=False)

    article_pair = ArticlePair(article_true, article_false)

    return article_pair.result
