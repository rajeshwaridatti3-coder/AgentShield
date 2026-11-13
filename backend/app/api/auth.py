from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models import User
from app.core.config import settings
from app.schemas import RegisterIn, LoginIn
router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(422, "Enter a valid email address")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered")
    organization = payload.organization.strip()
    if len(organization) < 2:
        raise HTTPException(422, "Workspace name must contain at least 2 non-space characters")
    # Registration cannot silently join an existing tenant; invitations are intentionally not implicit.
    if db.query(User).filter(User.organization == organization).first():
        raise HTTPException(409, "Workspace name already exists. Choose a unique workspace name.")
    role = "admin" if settings.bootstrap_admin_email and email == settings.bootstrap_admin_email.strip().lower() else "member"
    user = User(email=email, password_hash=hash_password(payload.password), organization=organization, role=role)
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}

@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "organization": user.organization, "role": user.role}
