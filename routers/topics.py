from fastapi import APIRouter

topic_router = APIRouter(prefix="/topics", tags=["Topics"])
@topic_router.get('/')