from fastapi import FastAPI

from routes import (
    accounts_router,
    profiles_router,
    movies_router,
    genres_router,
    stars_router,
    directors_router,
)

app = FastAPI(
    title="Online Cinema",
    description="Modern and user-friendly API for Online Cinema project",
)

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(movies_router, prefix="/theater", tags=["movies"])
app.include_router(genres_router, prefix="/theater/genres", tags=["genres"])
app.include_router(stars_router, prefix="/theater/stars", tags=["stars"])
app.include_router(directors_router, prefix="/theater/directors", tags=["directors"])
