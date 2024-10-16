from fastapi import APIRouter

replies_router = APIRouter(prefix = "replies", tags = ["Replies"])
@replies_router.get("/")