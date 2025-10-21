import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from core.gemini_client import configure
from routers import generate, score, adaptive, career, behavior, voice

# Firestore init
USE_FIRESTORE = os.getenv("USE_FIRESTORE","false").lower() == "true"
if USE_FIRESTORE:
    import firebase_admin
    from firebase_admin import credentials
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_service_account.json")
        firebase_admin.initialize_app(cred)

load_dotenv()

configure()

app = FastAPI(title="AI Competency Assessment API", version="0.2")

origins = [o.strip() for o in (os.getenv("CORS_ORIGINS","*").split(","))]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status":"ok","message":"AI Backend running","model":"gemini-2.5-flash"}

# Routers
app.include_router(generate.router)
app.include_router(score.router)
app.include_router(adaptive.router)
app.include_router(career.router)
app.include_router(behavior.router)
app.include_router(voice.router)
