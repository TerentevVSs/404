from dataclasses import dataclass
from typing import List, Dict, Union

import numpy as np
from numpy.linalg import norm
from nltk import ngrams
from controllers import vectorization, sample_articles_content

import requests
import json

from loguru import logger

NGRAM_LENGTH = 12
THRESHOLD_SIMILARITY_MIN_FOR_NGRAM = 0.8


def get_cosine_similarity(v1: np.ndarray, v2: np.ndarray):
    """Рассчитывает косинусную близость"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


class Ngram:
    url = 'https://morescience.app/api/translate'

    def __init__(self, ngram: list):
        self.ngram_lst = ngram
        self.ngram_str = ' '.join(ngram)
        self.vector = self.vectorize()
        self.translated = None
        self.ner_sentiment = None
        self.entities = None

    def vectorize(self):
        vector = vectorization.get_vector(self.ngram_str)
        return vector

    def get_translate(self):
        r = requests.post(self.url, json={'string': self.ngram_str})
        translated = r.text
        self.translated = translated

    def get_ner_sentiment(self):
        r = requests.post(self.url, json={'string': self.translated})
        sentiment = json.loads(r.text)
        self.ner_sentiment = sentiment

    def get_entities(self):
        entities = list()
        for entity in self.ner_sentiment['entities']:
            entities.append({'name': entity['name'],
                             'salience': entity['salience']})

        self.entities = entities

    def __repr__(self):
        return self.ngram_str

    def __str__(self):
        return self.ngram_str


class ArticleNer:
    def __init__(self, text: str, type_: bool,
                 ngram_length: int = NGRAM_LENGTH):
        self.text = text
        self.type = type_  # true or false
        logger.info(f'type = {self.type}')
        self.list = text.split()
        self.ngram_length = ngram_length
        if self.type is True:
            self.ngrams = self.split_to_ngrams_true()
            logger.info(f'ngrams = {self.ngrams}')
        else:
            self.ngrams = self.split_to_ngrams_false()
            logger.info(f'ngrams = {self.ngrams}')

    def get_chunks(self, lst, ngram_length):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(self.list), ngram_length):
            yield lst[i:i + ngram_length]

    def split_to_ngrams_true(self):
        ngrams_ = ngrams(self.list, self.ngram_length)
        ngrams_ = [Ngram(i) for i in ngrams_]
        return ngrams_

    def split_to_ngrams_false(self):
        ngrams_ = self.get_chunks(self.list, self.ngram_length)
        ngrams_ = [Ngram(i) for i in ngrams_]
        return ngrams_


@dataclass
class NgramPair:
    ngram_true: Ngram
    ngram_false: Ngram

    def print(self):
        print(f'ngram_false = {self.ngram_false.ngram_str}\n'
              f'gram_true = {self.ngram_true.ngram_str}\n\n')


class ArticlePair:
    def __init__(self, article_1: ArticleNer, article_2: ArticleNer):
        if article_1.type:
            self.article_true = article_1
            self.article_false = article_2
        else:
            self.article_true = article_2
            self.article_false = article_1

        self.ngram_pairs = self.get_ngram_pairs()
        self.result = self.compare_pairs()

    def print(self):
        [i.print() for i in self.ngram_pairs]

    def get_closest_ngram(self, ngram_false):
        similarities = dict()
        for ngram_true in self.article_true.ngrams:
            similarities[get_cosine_similarity(ngram_false.vector, ngram_true.vector)] = ngram_true

        max_similarity = max(similarities.keys())
        if max_similarity < THRESHOLD_SIMILARITY_MIN_FOR_NGRAM:
            # print('None')
            return ngram_false, 'not found'

        # print(similarities[max_similarity])
        return similarities[max_similarity], 'found'

    def get_ngram_pairs(self):
        ngram_pairs = list()
        for ngram_false in self.article_false.ngrams:
            ngram_true_closest = self.get_closest_ngram(ngram_false)
            ngram_pair = NgramPair(ngram_true_closest, ngram_false)
            ngram_pairs.append(ngram_pair)

        return ngram_pairs

    def get_average_weighted(self, values, weights):
        average_weighted = np.average(values, weights=weights)
        return average_weighted

    def compare_pairs(self):
        result = list()
        saliences = list()
        for ngram_pair in self.ngram_pairs:
            ngram_pair.ngram_true.get_translate()
            ngram_pair.ngram_false.get_translate()

            ngram_pair.ngram_true.get_ner_sentiment()
            ngram_pair.ngram_false.get_ner_sentiment()

            ngram_pair.ngram_true.get_entities()
            ngram_pair.ngram_false.get_entities()

            ner_sentiment_entities_true = ngram_pair.ngram_true.entities
            ner_sentiment_entities_false = ngram_pair.ngram_false.entities

            ner_sentiment_entities_true_names = [i['name'] for i in ner_sentiment_entities_true]
            ner_sentiment_entities_false_names = [i['name'] for i in ner_sentiment_entities_false]

            ner_sentiment_entities_true_salience = [i['salience'] for i in ner_sentiment_entities_true]
            ner_sentiment_entities_false_salience = [i['salience'] for i in ner_sentiment_entities_false]

            salience = np.median(ner_sentiment_entities_true_salience + ner_sentiment_entities_false_salience)
            saliences.append(salience)

            intersection = set(ner_sentiment_entities_true_names) & set(ner_sentiment_entities_false_names)
            coef = len(intersection) / len(ner_sentiment_entities_true)

            text_true = ngram_pair.ngram_true.ngram_str
            if ngram_pair.status == 'not found':
                text_true = ''

            # if ngram_pair.status == 'found':
            #     print()

            result.append({'text_false': ngram_pair.ngram_false.ngram_str,
                           'text_true': text_true,
                           'truth': coef})

        # percent = np.median([i['truth'] for i in result])
        percent = self.get_average_weighted([i['truth'] for i in result], saliences)

        return {'ngrams': result, 'percent': percent}


def main():
    article_true = ArticleNer(sample_articles_content.article_true_string,
                              type_=True)
    article_false = ArticleNer(sample_articles_content.article_false_string,
                               type_=False)

    article_pair = ArticlePair(article_true, article_false)
    logger.info(article_pair.result)


if __name__ == '__main__':
    main()
