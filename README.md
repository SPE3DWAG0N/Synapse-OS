<div align="center">
  <h1>🧠 Synapse OS</h1>
  <p><strong>A Next-Generation, AI-Powered Workspace & Knowledge Base</strong></p>
  
  <p>
    <a href="https://reactjs.org/"><img src="https://img.shields.io/badge/Frontend-React%2019%20%7C%20Next.js-blue?style=for-the-badge&logo=react" alt="React"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"></a>
    <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/Database-PostgreSQL%20%7C%20pgvector-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL"></a>
    <a href="https://docker.com/"><img src="https://img.shields.io/badge/DevOps-Docker-2496ED?style=for-the-badge&logo=docker" alt="Docker"></a>
  </p>
</div>

---

## 📖 Overview

**Synapse OS** is a powerful, Notion-inspired workspace built from the ground up to integrate deeply with Artificial Intelligence. Instead of just writing notes, Synapse OS actively ingests your documents, links, and text into a high-dimensional vector database. 

Using advanced **Retrieval-Augmented Generation (RAG)**, you can chat with your workspace. Ask questions, extract summaries, and let the AI instantly retrieve exact context from across all your saved documents.

## ✨ Key Features

- 💬 **Intelligent Chat (RAG)**: Chat directly with your knowledge base using Google GenAI models and LangChain.
- 📚 **Background Ingestion**: Upload PDFs, sync calendars, or paste notes. Synapse uses **Celery & Redis** to process, chunk, and vectorize your documents asynchronously without blocking the UI.
- 🔍 **Semantic Search**: Powered by **pgvector**, search your workspace by meaning, not just keywords.
- 🎨 **Premium Aesthetic**: A beautifully crafted, responsive frontend using Next.js and Vanilla CSS Modules.
- 🐳 **Fully Dockerized**: Spin up the entire architecture (Frontend, Backend, Redis, Postgres, and Background Workers) with a single command.

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js (React 19)
- **Styling**: Vanilla CSS Modules (Zero dependency styling)
- **Markdown**: `react-markdown` for rendering rich AI responses

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with the `pgvector` extension
- **ORM & Migrations**: SQLAlchemy & Alembic
- **Task Queue**: Celery + Redis
- **AI / LLMs**: LangChain + Google GenAI

---

## 🚀 Quick Start (Docker)

The easiest way to run Synapse OS is using Docker. Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SPE3DWAG0N/Synapse-OS.git
   cd Synapse-OS
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the `backend/` directory and add your AI API keys (e.g., `GOOGLE_API_KEY`).

3. **Spin up the stack:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - 🌐 **Frontend UI**: [http://localhost:3000](http://localhost:3000)
   - ⚙️ **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

Synapse OS includes a robust testing suite for the backend that runs in isolated SQL transactions to prevent dev-data corruption.

To run the test suite locally:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # (or venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
pytest tests/
```

## 🗄️ Database Migrations

Database schema changes are managed by **Alembic**. If you update the models in `backend/app/models.py`, generate a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of change"
alembic upgrade head
```

---

## 🤝 Contributing

Contributions are always welcome! Feel free to open a Pull Request or create an Issue if you find a bug or want to suggest a new feature.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
