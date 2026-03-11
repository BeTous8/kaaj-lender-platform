from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import lenders, programs, rules, applications, underwrite

app = FastAPI(title="Kaaj Lender Matching Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lenders.router)
app.include_router(programs.router)
app.include_router(rules.router)
app.include_router(applications.router)
app.include_router(underwrite.router)


@app.get("/health")
async def health():
    return {"status": "ok"}