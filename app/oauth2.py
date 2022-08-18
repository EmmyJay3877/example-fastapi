from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

# this file creates and verifies a token, also returns a tokendata

# this will give us the route to acess our token
# which leads us to our login function in the auth.py file
# oauth2_scheme is an instace variable of ouath2passwordbearer() class
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


# SECRET_KEY
# Alogorithm
# Expiration time
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy() #payload
    # current time + 30mins
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    # use  try incase of an error
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # extract the data
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


# Depends(oauth2_scheme) means, only if the token is generated from the tokenurl and we're authenticated then we can get the user
# verifies the id and fetches the user from our model(database), we depend on oath2_scheme whenever we want acess to a token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # db is a reference of of type session(an instance for our database connection)
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
    detail=f"could not validate credentials", headers={"WWW-Authenticate": "Bearer"})


    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id==token.id).first()

    return user