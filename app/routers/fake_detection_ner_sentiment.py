from fastapi import APIRouter

from controllers import sample_articles_content
from controllers.article_ner import ArticleNer, ArticlePair
from db.schemas import VectorArticleOutput

router = APIRouter(tags=['Fake News'])


@router.post("/check-article_ner_sentiment", status_code=200,
             response_model=VectorArticleOutput)
async def check_article_ner_sentiment(article_true_text: str=sample_articles_content.article_true_string,
                                      article_false_text: str=sample_articles_content.article_false_string):

    article_true = ArticleNer(article_true_text, type_=True)
    article_false = ArticleNer(article_false_text, type_=False)

    article_pair = ArticlePair(article_true, article_false)

    return article_pair.result
