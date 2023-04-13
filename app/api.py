from datetime import date
import time
import os
import shutil
import random
from fastapi import FastAPI, Depends, Query, Body, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from models import *
from pyparsing import Char
from auth.auth_handler import sign_JWT
from auth.auth_bearer import JWTBearer
from supabase import create_client, Client



app = FastAPI(
    title="Rido Developer API",
    description="This is an API for Rido App. Contact dev at khizer.khan98@gmail.com for more information.",
    version="Alpha Pre Release 0.1"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#DB Credentials
url: str = os.environ.get("RIDO_DB_URL")
key: str = os.environ.get("RIDO_DB_KEY")

supabase: Client = create_client(url, key)

#Credentials for email functionality
rido_email = "rido.rideapp@gmail.com"
rido_pswd = os.environ.get("RIDO_EMAIL_PSWD")

#List of Numbers waiting to be verified (OTP)
otp_queue = {}


@app.get("/")
async def root():
    return {"status" : "Active"}


@app.post("/ridersignup")
async def rider_signup(rider : RiderSchema):
    if rider_check_existing_email(rider):
        return {"response" : "A user with same email already exists"}
    elif rider_check_existing_phone(rider):
        return {"response" : "A user with same phone number already exists"}
    else:
        token = sign_JWT(rider.email)
        data = supabase.table("riders").insert(rider.dict()).execute()
        rider_id = ((((data.dict())["data"])[0])["rider_id"])
        return {
        "rider_id" : rider_id,
        "email" : rider.email,
        "name" : rider.name,
        "gender" : rider.gender,
        "phone number" : rider.phone_number,
        "token" : token
        }


@app.post("/riderlogin")
async def rider_login(rider : RiderLoginSchema):
    db_data = (supabase.table("riders").select("*").execute()).dict()["data"]
    for item in db_data:
        if item["email"] == rider.email and item["password"] == rider.password:
            token = sign_JWT(rider.email)
            return {
            "rider_id" : item["rider_id"],
            "email" : item["email"],
            "name" : item["name"],
            "gender" : item["gender"],
            "phone number" : item["phone_number"],
            "token" : token
            }
    return {"response" : "Email or password is incorrect"}


def rider_check_existing_email(data : RiderSchema):
    db_users = supabase.table("riders").select("*").execute()
    try:
        riders_dict = db_users.dict()
        for rider in riders_dict["data"]:
            if rider["email"] == data.email:
                return True
        return False
    except:
        return False


def rider_check_existing_phone(data : RiderSchema):    
    db_users = supabase.table("riders").select("*").execute()
    try:
        riders_dict = db_users.dict()
        for rider in riders_dict["data"]:
            if rider["phone_number"] == data.phone_number:
                return True
        return False
    except:
        return False