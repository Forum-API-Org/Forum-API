from datetime import datetime
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
    topic_date: str  # date
    is_locked: bool
    best_reply_id: int | None = None

class ReplyText(BaseModel):
    text: str

class Reply(BaseModel):
    id: int | None
    topic_id: int
    user_id: int
    reply_date: str  # date
    reply_text: str
    replies_reply_id: int | None = None

    @classmethod
    def from_query_result(cls, id, topic_id, user_id, reply_date, reply_text):
        return cls(id=id,
                   topic_id=topic_id,
                   user_id=user_id,
                   reply_date=reply_date,
                   reply_text=reply_text
                   )
    
    def __str__(self):
        return self.reply_text


TEmail = constr(pattern=r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$')
TUsername = constr(pattern=r'^[a-zA-Z0-9_.+-]+$')
TPassword = constr(min_length=5, max_length=20, pattern=r'^[a-zA-Z0-9_.+-]+$')
TName = constr(pattern=r'^[a-zA-Z]+$')


class User(BaseModel):
    id: int | None = None
    email: TEmail
    username: TUsername
    password: TPassword
    first_name: TName
    last_name: TName
    is_admin: bool | None = 0

    @classmethod
    def from_query_result(cls, id, email, username, password, first_name, last_name, is_admin):
        return cls(id=id,
                   email=email,
                   username=username,
                   password=password,
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

#class logindata(BaseModel):

#class registerdata(BaseModel):

class MessageText(BaseModel):
    text: str

class Message(BaseModel):
    id: int | None
    sender_id: int
    receiver_id: int
    message_date: datetime
    message_text: str

    @classmethod
    def from_query_result(cls, id, sender_id, receiver_id, message_date, message_text):
        return cls(id=id,
                   sender_id=sender_id,
                   receiver_id=receiver_id,
                   message_date=message_date,
                   message_text=message_text)


vote_dict = {'upvote': 1, 'downvote': 0}


class VoteResult(BaseModel):
    vote: Literal['upvote', 'downvote']
    
    @property
    def vote_value(self):
        return vote_dict[self.vote]

# class Vote(BaseModel):
#     user_id: int
#     reply_id: int
#     vote: Literal['upvote', 'downvote']


#     @property
#     def vote_value(self):
#         return vote_dict[self.vote]

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
