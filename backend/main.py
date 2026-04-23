from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from routers.resume_routes import router as resume_router
from routers.match_routes import router as match_router
from routers.history_routes import router as history_router
from routers.chat_routes import router as chat_router   # 🔥 NEW

# Database
from database import engine, Base

# ================================
# 🔹 Create DB Tables
# ================================
Base.metadata.create_all(bind=engine)

# ================================
# 🔹 App Init
# ================================
app = FastAPI(
    title="HireSmart AI Backend 🚀",
    version="1.0.0",
    description="AI-powered Resume Screening System"
)

# ================================
# 🔹 CORS (Frontend Connection)
# ================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# 🔹 Include Routers
# ================================
app.include_router(resume_router, tags=["Resume"])
app.include_router(match_router, tags=["Matching"])
app.include_router(history_router, tags=["History"])
app.include_router(chat_router, tags=["Chatbot"])   # 🔥 NEW

# ================================
# 🔹 Health Check
# ================================
@app.get("/health")
def health_check():
    return {"status": "Backend is running ✅"}

# ================================
# 🔹 Root Test Route
# ================================
@app.get("/")
def home():
    return {"message": "HireSmart Backend Running 🚀"}