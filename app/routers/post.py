from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from typing import Optional, List
from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func
# the fucntions below are also endpoints

router = APIRouter(
    prefix="/posts", # / = /{id}
    tags=['Post'] # group requests
)

# getting all posts
@router.get("/" , response_model=List[schemas.PostOut]) # retrieve a data
def get_posts(db: Session = Depends(get_db), 
current_user: int = Depends(oauth2.get_current_user), limit: int=10, skip: int=0,
search: Optional[str]=""): 
    # db is a reference of type session(an instance for our database connection)
    # and our create_user endpoint depends on it
    #cursor.execute(""" SELECT * FROM posts """) #execute a command on our db
    #posts = cursor.fetchall()
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() #offset skips posts
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id==models.Post.id, 
    isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

#creating a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post) # this path operator serves as a validation
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), 
current_user: int = Depends(oauth2.get_current_user)): # fastapi will judge the content we recieve from our path operation based on the Post module
    # get_current_user is gonna become a dependency which forces the user to be logged in before they create a post
    # cursor.execute("""INSERT INTO posts (title, content, published) 
    # VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published)) #%s are placeholders or variables reping post.title,.......
    # new_post = cursor.fetchone() # gets the returned value
    # conn.commit() #save changes after inserting
    new_post = models.Post(owner_id = current_user.id, **post.dict()) #** will unpack our dict
    db.add(new_post)
    db.commit()
    db.refresh(new_post) #retrieve
    return new_post

# getting individual posts
# retriveing posts with their id. But this is not the best practice
@router.get("/{id}", response_model=schemas.PostOut) # where {id} is a path parameter
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id),))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id==models.Post.id, 
    isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post: # raise a status code
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
        detail= f"post with id:{id} not found")
    return post

# deleting a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING * """, (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id{id} does not exist")

    if post.owner_id != current_user.id: #if the user isnt valid
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail=f"Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}" , response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), 
current_user: int = Depends(oauth2.get_current_user)): # we used a schema here

    # cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING * """,
    # (post.title, post.content, post.published, str(id),))

    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)# query to find post with an id

    post = post_query.first()#grab the post


    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"post with id{id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail=f"Not authorized to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()#send updated post back to the user
