from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Card, ReviewLog
from app.schemas import CardOut
from app.services.sm2 import calculate_sm2

router = APIRouter()


class ReviewRequest(BaseModel):
    rating: int  # 0=Again, 1=Hard, 2=Good, 3=Easy


class ReviewResponse(BaseModel):
    card_id: UUID
    rating: int
    new_interval: int
    new_ease_factor: float
    next_review: date


class DueCardsResponse(BaseModel):
    cards: list[CardOut]
    count: int


@router.get("/cards", response_model=list[CardOut])
def list_cards(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """全カード一覧を取得"""
    cards = db.query(Card).filter(Card.user_id == user.id).order_by(Card.created_at.desc()).all()
    return [CardOut.model_validate(c) for c in cards]


@router.get("/review/due", response_model=DueCardsResponse)
def get_due_cards(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """今日復習すべきカードを取得"""
    today = date.today()
    cards = db.query(Card).filter(
        Card.user_id == user.id,
        Card.next_review <= today
    ).order_by(Card.next_review).all()

    return DueCardsResponse(
        cards=[CardOut.model_validate(c) for c in cards],
        count=len(cards)
    )


@router.post("/review/{card_id}", response_model=ReviewResponse)
def submit_review(
    card_id: UUID,
    req: ReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """復習結果を送信してSM-2で次回日程を計算"""
    if req.rating < 0 or req.rating > 3:
        raise HTTPException(status_code=400, detail="Rating must be 0-3")

    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # SM-2計算
    result = calculate_sm2(
        rating=req.rating,
        repetitions=card.repetitions,
        ease_factor=card.ease_factor,
        interval=card.interval
    )

    # カード更新
    card.repetitions = result.repetitions
    card.ease_factor = result.ease_factor
    card.interval = result.interval
    card.next_review = result.next_review

    # 復習ログ記録
    log = ReviewLog(card_id=card.id, rating=req.rating)
    db.add(log)
    db.commit()

    return ReviewResponse(
        card_id=card.id,
        rating=req.rating,
        new_interval=result.interval,
        new_ease_factor=result.ease_factor,
        next_review=result.next_review
    )
