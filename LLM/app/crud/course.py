
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course, Enrollment, Content
from app.schemas.course import CourseCreate, CoursePublish, ContentSchema


class CourseCRUD:

    async def get_published_courses_from_db(self,db:AsyncSession):
        res= await db.execute(select(Course).where(Course.is_published==True))
        return res
    
    async def get_courses_from_db(self,db:AsyncSession):
        res= await db.execute(select(Course))
        return res

    async def get_course_from_db_by_id(self,id:int,db:AsyncSession):
        res= await db.execute(select(Course).where(Course.is_published==True and Course.id==id))
        return res
    
    async def create_course_for_db(self, db:AsyncSession, course:CourseCreate):
        db_course=Course(
            title = course.title,
            description = course.description,
            teacher_id = course.teacher_id,
            price = course.price
        )
        db.add(db_course)
        await db.commit()
        await db.refresh(db_course)
        
        return {'message':"Course is created"}
        
    async def publish_course(self,db:AsyncSession,publish: CoursePublish):
        try:
            await db.execute(update(Course).where(Course.id == publish.id).values(is_published=publish.publish))
            await db.commit()
            return {'message':'Course is published'}
        except Exception as e:
            raise e
    async def purchase_course(self,db:AsyncSession,student_id:int,course_id:int):
        try:
            db_purchase_course=Enrollment(
                student_id=student_id,
                course_id=course_id
            )
            db.add(db_purchase_course)
            await db.commit()
            await db.refresh(db_purchase_course)
        except Exception as e:
            raise e
        
    async def get_content(self,db:AsyncSession, id:int):
        try:
            res = await db.execute(select(Content).where(Content.course_id==id))
            content = res.scalar_one_or_none() 
            return {
                "link":content.link,
                "url": content.url
            }
        except Exception as e:
            raise e
    
    async def add_content(self,db:AsyncSession, id:int,link:str|None,url:str|None):
        content=Content(
                course_id=id,
                link=link,
                url=url
            )
        try:
            db.add(content)
            await db.commit()   
            await db.refresh(content)   
        except Exception as e:
            raise e
        
        
        



course_crud = CourseCRUD()
