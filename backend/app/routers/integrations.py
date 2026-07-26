from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests

from app.database import get_db
from app.models import Document, SourceType
from app.tasks.ingestion import process_document

router = APIRouter()

class GitHubIntegrationRequest(BaseModel):
    repository_name: str
    github_token: str

@router.post("/github")
def sync_github(request: GitHubIntegrationRequest, db: Session = Depends(get_db)):
    headers = {
        "Authorization": f"token {request.github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Fetch Issues (which includes PRs in GitHub API)
    url = f"https://api.github.com/repos/{request.repository_name}/issues?state=all&per_page=20"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch from GitHub: {response.text}")
        
    issues = response.json()
    processed_count = 0
    
    for issue in issues:
        title = issue.get("title", "Untitled")
        body = issue.get("body") or ""
        html_url = issue.get("html_url", "")
        
        # Format the content so the AI has good context
        content = f"Issue/PR: {title}\nURL: {html_url}\n\n{body}"
        
        db_doc = Document(
            title=f"GitHub: {title}",
            source_type=SourceType.github,
            content=content,
            source_url=html_url
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        # Trigger background ingestion
        process_document.delay(db_doc.id)
        processed_count += 1
        
    return {"message": f"Successfully queued {processed_count} GitHub items for processing."}

from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class YouTubeIntegrationRequest(BaseModel):
    youtube_url: str

@router.post("/youtube")
def sync_youtube(request: YouTubeIntegrationRequest, db: Session = Depends(get_db)):
    parsed = urlparse(request.youtube_url)
    video_id = ""
    if "youtube.com" in parsed.netloc:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    elif "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip("/")
        
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)
        full_text = " ".join([t.text for t in transcript.snippets])
        
        content = f"YouTube Video Transcript ({request.youtube_url}):\n\n{full_text}"
        
        db_doc = Document(
            title=f"YouTube Video: {video_id}",
            source_type=SourceType.note,
            content=content,
            source_url=request.youtube_url
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        process_document.delay(db_doc.id)
        
        return {"message": "Successfully queued YouTube video for processing."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transcript: {str(e)}")

from fastapi import UploadFile, File
import icalendar

@router.post("/calendar")
async def sync_calendar(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".ics"):
        raise HTTPException(status_code=400, detail="Only .ics files are supported")
        
    try:
        content = await file.read()
        cal = icalendar.Calendar.from_ical(content)
        
        processed_count = 0
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = str(component.get("summary", "Untitled Event"))
                description = str(component.get("description", ""))
                start = component.get("dtstart").dt if component.get("dtstart") else "Unknown"
                
                doc_content = f"Calendar Event: {summary}\nStart Time: {start}\n\nDescription: {description}"
                
                db_doc = Document(
                    title=f"Event: {summary}",
                    source_type=SourceType.calendar,
                    content=doc_content,
                    source_url=file.filename
                )
                db.add(db_doc)
                db.commit()
                db.refresh(db_doc)
                
                process_document.delay(db_doc.id)
                processed_count += 1
                
        return {"message": f"Successfully queued {processed_count} calendar events for processing."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse calendar: {str(e)}")

import imaplib
import email
from email.header import decode_header

class EmailIntegrationRequest(BaseModel):
    imap_server: str
    email_address: str
    app_password: str

@router.post("/email")
def sync_email(request: EmailIntegrationRequest, db: Session = Depends(get_db)):
    try:
        mail = imaplib.IMAP4_SSL(request.imap_server)
        mail.login(request.email_address, request.app_password)
        mail.select("inbox")
        
        _, search_data = mail.search(None, "ALL")
        mail_ids = search_data[0].split()
        
        recent_ids = mail_ids[-5:]
        processed_count = 0
        
        for i in recent_ids:
            _, msg_data = mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors='ignore')
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                except:
                                    pass
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors='ignore')
                        
                    content = f"Email Subject: {subject}\nFrom: {msg.get('From')}\nDate: {msg.get('Date')}\n\n{body}"
                    
                    db_doc = Document(
                        title=f"Email: {subject}",
                        source_type=SourceType.email,
                        content=content,
                        source_url=f"imap://{request.email_address}/{i.decode()}"
                    )
                    db.add(db_doc)
                    db.commit()
                    db.refresh(db_doc)
                    
                    process_document.delay(db_doc.id)
                    processed_count += 1
                    
        mail.logout()
        return {"message": f"Successfully queued {processed_count} recent emails for processing."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync email: {str(e)}")

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content_bytes = await file.read()
        
        if file.filename.endswith(".pdf"):
            import io
            from pypdf import PdfReader
            pdf = PdfReader(io.BytesIO(content_bytes))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            content = text
            source_type = SourceType.pdf
        else:
            content = content_bytes.decode('utf-8', errors='ignore')
            source_type = SourceType.note
            
        # PostgreSQL text fields cannot contain null bytes
        content = content.replace('\x00', '')
            
        db_doc = Document(
            title=file.filename,
            source_type=source_type,
            content=content,
            source_url=file.filename
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        process_document.delay(db_doc.id)
        
        return {"message": "Successfully queued document for processing."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
