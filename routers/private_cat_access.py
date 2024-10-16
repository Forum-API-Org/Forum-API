from fastapi import APIRouter

priv_cat_access_router = APIRouter()
@priv_cat_access_router.get("/")