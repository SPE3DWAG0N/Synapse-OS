import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.database import SessionLocal
from app.models import Document, SourceType
from app.tasks.ingestion import process_document

DROP_FOLDER = os.path.expanduser("~/Synapse_Drop")

class DocumentEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
            
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Wait a moment for file to finish copying
        time.sleep(1)
        
        try:
            content = ""
            source_type = SourceType.note
            
            if filepath.endswith(".pdf"):
                from pypdf import PdfReader
                with open(filepath, "rb") as f:
                    pdf = PdfReader(f)
                    for page in pdf.pages:
                        content += page.extract_text() + "\n"
                source_type = SourceType.pdf
            elif filepath.endswith(".md") or filepath.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            else:
                return # unsupported file
                
            content = content.replace('\x00', '')
            
            db = SessionLocal()
            try:
                db_doc = Document(
                    title=f"DropFolder: {filename}",
                    source_type=source_type,
                    content=content,
                    source_url=filepath
                )
                db.add(db_doc)
                db.commit()
                db.refresh(db_doc)
                
                process_document.delay(db_doc.id)
                print(f"Processed dropped file: {filename}")
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error processing dropped file {filename}: {e}")

def start_watcher():
    if not os.path.exists(DROP_FOLDER):
        os.makedirs(DROP_FOLDER)
        
    event_handler = DocumentEventHandler()
    observer = Observer()
    observer.schedule(event_handler, DROP_FOLDER, recursive=False)
    observer.start()
    print(f"Started Synapse Drop Watcher at {DROP_FOLDER}")
    return observer
