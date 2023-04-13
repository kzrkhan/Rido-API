from pydantic import BaseModel, EmailStr, Field
import datetime


class RiderLoginSchema (BaseModel):
    email : EmailStr
    password : str


class RiderSchema (BaseModel):
    name : str = Field(default=None)
    email : EmailStr = Field(default=None)
    gender : str = Field(default=None)
    password : str = Field(default=None)
    phone_number : str = Field(default=None)
    payment_card_id : int = Field(default=None)