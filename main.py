import uvicorn
from fastapi import FastAPI, APIRouter
from routers.categories import cat_router
from routers.replies import replies_router
from routers.users import user_router
from routers.votes import votes_router
from routers.messages import message_router
from routers.topics import topics_router

app = FastAPI()
app.include_router(user_router)
app.include_router(votes_router)
app.include_router(replies_router)
app.include_router(message_router)
app.include_router(cat_router)
app.include_router(topics_router)

if __name__ == "__main__":
    uvicorn.run('main:app', host="127.0.0.1", port=8000)

