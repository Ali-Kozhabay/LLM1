from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user, get_current_user, get_current_superuser
from app.core.database import get_db
from app.crud.user import user_crud
from app.crud.course import course_crud
from app.models.user import User
from app.schemas.user import UserInDB, UserUpdate
from app.schemas.course import ContentSchema

router = APIRouter()

@router.get("/me", response_model=UserInDB)
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=UserInDB)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    user = await user_crud.update(db, user_id=current_user.id, user_in=user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get('/my_courses')
async def get_my_courses(db:AsyncSession=Depends(get_db),current_user:User=Depends(get_current_user)):
    try:
        return await user_crud.get_my_course(db=db,id=current_user.id)
    except Exception as e:
        raise e
    
@router.get('/get_content')
async def get_content(course_id:int, db:AsyncSession=Depends(get_db)):
    try:
        return await course_crud.get_content(db,course_id)
    except HTTPException as e:
        raise e

    
@router.post('/add_content',status_code=201)
async def add_content(content:ContentSchema=Depends(), db:AsyncSession=Depends(get_db),current_user:User=Depends(get_current_superuser)):
    try:
        await course_crud.add_content(db,content.course_id,content.link,content.url)
        return {'message':'created'}
    except HTTPException as e:
        raise e