from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.init_db import init_db
from app.api.routes import router

app = FastAPI(title="TalentSort AI API", version="1.0.0",
              description="Evidence-based resume screening decision support. Human review required.")
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"name":"TalentSort AI","docs":"/docs","health":"/api/health"}
