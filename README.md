# NovaSphere

NovaSphere is an internal company knowledge assistant built with a FastAPI backend, a Next.js frontend, MongoDB Atlas vector search, sentence-transformer embeddings, and a Groq-powered response layer.

## What It Does

- Answers company knowledge questions using RAG over internal documents
- Supports a multi-agent flow with `RAG`, `generic`, and `fallback` behavior
- Stores chat history in MongoDB and reloads it across refreshes
- Provides a floating chatbot UI with a centered modal experience

## Tech Stack

### Backend

- FastAPI
- MongoDB Atlas
- PyMongo
- Sentence Transformers (`all-MiniLM-L6-v2`)
- Groq (`llama-3.1-8b-instant`)
- Python Dotenv

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- Axios

## Project Structure

```text
rag-eval-system/
├── backend/
│   ├── app/
│   ├── rag/
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── .env.example
└── README.md
```

## Backend Environment

Create `backend/.env` from `backend/.env.example` and fill in your values.

Required:

- `MONGODB_URI`
- `GROQ_API_KEY`

Available config:

- `MONGO_DATABASE_NAME`
- `MONGO_COLLECTION_NAME`
- `EMBEDDING_MODEL`
- `GROQ_MODEL_NAME`
- `VECTOR_SEARCH_INDEX_NAME`
- `VECTOR_SEARCH_EMBEDDING_PATH`
- `VECTOR_SEARCH_DIMENSIONS`
- `VECTOR_SEARCH_TOP_K`
- `VECTOR_SEARCH_NUM_CANDIDATES`
- `VECTOR_SEARCH_SCORE_THRESHOLD`
- `VECTOR_SEARCH_REQUIRED_FILTER_PATHS`

## Frontend Environment

Create `frontend/.env.local` or `frontend/.env` from `frontend/.env.example`.

Available config:

- `NEXT_PUBLIC_API_BASE_URL`

Default local backend:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Run Locally

Open two terminals.

### Backend

```powershell
cd c:\Projects\rag-eval-system\backend
uv sync
uv run uvicorn app.main:app --reload
```

### Frontend

```powershell
cd c:\Projects\rag-eval-system\frontend
npm install
npm run dev
```

Frontend:

- `http://localhost:3000`

Backend:

- `http://127.0.0.1:8000`

## API Endpoints

- `POST /chat`
- `GET /chat/history?session_id=...`
- `GET /chat/history/{conversation_id}?session_id=...`

## Python Dependencies

The backend dependency list is available in:

- `backend/requirements.txt`

If you use `uv`, the source of truth is:

- `backend/pyproject.toml`

## Notes

- `backend/.env` is ignored and will not be committed
- `frontend/.env` and `frontend/.env.local` are ignored and will not be committed
- `backend/.env.example` and `frontend/.env.example` are included for setup
