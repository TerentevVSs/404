from numpy import dot
from numpy.linalg import norm
from nltk import ngrams
import vectorization
# import sentiment
import sample_articles_content
import utils
import requests
import json
from pprint import pprint


logger = utils.get_logger('article.py', 'log.txt')
NGRAM_LENGTH = 12
THRESHOLD_SIMILARITY_MIN_FOR_NGRAM = 0.6


def get_cosine_similarity(v1, v2):
    return dot(v1, v2)/(norm(v1)*norm(v2))


class Ngram:
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
        r = requests.post('https://morescience.app/api/translate', json={'string': self.ngram_str})
        translated = r.text
        self.translated = translated

    def get_ner_sentiment(self):
        r = requests.post('https://morescience.app/api/sentiment', json={'string': self.translated})
        sentiment = json.loads(r.text)
        self.ner_sentiment = sentiment

    def get_entities(self):
        entities = list()
        for entity in self.ner_sentiment['entities']:
            entities.append(entity['name'])

        self.entities = entities

    def __repr__(self):
        return self.ngram_str

    def __str__(self):
        return self.ngram_str


class Article:
    def __init__(self, text: str, type_: bool, ngram_length: int = NGRAM_LENGTH):
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


class NgramPair:
    def __init__(self, ngram_true, ngram_false):
        self.ngram_true = ngram_true
        self.ngram_false = ngram_false

    def print(self):
        print(f'ngram_false = {self.ngram_false.ngram_str}\ngram_true = {self.ngram_true.ngram_str}\n\n')


class ArticlePair:
    def __init__(self, article_1: Article, article_2: Article):
        if article_1.type == True:
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

        if max(similarities.keys()) < THRESHOLD_SIMILARITY_MIN_FOR_NGRAM:
            return ngram_false

        # pprint(similarities)

        max_similarity = max(similarities.keys())
        return similarities[max_similarity]

    def get_ngram_pairs(self):
        ngram_pairs = list()
        for ngram_false in self.article_false.ngrams:
            ngram_true_closest = self.get_closest_ngram(ngram_false)
            ngram_pair = NgramPair(ngram_true_closest, ngram_false)
            ngram_pairs.append(ngram_pair)

        return ngram_pairs

    def compare_pairs(self):
        result = list()
        for ngram_pair in self.ngram_pairs:
            ngram_pair.ngram_true.get_translate()
            ngram_pair.ngram_false.get_translate()

            ngram_pair.ngram_true.get_ner_sentiment()
            ngram_pair.ngram_false.get_ner_sentiment()

            ngram_pair.ngram_true.get_entities()
            ngram_pair.ngram_false.get_entities()

            ner_sentiment_entities_true = ngram_pair.ngram_true.entities
            ner_sentiment_entities_false = ngram_pair.ngram_false.entities
            intersection = set(ner_sentiment_entities_true) & set(ner_sentiment_entities_false)
            coef = len(intersection) / len(ner_sentiment_entities_true)
            result.append({'text': ngram_pair.ngram_false.ngram_str, 'truth': coef})

        return result


test = True
if test:
    article_true = Article(sample_articles_content.article_true_string, type_=True)
    article_false = Article(sample_articles_content.article_false_string, type_=False)

    article_pair = ArticlePair(article_true, article_false)
    pprint(article_pair.result)
