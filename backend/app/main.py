from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import router

app = FastAPI(title="SupplyChain Sentinel API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()

app.include_router(router)

@app.get("/health")
def health():
    return {"status":"ok","service":"supplychain-sentinel"}
