"""
Authentication router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from ..database import get_db
from ..models import User, Student
from ..config import API_URL
from pydantic import BaseModel
import os

router = APIRouter()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None
    role: str
    student_id: int | None
    is_active: bool
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "student_id": user.student_id
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


@router.post("/login-json", response_model=Token)
async def login_json(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint (JSON)"""
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not user.check_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "student_id": user.student_id
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.post("/register")
async def register(
    username: str,
    password: str,
    email: str | None = None,
    role: str = "student",
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Register new user (admin only)"""
    # Check if username exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    if email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Validate student_id if role is student
    if role == "student" and student_id:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
    
    # Create user
    user = User(
        username=username,
        email=email,
        role=role,
        student_id=student_id
    )
    user.set_password(password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User created successfully", "user_id": user.id}

