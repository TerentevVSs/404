import torch
from transformers import BertForSequenceClassification, BertTokenizer

from controllers.estimator.module import ArticleEstimator

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
# Будем использовать русскоязычный BERT от Сбербанка
trained_model_name = "/data/Models/ruBERT_8k_2L_20_epochs.pt"
sber_model_name = "sberbank-ai/ruBert-base"
tokenizer = BertTokenizer.from_pretrained(sber_model_name)
bert_model = BertForSequenceClassification.from_pretrained(sber_model_name)
bert_model = bert_model.to(device)

model = ArticleEstimator(bert_model=bert_model).to(device)
model.load_state_dict(torch.load(trained_model_name))
model.eval()


def generate_character_mask(ids, mask, tokenizer):
    """
    Вычисляем посимвольную маску фейковости каждого слова
    Parameters
    ----------
    ids: массив input_ids
    mask: маска фейковости для слов, выходной массив BERT
    tokenizer: BERT токенизатор
    Returns
    -------
    characters_mask: строка - посимвольная маска фейковости слов
    characters_recovery: строка символов проверяемой статьи
    """

    first_sep, second_sep = 0, 0
    for i in range(512):
        if ids[i] == 102 and not first_sep:
            first_sep = i
        elif ids[i] == 102:
            second_sep = i

    tokens = tokenizer.convert_ids_to_tokens(ids)[first_sep + 2:second_sep]
    mask = mask[first_sep + 1:second_sep]

    characters_recovery = ''
    characters_mask = ''
    for i in range(len(tokens)):
        if not characters_recovery:
            # если пустой добавляем сразу
            characters_recovery += tokens[i]
            characters_mask += str(mask[i]) * len(tokens[i])
        else:
            # иначе предобрабатываем BPE-токены с #
            if tokens[i][0] == "#" and len(tokens[i]) > 1:
                for j in tokens[i]:
                    if j != "#":
                        characters_recovery += j
                        characters_mask += str(mask[i])
            else:
                # не ставим пробелы перед знаками препинания
                if tokens[i] not in [".", ",", "!", "?", ":", ";"]:
                    characters_recovery += " "
                    characters_mask += str(mask[i])
                characters_recovery += tokens[i]
                characters_mask += str(mask[i]) * len(tokens[i])
    return characters_mask, characters_recovery


def estimate_new_article(true_article: str, new_article: str,
                         tokenizer=tokenizer,
                         model=model,
                         device=device):
    """
    Вычисляем посимвольную маску фейковости каждого слова
    и общую фейковость статьи
    Parameters
    ----------
    true_article: строка - правдивая статья
    new_article: строка - статья, которую проверяем
    tokenizer: BERT токенизатор
    model: модель для оценки статьи
    device: CPU или GPU
    Returns
    -------
    article_mask: строка - посимвольная маска фейковости слов
    проверяемой статьи
    percent_of_true: правдивость статьи в процентах
    chars: строка символов проверяемой статьи
    """

    # Берем первые только 400 токенов статьи
    truncated_true_article = tokenizer.decode(
        tokenizer.encode(true_article)[1:400])
    # Будем оценивать новую статью частями по 100 токенов
    max_new_article_len = 100
    new_article_tokens = tokenizer.encode(new_article)[1:-1]
    new_article_len = len(new_article_tokens)
    parts_count = 1 + (new_article_len // max_new_article_len)

    percent_of_true = 0
    article_mask = ''
    chars = ''
    for i in range(parts_count):
        # Вернем к текстовому виду часть из 100 токенов
        new_article_part = tokenizer.decode(
            new_article_tokens[:max_new_article_len])
        new_article_tokens = new_article_tokens[max_new_article_len:]
        data = tokenizer(truncated_true_article,
                         new_article_part,
                         return_tensors="pt",
                         max_length=512,
                         padding='max_length')

        with torch.no_grad():
            (mask, text_class) = model(
                data["input_ids"].view((1, -1)).to(device),
                data["attention_mask"].view((1, -1)).to(device),
                data["token_type_ids"].view((1, -1)).to(device),
                device)
        mask = list(((mask.cpu().view((-1)) >= 0.5) * 1).numpy())
        percent_of_true += 100 * (1 - text_class.item())
        mask_part, characters_recov = generate_character_mask(
            data["input_ids"][0],
            mask,
            tokenizer)
        article_mask += mask_part
        chars += characters_recov
    percent_of_true /= parts_count
    percent_of_true = round(percent_of_true)
    return article_mask, percent_of_true, chars
