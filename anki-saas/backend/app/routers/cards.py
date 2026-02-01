from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Conversation, Message, Card
from app.schemas import (
    GenerateRequest, GenerateResponse, CardCandidate,
    ApproveRequest, ApproveResponse, CardOut,
    LookupRequest, LookupResponse, QuickCardRequest, CardUpdate
)
from app.services.card_generator import generate_cards_from_conversation
from app.services.word_lookup import lookup_word

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
def generate_cards(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == req.conversation_id,
        Conversation.user_id == user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()

    if not messages:
        raise HTTPException(status_code=400, detail="No messages in conversation")

    history = [{"role": m.role, "content": m.content} for m in messages]

    # Generate cards
    raw_cards = generate_cards_from_conversation(history)

    candidates = [
        CardCandidate(
            card_type=c.get("card_type", "vocab"),
            front=c.get("front", ""),
            back=c.get("back", "")
        )
        for c in raw_cards
        if c.get("front") and c.get("back")
    ]

    return GenerateResponse(candidates=candidates)


@router.post("/approve", response_model=ApproveResponse)
def approve_cards(
    req: ApproveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Verify conversation exists
    conversation = db.query(Conversation).filter(
        Conversation.id == req.conversation_id,
        Conversation.user_id == user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    created_cards = []
    for card_data in req.cards:
        card = Card(
            user_id=user.id,
            conversation_id=conversation.id,
            card_type=card_data.card_type,
            front=card_data.front,
            back=card_data.back
        )
        db.add(card)
        db.flush()
        created_cards.append(card)

    db.commit()

    return ApproveResponse(
        created=[CardOut.model_validate(c) for c in created_cards]
    )


@router.post("/lookup", response_model=LookupResponse)
def lookup_word_endpoint(
    req: LookupRequest,
    user: User = Depends(get_current_user)
):
    """単語の意味を取得（Claude API）"""
    result = lookup_word(req.word, req.context)
    return LookupResponse(**result)


@router.post("/quick", response_model=CardOut)
def quick_create_card(
    req: QuickCardRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """単語から直接カードを作成"""
    # Determine front/back based on card_type
    if req.card_type == "cloze" and req.context:
        # Cloze: 文脈で単語を___に置換
        front = req.context.replace(req.word, "___")
        back = req.word
    else:
        # Vocab: 単語 → 意味
        front = req.word
        back = req.meaning

    card = Card(
        user_id=user.id,
        card_type=req.card_type,
        front=front,
        back=back
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return CardOut.model_validate(card)


@router.put("/cards/{card_id}", response_model=CardOut)
def update_card(
    card_id: UUID,
    req: CardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """カードを編集"""
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if req.front is not None:
        card.front = req.front
    if req.back is not None:
        card.back = req.back
    if req.card_type is not None:
        card.card_type = req.card_type

    db.commit()
    db.refresh(card)

    return CardOut.model_validate(card)


@router.delete("/cards/{card_id}")
def delete_card(
    card_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """カードを削除"""
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    db.delete(card)
    db.commit()

    return {"status": "deleted"}
