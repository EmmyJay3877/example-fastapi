from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

# this file supervises the login process and returns a token
# the fucntions below are also endpoints
router = APIRouter(tags=['Authentication'])

# in the process of logging in the user is requesting for a token
@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(database.get_db)):
    # db is a reference of of type session(an instance for our database connection)
    # OAuth2PasswordRequestForm=Depends() returns a dict with username and password to user_credentials, acts as our schemas.Userlogin
    # OAuth2PasswordRequestForm=Depends() makes sure that a fromdata is returned to user_credentials
    user = db.query(models.User).filter(models.User.email==user_credentials.username).first() # we use username instead of email

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid credentials")

    
    if not utils.verify(user_credentials.password, user.password): # if the pswrd provided is incorrect
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, details=f"Invalid Credentials")

    # gets token from the oauth2.py file
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
    


