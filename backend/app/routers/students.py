"""
Students router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Student
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()


class StudentCreate(BaseModel):
    student_id: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    course: str | None = None
    group: str | None = None


class StudentResponse(BaseModel):
    id: int
    student_id: str
    full_name: str
    email: str | None
    phone: str | None
    course: str | None
    group: str | None
    is_active: bool
    created_at: datetime
    images_count: int = 0
    has_embedding: bool = False
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[StudentResponse])
async def get_students(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    db: Session = Depends(get_db)
):
    """Get all students with face data info"""
    from ..models import StudentImage, StudentEmbedding
    
    query = db.query(Student)
    
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    
    students = query.offset(skip).limit(limit).all()
    
    # Add images count and embedding info
    result = []
    for student in students:
        images_count = db.query(StudentImage).filter(StudentImage.student_id == student.id).count()
        has_embedding = db.query(StudentEmbedding).filter(StudentEmbedding.student_id == student.id).first() is not None
        
        student_dict = {
            "id": student.id,
            "student_id": student.student_id,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "course": student.course,
            "group": student.group,
            "is_active": student.is_active,
            "created_at": student.created_at,
            "images_count": images_count,
            "has_embedding": has_embedding
        }
        result.append(StudentResponse(**student_dict))
    
    return result


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get student by ID with face data info"""
    from ..models import StudentImage, StudentEmbedding
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    images_count = db.query(StudentImage).filter(StudentImage.student_id == student.id).count()
    has_embedding = db.query(StudentEmbedding).filter(StudentEmbedding.student_id == student.id).first() is not None
    
    return StudentResponse(
        id=student.id,
        student_id=student.student_id,
        full_name=student.full_name,
        email=student.email,
        phone=student.phone,
        course=student.course,
        group=student.group,
        is_active=student.is_active,
        created_at=student.created_at,
        images_count=images_count,
        has_embedding=has_embedding
    )


@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    from ..models import StudentImage, StudentEmbedding
    
    # Check if student_id already exists
    existing = db.query(Student).filter(Student.student_id == student.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    # Add images count and embedding info
    images_count = db.query(StudentImage).filter(StudentImage.student_id == db_student.id).count()
    has_embedding = db.query(StudentEmbedding).filter(StudentEmbedding.student_id == db_student.id).first() is not None
    
    return StudentResponse(
        id=db_student.id,
        student_id=db_student.student_id,
        full_name=db_student.full_name,
        email=db_student.email,
        phone=db_student.phone,
        course=db_student.course,
        group=db_student.group,
        is_active=db_student.is_active,
        created_at=db_student.created_at,
        images_count=images_count,
        has_embedding=has_embedding
    )


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """Update student"""
    from ..models import StudentImage, StudentEmbedding
    
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student_id is being changed and if it conflicts
    if student.student_id != db_student.student_id:
        existing = db.query(Student).filter(Student.student_id == student.student_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student ID already exists")
    
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    
    # Add images count and embedding info
    images_count = db.query(StudentImage).filter(StudentImage.student_id == db_student.id).count()
    has_embedding = db.query(StudentEmbedding).filter(StudentEmbedding.student_id == db_student.id).first() is not None
    
    return StudentResponse(
        id=db_student.id,
        student_id=db_student.student_id,
        full_name=db_student.full_name,
        email=db_student.email,
        phone=db_student.phone,
        course=db_student.course,
        group=db_student.group,
        is_active=db_student.is_active,
        created_at=db_student.created_at,
        images_count=images_count,
        has_embedding=has_embedding
    )


@router.delete("/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

