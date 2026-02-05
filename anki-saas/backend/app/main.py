import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, chat, cards, review, anki

app = FastAPI(
    title="Anki SaaS API",
    description="AIチャットからフラッシュカードを生成し、SM-2で復習管理",
    version="0.1.0"
)

# CORS設定（環境変数で制御、デフォルトはローカル開発用）
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5500,http://localhost:3000,http://127.0.0.1:5500").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(cards.router, tags=["Cards"])
app.include_router(review.router, tags=["Review"])
app.include_router(anki.router, tags=["Anki"])
