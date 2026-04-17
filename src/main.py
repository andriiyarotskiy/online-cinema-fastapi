from fastapi import FastAPI

from routes import accounts_router

app = FastAPI(
    title="Online Cinema",
    description="Modern and user-friendly API for Online Cinema project",
)

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
