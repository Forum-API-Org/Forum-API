from fastapi import APIRouter

priv_cat_access_router = APIRouter(prefix="/private_category", tags=["Private Category"])
@priv_cat_access_router.get("/")