from os import environ

bind = '0.0.0.0:' + environ.get('APP_PORT', '8080')
max_requests = 1000
worker_class = 'uvicorn.workers.UvicornWorker'
workers = int(environ.get('APP_WORKERS', 1))
worker_timeout = 600
