from fastapi import APIRouter

user_router = APIRouter(prefix = 'users', tags = ['Users'])
@user_router.get('/') #response_model=List[schemas.User]