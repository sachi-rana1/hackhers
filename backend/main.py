from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import index, explain

app = FastAPI(
    title="APIx High-Performance REST Gateway",
    description="Calculated Indian airfare CPI tracker API feeds.",
    version="1.0.0"
)

# Enable CORS for frontend or local dashboard connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🔌 ROUTER REGISTRATION ---
# This links your separate index.py and explain.py route files to the app
app.include_router(index.router, prefix="/api/v1")
app.include_router(explain.router, prefix="/api/v1")

@app.get("/")
def gateway_index():
    return {"status": "Online", "service": "APIx Core Platform Gateway"}
