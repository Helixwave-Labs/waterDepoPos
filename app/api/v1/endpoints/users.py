from datetime import timedelta
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1 import deps
from app.core import security
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password): # pyright: ignore[reportArgumentType]
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    username: str = Form(..., description="Username"),
    full_name: Optional[str] = Form(None, description="Full Name"),
    password: str = Form(..., description="Password"),
    role: UserRole = Form(UserRole.STAFF, description="Role: owner or staff"),
    phone: Optional[str] = Form(None, description="Phone number"),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Compare the value, not the SQLAlchemy column object
    if (getattr(current_user, "role", None) != UserRole.OWNER and getattr(current_user, "role", None) != "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    if full_name == "":
        full_name = None
    if phone == "":
        phone = None

    user = User(
        username=username,
        full_name=full_name,
        hashed_password=security.get_password_hash(password),
        role=role,
        phone=phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=str(user.id),
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.get("/", response_model=List[UserResponse])
def list_staff(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Only owner can see all staff
    if (getattr(current_user, "role", None) != UserRole.OWNER and getattr(current_user, "role", None) != "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    staff = db.query(User).filter(User.role == UserRole.STAFF).all()
    return [
        UserResponse(
            id=str(user.id),
            username=user.username,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        ) for user in staff
    ]

@router.delete("/{user_id}", response_model=UserResponse)
def delete_staff(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Only owner can delete staff
    if (getattr(current_user, "role", None) != UserRole.OWNER and getattr(current_user, "role", None) != "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.STAFF).first()
    if not user:
        raise HTTPException(status_code=404, detail="Staff user not found")
    db.delete(user)
    db.commit()
    return UserResponse(
        id=str(user.id),
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.patch("/{user_id}/status", response_model=UserResponse)
def toggle_user_status(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    active: bool,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Activate or deactivate a staff member.
    """
    if (getattr(current_user, "role", None) != UserRole.OWNER and getattr(current_user, "role", None) != "owner"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = active
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=str(user.id),
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )