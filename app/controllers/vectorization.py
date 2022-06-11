import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from config import get_settings
settings = get_settings()

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained(
    pretrained_model_name_or_path='sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
    cache_dir=settings.PRETRAINED_MODEL_CACHE_DIR,
)
model = AutoModel.from_pretrained(
    pretrained_model_name_or_path='sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
    cache_dir=settings.PRETRAINED_MODEL_CACHE_DIR,
)


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(
        token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9)


def get_vector(text: str) -> np.ndarray:
    # Tokenize sentences
    encoded_input = tokenizer(text, padding=True, truncation=True,
                              return_tensors='pt')

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    # Perform pooling. In this case, max pooling.
    sentence_embeddings = \
    mean_pooling(model_output, encoded_input['attention_mask'])[0]
    return sentence_embeddings
