from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import decode_token, get_user_by_username
from app.models.user import User

# auto_error=False allows requests without Bearer token to pass through
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        # Default to primary admin/system user so login is not required
        return db.query(User).filter(User.username == "admin").first() or db.query(User).first()
    try:
        token_data = decode_token(token)
        user = get_user_by_username(db, username=token_data.username)
        return user or db.query(User).first()
    except Exception:
        return db.query(User).first()

def get_current_active_user(current_user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    return current_user

def require_admin(current_user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    return current_user

def require_user(current_user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    return current_user
