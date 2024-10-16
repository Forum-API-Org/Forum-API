from datetime import date
from pydantic import BaseModel, Field


class Category(BaseModel):
    id: int | None
    cat_name: str
    creator_id: int
    is_locked: bool
    is_private: bool


class Topic(BaseModel):
    id: int | None
    top_name: str
    category_id: int
    user_id: int
    topic_date: date
    is_locked: bool
    best_reply_id: int


class Reply(BaseModel):
    id: int | None
    topic_id: int
    user_id: int
    reply_date: date
    reply_text: str
    #replies_reply_id: int

    @classmethod
    def from_query_result(cls, id, topic_id, user_id, reply_date, reply_text):
        return cls(id=id,
                   topic_id=topic_id,
                   user_id=user_id,
                   reply_date=reply_date,
                   reply_text=reply_text
        )


class User(BaseModel):
    id: int | None = None
    email: str
    username: str
    user_pass: str
    first_name: str
    last_name: str
    is_admin: bool | None = None

    @classmethod
    def from_query_result(cls, id, email, username, user_pass, first_name, last_name, is_admin):
        return cls(id=id,
                   email=email,
                   username=username,
                   user_pass = user_pass,
                   first_name=first_name,
                   last_name=last_name,
                   is_admin=is_admin)


class Message(BaseModel):
    id: int | None
    sender_id: int
    receiver_id: int
    message_date: date
    message_text: str


class Vote(BaseModel):
    user_id: int
    reply_id: int
    vote: bool

    @classmethod
    def from_query_result(cls, user_id, reply_id, vote):
        return cls(user_id=user_id,
                   reply_id=reply_id,
                   vote=vote
        )


class PrivateCatAccess(BaseModel):
    category_id: int
    user_id: int
    access_type: int

class LoginData(BaseModel):
    username: str
    password: str