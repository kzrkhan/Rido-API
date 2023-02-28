from datetime import date
import time
import os
import shutil
from fastapi import FastAPI, Depends, Query, Body, UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional

from pyparsing import Char
from app.models import PostSchema, UserLoginSchema, UserSchema
from app.auth.auth_handler import sign_JWT
from app.auth.auth_bearer import JWTBearer
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware
from geopy.distance import geodesic


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