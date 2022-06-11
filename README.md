# 404

----


## Запуск проекта локально

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
PRETRAINED_MODEL_CACHE_DIR=../.models # нужна для хранени моделей в папке проекта
```

### Команды запуска

#### Univorn Way

Внутри папки `app` выполните `python main.py` или `ENV_FILE=.env python main.py`

#### Gunicorn Way 

Внутри папки `app` выполните `gunicorn gunicorn_app:app --workers 1 --worker-class uvicorn.workers.UviocrnWorker --bind 0.0.0.:8080`

#### Docker Way

Coming soon...


#### Docker Compose Way 

Coming soon....