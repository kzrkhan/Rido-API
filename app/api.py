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


#Default end-point of API
@app.get("/")
async def root():
    return {"status" : "Active"}


#Signup end-point for Riders
@app.post("/rider_signup")
async def rider_signup(rider : RiderSchema):
    if rider_check_existing_email(rider):
        return {"response" : "A rider with same email already exists"}
    elif rider_check_existing_phone(rider):
        return {"response" : "A rider with same phone number already exists"}
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


#Login end-point for Riders
@app.post("/rider_login")
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


#Function to check if the email exists for the said Rider
def rider_check_existing_email(data : RiderSchema):
    db_riders = supabase.table("riders").select("*").execute()
    try:
        riders_dict = db_riders.dict()
        for rider in riders_dict["data"]:
            if rider["email"] == data.email:
                return True
        return False
    except:
        return False


#Function to check if the email exists for the said Driver
def driver_check_existing_email(data : DriverSchema):
    db_drivers = supabase.table("drivers").select("*").execute()
    try:
        drivers_dict = db_drivers.dict()
        for driver in drivers_dict["data"]:
            if driver["email"] == data.email:
                return True
        return False
    except:
        return False


#Function to check if the phone number exists for the said Driver
def driver_check_existing_phone(data : DriverSchema):    
    db_drivers = supabase.table("drivers").select("*").execute()
    try:
        drivers_dict = db_drivers.dict()
        for driver in drivers_dict["data"]:
            if driver["phone_number"] == data.phone_number:
                return True
        return False
    except:
        return False 


#Function to check if the phone number exists for the said Rider
def rider_check_existing_phone(data : RiderSchema):    
    db_riders = supabase.table("riders").select("*").execute()
    try:
        riders_dict = db_riders.dict()
        for rider in riders_dict["data"]:
            if rider["phone_number"] == data.phone_number:
                return True
        return False
    except:
        return False


#Signup end-point for Drivers
@app.post("/driver_signup")
async def driver_signup(driver : DriverSchema):
    if driver_check_existing_email(driver):
        return {"response" : "A driver with same email already exists"}
    elif driver_check_existing_phone(driver):
        return {"response" : "A driver with same phone number already exists"}
    else:
        token = sign_JWT(driver.email)
        data = supabase.table("drivers").insert(driver.dict()).execute()
        driver_id = ((((data.dict())["data"])[0])["driver_id"])
        return {
        "driver_id" : driver_id,
        "email" : driver.email,
        "name" : driver.name,
        "phone number" : driver.phone_number,
        "token" : token
        }


#Login end-point for Drivers
@app.post("/driver_login")
async def driver_login(driver : DriverLoginSchema):
    db_data = (supabase.table("drivers").select("*").execute()).dict()["data"]
    for item in db_data:
        if item["email"] == driver.email and item["password"] == driver.password:
            token = sign_JWT(driver.email)
            return {
            "driver_id" : item["driver_id"],
            "email" : item["email"],
            "name" : item["name"],
            "phone number" : item["phone_number"],
            "token" : token
            }
    return {"response" : "Email or password is incorrect"}


#Function to check if a vehicle with a certain license plate exists in the records
def check_existing_license_plate(data : VehicleSchema):
    db_vehicles = supabase.table("vehicles").select("*").execute()
    try:
        vehicles_dict = db_vehicles.dict()
        for vehicle in vehicles_dict["data"]:
            if vehicle["license_plate"] == data.license_plate:
                return True
        return False
    except:
        return False


#End-point to enter Vehicle details for Drivers
@app.post("/add_vehicle")
async def add_vehicle(vehicle : VehicleSchema):
    
    if check_existing_license_plate(vehicle):
        return {"response" : "A vehicle with same license plate exists"}
    else:
        data = supabase.table("vehicles").insert(vehicle.dict()).execute()
        driver_id = ((((data.dict())["data"])[0])["driver_id"])
        return {
        "response" : "Vehicle added successfully"
        }


#End-point to update Drivers position/coordinates in terms of Latitude and Longtitude
@app.post("/update_driver_position/{driver_id},{lat},{lon}")
async def update_driver_position(driver_id:int, lat:float, lon:float):

    try:
        data = supabase.table("driver_locations").select("*").eq("driver_id",driver_id).execute()
        db_dict = data.dict()
        if len(db_dict["data"]) == 0:
            try:
                supabase.table("driver_locations").insert({"driver_id":driver_id , "lat":lat , "lon":lon}).execute()
            except:
                return {"response" : "Error creating location entry for driver in db"}
        else:
            try:
                supabase.table("driver_locations").update({"lat":lat , "lon":lon}).eq("driver_id",driver_id).execute()
            except:
                return {"response" : "Error updating location for driver in db"}
    except:
        return {"response" : "Error in finding location entry for driver in db"}
    
    return {"response" : "Updated"}