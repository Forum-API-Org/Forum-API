from fastapi import APIRouter

user_router = APIRouter()
@user_router.get('/users', response_model=List[schemas.User])