from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, Conversation, Message
from app.schemas import ChatRequest, ChatResponse
from app.services.claude import chat_with_claude

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Get or create conversation
    if req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == user.id
        ).first()
        if not conversation:
            conversation = Conversation(user_id=user.id)
            db.add(conversation)
            db.flush()
    else:
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.flush()

    # Get existing conversation history
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()

    history = [{"role": m.role, "content": m.content} for m in messages]
    # Add current user message to history
    history.append({"role": "user", "content": req.message})

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=req.message
    )
    db.add(user_msg)

    # Call Claude
    response_text = chat_with_claude(history)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text
    )
