import json
import logging

from fastapi import APIRouter, Form
from starlette.responses import Response

from controllers.vectorization import get_vector

from loguru import logger

router = APIRouter(tags=['vectors'])


@router.post("/common_vectorization", status_code=200)
async def common_vectorization(text: str = Form(...)):
    logger.info(f'text = {text}')
    vector = get_vector(text)
    vector = json.dumps(vector, ensure_ascii=False, indent=4)
    return Response(content=vector)
