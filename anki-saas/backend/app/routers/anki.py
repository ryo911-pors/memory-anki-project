"""
AnkiConnect integration endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Card
from app.services import anki_connect


router = APIRouter(tags=["anki"])


class AnkiStatusResponse(BaseModel):
    connected: bool
    message: str


class DeckListResponse(BaseModel):
    decks: list[str]


class ExportRequest(BaseModel):
    deck_name: str = "English Learning"


class ExportResponse(BaseModel):
    success: bool
    note_id: Optional[int] = None
    message: str


class ExportAllRequest(BaseModel):
    deck_name: str = "English Learning"
    card_ids: Optional[list[str]] = None  # If None, export all cards


class ExportAllResponse(BaseModel):
    success: bool
    exported_count: int
    failed_count: int
    message: str


@router.get("/anki/status", response_model=AnkiStatusResponse)
async def get_anki_status():
    """
    Check if Anki is running and AnkiConnect is available
    """
    connected = await anki_connect.check_connection()

    if connected:
        return AnkiStatusResponse(
            connected=True,
            message="Anki is running and AnkiConnect is available"
        )
    else:
        return AnkiStatusResponse(
            connected=False,
            message="Cannot connect to Anki. Make sure Anki is running with AnkiConnect installed."
        )


@router.get("/anki/decks", response_model=DeckListResponse)
async def get_decks():
    """
    Get list of all Anki decks
    """
    try:
        decks = await anki_connect.get_deck_names()
        return DeckListResponse(decks=decks)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Anki: {str(e)}"
        )


@router.post("/anki/export/{card_id}", response_model=ExportResponse)
async def export_card_to_anki(
    card_id: str,
    req: ExportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Export a single card to Anki
    """
    # Get the card
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == user.id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    try:
        # Create deck if it doesn't exist
        await anki_connect.create_deck(req.deck_name)

        # Add the note
        note_id = await anki_connect.add_note(
            deck_name=req.deck_name,
            front=card.front,
            back=card.back,
            tags=["anki-saas", card.card_type]
        )

        return ExportResponse(
            success=True,
            note_id=note_id,
            message=f"Card exported to deck '{req.deck_name}'"
        )

    except Exception as e:
        error_msg = str(e)
        if "duplicate" in error_msg.lower():
            return ExportResponse(
                success=False,
                message="This card already exists in Anki"
            )
        raise HTTPException(
            status_code=503,
            detail=f"Failed to export to Anki: {error_msg}"
        )


@router.post("/anki/export-all", response_model=ExportAllResponse)
async def export_all_cards_to_anki(
    req: ExportAllRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Export multiple cards to Anki
    """
    # Get cards
    query = db.query(Card).filter(Card.user_id == user.id)
    if req.card_ids:
        query = query.filter(Card.id.in_(req.card_ids))
    cards = query.all()

    if not cards:
        return ExportAllResponse(
            success=True,
            exported_count=0,
            failed_count=0,
            message="No cards to export"
        )

    try:
        # Create deck if it doesn't exist
        await anki_connect.create_deck(req.deck_name)

        # Prepare notes
        notes = [
            {
                "deck_name": req.deck_name,
                "front": card.front,
                "back": card.back,
                "tags": ["anki-saas", card.card_type]
            }
            for card in cards
        ]

        # Add notes
        results = await anki_connect.add_notes(notes)

        exported_count = sum(1 for r in results if r is not None)
        failed_count = len(results) - exported_count

        return ExportAllResponse(
            success=True,
            exported_count=exported_count,
            failed_count=failed_count,
            message=f"Exported {exported_count} cards to '{req.deck_name}'"
        )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to export to Anki: {str(e)}"
        )
