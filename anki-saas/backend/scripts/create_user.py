#!/usr/bin/env python3
"""
テストユーザーとAPIキーを作成するスクリプト
Usage: python scripts/create_user.py
"""
import secrets
import hashlib
import uuid
import sys
sys.path.insert(0, '.')

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import User, ApiKey


def create_test_user():
    db = SessionLocal()
    try:
        # Create user
        user = User(id=uuid.uuid4())
        db.add(user)
        db.flush()

        # Generate API key
        api_key = f"ak_{secrets.token_hex(24)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        api_key_record = ApiKey(
            id=uuid.uuid4(),
            user_id=user.id,
            key_hash=key_hash
        )
        db.add(api_key_record)
        db.commit()

        print(f"User ID: {user.id}")
        print(f"API Key: {api_key}")
        print("\nUse this API key in the X-API-Key header")

    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
