import hashlib
from uuid import UUID

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApiKey, User


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def get_current_user(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    key_hash = hash_api_key(x_api_key)
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key.user
