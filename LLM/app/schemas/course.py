import enum

from pydantic import BaseModel


class CourseCreate(BaseModel):
    title : str
    description : str
    teacher_id : int
    price : float

    
class CoursePublish(BaseModel):
    id: int
    publish: bool


class CoursePurchase(BaseModel):
    student_id:int
    course_id:int

class ContentSchema(BaseModel):

    course_id:int
    link:str|None
    url:str|None