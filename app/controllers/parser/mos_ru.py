import json
import re
from datetime import datetime, timedelta
from typing import Union, List, Optional, Dict

import requests

from loguru import logger
from sqlalchemy.orm import Session

from controllers.vectorization import get_vector
from db.engine import Session as SessionLocal

from db import Article, VectorArticle

from workers.core import celery as celery_app


def clean_text(text: str) -> str:
    return re.sub('(&\w*;)|(<[^>]*>)', '', text)


class MosRuParser:
    articles: List[str]

    def __init__(self, url: str, source_id: int):
        self.url = url
        self.source_id = source_id

    def get_article_text(self, id: Union[int, str]) -> Optional[str]:
        response = requests.get(f'{self.url}/{id}')
        if response.ok:
            return clean_text(response.json()['full_text'])
        return None

    def create_articles(self, db: Session, date_from: datetime,
                        date_to: datetime):
        current_page = 1
        while True:
            data = self.get_article_ids(
                page=current_page,
                date_from=date_from.strftime("%Y-%m-%d %H:%M:%S"),
                date_to=date_to.strftime("%Y-%m-%d %H:%M:%S"),
            )
            if data:
                total_pages = data['_meta']['pageCount']
                self.save_new_articles(db=db, data=data)
                logger.info(f"Loaded {current_page} of {total_pages} page ")
                if total_pages <= current_page:
                    break

            logger.info(f"tried {current_page}")
            current_page += 1

    def get_article_ids(self, date_from: str = '', date_to: str = '',
                        page: int = 1) -> Optional[dict]:
        response = requests.get(self.url, params={
            'fields': 'id',
            'from': date_from,
            'to': date_to,
            'per-page': 50,
            'page': page,
            'sort': '-date',
        })
        if response.ok:
            return response.json()
        return None

    def save_new_articles(self, db: Session, data: Dict):
        for item in data['items']:
            external_id = str(item['id'])
            if db.query(Article).filter_by(external_id=external_id,
                                           source_id=self.source_id).first():
                continue
            text = self.get_article_text(id=external_id)
            if text:
                article = Article(content=text,
                                  source_id=self.source_id,
                                  external_id=str(item['id']))
                db.add(article)
                db.commit()
                db.refresh(article)
                vector = json.dumps(get_vector(text=text))
                v_article = VectorArticle(vector=vector, article=article)
                db.add(v_article)
                db.commit()

    def add_last_articles(self, db: Session):
        data = self.get_article_ids()
        if data:
            self.save_new_articles(db=db, data=data)
            logger.info("Articles updated!")
        else:
            logger.error('Data not found!')


URL = 'https://www.mos.ru/api/newsfeed/v4/frontend/json/ru/articles'


@celery_app.task(bind=True, name='download_all_articles_mos_ru')
def download_all_articles_mos_ru(self):
    session = SessionLocal()
    parser = MosRuParser(url=URL, source_id=1)
    date_from = datetime.now() - timedelta(days=270)
    date_to = datetime.now()
    logger.info("Started")
    parser.create_articles(db=session, date_from=date_from, date_to=date_to)


@celery_app.task(bind=True, name='download_last_articles_mos_ru')
def download_last_articles_mos_ru(self):
    session = SessionLocal()
    parser = MosRuParser(url=URL, source_id=1)
    date_from = datetime.now() - timedelta(days=1)
    date_to = datetime.now()
    parser.create_articles(db=session, date_from=date_from, date_to=date_to)


def main():
    download_all_articles_mos_ru.delay()


if __name__ == '__main__':
    main()
