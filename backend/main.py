from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import tasks as tasks_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo Manager", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
