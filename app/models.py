from pydantic import BaseModel, EmailStr, Field
import datetime

class BaseUser (BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    dob: datetime.date
    age: int
    helper: bool

class PostSchema (BaseModel):
    id : int = Field(default=None)
    title : str = Field(...)
    content : str = Field(...)

class UserSchema (BaseModel):
    fullname : str
    email : EmailStr
    password : str

class UserLoginSchema (BaseModel):
    email : EmailStr
    password : str


class Rider (BaseModel):
    name : str = Field(default=None)
    email : EmailStr = Field(default=None)
    gender : str = Field(default=None)
    password : str = Field(default=None)
    phone_number : str = Field(default=None)
    payment_card_id : int = Field(default=None)