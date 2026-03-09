from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import documents, tax, auth, payment, state_tax
from models.database import init_db

app = FastAPI(title="TaxAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    # Ensure database tables are created before handling requests
    await init_db()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(tax.router, prefix="/api/tax", tags=["tax"])
app.include_router(state_tax.router, prefix="/api/state-tax", tags=["state-tax"])
app.include_router(payment.router, prefix="/api/payment", tags=["payment"])

@app.get("/")
def root():
    return {"status": "TaxAI API running"}
