# Synapse OS - Tasks

## Phase 1: Foundation & Environment Setup
- `[x]` Initialize project structure in `d:\PROJECTS\synapse`
- `[x]` Create Python virtual environment for backend
- `[x]` Initialize Next.js frontend project
- `[x]` Create `docker-compose.yml` for PostgreSQL and Redis
- `[x]` Set up basic requirements (FastAPI, Google GenAI SDK, etc.)

## Phase 2: Core Data Ingestion & Storage
- `[x]` Configure PostgreSQL with `pgvector`
- `[x]` Set up Celery/Redis for background tasks
- `[x]` Implement initial ingestion pipeline (Text/Markdown notes)
- `[x]` Implement Gemini API integration for chunking/embeddings

## Phase 3: AI Retrieval & Chat Interface
- `[x]` Build FastAPI Chat endpoint with RAG
- `[x]` Build Next.js chat interface
- `[x]` Implement basic conversation history

## Phase 4: Integrations (GitHub, Email, Calendar)
- `[/]` Install new python dependencies (`requests`, `icalendar`, `beautifulsoup4`)
- `[ ]` Create `app/services/github.py` and `app/services/calendar.py`
- `[ ]` Create `app/services/email.py` (IMAP)
- `[ ]` Add `POST /integrations/*` routes to `app/main.py` or new router
- `[ ]` Build frontend `Integrations.tsx` settings panel with UI for entering credentials

## Phase 5: UI Polish & Deployment
- `[ ]` Polish UI/UX (Notion-like experience)
- `[ ]` Prepare for deployment (Vercel & Render)
