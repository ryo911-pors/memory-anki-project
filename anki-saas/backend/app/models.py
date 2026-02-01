import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Text, Float, Integer, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)

    api_keys = relationship("ApiKey", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    cards = relationship("Card", back_populates="user")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="api_keys")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    cards = relationship("Card", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    card_type = Column(String(20), nullable=False)  # 'vocab', 'cloze', 'rewrite'
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    # SRS fields
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cards")
    conversation = relationship("Conversation", back_populates="cards")
    review_logs = relationship("ReviewLog", back_populates="card")


class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 0=Again, 1=Hard, 2=Good, 3=Easy
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    card = relationship("Card", back_populates="review_logs")
