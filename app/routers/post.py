# from psycopg2 import cursor
from unittest import result
from .. import models,schemas,utils,oauth2
from fastapi import FastAPI,Response,status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Optional, List
from sqlalchemy import func


router = APIRouter(

    prefix="/posts",
    tags=['Posts'] #to create sections in documentation (to group path operations under one heading)

)




@router.get("/sqlalchemy")
def test_posts(db: Session= Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    
    posts = db.query(models.Post).all()
    
    return posts



@router.get("/",response_model=List[schemas.PostOut])
def get_posts(db: Session= Depends(get_db),current_user:int=Depends(oauth2.get_current_user), limit: int=10, skip: int = 0, search: Optional[str] = ""): # limit,skip,search are query parameters
    # Non ORM Code------------------------------
    # cursor.execute(""" SELECT * FROM posts  """)
    # posts=cursor.fetchall()
    #--------------------------------------------
    # posts=db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    # posts along with votes count
    # by default .join() will give left inner join
    posts = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
     

    # TO return only user's posts
    # posts=db.query(models.Post).filter(current_user.id == models.Post.owner_id).all()

    return posts

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post:schemas.PostCreate,db: Session= Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    
    # NON ORM CODE ------------------------------
    # cursor.execute(""" INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING * """,(post.title,post.content,post.published)) #We could have used f"" but that would make our app vulnerable to SQL injection attacks
    # new_post=cursor.fetchone()
    # conn.commit()
    # ---------------------------------------------


    # new_post=models.Post(title=post.title,content=post.content,published=post.published) :alternative
    new_post=models.Post(owner_id=current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/{id}",response_model=schemas.PostOut) #path parameter
def get_post(id:int,response:Response,db: Session= Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    


    # Non ORM Code -------------------------------------------------
    # cursor.execute(""" SELECT * FROM posts WHERE id=%s  """,str(id))
    # post=cursor.fetchone()
    # if not post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} was not found")
    #----------------------------------------------------------------

    # normal query
    # post=db.query(models.Post).filter(models.Post.id == id).first()


    # posts with votes
    post = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} was not found")

    return  post


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db: Session= Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):


    # Non ORM code-----------------------------------------------------------------
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """,str(id),)
    # deleted_post=cursor.fetchone()
    # conn.commit()
    # if deleted_post==None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    #------------------------------------------------------------------------------
   
    post_query=db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    # Check to ensure that a user may only delete his/her own post
    if current_user.id != post.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorized to perform requested action")


    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.put("/{id}",response_model=schemas.Post)
def update_post(id:int,updated_post:schemas.PostUpdate,db: Session= Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    
    # Non ORM code-----------------------------------------------------------------
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s , published = %s WHERE id = %s RETURNING * """,(post.title,post.content,post.published,id))
    # updated_post=cursor.fetchone()
    # conn.commit()

    # if updated_post==None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    #--------------------------------------------------------------------------------

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    # Check to ensure that a user may only update his/her own post
    if current_user.id != post.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorized to perform requested action")


    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()


    return post_query.first()