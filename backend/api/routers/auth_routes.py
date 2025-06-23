from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.user import User
from backend.api.schemas.user import UserCreate, UserResponse, TokenResponse
from backend.api.dependencies import get_db_session, get_current_user, create_access_token, create_refresh_token, verify_password, hash_password, security_scheme
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Register a new user.
    This endpoint allows a new user to register by providing a username and password.
    It checks if the username already exists and hashes the password before storing it in the database.
    """
    # Check if username exists
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create user
    db_user = User(username=user.username, password_hash=hash_password(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=TokenResponse)
async def login_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Log in an existing user.
    This endpoint allows a user to log in by providing their username and password.
    It verifies the credentials and generates access and refresh tokens.
    """
    # Verify user
    result = await db.execute(select(User).filter(User.username == user.username))
    db_user = result.scalars().first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate tokens
    access_token = create_access_token({"sub": db_user.username}, expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))))
    refresh_token = create_refresh_token({"sub": db_user.username}, expires_delta=timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(security_scheme)
):
    """
    Refresh access and refresh tokens.
    This endpoint allows a user to refresh their access and refresh tokens using their current session.
    It requires the user to be authenticated and returns new tokens.
    """
    # Generate new tokens
    access_token = create_access_token({"sub": current_user.username}, expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))))
    refresh_token = create_refresh_token({"sub": current_user.username}, expires_delta=timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}