from datetime import date
from pydantic import BaseModel


class Categories(BaseModel):
    id: int | None
    cat_name: str
    creator_id: int
    is_locked: bool
    is_private: bool


class Topics(BaseModel):
    id: int | None
    top_name: str
    category_id: int
    user_id: int
    topic_date: date
    is_locked: bool
    best_reply_id: int


class Replies(BaseModel):
    id: int | None
    topic_id: int
    user_id: int
    reply_date: date
    reply_text: str
    replies_reply_id: int


class Users(BaseModel):
    id: int | None
    email: str
    username: str
    user_pass: str
    first_name: str
    last_name: str
    is_admin: bool


class Messages(BaseModel):
    id: int | None
    sender_id: int
    receiver_id: int
    message_date: date
    message_text: str


class Votes(BaseModel):
    user_id: int
    reply_id: int
    vote: bool


class PrivateCatAccess(BaseModel):
    category_id: int
    user_id: int
    access_type: int

