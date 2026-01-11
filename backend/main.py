from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings

app = FastAPI(
    title="Duolingo Clone API",
    description="Backend API for Duolingo Clone",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Duolingo Clone API"}

