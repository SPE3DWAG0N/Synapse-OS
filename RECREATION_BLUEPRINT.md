# System Prompt: Synapse OS Recreation

**Role:** You are an expert AI software engineer tasked with recreating "Synapse OS", an AI-powered Personal Operating System.
**Goal:** Scaffold and implement the exact architecture, database schema, backend API, and frontend interface described below from scratch in a new directory. 
**Constraint Checklist & Confidence Score:** 
1. Use Next.js (TypeScript) for the frontend.
2. Strictly use Vanilla CSS Modules (`*.module.css`) for all frontend components. **DO NOT USE TAILWIND CSS.**
3. Use Python + FastAPI for the backend.
4. Use PostgreSQL with the `pgvector` extension for the database.
5. Use Celery and Redis for background processing.
6. Use LangChain and Google GenAI (`gemini-1.5-flash`, `text-embedding-004`) for AI operations.

---

## 1. Directory Structure Setup

Create a monorepo with the following base structure:
```text
/
  docker-compose.yml
  /backend
    requirements.txt
    /app
      __init__.py
      main.py
      database.py
      models.py
      celery_app.py
      /routers
      /services
      /tasks
  /frontend
    package.json
    /src
      /app
      /components
        Chat.tsx
        Chat.module.css
```

---

## 2. Infrastructure & Environment

### `docker-compose.yml`
Create a docker-compose file with:
- `synapse-db`: Image `ankane/pgvector:latest`, mapping port 5432, setting POSTGRES_USER/PASSWORD/DB.
- `synapse-redis`: Image `redis:7-alpine`, mapping port 6379.

### `backend/requirements.txt`
```text
fastapi[standard]
uvicorn
sqlalchemy
psycopg2-binary
pgvector
celery
redis
python-dotenv
google-genai
langchain
langchain-google-genai
pypdf
```

### Frontend Setup
Initialize a Next.js app in `/frontend` using `npx create-next-app@latest .`. 
Ensure you install `react-markdown`.
Remove all Tailwind boilerplate from `globals.css` and configure the app to use raw CSS.

---

## 3. Backend Implementation (FastAPI + Celery + pgvector)

### A. Database Models (`app/models.py`)
Implement SQLAlchemy models. You MUST use the `pgvector` Vector type for embeddings:
- `Document`: `id`, `title`, `source_type` (Enum: note, pdf, bookmark, github, email, calendar), `source_url`, `content`, `created_at`, `updated_at`.
- `DocumentChunk`: `id`, `document_id` (ForeignKey), `chunk_index`, `content`, `embedding` (Column: `Vector(3072)` for Gemini).

### B. Ingestion Pipeline (`app/tasks/ingestion.py`)
Implement a Celery task `@celery_app.task def process_document(document_id: int):` that:
1. Fetches the document from the DB.
2. Uses LangChain's `RecursiveCharacterTextSplitter` (chunk_size=1000, chunk_overlap=200).
3. Generates vector embeddings for each chunk using `langchain-google-genai` `GoogleGenerativeAIEmbeddings`.
4. Saves the chunks and embeddings to the `DocumentChunk` table.

### C. Retrieval-Augmented Generation (`app/services/rag.py`)
Implement `retrieve_relevant_chunks(db, query, top_k=5)`:
- Embed the user query.
- Perform a similarity search ordering by pgvector L2 distance: `DocumentChunk.embedding.l2_distance(query_embedding)`.
Implement `generate_rag_response(db, query)`:
- Pass the retrieved chunks as context to `ChatGoogleGenerativeAI` to answer the query.

### D. API Endpoints (`app/main.py`)
- `POST /documents/`: Accepts title, source_type, content, source_url. Saves `Document` and calls `process_document.delay(doc.id)`.
- `POST /chat/`: Accepts a user query, calls `generate_rag_response`, returns the AI string.

---

## 4. Frontend Implementation (Next.js + Vanilla CSS)

### A. Chat Component (`frontend/src/components/Chat.tsx`)
Build a highly polished, Notion-inspired chat interface.
- Must manage `messages` state (user/ai roles).
- Render AI messages using `react-markdown`.
- Must contain a "Settings / Integrations" header button that toggles an `<Integrations />` component.
- Display a micro-animated loading indicator when waiting for the backend.

### B. Styling (`frontend/src/components/Chat.module.css`)
- **Strict Constraint:** Do not use Tailwind. 
- Implement premium aesthetics: glassmorphism, smooth message bubble pop-in transitions, minimal scrollbars, and modern typography.

---

## 5. Phase 4 Integrations (Future Work)

After scaffolding the core, implement these planned integrations as new routers and Celery pipelines:
1. **GitHub:** `POST /api/integrations/github` -> Fetch recent issues/PRs using a PAT.
2. **Calendar:** `POST /api/integrations/calendar` -> Parse `.ics` files using `icalendar`.
3. **Email:** `POST /api/integrations/email` -> Connect to Gmail via IMAP with `imaplib`.
4. **Integrations UI (`Integrations.tsx`):** A sleek slide-out panel overlay on the frontend for entering these API keys and credentials.
