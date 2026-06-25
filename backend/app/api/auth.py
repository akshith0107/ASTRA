from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, Settings
from app.core.config import settings
from app.services.auth_service import verify_password, get_password_hash, create_access_token, get_current_user
from app.schemas.auth import UserCreate, UserResponse, Token
from app.repositories.user_repository import UserRepository
from app.services.audit_logger import audit_logger
from app.core.limiter import limiter

router = APIRouter()

@router.post("/register", response_model=Token)
@limiter.limit("7/minute")
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if UserRepository.get_by_email(db, user.email) or UserRepository.get_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Email or Username already registered")
        
    # Create user
    db_user = UserRepository.create(db, user)
    
    # Create default settings for user
    db_settings = Settings(user_id=db_user.id)
    db.add(db_settings)
    db.commit()

    # Generate token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}, expires_delta=access_token_expires
    )

    audit_logger.log_action(db, "User Registered", user_id=db_user.id)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
@limiter.limit("7/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = UserRepository.get_by_username(db, form_data.username)
    if not user:
        user = UserRepository.get_by_email(db, form_data.username)
        
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )

    audit_logger.log_action(db, "User Logged In", user_id=user.id)

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
