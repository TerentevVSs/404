import os
import random
import pandas as pd

class Tokens:
    def __init__(self, filepath=os.path.join('..', 'data', 'token_clusters.csv')):
        self.filepath = filepath
        self.df = self.load_tokens()
        self.mapping_by_cluster = self.create_mapping_by_cluster()
        self.mapping_by_token_id = self.create_mapping_by_token_id()

    def load_tokens(self):
        return pd.read_csv(self.filepath)

    def create_mapping_by_cluster(self):
        mapping_by_cluster = dict()
        for cluster, group in self.df.groupby('cluster'):
            mapping_by_cluster[cluster] = list(group.token_id)

        return mapping_by_cluster

    def create_mapping_by_token_id(self):
        mapping_by_token_id = dict()
        for token_id, cluster in zip(self.df.token_id, self.df.cluster):
            mapping_by_token_id[token_id] = cluster

        return mapping_by_token_id

    def get_cluster(self, token_id):
        return self.mapping_by_token_id[token_id]

    def get_token_id_from_cluster(self, cluster):
        return random.sample(self.mapping_by_cluster[cluster], 1)[0]

    def get_random_token(self, token_id):
        cluster = self.get_cluster(token_id)
        random_token = self.get_token_id_from_cluster(cluster)
        return random_token

test = False
if test:
    t = Tokens()
    print(f'random token for token 1550 is {t.get_random_token(1550)}')
