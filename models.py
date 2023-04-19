from pydantic import BaseModel, EmailStr, Field
import datetime


class RiderSchema (BaseModel):
    name : str = Field(default=None)
    email : EmailStr = Field(default=None)
    gender : str = Field(default=None)
    password : str = Field(default=None)
    phone_number : str = Field(default=None)


class DriverSchema (BaseModel):
    name : str = Field(default=None)
    email : EmailStr = Field(default=None)
    password : str = Field(default=None)
    phone_number : str = Field(default=None)
    license_number : str = Field(default=None)


class RiderLoginSchema (BaseModel):
    email : EmailStr
    password : str


class DriverLoginSchema (BaseModel):
    email : EmailStr
    password : str


class VehicleSchema (BaseModel):
    make : str = Field(default=None)
    model : str = Field(default=None)
    year : int = Field(default=None)
    license_plate : str = Field(default=None)
    driver_id : int = Field(default=None)
    max_capacity : int = Field(default=None)


class CardSchema (BaseModel):
    rider_id : int = Field(default=None)
    card_type : str = Field(default=None)
    card_number : str = Field(default=None)
    cardholder_name : str = Field(default=None)
    expiry_date : str = Field(default=None)
    expiry_code : int = Field(default=None)