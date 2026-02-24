# course-service/main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Course Microservice", version="1.0.0")

# 1. Models
class Course(BaseModel):
    id: int
    name: str
    credits: int
    instructor: str

class CourseCreate(BaseModel):
    name: str
    credits: int
    instructor: str

# 2. Mock Database
courses_db = [
    Course(id=1, name="Cloud Computing", credits=3, instructor="Dr. Smith"),
    Course(id=2, name="DevOps Engineering", credits=4, instructor="Prof. Johnson")
]
next_course_id = 3

# 3. Routes
@app.get("/")
def read_root():
    return {"message": "Course Microservice is running"}

@app.get("/api/courses", response_model=List[Course])
def get_all_courses():
    return courses_db

@app.post("/api/courses", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate):
    global next_course_id
    new_course = Course(id=next_course_id, **course.dict())
    courses_db.append(new_course)
    next_course_id += 1
    return new_course