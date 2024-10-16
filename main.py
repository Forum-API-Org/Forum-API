from fastapi import FastAPI, APIRouter
from routers.categories import cat_router
from routers.users import user_router

app = FastAPI()
app.include_router(user_router)
app.include_router(cat_router)