from datetime import datetime
from pydantic import BaseModel, Field, constr
from typing import Literal, Optional


class Topic(BaseModel):
    id: int | None
    top_name: str = Field(min_length=3, max_length=20, examples=['Engines'])
    category_id: int
    user_id: int
    topic_date: str  # date
    is_locked: bool = 0
    best_reply_id: int | None = None

    @classmethod
    def from_query_result(cls, id, top_name, category_id, user_id, topic_date, is_locked, best_reply_id):
        return cls(id=id,
                   top_name=top_name,
                   category_id=category_id,
                   user_id=user_id,
                   topic_date=topic_date,
                   is_locked=is_locked,
                   best_reply_id=best_reply_id)


class TopicResponse(BaseModel):
    top_name: str
    user_id: int
    topic_date: str  # date as a string
    is_locked: bool = False
    best_reply_id: Optional[int] = None
    replies: Optional[list['ReplyResponse']] = None

    @classmethod
    def from_query_result(cls, top_name, user_id, topic_date, is_locked, best_reply_id):
        return cls(
            top_name=top_name,
            user_id=user_id,
            topic_date=topic_date,
            is_locked=is_locked,
            best_reply_id=best_reply_id
        )


class TopicCreation(BaseModel):
    top_name: str = Field(min_length=3, max_length=20, examples=['Engines'])
    category_id: int


class Category(BaseModel):
    id: int | None
    cat_name: str = Field(min_length=3, max_length=20, examples=['Cars'])
    creator_id: int
    is_locked: bool
    is_private: bool

    @classmethod
    def from_query_result(cls, id, cat_name, creator_id, is_locked, is_private):
        return cls(id=id,
                   cat_name=cat_name,
                   creator_id=creator_id,
                   is_locked=is_locked,
                   is_private=is_private)


class CategoryResponse(BaseModel):
    cat_name: str = Field(min_length=3, max_length=20, examples=['Cars'])
    creator_id: int
    is_locked: bool
    is_private: bool
    topics: Optional[list[TopicResponse]] = None

    @classmethod
    def from_query_result(cls, cat_name, creator_id, is_locked, is_private):
        return cls(cat_name=cat_name,
                   creator_id=creator_id,
                   is_locked=is_locked,
                   is_private=is_private)


class CategoryCreation(BaseModel):
    cat_name: str = Field(min_length=3, max_length=20, examples=['Cars'])


class ReplyText(BaseModel):
    text: str
    topic_id: int


class ReplyResponse(BaseModel):
    user_id: int
    reply_date: datetime
    reply_text: str

    @classmethod
    def from_query_result(cls, user_id, reply_date, reply_text):
        return cls(user_id=user_id,
                   reply_date=reply_date,
                   reply_text=reply_text
                   )

class Reply(BaseModel):
    id: int | None
    topic_id: int
    user_id: int
    reply_date: datetime
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
    email: str = Field(max_length=45, pattern=r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', examples=['a@a.com'])     #TEmail
    username: str = Field(pattern=r'^[a-zA-Z0-9_.+-]+$', examples=['user1_+.-'])
    password: str = Field(min_length=5, max_length=20, pattern=r'^[a-zA-Z\d!@#$%^&*_.+\-]*[a-zA-Z]+[a-zA-Z\d!@#$%^&*_.+\-]*\d+[a-zA-Z\d!@#$%^&*_.+\-]*[!@#$%^&*_.+\-]+[a-zA-Z\d!@#$%^&*_.+\-]*$')
    first_name: str = Field(min_length=1, max_length=45, pattern=r'^[a-zA-Z-]+$')
    last_name: str = Field(min_length=1, max_length=45, pattern=r'^[a-zA-Z-]+$')
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

class LoginData(BaseModel):
    username: str
    password: str

class UserCategoryAccess(BaseModel):
    user_id: int
    category_id: int

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
    
class UserResponseChats(BaseModel):
    id: int | None = None
    username: str

    @classmethod
    def from_query_result(cls, id, username):
        return cls(id=id,
                   username=username,)

class UserAccessResponse(BaseModel):
    id: int | None = None
    email: str
    username: str
    first_name: str
    last_name: str
    access: str | None = None

    @classmethod
    def from_query_result(cls, id, email, username, first_name, last_name, access_type):
        access_str = "read" if access_type == 0 else "write" if access_type == 1 else None
        return cls(id=id,
                   email=email,
                   username=username,
                   first_name=first_name,
                   last_name=last_name,
                   access=access_str)

#class logindata(BaseModel):

#class registerdata(BaseModel):

class MessageText(BaseModel):
    text: str
    receiver_id: int

class MessageOutput(BaseModel):
    sender_id: int
    message_date: datetime
    message_text: str

    @classmethod
    def from_query_result(cls, sender_id, message_date, message_text):
        return cls(sender_id=sender_id,
                   message_date=message_date,
                   message_text=message_text)

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
