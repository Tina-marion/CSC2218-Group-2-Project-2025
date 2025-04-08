from fastapi import FastAPI
from api.routers import account_router, transaction_router

app = FastAPI(title="Simple Banking API")

# Include routers
app.include_router(account_router.router, prefix="/accounts", tags=["accounts"])
app.include_router(transaction_router.router, prefix="/transactions", tags=["transactions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Simple Banking API"}