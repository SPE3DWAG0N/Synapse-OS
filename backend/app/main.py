from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import engine, Base, get_db
from app.models import Document, SourceType
from app.tasks.ingestion import process_document
from app.services.rag import generate_rag_response
from app.routers import integrations, conversations
from sqlalchemy import text

# Enable pgvector extension
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

# Tables are managed by Alembic now
# Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.watcher import start_watcher
    observer = start_watcher()
    yield
    observer.stop()
    observer.join()

app = FastAPI(title="Synapse OS Backend", lifespan=lifespan)

# Register routers
app.include_router(integrations.router, prefix="/api/integrations")
app.include_router(conversations.router, prefix="/api/conversations")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentCreate(BaseModel):
    title: str
    source_type: SourceType
    content: str
    source_url: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None

@app.post("/documents/")
def create_document(doc_in: DocumentCreate, db: Session = Depends(get_db)):
    db_doc = Document(
        title=doc_in.title,
        source_type=doc_in.source_type,
        content=doc_in.content,
        source_url=doc_in.source_url
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Trigger background ingestion
    process_document.delay(db_doc.id)
    
    return {"message": "Document accepted for processing", "id": db_doc.id}

@app.post("/chat/")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        from app.models import Conversation, Message
        if not request.conversation_id:
            conv = Conversation(title=request.query[:30])
            db.add(conv)
            db.commit()
            db.refresh(conv)
            conv_id = conv.id
        else:
            conv_id = request.conversation_id
            
        user_msg = Message(conversation_id=conv_id, role="user", content=request.query)
        db.add(user_msg)
        db.commit()
        
        # We will use StreamingResponse
        from fastapi.responses import StreamingResponse
        import json
        from app.services.rag import generate_rag_response_stream
        
        def generate():
            full_response = ""
            # Send initial event with conversation_id for new chats
            yield f"data: {json.dumps({'conversation_id': conv_id, 'status': 'start'})}\n\n"
            
            for chunk in generate_rag_response_stream(db, request.query, conv_id):
                full_response += chunk
                yield f"data: {json.dumps({'text': chunk})}\n\n"
                
            yield f"data: {json.dumps({'status': 'end'})}\n\n"
            
            # Save to DB after streaming is done
            ai_msg = Message(conversation_id=conv_id, role="ai", content=full_response)
            db.add(ai_msg)
            db.commit()

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
