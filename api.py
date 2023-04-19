from datetime import date
import time
import os
import shutil
import random
from fastapi import FastAPI, Depends, Query, Body, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from models import *
from pyparsing import Char
from auth.auth_handler import sign_JWT
from auth.auth_bearer import JWTBearer
from supabase import create_client, Client
import bcrypt



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
    welcome_page = """
    <html lang="en">
  <head>
    <meta charset="utf-8">
  
    <title>Rido Dev API</title>
    <meta name="description" content="Developer API of Rido App">
    <link href="https://fonts.googleapis.com/css?family=Inter&display=swap" rel="stylesheet">
     
  </head>

  <body>
    <div>
      <div class="home-container" style="
        width: 100%;
        display: flex;
        overflow: auto;
        min-height: 100vh;
        align-items: center;
        flex-direction: column;
        justify-content: center;">
        <img
          src="https://i.ibb.co/8P9cSYb/image-18.png"
          alt="image"
          class="home-image"
          style="
            width: 356px;
            height: 104px;
            object-fit: cover;
            padding-left: 10px;
            padding-right: 10px;
          "
        />
        <h1 class="home-text" style="
          color: #4e4e4e;
          width: 262px;
          font-family:'Inter';
          font-size: 2em;
          font-style: normal;
          text-align: center;
          font-weight: 400;
          text-transform: uppercase;
        ">Developer API</h1>
        <div class="home-container1" style="
          width: 200px;
          height: 52px;
          display: flex;
          align-items: flex-start;
          flex-direction: column;
        "></div>
        <a href="https://rido-api.onrender.com/docs" class="home-link button" style="
          color: #ffffff;
          font-size: 24px;
          font-family: 'Inter';
          padding-top: 10px;
          border-width: 0px;
          padding-left: 30px;
          border-radius: 30px;
          padding-right: 30px;
          padding-bottom: 10px;
          text-decoration: none;
          background-color: #5f46ff;
        ">
          Explore
        </a>
      </div>
    </div>
  
</html>
    """
    return HTMLResponse(content=welcome_page, status_code=200)


#Signup end-point for Riders
@app.post("/rider_signup")
async def rider_signup(rider : RiderSchema):
    if rider_check_existing_email(rider):
        return {"response" : "A rider with same email already exists"}
    elif rider_check_existing_phone(rider):
        return {"response" : "A rider with same phone number already exists"}
    else:
        #Hashing passwords
        try:
            hashed_pswd = bcrypt.hashpw((rider.password).encode("utf-8"), bcrypt.gensalt())
            rider.password  = str(hashed_pswd)
        except:
            return {"response" : "Error in hashing password"}
        try:
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
        except:
            return {"response" : "DB Transaction Failed. Error inserting Rider record."}


#Login end-point for Riders
@app.post("/rider_login")
async def rider_login(rider : RiderLoginSchema):
    try:
        db_data = (supabase.table("riders").select("*").execute()).dict()["data"]
    except:
        return {"response" : "DB Transaction Failed. Error fetching Rider records."}
    for item in db_data:
        if item["email"] == rider.email and bcrypt.checkpw(rider.password.encode("utf-8"), item["password"][2:-1].encode("utf-8")):
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
    try:
        db_riders = supabase.table("riders").select("*").execute()
    except:
        return {"response" : "DB Transaction Failed. Error fetching Rider records."}
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
    try:
        db_drivers = supabase.table("drivers").select("*").execute()
    except:
        return {"response" : "DB Transaction Failed. Error fetching Driver records."}
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
    try:
        db_drivers = supabase.table("drivers").select("*").execute()
    except:
        return {"response" : "DB Transaction Failed. Error fetching Driver records."}
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
    try:   
        db_riders = supabase.table("riders").select("*").execute()
    except:
        return {"response" : "DB Transaction Failed. Error fetching Rider records."}
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
        #Hashing passwords
        try:
            hashed_pswd = bcrypt.hashpw((driver.password).encode("utf-8"), bcrypt.gensalt())
            driver.password  = str(hashed_pswd)
        except:
            return {"response" : "Error in hashing password"}        
        try:
            data = supabase.table("drivers").insert(driver.dict()).execute()
        except:
            return {"response" : "DB Transaction Failed. Error inserting Driver record."}
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
    try:
        db_data = (supabase.table("drivers").select("*").execute()).dict()["data"]
    except:
        return {"response" : "DB Transaction Failed. Error fetching Driver records."}
    for item in db_data:
        if item["email"] == driver.email and bcrypt.checkpw(driver.password.encode("utf-8"), item["password"][2:-1].encode("utf-8")):
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
    try:
        db_vehicles = supabase.table("vehicles").select("*").execute()
    except:
        return {"response" : "DB Transaction Failed. Error fetching Vehicle records."}
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
        try:
            data = supabase.table("vehicles").insert(vehicle.dict()).execute()
        except:
            return {"response" : "DB Transaction Failed. Error inserting Vehicle record."}
        
        driver_id = vehicle.driver_id

        try:
            data = supabase.table("vehicles").select("vehicle_id").eq("driver_id",driver_id).execute()
            db_dict = data.dict()
            vehicle_id = db_dict["data"][0]["vehicle_id"]
            try:
                supabase.table("drivers").update({"vehicle_id" : vehicle_id}).eq("driver_id",driver_id).execute()
            except:
                return {"response" : "DB Transaction Failed. Error inserting Driver ID."}
        except:
            return {"response" : "DB Transaction Failed. Error fetching Vehicle ID"}

        return {
        "response" : "Vehicle added successfully"
        }


#End-point to update Drivers position/coordinates in terms of Latitude and Longtitude
@app.put("/update_driver_position/{driver_id},{lat},{lon}")
async def update_driver_position(driver_id:int, lat:float, lon:float):

    try:
        data = supabase.table("driver_locations").select("*").eq("driver_id",driver_id).execute()
        db_dict = data.dict()
        if len(db_dict["data"]) == 0:
            try:
                supabase.table("driver_locations").insert({"driver_id":driver_id , "lat":lat , "lon":lon}).execute()
            except:
                return {"response" : "DB Transaction Failed. Error creating location entry for driver in db"}
        else:
            try:
                supabase.table("driver_locations").update({"lat":lat , "lon":lon}).eq("driver_id",driver_id).execute()
            except:
                return {"response" : "DB Transaction Failed. Error updating location for driver in db"}
    except:
        return {"response" : "DB Transaction Failed. Error in finding location entry for driver in db."}
    
    return {"response" : "Updated"}


#End-point to enter Payment Card information of Riders
@app.post("/add_card")
def add_payment_card(card : CardSchema):
    pass