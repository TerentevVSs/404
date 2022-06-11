import pickle
from fastapi import FastAPI, Response, Form, Request
import json
import utils
from vectorization import get_vector

logger = utils.get_logger('api.py', 'log.txt')
app = FastAPI()


@api_app.post("/common_vectorization", status_code=200)
async def common_vectorization(text: str = Form(...)):
    logger.info(f'text = {text}')
    vector = get_vector(text)
    vector = json.dumps(vector, ensure_ascii=False, indent=4)
    return Response(content=vector)
