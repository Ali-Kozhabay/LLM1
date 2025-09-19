import logging


from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.course import course_crud
from app.crud.lesson import lesson_crud
from app.models.user import User
from app.api.deps import get_current_superuser ,get_current_user
from app.schemas.course import CourseCreate, CoursePublish

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

router = APIRouter()

@router.get("/courses")
async def get_courses(db: AsyncSession = Depends(get_db)):
    logger.info("Fetching all courses")
    courses = await course_crud.get_published_courses_from_db(db)
    if not courses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No courses found")
    return {'courses:':courses.scalars().all()}


@router.get("/course/{id}")
async def get_course(id:int,db: AsyncSession = Depends(get_db)):
    logger.info("Fetching all courses")
    courses = await course_crud.get_courses_from_db(db)
    return courses.scalars().all()


@router.get("/courses_for_superuser")
async def get_courses_for_superuser(db: AsyncSession = Depends(get_db),current_user:User=Depends(get_current_superuser)):
    logger.info("Fetching all courses for superuser")
    courses = await course_crud.get_courses_from_db(db)
    return courses.scalars().all()


@router.post("/creating_courses")
async def create_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User=Depends(get_current_superuser),
    course:CourseCreate =Depends()
):
    try:
        return await course_crud.create_course_for_db(db=db,course=course)
    except Exception as e:
        raise e
    
@router.post("/publish_course")
async def publish_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User=Depends(get_current_superuser),
    publish:CoursePublish =Depends()
):
    try:
        return await course_crud.publish_course(db=db,publish=publish)
    except Exception :
        raise Exception

@router.post("/purchase_course/{course_id}",status_code=200)
async def purchase_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User=Depends(get_current_user),
):
    try:
        await course_crud.purchase_course(db=db,student_id=current_user.id,course_id=course_id)
        await lesson_crud.enroll_lesson(db,student_id=current_user.id,course_id=course_id)
        return {'message':'Course was purchased'}
    except HTTPException as e:
        return {'message': e}



    

