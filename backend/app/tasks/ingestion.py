import os
from celery.utils.log import get_task_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Document, DocumentChunk

logger = get_task_logger(__name__)

@celery_app.task
def process_document(document_id: int):
    logger.info(f"Processing document {document_id}")
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document {document_id} not found.")
            return

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(document.content)
        
        # gemini-embedding-2
        embeddings_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-2",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        for i, chunk_text in enumerate(chunks):
            embedding = embeddings_model.embed_query(chunk_text)
            
            doc_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding
            )
            db.add(doc_chunk)
            
        db.commit()
        logger.info(f"Successfully processed document {document_id} into {len(chunks)} chunks.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing document {document_id}: {e}")
    finally:
        db.close()
