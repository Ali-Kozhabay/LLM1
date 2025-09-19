from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


from app.core.database import Base
# from app.models.user import User

class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    teacher: Mapped[List["User"]] = relationship("User", back_populates="created_courses")
    enrollments: Mapped[List["Enrollment"]] = relationship("Enrollment", back_populates="course")
    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="course")

class Lesson(Base):
    __tablename__ = "lessons"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    order_index: Mapped[int] = mapped_column(Integer)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="lessons")
    progress: Mapped[List["Progress"]] = relationship("Progress", back_populates="lesson")

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True,default=(datetime.now()+timedelta(days=30)))
    
    # Relationships
    student: Mapped["User"] = relationship("User", back_populates="enrolled_courses")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")

class Progress(Base):
    __tablename__ = "progress"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")

class Content(Base):
    __tablename__ = "contents"

    id:Mapped[int] = mapped_column(primary_key=True,unique=True)
    course_id:Mapped[int] = mapped_column(ForeignKey('courses.id'))
    link:Mapped[str] = mapped_column()
    url:Mapped[str] = mapped_column()
    
