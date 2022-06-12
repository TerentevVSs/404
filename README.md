# 404

----
## Эксперименты:

Разработка кластеризации:
Experiments/fast_kmeans_via_faiss.ipynb

Разработка модели:
Experiments/BERT_training.ipynb

Логи экспериментов с моделью на wandb.ai
https://wandb.ai/diht404/ruBERT?workspace=user-diht404


## Запуск проекта локально

### Зависимости

Бэковые зависимости лежат в файле `app/requirements.txt`

```bash
pip install -r app/requirements.txt

```

---
### Переменные окружения

Создайте в корне проекта файл с переменными окружения. 
По умолчанию его название `.env`, но можно переопределить при запуске 
приложения 
```bash
ENV_FILE=your_file.env python...
```
В этом файле объявите следующие перменные
```bash
DEBUG=True 
PROJECT_NAME="FAKE NEWS"
DESCRIPTION="Распознаем фейки, проверяем новости"
APP_PORT=8080 
VERSION=0.0.1
PRETRAINED_MODEL_CACHE_DIR=../.models # нужна для хранения моделей в папке проекта

POSTGRES_DB=database
POSTGRES_USER=username
POSTGRES_PASSWORD=secret
POSTGRES_PORT=5432
POSTGRES_HOST=127.0.0.1 # если запускаете через docker-compose лучше указать название сервиса
```

### Команды запуска

#### Univorn Way

Внутри папки `app` выполните 

```bash
python main.py
```
 или 
```bash
ENV_FILE=.env python main.py
```

#### Gunicorn Way 

Внутри папки `app` выполните 
```bash
gunicorn gunicorn_app:app --workers 1  --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.:8080
```


#### Docker Compose Way 

Перед запуском через Docker Compose также необходимо создать файл с перменными 
окружения `.env` или экспортировать их в среду. 

**ВАЖНО:** Для правильной работы в docker-compose без внешнего порта для БД, 
назначьте `POSTGRES_HOST=database`.

Для запуска проекта со всеми сервисами одновременно необходимо выполнить

```bash
docker-compose  up --build
```

---
### Миграции

Управление версиями БД осущестляется с помощью пакета `alembic`. 
#### Создание миграции
Для автоматического создания миграции при изменении схемы
нужно выполнить
```bash
alembic revision --autogenerate -m "Name of migration"
```
#### Применение миграций
Для обновления/инициализации таблиц через миграции выполните 
внутри папки `app` команду
```bash
alembic upgrade head
```

