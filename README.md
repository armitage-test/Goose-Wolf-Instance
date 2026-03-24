# Todo Manager

A full-stack task management app built with **React** (frontend) and **FastAPI** (backend).

## Stack

- **Frontend**: React 18 + Vite + Vitest + React Testing Library
- **Backend**: FastAPI + SQLAlchemy + SQLite

## Getting started

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Running tests

### Backend

```bash
pytest backend/tests/ -v
```

### Frontend

```bash
cd frontend
npm test
# with coverage
npm run coverage
```
