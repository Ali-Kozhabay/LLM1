from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Enrollment

class LessonCRUD:

    async def enroll_lesson(self,db:AsyncSession,student_id:int,course_id:int):
        lesson=Enrollment(
            student_id=student_id,
            course_id=course_id,
            enrolled_at=datetime.now(),
            completed_at=datetime.now()+datetime.timedelta(days=30)
        )

lesson_crud = LessonCRUD()