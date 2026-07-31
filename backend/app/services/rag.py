from typing import List
from sqlalchemy.orm import Session
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.models import DocumentChunk

import os

from langchain_core.output_parsers import StrOutputParser

def retrieve_relevant_chunks(db: Session, query: str, top_k: int = 5) -> List[DocumentChunk]:
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2", 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    query_embedding = embeddings_model.embed_query(query)
    
    chunks = db.query(DocumentChunk).order_by(
        DocumentChunk.embedding.l2_distance(query_embedding)
    ).limit(top_k).all()
    
    return chunks

def generate_rag_response_stream(db: Session, query: str, conversation_id: int):
    chunks = retrieve_relevant_chunks(db, query)
    context = "\n\n".join([chunk.content for chunk in chunks])
    
    from app.models import Message
    history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).limit(10).all()
    history.reverse()
    
    messages_list = [
        ("system", f"You are Synapse OS, an expert AI assistant. Answer the user's question based ONLY on the following context and conversation history. If you don't know the answer, say that you don't know.\n\nContext:\n{context}")
    ]
    
    for msg in history:
        if msg.role == "user":
            messages_list.append(("human", msg.content))
        else:
            messages_list.append(("ai", msg.content))
            
    prompt = ChatPromptTemplate.from_messages(messages_list)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.2, 
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    chain = prompt | llm | StrOutputParser()
    
    for chunk in chain.stream({"context": context, "query": query}):
        yield chunk

def generate_rag_response(db: Session, query: str, conversation_id: int) -> str:
    # Retained for backwards compatibility if needed
    response = ""
    for chunk in generate_rag_response_stream(db, query, conversation_id):
        response += chunk
    return response
