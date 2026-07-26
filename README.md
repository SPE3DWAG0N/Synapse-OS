<div align="center">
  <h1>🧠 Synapse OS</h1>
  <p><strong>A Next-Generation, AI-Powered Workspace & Knowledge Base</strong></p>
  
  <p>
    <a href="https://reactjs.org/"><img src="https://img.shields.io/badge/Frontend-React%2019%20%7C%20Next.js-blue?style=for-the-badge&logo=react" alt="React"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"></a>
    <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/Database-PostgreSQL%20%7C%20pgvector-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL"></a>
    <a href="https://redis.io/"><img src="https://img.shields.io/badge/Message_Broker-Redis-DC382D?style=for-the-badge&logo=redis" alt="Redis"></a>
    <a href="https://docker.com/"><img src="https://img.shields.io/badge/DevOps-Docker%20Compose-2496ED?style=for-the-badge&logo=docker" alt="Docker"></a>
  </p>
</div>

---

## 📖 Project Overview

**Synapse OS** is a highly scalable, Notion-inspired workspace designed to integrate deeply with Artificial Intelligence. Rather than acting as a static note-taking app, Synapse functions as a dynamic knowledge engine. 

It actively ingests user documents into a high-dimensional **pgvector database**, utilizing a decoupled **Celery/Redis background worker architecture** to ensure the main API thread remains unblocked during heavy LangChain vectorization tasks. Users can then query their entire workspace using advanced **Retrieval-Augmented Generation (RAG)**.

This project was built to demonstrate proficiency in **System Design, Asynchronous Processing, and Modern Full-Stack Engineering**.

## 🏗️ System Architecture

```mermaid
graph LR
    Client([Next.js Frontend]) -->|REST API| API(FastAPI Backend)
    API --> DB[(PostgreSQL + pgvector)]
    API -->|Offload Ingestion| Broker(Redis Message Broker)
    Broker --> Worker(Celery Background Worker)
    Worker -->|Generate Embeddings| LLM(Google GenAI / LangChain)
    Worker -->|Store Vectors| DB
```

## ✨ Technical Highlights (For Engineering Teams)

- **Decoupled Background Processing**: Document ingestion (chunking, embedding, database storage) is offloaded to a **Celery** worker queue backed by **Redis**. This prevents the FastAPI event loop from blocking during computationally expensive LLM network calls.
- **Advanced Vector Search**: Utilizes **pgvector** natively within PostgreSQL (via SQLAlchemy) for high-performance semantic similarity search (Cosine Distance), avoiding the need for a separate, isolated vector database.
- **Isolated Transactional Testing**: The **Pytest** suite implements custom fixtures that run every test within a nested SQL transaction. Transactions are automatically rolled back upon test completion, ensuring a deterministic, non-destructive testing environment.
- **Robust Database Management**: Schema version control is strictly managed using **Alembic** migrations, adhering to production-ready database management standards.
- **Containerized Orchestration**: The entire distributed system (Frontend, Backend API, Celery Worker, Redis, and Postgres) is fully containerized and orchestrated via **Docker Compose** for a seamless, 1-click developer experience.

## 🛠️ Technology Stack

### Frontend Architecture
- **Framework**: Next.js (React 19)
- **Styling**: Vanilla CSS Modules (Demonstrating strong fundamental CSS architecture without utility-class bloat)
- **Data Rendering**: `react-markdown` for secure parsing of rich AI responses

### Backend Architecture
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL + `pgvector`
- **ORM & Migrations**: SQLAlchemy + Alembic
- **Task Queue**: Celery + Redis
- **AI & ML**: LangChain + Google GenAI Models
- **Testing**: Pytest + `httpx`

---

## 🚀 Quick Start (Docker)

To test the application locally, ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SPE3DWAG0N/Synapse-OS.git
   cd Synapse-OS
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the `backend/` directory and add your required keys:
   ```env
   GOOGLE_API_KEY=your_gemini_key_here
   ```

3. **Spin up the distributed system:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - 🌐 **Frontend UI**: [http://localhost:3000](http://localhost:3000)
   - ⚙️ **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

The backend includes a rigorous integration testing suite.

```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # (Windows)
pip install -r requirements.txt
pytest tests/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
