from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation, Message
from pydantic import BaseModel

router = APIRouter()

@router.get("/")
def get_conversations(db: Session = Depends(get_db)):
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    return [{"id": c.id, "title": c.title} for c in conversations]

@router.post("/")
def create_conversation(db: Session = Depends(get_db)):
    conv = Conversation(title="New Conversation")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "title": conv.title}

@router.get("/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": conv.id,
        "title": conv.title,
        "messages": [
            {"id": str(m.id), "role": m.role, "content": m.content} for m in conv.messages
        ]
    }

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conv)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}
