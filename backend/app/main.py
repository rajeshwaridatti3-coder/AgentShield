from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.core.config import settings
from app.api import auth, documents, chat, tools, redteam, observability, memory, platform

if settings.environment.lower() == "production" and (settings.secret_key == "dev-only-change-me" or len(settings.secret_key) < 32):
    raise RuntimeError("Set a unique SECRET_KEY of at least 32 characters before production startup")

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0", description="Security-first Agentic RAG platform")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(tools.router)
app.include_router(redteam.router)
app.include_router(observability.router)
app.include_router(memory.router)
app.include_router(platform.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "agentshield"}
