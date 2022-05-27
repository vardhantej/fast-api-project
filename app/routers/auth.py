from os import access
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model=schemas.Token)
def login(user_credentials: oauth2.OAuth2PasswordRequestForm = Depends() ,db: Session=Depends(database.get_db)):
    
    # because of OAUTH2PasswordRequestForm, 'user_credentials' should be form data {"username":"sdfsdf","password":"sdfsdfsd"} 
    
    # Search user in database
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    
    # if user does not exist then raise exception
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid credentials")

    # if user exists verify credentials
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid Credentials")

    # if credentials are correct generate and return token (see oauth2.py)
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return{"access_token":access_token, "token_type":"bearer"}








