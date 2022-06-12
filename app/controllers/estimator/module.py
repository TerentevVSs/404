from typing import Tuple

from torch import nn
from transformers import BertForSequenceClassification


class ArticleEstimator(nn.Module):
    def __init__(self, bert_model: BertForSequenceClassification):
        super().__init__()
        self.bert_model = bert_model
        self.pooler_dim = 768
        self.is_fake = nn.Linear(self.pooler_dim, 1)
        self.is_token_fake = nn.Linear(self.pooler_dim, 1)

    def forward(self, input_ids, attention_mask, token_type_ids, device) -> Tuple:
        out = self.bert_model.bert(input_ids=input_ids.int().to(device),
                                   attention_mask=attention_mask.to(device),
                                   token_type_ids=token_type_ids.int().to(
                                       device))
        tokens_cls = nn.Sigmoid()(
            self.is_token_fake(out.last_hidden_state)).squeeze(dim=-1)
        text_cls = nn.Sigmoid()(self.is_fake(out.pooler_output)).squeeze(dim=-1)
        return tokens_cls, text_cls