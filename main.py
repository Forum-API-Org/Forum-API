from fastapi import FastAPI, APIRouter
from routers.categories import cat_router
from routers.replies import replies_router
from routers.users import user_router
from routers.votes import votes_router

app = FastAPI()
app.include_router(user_router)
app.include_router(cat_router)
app.include_router(votes_router)
app.include_router(replies_router)