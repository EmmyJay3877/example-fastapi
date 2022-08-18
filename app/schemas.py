from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional

# a class on how our post should look like
# our schema
# we use the basemodel to model what our schema llok like,
# just like we modelled our tables from models.py
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True # default value is true

class PostCreate(PostBase):
    pass

# respose after creating a user
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# schema for response
class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut # returns user info

    class Config:
        orm_mode = True

# new schema for the get post response, including votes
class PostOut(BaseModel):
    Post: Post
    votes: int 

    class Config:
        orm_mode = True


# schema for user
class UserCreate(BaseModel):
    email: EmailStr #ensures the email is valid
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

# schema for the token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel): # schema for tokendata
    id: Optional[str] = None


# schema for voting
class Vote(BaseModel):
    post_id: int 
    dir: conint(le=1) # <=1


