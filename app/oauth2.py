# To generate Tokens, verify tokens etc
from fastapi import Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from . import schemas, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from . import database
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:    
        payload = jwt.decode(token,SECRET_KEY,[ALGORITHM])
        id:str=payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


# pass this function as a dependency in a path operation functions for eg: 
#   @router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
#   def create_posts(post:schemas.PostCreate,db: Session= Depends(get_db),user_id:int=Depends(oauth.get_current_user)): 
# Doing this will raise an exception if the user is not logged in or an imposter is trying to perform an operation
# All this function does is to call verify_access_token() with the token and the credentials_error. In other implementaions, this will also fetch user details
def get_current_user(token: str= Depends(oauth2_scheme),db:Session=Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials",headers={"WWW-Authenticate":"Bearer"})

    token = verify_access_token(token,credentials_exception) 
    user = db.query(models.User).filter(models.User.id == token.id).first()


    return user 