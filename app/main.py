from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings

models.Base.metadata.create_all(bind=engine)
#creates an instance of FastApi
app = FastAPI()

# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

#include our post.router
app.include_router(post.router)
#import all specific routes for user authentication
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

# # path operation / route
@app.get("/")
def root():
    return {"message": "Hello World!!!!"}