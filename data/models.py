from datetime import date
from pydantic import BaseModel, Field, constr
from typing import Literal


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

# TEmail = constr(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
# TUsername = constr(regex=r'^[a-zA-Z0-9]+$')
# TPassword = constr(min_length=8, max_length=20, regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$')
# TName = constr(regex=r'^[a-zA-Z]+$')

class User(BaseModel):
    id: int | None = None
    email: str
    username: str
    password: str
    first_name: str
    last_name: str
    is_admin: bool | None = 0

    @classmethod
    def from_query_result(cls, id, email, username, password, first_name, last_name, is_admin):
        return cls(id=id,
                   email=email,
                   username=username,
                   password = password,
                   first_name=first_name,
                   last_name=last_name,
                   is_admin=is_admin)
    
class UserResponse(BaseModel):
    id: int | None = None
    email: str
    username: str
    first_name: str
    last_name: str
    is_admin: bool | None = 0

    @classmethod
    def from_query_result(cls, id, email, username, first_name, last_name, is_admin):
        return cls(id=id,
                   email=email,
                   username=username,
                   first_name=first_name,
                   last_name=last_name,
                   is_admin=is_admin)


class Message(BaseModel):
    id: int | None
    sender_id: int
    receiver_id: int
    message_date: date
    message_text: str

    @classmethod
    def from_query_result(cls, id, sender_id, receiver_id, message_date, message_text):
        return cls(id=id,
                   sender_id=sender_id,
                   receiver_id=receiver_id,
                   message_date=message_date,
                   message_text=message_text)

    
vote_dict = {'upvote': 1, 'downvote': 0}

class Vote(BaseModel):
    user_id: int
    reply_id: int
    vote: Literal['upvote', 'downvote']
    

    @property
    def vote_value(self):
        return vote_dict[self.vote]

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