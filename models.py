from pydantic import BaseModel, EmailStr, Field
import datetime


class RiderSignupSchema (BaseModel):
    name : str = Field(default=None)
    email : EmailStr = Field(default=None)
    gender : str = Field(default=None)
    password : str = Field(default=None)
    phone_number : str = Field(default=None)


class DriverSignupSchema (BaseModel):
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


class VehicleRegistrationSchema (BaseModel):
    make : str = Field(default=None)
    model : str = Field(default=None)
    year : int = Field(default=None)
    license_plate : str = Field(default=None)
    driver_id : int = Field(default=None)
    max_capacity : int = Field(default=None)


class CardRegistrationSchema (BaseModel):
    rider_id : int = Field(default=None)
    card_type : str = Field(default=None)
    card_number : str = Field(default=None)
    cardholder_name : str = Field(default=None)
    expiry_date : str = Field(default=None)
    security_code : str = Field(default=None)


class RideRequestSchema (BaseModel):
    rider_id : int = Field(default=None)
    pickup_lat : float = Field(default=None)
    pickup_lon : float = Field(default=None)
    dropoff_lat : float = Field(default=None)
    dropoff_lon : float = Field(default=None)


class UpdatePositionSchema (BaseModel):
    driver_id : int = Field(default=None)
    lat : float = Field(default=None)
    lon : float = Field(default=None)