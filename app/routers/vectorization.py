from fastapi import APIRouter, Form
from loguru import logger

from controllers.vectorization import get_vector
from db.schemas import VectorArticleOutput

router = APIRouter(tags=['vectors'])


@router.post("/common_vectorization", status_code=200,
             response_model=VectorArticleOutput)
async def common_vectorization(text: str = Form(...)):
    logger.info(f'text = {text}')
    vector = VectorArticleOutput(vector=get_vector(text))
    return vector
