from datetime import date
import time
import os
import shutil
import random
from fastapi import FastAPI, Depends, Query, Body, UploadFile, File, Form, HTTPException
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
from cryptography.fernet import Fernet
from geopy.distance import geodesic
from geopy.geocoders import OpenCage
import requests
import aiohttp
import asyncio


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


#Fernet initialization
fernet = Fernet((os.environ.get("RIDO_FERNET_KEY")).encode("utf-8"))


#OpenCage initialization\
geolocator = OpenCage(api_key = os.environ.get("RIDO_OPENCAGE_KEY"))


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
async def rider_signup(rider : RiderSignupSchema):
    if rider_check_existing_email(rider):
        raise HTTPException(status_code=400, detail="A rider with same email already exists")
    elif rider_check_existing_phone(rider):
        raise HTTPException(status_code=400, detail="A rider with same phone number already exists")
    else:
        #Hashing passwords
        try:
            hashed_pswd = hash_pswd(rider.password)
            rider.password  = hashed_pswd
        except:
            raise HTTPException(status_code=500, detail="Error in hashing password")
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
            raise HTTPException(status_code=500, detail="DB Transaction Failed. Error inserting Rider record.")


#Login end-point for Riders
@app.post("/rider_login")
async def rider_login(rider : RiderLoginSchema):
    try:
        db_data = (supabase.table("riders").select("*").execute()).dict()["data"]
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Rider records.")
    for item in db_data:
        if item["email"] == rider.email and verify_pswd(rider.password , item["password"]):
            token = sign_JWT(rider.email)
            return {
            "rider_id" : item["rider_id"],
            "email" : item["email"],
            "name" : item["name"],
            "gender" : item["gender"],
            "phone number" : item["phone_number"],
            "token" : token
            }
    raise HTTPException(status_code=400, detail="Email or password is incorrect")


#Function to check if the email exists for the said Rider
def rider_check_existing_email(data : RiderSignupSchema):
    try:
        db_riders = supabase.table("riders").select("*").execute()
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Rider records.")
    try:
        riders_dict = db_riders.dict()
        for rider in riders_dict["data"]:
            if rider["email"] == data.email:
                return True
        return False
    except:
        return False


#Function to check if the email exists for the said Driver
def driver_check_existing_email(data : DriverSignupSchema):
    try:
        db_drivers = supabase.table("drivers").select("*").execute()
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Driver records.")
    try:
        drivers_dict = db_drivers.dict()
        for driver in drivers_dict["data"]:
            if driver["email"] == data.email:
                return True
        return False
    except:
        return False


#Function to check if the phone number exists for the said Driver
def driver_check_existing_phone(data : DriverSignupSchema):
    try:
        db_drivers = supabase.table("drivers").select("*").execute()
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Driver records.")
    try:
        drivers_dict = db_drivers.dict()
        for driver in drivers_dict["data"]:
            if driver["phone_number"] == data.phone_number:
                return True
        return False
    except:
        return False 


#Function to check if the phone number exists for the said Rider
def rider_check_existing_phone(data : RiderSignupSchema):
    try:   
        db_riders = supabase.table("riders").select("*").execute()
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Rider records.")
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
async def driver_signup(driver : DriverSignupSchema):
    if driver_check_existing_email(driver):
        raise HTTPException(status_code=400, detail="A driver with same email already exists")
    elif driver_check_existing_phone(driver):
        raise HTTPException(status_code=400, detail="A driver with same phone number already exists")
    else:
        token = sign_JWT(driver.email)
        #Hashing passwords
        try:
            hashed_pswd = hash_pswd(driver.password)
            driver.password  = hashed_pswd
        except:
            raise HTTPException(status_code=500, detail="Error in hashing password")      
        try:
            data = supabase.table("drivers").insert(driver.dict()).execute()
        except:
            raise HTTPException(status_code=500, detail="DB Transaction Failed. Error inserting Driver record.")
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
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Driver records.")
    for item in db_data:
        if item["email"] == driver.email and verify_pswd(driver.password , item["password"]):
            token = sign_JWT(driver.email)
            return {
            "driver_id" : item["driver_id"],
            "email" : item["email"],
            "name" : item["name"],
            "phone number" : item["phone_number"],
            "token" : token
            }
    raise HTTPException(status_code=400, detail="Email or password is incorrect")
    return {"response" : "Email or password is incorrect"}


#Function to check if a vehicle with a certain license plate exists in the records
def check_existing_license_plate(data : VehicleRegistrationSchema):
    try:
        db_vehicles = supabase.table("vehicles").select("*").execute()
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Vehicle records.")
    try:
        vehicles_dict = db_vehicles.dict()
        for vehicle in vehicles_dict["data"]:
            if vehicle["license_plate"] == data.license_plate:
                return True
        return False
    except:
        return False


#End-point to enter Vehicle details for Drivers
@app.post("/add_vehicle", dependencies=[Depends(JWTBearer())])
async def add_vehicle(vehicle : VehicleRegistrationSchema):
    
    if check_existing_license_plate(vehicle):
        raise HTTPException(status_code=400, detail="A vehicle with same license plate exists")
    else:
        try:
            data = supabase.table("vehicles").insert(vehicle.dict()).execute()
        except:
            raise HTTPException(status_code=500, detail="DB Transaction Failed. Error inserting Vehicle records.")
        
        driver_id = vehicle.driver_id

        try:
            data = supabase.table("vehicles").select("vehicle_id").eq("driver_id",driver_id).execute()
            db_dict = data.dict()
            vehicle_id = db_dict["data"][0]["vehicle_id"]
            try:
                supabase.table("drivers").update({"vehicle_id" : vehicle_id}).eq("driver_id",driver_id).execute()
            except:
                raise HTTPException(status_code=500, detail="DB Transaction Failed. Error inserting Driver ID")
        except:
            raise HTTPException(status_code=500, detail="DB Transaction Failed. Error fetching Vehicle ID")

        return {
        "response" : "Vehicle added successfully"
        }


#End-point to update Drivers position/coordinates in terms of Latitude and Longtitude
@app.put("/update_driver_position", dependencies=[Depends(JWTBearer())])
async def update_driver_position(update_position : UpdatePositionSchema):

    try:
        data = supabase.table("driver_locations").select("*").eq("driver_id",update_position.driver_id).execute()
        db_dict = data.dict()
        if len(db_dict["data"]) == 0:
            try:
                supabase.table("driver_locations").insert({"driver_id":update_position.driver_id , "lat":update_position.lat , "lon":update_position.lon}).execute()
            except:
                raise HTTPException(status_code=500, detail="Error creating location entry fo Driver in DB")
        else:
            try:
                supabase.table("driver_locations").update({"lat":update_position.lat , "lon":update_position.lon}).eq("driver_id",update_position.driver_id).execute()
            except:
                raise HTTPException(status_code=500, detail="DB Transaction Failed. Error updating location for Driver in DB")
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error in finding location entry for Driver in DB")
    
    return {"response" : "Updated"}


#End-point to enter Payment Card information of Riders
@app.post("/add_card", dependencies=[Depends(JWTBearer())])
async def add_payment_card(card : CardRegistrationSchema):
    
    #Encrypting Security Code
    encrypted_cvv = encrypt_cvv(card.security_code)
    card.security_code = encrypted_cvv
    
    try:
        supabase.table("card_details").insert(card.dict()).execute()
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error in inserting Card record.")
    
    return {"response" : "Card added successfully"}


def encrypt_cvv (cvv):
    encrypted_cvv = fernet.encrypt(str(cvv).encode("utf-8"))
    return str(encrypted_cvv)


def decrypt_cvv (cvv):
    decrypted_cvv = fernet.decrypt(cvv[2:-1].encode("utf-8"))
    return str(decrypt_cvv)


def hash_pswd (plain_pswd):
    hashed_pswd = bcrypt.hashpw(plain_pswd.encode("utf-8"), bcrypt.gensalt())
    return str(hashed_pswd)


def verify_pswd (plain_pswd, hashed_pswd):
    if bcrypt.checkpw(plain_pswd.encode("utf-8"), hashed_pswd[2:-1].encode("utf-8")):
        return True
    else:
        return False


#End-point to Create Ride requests from Riders
@app.post("/request_ride")
async def request_ride(ride_request : RideRequestSchema):
    
    busy_nearby_list = busy_drivers_nearby(ride_request.pickup_lat , ride_request.pickup_lon)

    if busy_nearby_list:

        target_drivers = []

        empty_seat_list = empty_seat_common_dropoff(ride_request.dropoff_lat , ride_request.dropoff_lon)

        if empty_seat_list:

            for busy_driver in busy_nearby_list:
                for empty_seat_driver in empty_seat_list:

                    if busy_driver["driver_id"] == empty_seat_driver["driver_id"]:
                        target_drivers.append(busy_driver)

            for driver in target_drivers:
                data = post_on_request_board(driver["driver_id"], ride_request.rider_id, ride_request.pickup_lat, ride_request.pickup_lon, ride_request.dropoff_lat, ride_request.dropoff_lon)
                id = data["data"][0]["id"]
                url = f"https://rido-api.onrender.com/request_watcher?id={id}"
                asyncio.create_task(send_request(url))

            return {"response" : "Request created"}

    else:

        online_nearby_list = online_drivers_nearby(ride_request.pickup_lat , ride_request.pickup_lon)

        if online_nearby_list:

            for driver in online_nearby_list:
                data = post_on_request_board(driver["driver_id"], ride_request.rider_id, ride_request.pickup_lat, ride_request.pickup_lon, ride_request.dropoff_lat, ride_request.dropoff_lon)
                id = data["id"]
                url = f"https://rido-api.onrender.com/request_watcher?id={id}"
                asyncio.create_task(send_request(url))
            
            return {"response" : "Request created"}
        
        raise HTTPException(status_code=400, detail="No drivers available")
        


#Function to find Busy drivers (Drivers who are in-process of completing a trip) in 'X'km radius of the Riders current location
#Returns list in the format [{'driver_id': 5}, {'driver_id': 4}]
def busy_drivers_nearby(pickup_lat : float, pickup_lon : float):
    
    
    data = supabase.table("drivers").select("driver_locations(driver_id, lat, lon)").eq("activity_status", "busy").execute()
    db_dict = data.dict()
    
    prospect_list = []

    for record in db_dict["data"]:
        prospect_list.append(record["driver_locations"][0])
    
    nearby_list = []

    rider_point = (pickup_lat, pickup_lon)

    radius = 1.5

    for driver in prospect_list:
        
        driver_point = (driver["lat"], driver["lon"])
        
        distance = geodesic(driver_point, rider_point).kilometers

        if distance <= radius:
            nearby_list.append({"driver_id" : driver["driver_id"]})
    
    return nearby_list
    

#This function finds the drivers from the "nearby_list" that have vacant seats in their car and are going towards an approximate common drop-off location
#Returns a list in the format [{'driver_id': 5}, {'driver_id': 4}] of all Drivers in the nearby_list that have free seat and are going to a destination in "X" km radius of the first dropoff of the trip
def empty_seat_common_dropoff(dropoff_lat : float, dropoff_lon : float):
    
    data = supabase.table("shared_trips").select("trip_id, driver_id, seats_occupied, shared_trip_details(dropoff_lat, dropoff_lon)").eq("status", "in progress").execute()
    
    seat_dict = data.dict()
    
    available_common_dropoff_list = []

    data = supabase.table("vehicles").select("driver_id, max_capacity").execute()
    
    capacity_dict = data.dict()

    for record in seat_dict["data"]:
        
        driver_id = record["driver_id"]
        seats_occupied = record["seats_occupied"]
        db_dropoff_lat = record["shared_trip_details"][0]["dropoff_lat"]
        db_dropoff_lon = record["shared_trip_details"][0]["dropoff_lon"]

        radius = 1.5

        for entry in capacity_dict["data"]:
            if int(entry["driver_id"]) == int(driver_id):
                if int(seats_occupied) < int(entry["max_capacity"]):
                    distance = geodesic((db_dropoff_lat, db_dropoff_lon) , (dropoff_lat, dropoff_lon)).kilometers
                    if distance <= radius:
                        available_common_dropoff_list.append({"driver_id" : driver_id})
    
    return available_common_dropoff_list


#Function to find Online drivers (Drivers who are logged in and are waiting to find a ride) in the given radius of "X" km
def online_drivers_nearby(pickup_lat : float, pickup_lon : float):
    
    data = supabase.table("drivers").select("driver_locations(driver_id, lat, lon)").eq("activity_status", "online").execute()
    db_dict = data.dict()
    
    prospect_list = []

    for record in db_dict["data"]:
        prospect_list.append(record["driver_locations"][0])
    
    nearby_list = []

    rider_point = (pickup_lat, pickup_lon)

    radius = 3

    for driver in prospect_list:
        
        driver_point = (driver["lat"], driver["lon"])
        
        distance = geodesic(driver_point, rider_point).kilometers

        if distance <= radius:
            nearby_list.append({"driver_id" : driver["driver_id"]})
    
    return nearby_list


#Function to post ride request to selected drivers
def post_on_request_board(driver_id : int, rider_id : int, pickup_lat : float, pickup_lon : float, dropoff_lat : float, dropoff_lon : float):
    
    pickup_location = geolocator.reverse(f"{pickup_lat}, {pickup_lon}")

    dropoff_location = geolocator.reverse(f"{dropoff_lat}, {dropoff_lon}")

    post = {
        "driver_id" : driver_id,
        "rider_id" : rider_id,
        "pickup_address" : str(pickup_location),
        "dropoff_address" : str(dropoff_location),
        "pickup_lat" : pickup_lat,
        "pickup_lon" : pickup_lon,
        "dropoff_lat" : dropoff_lat,
        "dropoff_lon" : dropoff_lon
    }

    data = supabase.table("request_board").insert(post).execute()
    
    return data.dict()


#Endpoint to watch request in request_board and expire/delete it after 15 seconds
@app.post("/request_watcher")
async def request_watcher(id : int):
    time.sleep(15.0)
    try:
        supabase.table("request_board").delete().eq("id" , id).execute()
        return {"response" : "Successfully handled"}
    except:
        raise HTTPException(status_code=500, detail="DB Transaction Failed. Error in deleting request in request_board")


#async request sending function to prevent the entire code from blocking
async def send_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.post(url) as response:
            return await response.text()


@app.get("/sqltest")
async def sqltest():
    
    print(post_on_request_board(6,24,24.940426,67.042131,24.832570,67.033961))

    return {"response" : "Success"}

    #nearby_list = busy_drivers_nearby(24.921527,67.130166)

    #print(empty_seat_common_dropoff(nearby_list,24.948310,67.052736))

    """data = supabase.table("drivers").select("driver_locations(driver_id, lat, lon)").eq("activity_status", "busy").execute()
    db_dict = data.dict()
    
    response_list = []

    for record in db_dict["data"]:
        response_list.append(record["driver_locations"][0])
        
    print(response_list)"""