from fastapi import APIRouter

cat_router = APIRouter(prefix="/categories", tags=["Categories"])
@get