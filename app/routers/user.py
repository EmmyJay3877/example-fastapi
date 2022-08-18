from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db
# the fucntions below are also endpoints

router = APIRouter(
    prefix="/users", # / = /{id}
    tags=['Users'] # group requests
)


# create new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # db is a reference of of type session(an instance for our database connection)
    # and our create_user endpoint depends on it
    # create the hash of the password
    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password 
    new_user = models.User(**user.dict()) #** will unpack our dict
    db.add(new_user)
    db.commit()
    db.refresh(new_user) #retrieve

    return new_user


@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Users with the id: {id} was not found.")

    return user



