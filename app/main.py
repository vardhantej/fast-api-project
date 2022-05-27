from operator import index, mod
from pyexpat import model
from turtle import pos, title
from typing import Optional, List
from colorama import Cursor
from fastapi import Body,FastAPI #Body is used for extracting info from body of the request eg def createPosts(body:dict=Body(...))
from pydantic import BaseModel #for defining schemas
from random import randrange
from fastapi import Response, status
from fastapi import HTTPException
from . import utils #for utility functions


app=FastAPI()
origins = ["*"]



#-----------------CORS---------------------------
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------importing env vars-------------------
from .config import settings



# -----------------routers-----------------
from .routers import post, user, auth, vote

# ----------------python driver------------
import psycopg2
from psycopg2.extras import RealDictCursor #for getting column names using psycopg2
#-------------------------------------------


# ---------for password hashing (see utils.py) ----------
from passlib.context import CryptContext
# -------------------------------------------------------

#---------------ORM dependencies-----------
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from fastapi import Depends
models.Base.metadata.create_all(bind=engine)
#------------------------------------------



#-------------------------pydantic model (see schemas.py)--------------------------
from . import schemas
# This is the schema for a post that should be received from front end side 
# This should not be confused with models.Post which is used for defining tables at the server using sqlalchemy

# class Post(BaseModel): schema for a post
#     title:str
#     content:str
#     published:bool = True default value
    #rating: Optional[int] =None for creating optional fields
#-----------------------------------------------------------------------------------

# pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")



# To connect to database non orm way 
# while True:
#     try:
#         conn=psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='postgrespwd@123',cursor_factory=RealDictCursor)
#         cursor=conn.cursor()
#         print("Database connection was successful")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error: ",error)
#         time.sleep(2)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/") #path operation or 'route'
async def read_root():
    return {"message": "Welocome to my Api"}



